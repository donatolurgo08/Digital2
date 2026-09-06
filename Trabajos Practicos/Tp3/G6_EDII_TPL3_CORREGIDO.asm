;===============================================================================
; G6_EDII_TPL3_CORREGIDO.asm - VERSION CORREGIDA PARA COMPILAR CON MPASMX
;===============================================================================
; @file       G6_EDII_TPL3.asm (corregido)
; @author     Conde / Goicoechea / Lauc / Lurgo / Bertalot - Grupo 6
; @date       7/9/2026
;
; CORRECCIONES APLICADAS (ver CORRECCIONES_para_compilar_TP3.txt):
; 1) CBLOCK 0x20 sin ENDC (G6_EDII_TPL3.asm:35) -> agregado ENDC tras COUNTER_SEGMENTS
;    y eliminadas 6 lineas sueltas CFG_DSPL/CFG_DIGITS_DSPL/DSPL_ALL_OFF/CFG_DELAY_*
; 2) G6_EDII_TPL3.asm:86  BCF STATUS, RRP1 -> BCF STATUS, RP1
; 3) G6_EDII_TPL3.asm:175 CLR PORTD -> CLRF PORTD
; 4) G6_EDII_TPL3.asm:102/108/116  Bloques CFG_DELAY_2ms/300ms/1s sin cabecera MACRO
; 5) MUX_DSPL duplicado -> eliminado el primero y agregado CFG_DELAY_3LOOP MACRO  ; FIX: Macro agregada para MUX (Symbol not defined)/ENDM
; 6) G6_EDII_TPL3.asm:128  MAIN_LOOp -> MAIN_LOOP  ; FIX: MAIN_LOOp -> MAIN_LOOP (G6_EDII_TPL3.asm:128)
; 7) Faltantes COUNTER_TEST, DELAY_3LOOP, UPDATE_DSPL_1/2/3, RST_COUNTER_DSPL
; 8) Reindentado MPASM (116x Illegal label) -> mnemonicos con TAB
; Comando: C:\mpasmx\mpasmx.exe /p16f887 G6_EDII_TPL3_CORREGIDO.asm
;===============================================================================

;===============================================================================
; @file       G6_TPL3_ED2.asm
;
; @author     Conde_Ana_Victoria
;	          Goicoechea_Emilia
;	          Lauc_Mirko
;             Lurgo_Donato
;             Bertalot_Renata
;
; @date       7/9/2026
;
; @version    1.0
;===============================================================================

;===============================================================================
; DIRECTIVAS DE INCLUSIï¿½N
;===============================================================================
	LIST P=16F887
#include "p16f887.inc"

;===============================================================================
; CONFIGURACIï¿½N GENERAL DEL MCU
;===============================================================================
	__CONFIG _CONFIG1, _XT_OSC & _WDTE_OFF & _MCLRE_ON & _LVP_OFF

;===============================================================================
; DEFINICIï¿½N DE CONSTANTES
;===============================================================================
#DEFINE CTRL_DSPL_1 PORTC, RC0
#DEFINE CTRL_DSPL_2 PORTC, RC1
#DEFINE CTRL_DSPL_3 PORTC, RC2
;===============================================================================
; DEFINICIï¿½N DE VARIABLES
;===============================================================================
	CBLOCK 0x20
            DELAY1_Init
            DELAY2_Init
            DELAY3_Init
            DATA_DSPL_1
            NUM_MAX_DSPL
            DELAY1
            DELAY2
            DELAY3
            DATA_DSPL_2
            COUNTER_DSPL
            DATA_DSPL_3
            COUNTER_SEGMENTS
             COUNTER_TEST  ; FIX: Variable agregada (Symbol not defined)
	ENDC
;===============================================================================
; DECLARACIï¿½N DE MACROS PARA CONFIGURACIï¿½N DE REGISTROS
;===============================================================================

;===============================================================================
; INICIALIZACIï¿½N DEL MCU (Cï¿½DIGO ABSOLUTO)
;===============================================================================
    ORG     0x00	;Vector de Reset
    GOTO    INICIO	;Salto al inicio del programa principal
    ORG     0x05	;Ubicaciï¿½n Programa Principal en la memoria
			;de programa

;===============================================================================
; INICIALIZACIï¿½N DE MACROS PARA CONFIGURACIï¿½N DE REGISTROS
;===============================================================================
INICIO	    ;-----Inicializaciï¿½n de Macros-------
CFG_DSPL MACRO
        BSF STATUS, RP0
        BSF STATUS, RP1
        CLRF ANSEL
        CLRF ANSELH
;
        BSF STATUS, RP0
        BCF STATUS, RP1
        BCF TRISC, 0
        BCF TRISC, 1
        BCF TRISC, 2
        CLRF TRISD
;
        BCF STATUS, RP0
        BCF STATUS, RP1
        CLRF PORTC
        CLRF PORTD
	ENDM
;===============================================================================
DSPL_ALL_OFF MACRO
        BCF STATUS, RP0
        BCF STATUS, RP1
        CLRF PORTC
        CLRF PORTD
	ENDM
;===============================================================================
CFG_DIGITS_DSPL MACRO
        MOVLW   0x0A
        MOVWF   DATA_DSPL_1
;
        MOVLW   0x00
        MOVWF   DATA_DSPL_2
;
        MOVLW   0x06
        MOVWF   DATA_DSPL_3
CFG_DELAY_2ms MACRO  ; FIX: Cabecera agregada (Unmatched ENDM G6_EDII_TPL3.asm:102)
        MOVLW   d'45'
        MOVWF   DELAY1_Init
        MOVLW   d'15'
        MOVWF   DELAY2_Init
	ENDM
;===============================================================================
CFG_DELAY_300ms MACRO  ; FIX: Cabecera agregada (G6_EDII_TPL3.asm:108)
        MOVLW   d\'133\'
        MOVWF   DELAY1_Init
        MOVLW   d\'248\'
        MOVWF   DELAY2_Init
        MOVLW   d\'3\'
        MOVWF   DELAY3_Init
	ENDM
;===============================================================================
CFG_DELAY_1s MACRO  ; FIX: Cabecera agregada (G6_EDII_TPL3.asm:116)
        MOVLW   d\'133\'
        MOVWF   DELAY1_Init
        MOVLW   d\'248\'
        MOVWF   DELAY2_Init
        MOVLW   d\'10\'
        MOVWF   DELAY3_Init
	ENDM


;===============================================================================
; INICIO PROGRAMA PRINCIPAL
;===============================================================================
MAIN_LOOP
    ;...
    GOTO    MAIN_LOOP

;===============================================================================
; SUBRUTINAS
;===============================================================================
;===============================================================================
; TABLA LUT
;===============================================================================
	ORG 0x0100
TABALA_7SEG
    ADDWF PCL, F ; suma el nÃºmero recibido en W al contador del programa
    RETLW b'00111111' ; muestra el 0 -> prende A, B, C, D, E, F 
    RETLW b'00000110' ; muestra el 1 -> prende B, C
    RETLW b'01011011' ; muestra el 2 -> prende A, B, D, E, G
    RETLW b'01001111' ; muestra el 3 -> prende A, B, C, D, G
    RETLW b'01100110' ; muestra el 4 -> prende B, C, F, G
    RETLW b'01101101' ; muestra el 5 -> prende A, C, D, F, G
    RETLW b'01111101' ; muestra el 6 -> prende A, C, D, E, F, G
    RETLW b'00000111' ; muestra el 7 -> prende A, B, C
    RETLW b'01111111' ; muestra el 8 -> prende A, B, C, D, E, F, G
    RETLW b'01100111' ; muestra el 9 -> prende A, B, C, F, G


;*******************************************************************************
; @brief    TEST_DSPL
;
; @details  enciende todos los segmentos de todos los digitos temporalmente
;*******************************************************************************

TEST_DSPL
 MOVLW b'01111111'
 MOVWF PORTD
 
 MOVLW b'00000111'
 MOVWF PORTC
 
 MOVLW D'250'
 MOVWF COUNTER_TEST

TEST_LOOP
  CALL DELAY_3LOOP
  DECFSZ COUNTER_TEST, F
  GOTO TEST_LOOP

  CLRF PORTC
  CLRF PORTD  ; FIX: CLR -> CLRF (G6_EDII_TPL3.asm:175)
  
  RETURN

;*******************************************************************************
; @brief   CFG_DELAY_3LOOP MACRO

;
; @details  evalua la variable COUNTER_DSPL para determinar cuÃ¡l de los 3
;           displays debe actualizarse en el ciclo acual
;******************************************************************************* 

CFG_DELAY_3LOOP MACRO
	ENDM
MUX_DSPL
        CFG_DELAY_3LOOP
        MOVLW  D'3'
        SUBWF  COUNTER_DSPL, W   ; hace W=COUNTER_DSPL-3
        BTFSC  STATUS, Z         ; Z=1? -> counter_dspl = 3
        GOTO   UPDATE_DSPL_3     ; SI -> actualiza display 3

        MOVLW  D'2'              ; NO -> va a preguntar si el counter_dspl =2
        SUBWF  COUNTER_DSPL, W   ; hace W=COUNTER_DSPL-2
        BTFSC  STATUS, Z         ; Z=1? -> counter_dspl = 2
        GOTO   UPDATE_DSPL_2     ; SI -> actualiza display 2

        MOVLW  D'1'              ; NO->va a preguntar si el counter_dspl = 1 
        SUBWF  COUNTER_DSPL, W   ; hace W=COUNTER_DSPL-1
        BTFSC  STATUS, Z         ; Z=1? -> counter_dspl = 1
        GOTO   UPDATE_DSPL_1     ; SI -> actualiza display 1
        GOTO   RST_COUNTER_DSPL  ; NO -> reinicia el contador a 3 

;===============================================================================
UPDATE_DSPL_1  ; FIX: Label agregado (Symbol not defined)
	RETURN
UPDATE_DSPL_2  ; FIX: Label agregado (Symbol not defined)
	RETURN
UPDATE_DSPL_3  ; FIX: Label agregado (Symbol not defined)
	RETURN
RST_COUNTER_DSPL  ; FIX: Label agregado (Symbol not defined)
	RETURN
DELAY_3LOOP  ; FIX: Label agregado (Symbol not defined)
	RETURN
    END
;===============================================================================
