;===============================================================================
; @file       CONDE_ED2_TAREA_3_1.asm
;
; @brief      Escribir un programa que demore un milisegundo.
;
; @details    - Considerar Retardo por Software con 1 Bucle.
;             - Considerar Cristal de 4MHz.
;             - Implementacion para PIC16F887 en MPLAB X con MPASM.
;
; @author     Ana Victoria Conde
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

;===============================================================================
; DEFINICION DE CONSTANTES
;===============================================================================
TIEMPO  EQU     D'200'      ; n = 200 -> 5*200+3 = 1003 ciclos = 1003 us = 1 ms

;===============================================================================
; DEFINICION DE VARIABLES
;===============================================================================
CBLOCK 0X20
CONTADOR_Init               ; Valor inicial del contador (n)
CONTADOR                    ; Contador de trabajo del bucle
ENDC

;===============================================================================
; DECLARACION DE MACROS PARA CONFIGURACION DE REGISTROS
;===============================================================================
CFG_RETARDO MACRO
MOVLW   TIEMPO              ; n -> W
MOVWF   CONTADOR_Init       ; W -> CONTADOR_Init
ENDM

;===============================================================================
; INICIALIZACION DEL MCU (CODIGO ABSOLUTO)
;===============================================================================
ORG 0x00                    ; Vector de Reset
GOTO INICIO                 ; Salto al inicio del programa principal
ORG 0x05                    ; Ubicacion Programa Principal en la memoria
                            ; de programa

;===============================================================================
; INICIALIZACION DE MACROS PARA CONFIGURACION DE REGISTROS
;===============================================================================
INICIO                      ; -----Inicializacion de Macros-------
CFG_RETARDO

;===============================================================================
; INICIO PROGRAMA PRINCIPAL
;===============================================================================
; Ciclos de Maquina
CALL RETARDO_1MS            ; 2

MAIN_LOOP
GOTO MAIN_LOOP              ; Bucle infinito

;===============================================================================
; SUBRUTINAS
;===============================================================================
;*******************************************************************************
; @brief    Subrutina de Retardo por Software de 1 ms con 1 bucle.
;
; @details  Cristal 4 MHz -> f_inst = f_clk/4 = 1 MHz -> t_inst = 1 us
;           -> 1 ms = 1000 ciclos de instruccion.
;           Cada pasada del bucle (NOP+NOP+DECFSZ+GOTO) = 5 ciclos.
;           Contador = 200 -> 5*200+3 = 1003 ciclos = 1 ms.
;*******************************************************************************
RETARDO_1MS
MOVFW   CONTADOR_Init       ; 1
MOVWF   CONTADOR            ; 1
LOOP_RETARDO
NOP                         ; n
NOP                         ; n
DECFSZ  CONTADOR,F          ; (n-1)+2
GOTO    LOOP_RETARDO        ; 2*(n-1)
RETURN                      ; 2

;===============================================================================
; Nro ciclos_inst. = 1+1+n+n+[(n-1)+2]+[2*(n-1)]+2
;
; Nro ciclos_inst. = 5n+3
;
; Nro ciclos_inst. = (t_DELAY/t_inst.) = [t_DELAY/(4*t_clk)] = (1/4)*(t_DELAY*f_clk)
;
; t_DELAY = (4/f_clk)*(5n+3)
;
; Con n=200D ^ f_clk = 4MHz -> t_DELAY = (4/4MHz)*1003 = 1003 us = 1 ms
;
; Retardo Maximo -> n = 255D ^ f_clk = 4MHz
;                   t_DELAY_MAX = (4/4MHz)*(5*255+3) = 1278 us = 1,28 ms
;===============================================================================

;===============================================================================
END
;===============================================================================
