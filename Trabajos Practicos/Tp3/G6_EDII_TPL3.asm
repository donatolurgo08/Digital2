;===============================================================================
; @file       G6_TPL3_ED2.asm
;
; @author     Conde_Ana_Victoria
;             Goicoechea_Emilia
;             Lauc_Mirko
;             Lurgo_Donato
;             Bertalot_Renata
;
; @date       07/09/2026
;
; @version    1.0
;===============================================================================

;===============================================================================
; DIRECTIVAS DE INCLUSIÓN
;===============================================================================
    LIST P=16F887
    #include "p16f887.inc"

;===============================================================================
; CONFIGURACIÓN GENERAL DEL MCU
;===============================================================================
    __CONFIG _CONFIG1, _XT_OSC & _WDTE_OFF & _MCLRE_ON & _LVP_OFF

;===============================================================================
; DEFINICIÓN DE CONSTANTES
;===============================================================================
    #DEFINE CTRL_DSPL_1 PORTC,RC0
    #DEFINE CTRL_DSPL_2 PORTC,RC1
    #DEFINE CTRL_DSPL_3 PORTC,RC2
;===============================================================================
; DEFINICIÓN DE VARIABLES
;===============================================================================
    CBLOCK 0X20
        DELAY1_Init
        DELAY2_Init
        DELAY3_Init
        DELAY1
        DELAY2
        DELAY3
        DATA_DSPL_1
	    DATA_DSPL_2
	    DATA_DSPL_3
        NUM_MAX_DSPL
	    COUNTER_DSPL
	    COUNTER_SEGMENTS
    ENDC

;===============================================================================
; DECLARACIÓN DE MACROS PARA CONFIGURACIÓN DE REGISTROS
;===============================================================================

CFG_DSPL MACRO
    BSF    STATUS,RP0
    BCF    STATUS,RP1       ;Banco 1
    BCF    TRISC,TRISC0     ;Pines RC0, RC1 y RC2 como salidas digitales
    BCF    TRISC,TRISC1
    BCF    TRISC,TRISC2
    BCF    STATUS,RP0       ;Banco 0
    BCF    CTRL_DSPL_1      ;Pines RC0, RC1 y RC2 comienzan en bajo
    BCF    CTRL_DSPL_2
    BCF    CTRL_DSPL_3
    MOVLW  D'3'             ;Índice 3 corresponde al caracter '6'
    MOVWF  DATA_DSPL_1
    MOVLW  D'2'             ;Índice 2 corresponde al caracter '0'
    MOVWF  DATA_DSPL_2
    MOVLW  D'1'             ;Índice 1 corresponde al caracter 'G'
    MOVWF  DATA_DSPL_3
    ENDM

CFG_DIGITS_DSPL MACRO
    BSF    STATUS,RP0
    BCF    STATUS,RP1       ;Banco 1
    CLRF   TRISD            ;Todos el puerto D como salida digital
    BCF    STATUS,RP0       ;Banco 0
    CLRF   PORTD            ;Todo el puerto D comienza en bajo
    ENDM

DSPL_ALL_OFF MACRO
    BCF    STATUS,RP0
    BCF    STATUS,RP1       ;Banco 0
    CLRF   PORTD            ;Todo el puerto D en bajo
    ENDM

DSPL_ALL_ON MACRO
    BCF    STATUS,RP0
    BCF    STATUS,RP1       ;Banco 0
    BSF    PORTD,RD0        ;Todo el puerto D en alto
    BSF    PORTD,RD1
    BSF    PORTD,RD2
    BSF    PORTD,RD3
    BSF    PORTD,RD4
    BSF    PORTD,RD5
    BSF    PORTD,RD6
    ENDM

CFG_DELAY_2ms5 MACRO
    MOVLW  D'5'
    MOVWF  DELAY1_Init
    MOVLW  D'9'
    MOVWF  DELAY2_Init
    MOVLW  D'17'
    MOVWF  DELAY3_Init
    ENDM

CFG_DELAY_300ms MACRO
    MOVLW  D'5'
    MOVWF  DELAY1_Init
    MOVLW  D'169'
    MOVWF  DELAY2_Init
    MOVLW  D'117'
    MOVWF  DELAY3_Init
    ENDM

CFG_DELAY_1s MACRO
    MOVLW  D'255'
    MOVWF  DELAY1_Init
    MOVLW  D'245'
    MOVWF  DELAY2_Init
    MOVLW  D'4'
    MOVWF  DELAY3_Init
    ENDM

CFG_DELAY_2s MACRO
    MOVLW  D'31'
    MOVWF  DELAY1_Init
    MOVLW  D'144'
    MOVWF  DELAY2_Init
    MOVLW  D'148'
    MOVWF  DELAY3_Init
    ENDM

;===============================================================================
; INICIALIZACIÓN DEL MCU (CÓDIGO ABSOLUTO)
;===============================================================================
    ORG     0x00	;Vector de Reset
    GOTO    INICIO	;Salto al inicio del programa principal
    ORG     0x05	;Ubicación Programa Principal en la memoria
			;de programa

;===============================================================================
; INICIALIZACIÓN DE MACROS PARA CONFIGURACIÓN DE REGISTROS
;===============================================================================
INICIO	    ;-----Inicialización de Macros-------
    CFG_DSPL
    CFG_DIGITS_DSPL

;===============================================================================
; INICIO PROGRAMA PRINCIPAL
;===============================================================================
    CALL   TEST_DSPL
    CFG_DELAY_2ms5
MAIN_LOOP
    CALL   MUX_DSPL
    GOTO   MAIN_LOOP

;===============================================================================
; SUBRUTINAS
;===============================================================================
;*******************************************************************************
; @brief    Retardo por Software
;
; @details  Implementa 3 bucles anidados
;           t_DELAY = (4/f_clk)*[(3*p*n*m)+(4*n*m)+(4*m)+5]
;*******************************************************************************
DELAY_3LOOP
    MOVFW  DELAY1_Init   ;m
    MOVWF  DELAY1
LOOP1
    MOVFW  DELAY2_Init   ;n
    MOVWF  DELAY2
LOOP2
    MOVFW  DELAY3_Init   ;p
    MOVWF  DELAY3
LOOP3
    DECFSZ DELAY3,F
      GOTO   LOOP3
    DECFSZ DELAY2,F
      GOTO   LOOP2
    DECFSZ DELAY1,F
      GOTO   LOOP1
    RETURN

;*******************************************************************************
; @brief    Reset del contador de display
;
; @details
;*******************************************************************************
RST_COUNTER_DSPL
    MOVLW    D'3'
    MOVWF    COUNTER_DSPL
    RETURN

;*******************************************************************************
; @brief    Decremento del contador de display
;
; @details  Decrementa el contador en 1
;*******************************************************************************
DECF_COUNTER_DSPL
    DECF    COUNTER_DSPL,F
    RETURN

;*******************************************************************************
; @brief    TABLA DISPLAY CÁTODO COMÚN
;
; @details
;          RD7|RD6|RD5|RD4|RD3|RD2|RD1|RD0
;Caractér   dp|	g | f | e | d | c | b | a     HEX
;  OFF	    0 | 0 | 0 | 0 | 0 | 0 | 0 | 0     00h
;   G	    0 | 1 | 1 | 1 | 1 | 1 | 0 | 1     7Dh
;   0	    0 | 0 | 1 | 1 | 1 | 1 | 1 | 1     3Fh
;   6	    0 | 1 | 1 | 1 | 1 | 1 | 0 | 1     7Dh
;*******************************************************************************
TABLE_DECO_DSPL_CC
    ADDWF    PCL,F
    RETLW    H'00'
    RETLW    H'7D'
    RETLW    H'3F'
    RETLW    H'7D'

;*******************************************************************************
; @brief    TABLA DE CONTROL
;
; @details
;          RC7|RC6|RC5|RC4|RC3|RC2|RC1|RC0    HEX
;           0 | 0 | 0 | 0 | 0 | 0 | 0 | 0     00h
;           0 | 0 | 0 | 0 | 0 | 1 | 0 | 0     04h
;           0 | 0 | 0 | 0 | 0 | 0 | 1 | 0     02h
;           0 | 0 | 0 | 0 | 0 | 0 | 0 | 1     01h
;*******************************************************************************
TABLE_CTRL_DSPL_CC
    ADDWF    PCL,F
    RETLW    H'00'
    RETLW    H'04'
    RETLW    H'02'
    RETLW    H'01'

;*******************************************************************************
; @brief    Subrutina de testeo de los display
;
; @details  Enciende los segmenttos de los display uno a uno, desde a hasta g,
;           luego prende y apaga todos los segmentos del display
;*******************************************************************************
TEST_DSPL
                    CALL   RST_COUNTER_DSPL
LOOP_TEST_DSPL      MOVF   COUNTER_DSPL,W
                    CALL   TABLE_CTRL_DSPL_CC ; Utiliza el valor W para determinar el patron
		            MOVWF  PORTC 			  ;a mostrar en el display
		            BCF    STATUS,RP0		  ;Banco 0
		            BCF    STATUS,RP1
		            BSF    STATUS,C			  ;Bit Carry = 1
		            DSPL_ALL_OFF
		            CFG_DELAY_300ms
		            MOVLW   D'7'
		            MOVWF  COUNTER_SEGMENTS	  ;COUNTER_SEGMENTES = 7
LOOP_TEST_SEGMENT   RLF    PORTD,F			  ;Rota los bits de PORTD una posicion a la izq
                    CALL   DELAY_3LOOP
		            DECFSZ COUNTER_SEGMENTS,F ;Decrementa COUNTER_SEGMENTES
		            GOTO   LOOP_TEST_SEGMENT  ;Repite el bucle mientras no sea cero
		            DSPL_ALL_ON
		            CFG_DELAY_2s
		            CALL   DELAY_3LOOP
		            DSPL_ALL_OFF
		            CALL   DELAY_3LOOP
		            DECFSZ COUNTER_DSPL,F     ;Decrementa COUNTER_DSPL para cambiar de display
		            GOTO   LOOP_TEST_DSPL     ;Repite el bucle mientras no sea cero
                    CALL   RST_COUNTER_DSPL
		    RETURN

;*******************************************************************************
; @brief    Actualización de display 1
;
; @details  Actualiza el caracter mostrado en el display 1
;*******************************************************************************
UPDATE_DSPL_1
    MOVF   DATA_DSPL_1,W
    CALL   TABLE_DECO_DSPL_CC  ;Decodifica el patron para el codigo correspondiente a W
    MOVWF  PORTD
    MOVF   COUNTER_DSPL,W
    CALL   TABLE_CTRL_DSPL_CC  ;Busca en tabla de control para seleccionar el display
    MOVWF  PORTC
    CALL   DECF_COUNTER_DSPL
    RETURN

;*******************************************************************************
; @brief    Actualización de display 2
;
; @details  Actualiza el caracter mostrado en el display 2
;*******************************************************************************
UPDATE_DSPL_2
    MOVF   DATA_DSPL_2,W
    CALL   TABLE_DECO_DSPL_CC  ;Decodifica el patron para W
    MOVWF  PORTD
    MOVF   COUNTER_DSPL,W
    CALL   TABLE_CTRL_DSPL_CC  ;Busca en tabla de control el display
    MOVWF  PORTC
    CALL   DECF_COUNTER_DSPL
    RETURN

;*******************************************************************************
; @brief    Actualización de display 3
;
; @details  Actualiza el caracter mostrado en el display 3
;*******************************************************************************
UPDATE_DSPL_3
    MOVF   DATA_DSPL_3,W
    CALL   TABLE_DECO_DSPL_CC   ;Decodifica el patron para el dato W
    MOVWF  PORTD
    MOVF   COUNTER_DSPL,W
    CALL   TABLE_CTRL_DSPL_CC   ;Busca en tabla de control el display
    MOVWF  PORTC
    CALL   DECF_COUNTER_DSPL
    RETURN

;*******************************************************************************
; @brief    Subrutina de manejo de displays
;
; @details  Multiplexa los displays
;*******************************************************************************
MUX_DSPL
    CALL   DELAY_3LOOP
    MOVLW  D'3'
    SUBWF  COUNTER_DSPL,W
    BTFSC  STATUS,Z
    GOTO   UPDATE_DSPL_3   ;Actualizar display 3
    MOVLW  D'2'
    SUBWF  COUNTER_DSPL,W
    BTFSC  STATUS,Z
    GOTO   UPDATE_DSPL_2   ;Actualizar display 2
    MOVLW  D'1'
    SUBWF  COUNTER_DSPL,W
    BTFSC  STATUS,Z
    GOTO   UPDATE_DSPL_1   ;Actualizar display 1
    CALL   RST_COUNTER_DSPL
    RETURN

;===============================================================================
    END
;===============================================================================