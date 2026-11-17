;===============================================================================
; Trabajo Integrador: HAND MOTION
; Universidad Nacional de Cordoba
; Facultad de Ciencias Exactas, Fisicas y Naturales
; Asignatura: Electronica Digital II
; Autores:
;   - Conde Ana Victoria
;   - Lurgo Donato
;
; Fecha: 17/11/2026
; Microcontrolador: PIC16F887
; Archivo: handmotion_work.S
;
; Descripcion:
;   Programa principal del sistema HAND MOTION. Adquiere temperatura y
;   aceleracion en los ejes X, Y y Z, procesa la alarma, actualiza los
;   displays y gestiona la comunicacion serie con la interfaz grafica.
;
; Hardware:
;   LM35 en AN0 y MMA7361 en AN1, AN5 y AN6.
;   Displays de tres digitos, indicadores LED y buzzer.
;   Comunicacion EUSART a 9600 Bd.
;
; Muestreo de X, Y y Z cada 20 ms mediante TIMER0.
; Los parametros de conversion de Z permanecen provisionales.
;===============================================================================

;===============================================================================
; DIRECTIVAS DE INCLUSION
;===============================================================================
        PROCESSOR 16F887
        #include <xc.inc>

;===============================================================================
; CONFIGURACION GENERAL DEL MCU
;===============================================================================
; Configura el oscilador interno y los bits de funcionamiento del PIC16F887.
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
; Configuracion del reloj interno a 8 MHz. TCY = 0,5 us.
;   FOSC = 8 MHz            -> TCY = 4 / FOSC = 0,5 us
;   OSCCON = 0111 0000b     -> IRCF<2:0> = 111 (8 MHz), SCS = 00 (INTOSC)
;
; Temporizacion confirmada para esta etapa:
;   TIMER0  FOSC/4, prescaler 1:8, precarga 6 -> 1 ms nominal
;   Muestreo de X cada 20 ticks                 -> 20 ms / 50 Hz
; Configuracion EUSART a 9600 Bd, formato 8N1.
        FOSC_KHZ        EQU     8000
        TCY_NS          EQU     500
        OSCCON_8MHZ     EQU     0x70

; EUSART: 8 MHz / (16 * (51 + 1)) = 9615 Bd, error +0,16 % sobre 9600.
;   TXSTA = 0010 0100b -> TXEN = 1, BRGH = 1, SYNC = 0
;   RCSTA = 1001 0000b -> SPEN = 1, CREN = 1
        EUSART_SPBRG    EQU     51
        EUSART_TXSTA    EQU     0x24
        EUSART_RCSTA    EQU     0x90

; Parametros del protocolo de comunicacion HAND MOTION.
        PROTO_SYNC1     EQU     0xAA
        PROTO_SYNC2     EQU     0x55
        PROTO_VERSION   EQU     3
        PROTO_CRC_POLY  EQU     0x07
        PROTO_PERIOD    EQU     50      ; 50 ms = 20 Hz por defecto
        PROTO_PERIOD_MIN EQU    20      ; 50 Hz
        PROTO_PERIOD_MAX EQU    250     ; 4 Hz
; TIMER0 genera una interrupcion nominal cada 1 ms.
; Cada 20 interrupciones solicita una nueva muestra de los tres ejes.
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

; Configuracion del ADC con FOSC/32, resultado justificado a la derecha
; y referencias VDD/VSS.
        ADC_ADCON1_INIT EQU     0x80
        ADC_CTRL_BASE   EQU     0x81    ; ADON + ADCS = FOSC/32
        ADC_ACQ_LOOPS   EQU     14      ; ~23 us a 8 MHz
        ADC_GO          EQU     1       ; bit GO/DONE de ADCON0

; TIMER1 utiliza el reloj interno para generar una base nominal de 1 ms.
        TMR1_RELOAD_H   EQU     0xF8
        TMR1_RELOAD_L   EQU     0x30

; Umbral de temperatura para activar la alarma.
        TEMP_ALARM     EQU     40

; Patron sonoro: 200 ms encendido y 800 ms apagado.
; La frecuencia del buzzer la genera el oscilador interno del modulo.
        BUZZ_DIVISOR   EQU     10      ; ticks de 1 ms por unidad de 10 ms
        BUZZ_ON_UNITS  EQU     20      ; 20 x 10 ms = 200 ms encendido
        BUZZ_OFF_UNITS EQU     80      ; 80 x 10 ms = 800 ms apagado

; Conversion de las cuentas ADC:
; LM35: 10 mV/C. La temperatura se calcula como cuentas * 125 / 256.
; MMA7361: rango +-1,5 g y sensibilidad nominal de 800 mV/g.
; La aceleracion se calcula como (cuentas - offset) * 49 / 8.
; Los parametros de Z son provisionales y requieren calibracion fisica.
        TEMP_MAX        EQU     99
        X_OFFSET_L      EQU     0x52    ; 338 = 0x0152
        X_OFFSET_H      EQU     0x01
        Y_OFFSET_L      EQU     0x52    ; nominal 338 = 0x0152
        Y_OFFSET_H      EQU     0x01
        Z_OFFSET_L      EQU     0x52    ; PROVISIONAL: 338, pendiente de calibracion
        Z_OFFSET_H      EQU     0x01
        X_MG_NUM        EQU     49
        Z_MG_NUM        EQU     49      ; PROVISIONAL: factor 49/8, pendiente de calibracion

; Canales analogicos habilitados: AN0, AN1, AN5 y AN6.
        ANSEL_INIT      EQU     0x63

; Configuracion de direccion de los puertos para la Rev E.
        TRISA_INIT      EQU     0xDB    ; RA2/RA5 salidas; RA4 y resto entradas
        TRISB_INIT      EQU     0xFF    ; todo entrada (ICSP incluido)
        TRISC_INIT      EQU     0xB0    ; RC0-RC3 y RC6 salidas
        TRISD_INIT      EQU     0x00    ; RD0-RD7 salidas (segmentos)
        TRISE_INIT      EQU     0x0F    ; RE0-RE3 entradas

;===============================================================================
; DEFINICION DE VARIABLES
;===============================================================================
; Variables de trabajo ubicadas en RAM comun.
; La rutina de interrupcion utiliza este espacio para guardar el contexto.
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

; Muestras y resultados de los ejes X, Y y Z.
; Las rutinas matematicas utilizan un espacio de trabajo compartido.
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

; Variables utilizadas por la comunicacion EUSART y el protocolo.
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

; Variables de control temporal del buzzer.
BUZZ_DIV:       DS      1       ; ticks de 1 ms acumulados (0..BUZZ_DIVISOR-1)
BUZZ_CNT:       DS      1       ; unidades de 10 ms restantes de la fase
BUZZ_PHASE:     DS      1       ; 0 = fase apagada, 1 = fase encendida

;===============================================================================
; VECTOR DE RESET
;===============================================================================
; Ubica el punto de entrada del programa en la direccion 0x0000.
        PSECT   resetVec,class=CODE,delta=2,abs
        ORG     0

resetVec:
        GOTO    main
;===============================================================================
; VECTOR DE INTERRUPCION
;===============================================================================
; Atiende TIMER0, guarda W y STATUS, actualiza la bandera de muestreo
; y restaura el contexto del procesador.
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
; Inicializa los modulos y perifericos del sistema.
        PSECT   code,class=CODE,delta=2

main:
        CALL    init
        CALL    display_init
        CALL    uart_init
        CALL    timer0_init

;===============================================================================
; BUCLE PRINCIPAL
;===============================================================================
; En cada iteracion:
;   1. Lee la temperatura mediante AN0.
;   2. Convierte el valor y procesa la alarma.
;   3. Adquiere X, Y y Z cuando corresponde.
;   4. Actualiza los displays.
;   5. Gestiona el buzzer.
;   6. Atiende la comunicacion UART.
;
; TIMER0 solicita una muestra cada 20 ms.
; Las lecturas y conversiones se realizan fuera de la interrupcion.
;===============================================================================
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
;===============================================================================
; @brief Adquiere y convierte los tres ejes del acelerometro.
;
; @details Comprueba la bandera generada por TIMER0. Cuando hay una
;          muestra pendiente, lee AN1, AN5 y AN6 y ejecuta las rutinas
;          de conversion correspondientes.
;
;          Deshabilita brevemente las interrupciones para consumir
;          la bandera sin perder una nueva solicitud de muestreo.
;
; @param Ninguno.
; @return Resultados X, Y y Z expresados en miligravedades (mg).
;===============================================================================
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
        ; Guarda el resultado de X antes de reutilizar las variables de trabajo.
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
