;==============VERSION PRRELIMINAR EDITAR ACA ESTO NO VA A ENTREGA FINAL=====================================================
; @file       G6_TPL2_ED2.asm
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
#DEFINE SW1   PORTE,RE0
#DEFINE BUZZ  PORTC,RC0
#DEFINE LED0  PORTD,RD0
#DEFINE LED1  PORTD,RD1
#DEFINE LED2  PORTD,RD2
#DEFINE LED3  PORTD,RD3
#DEFINE LED4  PORTD,RD4
#DEFINE LED5  PORTD,RD5
#DEFINE LED6  PORTD,RD6
#DEFINE LED7  PORTD,RD7
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
        BSF     STATUS,RP0   ;Switch presionado
        BSF     STATUS,RP1   ; pasamos al banco 3 para configurar ansel
        BCF     ANSEL,5
        BCF     STATUS,RP1   ;ver q onda lo de los bancos
        BSF     TRISE,TRISE0 ;esto setea el pin RE0 como entrada
        BCF     STATUS,RP0   ;retorno de banco 0

ENDM
;________________________________esto separa macros distintas pero dentro del bloque macro mamá________________________________________________
CFG_LEDS MACRO
        BSF     STATUS,RP0   ;Chequear estos puertos q no se q es
        BCF     STATUS,RP1
        CLRF    TRISD
        BCF     STATUS,RP0
        CLRF    PORTD        ; creo q aca chequeamos si el led pasa corriente, a estudiaar

ENDM
;________________________________________________________________________________
;------------------------estos guiones indican macros de la misma familia------------------------------------
LEDS_ON MACRO
        MOVLW  b'11111111'   ;Chequear esto esta raaaro
        MOVWF   PORTD
ENDM
;-------------------------------------------------------------------------------
LEDS_OFF MACRO
        CLRF   PORTD         ;aca se apagan todos los puertos
ENDM
;-------------------------------------------------------------------------------
LEDS_RLF MACRO
        RLF    PORTD,F       ;aca hacemos el desp a la izquirda de los leds, todos por eso se declara l puerto d
ENDM
;-------------------------------------------------------------------------------
LEDS_RRF MACRO
        RRF    PORTD,F       ;mover todo a la derecha ->
ENDM
;_______________________________________________________________________________
CFG_BUZZER MACRO
        BSF     STATUS,RP0          ; Banco 1
        BCF     STATUS,RP1          ; revisar esto ta raaaaaaro

        BCF     TRISC,TRISC0        ; RC0 como salida

        BCF     STATUS,RP0          ; Banco 0
        BCF     STATUS,RP1

        BCF     PORTC,RC0           ; Buzzer inicialmente apagado
ENDM
;_______________________________________________________________________________
BUZZER_ON MACRO
        BSF     PORTC,RC0
ENDM
;-------------------------------------------------------------------------------
BUZZER_OFF MACRO
        BCF    PORTC
ENDM
;*******************************************************************************
; formula para calcular los tiempor para cada delay
;tDELAY = 4/fCLK [3pnm]+[4nm]+[4m]+5 donde p=delay1,n=delay2 y m=delay3
;como trabajamos con un CRISTAL DE 4MZ nos queda:
;                                                   tDELAY [us] = 3pnm + 4nm + 4m + 5
;*******************************************************************************
;_______________________________________________________________________________
CFG_DELAY_100ms MACRO
        MOVLW D'1'
        MOVWF DELAY1_Init
        MOVLW D'198'
        MOVWF DELAY2_Init
        MOVLW D'167'
        MOVWF DELAY3_Init
;-------------------------------------------------------------------------------
CFG_DELAY_200ms MACRO
        MOVLW D'5'
        MOVWF DELAY1_Init
        MOVLW D'95'
        MOVWF DELAY2_Init
        MOVLW D'139'
        MOVWF DELAY3_Init
;-------------------------------------------------------------------------------
CFG_DELAY_300ms MACRO
        MOVLW D'5'
        MOVWF DELAY1_Init
        MOVLW D'169'
        MOVWF DELAY2_Init
        MOVLW D'117'
        MOVWF DELAY3_Init
;-------------------------------------------------------------------------------
CFG_DELAY_1s MACRO
        MOVLW D'46'     ; m = 46
        MOVWF DELAY1_Init
        MOVLW D'189'    ;n = 149
        MOVWF DELAY2_Init
        MOVLW D'37'     ; p = 37 y este bloque se repite asi con el resto de los delays
        MOVWF DELAY3_Init   ; calculamos siempre con la formula de arriba
;_______________________________________________________________________________
CFG_SECUENCES MACRO
        MOVLW D'3'
        MOVWF COUNTER_SECUENCES
ENDM
;===============================================================================
; INICIALIZACION DEL MCU (CODIGO ABSOLUTO)
;===============================================================================
    ORG     0x00	;Vector de Reset
    GOTO    INICIO	;Salto al inicio del programa principal
    ORG     0x05	;Ubicacion Programa Principal en la memoria
			;de programa

;===============================================================================
; INICIALIZACION DE MACROS PARA CONFIGURACION DE REGISTROS
;===============================================================================
INICIO	    ;-----Inicializacion de Macros-------
        CFG_SWITCH
        ;↑ configura el pin del pulsador
        CFG_LEDS
        ;↑ Configura el puerto de los LEDs
        CFG_SECUENCES
        ;↑ Carga el contador de repeticiones en 3
        CFG_BUZZER
        ;↑ Configura el pin del buzzer
        BUZZER_OFF
        ;↑ Garantice que el buzzer incie desactivado

;===============================================================================
; INICIO PROGRAMA PRINCIPAL
;===============================================================================
MAIN_LOOP
        CALL    TEST_LEDS
        ;**** preguntamos si el switch esta presionado o no ****
        BTFSC   SW1
    GOTO    MAIN_LOOP
        ;*** Si se skipeo la linea 185, llamamos a las secuencias
        ;segun el diagrama de flujo
        CALL    CFG_SECUENCES
    GOTO    MAIN_LOOP
;===============================================================================
; SUBRUTINAS
;===============================================================================
;*******************************************************************************
; @brief    Genera un retardo mediante tres bucles anidados.
;
; @details  Utiliza DELAY1_Init, DELAY2_Init y DELAY3_Init como
;           valores iniciales y DELAY1, DELAY2 y DELAY3 como contadores.
;*******************************************************************************

DELAY_3LOOP
    MOVF    DELAY1_Init,W       ; Copia el valor inicial del contador 1 a W
    MOVWF   DELAY1              ; Inicia el contador 1

LOOP1
    MOVF    DELAY2_Init,W       ; Copia el valor inicial del contador 2 a W
    MOVWF   DELAY2              ; Inicia el contador 2

LOOP2
    MOVF    DELAY3_Init,W       ; Copia el valor inicial del contador 3 a W
    MOVWF   DELAY3              ; Inicia el contador 3

LOOP3
    DECFSZ  DELAY3,F            ; Decrementa el contador 3
    GOTO    LOOP3               ; Repite hasta que DELAY3 llegue a 0

    DECFSZ  DELAY2,F            ; Decrementa el contador 2
    GOTO    LOOP2               ; Vuelve a cargar DELAY3 y repetir

    DECFSZ  DELAY1,F            ; Decrementa el contador 1
    GOTO    LOOP1               ; Vuelve a cargar DELAY2 y DELAY3

    RETURN                      ; Termina el delay y vuelve al CALL
;*******************************************************************************
; @brief    Testeo de hardware para los 8 LEDs
;
; @details  Ejecuta un parpadeo sincronizado para los 8 LEDs, cumpliendo un
;           cumpliendo el periodo de itermitencia de 2 segundos.
;*******************************************************************************
TEST_LEDS
        CFG_DELAY_1s
        LEDS_ON
        CALL    DELAY_3LOOP
        LEDS_OFF
        CALL    DELAY_3LOOP
RETURN
;*******************************************************************************
; @brief    Administacion de las diferentes secuencias de luces
;
; @details  Agrupa y ejecuta de forma secuencias la alarma acustica inicial
;           y los tres efectos visuales (Running, Bidir-Running, Crawling,
;           Forward y Backward) requeridos al presonar el pulsador.
;
;*******************************************************************************
        CALL    BUZZER_BIP
        CALL    RUNNING_LIGHT
        CALL    BIDIR_RUNNING_LIGHT
        CALL    CRAWLING
RETURN
;*******************************************************************************
; @brief    Alarma acustica  inicial
;
; @details  Enciende el buzzer conectado a RC0, ejecutando una demora de 200ms
;           y luego se apaga.
;*******************************************************************************
BUZZER_ON
        CFG_DELAY_200ms
        CALL    DELAY_3LOOP
        BUZZER_OFF
RETURN

;*******************************************************************************
; @brief    Efecto de barrido (Running_Light)
;
; @details  ejecuta el barrido hacia la derecha (Forward_Led), repitiendo la secuencia
;           tres veces (Counter_secuences) con una intermitencia de 300ms.
;*******************************************************************************
RUNNING_LIGHT
        CFG_DELAY_300ms
        LEDS_OFF
LOOP_RL
        CALL    FORWARD_LED
        DECF    COUNTER_SECUENCES, F ; resta uno al contador de repeticiones
        BTFSS   STATUS,Z  ; FLAG seteado(igual a 1)?
        GOTO    LOOP_RL ; NO -> se repite el barrido
        CFG_SECUENCES
        ; SI -> el contador llego a 0, es decir, se repitió 3 veces

RETURN

;*******************************************************************************
; @brief    Efecto de barrido bidereccional (Bidir_Running_Light)
;
; @details  ejecuta el barrido hacia la derecha (Forward_Led),despues hacia la
;           izquierda(Backward_Led),  repitiendo la secuencia
;           tres veces (Counter_secuences) con una intermitencia de 200ms.
;*******************************************************************************
BIDIR_RUNNING_LIGHT
        CFG_DELAY_200ms
        LEDS_OFF
LOOP_BRL
        CALL    FORWARD_LED
        CALL    BACKWARD_LED
        DECF    COUNTER_SECUENCES, F ; resta uno al contador de repeticiones
        BTFSS   STATUS, Z  ; FLAG seteado(igual a 1)?
        GOTO    LOOP_BRL ; NO -> se repite el barrido
        CFG_SECUENCES
        ; SI -> el contador llego a 0, es decir, se repitió 3 veces

RETURN
;*******************************************************************************
; @brief    Efecto de arrastre(Crawling)
;
; @details  Ejecuta el encendido (Progressive_Led_On) y apagado (Progressive_Led_Off)
;           de los leds, repitiendo la secuencia tres veces (Counter_Secuences),
;           con una intermitencia de 100ms.     
;*******************************************************************************
SUBROUTINE
CRAWLING
        CFG_DELAY_100ms
        LEDS_OFF
LOOP_CW
        CALL PROGRESSIVE_LED_ON
        CALL PROGRESSIVE_LED_OFF
        DECF COUNTER_SECUENCES, F ; resta uno al contador de repeticiones
        BTFSS STATUS,Z  ; FLAG seteado(igual a 1)?
        GOTO LOOP_CW ; NO -> se repite el barrido
        CFG_SECUENCES ; SI -> el contador llego a 0, es decir, se repitió 3 veces

RETURN
;*******************************************************************************
; @brief    Barrido hacia la derecha (Forward_Led)
;
; @details  Enciende los leds de forma progresiva de LED0 a LED7, generando el
;           efecto de barrido hacia la derecha.
;               
;*******************************************************************************
SUBROUTINE
FORWARD_LED
        BSF STATUS, C ; setea el LED0 
        
FW_LOOP
       LEDS_RLF ; desplaza el led encendido una posición a la derecha (LED0->LED1...)
       CALL DELAY_3LOOP ;llama al delay
       BTFSS LED7 ; LED7=ON?
       GOTO FW_LOOP ; NO-> repite el barrido
      RETURN ; SI-> termina

RETURN
;*******************************************************************************
; @brief    Encendido progresivo de los LEDs (Crawling ON).
;
; @details  Enciende los LEDs secuencialmente ingresando unos lógicos desde
;           LED0 hacia LED7, manteniendo encendidos los anteriores hasta
;           completar todo el puerto.
;*******************************************************************************
PROGRRESSIVE_LED_ON
        BCF     STATUS, C       ;Carry limpio
PROG_ON_LOOP
        BSF     STATUS, C       ;Forzamos un '1' en el carry
        LEDS_RLF
        CALL    DELAY_3LOOP     ;Espera para visualizar el salto
        BTFSS   PORTD,  7       ;Se encendio el ultimo led?
        GOTO    PROG_ON_LOOP    ;NO -> repite el ciclo
RETURN                          ;SI -> FIN
;*******************************************************************************
; @brief    Apagado progresivo de los 8 LEDs
;
; @details  Apaga los LEDs secuencialmente ingrsandoi ceros lógicos desde LED0
;           hacia LED7
;*******************************************************************************
PROGRESSIVE_LED_OFF
PROG_OFF_LOOP
        BCF     STATUS, C       ; Forzamos un '0' en el carry para ir vaciando
        LEDS_RLF
        CALL    DELAY_3LOOP     ; Espera para visualizar el salto
        MOVF    PORTD, F        ; Se mueve PORTD sobre sí mismo para actualizar el FLAG Z
        BTFSS   STATUS, Z       ; El puerto D quedó en 0?
        GOTO    PROG_OFF_LOOP   ; NO -> repite el ciclo
        RETURN                  ; SI -> FIN

;===============================================================================
    END
;===============================================================================
