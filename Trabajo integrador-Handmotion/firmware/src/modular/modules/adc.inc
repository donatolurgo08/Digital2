;*******************************************************************************
; MODULO ADC - Lectura de canales analogicos por polling
;
; Rutinas trasladadas sin cambios de logica desde firmware/src/handmotion.S
; delay_acq y leer_adc conservan la logica de la referencia original.
;
; No incluye: la configuracion inicial del ADC (ADCON1, ADCON0 y ANSEL, que
; permanecen en init), ni las conversiones de temperatura (convertir_temp) y
; de aceleracion (convertir_x_mg / convertir_y_mg).
;
; Dependencias:
;   - Constantes definidas en handmotion.S (no se redefinen aqui):
;       ADC_CTRL_BASE  (0x81: ADON + ADCS = FOSC/32)
;       ADC_ACQ_LOOPS  (14 iteraciones de adquisicion)
;       ADC_GO         (1: bit GO/DONE de ADCON0)
;   - Variables de RAM comun definidas en handmotion.S (no se redefinen aqui):
;       ADC_L, ADC_H, TMP, COUNT (0x70-0x7F, accesibles desde cualquier banco).
;   - Registros SFR: ADCON0, ADRESL, ADRESH (se accede con BANKSEL).
;   - Este archivo debe incluirse dentro de un PSECT de codigo, igual que en
;     handmotion.S. No debe incluirse junto con handmotion.S sin eliminar antes
;     las copias de delay_acq y leer_adc: las etiquetas se repetirian.
;*******************************************************************************

;*******************************************************************************
; @brief    Espera el tiempo de adquisicion del sample-and-hold.
;
; @details  Bucle de 14 iteraciones. Cada iteracion consume 3 TCY (DECFSZ +
;           GOTO) = 1,5 us; con CALL, MOVWF y RETURN el total supera los
;           20 us. Es un margen conservador sobre TACQ para fuentes de hasta
;           10 k. La salida del modulo MMA7361 se conecta directo: verificar
;           su impedancia de salida antes de reducir este margen.
;
; @param    W = cantidad de iteraciones (ADC_ACQ_LOOPS)
; @return   ninguno
; @modifica COUNT
;*******************************************************************************
delay_acq:
        MOVWF   COUNT
delay_acq_loop:
        DECFSZ  COUNT,F
        GOTO    delay_acq_loop
        RETURN

;*******************************************************************************
; @brief    Lee un canal del ADC por polling.
;
; @details  Construye ADCON0 con el canal pedido, espera la adquisicion,
;           inicia la conversion y espera a que GO/DONE vuelva a cero. El
;           resultado queda justificado a la derecha en ADC_H:ADC_L.
;           Canales: 0 = AN0 (LM35), 1 = AN1 (X), 5 = AN5 (Y), 6 = AN6 (Z).
;
; @param    W = numero de canal (0..13)
; @return   ADC_H:ADC_L = resultado de 10 bits
; @modifica W, ADCON0, ADC_L, ADC_H, TMP, COUNT, STATUS (RP1:RP0, C, Z)
;*******************************************************************************
leer_adc:
        MOVWF   TMP             ; guarda el canal
        BCF     STATUS,0
        RLF     TMP,F           ; TMP = canal << 1
        RLF     TMP,F           ; TMP = canal << 2
        MOVF    TMP,W
        IORLW   ADC_CTRL_BASE   ; ADON + ADCS = FOSC/32
        BANKSEL ADCON0
        MOVWF   ADCON0          ; selecciona canal y enciende ADC

        MOVLW   ADC_ACQ_LOOPS
        CALL    delay_acq       ; espera de adquisicion

        BSF     ADCON0,ADC_GO   ; inicia conversion
wait_adc:
        BTFSC   ADCON0,ADC_GO   ; GO = 1 mientras convierte
        GOTO    wait_adc

        BANKSEL ADRESL
        MOVF    ADRESL,W
        MOVWF   ADC_L
        BANKSEL ADRESH
        MOVF    ADRESH,W
        ANDLW   0x03            ; solo bits 9:8
        MOVWF   ADC_H
        RETURN
