;===============================================================================
; @file       APELLIDO_ED2_TAREA_1.asm
;
; @author     Lurgo Donato
;
; @date       13/8/2026
;
; @brief      Parpadeo de los 8 LEDs del PORTB.
;             Enciende todos los LEDs 500 ms y los apaga 500 ms,
;             formando un parpadeo visible (aprox. 1 Hz).
;===============================================================================

;===============================================================================
; CONFIGURACION DEL PIC16F887
;===============================================================================

; CONFIG1
CONFIG FOSC = INTRC_NOCLKOUT  ; oscilador interno 4 MHz
CONFIG WDTE = OFF             ; sin Watchdog
CONFIG PWRTE = ON             ; espera de arranque
CONFIG MCLRE = ON             ; pin MCLR como reset
CONFIG CP = OFF               ; sin proteccion de codigo
CONFIG CPD = OFF              ; sin proteccion de datos
CONFIG BOREN = ON             ; Brown-out detectado
CONFIG IESO = OFF
CONFIG FCMEN = OFF
CONFIG LVP = OFF              ; sin programacion de bajo voltaje

; CONFIG2
CONFIG BOR4V = BOR40V
CONFIG WRT = OFF

PROCESSOR 16F887
#include <xc.inc>

;===============================================================================
; VARIABLES EN RAM
;===============================================================================
; Variable en memoria compartida (0x70-0x7F), accesible sin cambiar de banco
PSECT udata_shr,class=COMMON

contador:
    DS  1

;===============================================================================
; VECTOR DE RESET
;===============================================================================

PSECT resetVec,class=CODE,delta=2

resetVec:
    goto    main

;===============================================================================
; PROGRAMA PRINCIPAL
;===============================================================================

PSECT code

main:

    ;------------------------------------------------
    ; Inicializacion: PORTB como salida
    ;------------------------------------------------
    BANKSEL TRISB
    CLRF    TRISB           ; todos los pines de PORTB como salida

    BANKSEL PORTB
    CLRF    PORTB           ; apaga todos los LEDs al inicio

    ;------------------------------------------------
    ; Bucle principal: parpadeo de LEDs
    ;------------------------------------------------
loop:
    MOVLW   0xFF
    MOVWF   PORTB           ; enciende los 8 LEDs

    CALL    retardo_500ms   ; espera 500 ms

    CLRF    PORTB           ; apaga los 8 LEDs

    CALL    retardo_500ms   ; espera 500 ms

    GOTO    loop            ; repite para siempre

;===============================================================================
; SUBRUTINAS DE RETARDO
;===============================================================================

;-------------------------------------------------------------------------------
; Retardo de 1 ms (base, igual que en la clase practica)
; Oscilador 4 MHz -> 1 instruccion = 1 us -> 1 ms = 1000 ciclos
; Bucle: (NOP + NOP + DECFSZ + GOTO) = 5 ciclos -> 200 * 5 = 1000 ciclos
;-------------------------------------------------------------------------------
retardo_1ms:
    MOVLW   200             ; contador = 200
    MOVWF   contador

bucle_retardo:
    NOP
    NOP
    DECFSZ  contador, F     ; decrementa; salta cuando llega a 0
    GOTO    bucle_retardo

    RETURN

;-------------------------------------------------------------------------------
; Retardo de 500 ms
; Llama 500 veces al retardo de 1 ms (500 * 1 ms = 500 ms)
;-------------------------------------------------------------------------------
retardo_500ms:
    MOVLW   500             ; repetir 500 veces
    MOVWF   contador

bucle_500ms:
    CALL    retardo_1ms     ; espera 1 ms
    DECFSZ  contador, F     ; decrementa; sale cuando llega a 0
    GOTO    bucle_500ms

    RETURN

;===============================================================================

END resetVec
