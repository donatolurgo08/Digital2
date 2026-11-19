;===============================================================================
; Trabajo Integrador: HAND MOTION
; Modulo: Alarmas
;
; Autores:
;   - Conde Ana Victoria
;   - Lurgo Donato
;
; Fecha: 17/11/2026
; Microcontrolador: PIC16F887
;
; Descripcion:
;   Control de la alarma por sobretemperatura mediante indicadores LED
;   y un buzzer activo. Incluye la gestion temporizada del sonido.
;
;===============================================================================

;===============================================================================
; @brief Controla la alarma segun la temperatura medida.
;
; @details Compara TEMP_C con ALARM_TEMP. Si la temperatura supera
;          el umbral, activa la alarma. En caso contrario, la desactiva.
;
; @param TEMP_C = temperatura medida en grados Celsius.
; @param ALARM_TEMP = umbral de temperatura.
; @modifica W, STATUS y ALARM_STATE.
;===============================================================================
procesar_alarma:
        BANKSEL ALARM_TEMP
        MOVF    TEMP_C,W
        SUBWF   ALARM_TEMP,W    ; W = umbral - TEMP_C; C=1 si TEMP_C <= umbral
        BTFSC   STATUS,0
        GOTO    alarma_off

;===============================================================================
; @brief Activa el estado de alarma.
;
; @details Establece ALARM_STATE y activa los indicadores LED.
;          El buzzer es controlado por separado mediante buzzer_service.
;
; @modifica ALARM_STATE y PORTA.
;===============================================================================
alarma_on:
        BSF     ALARM_STATE,0
        BANKSEL PORTA
        BSF     PORTA,2        ; LED1, pin 4 / RA2
        BSF     PORTA,5        ; LED2, pin 7 / RA5
        RETURN

;===============================================================================
; @brief Desactiva el estado de alarma.
;
; @details Apaga los indicadores LED y el buzzer. Reinicia los
;          contadores y la fase de funcionamiento del sonido.
;
; @modifica ALARM_STATE, PORTA, PORTC, BUZZ_DIV,
;           BUZZ_CNT y BUZZ_PHASE.
;===============================================================================
alarma_off:
        BCF     ALARM_STATE,0
        BANKSEL PORTA
        BCF     PORTA,2
        BCF     PORTA,5
        BANKSEL PORTC
        BSF     PORTC,3        ; BZ_CTRL activo-bajo: 1 apaga el buzzer
        BANKSEL BUZZ_DIV
        CLRF    BUZZ_DIV
        CLRF    BUZZ_CNT
        BCF     BUZZ_PHASE,0
        RETURN

;===============================================================================
; @brief Controla el funcionamiento intermitente del buzzer.
;
; @details Utiliza la base de tiempo de 1 ms para alternar las fases
;          de encendido y apagado sin bloquear el programa principal.
;          El buzzer permanece encendido 200 ms y apagado 800 ms.
;
; @param ALARM_STATE = estado de la alarma.
; @param TICK_FLAG = indicador temporal.
; @modifica W, STATUS, BUZZ_DIV, BUZZ_CNT, BUZZ_PHASE y PORTC.
;===============================================================================
buzzer_service:
        BANKSEL ALARM_STATE
        BTFSS   ALARM_STATE,0
        GOTO    buzzer_idle

; Inicia la fase de encendido de 200 ms.
        BANKSEL BUZZ_CNT
        MOVF    BUZZ_CNT,F
        BTFSC   STATUS,2
        GOTO    buzzer_start_on

; Espera el siguiente tick sin modificar la bandera.
        BANKSEL TICK_FLAG
        BTFSS   TICK_FLAG,0
        RETURN

        BANKSEL BUZZ_DIV
        INCF    BUZZ_DIV,F
        MOVLW   BUZZ_DIVISOR
        SUBWF   BUZZ_DIV,W
        BTFSS   STATUS,2
        RETURN

; Cada 10 ticks de 1 ms se completa una unidad de 10 ms.
        CLRF    BUZZ_DIV
        DECFSZ  BUZZ_CNT,F
        RETURN

; Cambia a la fase de apagado de 800 ms.
        BTFSS   BUZZ_PHASE,0
        GOTO    buzzer_start_on
        BCF     BUZZ_PHASE,0
        MOVLW   BUZZ_OFF_UNITS
        MOVWF   BUZZ_CNT
        BANKSEL PORTC
        BSF     PORTC,3
        RETURN

buzzer_start_on:
        BANKSEL BUZZ_DIV
        CLRF    BUZZ_DIV
        MOVLW   BUZZ_ON_UNITS
        MOVWF   BUZZ_CNT
        BSF     BUZZ_PHASE,0
        BANKSEL PORTC
        BCF     PORTC,3
        RETURN

buzzer_idle:
; Mantiene el buzzer apagado cuando no hay alarma.
        BANKSEL BUZZ_DIV
        CLRF    BUZZ_DIV
        CLRF    BUZZ_CNT
        BCF     BUZZ_PHASE,0
        BANKSEL PORTC
        BSF     PORTC,3
        RETURN
