PROCESSOR 16F887

#include <xc.inc>

;========================================================
; CONFIGURACIÓN DEL PIC16F887
;========================================================

; CONFIG1
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

; CONFIG2
CONFIG BOR4V = BOR40V
CONFIG WRT = OFF


;========================================================
; VECTOR DE RESET
;========================================================

PSECT resetVec,class=CODE,delta=2

resetVec:
    goto    main


;========================================================
; PROGRAMA PRINCIPAL
;========================================================

PSECT code

main:

    ;--------------------------------------------
    ; Escribe aquí tu código
    ;--------------------------------------------


loop:
    GOTO    loop


END resetVec
