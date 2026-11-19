;===============================================================================
; Trabajo Integrador: HAND MOTION
; Modulo: Inicializacion del microcontrolador
;
; Autores:
;   - Conde Ana Victoria
;   - Lurgo Donato
;
; Fecha: 17/11/2026
; Microcontrolador: PIC16F887
;
; Descripcion:
;   Configuracion inicial del reloj, puertos, entradas analogicas y
;   convertidor analogico-digital (ADC) del microcontrolador.
;
;===============================================================================

;===============================================================================
; @brief Inicializa los perifericos y registros principales del PIC16F887.
;
; @details Configura:
;          - Oscilador interno a 8 MHz.
;          - Estados iniciales de las salidas.
;          - Direcciones de los puertos mediante registros TRIS.
;          - Canales analogicos AN0, AN1, AN5 y AN6.
;          - ADC con referencia VDD/VSS y justificacion a la derecha.
;
;          Tambien inicializa las variables de estado, alarma y aceleracion.
;
; @param Ninguno.
; @return Ninguno.
; @modifica Registros de configuracion, puertos, ADC y variables de estado.
;===============================================================================
init:
        ;----- Reloj interno a 8 MHz -----
        BANKSEL OSCCON
        MOVLW   OSCCON_8MHZ
        MOVWF   OSCCON

wait_osc:
        BTFSS   OSCCON, 2       ; Espera la estabilizacion del oscilador.
        GOTO    wait_osc

        ;----- Salidas inactivas antes de habilitar los drivers -----
        BANKSEL PORTA
        CLRF    PORTA           ; Apaga los indicadores LED.
        CLRF    PORTC           ; Deshabilita los displays.
        BSF     PORTC,3         ; Mantiene el buzzer apagado.
        CLRF    PORTD           ; Apaga todos los segmentos.
        CLRF    FLAGS           ; Inicializa las banderas de estado.
        BANKSEL BUZZ_DIV
        CLRF    BUZZ_DIV        ; Reinicia el estado del buzzer.
        CLRF    BUZZ_CNT
        CLRF    BUZZ_PHASE
        CLRF    X_MG_L
        CLRF    X_MG_H
        CLRF    Y_MG_L
        CLRF    Y_MG_H
        CLRF    Y_SIGN
        CLRF    Z_L
        CLRF    Z_H
        CLRF    Z_MG_L
        CLRF    Z_MG_H
        CLRF    Z_SIGN

        ;----- Direcciones de los puertos -----
        BANKSEL TRISA
        MOVLW   TRISA_INIT
        MOVWF   TRISA
        MOVLW   TRISB_INIT
        MOVWF   TRISB
        MOVLW   TRISC_INIT
        MOVWF   TRISC
        MOVLW   TRISD_INIT
        MOVWF   TRISD
        MOVLW   TRISE_INIT
        MOVWF   TRISE

        ;----- Entradas analogicas -----
        BANKSEL ANSEL
        MOVLW   ANSEL_INIT
        MOVWF   ANSEL           ; Habilita los canales analogicos utilizados.
        CLRF    ANSELH          ; Configura los canales restantes como digitales.

        ;----- ADC -----
        MOVLW   ADC_ADCON1_INIT
        BANKSEL ADCON1          ; Configura el ADC con referencia VDD/VSS.
        MOVWF   ADCON1          ; ADFM=1, VCFG1:VCFG0=00 (VDD/VSS)
        BANKSEL ADCON0          ; ADCON0 esta en el banco 0 (0x1F)
        MOVLW   ADC_CTRL_BASE   ; ADON=1, ADCS=FOSC/32, CHS=AN0
        MOVWF   ADCON0

        RETURN
