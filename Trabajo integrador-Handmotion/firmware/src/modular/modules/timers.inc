;===============================================================================
; Trabajo Integrador: HAND MOTION
; Modulo: Temporizadores
;
; Autores:
;   - Conde Ana Victoria
;   - Lurgo Donato
;
; Fecha: 17/11/2026
; Microcontrolador: PIC16F887
;
; Descripcion:
;   Configuracion de TIMER0 como base de tiempo nominal de 1 ms.
;   Gestion del intervalo de muestreo sincronizado de los ejes X, Y y Z.
;
;===============================================================================

;===============================================================================
; @brief Configura TIMER0 como base de tiempo nominal de 1 ms.
;
; @details Utiliza el reloj interno FOSC/4 y un prescaler de 1:8.
;          Carga el valor inicial de TMR0 y habilita su interrupcion.
;
;          Inicializa el divisor de muestreo para generar una solicitud
;          de lectura de los ejes X, Y y Z cada 20 interrupciones.
;
; @param Ninguno.
; @return Ninguno.
; @modifica W, STATUS, OPTION_REG, TMR0, T0_DIV,
;           X_SAMPLE_FLAG e INTCON.
;===============================================================================
timer0_init:
        BANKSEL OPTION_REG
        BCF     OPTION_REG,5    ; Selecciona el reloj interno.
        BCF     OPTION_REG,3    ; Asigna el prescaler a TIMER0.
        BCF     OPTION_REG,2    ; Configura el prescaler en 1:8.
        BSF     OPTION_REG,1
        BCF     OPTION_REG,0

        BANKSEL TMR0
        MOVLW   TMR0_RELOAD
        MOVWF   TMR0

        BANKSEL T0_DIV
        MOVLW   X_SAMPLE_TICKS
        MOVWF   T0_DIV
        CLRF    X_SAMPLE_FLAG

        BANKSEL INTCON
        BCF     INTCON,7        ; Deshabilita interrupciones globales durante la configuracion.
        BCF     INTCON,2        ; Limpia la bandera de interrupcion pendiente.
        BSF     INTCON,5        ; Habilita la interrupcion de TIMER0.
        BSF     INTCON,7        ; Habilita las interrupciones globales.
        RETURN
