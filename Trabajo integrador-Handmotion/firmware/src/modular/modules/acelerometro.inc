;===============================================================================
; Trabajo Integrador: HAND MOTION
; Modulo: Acelerometro
;
; Autores:
;   - Conde Ana Victoria
;   - Lurgo Donato 
;
; Fecha: 17/11/2026
; Microcontrolador: PIC16F887
;
; Descripcion:
;   Rutinas de conversion de las muestras X, Y y Z del acelerometro
;   MMA7361 a valores de aceleracion expresados en miligravedades (mg).
;
;===============================================================================

;===============================================================================
; @brief Convierte la muestra del eje X a miligravedades.
;
; @details Resta el offset configurable y aplica el factor de conversion
;          49/8 miligravedades por cuenta. El resultado conserva el signo.
;
; @param  ADC_H:ADC_L = muestra ADC del eje X (AN1).
; @return DELTA_H:DELTA_L = aceleracion X en mg.
;===============================================================================
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
; Divide el resultado por 8.
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

;===============================================================================
; @brief Convierte la muestra del eje Y a miligravedades.
;
; @details Utiliza un offset nominal de 338 cuentas y el factor de
;          conversion 49/8 miligravedades por cuenta.
;          Almacena el signo en Y_SIGN para preservar FLAGS.
;
; @param  ADC_H:ADC_L = muestra ADC del eje Y (AN5).
; @return Y_MG_H:Y_MG_L = aceleracion Y en mg.
;===============================================================================
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

;===============================================================================
; @brief Convierte la muestra del eje Z a miligravedades.
;
; @details Utiliza el offset y el factor de conversion definidos
;          para el eje Z. Calcula la magnitud y conserva el signo
;          en Z_SIGN.
;
; @param  ADC_H:ADC_L = muestra ADC del eje Z (AN6).
; @return Z_MG_H:Z_MG_L = aceleracion Z en mg.
;===============================================================================
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
