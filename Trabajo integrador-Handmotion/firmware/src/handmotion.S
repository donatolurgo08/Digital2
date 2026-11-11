;===============================================================================
; @file       handmotion.S
;
; @author     Lurgo Donato
;
; @date       06/11/2026
;
; @brief      HAND MOTION - Etapas 2-4: ADC, alarma y displays.
;
; @details    PIC16F887 con oscilador interno a 8 MHz (OSCCON IRCF=111).
;             Configura el ADC a FOSC/32 (TAD = 4 us), lee el LM35 por AN0 y
;             los tres ejes del modulo MMA7361 por AN1 (X), AN5 (Y) y AN6 (Z),
;             sin amplificadores operacionales. Convierte la temperatura y la
;             aceleracion de X, controla la alarma termica y multiplexa tres
;             displays de anodo comun con TIMER1.
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
;               RD0-RD7  segmentos a,b,c,d,e,f,g,dp salidas
;               RB3/PGM, RB6/PGC, RB7/PGD           reservados a ICSP
;
;             Etapas 2-4: compiladas. NO probadas en hardware.
;             Sensor: MMA7361 en rango +-1,5 g, salidas directas al ADC y
;             referencia VREF = VDD. El offset de 0 g y la sensibilidad de X
;             son NOMINALES del datasheet; calibrar con la placa real antes
;             de usar DELTA para reconocimiento.
;             Displays rojos de anodo comun: segmentos activos bajos.
;             Q1-Q3 BC337 se proyectan como seguidores de emisor del lado
;             alto; verificar corriente y brillo antes de conectar todo.
;             R9-R16 = 150 ohm provisionales; R17-R19 = 330 ohm,
;             R21-R22 = 220 ohm y R23 = 10 kohm ya estan calculadas (nota
;             6.14 del netlist). LED1 se movio
;             de RA4 a RA2 porque RA4 es open-drain y no puede entregar corriente.
;             Pendiente de firmware: protocolo serie (T-03).
;             Pendiente de banco: polaridad electrica del terminal I/O del
;             buzzer; si es activo-bajo hay que invertir el nivel de RC3.
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
; Referencias para las etapas siguientes (todavia NO usadas en este archivo):
;   TIMER0  1:8 + recarga 6       -> 1 ms
;   EUSART  9600 Bd, BRGH=1       -> SPBRG = 51
        FOSC_KHZ        EQU     8000
        TCY_NS          EQU     500
        OSCCON_8MHZ     EQU     0x70

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

; Conversion de las cuentas ADC
;   LM35: 10 mV/C, VREF = 5 V -> 4,8828 mV/cuenta -> 0,48828 C/cuenta
;         T = cuentas * 125 / 256 (redondeado)
;   Eje X (MMA7361, rango +-1,5 g, modulo a 3,3 V):
;         0 g nominal -> VCC/2 = 1,65 V -> 338 cuentas (depende de VCC real)
;         800 mV/g -> 163,84 cuentas/g -> 6,103 mg/cuenta
;         mg = (cuentas - 338) * 49 / 8  (6,125 mg/cuenta, error 0,35 %)
;         Offset y sensibilidad NOMINALES: medir y recalibrar en banco.
        TEMP_MAX        EQU     99
        X_OFFSET_L      EQU     0x52    ; 338 = 0x0152
        X_OFFSET_H      EQU     0x01
        X_MG_NUM        EQU     49

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
; Los temporales W_TEMP/STATUS_TEMP se agregaran cuando exista ISR.
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
TEMP_C:         DS      1       ; temperatura en grados C (0..99)
PROD_H:         DS      1       ; reserva del multiplicador en mul16x8

; Muestras crudas de Y y Z. Quedan fuera de la RAM comun porque no hay
; espacio: todo acceso debe ir precedido de BANKSEL.
        PSECT   udata_bank0,class=BANK0
Y_L:            DS      1       ; eje Y, byte bajo del ADC
Y_H:            DS      1       ; eje Y, bits 9:8
Z_L:            DS      1       ; eje Z, byte bajo del ADC
Z_H:            DS      1       ; eje Z, bits 9:8

;===============================================================================
; VECTOR DE RESET
;===============================================================================
; pic-as V4.00 empaqueta los PSECT de codigo desde el final de la pagina 0,
; por lo que el vector de reset debe ubicarse de forma absoluta en 0x0000.
        PSECT   resetVec,class=CODE,delta=2,abs
        ORG     0

resetVec:
        GOTO    main

;===============================================================================
; PROGRAMA PRINCIPAL
;===============================================================================
        PSECT   code,class=CODE,delta=2

main:
        CALL    init
        CALL    display_init

;===============================================================================
; BUCLE PRINCIPAL
;===============================================================================
; Adquisicion continua de AN0 (LM35), AN1 (X), AN5 (Y) y AN6 (Z), alarma
; termica y servicio del display. TIMER1 se sondea por polling; las
; interrupciones permanecen deshabilitadas.
; Resultados: TEMP_C = grados C; DELTA_H:DELTA_L = mg de X con signo;
;             Y_H:Y_L y Z_H:Z_L = cuentas crudas de 10 bits.
loop:
        MOVLW   0               ; AN0 = LM35
        CALL    leer_adc
        CALL    convertir_temp
        CALL    procesar_alarma

        MOVLW   1               ; AN1 = X del MMA7361 (directo)
        CALL    leer_adc
        CALL    convertir_x_mg

        MOVLW   5               ; AN5 = Y del MMA7361 (directo)
        CALL    leer_adc
        BANKSEL Y_L
        MOVF    ADC_L,W
        MOVWF   Y_L
        MOVF    ADC_H,W
        MOVWF   Y_H

        MOVLW   6               ; AN6 = Z del MMA7361 (directo)
        CALL    leer_adc
        BANKSEL Z_L
        MOVF    ADC_L,W
        MOVWF   Z_L
        MOVF    ADC_H,W
        MOVWF   Z_H

        CALL    display_service

        GOTO    loop

;===============================================================================
; SUBRUTINAS
;===============================================================================
;*******************************************************************************
; @brief    Inicializa reloj, niveles de salida y direcciones de los puertos.
;
; @details  Orden de configuracion:
;             1. Reloj interno a 8 MHz y espera de estabilizacion (HTS).
;             2. Niveles inactivos en los latches de salida.
;             3. Direcciones (TRISx).
;             4. Entradas analogicas (ANSEL/ANSELH).
;             5. ADC a FOSC/32, referencia VDD/VSS y justificacion derecha.
;
;           Niveles inactivos elegidos:
;             - LED1 (RA2) y LED2 (RA5) apagados: nivel bajo.
;             - DIG1-DIG3 (RC0-RC2) en bajo: ningun display habilitado.
;             - BZ_CTRL (RC3) en bajo: buzzer apagado (confirmar polaridad).
;             - Segmentos (RD0-RD7) en alto: apagados (anodo comun).
;
; @param    ninguno
; @return   ninguno
; @modifica OSCCON, PORTA, PORTC, PORTD, TRISA-TRISE, ANSEL, ANSELH,
;           ADCON0, ADCON1, W
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
        CLRF    PORTC           ; digitos y buzzer apagados
        MOVLW   0xFF
        MOVWF   PORTD           ; segmentos activos bajos: todos apagados
        CLRF    FLAGS           ; signo X y estado del display iniciales

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
        MOVWF   ADCON1          ; ADFM=1, VCFG1:VCFG0=00 (VDD/VSS)
        BANKSEL ADCON0
        MOVLW   ADC_CTRL_BASE   ; ADON=1, ADCS=FOSC/32, CHS=AN0
        MOVWF   ADCON0

        RETURN

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
; @modifica COUNT, W
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
; @modifica W, ADCON0, ADC_L, ADC_H, TMP, COUNT
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

;*******************************************************************************
; @brief    Convierte las cuentas del LM35 a grados Celsius.
;
; @details  T = cuentas * 125 / 256, redondeado. Si el resultado supera
;           TEMP_MAX (99 C) se satura, porque el display de dos digitos no
;           muestra valores mayores. Si ADC_H != 0 la cuenta es >= 256, es
;           decir 125 C o mas, y tambien se satura.
;
; @param    ADC_H:ADC_L = cuentas del LM35
; @return   TEMP_C = temperatura en grados C (0..99)
; @modifica W, MUL_A, MUL_B, RES_L, RES_H, COUNT, TEMP_C
;*******************************************************************************
convertir_temp:
        MOVF    ADC_H,W
        BTFSS   STATUS,2
        GOTO    temp_sat
        MOVF    ADC_L,W
        MOVWF   MUL_A
        MOVLW   125
        MOVWF   MUL_B
        CALL    mul8x8
        MOVLW   128             ; redondeo: +0,5 cuenta de salida
        ADDWF   RES_L,F
        BTFSC   STATUS,0
        INCF    RES_H,F
        MOVF    RES_H,W
        SUBLW   TEMP_MAX
        BTFSS   STATUS,0        ; C = 0 -> RES_H > 99
        GOTO    temp_sat
        MOVF    RES_H,W
        MOVWF   TEMP_C
        RETURN
temp_sat:
        MOVLW   TEMP_MAX
        MOVWF   TEMP_C
        RETURN

;*******************************************************************************
; @brief    Actualiza las salidas de alarma segun la temperatura.
;
; @details  Si TEMP_C > TEMP_ALARM, activa LED1 (RA2), LED2 (RA5) y el
;           terminal de control del modulo buzzer (RC3). Con TEMP_C <= 40 C,
;           las tres salidas quedan en bajo. Se asume provisionalmente que
;           el modulo es activo-alto; confirmar en la prueba de banco.
;
; @param    TEMP_C = temperatura en grados C
; @return   ninguno
; @modifica PORTA<5,2>, PORTC<3>, W
;*******************************************************************************
procesar_alarma:
        MOVF    TEMP_C,W
        SUBLW   TEMP_ALARM     ; W = 40 - TEMP_C; C=1 si TEMP_C <= 40
        BTFSC   STATUS,0
        GOTO    alarma_off

alarma_on:
        BANKSEL PORTA
        BSF     PORTA,2        ; LED1, pin 4 / RA2
        BSF     PORTA,5        ; LED2, pin 7 / RA5
        BANKSEL PORTC
        BSF     PORTC,3        ; BZ_CTRL, pin 18 / RC3
        RETURN

alarma_off:
        BANKSEL PORTA
        BCF     PORTA,2
        BCF     PORTA,5
        BANKSEL PORTC
        BCF     PORTC,3
        RETURN

;*******************************************************************************
; @brief    Convierte las cuentas del eje X a miligramos con signo.
;
; @details  Resta el offset nominal de 0 g (338 cuentas para VCC = 3,3 V),
;           multiplica la magnitud por 49 y divide por 8. Resultado:
;           6,125 mg/cuenta. El offset y la sensibilidad son NOMINALES del
;           MMA7361 (+-1,5 g, 800 mV/g); se ajustan por calibracion con la
;           placa real.
;
; @param    ADC_H:ADC_L = cuentas del eje X
; @return   DELTA_H:DELTA_L = aceleracion en mg (complemento a dos, 16 bits)
; @modifica W, DELTA_L, DELTA_H, FLAGS, MUL_B, RES_L, RES_M, RES_H,
;           MC_L, MC_H, COUNT, TMP, PROD_H
;*******************************************************************************
convertir_x_mg:
        MOVF    ADC_L,W
        MOVWF   DELTA_L
        MOVF    ADC_H,W
        MOVWF   DELTA_H
        MOVLW   X_OFFSET_L
        SUBWF   DELTA_L,F
        MOVLW   X_OFFSET_H
        BTFSS   STATUS,0
        ADDLW   1
        SUBWF   DELTA_H,F
        BTFSC   STATUS,0
        GOTO    x_positivo
        COMF    DELTA_L,F
        COMF    DELTA_H,F
        INCF    DELTA_L,F
        BTFSC   STATUS,0
        INCF    DELTA_H,F
        BSF     FLAGS,0         ; signo negativo
        GOTO    x_magnitud
x_positivo:
        BCF     FLAGS,0
x_magnitud:
        MOVLW   X_MG_NUM
        MOVWF   MUL_B
        CALL    mul16x8
        ; divide por 8: tres desplazamientos a la derecha de 24 bits
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
        BTFSC   STATUS,0
        INCF    DELTA_H,F
        RETURN

;*******************************************************************************
; @brief    Multiplica dos valores de 8 bits sin signo.
;
; @details  Algoritmo de suma y desplazamiento. El producto maximo
;           255 * 255 = 65025 cabe en 16 bits.
;
; @param    MUL_A = multiplicando, MUL_B = multiplicador
; @return   RES_H:RES_L = producto de 16 bits
; @modifica MUL_B, RES_L, RES_H, MC_L, MC_H, COUNT, W
;*******************************************************************************
mul8x8:
        CLRF    RES_L
        CLRF    RES_H
        MOVF    MUL_A,W
        MOVWF   MC_L
        CLRF    MC_H
        MOVLW   8
        MOVWF   COUNT
mul8_loop:
        BTFSS   MUL_B,0
        GOTO    mul8_skip
        MOVF    MC_L,W
        ADDWF   RES_L,F
        MOVF    MC_H,W
        BTFSC   STATUS,0
        ADDLW   1
        ADDWF   RES_H,F
mul8_skip:
        BCF     STATUS,0
        RLF     MC_L,F
        RLF     MC_H,F
        BCF     STATUS,0
        RRF     MUL_B,F
        DECFSZ  COUNT,F
        GOTO    mul8_loop
        RETURN

;*******************************************************************************
; @brief    Multiplica un valor de 16 bits por otro de 8 bits.
;
; @details  Separa el multiplicando en dos bytes y reutiliza mul8x8. El mayor
;           caso de este proyecto es 685 * 49 = 33565, que entra en 16 bits,
;           pero se devuelve el producto completo de 24 bits.
;
; @param    DELTA_H:DELTA_L = multiplicando, MUL_B = multiplicador
; @return   RES_H:RES_M:RES_L = producto de 24 bits
; @modifica MUL_A, MUL_B, RES_L, RES_M, RES_H, MC_L, MC_H, COUNT,
;           TMP, PROD_H, W
;*******************************************************************************
mul16x8:
        MOVF    MUL_B,W
        MOVWF   PROD_H          ; guarda el multiplicador
        MOVF    DELTA_L,W
        MOVWF   MUL_A
        CALL    mul8x8
        MOVF    RES_L,W
        MOVWF   TMP             ; producto bajo P_L
        MOVF    RES_H,W
        MOVWF   RES_M           ; producto alto P_H
        MOVF    PROD_H,W
        MOVWF   MUL_B           ; restaura el multiplicador
        MOVF    DELTA_H,W
        MOVWF   MUL_A
        CALL    mul8x8
        MOVF    RES_L,W
        ADDWF   RES_M,F         ; medio = P_H + Q_L
        BTFSC   STATUS,0
        INCF    RES_H,F         ; acarreo al byte alto
        MOVF    TMP,W
        MOVWF   RES_L           ; bajo = P_L
        RETURN

;===============================================================================
; Modulo separado: multiplexado de los displays (Etapa 4).
        #include "modules/display.inc"

;===============================================================================
        END     resetVec
