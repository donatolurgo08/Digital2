;===============================================================================
; @file       TPL1.asm
;
; @author     Lurgo Donato
;
; @date       19/8/2026
;
; @brief      TPL1 - Programacion del MCU. Blink LED en RC0.
;
; @details    PIC16F887 con clock externo (cristal) de 4 MHz.
;             1 LED conectado en RC0 con periodo de intermitencia de 2 s
;             (1 s encendido + 1 s apagado).
;             Firmware final: TPL1.hex
;===============================================================================

;===============================================================================
; DIRECTIVAS DE INCLUSION
;===============================================================================
PROCESSOR 16F887
#include <xc.inc>

;===============================================================================
; CONFIGURACION GENERAL DEL MCU
;===============================================================================
; Clock externo: cristal de 4 MHz en RA7/OSC1 y RA6/OSC2 (modo XT)
CONFIG FOSC = XT
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
; Retardo: cristal 4 MHz -> FOSC/4 = 1 MHz -> 1 instruccion = 1 us
;           1 s = 1.000.000 us = 1.000.000 ciclos de instruccion.
; Tres loops anidados (DECFSZ + GOTO):
;   K3 * (K2 * (K1 * 3)) ~ 1.000.000 con contadores K1=147, K2=107, K3=21
K1      EQU     147
K2      EQU     107
K3      EQU     21

;===============================================================================
; DEFINICION DE VARIABLES
;===============================================================================
; Variables en RAM comun (0x70-0x7F), accesibles sin BANKSEL
PSECT udata_shr,class=COMMON

cont1:
    DS  1
cont2:
    DS  1
cont3:
    DS  1

;===============================================================================
; VECTOR DE RESET
;===============================================================================
PSECT resetVec,class=CODE,delta=2

resetVec:
    GOTO    main

;===============================================================================
; PROGRAMA PRINCIPAL
;===============================================================================
PSECT code

main:
    ;----- Inicializacion de puertos ----
    ; RC0 como salida (bit 0 de TRISC en 0)
    BANKSEL TRISC
    MOVLW   0xFE
    MOVWF   TRISC

    ; PORTC inicialmente en 0
    BANKSEL PORTC
    CLRF    PORTC

;===============================================================================
; INICIO PROGRAMA PRINCIPAL
;===============================================================================
loop:
    ; Encender LED en RC0
    BSF     PORTC, 0

    ; Retardo de 1 s (LED encendido)
    CALL    retardo_1s

    ; Apagar LED en RC0
    BCF     PORTC, 0

    ; Retardo de 1 s (LED apagado)
    CALL    retardo_1s

    GOTO    loop

;===============================================================================
; SUBRUTINAS
;===============================================================================
;*******************************************************************************
; @brief    Retardo por software de 1 s con 3 bucles anidados.
;
; @details  Cristal 4 MHz -> clock de instruccion = FOSC/4 = 1 MHz
;           -> 1 instruccion = 1 us -> 1 s = 1.000.000 ciclos.
;           Formula exacta del bucle triple (sin NOP extra):
;             ciclos = (K3-1)*(3*K1*K2 + 4*K2 + 4) + 3*K1*K2 + 4*K2 + 5
;           Con K1=147, K2=107, K3=21 -> 1.000.000 ciclos = 1,000000 s.
;*******************************************************************************
retardo_1s:
    MOVLW   K3
    MOVWF   cont3

bucle3:
    MOVLW   K2
    MOVWF   cont2

bucle2:
    MOVLW   K1
    MOVWF   cont1

bucle1:
    DECFSZ  cont1, F        ; decrementa; salta si llega a 0
    GOTO    bucle1

    DECFSZ  cont2, F
    GOTO    bucle2

    DECFSZ  cont3, F
    GOTO    bucle3

    RETURN

;===============================================================================
    END resetVec
