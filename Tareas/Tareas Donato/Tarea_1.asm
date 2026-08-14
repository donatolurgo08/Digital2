;===============================================================================
; @file       APELLIDO_ED2_TAREA_1.asm
;
; @author     Lurgo Donato
;
; @date       13/8/2026

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
; Retardo: cristal 4 MHz -> instruccion = 1 us -> 1 ms = 1000 ciclos
; Cada pasada del bucle (NOP+NOP+DECFSZ+GOTO) = 5 ciclos
; Contador = 200 -> 200 * 5 = 1000 ciclos = 1 ms
TIEMPO  EQU     200

;===============================================================================
; DEFINICION DE VARIABLES
;===============================================================================
; Variable en RAM comun (0x70-0x7F), accesible sin BANKSEL
PSECT udata_shr,class=COMMON

contador:
    DS  1

;===============================================================================
; DECLARACION DE MACROS PARA CONFIGURACION DE REGISTROS
;===============================================================================

;===============================================================================
; INICIALIZACION DEL MCU (VECTOR DE RESET)
;===============================================================================
PSECT resetVec,class=CODE,delta=2

resetVec:
    GOTO    INICIO

;===============================================================================
; INICIALIZACION DE MACROS PARA CONFIGURACION DE REGISTROS
;===============================================================================
PSECT code

INICIO:
    ;-----Inicializacion de Macros-------
    ; Puerto B como salida
    BANKSEL TRISB
    CLRF    TRISB

    BANKSEL PORTB
    CLRF    PORTB

;===============================================================================
; INICIO PROGRAMA PRINCIPAL
;===============================================================================
MAIN_LOOP:
    ; Encender LEDs de Puerto B
    MOVLW   0xFF
    MOVWF   PORTB

    ; Retardo de 1 ms
    CALL    retardo_1ms

    ; Apagar LEDs de Puerto B
    BANKSEL PORTB
    CLRF    PORTB

    ; Retardo de 1 ms
    CALL    retardo_1ms

    GOTO    MAIN_LOOP

;===============================================================================
; SUBRUTINAS
;===============================================================================
;*******************************************************************************
; @brief    Retardo por software de 1 ms con 1 bucle.
;
; @details  Cristal 4 MHz -> clock de instruccion = FOSC/4 = 1 MHz
;           -> 1 instruccion = 1 us
;           -> 1 ms = 1000 us = 1000 ciclos de instruccion.
;           Cada pasada del bucle (NOP + NOP + DECFSZ + GOTO) = 5 ciclos.
;           Contador = 200 -> 200 * 5 = 1000 ciclos = 1 ms.
;*******************************************************************************
retardo_1ms:
    MOVLW   TIEMPO          ; contador = 200
    MOVWF   contador

bucle_retardo:
    NOP
    NOP
    DECFSZ  contador, F     ; decrementa; salta si llega a 0
    GOTO    bucle_retardo

    RETURN

;===============================================================================
    END resetVec