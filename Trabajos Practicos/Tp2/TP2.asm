;==============VERSION PRRELIMINAR EDITAR ACA ESTO NO VA A ENTREGA FINAL=====================================================
; @file       G6_TPL2_ED2.asm
;
; @author     Conde_Ana_Victoria
;	          Lauc_Mirko_Gaston
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
#DEFINE SW1   PORTA,RA4
#DEFINE BUZZ  PORTB,RC0
#DEFINE LED0  PORTC,RD0
#DEFINE LED1  PORTC,RD1
#DEFINE LED2  PORTC,RD2
#DEFINE LED3  PORTC,RD3
#DEFINE LED4  PORTC,RD4
#DEFINE LED5  PORTC,RD5
#DEFINE LED6  PORTC,RD6
#DEFINE LED7  PORTC,RD7
;===============================================================================
; DEFINICION DE VARIABLES
;===============================================================================
CBLOCK 0x20
         DELAY1_Init
         DELAY2_Init
         DELAY3_Init
         COUNTER_LED
         COUNTER_SECUENCES
;===============================================================================
; DECLARACION DE MACROS PARA CONFIGURACION DE REGISTROS
;===============================================================================
CFG_SWITCH MACRO
        BSF     STATUS,RP0  ;Switch presionado
        BCF     STATUS,RP1  ;Switch no presionado
        BSF     TRISA,TRISA4 ;RA4 entrada digital ver que carajo es el tris

ENDM
;________________________________esto separa macros distintas pero dentro del bloque macro mamá________________________________________________
CFG_LEDS MACRO
        BSF     STATUS,RP0    ;Chequear estos puertos q no se q es
        BSF     STATUS,RP1
        BCF     ANSELH,RD0    ;ver que es el anselh xd
        BCF     ANSELH,RD1    ; y como es la distribucion de los bancos
        BCF     ANSELH,RD2
        BCF     ANSELH,RD3
        BCF     ANSELH,RD4
        BCF     ANSELH,RD5
        BCF     ANSELH,RD6
        BCF     ANSELH,RD7
        BCF     STATUS,RP1    ;fijate si esta en cero basicamente, supuestamente termina el banco aca
        CLRF     TRISD ; creo q aca chequeamos si el led pasa corriente, a estudiaar
        BCF     STATUS,RP0  ;verr por que se eligen el rp1,rp0 etcetc
        BCF     LED0
        BCF     LED1
        BCF     LED2
        BCF     LED3
        BCF     LED4
        BCF     LED5
        BCF     LED6
        BCF     LED7
        ; VER POR QUE NO SE CIERRA LA FUNCION, COMO QUE EL  PROGRAMA ESPERA ALGO??? capaz sea por el VISUAL code
        ;Se supone que los leds estan apagados por el bcf
        ENDM
;________________________________________________________________________________
;------------------------estos guiones indican macros de la misma familia------------------------------------
LEDS_ON MACRO
        MOVLW  b'11111111' ;Chequear esto esta raaaro
        MOWF   PORTD
ENDM
;-------------------------------------------------------------------------------
LEDS_OFF MACRO
        CLRF   PORTD  ;aca se apagan todos los puertos
ENDM
;-------------------------------------------------------------------------------
LEDS_RLF MACRO
        RLF    PORTD,F  ;aca hacemos el desp a la izquirda de los leds, todos por eso se declara l puerto d
ENDM
;-------------------------------------------------------------------------------
LEDS_RRF MACRO
        RRF    PORTD,F  ;mover todo a la derecha ->
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


;===============================================================================
; INICIO PROGRAMA PRINCIPAL
;===============================================================================
MAIN_LOOP
    ;...
    GOTO    MAIN_LOOP

;===============================================================================
; SUBRUTINAS
;===============================================================================
;*******************************************************************************
; @brief    Descripcion general de la subrutina.
;
; @details  Descripcion especifica de la subrutina.
;*******************************************************************************
SUBROUTINE
    ;...
    RETURN

;===============================================================================
    END
;===============================================================================
