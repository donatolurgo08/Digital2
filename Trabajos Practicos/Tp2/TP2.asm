;===============================================================================; @file       G6_TPL2_ED2.asm
;
; @author     Conde_Ana_Victoria
;	      Lauc_Mirko_Gaston
;             Bertalot_Gomez_Renata
;             Lurgo_Donato_Agustin
;             Goicoechea_Emilia
;
;
; @date       31/8/2026
;
; @version    1.0
;===============================================================================

;===============================================================================
; DIRECTIVAS DE INCLUSION
;===============================================================================
LIST P=16F887
        #include "p16f887.inc"

;===============================================================================
; CONFIGURACION GENERAL DEL MCU
;===============================================================================
        __CONFIG _CONFIG1, _XT_OSC & _WDTE_OFF & _MCLRE_ON & _LVP_OFF

;===============================================================================
; DEFINICION DE CONSTANTES
;===============================================================================
#DEFINE SW1   PORTE,    RE0     ; Pulsador conectado a RE0
#DEFINE BUZZ  PORTC,    RC0     ; Buzzer activo conectado a RC0 (Alarma auditiva)
#DEFINE LED0  PORTD,    RD0     ; Leds conectados al Puerto D (Alarmas visuales)
#DEFINE LED1  PORTD,    RD1
#DEFINE LED2  PORTD,    RD2
#DEFINE LED3  PORTD,    RD3
#DEFINE LED4  PORTD,    RD4
#DEFINE LED5  PORTD,    RD5
#DEFINE LED6  PORTD,    RD6
#DEFINE LED7  PORTD,    RD7
;===============================================================================
; DEFINICION DE VARIABLES
;===============================================================================
CBLOCK 0x20
         DELAY1_Init
         DELAY2_Init
         DELAY3_Init
         DELAY1
         DELAY2
         DELAY3
         COUNTER_LED
         COUNTER_SECUENCES
ENDC
;===============================================================================
; DECLARACION DE MACROS PARA CONFIGURACION DE REGISTROS
;===============================================================================
CFG_SWITCH MACRO
        BSF     STATUS, RP0
        BSF     STATUS, RP1     ; Acceso al Banco 3
        BCF     ANSEL,  5       ; Limpia el bit 5 de ANSEL
        BCF     STATUS, RP1     ; Acceso al Banco 1
        BSF     TRISE,  TRISE0  ; Configura RE0 como entrada
        BCF     STATUS, RP0     ; Retorno al Banco 0

ENDM
;_______________________________________________________________________________
CFG_LEDS MACRO
        BSF     STATUS, RP0     ; Acceso al Banco 1
        BCF     STATUS, RP1
        CLRF    TRISD           ; Configura todo el Puerto D como salidas
        BCF     STATUS, RP0     ; Retorno al Banco 0
        CLRF    PORTD           ; Asegura que todos los LEDs incien apagados

ENDM
;_______________________________________________________________________________
LEDS_ON MACRO
        MOVLW   b'11111111'
        MOVWF   PORTD
ENDM
;-------------------------------------------------------------------------------
LEDS_OFF MACRO
        CLRF    PORTD
ENDM
;-------------------------------------------------------------------------------
LEDS_RLF MACRO
        RLF     PORTD,  F       ; Rota los bits del Puerto D a la derecha
;                                 a través del carry
ENDM
;-------------------------------------------------------------------------------
LEDS_RRF MACRO
        RRF     PORTD,  F       ; Rota los bits del Puerto D a la izquierda
;                                 a través del carry
ENDM
;_______________________________________________________________________________
CFG_BUZZER MACRO
        BSF     STATUS, RP0     ; Acceso al Banco 1
        BCF     STATUS, RP1

        BCF     TRISC, TRISC0   ; Configura RC0 como salida

        BCF     STATUS, RP0     ; Retorno al Banco 0
        BCF     STATUS, RP1
ENDM
;_______________________________________________________________________________
BUZZER_ON MACRO
        BSF     PORTC,  RC0     ; Envía 5V al buzzer
ENDM
;-------------------------------------------------------------------------------
BUZZER_OFF MACRO
        BCF     PORTC,  RC0     ; Corta la señal al buzzer
ENDM
;_______________________________________________________________________________
;
CFG_SECUENCES MACRO
        MOVLW   D'3'
        MOVWF   COUNTER_SECUENCES
ENDM
;_______________________________________________________________________________
;
;*******************************************************************************
; Macros de Delays
; tDELAY [us] = 3pnm + 4nm + 4m + 5 ---> p = delay1, n = delay2 y m = delay3
;*******************************************************************************
;_______________________________________________________________________________
CFG_DELAY_100ms MACRO
        MOVLW   D'1'
        MOVWF   DELAY1_Init
        MOVLW   D'198'
        MOVWF   DELAY2_Init
        MOVLW   D'167'
        MOVWF   DELAY3_Init
        ENDM
;-------------------------------------------------------------------------------
CFG_DELAY_200ms MACRO
        MOVLW   D'5'
        MOVWF   DELAY1_Init
        MOVLW   D'95'
        MOVWF   DELAY2_Init
        MOVLW   D'139'
        MOVWF   DELAY3_Init
        ENDM
;-------------------------------------------------------------------------------
CFG_DELAY_300ms MACRO
        MOVLW   D'5'
        MOVWF   DELAY1_Init
        MOVLW   D'169'
        MOVWF   DELAY2_Init
        MOVLW   D'117'
        MOVWF   DELAY3_Init
        ENDM
;-------------------------------------------------------------------------------
CFG_DELAY_1s MACRO
        MOVLW   D'46'
        MOVWF   DELAY1_Init
        MOVLW   D'189'
        MOVWF   DELAY2_Init
        MOVLW   D'37'
        MOVWF   DELAY3_Init
        ENDM
;===============================================================================
; INICIALIZACION DEL MCU (CODIGO ABSOLUTO)
;===============================================================================

        ORG     0x00	        ; Vector de Reset
        GOTO    INICIO	        ; Salto al inicio del programa principal
        ORG     0x05	        ; Ubicacion Programa Principal en la memoria
;                               de programa
;
;===============================================================================
; INICIALIZACION DE MACROS PARA CONFIGURACION DE REGISTROS
;===============================================================================
INICIO
                                ;-----Inicializacion de Macros-------
;
        CFG_SWITCH              ; Configura el pin del pulsador
        CFG_LEDS                ; Configura el puerto de los LEDs
        CFG_SECUENCES           ; Carga el contador de repeticiones
        CFG_BUZZER              ; Configura el pin del buzzer
        BUZZER_OFF              ; Garantiza que el buzzer incie desactivado
;
;===============================================================================
; INICIO PROGRAMA PRINCIPAL
;===============================================================================
MAIN_LOOP

        CALL    TEST_LEDS       ; Parpadeo constante
        BTFSC   SW1             ; El pin RE0 está en presionado (en 0)?
        GOTO    MAIN_LOOP       ; NO -> El pin lee 1, se repite TEST_LEDS
        CALL    SECUENCES       ; SI -> Entra a la secuencias de alarma acústica y visual
        GOTO    MAIN_LOOP       ; Reinicia el ciclo principal
;
;===============================================================================
; SUBRUTINAS
;===============================================================================
;
;*******************************************************************************
; @brief    Genera un retardo mediante tres bucles anidados.
;
; @details  Utiliza DELAY1_Init, DELAY2_Init y DELAY3_Init como
;           valores iniciales y DELAY1, DELAY2 y DELAY3 como contadores.
;*******************************************************************************
;
DELAY_3LOOP
        MOVF    DELAY1_Init, W  ; Copia el valor inicial del contador 1 a W
        MOVWF   DELAY1          ; Inicia el contador 1

LOOP1
        MOVF    DELAY2_Init, W  ; Copia el valor inicial del contador 2 a W
        MOVWF   DELAY2          ; Inicia el contador 2

LOOP2
        MOVF    DELAY3_Init, W  ; Copia el valor inicial del contador 3 a W
        MOVWF   DELAY3          ; Inicia el contador 3

LOOP3
        DECFSZ  DELAY3, F       ; Decrementa el contador 3
        GOTO    LOOP3           ; Repite hasta que DELAY3 llegue a 0
        DECFSZ  DELAY2, F       ; Decrementa el contador 2
        GOTO    LOOP2           ; Vuelve a cargar DELAY3 y repetir
        DECFSZ  DELAY1, F       ; Decrementa el contador 1
        GOTO    LOOP1           ; Vuelve a cargar DELAY2 y DELAY3
RETURN                          ; Termina el delay y vuelve al CALL
;
;*******************************************************************************
; @brief    Testeo de hardware para los 8 LEDs
;
; @details  Ejecuta un parpadeo sincronizado para los 8 LEDs, cumpliendo un
;           cumpliendo el periodo de itermitencia de 2 segundos.
;*******************************************************************************
;
TEST_LEDS
        CFG_DELAY_1s
        LEDS_ON
        CALL    DELAY_3LOOP
        LEDS_OFF
        CALL    DELAY_3LOOP
RETURN
;

;*******************************************************************************
; @brief    Alarma acustica  inicial
;
; @details  Enciende el buzzer conectado a RC0, ejecutando una demora de 200ms
;           y luego se apaga.
;*******************************************************************************
;
BUZZER_BIP
        BUZZER_ON               ; Macro que enciende el puerto RC0
        CFG_DELAY_200ms
        CALL    DELAY_3LOOP
        BUZZER_OFF              ; Macro que apaga el puerto RC0
RETURN
;
;*******************************************************************************
; @brief    Administacion de las diferentes secuencias de luces
;
; @details  Agrupa y ejecuta de forma secuencias la alarma acustica inicial
;           y los tres efectos visuales (Running, Bidir-Running, Crawling,
;           Forward y Backward) requeridos al presonar el pulsador.
;*******************************************************************************
;
SECUENCES
        CALL    BUZZER_BIP
        CALL    RUNNING_LIGHT
        CALL    BIDIR_RUNNING_LIGHT
        CALL    CRAWLING
RETURN
;
;*******************************************************************************
; @brief    Efecto de barrido (Running_Light)
;
; @details  ejecuta el barrido hacia la derecha (Forward_Led), repitiendo
;           la secuencia tres veces (Counter_secuences) con una intermitencia de 300ms.
;*******************************************************************************
;
RUNNING_LIGHT
        CFG_DELAY_300ms
        LEDS_OFF
LOOP_RL
        CALL    FORWARD_LED
        DECFSZ  COUNTER_SECUENCES, F ; Resta 1 al contador y evalúa si llegó a 0
        GOTO    LOOP_RL              ; NO -> se repite el barrido
        CFG_SECUENCES                ; SI -> el contador llego a 0, es decir, se repitió 3 veces
RETURN
;
;*******************************************************************************
; @brief    Efecto de barrido bidereccional (Bidir_Running_Light)
;
; @details  ejecuta el barrido hacia la derecha (Forward_Led),despues hacia la
;           izquierda(Backward_Led),  repitiendo la secuencia
;           tres veces (Counter_secuences) con una intermitencia de 200ms.
;*******************************************************************************
;
BIDIR_RUNNING_LIGHT
        CFG_DELAY_200ms
        LEDS_OFF
LOOP_BRL
        CALL    FORWARD_LED
        CALL    BACKWARD_LED
        DECFSZ    COUNTER_SECUENCES, F
        GOTO    LOOP_BRL
        CFG_SECUENCES
RETURN
;
;*******************************************************************************
; @brief    Efecto de arrastre(Crawling)
;
; @details  Ejecuta el encendido (Progressive_Led_On) y apagado (Progressive_Led_Off)
;           de los leds, repitiendo la secuencia tres veces (Counter_Secuences),
;           con una intermitencia de 100ms.
;*******************************************************************************
;
CRAWLING
        CFG_DELAY_100ms
        LEDS_OFF
LOOP_CW
        CALL    PROGRESSIVE_LED_ON
        CALL    PROGRESSIVE_LED_OFF
        DECFSZ    COUNTER_SECUENCES, F
        GOTO    LOOP_CW
        CFG_SECUENCES
RETURN
;
;*******************************************************************************
; @brief    Barrido hacia la derecha (Forward_Led)
;
; @details  Enciende los leds de forma progresiva de LED0 a LED7, generando el
;           efecto de barrido hacia la derecha.
;
;*******************************************************************************
;
FORWARD_LED
        BSF     STATUS, C       ; Setea el carry en 1 para ingresar el primer LED
FW_LOOP
       LEDS_RLF                 ; Desplaza el led encendido una posición a la derecha (LED0->LED1...)
       CALL     DELAY_3LOOP
       BTFSS LED7               ; LED7 = ON?
       GOTO     FW_LOOP         ; NO -> Sigue desplazando
       RETURN                   ; SI -> Finaliza
;
;*******************************************************************************
; @brief    Desplazamiento hacia la derecha (Backward).
;
; @details  Desplaza un único LED encendido desde la posición actual hacia
;           la derecha (hacia LED0) utilizando la instrucción RRF. Finaliza
;           cuando el LED0 se enciende.
;*******************************************************************************
BACKWARD_LED
        BCF     STATUS, C       ; CLR FLAG C: Limpia el acarreo para no ingresar '1's extra
BW_LOOP
        LEDS_RRF                ; Desplaza a la derecha (PORTD, F)
        CALL    DELAY_3LOOP     ; Ejecuta la demora para visualizar el salto
        BTFSS   PORTD,  0       ; LED0 = ON? (Verifica si el '1' llegó al final)
        GOTO    BW_LOOP         ; NO -> Sigue desplazando
RETURN                          ; SI -> FIN
;
;*******************************************************************************
; @brief    Encendido progresivo de los LEDs (Crawling ON).
;
; @details  Enciende los LEDs secuencialmente ingresando unos lógicos desde
;           LED0 hacia LED7, manteniendo encendidos los anteriores hasta
;           completar todo el puerto.
;*******************************************************************************
;
PROGRESSIVE_LED_ON
        BCF     STATUS, C       ; Carry limpio
PROG_ON_LOOP
        BSF     STATUS, C       ; Forzamos un '1' en el carry
        LEDS_RLF
        CALL    DELAY_3LOOP     ; Espera para visualizar el salto
        BTFSS   PORTD,  7       ; Se encendio el ultimo led?
        GOTO    PROG_ON_LOOP    ; NO -> repite el ciclo
RETURN                          ; SI -> FIN
;
;*******************************************************************************
; @brief    Apagado progresivo de los 8 LEDs
;
; @details  Apaga los LEDs secuencialmente ingrsando ceros lógicos desde LED0
;           hacia LED7
;*******************************************************************************
;
PROGRESSIVE_LED_OFF
PROG_OFF_LOOP
        BCF     STATUS, C       ; Forzamos un '0' en el carry para ir vaciando
        LEDS_RLF
        CALL    DELAY_3LOOP     ; Espera para visualizar el salto
        MOVF    PORTD,  F       ; Se mueve PORTD sobre sí mismo para actualizar el FLAG Z
        BTFSS   STATUS, Z       ; El puerto D quedó en 0?
        GOTO    PROG_OFF_LOOP   ; NO -> repite el ciclo
RETURN                          ; SI -> FIN

;===============================================================================
    END
;===============================================================================
