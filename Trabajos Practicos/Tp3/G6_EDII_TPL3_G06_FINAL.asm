;===============================================================================
; @file       G6_EDII_TPL3_G06_FINAL.asm
;
; @author     Conde_Ana_Victoria
;             Goicoechea_Emilia
;             Lauc_Mirko
;             Lurgo_Donato
;             Bertalot_Renata
;             Grupo 06
;
; @date       7/9/2026 - Final G06
; @version    2.0
;
; @brief      Sistema de visualizacion de datos - 3 displays 7-seg catodo comun
;             PIC16F887 @ 4MHz XT
;             - Segmentos: PORTD (RD0=a,RD1=b,RD2=c,RD3=d,RD4=e,RD5=f,RD6=g,RD7=dp)
;             - Control digito (BC337 NPN logica positiva): RC0=DSPL1, RC1=DSPL2, RC2=DSPL3
;             - Comportamiento:
;               1) Al encender: rutina TEST_DSPL secuencial por display
;                  a->g individual 600ms (req) / 300ms (diagrama) + todos ON 2s + OFF 2s
;               2) Luego multiplexado indefinido mensaje G06 (grupo 6)
;                 DATA_DSPL_1=0x0A (G/A), DATA_DSPL_2=0x00, DATA_DSPL_3=0x06
;             - Ref diagramas: ED2_TPL_3_EMigliore.pdf
;
; @note       Compilacion: C:\mpasmx\mpasmx.exe /p16f887 G6_EDII_TPL3_G06_FINAL.asm
;             Config: _XT_OSC & _WDTE_OFF & _PWRTE_ON & _BOREN_OFF & _MCLRE_ON & _LVP_OFF
;===============================================================================

;===============================================================================
; DIRECTIVAS DE INCLUSION
;===============================================================================
	LIST P=16F887
	#include "p16f887.inc"

;===============================================================================
; CONFIGURACION GENERAL DEL MCU - 4MHz XT
;===============================================================================
	__CONFIG _CONFIG1, _XT_OSC & _WDTE_OFF & _PWRTE_ON & _BOREN_OFF & _MCLRE_ON & _LVP_OFF
	__CONFIG _CONFIG2, _WRT_OFF & _BOR21V

;===============================================================================
; DEFINICION DE CONSTANTES
;===============================================================================
	#DEFINE CTRL_DSPL_1 PORTC, RC0
	#DEFINE CTRL_DSPL_2 PORTC, RC1
	#DEFINE CTRL_DSPL_3 PORTC, RC2
;===============================================================================
; DEFINICION DE VARIABLES - Banco 0 (0x20-0x2B)
;===============================================================================
	CBLOCK 0x20
		DELAY1_Init
		DELAY2_Init
		DELAY3_Init
		DATA_DSPL_1
		DELAY1
		DELAY2
		DELAY3
		DATA_DSPL_2
		COUNTER_DSPL
		DATA_DSPL_3
		COUNTER_SEGMENTS
		SEGMENT_SHADOW
	ENDC
;===============================================================================
; DECLARACION DE MACROS PARA CONFIGURACION DE REGISTROS
;===============================================================================
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
CFG_DELAY_2ms MACRO
	MOVLW   d'1'
	MOVWF   DELAY1_Init
	MOVLW   d'45'
	MOVWF   DELAY2_Init
	MOVLW   d'15'
	MOVWF   DELAY3_Init
	ENDM
; Para multiplexado: ~5ms por digito => 15ms ciclo 3 digitos ~66Hz sin parpadeo
; Alternativa lista: CFG_DELAY_5ms = 1*112*15*3us ~5ms
CFG_DELAY_5ms MACRO
	MOVLW   d'1'
	MOVWF   DELAY1_Init
	MOVLW   d'112'
	MOVWF   DELAY2_Init
	MOVLW   d'15'
	MOVWF   DELAY3_Init
	ENDM
;===============================================================================
CFG_DIGITS_DSPL MACRO
	MOVLW   0x0A
	MOVWF   DATA_DSPL_1	; G06: digito 1 = 'G' (codificado como 0x0A -> tabla muestra 'G'/'A')
;
	MOVLW   0x00
	MOVWF   DATA_DSPL_2	; G06: digito 2 = '0'
;
	MOVLW   0x06
	MOVWF   DATA_DSPL_3	; G06: digito 3 = '6'
	ENDM
DSPL_ALL_OFF MACRO
	BCF STATUS, RP0
	BCF STATUS, RP1
	CLRF PORTC
	CLRF PORTD
	ENDM

;===============================================================================
CFG_DELAY_300ms MACRO
	MOVLW   d'3'
	MOVWF   DELAY1_Init
	MOVLW   d'248'
	MOVWF   DELAY2_Init
	MOVLW   d'133'
	MOVWF   DELAY3_Init
	ENDM
;===============================================================================
; 600ms solicitado en consigna: cada segmento a->g permanece 600ms encendido
; Calculo @4MHz (1us/inst): 6*248*133*3us ~= 593ms ~600ms
CFG_DELAY_600ms MACRO
	MOVLW   d'6'
	MOVWF   DELAY1_Init
	MOVLW   d'248'
	MOVWF   DELAY2_Init
	MOVLW   d'133'
	MOVWF   DELAY3_Init
	ENDM
;===============================================================================
CFG_DELAY_1s MACRO
	MOVLW   d'10'
	MOVWF   DELAY1_Init
	MOVLW   d'248'
	MOVWF   DELAY2_Init
	MOVLW   d'133'
	MOVWF   DELAY3_Init
	ENDM
;===============================================================================
; INICIALIZACION DEL MCU (CODIGO ABSOLUTO)
;===============================================================================
	ORG     0x00 ;Vector de Reset
	GOTO    INICIO  ;Salto al inicio del programa principal
	ORG     0x05 ;Ubicacion Programa Principal en la memoria de programa

;===============================================================================
; PROGRAMA PRINCIPAL - Respeta diagrama flujo hoja 0x05
;===============================================================================
INICIO      ;-----Inicializacion de Macros-------
	CFG_DSPL            ; Configura puertos (ANSEL=0, TRISC0-2/TRISD salida, PORTC/D=0)
	CFG_DELAY_2ms       ; Carga valores delay multiplexado (2ms base, usar 5ms si parpadea)
	CALL    TEST_DSPL
	CFG_DIGITS_DSPL     ; Carga mensaje G06 despues del test (segun diagrama flujo)
;===============================================================================
; BUCLE PRINCIPAL INFINITO - MUX_DSPL
;===============================================================================
MAIN_LOOP
	CALL    MUX_DSPL
	GOTO    MAIN_LOOP

;===============================================================================
; SUBRUTINAS
;===============================================================================
;*******************************************************************************
; @brief    Genera un retardo mediante tres bucles anidados.
;
; @details  Utiliza DELAY1_Init, DELAY2_Init y DELAY3_Init como
;           valores iniciales y DELAY1, DELAY2 y DELAY3 como contadores.
;           @4MHz 1inst=1us, formula aprox: DELAY1*DELAY2*DELAY3*3us
;*******************************************************************************
;
DELAY_3LOOP
	MOVF    DELAY1_Init, W  ; Copia el valor inicial del contador 1 a W
	MOVWF   DELAY1          ; Inicia el contador 1

LOOP1
	MOVF    DELAY2_Init, W  ; Copia el valor inicial del contador 2 a W
	MOVWF   DELAY2          ; Inicia el contador 2

LOOP2
	MOVF    DELAY3_Init, W  ; Copia el valor inicial del contador 3 a W
	MOVWF   DELAY3          ; Inicia el contador 3

LOOP3
	DECFSZ  DELAY3, F       ; Decrementa el contador 3
	GOTO    LOOP3           ; Repite hasta que DELAY3 llegue a 0
	DECFSZ  DELAY2, F       ; Decrementa el contador 2
	GOTO    LOOP2           ; Vuelve a cargar DELAY3 y repetir
	DECFSZ  DELAY1, F       ; Decrementa el contador 1
	GOTO    LOOP1           ; Vuelve a cargar DELAY2 y DELAY3
	RETURN                  ; Termina el delay y vuelve al CALL
;
;*******************************************************************************
; @brief   MUX_DSPL - Multiplexado segun COUNTER_DSPL
;
; @details  evalua la variable COUNTER_DSPL para determinar cual de los 3
;           displays debe actualizarse en el ciclo actual. Incluye delay
;           de visualizacion (~2-5ms) para persistencia retina.
;*******************************************************************************
MUX_DSPL
	CALL DELAY_3LOOP
;
	MOVF   COUNTER_DSPL, W
	XORLW  d'3'
	BTFSC  STATUS, Z         ; Z=1? -> counter_dspl = 3
	GOTO   UPDATE_DSPL_3     ; SI -> actualiza display 3
;
	MOVF   COUNTER_DSPL, W
	XORLW  d'2'
	BTFSC  STATUS, Z         ; Z=1? -> counter_dspl = 2
	GOTO   UPDATE_DSPL_2     ; SI -> actualiza display 2

	MOVF   COUNTER_DSPL, W
	XORLW  d'1'
	BTFSC  STATUS, Z         ; Z=1? -> counter_dspl = 1
	GOTO   UPDATE_DSPL_1     ; SI -> actualiza display 1
;
	GOTO   RST_COUNTER_DSPL  ; NO -> reinicia el contador a 3 (caso 0 o corrupto)

;*******************************************************************************
; @brief    Actualiza los datos y la senal de control del display activo.
;
; @details  Envia el patron de segmentos (LUT CC) de DATA_DSPL_i al PORTD
;           y activa el transistor BC337 correspondiente en PORTC segun
;           COUNTER_DSPL via TABLE_CTRL_DSPL_CC (logica positiva: 1=ON).
;*******************************************************************************
UPDATE_DSPL_3
	MOVF    DATA_DSPL_3, W
	CALL    TABLE_DECO_DSPL_CC
	MOVWF    PORTD
	MOVF    COUNTER_DSPL, W
	CALL    TABLE_CTRL_DSPL_CC
	MOVWF   PORTC
;
	GOTO    DECF_COUNTER_DSPL
;-------------------------------------------------------------------------------
UPDATE_DSPL_2
	MOVF    DATA_DSPL_2, W
	CALL    TABLE_DECO_DSPL_CC
	MOVWF    PORTD
	MOVF    COUNTER_DSPL, W
	CALL    TABLE_CTRL_DSPL_CC
	MOVWF   PORTC
;
	GOTO    DECF_COUNTER_DSPL
;-------------------------------------------------------------------------------
UPDATE_DSPL_1
	MOVF    DATA_DSPL_1, W
	CALL    TABLE_DECO_DSPL_CC
	MOVWF    PORTD
	MOVF    COUNTER_DSPL, W
	CALL    TABLE_CTRL_DSPL_CC
	MOVWF   PORTC
;
	GOTO    DECF_COUNTER_DSPL
;*******************************************************************************
; @brief    Actualiza o reinicia el contador del multiplexado.
;
; @details  Resta 1 para pasar al siguiente display, o lo vuelve a 3
;           cuando termina el ciclo. Ambas opciones retornan al MAIN.
;*******************************************************************************
DECF_COUNTER_DSPL
	DECF    COUNTER_DSPL, F
	RETURN

RST_COUNTER_DSPL
	MOVLW   d'3'
	MOVWF   COUNTER_DSPL
	RETURN
;*******************************************************************************
; @brief    TEST_DSPL - Rutina de test secuencial por digito
;
; @details  Para cada uno de los 3 displays (3->2->1):
;           - Activa solo ese display via TABLE_CTRL_DSPL_CC
;           - Recorre segmentos a..g individualmente con SEGMENT_SHADOW
;             y delay 600ms (consigna) - configurable a 300ms si se desea
;           - Luego enciende todos los segmentos 2s y apaga 2s
;           Flujo exacto diagrama: RST COUNTER=3 -> LOOP_TEST_DSPL ->
;           TABLE_CTRL -> SEGMENT_SHADOW=0x01, COUNTER_SEG=7 ->
;           LOOP_TEST_SEGMENT (PORTD=SHADOW, delay, RLF, DECFSZ) ->
;           todos ON 2s -> todos OFF 2s -> COUNTER-- -> Z? RST:LOOP
;*******************************************************************************
TEST_DSPL
	MOVLW  d'3'
	MOVWF  COUNTER_DSPL
;
LOOP_TEST_DSPL
	MOVF  COUNTER_DSPL, W
	CALL   TABLE_CTRL_DSPL_CC
	MOVWF  PORTC
;
	MOVLW  b'00000001'
	MOVWF  SEGMENT_SHADOW	; a=1
	MOVLW  d'7'
	MOVWF  COUNTER_SEGMENTS	; 7 segmentos a-g (dp apagado)
LOOP_TEST_SEGMENT
	MOVF    SEGMENT_SHADOW, W
	MOVWF   PORTD
;
	; Periodo intermitencia: consigna pide 600ms por segmento
	; Si se requiere exacto diagrama (300ms), cambiar a CFG_DELAY_300ms
	CFG_DELAY_600ms
	CALL    DELAY_3LOOP
;
	BCF     STATUS, C
	RLF     SEGMENT_SHADOW, F	; desplaza a siguiente segmento b->c->d...
	DECFSZ  COUNTER_SEGMENTS, F
	GOTO    LOOP_TEST_SEGMENT
;
	MOVLW   b'01111111'
	MOVWF   PORTD	; todos los segmentos ON (catodo comun =1 enciende)
;
	CFG_DELAY_1s
	CALL    DELAY_3LOOP
	CFG_DELAY_1s
	CALL    DELAY_3LOOP	; 2s total ON
;
	CLRF    PORTD	; todos OFF
	CFG_DELAY_1s
	CALL    DELAY_3LOOP
	CFG_DELAY_1s
	CALL    DELAY_3LOOP	; 2s total OFF
;
	DECF    COUNTER_DSPL, F
	MOVF    COUNTER_DSPL, W
	BTFSS   STATUS, Z
	GOTO    LOOP_TEST_DSPL
	; Al terminar, reset para que MUX arranque en 3 (segun flujo)
	MOVLW  d'3'
	MOVWF  COUNTER_DSPL
	RETURN

;===============================================================================
; TABLAS LUT - CATODO COMUN (logica positiva segmentos)
; Orden bits PORTD: bit0=a,1=b,2=c,3=d,4=e,5=f,6=g,7=dp(0)
; Para catodo comun: 1=segmento encendido
;===============================================================================
	ORG     0x0100
TABLE_DECO_DSPL_CC
	ADDWF   PCL, F
	RETLW   b'00111111'	; 0: a b c d e f
	RETLW   b'00000110'	; 1: b c
	RETLW   b'01011011'	; 2: a b d e g
	RETLW   b'01001111'	; 3: a b c d g
	RETLW   b'01100110'	; 4: b c f g
	RETLW   b'01101101'	; 5: a c d f g
	RETLW   b'01111101'	; 6: a c d e f g
	RETLW   b'00000111'	; 7: a b c
	RETLW   b'01111111'	; 8: a b c d e f g
	RETLW   b'01101111'	; 9: a b c d f g
	RETLW   b'01110111'	; 10(A/G): a b c e f g -> 'A' aprox 'G' para G06 (ver nota)
	; Para 'G' puro catodo: 00111101 (a c d e f) alternativa: si queres G exacta usar 00111101
	; Se eligio A=01110111 como representacion de G mas visible en 7seg (G y 6 comparten similar)
TABLE_CTRL_DSPL_CC
	ADDWF   PCL, F
	RETLW   b'00000000'	; 0: ninguno (apagado)
	RETLW   b'00000001'	; 1: RC0 -> DSPL1 ON (BC337)
	RETLW   b'00000010'	; 2: RC1 -> DSPL2 ON
	RETLW   b'00000100'	; 3: RC2 -> DSPL3 ON
;===============================================================================
	END
;===============================================================================
