;*******************************************************************************
; MODULO TEMPERATURA - Conversion de cuentas ADC del LM35 a grados Celsius
;
; Rutina trasladada sin cambios de logica desde firmware/src/handmotion.S
; (referencia original, no modificada): convertir_temp.
;
; Hardware: LM35 (VOUT, pata 2 del U4) conectado a RA0/AN0 (pata 2 del PIC16F887).
;
; No incluye: la lectura del ADC (leer_adc, en adc.inc) ni la alarma por
; temperatura (procesar_alarma, en alarmas.inc).
;
; Dependencias:
;   - Rutina externa: mul8x8 (matematicas.inc). Debe estar incluida y ser
;     alcanzable por CALL desde este modulo.
;   - Entrada de datos: ADC_H:ADC_L, cargados previamente por leer_adc
;     (adc.inc) con el canal AN0.
;   - Constante definida en handmotion.S (no se redefine aqui):
;       TEMP_MAX (99): limite superior de TEMP_C.
;   - Variables de RAM definidas en handmotion.S (no se redefinen aqui):
;       ADC_L, ADC_H            RAM comun (0x70-0x7F)
;       MUL_A, MUL_B, RES_L,
;       RES_H, MC_L, MC_H,
;       COUNT                   RAM comun, usadas por mul8x8
;       TEMP_C                  banco 0 (udata_bank0)
;   - Registros SFR: STATUS (bits C, DC, Z y RP1:RP0, usados por BANKSEL).
;     No usa SFR de perifericos.
;   - Este archivo debe incluirse dentro de un PSECT de codigo, igual que en
;     handmotion.S. No debe incluirse junto con handmotion.S sin eliminar antes
;     la copia de convertir_temp: la etiqueta se repetiria.
;*******************************************************************************

;*******************************************************************************
; @brief    Convierte las cuentas del LM35 a grados Celsius.
;
; @details  T = cuentas * 125 / 256, redondeado. Si el resultado supera
;           TEMP_MAX (99 C) se satura, porque el display de dos digitos no
;           muestra valores mayores. Si ADC_H != 0 la cuenta es >= 256, es
;           decir 125 C o mas, y tambien se satura.
;
;           Pasos reales de la rutina:
;             1. Selecciona el banco de TEMP_C.
;             2. Si ADC_H != 0, salta a temp_sat (TEMP_C = TEMP_MAX).
;             3. Calcula ADC_L * 125 con mul8x8 (producto de 16 bits).
;             4. Suma 128 (redondeo) y propaga el acarreo a RES_H.
;             5. Si RES_H > TEMP_MAX, salta a temp_sat.
;             6. Copia RES_H en TEMP_C.
;
; @param    ADC_H:ADC_L = cuentas del LM35 (10 bits, resultado de leer_adc)
; @return   TEMP_C = temperatura en grados C (0..99)
; @modifica W, STATUS (RP1:RP0, C, DC, Z), MUL_A, MUL_B, RES_L,
;           RES_H, MC_L, MC_H, COUNT, TEMP_C
;*******************************************************************************
convertir_temp:
        BANKSEL TEMP_C
        MOVF    ADC_H,W
        BTFSS   STATUS,2
        GOTO    temp_sat
        MOVF    ADC_L,W
        MOVWF   MUL_A
        MOVLW   125
        MOVWF   MUL_B
        CALL    mul8x8
        MOVLW   128             ; redondeo: +0,5 cuenta de salida
        ADDWF   RES_L,F
        BTFSC   STATUS,0
        INCF    RES_H,F
        MOVF    RES_H,W
        SUBLW   TEMP_MAX
        BTFSS   STATUS,0        ; C = 0 -> RES_H > 99
        GOTO    temp_sat
        MOVF    RES_H,W
        MOVWF   TEMP_C
        RETURN
temp_sat:
        MOVLW   TEMP_MAX
        MOVWF   TEMP_C
        RETURN
