;===============================================================================
; @file       Gx_TPL4_ED2.asm
;
; @author     Conde_Ana_Victoria
;              Bertalot_Renata
;             Goicoechea_Emilia
;             Lauc_Mirko
;             Lurgo_Donato             
;
; @date       dia/mes/año
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
; DEFINICIÓN DE CONSTANTES (lo dan en la consigna, y lo veo en el diagrama del pic)
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
; DEFINICIÓN DE VARIABLES (lo veo en el diagrama de bloques)
;=============================================================================== 
	W_TEMP          EQU   0x70
    KEYPAD_NUMBER   EQU   0x20
    STATUS_TEMP     EQU   0x71
;===============================================================================
; DECLARACIÓN DE MACROS PARA CONFIGURACIÓN DE REGISTROS
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
         CLRF     ANSHEL                  ;RB0 Y RB5 como salidas digitales
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
         BCF     INTCON,RBIF         ;Baja bandera de interrupción por PORTB
         BSF     INTCON,RBIE         ;Habilita interrupción por cambio en PORTB
         BSF     INTCON,GIE          ;Habilita interrupciones globales
    ENDM
;===============================================================================
; INICIALIZACIÓN DEL MCU (CÓDIGO ABSOLUTO)
;===============================================================================    
    ORG     0x00	    ;Vector de Reset
    GOTO    INICIO	    ;Salto al inicio del programa principal
    ORG     0x04	    ;Vector de Interrupción
    GOTO    ISR_INICIO	    ;Salto al Rutina de Servicio de Interrupción
    ORG     0x05	    ;Ubicación Programa Principal en la memoria 
			    ;de programa
		
;===============================================================================
; INICIALIZACIÓN DE MACROS PARA CONFIGURACIÓN DE REGISTROS
;===============================================================================    	    
INICIO	    ;-----Inicialización de Macros-------
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
; INICIALIZACIÓN DE RUTINAS DE SERVICIO DE INTERRUPCIÓN
;===============================================================================		    
ISR_INICIO		
    ;--------Guardado de Contexto--------
    MOVWF   W_TEMP
    SWAPF   STATUS,W
    MOVWF   STATUS_TEMP
    ;------------------------------------
    ;---Identificación de Interrupción---
    BANKSEL INTCON
    BTFSC   INTCON,RBIF
    GOTO    ISR_IOC
    GOTO    ISR_FIN
    ;------------------------------------	
		
;===============================================================================
; FINALIZACIÓN DE RUTINAS DE SERVICIO DE INTERRUPCIÓN
;===============================================================================		    
ISR_FIN			    
    ;--------Restauración de Contexto--------        
    SWAPF   STATUS_TEMP,W
    MOVWF   STATUS
    SWAPF   W_TEMP,F
    SWAPF   W_TEMP,W
    RETFIE
    ;---------------------------------------- 	  
	
;===============================================================================
; SUBRUTINAS
;===============================================================================
;*******************************************************************************
; @brief    Descripción general de la subrutina.
;           
; @details  Descripción específica de la subrutina.
;******************************************************************************* 
SUBROUTINE
    ;...
    RETURN

;===============================================================================		
    END
;===============================================================================
