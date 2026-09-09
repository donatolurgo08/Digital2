;===============================================================================
; @file       G6_EDII_TPL3_PICAS.asm
;
; @brief      Grupo 6 - TP3 EDII
;             PIC16F887 - 3 displays de 7 segmentos - catodo comun
;===============================================================================

#include <xc.inc>

;===============================================================================
; CONFIGURACION
;==============================================================================

#define Z STATUS_Z_POSITION
#define C STATUS_C_POSITION
CONFIG FOSC = XT
CONFIG WDTE = OFF
CONFIG PWRTE = OFF
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
; VARIABLES
;===============================================================================
PSECT udata_bank0

DELAY1_Init:        DS 1
DELAY2_Init:        DS 1
DELAY3_Init:        DS 1

DELAY1:             DS 1
DELAY2:             DS 1
DELAY3:             DS 1

DATA_DSPL_1:        DS 1
DATA_DSPL_2:        DS 1
DATA_DSPL_3:        DS 1

COUNTER_DSPL:       DS 1
COUNTER_SEGMENTS:   DS 1
;===============================================================================
; MACROS
;===============================================================================

;-------------------------------------------------------------------------------
; Configuracion de puertos
;-------------------------------------------------------------------------------
CFG_DSPL macro
        ; Banco 3: entradas analogicas -> digitales
        BANKSEL ANSEL
        CLRF    ANSEL
        CLRF    ANSELH

        ; RC0, RC1 y RC2 como salidas
        BANKSEL TRISC
        BCF     TRISC,0
        BCF     TRISC,1
        BCF     TRISC,2

        ; PORTD completo como salida
        BANKSEL TRISD
        CLRF    TRISD

        ; Estado inicial
        BANKSEL PORTC
        CLRF    PORTC
        CLRF    PORTD

        ; Datos propios del Grupo 6
        MOVLW   0x0A
        MOVWF   DATA_DSPL_1

        MOVLW   0x00
        MOVWF   DATA_DSPL_2

        MOVLW   0x06
        MOVWF   DATA_DSPL_3
        endm

;-------------------------------------------------------------------------------
; Apaga todos los segmentos
;-------------------------------------------------------------------------------
DSPL_ALL_OFF macro
        BANKSEL PORTD
        CLRF    PORTD
        endm

;-------------------------------------------------------------------------------
; Enciende los segmentos a-g
;-------------------------------------------------------------------------------
DSPL_ALL_ON macro
        BANKSEL PORTD
        MOVLW   0b01111111
        MOVWF   PORTD
        endm

;-------------------------------------------------------------------------------
; Delay aproximado de 2 ms
;-------------------------------------------------------------------------------
CFG_DELAY_2ms macro
        MOVLW   1
        MOVWF   DELAY1_Init
        MOVLW   45
        MOVWF   DELAY2_Init
        MOVLW   15
        MOVWF   DELAY3_Init
        endm

;-------------------------------------------------------------------------------
; Delay aproximado de 300 ms
;-------------------------------------------------------------------------------
CFG_DELAY_300ms macro
        MOVLW   3
        MOVWF   DELAY1_Init
        MOVLW   248
        MOVWF   DELAY2_Init
        MOVLW   133
        MOVWF   DELAY3_Init
        endm

;-------------------------------------------------------------------------------
; Delay aproximado de 1 s
;-------------------------------------------------------------------------------
CFG_DELAY_1s macro
        MOVLW   10
        MOVWF   DELAY1_Init
        MOVLW   248
        MOVWF   DELAY2_Init
        MOVLW   133
        MOVWF   DELAY3_Init
        endm

;===============================================================================
; VECTOR DE RESET
;===============================================================================
PSECT resetVec,class=CODE,delta=2
resetVec:
        goto    INICIO

;===============================================================================
; CODIGO
;===============================================================================
PSECT code

;===============================================================================
; INICIO
;===============================================================================
INICIO:
        CFG_DSPL
        CALL    RST_COUNTER_DSPL

        ; Test inicial de displays
        CALL    TEST_DSPL

        ; Delay utilizado por el multiplexado
        CFG_DELAY_2ms

MAIN_LOOP:
        CALL    MUX_DSPL
        GOTO    MAIN_LOOP

;===============================================================================
; DELAY DE TRES BUCLES
;===============================================================================
DELAY_3LOOP:
        MOVF    DELAY1_Init,W
        MOVWF   DELAY1

LOOP1:
        MOVF    DELAY2_Init,W
        MOVWF   DELAY2

LOOP2:
        MOVF    DELAY3_Init,W
        MOVWF   DELAY3

LOOP3:
        DECFSZ  DELAY3,F
        GOTO    LOOP3

        DECFSZ  DELAY2,F
        GOTO    LOOP2

        DECFSZ  DELAY1,F
        GOTO    LOOP1

        RETURN

;===============================================================================
; RESET DEL CONTADOR DE DISPLAY
;===============================================================================
RST_COUNTER_DSPL:
        MOVLW   3
        MOVWF   COUNTER_DSPL
        RETURN

;===============================================================================
; DECREMENTO DEL CONTADOR DE DISPLAY
;===============================================================================
DECF_COUNTER_DSPL:
        DECF    COUNTER_DSPL,F
        RETURN

;===============================================================================
; MULTIPLEXADO
;===============================================================================
MUX_DSPL:
        CALL    DELAY_3LOOP

        ; COUNTER_DSPL == 3
        MOVLW   3
        SUBWF   COUNTER_DSPL,W
       BTFSC   STATUS,STATUS_Z_POSITION
        GOTO    UPDATE_DSPL_3

        ; COUNTER_DSPL == 2
        MOVLW   2
        SUBWF   COUNTER_DSPL,W
        BTFSC   STATUS,STATUS_Z_POSITION
        GOTO    UPDATE_DSPL_2

        ; COUNTER_DSPL == 1
        MOVLW   1
        SUBWF   COUNTER_DSPL,W
        BTFSC   STATUS,STATUS_Z_POSITION
        GOTO    UPDATE_DSPL_1

        CALL    RST_COUNTER_DSPL
        RETURN

;===============================================================================
; DISPLAY 1
;===============================================================================
UPDATE_DSPL_1:
        MOVF    DATA_DSPL_1,W
        CALL    TABLE_DECO_DSPL_CC
        BANKSEL PORTD
        MOVWF   PORTD

        MOVF    COUNTER_DSPL,W
        CALL    TABLE_CTRL_DSPL_CC
        BANKSEL PORTC
        MOVWF   PORTC

        CALL    DECF_COUNTER_DSPL
        RETURN

;===============================================================================
; DISPLAY 2
;===============================================================================
UPDATE_DSPL_2:
        MOVF    DATA_DSPL_2,W
        CALL    TABLE_DECO_DSPL_CC
        BANKSEL PORTD
        MOVWF   PORTD

        MOVF    COUNTER_DSPL,W
        CALL    TABLE_CTRL_DSPL_CC
        BANKSEL PORTC
        MOVWF   PORTC

        CALL    DECF_COUNTER_DSPL
        RETURN

;===============================================================================
; DISPLAY 3
;===============================================================================
UPDATE_DSPL_3:
        MOVF    DATA_DSPL_3,W
        CALL    TABLE_DECO_DSPL_CC
        BANKSEL PORTD
        MOVWF   PORTD

        MOVF    COUNTER_DSPL,W
        CALL    TABLE_CTRL_DSPL_CC
        BANKSEL PORTC
        MOVWF   PORTC

        CALL    DECF_COUNTER_DSPL
        RETURN

;===============================================================================
; TEST DE DISPLAY
;===============================================================================
TEST_DSPL:
        CALL    RST_COUNTER_DSPL

LOOP_TEST_DSPL:
        ; Selecciona el display actual
        MOVF    COUNTER_DSPL,W
        CALL    TABLE_CTRL_DSPL_CC
        BANKSEL PORTC
        MOVWF   PORTC

        ; Apaga segmentos antes de comenzar
        DSPL_ALL_OFF

        CFG_DELAY_300ms
        CALL    DELAY_3LOOP

        ; Comienza con segmento A
        BANKSEL PORTD
        MOVLW   0b00000001
        MOVWF   PORTD

        MOVLW   7
        MOVWF   COUNTER_SEGMENTS

LOOP_TEST_SEGMENT:
        CALL    DELAY_3LOOP

        ; Rota el segmento hacia la izquierda
        BCF     STATUS,STATUS_C_POSITION
        RLF     PORTD,F

        DECFSZ  COUNTER_SEGMENTS,F
        GOTO    LOOP_TEST_SEGMENT

        ; Todos los segmentos encendidos
        DSPL_ALL_ON

        ; Aproximadamente 2 segundos
        CFG_DELAY_1s
        CALL    DELAY_3LOOP

        CFG_DELAY_1s
        CALL    DELAY_3LOOP

        ; Todos los segmentos apagados
        DSPL_ALL_OFF

        CFG_DELAY_1s
        CALL    DELAY_3LOOP

        CFG_DELAY_1s
        CALL    DELAY_3LOOP

        ; Siguiente display
        DECFSZ  COUNTER_DSPL,F
        GOTO    LOOP_TEST_DSPL

        CALL    RST_COUNTER_DSPL
        RETURN

;===============================================================================
; TABLA LUT - CÁTODO COMÚN
;
; Indice:
;   0  -> 0
;   1  -> 1
;   2  -> 2
;   ...
;   9  -> 9
;   A  -> A
;
; Grupo 6 utiliza:
;   DATA_DSPL_1 = 10 -> A
;   DATA_DSPL_2 = 0  -> 0
;   DATA_DSPL_3 = 6  -> 6
;===============================================================================
TABLE_DECO_DSPL_CC:
        ADDWF   PCL,F
        RETLW   0b00111111     ; 0
        RETLW   0b00000110     ; 1
        RETLW   0b01011011     ; 2
        RETLW   0b01001111     ; 3
        RETLW   0b01100110     ; 4
        RETLW   0b01101101     ; 5
        RETLW   0b01111101     ; 6
        RETLW   0b00000111     ; 7
        RETLW   0b01111111     ; 8
        RETLW   0b01100111     ; 9
        RETLW   0b01101111     ; A

;===============================================================================
; TABLA DE CONTROL
;
;   0 -> ninguno
;   1 -> RC0
;   2 -> RC1
;   3 -> RC2
;===============================================================================
TABLE_CTRL_DSPL_CC:
        ADDWF   PCL,F
        RETLW   0x00
        RETLW   0x01
        RETLW   0x02
        RETLW   0x04

        END