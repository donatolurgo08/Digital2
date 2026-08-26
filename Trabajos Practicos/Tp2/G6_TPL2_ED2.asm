;===============================================================================
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
#DEFINE SW1   PORTA, RA4
#DEFINE BUZZ  PORTB, RC0
#DEFINE LED0  PORTC,RD0
#DEFINE LED1  PORT,RD1
#DEFINE LED2  PORTC,RD2
#DEFINE LED3  PORTC,RD3
#DEFINE LED4  PORTC,RD4
#DEFINE LED5 PORTC,RD5
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
    BSF STATUS,RP0      ;Switch presionado
    BCF STATUS,RP1      ;Switch no presionado
    BSF TRISA, TRISA4   ;RA4 entrada digital (ver que es el tris)
ENDM
;----------------------------------------
CFG_LEDS MACRO 
    BSF STATUS,RP0
    BSF STATUS,RP1
    BCF ANSELH,RD0
    BCF ANSELH,RD1
    BCF ANSELH,RD2
    BCF ANSELH,RD3
    BCF ANSELH,RD4
    BCF ANSELH,RD5
    BCF ANSELH,RD6
    BCF ANSELH,RD7
    BCF STATUS,RP1 ;Me fijo si estan en cero los leds
    BCF TRSD, TRISD0
    BCF TRSD, TRISD1
    BCF TRSD, TRISD2
    BCF TRSD, TRISD3
    BCF TRSD, TRISD4
    BCF TRSD, TRISD5
    BCF TRSD, TRISD6
    BCF TRSD, TRISD7
    BCF STATUS, RP0
    BCF LED0
    BCF LED1
    BCF LED2
    BCF LED3
    BCF LED4
    BCF LED5
    BCF LED6
    BCF LED7    
ENDM      
;----------------------------------------

LEDS_ON MACRO
    MOVLW b'11111111'
    MOVWF PORTD
ENDM

;----------------------------------------

LEDS_OFF MACRO
        CLRF PORTD
ENDM

;----------------------------------------

LEDS_RLF MACRO
    RLF    PORTD,F
ENDM

;----------------------------------------

LEDS_RRF MACRO
    RRF    PORTD,F 
ENDM

;_________________________________________

CFG_BUZZER MACRO
    BSF     STATUS,RP0          ;Banco 1 
        BCF     STATUS,RP1

        BCF     TRISC,TRISC0     

        BCF     STATUS,RP0       ;Banco 2
        BCF     STATUS,RP1

        BCF     PORTC,RC0           ; Buzzer inicialmente apagado
ENDM

;-----------------------------------------

BUZZER_ON MACRO
    BSF  PORTC,RC0      ;Pongo RC0 en 1
ENDM

;-----------------------------------------

BUZZER_ OFF MACRO
    BCF  PORTC,RC0      ;Pongo RC0 en 0
ENDM

;_________________________________________

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
CFG_DELAY_1s MACRO
        MOVLW D'46'     ; m = 46
        MOVWF DELAY1_Init
        MOVLW D'189'    ;n = 149
        MOVWF DELAY2_Init
        MOVLW D'37'     ; p = 37 y este bloque se repite asi con el resto de los delays
        MOVWF DELAY3_Init   ; calculamos siempre con la formula de arriba
;-------------------------------------------------------------------------------








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
