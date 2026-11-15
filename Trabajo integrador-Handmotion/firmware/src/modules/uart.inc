;*******************************************************************************
; MODULO EUSART Y PROTOCOLO - Etapa 6
;
; Enlace: 9600 Bd, 8N1, sin control de flujo.
;   FOSC = 8 MHz, BRGH = 1 -> SPBRG = 51 -> 9615 Bd (error +0,16 %).
;
; Trama en ambos sentidos:
;   AA 55 | LEN | TIPO | DATOS (LEN-1) | CRC8
;   LEN cuenta desde TIPO. CRC8 polinomio 0x07, inicial 0x00, sobre
;   LEN, TIPO y DATOS.
;
; PIC -> PC:
;   0x01 DATA    SEQ, TEMP, X_L, X_H, Y_L, Y_H, Z_L, Z_H, FLAGS (14 bytes, v3)
;   0x02 STATUS  VERSION, PERIOD, THRESH, OFF_L, OFF_H, MODO  (11 bytes)
;   0x03 ACK     CMD, RESULT                     (7 bytes)
;
; PC -> PIC:
;   0x81 PING          sin datos
;   0x82 START         PERIOD_MS (0 = mantener)
;   0x83 STOP          sin datos
;   0x84 SET_THRESHOLD grados C (0..99)
;   0x85 GET_STATUS    sin datos
;   0x86 SET_OFFSET    X_OFF_L, X_OFF_H (0..1023)
;
; No usa interrupciones: uart_service drena un byte de TX y sondea RCIF en
; cada pasada del bucle principal, para no bloquear el multiplexado.
;
; DATA v3 contiene X, Y y Z en mg con signo, complemento a dos, little-endian.
; LEN=10 cuenta TYPE + los 9 bytes SEQ/TEMP/X/Y/Z/FLAGS. CRC cubre LEN..FLAGS.
;*******************************************************************************

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
; @brief Inicia el EUSART y el estado del protocolo.
; @param ninguno
; @return ninguno
; @modifica TXSTA, BAUDCTL, SPBRG, RCSTA, PIE1 y las variables del modulo
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
; @brief Atiende TX, RX y el período de muestreo. Se llama en cada pasada.
; @param ninguno
; @return ninguno
; @modifica W, FSR y variables del modulo
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
; @brief Encola un byte en el buffer circular de transmision.
; @param W = byte
; @return ninguno (si el buffer esta lleno, descarta el byte)
; @modifica W, FSR, TMP2, TX_HEAD, TX_CNT
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
; @brief Actualiza el CRC8 con un byte.
; @param W = byte; CRC_REG = CRC parcial
; @return CRC_REG actualizado
; @modifica W, CRC_REG, CRC_CNT
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
; @brief Actualiza el CRC8 de recepcion con un byte.
; @param W = byte; CRC_RX = CRC parcial de recepcion
; @return CRC_RX actualizado
; @modifica W, CRC_RX, CRC_CNT_RX
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
; @brief Encola un byte y lo incluye en el CRC.
; @param W = byte
; @return ninguno
; @modifica W, TMP2, FSR, CRC_REG, CRC_CNT, TX_HEAD, TX_CNT
;-------------------------------------------------------------------------------
tx_frame_byte:
        MOVWF   TMP2
        CALL    crc8_update
        MOVF    TMP2,W
        CALL    tx_push
        RETURN

;-------------------------------------------------------------------------------
; @brief Arma y encola una trama DATA v3 con temperatura, X, Y, Z y alarma.
; @param ninguno
; @return ninguno
; @modifica W, FSR, TMP2, CRC_REG, CRC_CNT, SEQ, TX_HEAD, TX_CNT
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
; @brief Arma y encola la trama STATUS.
; @param ninguno
; @return ninguno
; @modifica W, FSR, TMP2, CRC_REG, CRC_CNT, TX_HEAD, TX_CNT
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
; @brief Arma y encola una trama ACK.
; @param ACK_CMD = comando, ACK_RES = resultado
; @return ninguno
; @modifica W, FSR, TMP2, CRC_REG, CRC_CNT, TX_HEAD, TX_CNT
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
; @brief Procesa un byte recibido segun la maquina de estados.
; @param W = byte
; @return ninguno
; @modifica W, TMP2, RX_STATE, RX_LEN, RX_IDX, RX_TYPE, RX_D0, RX_D1, CRC_RX, CRC_CNT_RX
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

; @brief Estado 0: espera del primer byte de sincronismo (0xAA).
rx_state0:
        MOVF    TMP2,W
        XORLW   PROTO_SYNC1
        BTFSS   STATUS,2
        RETURN
        MOVLW   1
        MOVWF   RX_STATE
        RETURN

; @brief Estado 1: espera del segundo byte de sincronismo (0x55).
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

; @brief Estado 2: recepcion de LEN y validacion de longitud.
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

; @brief Estado 3: recepcion de TIPO y DATOS, actualizacion de CRC.
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

; @brief Estado 4: recepcion y validacion del CRC final.
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
; @brief Despacha el comando recibido.
; @details Valida RX_LEN segun el comando y ejecuta la accion correspondiente.
;          Responde con ACK. Los comandos no soportados devuelven RES_UNKNOWN.
; @param RX_TYPE = comando, RX_D0/RX_D1 = datos, RX_LEN = longitud
; @return ninguno
; @modifica W, ACK_CMD, ACK_RES, ALARM_TEMP, PERIOD_MS, PERIOD_CNT, MODO,
;           X_OFF_L, X_OFF_H, TX_HEAD, TX_CNT
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

; @brief Comando PING: responde con ACK y resultado OK.
cmd_ping:
        MOVF    RX_LEN,W
        XORLW   1
        BTFSS   STATUS,2
        GOTO    cmd_bad_param
        MOVLW   RES_OK
        GOTO    cmd_ack

; @brief Comando START: habilita streaming y opcionalmente cambia el periodo.
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

; @brief Comando STOP: deshabilita streaming.
cmd_stop:
        MOVF    RX_LEN,W
        XORLW   1
        BTFSS   STATUS,2
        GOTO    cmd_bad_param
        BCF     MODO,0
        MOVLW   RES_OK
        GOTO    cmd_ack

; @brief Comando SET_THRESHOLD: configura umbral de alarma (0..99 C).
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

; @brief Comando GET_STATUS: envia trama STATUS con la configuracion actual.
cmd_get_status:
        MOVF    RX_LEN,W
        XORLW   1
        BTFSS   STATUS,2
        GOTO    cmd_bad_param
        CALL    send_status
        RETURN

; @brief Comando SET_OFFSET: configura el offset de X (0..1023).
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
