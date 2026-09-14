;===============================================================================
; @file       G6_TPL3_ED2.asm
;
; @author     Conde_Ana_Victoria
;             Goicoechea_Emilia
;             Lauc_Mirko
;             Lurgo_Donato
;             Bertalot_Renata
;
; @date       7/9/2026
;
; @version    1.1 
;===============================================================================

;===============================================================================
; DIRECTIVAS DE INCLUSIÃN
;===============================================================================
    LIST P=16F887
    #include "p16f887.inc"

;===============================================================================
; CONFIGURACIÃN GENERAL DEL MCU
;===============================================================================
    __CONFIG _CONFIG1, _XT_OSC & _WDTE_OFF & _MCLRE_ON & _LVP_OFF

;===============================================================================
; DEFINICIÃN DE CONSTANTES
;===============================================================================
    #DEFINE CTRL_DSPL_1 PORTC, RC0
    #DEFINE CTRL_DSPL_2 PORTC, RC1
    #DEFINE CTRL_DSPL_3 PORTC, RC2
;===============================================================================
; DEFINICIÃN DE VARIABLES
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
; DECLARACIÃN DE MACROS PARA CONFIGURACIÃN DE REGISTROS
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
; CORRECCION (G10): valores de delay de mux 2.5ms del grupo 10 (5,9,17).
; Original G6: d'1', d'45', d'15' -> parpadeo/brillo inestable.
;       MOVLW   d'1'
        MOVLW   d'5'            ; CORRECCION: valor G10
        MOVWF   DELAY1_Init
;       MOVLW   d'45'
        MOVLW   d'9'            ; CORRECCION: valor G10
        MOVWF   DELAY2_Init
;       MOVLW   d'15'
        MOVLW   d'17'           ; CORRECCION: valor G10
        MOVWF   DELAY3_Init
    ENDM
;===============================================================================
CFG_DIGITS_DSPL MACRO
        MOVLW   0x0A            ; G (indice 10) - display G06
        MOVWF   DATA_DSPL_1
;
        MOVLW   0x00            ; 0 - display G06
        MOVWF   DATA_DSPL_2
;
        MOVLW   0x06            ; 6 - display G06
        MOVWF   DATA_DSPL_3
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
CFG_DELAY_1s MACRO
        MOVLW   d'10'
        MOVWF   DELAY1_Init
        MOVLW   d'248'
        MOVWF   DELAY2_Init
        MOVLW   d'133'
        MOVWF   DELAY3_Init
    ENDM
;===============================================================================
; INICIALIZACIÃN DEL MCU (CÃDIGO ABSOLUTO)
;===============================================================================
    ORG     0x00 ;Vector de Reset
    GOTO    INICIO  ;Salto al inicio del programa principal
    ORG     0x05 ;UbicaciÃ³n Programa Principal en la memoria
            ;de programa

;===============================================================================
; INICIALIZACIÃN DE MACROS PARA CONFIGURACIÃN DE REGISTROS
;===============================================================================
INICIO      ;-----InicializaciÃ³n de Macros-------
        CFG_DSPL            ; Ejecuta la configuraciÃ³n de puertos
        CFG_DELAY_2ms       ; Ejecuta la carga de variables del delay
        CFG_DIGITS_DSPL     ; Ejecuta la carga de datos del grupo

    CALL    TEST_DSPL

   DSPL_ALL_OFF
   CFG_DELAY_2ms            ; Evita el parpadeo visble
   MOVLW   d'3'
   MOVWF   COUNTER_DSPL     ; Estado inicial del contador de multiplexado
;===============================================================================
; INICIO PROGRAMA PRINCIPAL
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
    RETURN                      ; Termina el delay y vuelve al CALL
;
;*******************************************************************************
; @brief   MUX_DSPL
;
; @details  evalua la variable COUNTER_DSPL para determinar cuÃ¡l de los 3
;           displays debe actualizarse en el ciclo acual
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
        GOTO   RST_COUNTER_DSPL  ; NO -> reinicia el contador a 3

;*******************************************************************************
; @brief    Actualiza los datos y la seÃ±al de control del display activo.
;
; @details  EnvÃ­a el patrÃ³n de segmentos (LUT) de DATA_DSPL_i al PORTD
;           y activa el transistor correspondiente en el PORTC segÃºn COUNTER_DSPL.
;*******************************************************************************
UPDATE_DSPL_3
        CLRF    PORTC
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
        CLRF    PORTC
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
; CORRECCION (G10/fantasma): apagar displays antes de cambiar PORTD.
; Faltaba este CLRF PORTC (DSPL_3 y DSPL_2 si lo tienen).
        CLRF    PORTC           ; CORRECCION: agregado
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
        BTFSS   STATUS, Z
        GOTO DSPL_CNT_OK
        MOVLW   d'3'
        MOVWF   COUNTER_DSPL
DSPL_CNT_OK
        RETURN

RST_COUNTER_DSPL
        MOVLW   d'3'
        MOVWF   COUNTER_DSPL
        RETURN
;*******************************************************************************
; @brief    TEST_DSPL
;
; @details  enciende todos los segmentos de todos los digitos temporalmente
;*******************************************************************************
TEST_DSPL
        MOVLW  d'3'
        MOVWF  COUNTER_DSPL
;
LOOP_TEST_DSPL
        CLRF  PORTC
        MOVF  COUNTER_DSPL, W
        CALL   TABLE_CTRL_DSPL_CC
        MOVWF  PORTC
;
        MOVLW  b'00000001'
        MOVWF  SEGMENT_SHADOW
        MOVLW  d'7'
        MOVWF  COUNTER_SEGMENTS
LOOP_TEST_SEGMENT
        MOVF    SEGMENT_SHADOW, W
        MOVWF   PORTD
;
        CFG_DELAY_300ms
        CALL    DELAY_3LOOP
        CALL    DELAY_3LOOP
;
        BCF     STATUS, C
        RLF     SEGMENT_SHADOW, F
        DECFSZ  COUNTER_SEGMENTS, F
        GOTO    LOOP_TEST_SEGMENT

;
       ; Enciende todos los segmentos durante 2 s
        MOVLW   b'01111111'
        MOVWF   PORTD
        CFG_DELAY_1s
        CALL    DELAY_3LOOP
        CFG_DELAY_1s
        CALL    DELAY_3LOOP
;
; Apaga todos los segmentos durante 2 s
        CLRF    PORTD
        CFG_DELAY_1s
        CALL    DELAY_3LOOP
        CFG_DELAY_1s
        CALL    DELAY_3LOOP
;
        DECF    COUNTER_DSPL, F
        MOVF    COUNTER_DSPL, W
        BTFSS   STATUS, Z
        GOTO    LOOP_TEST_DSPL
RETURN

;===============================================================================
; TABLA LUT - CÃTODO COMÃN
;===============================================================================
; CORRECCION (G10/PCL): se elimina el ORG 0x00C0 fijo.
; Con ORG fijo + ADDWF PCL,F sin PCLATH, si el codigo supera ~187 words
; las tablas se pisan o el salto cae fuera de pagina. El G10 que funciona
; deja las tablas pegadas al codigo, sin ORG.
;       ORG     0x00C0

TABLE_DECO_DSPL_CC
        ADDWF   PCL, F
        RETLW   b'00111111'     ; 0
        RETLW   b'00000110'     ; 1
        RETLW   b'01011011'     ; 2
        RETLW   b'01001111'     ; 3
        RETLW   b'01100110'     ; 4
        RETLW   b'01101101'     ; 5
        RETLW   b'01111101'     ; 6
        RETLW   b'00000111'     ; 7
        RETLW   b'01111111'     ; 8
        RETLW   b'01100111'     ; 9
	RETLW   b'01111101'     ; G tipo 6 (a,c,d,e,f,g)

TABLE_CTRL_DSPL_CC
        ADDWF   PCL, F
        RETLW   b'00000000'
        RETLW   b'00000001'     ; Display 1 -> RC0
        RETLW   b'00000010'     ; Display 2 -> RC1
        RETLW   b'00000100'     ; Display 3 -> RC2
;===============================================================================
    END
;===============================================================================
