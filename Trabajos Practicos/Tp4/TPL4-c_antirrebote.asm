L;===============================================================================
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
; DIRECTIVAS DE INCLUSION
;===============================================================================
LIST P=16F887
#include "p16f887.inc"

;===============================================================================
; CONFIGURACION GENERAL DEL MCU
;===============================================================================
__CONFIG _CONFIG1, _XT_OSC & _WDTE_OFF & _MCLRE_ON & _LVP_OFF

;===============================================================================
; DEFINICION DE CONSTANTES
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
; DEFINICION DE VARIABLES
;===============================================================================
	W_TEMP          EQU   0x70
    KEYPAD_NUMBER   EQU   0x20
    STATUS_TEMP     EQU   0x71
    DEBOUNCE_OUTER  EQU   0x21
    DEBOUNCE_INNER  EQU   0x22
;===============================================================================
; DECLARACION DE MACROS PARA CONFIGURACION DE REGISTROS
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
         BCF     INTCON,RBIF         ;Baja bandera de interrupcion por PORTB
         BSF     INTCON,RBIE         ;Habilita interrupcion por cambio en PORTB
         BSF     INTCON,GIE          ;Habilita interrupciones globales
    ENDM
;===============================================================================
; INICIALIZACION DEL MCU (CODIGO ABSOLUTO)
;===============================================================================
    ORG     0x00        ;Vector de Reset
    GOTO    INICIO      ;Salto al inicio del programa principal
    ORG     0x04        ;Vector de Interrupcion
    GOTO    ISR_INICIO  ;Salto a la Rutina de Servicio de Interrupcion
    ORG     0x05        ;Ubicacion Programa Principal en la memoria
                        ;de programa

;===============================================================================
; INICIALIZACION DE MACROS PARA CONFIGURACION DE REGISTROS
;===============================================================================
INICIO      ;-----Inicializacion de Macros-------
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
; INICIALIZACION DE RUTINAS DE SERVICIO DE INTERRUPCION
;===============================================================================
ISR_INICIO
    ;--------Guardado de Contexto--------
    MOVWF   W_TEMP
    SWAPF   STATUS,W
    MOVWF   STATUS_TEMP
    ;------------------------------------
    ;---Identificacion de Interrupcion---
    BANKSEL INTCON
    BTFSC   INTCON,RBIF
    GOTO    ISR_IOC
    GOTO    ISR_FIN
    ;------------------------------------

;===============================================================================
; FINALIZACION DE RUTINAS DE SERVICIO DE INTERRUPCION
;===============================================================================
ISR_FIN
;--------Restauracion de Contexto--------
    SWAPF   STATUS_TEMP,W
    MOVWF   STATUS
    SWAPF   W_TEMP,F
    SWAPF   W_TEMP,W
    RETFIE
;-----------------------------------------
ISR_IOC
    CALL    DEBOUNCE_10MS   ; Antirrebote de la pulsacion
    CALL    KEY_READ        ; Ejecuta KEY_READ
    CALL    TEST_KEYPAD     ; Ejecuta TEST_KEYPAD

    BANKSEL INTCON
    BCF     INTCON, RBIF    ; Limpia la bandera de interrupcion por PORTB
    GOTO    ISR_FIN         ; Salta a ISR_FIN para terminar

;===============================================================================
; SUBRUTINAS
;===============================================================================
;*******************************************************************************
; @brief    Retardo antirrebote de aproximadamente 10 ms a 4 MHz.
;
; @details  Usa dos contadores en RAM comun de banco 0. Se llama al entrar a la
;           ISR para estabilizar la pulsacion y desde WAIT_RELEASE para exigir
;           que las columnas permanezcan altas durante el retardo.
;*******************************************************************************
DEBOUNCE_10MS
    MOVLW   d'10'
    MOVWF   DEBOUNCE_OUTER
DEBOUNCE_OUTER_LOOP
    MOVLW   d'250'
    MOVWF   DEBOUNCE_INNER
DEBOUNCE_INNER_LOOP
    NOP
    DECFSZ  DEBOUNCE_INNER,F
    GOTO    DEBOUNCE_INNER_LOOP
    DECFSZ  DEBOUNCE_OUTER,F
    GOTO    DEBOUNCE_OUTER_LOOP
    RETURN

;*******************************************************************************
; @brief    Inicializa la lectura del teclado matricial y activa la primera fila.
;
; @details  Limpia la variable KEYPAD_NUMBER y la incrementa a 1. Luego,
;           configura las salidas de las filas activando KEYPAD_ROW1 (con un 0
;           logico) y desactivando KEYPAD_ROW2 (con un 1 logico), omitiendo las
;           filas 3 y 4 segun el diagrama. Finalmente, salta a SCANN_COLS.
;*******************************************************************************
KEY_READ
    CLRF    KEYPAD_NUMBER       ; Limpia la variable KEYPAD_NUMBER
    INCF    KEYPAD_NUMBER, F    ; Incrementa KEYPAD_NUMBER a 1

ACTIVE_ROW1
    BANKSEL PORTB
    BCF     KEYPAD_ROW1         ; Activa la fila 1 (con un 0 logico)
    BSF     KEYPAD_ROW2         ; Desactiva la fila 2 (con un 1 logico)
                                ; Omite las filas 3 y 4 segun el diagrama
    GOTO    SCANN_COLS          ; Salta a escanear columnas
;*******************************************************************************
; @brief    Enciende el LED correspondiente a la tecla presionada.
;
; @details  Apaga todos los LEDs mediante la macro LEDS_OFF, carga el valor de
;           KEYPAD_NUMBER en W y llama a la tabla de decodificacion. Finalmente,
;           asigna el valor devuelto al PORTD para encender el LED y retorna.
;*******************************************************************************
TEST_KEYPAD
    LEDS_OFF                    ; Apaga todos los LEDs
    MOVF    KEYPAD_NUMBER, W    ; Carga el valor de KEYPAD_NUMBER en W
    CALL    TABLE_DECO_LEDS     ; Llama a la tabla de decodificacion
    BANKSEL PORTD
    MOVWF   PORTD               ; Asigna el valor devuelto al PORTD para encender el LED
    RETURN                      ; Retorna de la subrutina
;*******************************************************************************
; @brief    Tabla de decodificacion para los LEDs.
;
; @details  Recibe en W el numero de tecla (1 a 8) y retorna en W el valor
;           binario necesario para encender el LED correspondiente en el Puerto D.
;*******************************************************************************
TABLE_DECO_LEDS
    ADDWF   PCL, F          ; Suma W al Program Counter
    RETLW   b'00000000'     ; Index 0 (No se usa, KEYPAD_NUMBER arranca en 1)
    RETLW   b'00000001'     ; Numero 1 -> D0 encendido
    RETLW   b'00000010'     ; Numero 2 -> D1 encendido
    RETLW   b'00000100'     ; Numero 3 -> D2 encendido
    RETLW   b'00001000'     ; Numero 4 -> D3 encendido
    RETLW   b'00010000'     ; Numero 5 -> D4 encendido
    RETLW   b'00100000'     ; Numero 6 -> D5 encendido
    RETLW   b'01000000'     ; Numero 7 -> D6 encendido
    RETLW   b'10000000'     ; Numero 8 -> D7 encendido
;*******************************************************************************
; @brief    Escaneo de las columnas del teclado matricial.
;
; @details  Verifica secuencialmente si las columnas 1 a 4 se encuentran en
;           estado alto (1). Si una columna esta en bajo (0), salta a WAIT_RELEASE.
;           Si esta en alto, incrementa KEYPAD_NUMBER y verifica la siguiente.
;           Si ninguna columna esta en bajo, salta a SCANN_ROWS.
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
    GOTO    SCANN_ROWS          ; Salta a escanear filas si ninguna columna esta en bajo
;*******************************************************************************
; @brief    Espera a que el usuario libere la tecla presionada.
;
; @details  Espera que las cuatro columnas vuelvan a alto y confirma el estado
;           despues de 10 ms para filtrar el rebote de liberacion. Luego limpia
;           las filas 1 y 2 y retorna a ISR_IOC.
;*******************************************************************************
WAIT_RELEASE
    BANKSEL PORTB
LOOP_COL1
    BTFSS   KEYPAD_COL1         ; ?KEYPAD_COL1 = 1?
    GOTO    LOOP_COL1           ; NO (ES 0) -> Sigue esperando
LOOP_COL2
    BTFSS   KEYPAD_COL2         ; ?KEYPAD_COL2 = 1?
    GOTO    LOOP_COL1           ; NO (ES 0) -> Revisa nuevamente las columnas
LOOP_COL3
    BTFSS   KEYPAD_COL3         ; ?KEYPAD_COL3 = 1?
    GOTO    LOOP_COL1           ; NO (ES 0) -> Revisa nuevamente las columnas
LOOP_COL4
    BTFSS   KEYPAD_COL4         ; ?KEYPAD_COL4 = 1?
    GOTO    LOOP_COL1           ; NO (ES 0) -> Revisa nuevamente las columnas

    CALL    DEBOUNCE_10MS       ; Espera para filtrar el rebote de liberacion
    BTFSS   KEYPAD_COL1
    GOTO    LOOP_COL1
    BTFSS   KEYPAD_COL2
    GOTO    LOOP_COL1
    BTFSS   KEYPAD_COL3
    GOTO    LOOP_COL1
    BTFSS   KEYPAD_COL4
    GOTO    LOOP_COL1

; Cuando se sueltan todos los botones, se limpian las filas activas
    BCF     KEYPAD_ROW1         ; Limpia la fila 1 (con un 0 logico)
    BCF     KEYPAD_ROW2         ; Limpia la fila 2 (con un 0 logico)
                                ; Omite las filas 3 y 4 segun el diagrama
    RETURN                      ; Retorna a la rutina que la llamo (ISR_IOC)
;*******************************************************************************
; @brief    Determina la fila actual y cambia a la siguiente.
;
; @details  Verifica si KEYPAD_ROW1 esta en 1. Si no lo esta (es 0), significa
;           que se escaneo la fila 1 sin exito, por lo que salta a ACTIVE_ROW2.
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
; @details  Desactiva la fila 1 (poniendola en 1) y activa la fila 2 (poniendola
;           en 0), omitiendo las filas 3 y 4. Luego vuelve a SCANN_COLS.
;*******************************************************************************
ACTIVE_ROW2
    BANKSEL PORTB
    BSF     KEYPAD_ROW1         ; Desactiva la fila 1 (con un 1 logico)
    BCF     KEYPAD_ROW2         ; Activa la fila 2 (con un 0 logico)
                                ; Omite las filas 3 y 4 segun el diagrama
    GOTO    SCANN_COLS          ; Salta a escanear columnas
;*******************************************************************************
; @brief    Reinicia las variables del teclado si no se detecto pulsacion.
;
; @details  Limpia la variable KEYPAD_NUMBER y pone en 0 las filas 1 y 2
;           para dejarlas en estado inicial. Retorna a la rutina llamadora.
;*******************************************************************************
RST_KEYPAD
    CLRF    KEYPAD_NUMBER       ; Limpia la variable KEYPAD_NUMBER
    BANKSEL PORTB
    BCF     KEYPAD_ROW1         ; Limpia la fila 1 (con un 0 logico)
    BCF     KEYPAD_ROW2         ; Limpia la fila 2 (con un 0 logico)
                                ; Omite las filas 3 y 4 segun el diagrama
    RETURN                      ; Retorna a la rutina que la llamo (ISR_IOC)
;===============================================================================
    END
;===============================================================================
