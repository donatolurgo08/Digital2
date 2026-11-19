;===============================================================================
; Trabajo Integrador: HAND MOTION
; Modulo: Temperatura
;
; Autores:
;   - Conde Ana Victoria
;   - Lurgo Donato
;
; Fecha: 17/11/2026
; Microcontrolador: PIC16F887
;
; Descripcion:
;   Conversion de las muestras del sensor LM35 a grados Celsius.
;   Incluye redondeo y limitacion del valor maximo de temperatura.
;
;===============================================================================

;===============================================================================
; @brief Convierte la lectura ADC del LM35 a grados Celsius.
;
; @details Aplica la relacion T = cuentas * 125 / 256.
;          Redondea el resultado y limita la temperatura al valor
;          definido por TEMP_MAX.
;
; @param ADC_H:ADC_L = muestra ADC del canal AN0.
; @return TEMP_C = temperatura en grados Celsius (0 a 99).
; @modifica W, STATUS, MUL_A, MUL_B, RES_L, RES_H,
;           MC_L, MC_H, COUNT y TEMP_C.
;===============================================================================
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
        MOVLW   128             ; Suma 128 para redondear el resultado.
        ADDWF   RES_L,F
        BTFSC   STATUS,0
        INCF    RES_H,F
        MOVF    RES_H,W
        SUBLW   TEMP_MAX
        BTFSS   STATUS,0        ; Limita la temperatura al valor maximo permitido.
        GOTO    temp_sat
        MOVF    RES_H,W
        MOVWF   TEMP_C
        RETURN
temp_sat:
        MOVLW   TEMP_MAX
        MOVWF   TEMP_C
        RETURN
