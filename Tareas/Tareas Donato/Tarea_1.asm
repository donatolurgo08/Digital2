;===============================================================================
; @file       APELLIDO_ED2_TAREA_1.asm
;
; @author     Lurgo Donato
;
; @date       13/8/2026
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
__CONFIG _CONFIG1, _FOSC_INTRC_NOCLKOUT & _WDTE_OFF & _PWRTE_ON & _MCLRE_ON & _CP_OFF & _CPD_OFF & _BOREN_ON & _IESO_OFF & _FCMEN_OFF & _LVP_OFF
__CONFIG _CONFIG2, _BOR4V_BOR40V & _WRT_OFF

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
; Variable en RAM comun (0x70-0x7F), accesible sin cambiar de banco
contador   EQU  0x70

;===============================================================================
; DECLARACION DE MACROS PARA CONFIGURACION DE REGISTROS
;===============================================================================

;===============================================================================
; INICIALIZACION DEL MCU (CODIGO ABSOLUTO)
;===============================================================================
    ORG     0x00        ; Vector de Reset
    GOTO    INICIO      ; Salto al inicio del programa principal

    ORG     0x05        ; Ubicacion del programa principal

;===============================================================================
; INICIALIZACION DE MACROS PARA CONFIGURACION DE REGISTROS
;===============================================================================
INICIO
    ;-----Inicializacion de Macros-------
    ; Puerto B como salida
    BANKSEL TRISB
    CLRF    TRISB

    BANKSEL PORTB
    CLRF    PORTB

;===============================================================================
; INICIO PROGRAMA PRINCIPAL
;===============================================================================
MAIN_LOOP
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
retardo_1ms
    MOVLW   TIEMPO          ; contador = 200
    MOVWF   contador

bucle_retardo
    NOP
    NOP
    DECFSZ  contador, F     ; decrementa; salta si llega a 0
    GOTO    bucle_retardo

    RETURN

;===============================================================================
    END
;===============================================================================
