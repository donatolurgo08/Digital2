;===============================================================================
; Trabajo Integrador: HAND MOTION
; Modulo: Visualizacion en displays
;
; Autores:
;   - Conde Ana Victoria
;   - Lurgo Donato
;
; Fecha: 17/11/2026
; Microcontrolador: PIC16F887
;
; Descripcion:
;   Control de tres displays de siete segmentos mediante multiplexado.
;   Utiliza TIMER1 para establecer una base de tiempo nominal de 1 ms.
;   Muestra la temperatura medida en grados Celsius.
;
;===============================================================================

;===============================================================================
; @brief Inicializa TIMER1 para el multiplexado de los displays.
;
; @details Configura el reloj interno FOSC/4, prescaler 1:1 y
;          precarga 0xF830 para obtener un periodo nominal de 1 ms.
;
; @param Ninguno.
; @return Ninguno.
; @modifica T1CON, TMR1H, TMR1L, PIR1 y W.
;===============================================================================
display_init:
        BANKSEL T1CON
        CLRF    T1CON          ; Detiene TIMER1 durante la configuracion.

        BANKSEL TMR1H
        MOVLW   TMR1_RELOAD_H
        MOVWF   TMR1H
        MOVLW   TMR1_RELOAD_L
        MOVWF   TMR1L

        BANKSEL PIR1
        BCF     PIR1,0          ; Limpia la bandera de TIMER1.

        BANKSEL T1CON
        MOVLW   0x01            ; Habilita TIMER1 con prescaler 1:1.
        MOVWF   T1CON
        RETURN

;===============================================================================
; @brief Actualiza los displays cuando vence TIMER1.
;
; @details Alterna entre los dígitos de decenas, unidades y el símbolo C.
;          Apaga los dígitos antes de actualizar los segmentos para
;          evitar activaciones simultáneas.
;          También genera TICK_FLAG para el protocolo serie.
;
; @param TEMP_C = temperatura medida.
; @return Visualizacion actualizada en PORTC y PORTD.
; @modifica PIR1, TMR1H, TMR1L, PORTC, PORTD, FLAGS,
;           TICK_FLAG y W.
;===============================================================================
display_service:
        BANKSEL PIR1
        BTFSS   PIR1,0          ; Comprueba si vencio el periodo de TIMER1.
        RETURN
        BCF     PIR1,0
        BANKSEL TICK_FLAG
        BSF     TICK_FLAG,0     ; Genera el tick de 1 ms.

        BANKSEL TMR1H
        MOVLW   TMR1_RELOAD_H
        MOVWF   TMR1H
        MOVLW   TMR1_RELOAD_L
        MOVWF   TMR1L

        ; Apaga los tres digitos antes de cambiar segmentos (sin ghosting).
        BANKSEL PORTC
        BCF     PORTC,0
        BCF     PORTC,1
        BCF     PORTC,2

        BTFSC   FLAGS,1
        GOTO    display_digit_units
        BTFSC   FLAGS,2
        GOTO    display_digit_c

; Estado 00: decenas.
display_digit_tens:
        CALL    display_split_temp
        MOVF    TMP,W           ; Guarda las decenas.
        CALL    display_pattern
        BANKSEL PORTD
        MOVWF   PORTD
        BANKSEL PORTC
        BSF     PORTC,0
        BSF     FLAGS,1         ; siguiente: unidades (01)
        RETURN

; Estado 01: unidades.
display_digit_units:
        CALL    display_split_temp
        MOVF    COUNT,W         ; Guarda las unidades.
        MOVWF   TMP
        CALL    display_pattern
        BANKSEL PORTD
        MOVWF   PORTD
        BANKSEL PORTC
        BSF     PORTC,1
        BCF     FLAGS,1
        BSF     FLAGS,2         ; siguiente: C (10)
        RETURN

; Estado 10: letra C estándar (a, d, e, f).
display_digit_c:
        MOVLW   10              ; Selecciona el simbolo C.
        MOVWF   TMP
        CALL    display_pattern
        BANKSEL PORTD
        MOVWF   PORTD
        BANKSEL PORTC
        BSF     PORTC,2
        BCF     FLAGS,2         ; siguiente: decenas (00)
        RETURN

;===============================================================================
; @brief Separa la temperatura en decenas y unidades.
;
; @details Divide TEMP_C por 10 mediante restas sucesivas.
;
; @param TEMP_C = temperatura en grados Celsius.
; @return TMP = decenas; COUNT = unidades.
; @modifica W, TMP, COUNT y STATUS.
;===============================================================================
display_split_temp:
        BANKSEL TEMP_C
        MOVF    TEMP_C,W
        MOVWF   COUNT
        CLRF    TMP
display_split_loop:
        MOVLW   10
        SUBWF   COUNT,W         ; Comprueba si COUNT es mayor o igual a 10.
        BTFSS   STATUS,0
        RETURN
        MOVWF   COUNT
        INCF    TMP,F
        GOTO    display_split_loop

;===============================================================================
; @brief Obtiene el patron de segmentos correspondiente a un indice.
;
; @details Reconoce los digitos del 0 al 9 y la letra C.
;          Los patrones utilizan logica activa en alto.
;
; @param TMP = indice del digito (0-9) o letra C (10).
; @return W = patron de segmentos para PORTD.
; @modifica W y STATUS.
;===============================================================================
display_pattern:
        MOVF    TMP,W
        BTFSC   STATUS,2
        GOTO    display_pattern_0
        MOVF    TMP,W
        XORLW   1
        BTFSC   STATUS,2
        GOTO    display_pattern_1
        MOVF    TMP,W
        XORLW   2
        BTFSC   STATUS,2
        GOTO    display_pattern_2
        MOVF    TMP,W
        XORLW   3
        BTFSC   STATUS,2
        GOTO    display_pattern_3
        MOVF    TMP,W
        XORLW   4
        BTFSC   STATUS,2
        GOTO    display_pattern_4
        MOVF    TMP,W
        XORLW   5
        BTFSC   STATUS,2
        GOTO    display_pattern_5
        MOVF    TMP,W
        XORLW   6
        BTFSC   STATUS,2
        GOTO    display_pattern_6
        MOVF    TMP,W
        XORLW   7
        BTFSC   STATUS,2
        GOTO    display_pattern_7
        MOVF    TMP,W
        XORLW   8
        BTFSC   STATUS,2
        GOTO    display_pattern_8
        MOVF    TMP,W
        XORLW   9
        BTFSC   STATUS,2
        GOTO    display_pattern_9
        MOVF    TMP,W
        XORLW   10
        BTFSC   STATUS,2
        GOTO    display_pattern_C
        MOVLW   0x00            ; Devuelve el display apagado.
        RETURN

display_pattern_0:
        MOVLW   0x3F
        RETURN
display_pattern_1:
        MOVLW   0x06
        RETURN
display_pattern_2:
        MOVLW   0x5B
        RETURN
display_pattern_3:
        MOVLW   0x4F
        RETURN
display_pattern_4:
        MOVLW   0x66
        RETURN
display_pattern_5:
        MOVLW   0x6D
        RETURN
display_pattern_6:
        MOVLW   0x7D
        RETURN
display_pattern_7:
        MOVLW   0x07
        RETURN
display_pattern_8:
        MOVLW   0x7F
        RETURN
display_pattern_9:
        MOVLW   0x6F
        RETURN
display_pattern_C:
        MOVLW   0x39
        RETURN
