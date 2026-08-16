;===============================================================================
; @file       APELLIDO_ED2_TAREA_1.asm
;
; @author     Lurgo Donato
;
; @date       16/8/2026
;
; @version    1.0
;===============================================================================

;===============================================================================
; DIRECTIVAS DE INCLUSION
;===============================================================================
PROCESSOR 16F887
#include <xc.inc>

;===============================================================================
; CONFIGURACION GENERAL DEL MCU
;===============================================================================
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
CONFIG BOR4V = BOR40V
CONFIG WRT = OFF

;===============================================================================
; DEFINICION DE CONSTANTES
;===============================================================================
TIEMPO  EQU     200

;===============================================================================
; DEFINICION DE VARIABLES
;===============================================================================
PSECT udata_shr,class=COMMON
contador:
    DS  1

;===============================================================================
; INICIALIZACION DEL MCU (VECTOR DE RESET)
;===============================================================================
PSECT resetVec,class=CODE,delta=2
resetVec:
    GOTO    INICIO

;===============================================================================
; INICIO PROGRAMA PRINCIPAL
;===============================================================================
PSECT code
INICIO:
    BANKSEL TRISB
    CLRF    TRISB
    BANKSEL PORTB
    CLRF    PORTB

MAIN_LOOP:
    MOVLW   0xFF
    MOVWF   PORTB
    CALL    retardo_1ms
    BANKSEL PORTB
    CLRF    PORTB
    CALL    retardo_1ms
    GOTO    MAIN_LOOP

;===============================================================================
; SUBRUTINAS
;===============================================================================
retardo_1ms:
    MOVLW   TIEMPO
    MOVWF   contador
bucle_retardo:
    NOP
    NOP
    DECFSZ  contador, F
    GOTO    bucle_retardo
    RETURN

;===============================================================================
    END resetVec
