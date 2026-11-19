;===============================================================================
; Trabajo Integrador: HAND MOTION
; Modulo: Comunicacion UART (EUSART)
;
; Autores:
;   - Conde Ana Victoria
;   - Lurgo Donato
;
; Fecha: 17/11/2026
; Microcontrolador: PIC16F887
;
; Descripcion:
;   Gestion de la comunicacion serie entre el microcontrolador y la
;   interfaz grafica mediante el protocolo HAND MOTION.
;   Incluye transmision, recepcion, validacion CRC8 y procesamiento
;   de comandos.
;
;===============================================================================
; Comunicacion: 9600 Bd, 8 bits de datos, sin paridad y 1 bit de parada.
; Oscilador: 8 MHz. Generador de baud rate: 9615 Bd (error +0,16 %).
;
; Formato de trama:
;   AA 55 | LEN | TIPO | DATOS | CRC8
;
; El CRC8 utiliza polinomio 0x07, valor inicial 0x00 y procesa
; los bytes desde LEN hasta el ultimo dato.
;
; Tramas PIC -> PC:
;   DATA:   temperatura, X, Y, Z y estado de alarma.
;   STATUS: version, periodo, umbral, offset y modo.
;   ACK:    comando recibido y resultado.
;
; Comandos PC -> PIC:
;   PING, START, STOP, SET_THRESHOLD, GET_STATUS y SET_OFFSET.
;
; La comunicacion se gestiona mediante polling, sin interrupciones.
; uart_service atiende la transmision, recepcion y temporizacion.
;===============================================================================
;-------------------------------------------------------------------------------
; Variables locales del modulo (banco 0, asignadas por el linker).
; CRC_REG se reserva para transmision; CRC_RX para recepcion, de modo que una
; trama en curso no se corrompa si send_data se ejecuta durante la recepcion.
;-------------------------------------------------------------------------------
        PSECT   udata_bank0,class=BANK0
CRC_RX:         DS      1       ; CRC8 parcial de recepcion
CRC_CNT_RX:     DS      1       ; contador de bits del CRC de recepcion

        PSECT   code,class=CODE,delta=2

;-------------------------------------------------------------------------------
; @brief Inicializa el modulo EUSART y el protocolo de comunicacion.
; @details Configura la comunicacion serie a 9600 Bd, formato 8N1,
;          y reinicia los buffers, contadores y variables del protocolo.
; @param Ninguno.
; @return Ninguno.
; @modifica TXSTA, BAUDCTL, SPBRG, RCSTA, PIE1 y variables del modulo.
;-------------------------------------------------------------------------------
uart_init:
        BANKSEL TXSTA
        MOVLW   EUSART_TXSTA    ; TXEN=1, BRGH=1, SYNC=0
        MOVWF   TXSTA

        BANKSEL BAUDCTL
        BCF     BAUDCTL,3       ; BRG16=0: generador de 8 bits

        BANKSEL SPBRG
        MOVLW   EUSART_SPBRG    ; 51 -> 9615 Bd
        MOVWF   SPBRG

        BANKSEL RCSTA
        MOVLW   EUSART_RCSTA    ; SPEN=1, CREN=1
        MOVWF   RCSTA

        BANKSEL PIE1
        BCF     PIE1,4          ; TXIE deshabilitado
        BCF     PIE1,5          ; RCIE deshabilitado

        BANKSEL TX_CNT
        CLRF    TX_HEAD
        CLRF    TX_TAIL
        CLRF    TX_CNT
        CLRF    RX_STATE
        CLRF    CRC_REG
        CLRF    SEQ
        CLRF    TICK_FLAG
        CLRF    ALARM_STATE
        MOVLW   PROTO_PERIOD
        MOVWF   PERIOD_MS
        MOVWF   PERIOD_CNT
        MOVLW   TEMP_ALARM
        MOVWF   ALARM_TEMP
        MOVLW   X_OFFSET_L
        MOVWF   X_OFF_L
        MOVLW   X_OFFSET_H
        MOVWF   X_OFF_H
        MOVLW   0x01            ; streaming habilitado desde el reset
        MOVWF   MODO
        RETURN

;-------------------------------------------------------------------------------
; @brief Atiende las tareas de comunicacion serie.
; @details Gestiona la transmision, recepcion y periodo de envio de datos.
;          Procesa un byte de transmision por llamada y vacia la FIFO
;          de recepcion.
; @param Ninguno.
; @return Ninguno.
; @modifica W, FSR y variables del modulo.
;-------------------------------------------------------------------------------
uart_service:
        ;----- Transmision: un byte por pasada -----
        BANKSEL PIR1
        BTFSS   PIR1,4          ; TXIF
        GOTO    uart_rx
        BANKSEL TX_CNT
        MOVF    TX_CNT,W
        BTFSC   STATUS,2        ; buffer vacio
        GOTO    uart_rx
        MOVF    TX_TAIL,W
        ADDLW   LOW(TX_BUF)
        MOVWF   FSR
        MOVF    INDF,W
        BANKSEL TXREG
        MOVWF   TXREG
        BANKSEL TX_TAIL
        MOVF    TX_TAIL,W
        ADDLW   1
        ANDLW   0x1F
        MOVWF   TX_TAIL
        DECF    TX_CNT,F

        ;----- Recepcion: vacia la FIFO del EUSART -----
uart_rx:
        BANKSEL PIR1
        BTFSS   PIR1,5          ; RCIF
        GOTO    uart_tick
        BANKSEL RCSTA
        BTFSC   RCSTA,1          ; OERR
        GOTO    uart_rx_restart
        BTFSC   RCSTA,2          ; FERR: descarta el byte y resincroniza
        GOTO    uart_framing_error
        MOVF    RCREG,W
        CALL    rx_byte
        GOTO    uart_rx         ; puede quedar otro byte en la FIFO
uart_framing_error:
        MOVF    RCREG,W          ; leer RCREG libera el carácter con error
        BANKSEL RX_STATE
        CLRF    RX_STATE
        GOTO    uart_rx
uart_rx_restart:
        BCF     RCSTA,4          ; CREN
        BSF     RCSTA,4          ; CREN
        BANKSEL RX_STATE
        CLRF    RX_STATE         ; descarta la trama parcial tras overrun
        GOTO    uart_tick

        ;----- Base de tiempo de 1 ms y período de muestreo -----
uart_tick:
        BANKSEL TICK_FLAG
        BTFSS   TICK_FLAG,0
        RETURN
        BCF     TICK_FLAG,0
        DECFSZ  PERIOD_CNT,F
        RETURN
        MOVF    PERIOD_MS,W
        MOVWF   PERIOD_CNT
        MOVF    MODO,W
        ANDLW   0x01
        BTFSC   STATUS,2
        RETURN
        CALL    send_data
        RETURN

;-------------------------------------------------------------------------------
; @brief Inserta un byte en el buffer circular de transmision.
; @param W = byte a transmitir.
; @return Ninguno. Descarta el byte si el buffer esta lleno.
; @modifica W, FSR, TMP2, TX_HEAD y TX_CNT.
;-------------------------------------------------------------------------------
tx_push:
        BANKSEL TX_CNT
        MOVWF   TMP2
        MOVF    TX_CNT,W
        XORLW   32
        BTFSC   STATUS,2
        RETURN                  ; buffer lleno
        MOVF    TX_HEAD,W
        ADDLW   LOW(TX_BUF)
        MOVWF   FSR
        MOVF    TMP2,W
        MOVWF   INDF
        MOVF    TX_HEAD,W
        ADDLW   1
        ANDLW   0x1F
        MOVWF   TX_HEAD
        INCF    TX_CNT,F
        RETURN

;-------------------------------------------------------------------------------
; @brief Actualiza el CRC8 de transmision.
; @param W = byte a procesar; CRC_REG = valor parcial.
; @return CRC_REG actualizado.
; @modifica W, CRC_REG y CRC_CNT.
;-------------------------------------------------------------------------------
crc8_update:
        BANKSEL CRC_REG
        XORWF   CRC_REG,F
        MOVLW   8
        MOVWF   CRC_CNT
crc8_loop:
        BTFSS   CRC_REG,7
        GOTO    crc8_shift
        BCF     STATUS,0
        RLF     CRC_REG,F
        MOVLW   PROTO_CRC_POLY
        XORWF   CRC_REG,F
        GOTO    crc8_next
crc8_shift:
        BCF     STATUS,0
        RLF     CRC_REG,F
crc8_next:
        DECFSZ  CRC_CNT,F
        GOTO    crc8_loop
        RETURN

;-------------------------------------------------------------------------------
; @brief Actualiza el CRC8 de recepcion.
; @param W = byte a procesar; CRC_RX = valor parcial.
; @return CRC_RX actualizado.
; @modifica W, CRC_RX y CRC_CNT_RX.
;-------------------------------------------------------------------------------
crc8_update_rx:
        BANKSEL CRC_RX
        XORWF   CRC_RX,F
        MOVLW   8
        MOVWF   CRC_CNT_RX
crc8_loop_rx:
        BTFSS   CRC_RX,7
        GOTO    crc8_shift_rx
        BCF     STATUS,0
        RLF     CRC_RX,F
        MOVLW   PROTO_CRC_POLY
        XORWF   CRC_RX,F
        GOTO    crc8_next_rx
crc8_shift_rx:
        BCF     STATUS,0
        RLF     CRC_RX,F
crc8_next_rx:
        DECFSZ  CRC_CNT_RX,F
        GOTO    crc8_loop_rx
        RETURN

;-------------------------------------------------------------------------------
; @brief Incorpora un byte al CRC y lo encola para transmision.
; @param W = byte a incorporar.
; @return Ninguno.
; @modifica W, TMP2, FSR, CRC_REG, CRC_CNT, TX_HEAD y TX_CNT.
;-------------------------------------------------------------------------------
tx_frame_byte:
        MOVWF   TMP2
        CALL    crc8_update
        MOVF    TMP2,W
        CALL    tx_push
        RETURN

;-------------------------------------------------------------------------------
; @brief Construye y encola una trama DATA version 3.
; @details Incluye secuencia, temperatura, aceleraciones X/Y/Z y alarma.
; @param Ninguno.
; @return Ninguno.
; @modifica W, FSR, TMP2, CRC_REG, CRC_CNT, SEQ, TX_HEAD y TX_CNT.
;-------------------------------------------------------------------------------
send_data:
        BANKSEL MODO
        BTFSS   MODO,0
        RETURN
        MOVF    TX_CNT,W
        SUBLW   18              ; C=1 si TX_CNT <= 18 (libre >= 14)
        BTFSS   STATUS,0
        RETURN

        MOVLW   PROTO_SYNC1
        CALL    tx_push
        MOVLW   PROTO_SYNC2
        CALL    tx_push

        CLRF    CRC_REG
        MOVLW   10              ; TIPO + 9 datos (DATA v3)
        CALL    tx_frame_byte
        MOVLW   T_DATA
        CALL    tx_frame_byte

        MOVF    SEQ,W
        CALL    tx_frame_byte
        INCF    SEQ,F

        MOVF    TEMP_C,W
        CALL    tx_frame_byte
        MOVF    X_MG_L,W
        CALL    tx_frame_byte
        MOVF    X_MG_H,W
        CALL    tx_frame_byte
        MOVF    Y_MG_L,W
        CALL    tx_frame_byte
        MOVF    Y_MG_H,W
        CALL    tx_frame_byte
        MOVF    Z_MG_L,W
        CALL    tx_frame_byte
        MOVF    Z_MG_H,W
        CALL    tx_frame_byte

        CLRF    TMP2
        BTFSC   ALARM_STATE,0
        BSF     TMP2,0
        MOVF    TMP2,W
        CALL    tx_frame_byte

        MOVF    CRC_REG,W
        CALL    tx_push
        RETURN

;-------------------------------------------------------------------------------
; @brief Construye y encola una trama STATUS.
; @details Informa la version del protocolo y la configuracion actual.
; @param Ninguno.
; @return Ninguno.
; @modifica W, FSR, TMP2, CRC_REG, CRC_CNT, TX_HEAD y TX_CNT.
;-------------------------------------------------------------------------------
send_status:
        BANKSEL TX_CNT
        MOVF    TX_CNT,W
        SUBLW   21              ; libre >= 11
        BTFSS   STATUS,0
        RETURN

        MOVLW   PROTO_SYNC1
        CALL    tx_push
        MOVLW   PROTO_SYNC2
        CALL    tx_push

        CLRF    CRC_REG
        MOVLW   7               ; TIPO + 6 datos
        CALL    tx_frame_byte
        MOVLW   T_STATUS
        CALL    tx_frame_byte
        MOVLW   PROTO_VERSION
        CALL    tx_frame_byte
        MOVF    PERIOD_MS,W
        CALL    tx_frame_byte
        MOVF    ALARM_TEMP,W
        CALL    tx_frame_byte
        MOVF    X_OFF_L,W
        CALL    tx_frame_byte
        MOVF    X_OFF_H,W
        CALL    tx_frame_byte
        MOVF    MODO,W
        CALL    tx_frame_byte

        MOVF    CRC_REG,W
        CALL    tx_push
        RETURN

;-------------------------------------------------------------------------------
; @brief Construye y encola una trama de confirmacion ACK.
; @param ACK_CMD = comando recibido; ACK_RES = resultado.
; @return Ninguno.
; @modifica W, FSR, TMP2, CRC_REG, CRC_CNT, TX_HEAD y TX_CNT.
;-------------------------------------------------------------------------------
send_ack:
        BANKSEL TX_CNT
        MOVF    TX_CNT,W
        SUBLW   25              ; libre >= 7
        BTFSS   STATUS,0
        RETURN

        MOVLW   PROTO_SYNC1
        CALL    tx_push
        MOVLW   PROTO_SYNC2
        CALL    tx_push

        CLRF    CRC_REG
        MOVLW   3               ; TIPO + 2 datos
        CALL    tx_frame_byte
        MOVLW   T_ACK
        CALL    tx_frame_byte
        MOVF    ACK_CMD,W
        CALL    tx_frame_byte
        MOVF    ACK_RES,W
        CALL    tx_frame_byte

        MOVF    CRC_REG,W
        CALL    tx_push
        RETURN

;-------------------------------------------------------------------------------
; @brief Procesa un byte recibido mediante una maquina de estados.
; @details Reconoce la sincronizacion, longitud, tipo, datos y CRC.
; @param W = byte recibido.
; @return Ninguno.
; @modifica W, TMP2 y variables de recepcion.
;-------------------------------------------------------------------------------
rx_byte:
        BANKSEL TMP2
        MOVWF   TMP2
        BANKSEL RX_STATE
        MOVF    RX_STATE,W
        XORLW   0
        BTFSC   STATUS,2
        GOTO    rx_state0
        MOVF    RX_STATE,W
        XORLW   1
        BTFSC   STATUS,2
        GOTO    rx_state1
        MOVF    RX_STATE,W
        XORLW   2
        BTFSC   STATUS,2
        GOTO    rx_state2
        MOVF    RX_STATE,W
        XORLW   3
        BTFSC   STATUS,2
        GOTO    rx_state3
        GOTO    rx_state4

; Espera el primer byte de sincronizacion (0xAA).
rx_state0:
        MOVF    TMP2,W
        XORLW   PROTO_SYNC1
        BTFSS   STATUS,2
        RETURN
        MOVLW   1
        MOVWF   RX_STATE
        RETURN

; Espera el segundo byte de sincronizacion (0x55).
rx_state1:
        MOVF    TMP2,W
        XORLW   PROTO_SYNC2
        BTFSC   STATUS,2
        GOTO    rx_sync_ok
        MOVF    TMP2,W
        XORLW   PROTO_SYNC1
        BTFSC   STATUS,2
        RETURN                  ; sigue esperando el segundo byte
        CLRF    RX_STATE
        RETURN
rx_sync_ok:
        MOVLW   2
        MOVWF   RX_STATE
        RETURN

; Recibe y valida la longitud de la trama.
rx_state2:
        MOVF    TMP2,W
        BTFSC   STATUS,2
        GOTO    rx_abort        ; LEN = 0 invalido
        MOVF    TMP2,W
        SUBLW   8
        BTFSS   STATUS,0        ; C=0 -> LEN > 8
        GOTO    rx_abort
        MOVF    TMP2,W
        MOVWF   RX_LEN
        CLRF    CRC_RX
        MOVF    RX_LEN,W
        CALL    crc8_update_rx   ; CRC tambien procesa LEN
        CLRF    RX_IDX
        MOVLW   3
        MOVWF   RX_STATE
        RETURN

; Recibe el tipo y los datos de la trama.
rx_state3:
        MOVF    TMP2,W
        CALL    crc8_update_rx
        MOVF    RX_IDX,W
        BTFSC   STATUS,2
        GOTO    rx_store_type
        MOVF    RX_IDX,W
        XORLW   1
        BTFSC   STATUS,2
        GOTO    rx_store_d0
        MOVF    RX_IDX,W
        XORLW   2
        BTFSC   STATUS,2
        GOTO    rx_store_d1
        GOTO    rx_idx_next
rx_store_type:
        MOVF    TMP2,W
        MOVWF   RX_TYPE
        GOTO    rx_idx_next
rx_store_d0:
        MOVF    TMP2,W
        MOVWF   RX_D0
        GOTO    rx_idx_next
rx_store_d1:
        MOVF    TMP2,W
        MOVWF   RX_D1
rx_idx_next:
        INCF    RX_IDX,F
        MOVF    RX_IDX,W
        XORWF   RX_LEN,W
        BTFSS   STATUS,2
        RETURN
        MOVLW   4
        MOVWF   RX_STATE
        RETURN

; Valida el CRC recibido.
rx_state4:
        CLRF    RX_STATE
        MOVF    TMP2,W
        XORWF   CRC_RX,W
        BTFSS   STATUS,2
        RETURN                  ; CRC invalido: descarta
        GOTO    rx_process

rx_abort:
        CLRF    RX_STATE
        RETURN

;-------------------------------------------------------------------------------
; @brief Procesa el comando recibido y ejecuta la accion correspondiente.
; @details Valida los parametros de cada comando y genera una respuesta ACK.
; @param RX_TYPE = comando; RX_D0/RX_D1 = datos recibidos.
; @return Ninguno.
; @modifica W, ACK_CMD, ACK_RES, ALARM_TEMP, PERIOD_MS, PERIOD_CNT,
;           MODO, X_OFF_L, X_OFF_H, TX_HEAD y TX_CNT.
;-------------------------------------------------------------------------------
rx_process:
        BANKSEL RX_TYPE
        MOVF    RX_TYPE,W
        XORLW   CMD_PING
        BTFSC   STATUS,2
        GOTO    cmd_ping
        MOVF    RX_TYPE,W
        XORLW   CMD_START
        BTFSC   STATUS,2
        GOTO    cmd_start
        MOVF    RX_TYPE,W
        XORLW   CMD_STOP
        BTFSC   STATUS,2
        GOTO    cmd_stop
        MOVF    RX_TYPE,W
        XORLW   CMD_SET_THRESH
        BTFSC   STATUS,2
        GOTO    cmd_set_thresh
        MOVF    RX_TYPE,W
        XORLW   CMD_GET_STATUS
        BTFSC   STATUS,2
        GOTO    cmd_get_status
        MOVF    RX_TYPE,W
        XORLW   CMD_SET_OFFSET
        BTFSC   STATUS,2
        GOTO    cmd_set_offset
        MOVLW   RES_UNKNOWN
        GOTO    cmd_ack

; Comando PING: responde con una confirmacion.
cmd_ping:
        MOVF    RX_LEN,W
        XORLW   1
        BTFSS   STATUS,2
        GOTO    cmd_bad_param
        MOVLW   RES_OK
        GOTO    cmd_ack

; Comando START: habilita la transmision de datos.
cmd_start:
        MOVF    RX_LEN,W
        XORLW   2
        BTFSS   STATUS,2
        GOTO    cmd_bad_param
        MOVF    RX_D0,W
        BTFSC   STATUS,2
        GOTO    cmd_start_enable  ; 0 = mantiene el período actual
        MOVF    RX_D0,W
        SUBLW   PROTO_PERIOD_MIN-1
        BTFSC   STATUS,0          ; C=1 -> menor que el mínimo
        GOTO    cmd_bad_param
        MOVF    RX_D0,W
        SUBLW   PROTO_PERIOD_MAX
        BTFSS   STATUS,0          ; C=0 -> mayor que el máximo
        GOTO    cmd_bad_param
        MOVF    RX_D0,W
        MOVWF   PERIOD_MS
        MOVWF   PERIOD_CNT
cmd_start_enable:
        BSF     MODO,0
        MOVLW   RES_OK
        GOTO    cmd_ack

; Comando STOP: deshabilita la transmision de datos.
cmd_stop:
        MOVF    RX_LEN,W
        XORLW   1
        BTFSS   STATUS,2
        GOTO    cmd_bad_param
        BCF     MODO,0
        MOVLW   RES_OK
        GOTO    cmd_ack

; Comando SET_THRESHOLD: configura el umbral de temperatura.
cmd_set_thresh:
        MOVF    RX_LEN,W
        XORLW   2
        BTFSS   STATUS,2
        GOTO    cmd_bad_param
        MOVF    RX_D0,W
        SUBLW   TEMP_MAX
        BTFSS   STATUS,0          ; C=0 -> mayor que 99
        GOTO    cmd_bad_param
        MOVF    RX_D0,W
        MOVWF   ALARM_TEMP
        MOVLW   RES_OK
        GOTO    cmd_ack

; Comando GET_STATUS: solicita el estado actual del sistema.
cmd_get_status:
        MOVF    RX_LEN,W
        XORLW   1
        BTFSS   STATUS,2
        GOTO    cmd_bad_param
        CALL    send_status
        RETURN

; Comando SET_OFFSET: configura el offset del eje X.
cmd_set_offset:
        MOVF    RX_LEN,W
        XORLW   3
        BTFSS   STATUS,2
        GOTO    cmd_bad_param
        MOVF    RX_D1,W
        SUBLW   3                 ; C=1 si D1 <= 3 (offset <= 1023)
        BTFSS   STATUS,0
        GOTO    cmd_bad_param
        MOVF    RX_D0,W
        MOVWF   X_OFF_L
        MOVF    RX_D1,W
        MOVWF   X_OFF_H
        MOVLW   RES_OK
        GOTO    cmd_ack

cmd_bad_param:
        MOVLW   RES_BAD_PARAM
cmd_ack:
        MOVWF   ACK_RES
        MOVF    RX_TYPE,W
        MOVWF   ACK_CMD
        CALL    send_ack
        RETURN
