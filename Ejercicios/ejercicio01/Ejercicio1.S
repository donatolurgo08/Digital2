PROCESSOR 16F887

#include <xc.inc>

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


; Variable en memoria compartida (evita problemas de banco)
PSECT udata_shr,class=COMMON

contador:
    DS  1


; Vector de reset
PSECT resetVec,class=CODE,delta=2

resetVec:
    goto    main


PSECT code

main:

    ; Puerto B como salida
    BANKSEL TRISB
    CLRF    TRISB

    BANKSEL PORTB
    CLRF    PORTB

bucle:
    ; Encender LEDs
    MOVLW   0xFF
    MOVWF   PORTB

    CALL    retardo_1ms     ; pausa de 1 ms

    ; Apagar LEDs
    BANKSEL PORTB
    CLRF    PORTB

    CALL    retardo_1ms     ; pausa de 1 ms

    GOTO    bucle           ; repite


; Retardo de 1 ms con 1 bucle
; Cristal 4 MHz -> instruccion = 1 us -> 1 ms = 1000 ciclos
; Cada pasada (NOP+NOP+DECFSZ+GOTO) = 5 ciclos -> 200 * 5 = 1000
retardo_1ms:

    MOVLW   200             ; contador = 200
    MOVWF   contador

bucle_retardo:
    NOP
    NOP
    DECFSZ  contador, F     ; decrementa; salta si es 0
    GOTO    bucle_retardo

    RETURN


END resetVec