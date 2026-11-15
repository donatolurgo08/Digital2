;*******************************************************************************
; MODULO TIMERS - Inicializacion de TIMER0
;
; timer0_init conserva la logica de la referencia firmware/src/handmotion.S.
;
; No incluye: el vector de interrupcion (ORG 4, interruptVec), la ISR
; (t0_isr_restore), sample_xyz_if_due ni sample_xyz_not_due. Esas partes
; permanecen en handmotion_work.S.
;
; Dependencias:
;   - Constantes definidas en handmotion_work.S (no se redefinen aqui):
;       TMR0_RELOAD    (6): valor de precarga de TMR0.
;       X_SAMPLE_TICKS (20): ticks de TIMER0 entre muestras sincronizadas X/Y/Z.
;   - Variables definidas en handmotion_work.S (no se redefinen aqui):
;       T0_DIV         banco 0: divisor por software del muestreo sincronizado.
;       X_SAMPLE_FLAG  banco 0: bit 0 = hay una muestra X/Y/Z pendiente.
;   - Registros SFR: OPTION_REG (T0CS, PSA, PS2:PS0), TMR0 e INTCON
;     (GIE, T0IE, T0IF). Se accede a ellos con BANKSEL.
;   - La rutina depende de la ISR y de sample_xyz_if_due, que estan en
;     handmotion_work.S: timer0_init deja T0_DIV y X_SAMPLE_FLAG listos para
;     que la ISR y sample_xyz_if_due los usen.
;   - Este archivo debe incluirse dentro de un PSECT de codigo, igual que en
;     handmotion.S. No debe incluirse junto con handmotion.S sin eliminar antes
;     la copia de timer0_init: la etiqueta se repetiria.
;*******************************************************************************

;*******************************************************************************
; @brief    Configura TIMER0 como base nominal de 1 ms e inicia la interrupcion
;           de TIMER0.
;
; @details  Configuracion de OPTION_REG:
;             T0CS = 0      reloj interno FOSC/4 (2 MHz con FOSC = 8 MHz)
;             PSA  = 0      prescaler asignado a TIMER0
;             PS2:PS0 = 010 divisor 1:8
;           Precarga TMR0 con TMR0_RELOAD (6): (256 - 6) x 8 x 0,5 us = 1 ms
;           nominal. La frecuencia es nominal: el periodo y el jitter deben
;           medirse en hardware.
;
;           Inicializacion del planificador de muestreo sincronizado X/Y/Z:
;           T0_DIV recibe X_SAMPLE_TICKS (20) y X_SAMPLE_FLAG se limpia. La ISR
;           decrementa T0_DIV en cada desborde y activa la bandera al llegar a
;           cero; el foreground lee/convierte AN1, AN5 y AN6.
;
;           Interrupciones: limpia T0IF pendiente, habilita T0IE y finalmente
;           habilita GIE. GIE se pone en 0 al inicio y en 1 al final.
;
; @param    ninguno
; @return   ninguno
; @modifica W, STATUS (RP1:RP0, Z), OPTION_REG<5,3,2,1,0>,
;           TMR0, T0_DIV, X_SAMPLE_FLAG, INTCON<7,5,2>
;*******************************************************************************
timer0_init:
        BANKSEL OPTION_REG
        BCF     OPTION_REG,5    ; T0CS=0: reloj interno FOSC/4
        BCF     OPTION_REG,3    ; PSA=0: prescaler asignado a TIMER0
        BCF     OPTION_REG,2    ; PS2:PS0 = 010 -> 1:8
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
        BCF     INTCON,7        ; GIE se habilita al final
        BCF     INTCON,2        ; limpia T0IF pendiente
        BSF     INTCON,5        ; T0IE
        BSF     INTCON,7        ; GIE
        RETURN
