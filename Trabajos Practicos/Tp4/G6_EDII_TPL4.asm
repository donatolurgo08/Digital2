;===============================================================================
; @file       G6_TPL4_ED2.asm
;
; @author     Conde_Ana_Victoria
;              Bertalot_Renata
;             Goicoechea_Emilia
;             Lauc_Mirko
;             Lurgo_Donato
;
; @date       30/9/2026
;
; @version    1.0
;===============================================================================

;===============================================================================
; DIRECTIVAS DE INCLUSI?N
;===============================================================================
LIST P=16F887
#include "p16f887.inc"

;===============================================================================
; CONFIGURACI?N GENERAL DEL MCU
;===============================================================================
__CONFIG _CONFIG1, _XT_OSC & _WDTE_OFF & _MCLRE_ON & _LVP_OFF

;===============================================================================
; DEFINICI?N DE CONSTANTES
;===============================================================================
    #DEFINE LED0           PORTD,0
    #DEFINE LED1           PORTD,1
    #DEFINE LED2           PORTD,2
    #DEFINE LED3           PORTD,3
    #DEFINE LED4           PORTD,4
    #DEFINE LED5           PORTD,5
    #DEFINE LED6           PORTD,6
    #DEFINE LED7           PORTD,7

    #DEFINE KEYPAD_ROW1    PORTB,0  ; fila 1 (salida)
    #DEFINE KEYPAD_ROW2    PORTB,1  ; fila 2 (salida)
    #DEFINE KEYPAD_COL1    PORTB,4  ; columna 1 (entrada)
    #DEFINE KEYPAD_COL2    PORTB,5  ; columna 2 (entrada)
    #DEFINE KEYPAD_COL3    PORTB,6  ; columna 3 (entrada)
    #DEFINE KEYPAD_COL4    PORTB,7  ; columna 4 (entrada)
;===============================================================================
; DEFINICI?N DE VARIABLES
;===============================================================================
	W_TEMP          EQU   0x70
    KEYPAD_NUMBER   EQU   0x20
    STATUS_TEMP     EQU   0x71
;===============================================================================
; DECLARACI?N DE MACROS PARA CONFIGURACI?N DE REGISTROS
;===============================================================================
    CFG_LEDS MACRO
         BCF      STATUS,RP0
         BCF      STATUS,RP1              ;banco 0
         CLRF     PORTD                   ;leds apagados
         BSF      STATUS,RP0              ;banco 1
         CLRF     TRISD                   ;configuro puerto d como salida
         BCF      STATUS,RP0              ;banco 0
    ENDM
;_______________________________________________________________________________
    CFG_KEYPAD MACRO
         BCF      STATUS,RP0
         BCF      STATUS,RP1              ;banco 0
         CLRF     PORTB                   ;filas en  0
         BSF      STATUS,RP0
         BSF      STATUS,RP1              ;banco 3
         CLRF     ANSELH                  ;RB0 Y RB5 como salidas digitales
         BCF      STATUS,RP1              ;banco 1
         MOVLW    b'11110000'
         MOVWF    TRISB                   ; RB7-RB4 entradas(columnas), RB3-RB0 salidas(filas)
         BCF      OPTION_REG,NOT_RBPU     ;banco 1
         MOVLW    b'11110000'
         MOVWF    WPUB
         MOVLW    b'11110000'
         MOVWF    IOCB
         BCF      STATUS,RP0
    ENDM
;_______________________________________________________________________________
    LEDS_OFF MACRO
         BCF      STATUS,RP0
         BCF      STATUS,RP1              ;banco 0
         CLRF     PORTD                   ;leds apagados
    ENDM
;_______________________________________________________________________________
    CFG_ISR MACRO
         BANKSEL IOCB
         BSF     IOCB,IOCB4          ;Habilita IOC en RB4 (COL1)
         BSF     IOCB,IOCB5          ;Habilita IOC en RB5 (COL2)
         BSF     IOCB,IOCB6          ;Habilita IOC en RB6 (COL3)
         BSF     IOCB,IOCB7          ;Habilita IOC en RB7 (COL4)
         BANKSEL PORTB
         MOVF    PORTB,W             ;Lee PORTB: termina el mismatch
         BCF     INTCON,RBIF         ;Baja bandera de interrupci?n por PORTB
         BSF     INTCON,RBIE         ;Habilita interrupci?n por cambio en PORTB
         BSF     INTCON,GIE          ;Habilita interrupciones globales
    ENDM
;===============================================================================
; INICIALIZACI?N DEL MCU (C?DIGO ABSOLUTO)
;===============================================================================
    ORG     0x00	    ;Vector de Reset
    GOTO    INICIO	    ;Salto al inicio del programa principal
    ORG     0x04	    ;Vector de Interrupci?n
    GOTO    ISR_INICIO	    ;Salto al Rutina de Servicio de Interrupci?n
    ORG     0x05	    ;Ubicaci?n Programa Principal en la memoria
			            ;de programa

;===============================================================================
; INICIALIZACI?N DE MACROS PARA CONFIGURACI?N DE REGISTROS
;===============================================================================
INICIO	    ;-----Inicializaci?n de Macros-------
    CFG_LEDS
    CFG_KEYPAD
	CFG_ISR
;===============================================================================
; INICIO PROGRAMA PRINCIPAL
;===============================================================================
MAIN_LOOP
    ;...
    GOTO    MAIN_LOOP

;===============================================================================
; INICIALIZACI?N DE RUTINAS DE SERVICIO DE INTERRUPCI?N
;===============================================================================
ISR_INICIO
    ;--------Guardado de Contexto--------
    MOVWF   W_TEMP
    SWAPF   STATUS,W
    MOVWF   STATUS_TEMP
    ;------------------------------------
    ;---Identificaci?n de Interrupci?n---
    BANKSEL INTCON
    BTFSC   INTCON,RBIF
    GOTO    ISR_IOC
    GOTO    ISR_FIN
    ;------------------------------------

;===============================================================================
; FINALIZACI?N DE RUTINAS DE SERVICIO DE INTERRUPCI?N
;===============================================================================
ISR_FIN
;--------Restauraci?n de Contexto--------
    SWAPF   STATUS_TEMP,W
    MOVWF   STATUS
    SWAPF   W_TEMP,F
    SWAPF   W_TEMP,W
    RETFIE
;-----------------------------------------
ISR_IOC
    CALL    KEY_READ        ; Ejecuta KEY_READ
    CALL    TEST_KEYPAD     ; Ejecuta TEST_KEYPAD

    BANKSEL INTCON
    BCF     INTCON, RBIF    ; CLR FLAG RBIF: Limpia la bandera de interrupci?n
    GOTO    ISR_FIN         ; Salta a ISR_FIN para terminar

;===============================================================================
; SUBRUTINAS
;===============================================================================
;*******************************************************************************
; @brief    Inicializa la lectura del teclado matricial y activa la primera fila.
;
; @details  Limpia la variable KEYPAD_NUMBER y la incrementa a 1. Luego,
;           configura las salidas de las filas activando KEYPAD_ROW1 (con un 0
;           l?gico) y desactivando KEYPAD_ROW2 (con un 1 l?gico), omitiendo las
;           filas 3 y 4 seg?n el diagrama. Finalmente, salta a SCANN_COLS.
;*******************************************************************************
KEY_READ
    CLRF    KEYPAD_NUMBER       ; Limpia la variable KEYPAD_NUMBER
    INCF    KEYPAD_NUMBER, F    ; Incrementa KEYPAD_NUMBER a 1

ACTIVE_ROW1
    BANKSEL PORTB
    BCF     KEYPAD_ROW1         ; Activa la fila 1 (con un 0 l?gico)
    BSF     KEYPAD_ROW2         ; Desactiva la fila 2 (con un 1 l?gico)
                                ; Omite las filas 3 y 4 seg?n el diagrama
    GOTO    SCANN_COLS          ; Salta a escanear columnas
;*******************************************************************************
; @brief    Enciende el LED correspondiente a la tecla presionada.
;
; @details  Apaga todos los LEDs mediante la macro LEDS_OFF, carga el valor de
;           KEYPAD_NUMBER en W y llama a la tabla de decodificaci?n. Finalmente,
;           asigna el valor devuelto al PORTD para encender el LED y retorna.
;*******************************************************************************
TEST_KEYPAD
    LEDS_OFF                    ; Apaga todos los LEDs
    MOVF    KEYPAD_NUMBER, W    ; Carga el valor de KEYPAD_NUMBER en W
    CALL    TABLE_DECO_LEDS     ; Llama a la tabla de decodificaci?n
    BANKSEL PORTD
    MOVWF   PORTD               ; Asigna el valor devuelto al PORTD para encender el LED
    RETURN                      ; Retorna de la subrutina
;*******************************************************************************
; @brief    Tabla de decodificaci?n para los LEDs.
;
; @details  Recibe en W el n?mero de tecla (1 a 8) y retorna en W el valor
;           binario necesario para encender el LED correspondiente en el Puerto D.
;*******************************************************************************
TABLE_DECO_LEDS
    ADDWF   PCL, F          ; Suma W al Program Counter
    RETLW   b'00000000'     ; Index 0 (No se usa, KEYPAD_NUMBER arranca en 1)
    RETLW   b'00000001'     ; N?mero 1 -> D0 encendido
    RETLW   b'00000010'     ; N?mero 2 -> D1 encendido
    RETLW   b'00000100'     ; N?mero 3 -> D2 encendido
    RETLW   b'00001000'     ; N?mero 4 -> D3 encendido
    RETLW   b'00010000'     ; N?mero 5 -> D4 encendido
    RETLW   b'00100000'     ; N?mero 6 -> D5 encendido
    RETLW   b'01000000'     ; N?mero 7 -> D6 encendido
    RETLW   b'10000000'     ; N?mero 8 -> D7 encendido
;*******************************************************************************
; @brief    Escaneo de las columnas del teclado matricial.
;
; @details  Verifica secuencialmente si las columnas 1 a 4 se encuentran en
;           estado alto (1). Si una columna est? en bajo (0), salta a WAIT_RELEASE.
;           Si est? en alto, incrementa KEYPAD_NUMBER y verifica la siguiente.
;           Si ninguna columna est? en bajo, salta a SCANN_ROWS.
;*******************************************************************************
SCANN_COLS
    BANKSEL PORTB
;   --- ESCANEO COL 1 ---
    BTFSS   KEYPAD_COL1         ; ?KEYPAD_COL1 = 1?
    GOTO    WAIT_RELEASE        ; NO (ES 0) -> Salta a WAIT_RELEASE
    INCF    KEYPAD_NUMBER, F    ; SI (ES 1) -> Incrementa KEYPAD_NUMBER ++
;   --- ESCANEO COL 2 ---
    BTFSS   KEYPAD_COL2         ; ?KEYPAD_COL2 = 1?
    GOTO    WAIT_RELEASE        ; NO (ES 0) -> Salta a WAIT_RELEASE
    INCF    KEYPAD_NUMBER, F    ; SI (ES 1) -> Incrementa KEYPAD_NUMBER
;   --- ESCANEO COL 3 ---
    BTFSS   KEYPAD_COL3         ; ?KEYPAD_COL3 = 1?
    GOTO    WAIT_RELEASE        ; NO (ES 0) -> Salta a WAIT_RELEASE
    INCF    KEYPAD_NUMBER, F    ; SI (ES 1) -> Incrementa KEYPAD_NUMBER
;   --- ESCANEO COL 4 ---
    BTFSS   KEYPAD_COL4         ; ?KEYPAD_COL4 = 1?
    GOTO    WAIT_RELEASE        ; NO (ES 0) -> Salta a WAIT_RELEASE
    INCF    KEYPAD_NUMBER, F    ; SI (ES 1) -> Incrementa KEYPAD_NUMBER
    GOTO    SCANN_ROWS          ; Salta a escanear filas si ninguna columna est? en bajo
;*******************************************************************************
; @brief    Espera a que el usuario libere la tecla presionada.
;
; @details  Implementa bucles de espera para cada columna verificando que su
;           estado vuelva a alto (1 l?gico), indicando que el bot?n fue liberado.
;           Luego limpia las filas 1 y 2 (poni?ndolas en 0) y retorna a la
;           rutina que la llam? (ISR_IOC). Se omiten las filas 3 y 4.
;*******************************************************************************
WAIT_RELEASE
    BANKSEL PORTB
LOOP_COL1
    BTFSS   KEYPAD_COL1         ; ?KEYPAD_COL1 = 1?
    GOTO    LOOP_COL1           ; NO (ES 0) -> Sigue esperando
LOOP_COL2
    BTFSS   KEYPAD_COL2         ; ?KEYPAD_COL2 = 1?
    GOTO    LOOP_COL2           ; NO (ES 0) -> Sigue esperando
LOOP_COL3
    BTFSS   KEYPAD_COL3         ; ?KEYPAD_COL3 = 1?
    GOTO    LOOP_COL3           ; NO (ES 0) -> Sigue esperando
LOOP_COL4
    BTFSS   KEYPAD_COL4         ; ?KEYPAD_COL4 = 1?
    GOTO    LOOP_COL4           ; NO (ES 0) -> Sigue esperando
; Cuando se sueltas todos los botones, se limpian las filas activas
    BCF     KEYPAD_ROW1         ; Limpia la fila 1 (con un 0 l?gico)
    BCF     KEYPAD_ROW2         ; Limpia la fila 2 (con un 0 l?gico)
                                ; Omite las filas 3 y 4 seg?n el diagrama
    RETURN                      ; Retorna a la rutina que la llam? (ISR_IOC)
;*******************************************************************************
; @brief    Determina la fila actual y cambia a la siguiente.
;
; @details  Verifica si KEYPAD_ROW1 est? en 1. Si no lo est? (es 0), significa
;           que se escane? la fila 1 sin ?xito, por lo que salta a ACTIVE_ROW2.
;           Si KEYPAD_ROW2 estaba activa (en 0), como se omiten las filas 3 y 4,
;           el programa se dirige a RST_KEYPAD para reiniciar la secuencia.
;*******************************************************************************
SCANN_ROWS
    BANKSEL PORTB
SCANN_ROW1
    BTFSS   KEYPAD_ROW1         ; ?KEYPAD_ROW1 = 1?
    GOTO    ACTIVE_ROW2         ; NO (ES 0) -> Salta a activar fila 2
SCANN_ROW2
    BTFSS   KEYPAD_ROW2         ; ?KEYPAD_ROW2 = 1?
    GOTO    RST_KEYPAD          ; NO (ES 0) -> Salta a reiniciar secuencia
    GOTO    RST_KEYPAD          ; SI (ES 1) -> Vamos al reset
;*******************************************************************************
; @brief    Activa la segunda fila para el escaneo.
;
; @details  Desactiva la fila 1 (poni?ndola en 1) y activa la fila 2 (poni?ndola
;           en 0), omitiendo las filas 3 y 4. Luego vuelve a SCANN_COLS.
;*******************************************************************************
ACTIVE_ROW2
    BANKSEL PORTB
    BSF     KEYPAD_ROW1         ; Desactiva la fila 1 (con un 1 l?gico)
    BCF     KEYPAD_ROW2         ; Activa la fila 2 (con un 0 l?gico)
                                ; Omite las filas 3 y 4 seg?n el diagrama
    GOTO    SCANN_COLS          ; Salta a escanear columnas
;*******************************************************************************
; @brief    Reinicia las variables del teclado si no se detect? pulsaci?n.
;
; @details  Limpia la variable KEYPAD_NUMBER y pone en 0 las filas 1 y 2
;           para dejarlas en estado inicial. Retorna a la rutina llamadora.
;*******************************************************************************
RST_KEYPAD
    CLRF    KEYPAD_NUMBER       ; Limpia la variable KEYPAD_NUMBER
    BANKSEL PORTB
    BCF     KEYPAD_ROW1         ; Limpia la fila 1 (con un 0 l?gico)
    BCF     KEYPAD_ROW2         ; Limpia la fila 2 (con un 0 l?gico)
                                ; Omite las filas 3 y 4 seg?n el diagrama
    RETURN                      ; Retorna a la rutina que la llam? (ISR_IOC)
;===============================================================================
    END
;===============================================================================
