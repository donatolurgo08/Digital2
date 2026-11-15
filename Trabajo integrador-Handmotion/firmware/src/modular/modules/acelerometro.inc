;*******************************************************************************
; MODULO ACELEROMETRO - Conversion de X/Y/Z del MMA7361 a miligramos
;
; convertir_x_mg y convertir_y_mg se mantienen sin cambios respecto de v2.
; convertir_z_mg tiene offset/factor provisionales y comparte mul16x8.
;
; Hardware: salida X del MMA7361 conectada a RA1/AN1 (pata 3 del PIC16F887).
; La lectura ADC se realiza antes con leer_adc (adc.inc) usando el canal AN1.
;
; No incluye: leer_adc, mul8x8 ni mul16x8 (ver adc.inc y matematicas.inc).
;
; Dependencias:
;   - Rutina externa: mul16x8 (matematicas.inc), que a su vez llama a mul8x8.
;   - Constantes definidas en handmotion_work.S (no se redefinen aqui):
;       X_MG_NUM (49): factor de escala en mg por cuenta, multiplicado antes
;                      de dividir por 8.
;       Y_OFFSET_H:L (338): offset nominal de cero g para Y.
;       Z_OFFSET_H:L (338) y Z_MG_NUM (49): valores PROVISIONALES de Z,
;       pendientes de calibracion fisica.
;   - Variables de RAM comun definidas en handmotion_work.S (no se redefinen aqui):
;       ADC_L, ADC_H   entrada (lectura del eje actual, escrita por leer_adc)
;       DELTA_L, DELTA_H  entrada/salida de la conversion
;       FLAGS          bit 0 = signo del resultado
;       MUL_A, MUL_B, RES_L, RES_M, RES_H, MC_L, MC_H, COUNT, TMP, PROD_H
;                      usadas por mul16x8 y mul8x8
;       Y_SIGN, Z_SIGN bit 0 = signo temporal; no pisan FLAGS<0> de X
;   - Variables de banco 0 definidas en handmotion_work.S (no se redefinen aqui):
;       X_OFF_L, X_OFF_H  offset de 0 g de X (valor por defecto 338 = 0x0152,
;                         ajustable con SET_OFFSET)
;       Y_L, Y_H, Y_MG_L, Y_MG_H  muestra ADC y resultado Y
;       Z_L, Z_H, Z_MG_L, Z_MG_H  muestra ADC y resultado Z
;   - Registros SFR: STATUS (bits C, DC y Z, y bits RP1:RP0 usados por BANKSEL).
;   - Este archivo debe incluirse dentro de un PSECT de codigo, igual que en
;     handmotion_work.S. No debe incluirse junto con handmotion.S sin eliminar
;     antes las copias de convertir_x_mg/convertir_y_mg: las etiquetas se repiten.
;
; CORRECCION DEL ACARREO EN LA NEGACION COMPLEMENTO A DOS:
;   INCF modifica Z, no C. El acarreo del byte bajo al byte alto se detecta
;   con BTFSC STATUS,2 (Z=1 cuando el incremento dio 0x00). Se aplica en las
;   dos negaciones: la conversion a magnitud y la restauracion del signo.
;   Antes se comprobaba STATUS,0 (C), que en esos puntos no reflejaba el
;   acarreo real. Ejemplo: ADC=337, offset=338 -> -6 mg (antes -1318 mg).
;   Verificado ejecutando el codigo real con un emulador PIC16 (9216 casos
;   ADC 0..1023 con varios offsets, comparados con floor(|x|*49/8)).
;   Pendiente: prueba en hardware con el MMA7361 real.
;*******************************************************************************

;*******************************************************************************
; @brief    Convierte las cuentas del eje X a miligramos con signo.
;
; @details  Resta el offset de 0 g guardado en X_OFF_H:X_OFF_L (338 cuentas
;           nominales para VCC = 3,3 V, ajustable por SET_OFFSET), multiplica
;           la magnitud por X_MG_NUM (49) y divide por 8 mediante tres
;           desplazamientos a la derecha de 24 bits. Resultado: 6,125 mg por
;           cuenta. La sensibilidad y el offset son NOMINALES del MMA7361
;           (+-1,5 g, 800 mV/g); deben calibrarse con el acelerometro real.
;
;           Pasos reales de la rutina:
;             1. Copia ADC_H:ADC_L en DELTA_H:DELTA_L.
;             2. Resta X_OFF_H:X_OFF_L de DELTA_H:DELTA_L (con acarreo).
;             3. Si el resultado es negativo (C = 0 tras la resta alta),
;                toma su magnitud por complemento a dos y pone FLAGS<0> = 1;
;                si es positivo o cero, pone FLAGS<0> = 0.
;             4. Llama a mul16x8: RES_H:RES_M:RES_L = magnitud * X_MG_NUM.
;             5. Divide por 8 con tres RRF sobre RES_H:RES_M:RES_L.
;             6. Copia RES_M:RES_L en DELTA_H:DELTA_L.
;             7. Si FLAGS<0> = 1, aplica complemento a dos a DELTA_H:DELTA_L.
;           En los pasos 3 y 7 el acarreo entre bytes usa Z (ver encabezado).
;
; @param    ADC_H:ADC_L = cuentas del eje X (10 bits, resultado de leer_adc
;                         con el canal AN1)
; @return   DELTA_H:DELTA_L = aceleracion en mg, pensada como complemento a dos
;                             de 16 bits (ver CORRECCION en el encabezado)
; @modifica W, STATUS (RP1:RP0, C, DC, Z), DELTA_L, DELTA_H,
;           FLAGS<0>, MUL_A, MUL_B, RES_L, RES_M, RES_H, MC_L, MC_H, COUNT,
;           TMP, PROD_H
;*******************************************************************************
convertir_x_mg:
        BANKSEL X_OFF_L
        MOVF    ADC_L,W
        MOVWF   DELTA_L
        MOVF    ADC_H,W
        MOVWF   DELTA_H
        MOVF    X_OFF_L,W
        SUBWF   DELTA_L,F
        MOVF    X_OFF_H,W
        BTFSS   STATUS,0
        ADDLW   1
        SUBWF   DELTA_H,F
        BTFSC   STATUS,0
        GOTO    x_positivo
        COMF    DELTA_L,F
        COMF    DELTA_H,F
        INCF    DELTA_L,F
        BTFSC   STATUS,2        ; Z=1: acarreo al byte alto
        INCF    DELTA_H,F
        BSF     FLAGS,0         ; signo negativo
        GOTO    x_magnitud
x_positivo:
        BCF     FLAGS,0
x_magnitud:
        MOVLW   X_MG_NUM
        MOVWF   MUL_B
        CALL    mul16x8
        ; divide por 8: tres desplazamientos a la derecha de 24 bits
        BCF     STATUS,0
        RRF     RES_H,F
        RRF     RES_M,F
        RRF     RES_L,F
        BCF     STATUS,0
        RRF     RES_H,F
        RRF     RES_M,F
        RRF     RES_L,F
        BCF     STATUS,0
        RRF     RES_H,F
        RRF     RES_M,F
        RRF     RES_L,F
        MOVF    RES_L,W
        MOVWF   DELTA_L
        MOVF    RES_M,W
        MOVWF   DELTA_H
        BTFSS   FLAGS,0
        RETURN
        COMF    DELTA_L,F
        COMF    DELTA_H,F
        INCF    DELTA_L,F
        BTFSC   STATUS,2        ; Z=1: acarreo al byte alto
        INCF    DELTA_H,F
        RETURN

;*******************************************************************************
; @brief    Convierte las cuentas del eje Y a miligramos con signo.
;
; @details  Usa el offset nominal Y_OFFSET_H:L = 338 y el factor compartido
;           X_MG_NUM = 49: Y_mg = (ADC_Y - 338) * 49 / 8. Guarda el signo
;           temporal en Y_SIGN para no modificar FLAGS<0>, que conserva el
;           signo de X usado por el display. DELTA_H:L y los temporales de
;           mul16x8 se reutilizan solo despues de haber guardado X_MG_H:L.
;           La sensibilidad y el offset son nominales; requieren calibracion
;           fisica del MMA7361 y del VDD/VREF real.
;
; @param    ADC_H:ADC_L = cuentas del eje Y (10 bits, canal AN5)
; @return   Y_MG_H:Y_MG_L = aceleracion Y en mg, complemento a dos de 16 bits
; @modifica W, STATUS, DELTA_L, DELTA_H, Y_SIGN, Y_MG_L, Y_MG_H,
;           MUL_A, MUL_B, RES_L, RES_M, RES_H, MC_L, MC_H, COUNT, TMP, PROD_H
;*******************************************************************************
convertir_y_mg:
        BANKSEL Y_MG_L
        MOVF    ADC_L,W
        MOVWF   DELTA_L
        MOVF    ADC_H,W
        MOVWF   DELTA_H
        MOVLW   Y_OFFSET_L
        SUBWF   DELTA_L,F
        MOVLW   Y_OFFSET_H
        BTFSS   STATUS,0
        ADDLW   1
        SUBWF   DELTA_H,F
        BTFSC   STATUS,0
        GOTO    y_positivo
        COMF    DELTA_L,F
        COMF    DELTA_H,F
        INCF    DELTA_L,F
        BTFSC   STATUS,2        ; Z=1: acarreo al byte alto
        INCF    DELTA_H,F
        BSF     Y_SIGN,0
        GOTO    y_magnitud
y_positivo:
        BCF     Y_SIGN,0
y_magnitud:
        MOVLW   X_MG_NUM
        MOVWF   MUL_B
        CALL    mul16x8
        ; Divide por 8: tres desplazamientos a la derecha de 24 bits.
        BCF     STATUS,0
        RRF     RES_H,F
        RRF     RES_M,F
        RRF     RES_L,F
        BCF     STATUS,0
        RRF     RES_H,F
        RRF     RES_M,F
        RRF     RES_L,F
        BCF     STATUS,0
        RRF     RES_H,F
        RRF     RES_M,F
        RRF     RES_L,F
        MOVF    RES_L,W
        MOVWF   DELTA_L
        MOVF    RES_M,W
        MOVWF   DELTA_H
        BTFSS   Y_SIGN,0
        GOTO    y_guardar
        COMF    DELTA_L,F
        COMF    DELTA_H,F
        INCF    DELTA_L,F
        BTFSC   STATUS,2        ; Z=1: acarreo al byte alto
        INCF    DELTA_H,F
y_guardar:
        BANKSEL Y_MG_L
        MOVF    DELTA_L,W
        MOVWF   Y_MG_L
        MOVF    DELTA_H,W
        MOVWF   Y_MG_H
        RETURN

;*******************************************************************************
; @brief    Convierte las cuentas del eje Z a miligramos con signo.
;
; @details  Hipotesis de arranque, NO calibrada:
;           Z_mg = (ADC_Z - Z_OFFSET_H:L) * Z_MG_NUM / 8.
;           Z_OFFSET_H:L=338 y Z_MG_NUM=49 son valores provisionales tomados
;           como punto de partida, no mediciones de Z. Medir cero-g y
;           sensibilidad del eje Z con el modulo y VDD/VREF reales antes de
;           usar los valores para analisis.
;
;           Usa DELTA_H:L y el workspace de mul16x8 solo despues de que X e Y
;           quedaron guardados en X_MG_H:L e Y_MG_H:L. Z_SIGN conserva el
;           signo temporal sin modificar FLAGS<0> de X ni Y_SIGN.
;           ADC de 10 bits y los factores provisionales producen un resultado
;           dentro de signed 16-bit; la rutina no satura.
;
; @param    ADC_H:ADC_L = cuentas del eje Z (10 bits, canal AN6)
; @return   Z_MG_H:Z_MG_L = aceleracion Z en mg, complemento a dos de 16 bits
; @modifica W, STATUS, DELTA_L, DELTA_H, Z_SIGN, Z_MG_L, Z_MG_H,
;           MUL_A, MUL_B, RES_L, RES_M, RES_H, MC_L, MC_H, COUNT, TMP, PROD_H
;*******************************************************************************
convertir_z_mg:
        BANKSEL Z_MG_L
        MOVF    ADC_L,W
        MOVWF   DELTA_L
        MOVF    ADC_H,W
        MOVWF   DELTA_H
        MOVLW   Z_OFFSET_L
        SUBWF   DELTA_L,F
        MOVLW   Z_OFFSET_H
        BTFSS   STATUS,0
        ADDLW   1
        SUBWF   DELTA_H,F
        BTFSC   STATUS,0
        GOTO    z_positivo
        COMF    DELTA_L,F
        COMF    DELTA_H,F
        INCF    DELTA_L,F
        BTFSC   STATUS,2        ; Z=1: acarreo al byte alto
        INCF    DELTA_H,F
        BSF     Z_SIGN,0
        GOTO    z_magnitud
z_positivo:
        BCF     Z_SIGN,0
z_magnitud:
        MOVLW   Z_MG_NUM
        MOVWF   MUL_B
        CALL    mul16x8
        ; Divide por 8: tres desplazamientos a la derecha de 24 bits.
        BCF     STATUS,0
        RRF     RES_H,F
        RRF     RES_M,F
        RRF     RES_L,F
        BCF     STATUS,0
        RRF     RES_H,F
        RRF     RES_M,F
        RRF     RES_L,F
        BCF     STATUS,0
        RRF     RES_H,F
        RRF     RES_M,F
        RRF     RES_L,F
        MOVF    RES_L,W
        MOVWF   DELTA_L
        MOVF    RES_M,W
        MOVWF   DELTA_H
        BTFSS   Z_SIGN,0
        GOTO    z_guardar
        COMF    DELTA_L,F
        COMF    DELTA_H,F
        INCF    DELTA_L,F
        BTFSC   STATUS,2        ; Z=1: acarreo al byte alto
        INCF    DELTA_H,F
z_guardar:
        BANKSEL Z_MG_L
        MOVF    DELTA_L,W
        MOVWF   Z_MG_L
        MOVF    DELTA_H,W
        MOVWF   Z_MG_H
        RETURN
