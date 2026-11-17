;===============================================================================
; Trabajo Integrador: HAND MOTION
; Modulo: Conversion Analogica-Digital (ADC)
;
; Autores:
;   - Conde Ana Victoria
;   - Lurgo Donato
;
; Fecha: 17/11/2026
; Microcontrolador: PIC16F887
;
; Descripcion:
;   Configuracion de la lectura de canales analogicos mediante el ADC
;   del PIC16F887. Las conversiones se realizan mediante polling.
;
;===============================================================================

;===============================================================================
; @brief Espera el tiempo de adquisicion del ADC.
;
; @details Ejecuta un bucle de 14 iteraciones para permitir que
;          el capacitor de sample-and-hold alcance el nivel de entrada.
;
; @param W = cantidad de iteraciones.
; @return Ninguno.
; @modifica COUNT.
;===============================================================================
delay_acq:
        MOVWF   COUNT
delay_acq_loop:
        DECFSZ  COUNT,F
        GOTO    delay_acq_loop
        RETURN

;===============================================================================
; @brief Lee un canal analogico del ADC.
;
; @details Selecciona el canal, espera el tiempo de adquisicion,
;          inicia la conversion y espera su finalizacion.
;          El resultado de 10 bits queda almacenado en ADC_H:ADC_L.
;
;          Canales utilizados:
;          AN0 = Temperatura (LM35).
;          AN1 = Aceleracion X.
;          AN5 = Aceleracion Y.
;          AN6 = Aceleracion Z.
;
; @param W = numero de canal analogico.
; @return ADC_H:ADC_L = resultado de la conversion.
; @modifica W, ADCON0, ADC_L, ADC_H, TMP, COUNT y STATUS.
;===============================================================================
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
