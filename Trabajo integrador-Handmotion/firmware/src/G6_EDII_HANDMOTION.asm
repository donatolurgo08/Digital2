;*******************************************************************************
; @brief       ANEXO B - FIRMWARE DEL SISTEMA HAND MOTION.
;
; @brief       Descripción general del funcionamiento del firmware desarrollado
;              para el sistema HAND MOTION basado en el microcontrolador PIC16F887.
;
; @details     El firmware realiza la adquisición de señales analógicas
;              provenientes de un sensor de temperatura LM35 y de un acelerómetro
;              triaxial MMA7361, utilizando el módulo convertidor analógico-digital
;              (ADC) del microcontrolador.
;
;              Implementa el procesamiento de las muestras correspondientes a
;              los ejes X, Y y Z, la conversión de los valores obtenidos y la
;              gestión de una alarma térmica mediante indicadores LED y buzzer.
;
;              También incorpora la actualización de un display de siete
;              segmentos mediante multiplexado y la comunicación serial EUSART
;              con una interfaz gráfica en computadora. Esta comunicación permite
;              transmitir mediciones y estados del sistema, así como recibir
;              comandos de configuración y control.
;
;              La temporización se gestiona mediante TIMER0 y TIMER1, empleando
;              interrupciones y sondeo de periféricos según la función requerida.
;
; @author      Lurgo, Donato
;              Conde, Ana Victoria
;
; @date        20/11/2026
;
; @version     2.0
;*******************************************************************************
;===============================================================================
; DIRECTIVAS DE INCLUSION
;===============================================================================
        LIST    P=16F887
        #include "p16f887.inc"

;===============================================================================
; CONFIGURACION GENERAL DEL MCU
;===============================================================================
        __CONFIG _CONFIG1, _FOSC_INTRC_NOCLKOUT & _WDTE_OFF & _PWRTE_ON & _MCLRE_ON & _CP_OFF & _CPD_OFF & _BOREN_ON & _IESO_OFF & _FCMEN_OFF & _LVP_OFF & _DEBUG_OFF
        __CONFIG _CONFIG2, _BOR4V_BOR40V & _WRT_OFF

;===============================================================================
; DEFINICION DE CONSTANTES
;===============================================================================

#DEFINE LED1            PORTA, RA2     ; LED de alarma 1, activo alto
#DEFINE LED2            PORTA, RA5     ; LED de alarma 2, activo alto
#DEFINE BZ_CTRL         PORTC, RC3     ; Buzzer MDU1095, activo bajo
#DEFINE DIG1            PORTC, RC0     ; Digito de decenas, activo alto
#DEFINE DIG2            PORTC, RC1     ; Digito de unidades, activo alto
#DEFINE DIG3            PORTC, RC2     ; Digito de la letra C, activo alto
#DEFINE SEG_PORT        PORTD          ; Segmentos a-g y dp, activos altos

;----- Reloj y base de tiempo -----
        OSCCON_8MHZ     EQU     0x70    ;oscilador interno a 8Mhz
        TMR0_RELOAD     EQU     6       ;TMR0 se interrumpe cada 1ms
        X_SAMPLE_TICKS  EQU     D'20'   ;20 interrupciones de 1ms para muestrear 20ms
        TMR1_RELOAD_H   EQU     0xF8    ;parte alta del valor de recarga de TMR1
        TMR1_RELOAD_L   EQU     0x30    ; parte baja del valor de recarga

;----- ADC -----
        ADC_ADCON1_INIT EQU     0x80    ;valor para ADCON1
        ADC_CTRL_BASE   EQU     0x81    ;valor base de ADCON0
        ADC_ACQ_LOOPS   EQU     D'14'   ;cantidad de vueltas que espera antes de convertir   
        ADC_GO          EQU     1       ;numero de bit para arrancar la conversion

;----- Direcciones de los puertos -----
        TRISA_INIT      EQU     0xDB    ; RA2 y RA5 salidas
        TRISB_INIT      EQU     0xFF    ; todo entrada 
        TRISC_INIT      EQU     0xB0    ; RC0-RC3 y RC6 salidas
        TRISD_INIT      EQU     0x00    ; RD0-RD7 salidas (segmentos)
        TRISE_INIT      EQU     0x0F    ; RE0-RE3 --> pin de reset (no se usa)

;----- Entradas analogicas: AN0 (LM35), AN1 (X), AN5 (Y), AN6 (Z) -----
        ANSEL_INIT      EQU     0x63   ;valor inicial de init

;----- Conversion de las cuentas ADC -----
        TEMP_MAX        EQU     D'99'   ;temperatura maxima que se puede mostrar
        X_OFFSET_L      EQU     0x52    
        X_OFFSET_H      EQU     0x01
        Y_OFFSET_L      EQU     0x52    
        Y_OFFSET_H      EQU     0x01
        Z_OFFSET_L      EQU     0x52    
        Z_OFFSET_H      EQU     0x01
        X_MG_NUM        EQU     D'49'   
        Z_MG_NUM        EQU     D'49'      

;----- Alarma termica -----
        TEMP_ALARM      EQU     D'40'      ;fijar el humbral de la alarma termica

;----- Patron del buzzer activo (200 ms ON + 800 ms OFF) -----
        BUZZ_DIVISOR    EQU     D'10'      ;ticks de 1 ms por unidad de 10 ms
        BUZZ_ON_UNITS   EQU     D'20'      ;20 * 10 ms = 200 ms
        BUZZ_OFF_UNITS  EQU     D'80'      ;80 * 10 ms = 800 ms

;----- Tipos de trama -----
        T_DATA          EQU     0x01       ;trama de datos 
        T_STATUS        EQU     0x02       ;trama de estado
        T_ACK           EQU     0x03       ;trama de respuesta

;----- Comandos PC -> PIC -----
        CMD_PING        EQU     0x81       ;la pc pregunta si el pic esta respondiendo
        CMD_START       EQU     0x82       ;activa el envio de datos
        CMD_STOP        EQU     0x83       ;desactiva el envio de datos
        CMD_SET_THRESH  EQU     0x84       ;cambia el umbral de temperatura para la alarma (para la gui)
        CMD_GET_STATUS  EQU     0x85       ;pide al pic que informe su configuracion actual 
        CMD_SET_OFFSET  EQU     0x86

;----- Resultados de ACK -----              --> bloque de confirmacion
        RES_OK          EQU     0          ;indica que el comando se ejecuto bien
        RES_BAD_PARAM   EQU     1          ;indica que el comando llego pero que el comando no es valido
        RES_UNKNOWN     EQU     2          ;el pic no reconoce el comando recibido

;----- EUSART y protocolo -----
        EUSART_SPBRG    EQU     D'51'      ;defino el valor para transmitir a 9600baud
        EUSART_TXSTA    EQU     0x24       ;actuva el transmisor y selecciona la comunicacion de alta velocidad 
        EUSART_RCSTA    EQU     0x90       ;habilita el puerto serie y la recepcion continua
        PROTO_SYNC1     EQU     0xAA       ;primer byte que marca el inicio de una trama
        PROTO_SYNC2     EQU     0x55       ;segundo byte de inicio de la trama
        PROTO_VERSION   EQU     3
        PROTO_CRC_POLY  EQU     0x07
        PROTO_PERIOD    EQU     D'50'      ;envia datos cada 50ms por defecto  
        PROTO_PERIOD_MIN EQU    D'20'      
        PROTO_PERIOD_MAX EQU    D'250'     

;===============================================================================
; DEFINICION DE VARIABLES
;===============================================================================
        CBLOCK  0x70            
        ADC_L                   ;guarda los 8 bits bajos de la conversion
        ADC_H                   ;guarda los bits 8 y 9 de la conversion
        TMP                     ;guarda temporalmente un valor durante los calculos 
        COUNT                   ;cuenta repeticiones
        MUL_A                   ;guarda valores que se van a multiplicar
        MUL_B                   ;''
        RES_L                   ;guardan las partes del producto 
        RES_M                   ;''
        RES_H                   ;''
        MC_L                    ;guarda el multiplicando 
        MC_H                    ;''
        DELTA_L                 ;guardan un resultado de 16 bits (alto y bajo)
        DELTA_H                 ;
        FLAGS                   ;
        W_TEMP                  ;guarda temporalmente el registro w al entrar en interrupcion 
        STATUS_TEMP             ;guarda temporalmente el registro status al entrar en interrupcion
        ENDC

; Banco 0: reservamos 16 variables en el banco 0, desde 0x20 hasta 0x2F para guardar muestras y resultados (primera parte)

        CBLOCK  0x20   
        Y_L                     ; eje Y, byte bajo del ADC
        Y_H                     ; eje Y, bits 9:8
        X_MG_L                  ; resultado X con signo, byte bajo
        X_MG_H                  ; resultado X con signo, byte alto
        Y_MG_L                  ; resultado Y con signo, byte bajo
        Y_MG_H                  ; resultado Y con signo, byte alto
        Y_SIGN                  ; bit0 = signo temporal de Y
        Z_L                     ; eje Z, byte bajo del ADC
        Z_H                     ; eje Z, bits 9:8
        Z_MG_L                  ; resultado Z con signo, byte bajo
        Z_MG_H                  ; resultado Z con signo, byte alto
        Z_SIGN                  ; bit0 = signo temporal de Z
        TEMP_C                  ;  
        PROD_H                  ; 
        T0_DIV                  ; 
        X_SAMPLE_FLAG           ; indica que hay una nueva lectura de x/y/z
        ENDC

; Buffer 
        TX_BUF  EQU     0x30    ;

; Banco 0, segunda parte: 
        CBLOCK  0x50
        TX_HEAD                 ; indice de escritura
        TX_TAIL                 ; indice de lectura
        TX_CNT                  ; bytes pendientes
        RX_TYPE                 ; tipo de la trama recibida
        RX_D0                   ; primer byte de datos
        RX_D1                   ; segundo byte de datos
        RX_STATE                ; 0..4, sincronismo y recepcion
        RX_LEN                  ; LEN de la trama en curso
        RX_IDX                  ; indice dentro de la trama
        CRC_REG                 ; CRC8 parcial de transmision
        CRC_CNT                 ; contador de bits del CRC de transmision
        CRC_RX                  ; CRC8 parcial de recepcion
        CRC_CNT_RX              ; contador de bits del CRC de recepcion
        TMP2                    ; auxiliar del modulo UART
        PERIOD_MS               ; periodo de DATA en ms
        PERIOD_CNT              ; cuenta regresiva en ms
        ALARM_TEMP              ; umbral de alarma en grados C
        X_OFF_L                 ; offset de X, byte bajo
        X_OFF_H                 ; offset de X, bits 9:8
        MODO                    ; bit0 = streaming habilitado
        SEQ                     ; numero de trama DATA
        TICK_FLAG               ; bandera de 1 ms puesta por el display
        ALARM_STATE             ; bit0 = alarma termica activa
        ACK_CMD                 ; comando respondido
        ACK_RES                 ; resultado de la respuesta
        BUZZ_DIV                ; ticks de 1 ms acumulados
        BUZZ_CNT                ; unidades de 10 ms restantes
        BUZZ_PHASE              ; 0 = fase apagada, 1 = fase encendida
        ENDC

;===============================================================================
; DECLARACION DE MACROS PARA CONFIGURACION DE REGISTROS
;===============================================================================
; Reloj interno a 8 MHz. La espera de HTS se hace en ESPERA_OSC.
CFG_RELOJ MACRO
        BANKSEL OSCCON
        MOVLW   OSCCON_8MHZ
        MOVWF   OSCCON
ENDM

; Direcciones de los cinco puertos (todos los TRISx estan en el banco 1).
CFG_DIRECCIONES MACRO
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
ENDM

; Entradas analogicas y ADC justificado a la derecha, VDD/VSS.
CFG_ANALOGICAS MACRO
        BANKSEL ANSEL
        MOVLW   ANSEL_INIT
        MOVWF   ANSEL
        CLRF    ANSELH
        MOVLW   ADC_ADCON1_INIT
        BANKSEL ADCON1
        MOVWF   ADCON1
        BANKSEL ADCON0
        MOVLW   ADC_CTRL_BASE
        MOVWF   ADCON0
ENDM

; Buzzer activo-bajo: 1 = apagado, 0 = encendido.
BUZZER_OFF MACRO
        BSF     BZ_CTRL
ENDM

BUZZER_ON MACRO
        BCF     BZ_CTRL
ENDM

;===============================================================================
; VECTORES DE RESET E INTERRUPCION (CODIGO ABSOLUTO)
;===============================================================================
        ORG     0x00            ; Vector de reset
        GOTO    INICIO          ; Salto al programa principal

        ORG     0x04            ; Vector de interrupcion
        GOTO    ISR_INICIO      ; Salto a la rutina de servicio

        ORG     0x05            ; Programa principal

;===============================================================================
; INICIO
;===============================================================================
INICIO:
        CFG_RELOJ               ; Oscilador interno a 8 MHz
        CALL    ESPERA_OSC      ; Espera HTS = 1
        CALL    INIT_SALIDAS    ; Niveles inactivos y variables en cero
        CFG_DIRECCIONES         ; TRISA-TRISE
        CFG_ANALOGICAS          ; ANSEL, ANSELH, ADCON1 y ADCON0
        CALL    DISPLAY_INIT    ; TIMER1 para el multiplexado
        CALL    UART_INIT       ; EUSART y estado del protocolo
        CALL    TIMER0_INIT     ; Base de 1 ms y muestreo cada 20 ms

;===============================================================================
; BUCLE PRINCIPAL
;===============================================================================
; AN0 (LM35) se lee en cada vuelta. X/AN1, Y/AN5 y Z/AN6 se leen y convierten
; juntos cada 20 ms por evento de TIMER0. TIMER1 y EUSART se sondean por
; polling; la unica interrupcion habilitada es TIMER0.
; Resultados: TEMP_C = grados C; X/Y/Z_MG_H:L = aceleraciones con signo.
MAIN_LOOP:
        MOVLW   0               ; AN0 = LM35
        CALL    LEER_ADC
        CALL    CONVERTIR_TEMP
        CALL    PROCESAR_ALARMA

        CALL    SAMPLE_XYZ_IF_DUE ; AN1/X + AN5/Y + AN6/Z cada 20 ms

        CALL    DISPLAY_SERVICE   ; Multiplexado de los tres displays
        CALL    BUZZER_SERVICE    ; Patron del buzzer (solo lee TICK_FLAG)
        CALL    UART_SERVICE      ; TX, RX y periodo de DATA

        GOTO    MAIN_LOOP

;===============================================================================
; RUTINA DE SERVICIO DE INTERRUPCION (TIMER0)
;===============================================================================
; La ISR solo atiende TIMER0 y solo fija X_SAMPLE_FLAG cada 20 ms. Guarda W y
; STATUS porque BANKSEL modifica RP1:RP0. El ADC y las conversiones se hacen
; en el bucle principal.
ISR_INICIO:
        MOVWF   W_TEMP          ; Guardado de contexto
        SWAPF   STATUS,W
        MOVWF   STATUS_TEMP

        BANKSEL INTCON
        BTFSS   INTCON,2        ; T0IF
        GOTO    ISR_FIN
        BCF     INTCON,2        ; Limpia T0IF

        BANKSEL TMR0
        MOVLW   TMR0_RELOAD
        MOVWF   TMR0

        BANKSEL T0_DIV
        DECF    T0_DIV,F
        BTFSS   STATUS,2        ; Z=1 cada 20 ticks
        GOTO    ISR_FIN
        MOVLW   X_SAMPLE_TICKS
        MOVWF   T0_DIV
        BSF     X_SAMPLE_FLAG,0

ISR_FIN:
        SWAPF   STATUS_TEMP,W   ; Restauracion de contexto
        MOVWF   STATUS
        SWAPF   W_TEMP,F
        SWAPF   W_TEMP,W
        RETFIE

;===============================================================================
; SUBRUTINAS
;===============================================================================

;*******************************************************************************
; @brief    Espera a que el oscilador interno este estable.
; @details  Repite BTFSS OSCCON,2 hasta que HTS = 1.
;*******************************************************************************
ESPERA_OSC:
        BANKSEL OSCCON
        BTFSS   OSCCON,2        ; HTS: 1 cuando el HFINTOSC esta listo
        GOTO    ESPERA_OSC
        RETURN

;*******************************************************************************
; @brief    Deja las salidas en estado inactivo e inicializa variables.
; @details  LED1/LED2 apagados, digitos apagados, BZ_CTRL en alto (buzzer
;           apagado) y segmentos apagados. Limpia FLAGS, el estado del buzzer
;           y los resultados X/Y/Z.
;*******************************************************************************
INIT_SALIDAS:
        BANKSEL PORTA
        CLRF    PORTA           ; LED1 y LED2 apagados
        CLRF    PORTC           ; digitos apagados
        BUZZER_OFF              ; BZ_CTRL = 1, buzzer apagado
        CLRF    PORTD           ; segmentos apagados
        CLRF    FLAGS

        BANKSEL BUZZ_DIV
        CLRF    BUZZ_DIV
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
        RETURN

;*******************************************************************************
; @brief    Configura TIMER0 como base de 1 ms e inicia su interrupcion.
; @details  FOSC/4, prescaler 1:8 y recarga 6. T0_DIV se carga con
;           X_SAMPLE_TICKS y X_SAMPLE_FLAG se limpia. GIE se habilita al final.
;*******************************************************************************
TIMER0_INIT:
        BANKSEL OPTION_REG
        BCF     OPTION_REG,5    ; T0CS=0: reloj interno FOSC/4
        BCF     OPTION_REG,3    ; PSA=0: prescaler asignado a TIMER0
        BCF     OPTION_REG,2    ; PS2:PS0 = 010 -> 1:8
        BSF     OPTION_REG,1
        BCF     OPTION_REG,0

        BANKSEL TMR0
        MOVLW   TMR0_RELOAD
        MOVWF   TMR0

        BANKSEL T0_DIV
        MOVLW   X_SAMPLE_TICKS
        MOVWF   T0_DIV
        CLRF    X_SAMPLE_FLAG

        BANKSEL INTCON
        BCF     INTCON,7        ; GIE se habilita al final
        BCF     INTCON,2        ; Limpia T0IF pendiente
        BSF     INTCON,5        ; T0IE
        BSF     INTCON,7        ; GIE
        RETURN

;*******************************************************************************
; @brief    Configura TIMER1 para el multiplexado de displays.
; @details  Reloj interno FOSC/4, prescaler 1:1 y recarga 0xF830 (1 ms).
;           El principal sondea TMR1IF; no hay interrupcion de TIMER1.
;*******************************************************************************
DISPLAY_INIT:
        BANKSEL T1CON
        CLRF    T1CON           ; Detenido mientras se carga la precarga

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

;*******************************************************************************
; @brief    Avanza un digito cuando TIMER1 vence.
; @details  Orden: decenas, unidades y C. FLAGS<2:1> guardan el estado.
;           Apaga los tres digitos antes de cambiar los segmentos para evitar
;           fantasmas. Genera TICK_FLAG para el protocolo y el buzzer.
;*******************************************************************************
DISPLAY_SERVICE:
        BANKSEL PIR1
        BTFSS   PIR1,0          ; TMR1IF=1 si vencio el milisegundo
        RETURN
        BCF     PIR1,0

        BANKSEL TICK_FLAG
        BSF     TICK_FLAG,0     ; Base de 1 ms para UART y buzzer

        BANKSEL TMR1H
        MOVLW   TMR1_RELOAD_H
        MOVWF   TMR1H
        MOVLW   TMR1_RELOAD_L
        MOVWF   TMR1L

        ; Apaga los tres digitos antes de cambiar segmentos.
        BANKSEL PORTC
        BCF     DIG1
        BCF     DIG2
        BCF     DIG3

        BTFSC   FLAGS,1
        GOTO    DISPLAY_UNIDADES
        BTFSC   FLAGS,2
        GOTO    DISPLAY_C

;----- Estado 00: decenas -----
DISPLAY_DECENAS:
        CALL    DISPLAY_SEPARA
        MOVF    TMP,W           ; TMP = decenas
        CALL    DISPLAY_PATRON
        BANKSEL SEG_PORT
        MOVWF   SEG_PORT
        BANKSEL PORTC
        BSF     DIG1
        BSF     FLAGS,1         ; Siguiente: unidades (01)
        RETURN

;----- Estado 01: unidades -----
DISPLAY_UNIDADES:
        CALL    DISPLAY_SEPARA
        MOVF    COUNT,W         ; COUNT = unidades
        MOVWF   TMP
        CALL    DISPLAY_PATRON
        BANKSEL SEG_PORT
        MOVWF   SEG_PORT
        BANKSEL PORTC
        BSF     DIG2
        BCF     FLAGS,1
        BSF     FLAGS,2         ; Siguiente: C (10)
        RETURN

;----- Estado 10: letra C (segmentos a, d, e, f) -----
DISPLAY_C:
        MOVLW   D'10'              ; Indice especial para C
        MOVWF   TMP
        CALL    DISPLAY_PATRON
        BANKSEL SEG_PORT
        MOVWF   SEG_PORT
        BANKSEL PORTC
        BSF     DIG3
        BCF     FLAGS,2         ; Siguiente: decenas (00)
        RETURN

;*******************************************************************************
; @brief    Separa TEMP_C en decenas y unidades por restas sucesivas.
; @return   TMP = decenas; COUNT = unidades
;*******************************************************************************
DISPLAY_SEPARA:
        BANKSEL TEMP_C
        MOVF    TEMP_C,W
        MOVWF   COUNT
        CLRF    TMP
DISPLAY_SEPARA_LOOP:
        MOVLW   D'10'
        SUBWF   COUNT,W         ; C=1 mientras COUNT >= 10
        BTFSS   STATUS,0
        RETURN
        MOVWF   COUNT
        INCF    TMP,F
        GOTO    DISPLAY_SEPARA_LOOP

;*******************************************************************************
; @brief    Convierte un indice 0-9 o 10 (C) al patron de segmentos.
; @param    TMP = indice
; @return   W = patron para PORTD (RD0=a ... RD6=g, RD7=dp)
;*******************************************************************************
DISPLAY_PATRON:
        MOVF    TMP,W
        BTFSC   STATUS,2
        GOTO    DISPLAY_PATRON_0
        MOVF    TMP,W
        XORLW   1
        BTFSC   STATUS,2
        GOTO    DISPLAY_PATRON_1
        MOVF    TMP,W
        XORLW   2
        BTFSC   STATUS,2
        GOTO    DISPLAY_PATRON_2
        MOVF    TMP,W
        XORLW   3
        BTFSC   STATUS,2
        GOTO    DISPLAY_PATRON_3
        MOVF    TMP,W
        XORLW   4
        BTFSC   STATUS,2
        GOTO    DISPLAY_PATRON_4
        MOVF    TMP,W
        XORLW   5
        BTFSC   STATUS,2
        GOTO    DISPLAY_PATRON_5
        MOVF    TMP,W
        XORLW   6
        BTFSC   STATUS,2
        GOTO    DISPLAY_PATRON_6
        MOVF    TMP,W
        XORLW   7
        BTFSC   STATUS,2
        GOTO    DISPLAY_PATRON_7
        MOVF    TMP,W
        XORLW   8
        BTFSC   STATUS,2
        GOTO    DISPLAY_PATRON_8
        MOVF    TMP,W
        XORLW   9
        BTFSC   STATUS,2
        GOTO    DISPLAY_PATRON_9
        MOVF    TMP,W
        XORLW   D'10'
        BTFSC   STATUS,2
        GOTO    DISPLAY_PATRON_C
        MOVLW   0x00            ; Fuera de rango: display en blanco
        RETURN

DISPLAY_PATRON_0:
        MOVLW   0x3F
        RETURN
DISPLAY_PATRON_1:
        MOVLW   0x06
        RETURN
DISPLAY_PATRON_2:
        MOVLW   0x5B
        RETURN
DISPLAY_PATRON_3:
        MOVLW   0x4F
        RETURN
DISPLAY_PATRON_4:
        MOVLW   0x66
        RETURN
DISPLAY_PATRON_5:
        MOVLW   0x6D
        RETURN
DISPLAY_PATRON_6:
        MOVLW   0x7D
        RETURN
DISPLAY_PATRON_7:
        MOVLW   0x07
        RETURN
DISPLAY_PATRON_8:
        MOVLW   0x7F
        RETURN
DISPLAY_PATRON_9:
        MOVLW   0x6F
        RETURN
DISPLAY_PATRON_C:
        MOVLW   0x39
        RETURN

;*******************************************************************************
; @brief    Espera el tiempo de adquisicion del sample-and-hold.
; @param    W = cantidad de iteraciones (ADC_ACQ_LOOPS)
;*******************************************************************************
DELAY_ACQ:
        MOVWF   COUNT
DELAY_ACQ_LOOP:
        DECFSZ  COUNT,F
        GOTO    DELAY_ACQ_LOOP
        RETURN

;*******************************************************************************
; @brief    Lee un canal del ADC por polling.
; @param    W = numero de canal (0=AN0, 1=AN1, 5=AN5, 6=AN6)
; @return   ADC_H:ADC_L = resultado de 10 bits
;*******************************************************************************
LEER_ADC:
        MOVWF   TMP             ; Guarda el canal
        BCF     STATUS,0
        RLF     TMP,F
        RLF     TMP,F           ; TMP = canal << 2
        MOVF    TMP,W
        IORLW   ADC_CTRL_BASE   ; ADON + ADCS = FOSC/32
        BANKSEL ADCON0
        MOVWF   ADCON0          ; Selecciona canal y enciende ADC

        MOVLW   ADC_ACQ_LOOPS
        CALL    DELAY_ACQ

        BSF     ADCON0,ADC_GO   ; Inicia conversion
ESPERA_ADC:
        BTFSC   ADCON0,ADC_GO   ; GO=1 mientras convierte
        GOTO    ESPERA_ADC

        BANKSEL ADRESL
        MOVF    ADRESL,W
        MOVWF   ADC_L
        BANKSEL ADRESH
        MOVF    ADRESH,W
        ANDLW   0x03            ; Solo bits 9:8
        MOVWF   ADC_H
        RETURN

;*******************************************************************************
; @brief    Convierte las cuentas del LM35 a grados Celsius.
; @details  T = cuentas * 125 / 256, redondeado y saturado a TEMP_MAX.
; @param    ADC_H:ADC_L = cuentas del LM35
; @return   TEMP_C = temperatura en grados C (0..99)
;*******************************************************************************
CONVERTIR_TEMP:
        BANKSEL TEMP_C
        MOVF    ADC_H,W
        BTFSS   STATUS,2        ; ADC_H != 0 -> 125 C o mas
        GOTO    TEMP_SAT
        MOVF    ADC_L,W
        MOVWF   MUL_A
        MOVLW   D'125'
        MOVWF   MUL_B
        CALL    MUL8X8
        MOVLW   D'128'             ; Redondeo: +0,5 cuenta de salida
        ADDWF   RES_L,F
        BTFSC   STATUS,0
        INCF    RES_H,F
        MOVF    RES_H,W
        SUBLW   TEMP_MAX
        BTFSS   STATUS,0        ; C=0 -> RES_H > 99
        GOTO    TEMP_SAT
        MOVF    RES_H,W
        MOVWF   TEMP_C
        RETURN
TEMP_SAT:
        MOVLW   TEMP_MAX
        MOVWF   TEMP_C
        RETURN

;*******************************************************************************
; @brief    Actualiza la alarma termica.
; @details  Alarma activa si TEMP_C > ALARM_TEMP (comparacion estricta).
;*******************************************************************************
PROCESAR_ALARMA:
        BANKSEL ALARM_TEMP
        MOVF    TEMP_C,W
        SUBWF   ALARM_TEMP,W    ; C=1 si TEMP_C <= umbral
        BTFSC   STATUS,0
        GOTO    ALARMA_OFF

ALARMA_ON:
        BSF     ALARM_STATE,0
        BANKSEL PORTA
        BSF     LED1
        BSF     LED2
        RETURN

ALARMA_OFF:
        BCF     ALARM_STATE,0
        BANKSEL PORTA
        BCF     LED1
        BCF     LED2
        BANKSEL PORTC
        BUZZER_OFF
        BANKSEL BUZZ_DIV
        CLRF    BUZZ_DIV
        CLRF    BUZZ_CNT
        BCF     BUZZ_PHASE,0
        RETURN

;*******************************************************************************
; @brief    Patron no bloqueante del buzzer activo.
; @details  Solo LEE TICK_FLAG<0>; no lo limpia, porque UART_SERVICE lo
;           consume para contar PERIOD_MS. Divide los ticks de 1 ms por
;           BUZZ_DIVISOR y alterna 200 ms encendido / 800 ms apagado.
;*******************************************************************************
BUZZER_SERVICE:
        BANKSEL ALARM_STATE
        BTFSS   ALARM_STATE,0
        GOTO    BUZZER_IDLE

        ; Al comenzar una alarma, iniciar inmediatamente la fase de 200 ms.
        BANKSEL BUZZ_CNT
        MOVF    BUZZ_CNT,F
        BTFSC   STATUS,2
        GOTO    BUZZER_START_ON

        BANKSEL TICK_FLAG
        BTFSS   TICK_FLAG,0
        RETURN

        BANKSEL BUZZ_DIV
        INCF    BUZZ_DIV,F
        MOVLW   BUZZ_DIVISOR
        SUBWF   BUZZ_DIV,W
        BTFSS   STATUS,2
        RETURN

        ; 10 ticks de 1 ms = una unidad de fase de 10 ms.
        CLRF    BUZZ_DIV
        DECFSZ  BUZZ_CNT,F
        RETURN

        ; Fin de fase: si estaba encendido, pasar a apagado por 800 ms.
        BTFSS   BUZZ_PHASE,0
        GOTO    BUZZER_START_ON
        BCF     BUZZ_PHASE,0
        MOVLW   BUZZ_OFF_UNITS
        MOVWF   BUZZ_CNT
        BANKSEL PORTC
        BUZZER_OFF
        RETURN

BUZZER_START_ON:
        BANKSEL BUZZ_DIV
        CLRF    BUZZ_DIV
        MOVLW   BUZZ_ON_UNITS
        MOVWF   BUZZ_CNT
        BSF     BUZZ_PHASE,0
        BANKSEL PORTC
        BUZZER_ON
        RETURN

BUZZER_IDLE:
        ; Estado seguro mientras la alarma termica esta apagada.
        BANKSEL BUZZ_DIV
        CLRF    BUZZ_DIV
        CLRF    BUZZ_CNT
        BCF     BUZZ_PHASE,0
        BANKSEL PORTC
        BUZZER_OFF
        RETURN

;*******************************************************************************
; @brief    Multiplica dos valores de 8 bits sin signo.
; @param    MUL_A = multiplicando, MUL_B = multiplicador
; @return   RES_H:RES_L = producto de 16 bits
;*******************************************************************************
MUL8X8:
        CLRF    RES_L
        CLRF    RES_H
        MOVF    MUL_A,W
        MOVWF   MC_L
        CLRF    MC_H
        MOVLW   8
        MOVWF   COUNT
MUL8_LOOP:
        BTFSS   MUL_B,0
        GOTO    MUL8_SKIP
        MOVF    MC_L,W
        ADDWF   RES_L,F
        MOVF    MC_H,W
        BTFSC   STATUS,0
        ADDLW   1
        ADDWF   RES_H,F
MUL8_SKIP:
        BCF     STATUS,0
        RLF     MC_L,F
        RLF     MC_H,F
        BCF     STATUS,0
        RRF     MUL_B,F
        DECFSZ  COUNT,F
        GOTO    MUL8_LOOP
        RETURN

;*******************************************************************************
; @brief    Multiplica un valor de 16 bits por otro de 8 bits.
; @param    DELTA_H:DELTA_L = multiplicando, MUL_B = multiplicador
; @return   RES_H:RES_M:RES_L = producto de 24 bits
;*******************************************************************************
MUL16X8:
        BANKSEL PROD_H
        MOVF    MUL_B,W
        MOVWF   PROD_H          ; Guarda el multiplicador
        MOVF    DELTA_L,W
        MOVWF   MUL_A
        CALL    MUL8X8
        MOVF    RES_L,W
        MOVWF   TMP             ; Producto bajo P_L
        MOVF    RES_H,W
        MOVWF   RES_M           ; Producto alto P_H
        MOVF    PROD_H,W
        MOVWF   MUL_B           ; Restaura el multiplicador
        MOVF    DELTA_H,W
        MOVWF   MUL_A
        CALL    MUL8X8
        MOVF    RES_L,W
        ADDWF   RES_M,F         ; Medio = P_H + Q_L
        BTFSC   STATUS,0
        INCF    RES_H,F         ; Acarreo al byte alto
        MOVF    TMP,W
        MOVWF   RES_L           ; Bajo = P_L
        RETURN

;*******************************************************************************
; @brief    Convierte las cuentas del eje X a miligramos con signo.
; @details  mg = (cuentas - X_OFF) * 49 / 8. El acarreo entre bytes de la
;           negacion se detecta con Z (INCF no modifica C).
; @param    ADC_H:ADC_L = cuentas del eje X
; @return   DELTA_H:DELTA_L = aceleracion en mg (complemento a dos)
;*******************************************************************************
CONVERTIR_X_MG:
        BANKSEL X_OFF_L
        MOVF    ADC_L,W
        MOVWF   DELTA_L
        MOVF    ADC_H,W
        MOVWF   DELTA_H
        MOVF    X_OFF_L,W
        SUBWF   DELTA_L,F
        MOVF    X_OFF_H,W
        BTFSS   STATUS,0
        ADDLW   1
        SUBWF   DELTA_H,F
        BTFSC   STATUS,0
        GOTO    X_POSITIVO
        COMF    DELTA_L,F
        COMF    DELTA_H,F
        INCF    DELTA_L,F
        BTFSC   STATUS,2        ; Z=1: acarreo al byte alto
        INCF    DELTA_H,F
        BSF     FLAGS,0         ; Signo negativo
        GOTO    X_MAGNITUD
X_POSITIVO:
        BCF     FLAGS,0
X_MAGNITUD:
        MOVLW   X_MG_NUM
        MOVWF   MUL_B
        CALL    MUL16X8
        ; Divide por 8: tres desplazamientos a la derecha de 24 bits.
        BCF     STATUS,0
        RRF     RES_H,F
        RRF     RES_M,F
        RRF     RES_L,F
        BCF     STATUS,0
        RRF     RES_H,F
        RRF     RES_M,F
        RRF     RES_L,F
        BCF     STATUS,0
        RRF     RES_H,F
        RRF     RES_M,F
        RRF     RES_L,F
        MOVF    RES_L,W
        MOVWF   DELTA_L
        MOVF    RES_M,W
        MOVWF   DELTA_H
        BTFSS   FLAGS,0
        RETURN
        COMF    DELTA_L,F
        COMF    DELTA_H,F
        INCF    DELTA_L,F
        BTFSC   STATUS,2        ; Z=1: acarreo al byte alto
        INCF    DELTA_H,F
        RETURN

;*******************************************************************************
; @brief    Convierte las cuentas del eje Y a miligramos con signo.
; @details  mg = (cuentas - Y_OFFSET) * 49 / 8. Usa Y_SIGN para no pisar el
;           signo de X guardado en FLAGS<0>.
; @param    ADC_H:ADC_L = cuentas del eje Y
; @return   Y_MG_H:Y_MG_L = aceleracion Y en mg
;*******************************************************************************
CONVERTIR_Y_MG:
        BANKSEL Y_MG_L
        MOVF    ADC_L,W
        MOVWF   DELTA_L
        MOVF    ADC_H,W
        MOVWF   DELTA_H
        MOVLW   Y_OFFSET_L
        SUBWF   DELTA_L,F
        MOVLW   Y_OFFSET_H
        BTFSS   STATUS,0
        ADDLW   1
        SUBWF   DELTA_H,F
        BTFSC   STATUS,0
        GOTO    Y_POSITIVO
        COMF    DELTA_L,F
        COMF    DELTA_H,F
        INCF    DELTA_L,F
        BTFSC   STATUS,2
        INCF    DELTA_H,F
        BSF     Y_SIGN,0
        GOTO    Y_MAGNITUD
Y_POSITIVO:
        BCF     Y_SIGN,0
Y_MAGNITUD:
        MOVLW   X_MG_NUM
        MOVWF   MUL_B
        CALL    MUL16X8
        ; Divide por 8.
        BCF     STATUS,0
        RRF     RES_H,F
        RRF     RES_M,F
        RRF     RES_L,F
        BCF     STATUS,0
        RRF     RES_H,F
        RRF     RES_M,F
        RRF     RES_L,F
        BCF     STATUS,0
        RRF     RES_H,F
        RRF     RES_M,F
        RRF     RES_L,F
        MOVF    RES_L,W
        MOVWF   DELTA_L
        MOVF    RES_M,W
        MOVWF   DELTA_H
        BTFSS   Y_SIGN,0
        GOTO    Y_GUARDAR
        COMF    DELTA_L,F
        COMF    DELTA_H,F
        INCF    DELTA_L,F
        BTFSC   STATUS,2
        INCF    DELTA_H,F
Y_GUARDAR:
        BANKSEL Y_MG_L
        MOVF    DELTA_L,W
        MOVWF   Y_MG_L
        MOVF    DELTA_H,W
        MOVWF   Y_MG_H
        RETURN

;*******************************************************************************
; @brief    Convierte las cuentas del eje Z a miligramos con signo.
; @details  Z es PROVISIONAL: offset 338 y factor 49/8 sin calibrar.
; @param    ADC_H:ADC_L = cuentas del eje Z
; @return   Z_MG_H:Z_MG_L = aceleracion Z en mg
;*******************************************************************************
CONVERTIR_Z_MG:
        BANKSEL Z_MG_L
        MOVF    ADC_L,W
        MOVWF   DELTA_L
        MOVF    ADC_H,W
        MOVWF   DELTA_H
        MOVLW   Z_OFFSET_L
        SUBWF   DELTA_L,F
        MOVLW   Z_OFFSET_H
        BTFSS   STATUS,0
        ADDLW   1
        SUBWF   DELTA_H,F
        BTFSC   STATUS,0
        GOTO    Z_POSITIVO
        COMF    DELTA_L,F
        COMF    DELTA_H,F
        INCF    DELTA_L,F
        BTFSC   STATUS,2
        INCF    DELTA_H,F
        BSF     Z_SIGN,0
        GOTO    Z_MAGNITUD
Z_POSITIVO:
        BCF     Z_SIGN,0
Z_MAGNITUD:
        MOVLW   Z_MG_NUM
        MOVWF   MUL_B
        CALL    MUL16X8
        ; Divide por 8.
        BCF     STATUS,0
        RRF     RES_H,F
        RRF     RES_M,F
        RRF     RES_L,F
        BCF     STATUS,0
        RRF     RES_H,F
        RRF     RES_M,F
        RRF     RES_L,F
        BCF     STATUS,0
        RRF     RES_H,F
        RRF     RES_M,F
        RRF     RES_L,F
        MOVF    RES_L,W
        MOVWF   DELTA_L
        MOVF    RES_M,W
        MOVWF   DELTA_H
        BTFSS   Z_SIGN,0
        GOTO    Z_GUARDAR
        COMF    DELTA_L,F
        COMF    DELTA_H,F
        INCF    DELTA_L,F
        BTFSC   STATUS,2
        INCF    DELTA_H,F
Z_GUARDAR:
        BANKSEL Z_MG_L
        MOVF    DELTA_L,W
        MOVWF   Z_MG_L
        MOVF    DELTA_H,W
        MOVWF   Z_MG_H
        RETURN

;*******************************************************************************
; @brief    Lee y convierte X, Y y Z cuando TIMER0 completa 20 ticks.
; @details  La ISR solo fija la bandera. Se enmascara GIE brevemente al
;           consumirla para no perder una muestra que llegue durante el
;           test-and-clear.
;*******************************************************************************
SAMPLE_XYZ_IF_DUE:
        BANKSEL INTCON
        BCF     INTCON,7        ; Seccion critica de test-and-clear
        BANKSEL X_SAMPLE_FLAG
        BTFSS   X_SAMPLE_FLAG,0
        GOTO    SAMPLE_XYZ_NOT_DUE
        BCF     X_SAMPLE_FLAG,0
        BANKSEL INTCON
        BSF     INTCON,7

        MOVLW   1               ; AN1 = X del MMA7361
        CALL    LEER_ADC
        CALL    CONVERTIR_X_MG
        ; Guardar X antes de reutilizar el workspace para Y.
        BANKSEL X_MG_L
        MOVF    DELTA_L,W
        MOVWF   X_MG_L
        MOVF    DELTA_H,W
        MOVWF   X_MG_H

        MOVLW   5               ; AN5 = Y del MMA7361
        CALL    LEER_ADC
        BANKSEL Y_L
        MOVF    ADC_L,W
        MOVWF   Y_L
        MOVF    ADC_H,W
        MOVWF   Y_H
        CALL    CONVERTIR_Y_MG

        MOVLW   6               ; AN6 = Z del MMA7361
        CALL    LEER_ADC
        BANKSEL Z_L
        MOVF    ADC_L,W
        MOVWF   Z_L
        MOVF    ADC_H,W
        MOVWF   Z_H
        CALL    CONVERTIR_Z_MG
        RETURN

SAMPLE_XYZ_NOT_DUE:
        BANKSEL INTCON
        BSF     INTCON,7
        RETURN

;*******************************************************************************
; @brief    Inicia el EUSART y el estado del protocolo.
;*******************************************************************************
UART_INIT:
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
        MOVLW   0x01            ; Streaming habilitado desde el reset
        MOVWF   MODO
        RETURN

;*******************************************************************************
; @brief    Atiende TX, RX y el periodo de muestreo. Se llama en cada vuelta.
;*******************************************************************************
UART_SERVICE:
        ;----- Transmision: un byte por pasada -----
        BANKSEL PIR1
        BTFSS   PIR1,4          ; TXIF
        GOTO    UART_RX
        BANKSEL TX_CNT
        MOVF    TX_CNT,W
        BTFSC   STATUS,2        ; Buffer vacio
        GOTO    UART_RX
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
UART_RX:
        BANKSEL PIR1
        BTFSS   PIR1,5          ; RCIF
        GOTO    UART_TICK
        BANKSEL RCSTA
        BTFSC   RCSTA,1         ; OERR
        GOTO    UART_RX_RESTART
        BTFSC   RCSTA,2         ; FERR: descarta el byte y resincroniza
        GOTO    UART_FRAMING_ERROR
        MOVF    RCREG,W
        CALL    RX_BYTE
        GOTO    UART_RX         ; Puede quedar otro byte en la FIFO
UART_FRAMING_ERROR:
        MOVF    RCREG,W         ; Leer RCREG libera el caracter con error
        BANKSEL RX_STATE
        CLRF    RX_STATE
        GOTO    UART_RX
UART_RX_RESTART:
        BCF     RCSTA,4         ; CREN
        BSF     RCSTA,4         ; CREN
        BANKSEL RX_STATE
        CLRF    RX_STATE        ; Descarta la trama parcial tras overrun
        GOTO    UART_TICK

        ;----- Base de tiempo de 1 ms y periodo de muestreo -----
UART_TICK:
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
        CALL    SEND_DATA
        RETURN

;*******************************************************************************
; @brief    Encola un byte en el buffer circular de transmision.
; @param    W = byte
;*******************************************************************************
TX_PUSH:
        BANKSEL TX_CNT
        MOVWF   TMP2
        MOVF    TX_CNT,W
        XORLW   D'32'
        BTFSC   STATUS,2
        RETURN                  ; Buffer lleno: descarta el byte
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

;*******************************************************************************
; @brief    Actualiza el CRC8 de transmision con un byte.
; @param    W = byte; CRC_REG = CRC parcial
;*******************************************************************************
CRC8_UPDATE:
        BANKSEL CRC_REG
        XORWF   CRC_REG,F
        MOVLW   8
        MOVWF   CRC_CNT
CRC8_LOOP:
        BTFSS   CRC_REG,7
        GOTO    CRC8_SHIFT
        BCF     STATUS,0
        RLF     CRC_REG,F
        MOVLW   PROTO_CRC_POLY
        XORWF   CRC_REG,F
        GOTO    CRC8_NEXT
CRC8_SHIFT:
        BCF     STATUS,0
        RLF     CRC_REG,F
CRC8_NEXT:
        DECFSZ  CRC_CNT,F
        GOTO    CRC8_LOOP
        RETURN

;*******************************************************************************
; @brief    Actualiza el CRC8 de recepcion con un byte.
; @param    W = byte; CRC_RX = CRC parcial de recepcion
;*******************************************************************************
CRC8_UPDATE_RX:
        BANKSEL CRC_RX
        XORWF   CRC_RX,F
        MOVLW   8
        MOVWF   CRC_CNT_RX
CRC8_LOOP_RX:
        BTFSS   CRC_RX,7
        GOTO    CRC8_SHIFT_RX
        BCF     STATUS,0
        RLF     CRC_RX,F
        MOVLW   PROTO_CRC_POLY
        XORWF   CRC_RX,F
        GOTO    CRC8_NEXT_RX
CRC8_SHIFT_RX:
        BCF     STATUS,0
        RLF     CRC_RX,F
CRC8_NEXT_RX:
        DECFSZ  CRC_CNT_RX,F
        GOTO    CRC8_LOOP_RX
        RETURN

;*******************************************************************************
; @brief    Encola un byte y lo incluye en el CRC de transmision.
; @param    W = byte
;*******************************************************************************
TX_FRAME_BYTE:
        MOVWF   TMP2
        CALL    CRC8_UPDATE
        MOVF    TMP2,W
        CALL    TX_PUSH
        RETURN

;*******************************************************************************
; @brief    Arma y encola una trama DATA v3.
; @details  LEN=10: TIPO + SEQ, TEMP, X_L, X_H, Y_L, Y_H, Z_L, Z_H, FLAGS.
;*******************************************************************************
SEND_DATA:
        BANKSEL MODO
        BTFSS   MODO,0
        RETURN
        MOVF    TX_CNT,W
        SUBLW   D'18'              ; C=1 si TX_CNT <= 18 (libre >= 14)
        BTFSS   STATUS,0
        RETURN

        MOVLW   PROTO_SYNC1
        CALL    TX_PUSH
        MOVLW   PROTO_SYNC2
        CALL    TX_PUSH

        CLRF    CRC_REG
        MOVLW   D'10'              ; TIPO + 9 datos (DATA v3)
        CALL    TX_FRAME_BYTE
        MOVLW   T_DATA
        CALL    TX_FRAME_BYTE

        MOVF    SEQ,W
        CALL    TX_FRAME_BYTE
        INCF    SEQ,F

        MOVF    TEMP_C,W
        CALL    TX_FRAME_BYTE
        MOVF    X_MG_L,W
        CALL    TX_FRAME_BYTE
        MOVF    X_MG_H,W
        CALL    TX_FRAME_BYTE
        MOVF    Y_MG_L,W
        CALL    TX_FRAME_BYTE
        MOVF    Y_MG_H,W
        CALL    TX_FRAME_BYTE
        MOVF    Z_MG_L,W
        CALL    TX_FRAME_BYTE
        MOVF    Z_MG_H,W
        CALL    TX_FRAME_BYTE

        CLRF    TMP2
        BTFSC   ALARM_STATE,0
        BSF     TMP2,0
        MOVF    TMP2,W
        CALL    TX_FRAME_BYTE

        MOVF    CRC_REG,W
        CALL    TX_PUSH
        RETURN

;*******************************************************************************
; @brief    Arma y encola la trama STATUS.
; @details  LEN=7: TIPO + VERSION, PERIOD, THRESH, OFF_L, OFF_H, MODO.
;*******************************************************************************
SEND_STATUS:
        BANKSEL TX_CNT
        MOVF    TX_CNT,W
        SUBLW   D'21'              ; Libre >= 11
        BTFSS   STATUS,0
        RETURN

        MOVLW   PROTO_SYNC1
        CALL    TX_PUSH
        MOVLW   PROTO_SYNC2
        CALL    TX_PUSH

        CLRF    CRC_REG
        MOVLW   7               ; TIPO + 6 datos
        CALL    TX_FRAME_BYTE
        MOVLW   T_STATUS
        CALL    TX_FRAME_BYTE
        MOVLW   PROTO_VERSION
        CALL    TX_FRAME_BYTE
        MOVF    PERIOD_MS,W
        CALL    TX_FRAME_BYTE
        MOVF    ALARM_TEMP,W
        CALL    TX_FRAME_BYTE
        MOVF    X_OFF_L,W
        CALL    TX_FRAME_BYTE
        MOVF    X_OFF_H,W
        CALL    TX_FRAME_BYTE
        MOVF    MODO,W
        CALL    TX_FRAME_BYTE

        MOVF    CRC_REG,W
        CALL    TX_PUSH
        RETURN

;*******************************************************************************
; @brief    Arma y encola una trama ACK.
; @details  LEN=3: TIPO + CMD, RESULT.
;*******************************************************************************
SEND_ACK:
        BANKSEL TX_CNT
        MOVF    TX_CNT,W
        SUBLW   D'25'              ; Libre >= 7
        BTFSS   STATUS,0
        RETURN

        MOVLW   PROTO_SYNC1
        CALL    TX_PUSH
        MOVLW   PROTO_SYNC2
        CALL    TX_PUSH

        CLRF    CRC_REG
        MOVLW   3               ; TIPO + 2 datos
        CALL    TX_FRAME_BYTE
        MOVLW   T_ACK
        CALL    TX_FRAME_BYTE
        MOVF    ACK_CMD,W
        CALL    TX_FRAME_BYTE
        MOVF    ACK_RES,W
        CALL    TX_FRAME_BYTE

        MOVF    CRC_REG,W
        CALL    TX_PUSH
        RETURN

;*******************************************************************************
; @brief    Procesa un byte recibido segun la maquina de estados.
; @param    W = byte
;*******************************************************************************
RX_BYTE:
        BANKSEL TMP2
        MOVWF   TMP2
        BANKSEL RX_STATE
        MOVF    RX_STATE,W
        XORLW   0
        BTFSC   STATUS,2
        GOTO    RX_STATE0
        MOVF    RX_STATE,W
        XORLW   1
        BTFSC   STATUS,2
        GOTO    RX_STATE1
        MOVF    RX_STATE,W
        XORLW   2
        BTFSC   STATUS,2
        GOTO    RX_STATE2
        MOVF    RX_STATE,W
        XORLW   3
        BTFSC   STATUS,2
        GOTO    RX_STATE3
        GOTO    RX_STATE4

;----- Estado 0: espera el primer byte de sincronismo (0xAA) -----
RX_STATE0:
        MOVF    TMP2,W
        XORLW   PROTO_SYNC1
        BTFSS   STATUS,2
        RETURN
        MOVLW   1
        MOVWF   RX_STATE
        RETURN

;----- Estado 1: espera el segundo byte de sincronismo (0x55) -----
RX_STATE1:
        MOVF    TMP2,W
        XORLW   PROTO_SYNC2
        BTFSC   STATUS,2
        GOTO    RX_SYNC_OK
        MOVF    TMP2,W
        XORLW   PROTO_SYNC1
        BTFSC   STATUS,2
        RETURN                  ; Sigue esperando el segundo byte
        CLRF    RX_STATE
        RETURN
RX_SYNC_OK:
        MOVLW   2
        MOVWF   RX_STATE
        RETURN

;----- Estado 2: recepcion de LEN y validacion de longitud -----
RX_STATE2:
        MOVF    TMP2,W
        BTFSC   STATUS,2
        GOTO    RX_ABORT        ; LEN = 0 invalido
        MOVF    TMP2,W
        SUBLW   8
        BTFSS   STATUS,0        ; C=0 -> LEN > 8
        GOTO    RX_ABORT
        MOVF    TMP2,W
        MOVWF   RX_LEN
        CLRF    CRC_RX
        MOVF    RX_LEN,W
        CALL    CRC8_UPDATE_RX  ; El CRC tambien procesa LEN
        CLRF    RX_IDX
        MOVLW   3
        MOVWF   RX_STATE
        RETURN

;----- Estado 3: recepcion de TIPO y DATOS, actualizacion de CRC -----
RX_STATE3:
        MOVF    TMP2,W
        CALL    CRC8_UPDATE_RX
        MOVF    RX_IDX,W
        BTFSC   STATUS,2
        GOTO    RX_STORE_TYPE
        MOVF    RX_IDX,W
        XORLW   1
        BTFSC   STATUS,2
        GOTO    RX_STORE_D0
        MOVF    RX_IDX,W
        XORLW   2
        BTFSC   STATUS,2
        GOTO    RX_STORE_D1
        GOTO    RX_IDX_NEXT
RX_STORE_TYPE:
        MOVF    TMP2,W
        MOVWF   RX_TYPE
        GOTO    RX_IDX_NEXT
RX_STORE_D0:
        MOVF    TMP2,W
        MOVWF   RX_D0
        GOTO    RX_IDX_NEXT
RX_STORE_D1:
        MOVF    TMP2,W
        MOVWF   RX_D1
RX_IDX_NEXT:
        INCF    RX_IDX,F
        MOVF    RX_IDX,W
        XORWF   RX_LEN,W
        BTFSS   STATUS,2
        RETURN
        MOVLW   4
        MOVWF   RX_STATE
        RETURN

;----- Estado 4: recepcion y validacion del CRC final -----
RX_STATE4:
        CLRF    RX_STATE
        MOVF    TMP2,W
        XORWF   CRC_RX,W
        BTFSS   STATUS,2
        RETURN                  ; CRC invalido: descarta la trama
        GOTO    RX_PROCESS

RX_ABORT:
        CLRF    RX_STATE
        RETURN

;*******************************************************************************
; @brief    Despacha el comando recibido y responde con ACK.
;*******************************************************************************
RX_PROCESS:
        BANKSEL RX_TYPE
        MOVF    RX_TYPE,W
        XORLW   CMD_PING
        BTFSC   STATUS,2
        GOTO    RX_CMD_PING
        MOVF    RX_TYPE,W
        XORLW   CMD_START
        BTFSC   STATUS,2
        GOTO    RX_CMD_START
        MOVF    RX_TYPE,W
        XORLW   CMD_STOP
        BTFSC   STATUS,2
        GOTO    RX_CMD_STOP
        MOVF    RX_TYPE,W
        XORLW   CMD_SET_THRESH
        BTFSC   STATUS,2
        GOTO    RX_CMD_SET_THRESH
        MOVF    RX_TYPE,W
        XORLW   CMD_GET_STATUS
        BTFSC   STATUS,2
        GOTO    RX_CMD_GET_STATUS
        MOVF    RX_TYPE,W
        XORLW   CMD_SET_OFFSET
        BTFSC   STATUS,2
        GOTO    RX_CMD_SET_OFFSET
        MOVLW   RES_UNKNOWN
        GOTO    RX_CMD_ACK

;----- PING: responde OK -----
RX_CMD_PING:
        MOVF    RX_LEN,W
        XORLW   1
        BTFSS   STATUS,2
        GOTO    RX_CMD_BAD_PARAM
        MOVLW   RES_OK
        GOTO    RX_CMD_ACK

;----- START: habilita streaming y opcionalmente cambia el periodo -----
RX_CMD_START:
        MOVF    RX_LEN,W
        XORLW   2
        BTFSS   STATUS,2
        GOTO    RX_CMD_BAD_PARAM
        MOVF    RX_D0,W
        BTFSC   STATUS,2
        GOTO    RX_CMD_START_ENABLE ; 0 = mantiene el periodo actual
        MOVF    RX_D0,W
        SUBLW   PROTO_PERIOD_MIN-1
        BTFSC   STATUS,0        ; C=1 -> menor que el minimo
        GOTO    RX_CMD_BAD_PARAM
        MOVF    RX_D0,W
        SUBLW   PROTO_PERIOD_MAX
        BTFSS   STATUS,0        ; C=0 -> mayor que el maximo
        GOTO    RX_CMD_BAD_PARAM
        MOVF    RX_D0,W
        MOVWF   PERIOD_MS
        MOVWF   PERIOD_CNT
RX_CMD_START_ENABLE:
        BSF     MODO,0
        MOVLW   RES_OK
        GOTO    RX_CMD_ACK

;----- STOP: deshabilita streaming -----
RX_CMD_STOP:
        MOVF    RX_LEN,W
        XORLW   1
        BTFSS   STATUS,2
        GOTO    RX_CMD_BAD_PARAM
        BCF     MODO,0
        MOVLW   RES_OK
        GOTO    RX_CMD_ACK

;----- SET_THRESHOLD: umbral de alarma (0..99 C) -----
RX_CMD_SET_THRESH:
        MOVF    RX_LEN,W
        XORLW   2
        BTFSS   STATUS,2
        GOTO    RX_CMD_BAD_PARAM
        MOVF    RX_D0,W
        SUBLW   TEMP_MAX
        BTFSS   STATUS,0        ; C=0 -> mayor que 99
        GOTO    RX_CMD_BAD_PARAM
        MOVF    RX_D0,W
        MOVWF   ALARM_TEMP
        MOVLW   RES_OK
        GOTO    RX_CMD_ACK

;----- GET_STATUS: envia la trama STATUS -----
RX_CMD_GET_STATUS:
        MOVF    RX_LEN,W
        XORLW   1
        BTFSS   STATUS,2
        GOTO    RX_CMD_BAD_PARAM
        CALL    SEND_STATUS
        RETURN

;----- SET_OFFSET: offset de X (0..1023) -----
RX_CMD_SET_OFFSET:
        MOVF    RX_LEN,W
        XORLW   3
        BTFSS   STATUS,2
        GOTO    RX_CMD_BAD_PARAM
        MOVF    RX_D1,W
        SUBLW   3               ; C=1 si D1 <= 3 (offset <= 1023)
        BTFSS   STATUS,0
        GOTO    RX_CMD_BAD_PARAM
        MOVF    RX_D0,W
        MOVWF   X_OFF_L
        MOVF    RX_D1,W
        MOVWF   X_OFF_H
        MOVLW   RES_OK
        GOTO    RX_CMD_ACK

RX_CMD_BAD_PARAM:
        MOVLW   RES_BAD_PARAM
RX_CMD_ACK:
        MOVWF   ACK_RES
        MOVF    RX_TYPE,W
        MOVWF   ACK_CMD
        CALL    SEND_ACK
        RETURN

;===============================================================================
        END
;===============================================================================
