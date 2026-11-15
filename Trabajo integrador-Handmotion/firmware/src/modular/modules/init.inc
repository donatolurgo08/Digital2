;*******************************************************************************
; MODULO INIT - Configuracion inicial del MCU
;
; Rutina trasladada desde firmware/src/handmotion.S (referencia original, no
; modificada): init, incluida su etiqueta interna wait_osc.
;
; CORRECCION DE SELECCION DE BANCO (verificada en el datasheet DS40001291H,
; pagina 26): ADCON1 esta en el banco 1 (0x9F) y ANSEL en el banco 3 (0x188).
; La instruccion BANKSEL ANSEL deja seleccionado el banco 3, por lo que la
; escritura a ADCON1 no alcanzaba su registro. Se agrega BANKSEL ADCON1
; inmediatamente antes de MOVWF ADCON1. Es la unica diferencia funcional
; respecto del original.
;
; Configura: reloj interno, niveles iniciales de salida, direcciones de los
; puertos, entradas analogicas y el ADC. No configura INTCON, OPTION_REG ni
; TIMER1, UART ni interrupciones. Inicializa FLAGS, el estado temporal del
; patron sonoro y los resultados X/Y/Z.
;
; Dependencias:
;   - Constantes definidas en handmotion_work.S (no se redefinen aqui):
;       OSCCON_8MHZ      (0x70): IRCF=111, SCS=00.
;       TRISA_INIT       (0xDB), TRISB_INIT (0xFF), TRISC_INIT (0xB0),
;       TRISD_INIT       (0x00), TRISE_INIT (0x0F).
;       ANSEL_INIT       (0x63): AN0, AN1, AN5 y AN6 analogicas.
;       ADC_ADCON1_INIT  (0x80): ADFM=1 (justificado a la derecha), VDD/VSS.
;       ADC_CTRL_BASE    (0x81): ADON=1, ADCS=FOSC/32, CHS=AN0.
;   - Variables definidas en handmotion_work.S (no se redefinen aqui):
;       FLAGS, BUZZ_DIV, BUZZ_CNT, BUZZ_PHASE, X/Y/Z_MG_L:H, Y_SIGN, Z_SIGN:
;       se inicializan a 0.
;   - Registros SFR: OSCCON, PORTA, PORTC, PORTD, TRISA a TRISE, ANSEL,
;     ANSELH, ADCON1 y ADCON0. El acceso se hace con BANKSEL.
;   - Rutinas externas: ninguna.
;   - Los modulos adc.inc, alarmas.inc, acelerometro.inc, display.inc y
;     uart.inc dependen de la configuracion que deja init.
;   - Este archivo debe incluirse dentro de un PSECT de codigo, igual que en
;     handmotion.S. No debe incluirse junto con handmotion.S sin eliminar antes
;     la copia de init y wait_osc: las etiquetas se repetirian.
;*******************************************************************************

;*******************************************************************************
; @brief    Inicializa reloj, niveles de salida, direcciones de los puertos y
;           el ADC del PIC16F887.
;
; @details  Orden de configuracion:
;             1. Reloj interno a 8 MHz y espera de estabilizacion (HTS).
;             2. Niveles inactivos en los latches de salida.
;             3. Direcciones de los puertos (TRISx).
;             4. Entradas analogicas (ANSEL/ANSELH).
;             5. ADC a FOSC/32, referencia VDD/VSS y justificacion derecha.
;
;           1. OSCCON: se escribe OSCCON_8MHZ (IRCF=111, SCS=00). wait_osc
;              repite BTFSS OSCCON,2 hasta que HTS=1. No tiene limite de
;              tiempo: si el oscilador no estabiliza, la rutina queda bloqueada.
;           2. Latches: PORTA y PORTC se ponen a 0; RC3 (BZ_CTRL, activo-bajo)
;              queda en 1, buzzer apagado; PORTD se pone a 0 (segmentos
;              apagados). FLAGS, el estado del buzzer y los resultados X/Y/Z se
;              inicializan a 0.
;           3. TRISA-TRISE: direcciones de cada puerto segun TRISx_INIT.
;           4. ANSEL habilita AN0, AN1, AN5 y AN6; ANSELH deja AN8-AN13
;              digitales.
;           5. ADCON1 = ADC_ADCON1_INIT (ADFM=1, VCFG=00). Antes de escribirlo
;              se selecciona el banco 1 con BANKSEL ADCON1 (correccion de banco
;              verificada en el datasheet). ADCON0 = ADC_CTRL_BASE con el
;              banco 0 seleccionado mediante BANKSEL ADCON0.
;
;           Niveles inactivos elegidos:
;             - LED1 (RA2) y LED2 (RA5) apagados: nivel bajo.
;             - DIG1-DIG3 (RC0-RC2) en bajo: ningun display habilitado.
;             - BZ_CTRL (RC3) en alto: buzzer activo-bajo apagado.
;             - Segmentos (RD0-RD7) en bajo: apagados (catodo comun).
;
;           Seleccion de bancos: BANKSEL cambia RP1:RP0 de STATUS; no existe
;           un registro BSR independiente en el PIC16F887.
;
; @param    ninguno
; @return   ninguno
; @modifica W, STATUS (RP1:RP0, Z), OSCCON, PORTA, PORTC, PORTD,
;           TRISA, TRISB, TRISC, TRISD, TRISE, ANSEL, ANSELH, ADCON1,
;           ADCON0, FLAGS, BUZZ_DIV, BUZZ_CNT, BUZZ_PHASE, X/Y/Z_MG_L:H,
;           Y_SIGN, Z_SIGN
;*******************************************************************************
init:
        ;----- Reloj interno a 8 MHz -----
        BANKSEL OSCCON
        MOVLW   OSCCON_8MHZ
        MOVWF   OSCCON

wait_osc:
        BTFSS   OSCCON, 2       ; bit 2 = HTS: 1 cuando el HFINTOSC esta listo
        GOTO    wait_osc

        ;----- Salidas inactivas antes de habilitar los drivers -----
        BANKSEL PORTA
        CLRF    PORTA           ; LED1/LED2 apagados
        CLRF    PORTC           ; digitos apagados; fijar BZ_CTRL en inactivo
        BSF     PORTC,3         ; BZ_CTRL activo-bajo: alto = apagado
        CLRF    PORTD           ; segmentos activos altos: todos apagados
        CLRF    FLAGS           ; signo X y estado del display iniciales
        BANKSEL BUZZ_DIV
        CLRF    BUZZ_DIV        ; estado inicial seguro del patron sonoro
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
        MOVWF   ANSEL           ; AN0, AN1, AN5 y AN6 analogicas
        CLRF    ANSELH          ; AN8-AN13 digitales

        ;----- ADC -----
        MOVLW   ADC_ADCON1_INIT
        BANKSEL ADCON1          ; ADCON1 esta en el banco 1 (0x9F)
        MOVWF   ADCON1          ; ADFM=1, VCFG1:VCFG0=00 (VDD/VSS)
        BANKSEL ADCON0          ; ADCON0 esta en el banco 0 (0x1F)
        MOVLW   ADC_CTRL_BASE   ; ADON=1, ADCS=FOSC/32, CHS=AN0
        MOVWF   ADCON0

        RETURN
