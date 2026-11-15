;===============================================================================
; @file       handmotion_work.S
;
; @author     Lurgo Donato
;
; @date       06/11/2026
;
; @brief      HAND MOTION - Firmware de trabajo v3: ADC, alarma, displays y EUSART.
;
; @details    PIC16F887 con oscilador interno a 8 MHz (OSCCON IRCF=111).
;             ADC a FOSC/32 (TAD = 4 us); AN1/X, AN5/Y y AN6/Z se muestrean
;             juntos cada 20 ms mediante TIMER0. LM35/AN0 se conserva.
;             Sin amplificadores operacionales. Convierte temperatura y ejes,
;             controla la alarma termica, multiplexa tres displays con TIMER1
;             y comunica temperatura/X/Y/Z por EUSART con protocolo CRC-8.
;
;             Mapa de pines segun la Rev E del esquema:
;               RA0/AN0  LM35                       entrada analogica
;               RA1/AN1  X del MMA7361 (directo)    entrada analogica
;               RA2/AN2  LED1                       salida digital
;               RA3/AN3  libre                      entrada analogica reservada
;               RA4      libre                      entrada open-drain
;               RA5/AN4  LED2                       salida digital
;               RE0/AN5  Y del MMA7361 (directo)    entrada analogica
;               RE1/AN6  Z del MMA7361 (directo)    entrada analogica
;               RE2/AN7  libre
;               RE3/MCLR reset externo              entrada (MCLRE=ON)
;               RC0-RC2  DIG1-DIG3 (bases Q1-Q3)    salidas activas altas
;               RC3      BZ_CTRL (I/O del modulo)   salida
;               RC6/TX   TX_TTL                     salida EUSART
;               RC7/RX   RX_TTL                     entrada EUSART
;               RD0-RD7  segmentos a,b,c,d,e,f,g,dp salidas activas altas
;               RB3/PGM, RB6/PGC, RB7/PGD           reservados a ICSP
;
;             Z usa parametros PROVISIONALES: calibrar con el MMA7361 real.
;             Sensor: MMA7361 en rango +-1,5 g, salidas directas al ADC y
;             referencia VREF = VDD. La calibracion de cada eje debe medirse
;             con la placa real antes de usar los mg en analisis de movimiento.
;             Displays rojos de catodo comun (decision 2026-11-12): segmentos
;             activos altos; Q1-Q3 BC337 como selectores de catodo lado bajo.
;             R9-R16=220 ohm adoptadas para 10 mA (confirmar Vf/VOH);
;             R17-R19=330 ohm quedan como valores existentes a validar.
;             R21-R22=220 ohm y R23=10 kohm siguen calculadas. LED1 se movio
;             de RA4 a RA2 porque RA4 es open-drain y no puede entregar corriente.
;             EUSART a 9600 Bd con protocolo v3 AA 55 / LEN / TIPO / DATOS /
;             CRC8. DATA transmite temperatura, X/Y/Z y alarma. El modulo
;             esta en modules/uart.inc.
;             Etapa 5: TIMER0 FOSC/4, prescaler 1:8, precarga 6 (1 ms nominal);
;             cada 20 ticks inicia una muestra X/Y/Z en foreground.
;             El modulo buzzer MDU1095 (3,5-5,5 V) tiene trigger activo-bajo:
;             RC3 alto lo apaga, RC3 bajo lo activa. Confirmar corriente de
;             la entrada I/O en banco (los 30 mA son del modulo).
;===============================================================================

;===============================================================================
; DIRECTIVAS DE INCLUSION
;===============================================================================
        PROCESSOR 16F887
        #include <xc.inc>

;===============================================================================
; CONFIGURACION GENERAL DEL MCU
;===============================================================================
; Oscilador interno, sin salida de reloj en RA6.
; El resto de los bits se fija con los valores ya verificados en el DFP.
        CONFIG FOSC = INTRC_NOCLKOUT
        CONFIG WDTE = OFF
        CONFIG PWRTE = ON
        CONFIG MCLRE = ON
        CONFIG CP = OFF
        CONFIG CPD = OFF
        CONFIG BOREN = ON
        CONFIG IESO = OFF
        CONFIG FCMEN = OFF
        CONFIG LVP = OFF
        CONFIG DEBUG = OFF
        CONFIG BOR4V = BOR40V
        CONFIG WRT = OFF

;===============================================================================
; DEFINICION DE CONSTANTES
;===============================================================================
; Reloj interno a 8 MHz confirmado como decision de diseno.
;   FOSC = 8 MHz            -> TCY = 4 / FOSC = 0,5 us
;   OSCCON = 0111 0000b     -> IRCF<2:0> = 111 (8 MHz), SCS = 00 (INTOSC)
;
; Temporizacion confirmada para esta etapa:
;   TIMER0  FOSC/4, prescaler 1:8, precarga 6 -> 1 ms nominal
;   Muestreo de X cada 20 ticks                 -> 20 ms / 50 Hz
;   EUSART  9600 Bd, BRGH=1                     -> SPBRG = 51
        FOSC_KHZ        EQU     8000
        TCY_NS          EQU     500
        OSCCON_8MHZ     EQU     0x70

; EUSART: 8 MHz / (16 * (51 + 1)) = 9615 Bd, error +0,16 % sobre 9600.
;   TXSTA = 0010 0100b -> TXEN = 1, BRGH = 1, SYNC = 0
;   RCSTA = 1001 0000b -> SPEN = 1, CREN = 1
        EUSART_SPBRG    EQU     51
        EUSART_TXSTA    EQU     0x24
        EUSART_RCSTA    EQU     0x90

; Protocolo serie: ver modules/uart.inc y docs/comunicacion/protocolo.md
        PROTO_SYNC1     EQU     0xAA
        PROTO_SYNC2     EQU     0x55
        PROTO_VERSION   EQU     3
        PROTO_CRC_POLY  EQU     0x07
        PROTO_PERIOD    EQU     50      ; 50 ms = 20 Hz por defecto
        PROTO_PERIOD_MIN EQU    20      ; 50 Hz
        PROTO_PERIOD_MAX EQU    250     ; 4 Hz

; TIMER0: TCY=0,5 us; (256-6) x 8 x 0,5 us = 1 ms nominal.
        TMR0_RELOAD     EQU     6
        X_SAMPLE_TICKS  EQU     20      ; 20 ms = 50 Hz para AN1/X, AN5/Y y AN6/Z

        T_DATA          EQU     0x01
        T_STATUS        EQU     0x02
        T_ACK           EQU     0x03

        CMD_PING        EQU     0x81
        CMD_START       EQU     0x82
        CMD_STOP        EQU     0x83
        CMD_SET_THRESH  EQU     0x84
        CMD_GET_STATUS  EQU     0x85
        CMD_SET_OFFSET  EQU     0x86

        RES_OK          EQU     0
        RES_BAD_PARAM   EQU     1
        RES_UNKNOWN     EQU     2

; ADC: FOSC/32 -> TAD = 4 us (valido para VREF = VDD = 5 V)
;   ADCON0 = 10 0000 01b -> ADCS = 10 (FOSC/32), CHS = 0000 (AN0), ADON = 1
;   ADCON1 = 1000 0000b -> ADFM = 1 (justificado a la derecha), VCFG = 00
;   La adquisicion se espera con un lazo conservador de ~23 us.
        ADC_ADCON1_INIT EQU     0x80
        ADC_CTRL_BASE   EQU     0x81    ; ADON + ADCS = FOSC/32
        ADC_ACQ_LOOPS   EQU     14      ; ~23 us a 8 MHz
        ADC_GO          EQU     1       ; bit GO/DONE de ADCON0

; TIMER1 interno FOSC/4, prescaler 1:1: 2000 cuentas = 1 ms.
        TMR1_RELOAD_H   EQU     0xF8
        TMR1_RELOAD_L   EQU     0x30

; Alarma termica: ambos LED y buzzer activos si TEMP_C > 40 C.
        TEMP_ALARM     EQU     40

; Patron sonoro intermitente. El MDU1095 es un buzzer ACTIVO: su frecuencia
; (unos 2500 Hz) la fija su oscilador interno y NO se puede cambiar desde el
; PIC. El firmware solo conmuta RC3 para dar el ritmo:
;   200 ms encendido + 800 ms apagado = 1 s por ciclo.
; Se cuenta en unidades de 10 ms para que cada fase quepa en un byte.
        BUZZ_DIVISOR   EQU     10      ; ticks de 1 ms por unidad de 10 ms
        BUZZ_ON_UNITS  EQU     20      ; 20 x 10 ms = 200 ms encendido
        BUZZ_OFF_UNITS EQU     80      ; 80 x 10 ms = 800 ms apagado

; Conversion de las cuentas ADC
;   LM35: 10 mV/C, VREF = 5 V -> 4,8828 mV/cuenta -> 0,48828 C/cuenta
;         T = cuentas * 125 / 256 (redondeado)
;   Ejes X/Y/Z (MMA7361, rango +-1,5 g, modulo a 3,3 V):
;         0 g nominal -> VCC/2 = 1,65 V -> 338 cuentas (depende de VCC real)
;         800 mV/g -> 163,84 cuentas/g -> 6,103 mg/cuenta
;         mg = (cuentas - offset) * 49 / 8 (6,125 mg/cuenta, error 0,35 %)
;         X/Y conservan los parametros de v2. Z: offset 338 y factor 49/8 son
;         SOLO PROVISIONALES; medir el modulo real antes de declarar calibracion.
        TEMP_MAX        EQU     99
        X_OFFSET_L      EQU     0x52    ; 338 = 0x0152
        X_OFFSET_H      EQU     0x01
        Y_OFFSET_L      EQU     0x52    ; nominal 338 = 0x0152
        Y_OFFSET_H      EQU     0x01
        Z_OFFSET_L      EQU     0x52    ; PROVISIONAL: 338, pendiente de calibracion
        Z_OFFSET_H      EQU     0x01
        X_MG_NUM        EQU     49
        Z_MG_NUM        EQU     49      ; PROVISIONAL: factor 49/8, pendiente de calibracion

; Bits analogicos habilitados en ANSEL: AN0 (LM35), AN1 (X), AN5 (Y), AN6 (Z)
        ANSEL_INIT      EQU     0x63

; Direcciones de puerto para la Rev E
        TRISA_INIT      EQU     0xDB    ; RA2/RA5 salidas; RA4 y resto entradas
        TRISB_INIT      EQU     0xFF    ; todo entrada (ICSP incluido)
        TRISC_INIT      EQU     0xB0    ; RC0-RC3 y RC6 salidas
        TRISD_INIT      EQU     0x00    ; RD0-RD7 salidas (segmentos)
        TRISE_INIT      EQU     0x0F    ; RE0-RE3 entradas

;===============================================================================
; DEFINICION DE VARIABLES
;===============================================================================
; Variables en RAM comun (0x70-0x7F): accesibles desde cualquier banco sin
; BANKSEL. Son 16 bytes, el maximo de RAM comun del PIC16F887.
; La ISR de TIMER0 preserva W y STATUS en RAM comun.
        PSECT   udata_shr,class=COMMON

ADC_L:          DS      1       ; resultado ADC, byte bajo
ADC_H:          DS      1       ; resultado ADC, bits 9:8
TMP:            DS      1       ; auxiliar; en mul16x8 guarda el producto bajo
COUNT:          DS      1       ; contador de lazos (demora y multiplicacion)
MUL_A:          DS      1       ; multiplicando de 8 bits
MUL_B:          DS      1       ; multiplicador de 8 bits
RES_L:          DS      1       ; resultado de multiplicacion, byte bajo
RES_M:          DS      1       ; resultado, byte medio
RES_H:          DS      1       ; resultado, byte alto
MC_L:           DS      1       ; multiplicando desplazado, byte bajo
MC_H:           DS      1       ; multiplicando desplazado, byte alto
DELTA_L:        DS      1       ; X: cuentas-offset (entrada) / mg (salida)
DELTA_H:        DS      1       ; idem, byte alto
FLAGS:          DS      1       ; bit 0 = signo X; bits 2:1 = digito activo
T0_W_TEMP:      DS      1       ; contexto W de la ISR TIMER0
T0_STATUS_TEMP: DS      1       ; contexto STATUS de la ISR TIMER0

; Muestras/resultados del acelerometro. Todo acceso debe ir precedido de
; BANKSEL. DELTA y MUL/RES son workspace compartido, usado secuencialmente.
        PSECT   udata_bank0,class=BANK0
Y_L:            DS      1       ; eje Y, byte bajo del ADC
Y_H:            DS      1       ; eje Y, bits 9:8
X_MG_L:         DS      1       ; resultado X con signo, byte bajo (mg)
X_MG_H:         DS      1       ; resultado X con signo, byte alto (mg)
Y_MG_L:         DS      1       ; resultado Y con signo, byte bajo (mg)
Y_MG_H:         DS      1       ; resultado Y con signo, byte alto (mg)
Y_SIGN:         DS      1       ; bit 0 = signo de la conversion Y
Z_L:            DS      1       ; eje Z, byte bajo del ADC
Z_H:            DS      1       ; eje Z, bits 9:8
Z_MG_L:         DS      1       ; resultado Z con signo, byte bajo (mg)
Z_MG_H:         DS      1       ; resultado Z con signo, byte alto (mg)
Z_SIGN:         DS      1       ; bit 0 = signo temporal de la conversion Z
TEMP_C:         DS      1       ; temperatura en grados C (0..99)
PROD_H:         DS      1       ; reserva del multiplicador en mul16x8
T0_DIV:         DS      1       ; divisor por software para muestreo X/Y/Z
X_SAMPLE_FLAG:  DS      1       ; bit 0 = hay una muestra X/Y/Z pendiente

; EUSART y protocolo (Etapa 6). Todo en banco 0; el codigo hace BANKSEL.
TX_BUF:         DS      32      ; buffer circular de transmision
TX_HEAD:        DS      1       ; indice de escritura
TX_TAIL:        DS      1       ; indice de lectura
TX_CNT:         DS      1       ; bytes pendientes
RX_TYPE:        DS      1       ; tipo de la trama recibida
RX_D0:          DS      1       ; primer byte de datos
RX_D1:          DS      1       ; segundo byte de datos
RX_STATE:       DS      1       ; 0..4, sincronismo y recepcion
RX_LEN:         DS      1       ; LEN de la trama en curso
RX_IDX:         DS      1       ; indice dentro de la trama
CRC_REG:        DS      1       ; CRC8 parcial
CRC_CNT:        DS      1       ; contador de bits del CRC
TMP2:           DS      1       ; auxiliar del modulo
PERIOD_MS:      DS      1       ; periodo de DATA en ms
PERIOD_CNT:     DS      1       ; cuenta regresiva en ms
ALARM_TEMP:     DS      1       ; umbral de alarma en grados C
X_OFF_L:        DS      1       ; offset de X, byte bajo
X_OFF_H:        DS      1       ; offset de X, bits 9:8
MODO:           DS      1       ; bit 0 = streaming habilitado
SEQ:            DS      1       ; numero de trama DATA
TICK_FLAG:      DS      1       ; bandera de 1 ms puesta por el display
ALARM_STATE:    DS      1       ; bit 0 = alarma termica activa
ACK_CMD:        DS      1       ; comando respondido
ACK_RES:        DS      1       ; resultado de la respuesta

; Control temporal del patron sonoro (ver buzzer_service en alarmas.inc).
; El divisor baja la base de 1 ms a unidades de 10 ms.
BUZZ_DIV:       DS      1       ; ticks de 1 ms acumulados (0..BUZZ_DIVISOR-1)
BUZZ_CNT:       DS      1       ; unidades de 10 ms restantes de la fase
BUZZ_PHASE:     DS      1       ; 0 = fase apagada, 1 = fase encendida

;===============================================================================
; VECTOR DE RESET
;===============================================================================
; pic-as V4.00 empaqueta los PSECT de codigo desde el final de la pagina 0,
; por lo que el vector de reset debe ubicarse de forma absoluta en 0x0000.
        PSECT   resetVec,class=CODE,delta=2,abs
        ORG     0

resetVec:
        GOTO    main

; Vector unico de interrupcion. La ISR solo atiende TIMER0; guarda W y STATUS
; porque BANKSEL modifica RP1:RP0. Todas las instrucciones de servicio operan
; en banco 0, que es el banco estable del bucle principal.
        PSECT   interruptVec,class=CODE,delta=2,abs
        ORG     4

interruptVec:
        MOVWF   T0_W_TEMP
        SWAPF   STATUS,W
        MOVWF   T0_STATUS_TEMP

        BANKSEL INTCON
        BTFSS   INTCON,2        ; T0IF
        GOTO    t0_isr_restore
        BCF     INTCON,2        ; limpia T0IF

        BANKSEL TMR0
        MOVLW   TMR0_RELOAD
        MOVWF   TMR0

        BANKSEL T0_DIV
        DECF    T0_DIV,F
        BTFSS   STATUS,2        ; Z=1 cada 20 ticks
        GOTO    t0_isr_restore
        MOVLW   X_SAMPLE_TICKS
        MOVWF   T0_DIV
        BSF     X_SAMPLE_FLAG,0

t0_isr_restore:
        SWAPF   T0_STATUS_TEMP,W
        MOVWF   STATUS
        SWAPF   T0_W_TEMP,F
        SWAPF   T0_W_TEMP,W
        RETFIE

;===============================================================================
; PROGRAMA PRINCIPAL
;===============================================================================
        PSECT   code,class=CODE,delta=2

main:
        CALL    init
        CALL    display_init
        CALL    uart_init
        CALL    timer0_init

;===============================================================================
; BUCLE PRINCIPAL
;===============================================================================
; AN0 (LM35) se lee en cada vuelta. X/AN1, Y/AN5 y Z/AN6 se leen y convierten
; juntos cada 20 ms por evento de TIMER0. TIMER1 y EUSART se sondean por polling;
; la unica interrupcion habilitada es TIMER0.
; Resultados: TEMP_C = grados C; X/Y/Z_MG_H:L = aceleraciones con signo.
; El EUSART transmite temperatura, X/Y/Z y alarma cada PERIOD_MS (20 Hz por
; defecto) y atiende los comandos de la GUI sin bloquear el multiplexado.
loop:
        MOVLW   0               ; AN0 = LM35
        CALL    leer_adc
        CALL    convertir_temp
        CALL    procesar_alarma

        CALL    sample_xyz_if_due ; AN1/X + AN5/Y + AN6/Z: juntos cada 20 ms

        CALL    display_service
        CALL    buzzer_service  ; patron del buzzer: solo LEE TICK_FLAG,1
        CALL    uart_service    ; consume TICK_FLAG,0 para contar PERIOD_MS

        GOTO    loop

;===============================================================================
; SUBRUTINAS
;*******************************************************************************
; @brief Lee y convierte X, Y y Z cuando TIMER0 completa 20 ticks (20 ms).
; @details La ISR solo fija la bandera; ADC y conversiones se hacen en foreground.
;          Se enmascara GIE brevemente al consumir la bandera para no perder
;          una muestra que llegue justo durante el test/clear.
;*******************************************************************************
sample_xyz_if_due:
        BANKSEL INTCON
        BCF     INTCON,7        ; sección crítica de test-and-clear
        BANKSEL X_SAMPLE_FLAG
        BTFSS   X_SAMPLE_FLAG,0
        GOTO    sample_xyz_not_due
        BCF     X_SAMPLE_FLAG,0
        BANKSEL INTCON
        BSF     INTCON,7

        MOVLW   1               ; AN1 = X del MMA7361
        CALL    leer_adc
        CALL    convertir_x_mg
        ; X usa DELTA_H:L y FLAGS<0>. Guardar su resultado antes de reutilizar
        ; el workspace matematico para Y.
        BANKSEL X_MG_L
        MOVF    DELTA_L,W
        MOVWF   X_MG_L
        MOVF    DELTA_H,W
        MOVWF   X_MG_H

        MOVLW   5               ; AN5 = Y del MMA7361
        CALL    leer_adc
        BANKSEL Y_L
        MOVF    ADC_L,W
        MOVWF   Y_L
        MOVF    ADC_H,W
        MOVWF   Y_H
        CALL    convertir_y_mg

        MOVLW   6               ; AN6 = Z del MMA7361
        CALL    leer_adc
        BANKSEL Z_L
        MOVF    ADC_L,W
        MOVWF   Z_L
        MOVF    ADC_H,W
        MOVWF   Z_H
        CALL    convertir_z_mg
        RETURN

sample_xyz_not_due:
        BANKSEL INTCON
        BSF     INTCON,7
        RETURN

;===============================================================================
; Modulos separados

        #include "modules/display.inc"
        #include "modules/uart.inc"
        #include "modular/modules/init.inc"
        #include "modular/modules/timers.inc"
        #include "modular/modules/adc.inc"
        #include "modular/modules/matematicas.inc"
        #include "modular/modules/temperatura.inc"
        #include "modular/modules/acelerometro.inc"
        #include "modular/modules/alarmas.inc"

;===============================================================================
        END     resetVec
