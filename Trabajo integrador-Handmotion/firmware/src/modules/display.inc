;*******************************************************************************
; MODULO DE DISPLAY - Etapa 4
;
; Tres displays de 7 segmentos, anodo comun. Los segmentos RD0-RD7 son
; activos en bajo. RC0-RC2 seleccionan el digito; nivel alto habilita el
; BC337 conectado como seguidor de emisor en el lado alto.
;
; TIMER1 usa reloj interno FOSC/4, prescaler 1:1 y recarga 0xF830 para un
; periodo nominal de 1 ms. El principal sondea TMR1IF; no hay ISR.
;
; La salida alta del seguidor de emisor queda aproximadamente un VBE debajo
; de VDD. Confirmar corriente y brillo en banco antes de conectar todos los
; segmentos. No se fijan valores de R9-R19 en este modulo.
;*******************************************************************************

;-------------------------------------------------------------------------------
; @brief Inicia TIMER1 para el multiplexado.
;-------------------------------------------------------------------------------
display_init:
        BANKSEL T1CON
        CLRF    T1CON           ; detenido mientras se carga la precarga

        BANKSEL TMR1H
        MOVLW   TMR1_RELOAD_H
        MOVWF   TMR1H
        MOVLW   TMR1_RELOAD_L
        MOVWF   TMR1L

        BANKSEL PIR1
        BCF     PIR1,0          ; TMR1IF

        BANKSEL T1CON
        MOVLW   0x01            ; TMR1ON=1, FOSC/4, prescaler 1:1
        MOVWF   T1CON
        RETURN

;-------------------------------------------------------------------------------
; @brief Avanza un digito cuando TIMER1 vence.
; @details El orden es decenas, unidades y C. FLAGS<2:1> guardan el estado.
;          FLAGS<0> sigue reservado al signo de DELTA.
;-------------------------------------------------------------------------------
display_service:
        BANKSEL PIR1
        BTFSS   PIR1,0          ; TMR1IF=1 si vencio el milisegundo
        RETURN
        BCF     PIR1,0

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
        MOVF    TMP,W           ; TMP = decenas
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
        MOVF    COUNT,W         ; COUNT = unidades
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
        MOVLW   10              ; indice especial para C
        MOVWF   TMP
        CALL    display_pattern
        BANKSEL PORTD
        MOVWF   PORTD
        BANKSEL PORTC
        BSF     PORTC,2
        BCF     FLAGS,2         ; siguiente: decenas (00)
        RETURN

;-------------------------------------------------------------------------------
; @brief Divide TEMP_C por 10 mediante restas sucesivas.
; @return TMP = decenas; COUNT = unidades.
;-------------------------------------------------------------------------------
display_split_temp:
        MOVF    TEMP_C,W
        MOVWF   COUNT
        CLRF    TMP
display_split_loop:
        MOVLW   10
        SUBWF   COUNT,W         ; C=1 mientras COUNT >= 10
        BTFSS   STATUS,0
        RETURN
        MOVWF   COUNT
        INCF    TMP,F
        GOTO    display_split_loop

;-------------------------------------------------------------------------------
; @brief Convierte un indice 0-9 o 10 (C) a segmentos activos en bajo.
; @return W = patron para PORTD (RD0=a ... RD6=g, RD7=dp).
;-------------------------------------------------------------------------------
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
        MOVLW   0xFF            ; valor fuera de rango: display en blanco
        RETURN

display_pattern_0:
        MOVLW   0xC0
        RETURN
display_pattern_1:
        MOVLW   0xF9
        RETURN
display_pattern_2:
        MOVLW   0xA4
        RETURN
display_pattern_3:
        MOVLW   0xB0
        RETURN
display_pattern_4:
        MOVLW   0x99
        RETURN
display_pattern_5:
        MOVLW   0x92
        RETURN
display_pattern_6:
        MOVLW   0x82
        RETURN
display_pattern_7:
        MOVLW   0xF8
        RETURN
display_pattern_8:
        MOVLW   0x80
        RETURN
display_pattern_9:
        MOVLW   0x90
        RETURN
display_pattern_C:
        MOVLW   0xC6
        RETURN
