;*******************************************************************************
; MODULO ALARMAS - Alarma por sobretemperatura
;
; Rutinas trasladadas sin cambios de logica desde firmware/src/handmotion.S
; (referencia original, no modificada): procesar_alarma, alarma_on y
; alarma_off.
;
; Hardware:
;   LED1      RA2 (pata 4 del PIC16F887)   salida, activa-alta
;   LED2      RA5 (pata 7 del PIC16F887)   salida, activa-alta
;   BZ_CTRL   RC3 (pata 18 del PIC16F887)  salida, activa-baja (buzzer MDU1095)
;     RC3 = 0: buzzer encendido.   RC3 = 1: buzzer apagado.
;
; Logica: la alarma se activa cuando TEMP_C > ALARM_TEMP (comparacion estricta).
;
; No incluye: el calculo de TEMP_C (convertir_temp, en temperatura.inc), ni la
; configuracion de TRISA/TRISC (init), ni el envio del estado en DATA
; (send_data, en uart.inc).
;
; Dependencias:
;   - buzzer_service es una rutina publica llamada desde el bucle principal.
;     Las ramas alarma_on y alarma_off son alcanzadas por salto desde
;     procesar_alarma, no por CALL.
;   - Constantes definidas en handmotion_work.S (no se redefinen aqui):
;       TEMP_ALARM (40): valor con el que uart_init carga ALARM_TEMP al
;                        arrancar. Es una constante, no la variable.
;       BUZZ_DIVISOR, BUZZ_ON_UNITS, BUZZ_OFF_UNITS: parametros de tiempo.
;   - Variables definidas en handmotion_work.S (no se redefinen aqui):
;       TEMP_C      banco 0 (udata_bank0): temperatura en grados C.
;       ALARM_TEMP  banco 0 (udata_bank0): umbral de alarma. Lo puede cambiar
;                   el comando SET_THRESHOLD (uart.inc).
;       ALARM_STATE banco 0 (udata_bank0): bit 0 = alarma termica activa.
;       BUZZ_DIV, BUZZ_CNT, BUZZ_PHASE: estado del patron sonoro.
;   - Registros SFR: STATUS (bits C, DC, Z y bits RP1:RP0), PORTA (RA2, RA5),
;     PORTC (RC3). Requiere que TRISA<2,5> y TRISC<3> sean salidas, lo que
;     configura init en handmotion.S.
;   - Este archivo debe incluirse dentro de un PSECT de codigo, igual que en
;     handmotion.S. No debe incluirse junto con handmotion.S sin eliminar antes
;     las copias de procesar_alarma, alarma_on y alarma_off: las etiquetas se
;     repetirian.
;*******************************************************************************

;*******************************************************************************
; @brief    Actualiza las salidas de alarma segun la temperatura.
;
; @details  Si TEMP_C > ALARM_TEMP (40 C por defecto, configurable por
;           SET_THRESHOLD), activa LED1 (RA2) y LED2 (RA5). ALARM_STATE<0>
;           refleja la alarma termica y viaja en la trama DATA. buzzer_service
;           controla por separado el patron intermitente del buzzer.
;
;           Logica real: calcula W = ALARM_TEMP - TEMP_C con SUBWF. El bit C
;           queda en 1 cuando TEMP_C <= ALARM_TEMP; en ese caso salta a
;           alarma_off. En cualquier otro caso (TEMP_C > ALARM_TEMP) continua
;           con alarma_on.
;
; @param    TEMP_C = temperatura en grados C
; @return   ninguno
; @modifica W, STATUS (RP1:RP0, C, DC, Z), ALARM_STATE<0>, PORTA<2,5>
;*******************************************************************************
procesar_alarma:
        BANKSEL ALARM_TEMP
        MOVF    TEMP_C,W
        SUBWF   ALARM_TEMP,W    ; W = umbral - TEMP_C; C=1 si TEMP_C <= umbral
        BTFSC   STATUS,0
        GOTO    alarma_off

;*******************************************************************************
; @brief    Enciende los LED de alarma. Rama de procesar_alarma.
;
; @details  Se alcanza solo desde procesar_alarma (continuacion sin salto)
;           cuando TEMP_C > ALARM_TEMP. Pone ALARM_STATE<0> = 1, pone en 1
;           RA2 (LED1) y RA5 (LED2). El buzzer se gestiona de forma no
;           bloqueante por buzzer_service; esta rutina no escribe RC3.
;
; @param    ninguno
; @return   ninguno
; @modifica STATUS (RP1:RP0), ALARM_STATE<0>, PORTA<2,5>
;*******************************************************************************
alarma_on:
        BSF     ALARM_STATE,0
        BANKSEL PORTA
        BSF     PORTA,2        ; LED1, pin 4 / RA2
        BSF     PORTA,5        ; LED2, pin 7 / RA5
        RETURN

;*******************************************************************************
; @brief    Apaga la alarma: LED1, LED2 y buzzer. Rama de procesar_alarma.
;
; @details  Se alcanza desde procesar_alarma mediante GOTO cuando
;           TEMP_C <= ALARM_TEMP. Pone ALARM_STATE<0> = 0, pone en 0 RA2 y
;           RA5, y pone inmediatamente RC3 = 1 para apagar el buzzer. Tambien
;           reinicia el estado temporal, para que no quede una fase pendiente.
;
; @param    ninguno
; @return   ninguno
; @modifica STATUS (RP1:RP0), ALARM_STATE<0>, PORTA<2,5>, PORTC<3>,
;           BUZZ_DIV, BUZZ_CNT, BUZZ_PHASE
;*******************************************************************************
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

;*******************************************************************************
; @brief    Atiende el patron no bloqueante del buzzer activo.
;
; @details  Se llama despues de display_service y antes de uart_service.
;           Solo LEE TICK_FLAG<0>; no lo limpia, por lo que uart_service
;           conserva su tick de 1 ms para el protocolo. Divide esos ticks por
;           BUZZ_DIVISOR (10): mantiene RC3=0 durante BUZZ_ON_UNITS (20)
;           unidades = 200 ms, y RC3=1 durante BUZZ_OFF_UNITS (80) unidades
;           = 800 ms. La fase de encendido comienza inmediatamente al detectar
;           ALARM_STATE<0>. Si la alarma se apaga, alarma_off apaga RC3 y limpia
;           los contadores sin esperar otro tick.
;
;           El MDU1095 es activo y genera su propia frecuencia; esta rutina
;           solo controla su encendido/apagado. No usa PWM ni retardos.
;
; @param    ALARM_STATE<0>, TICK_FLAG<0>
; @return   ninguno
; @modifica W, STATUS, BUZZ_DIV, BUZZ_CNT, BUZZ_PHASE, PORTC<3>
;*******************************************************************************
buzzer_service:
        BANKSEL ALARM_STATE
        BTFSS   ALARM_STATE,0
        GOTO    buzzer_idle

        ; Al comenzar una alarma, iniciar inmediatamente la fase de 200 ms.
        BANKSEL BUZZ_CNT
        MOVF    BUZZ_CNT,F
        BTFSC   STATUS,2
        GOTO    buzzer_start_on

        ; La base de 1 ms la genera display_service. No consumir la bandera:
        ; uart_service la limpia y la usa para PERIOD_CNT.
        BANKSEL TICK_FLAG
        BTFSS   TICK_FLAG,0
        RETURN

        BANKSEL BUZZ_DIV
        INCF    BUZZ_DIV,F
        MOVLW   BUZZ_DIVISOR
        SUBWF   BUZZ_DIV,W
        BTFSS   STATUS,2
        RETURN

        ; Acumular 10 ticks de 1 ms = una unidad de fase de 10 ms.
        CLRF    BUZZ_DIV
        DECFSZ  BUZZ_CNT,F
        RETURN

        ; Fin de fase: si estaba encendido, pasar a apagado por 800 ms.
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
        ; Estado seguro e inmediato mientras la alarma termica esta apagada.
        BANKSEL BUZZ_DIV
        CLRF    BUZZ_DIV
        CLRF    BUZZ_CNT
        BCF     BUZZ_PHASE,0
        BANKSEL PORTC
        BSF     PORTC,3
        RETURN
