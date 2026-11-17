;===============================================================================
; Trabajo Integrador: HAND MOTION
; Modulo: Operaciones matematicas
;
; Autores:
;   - Conde Ana Victoria
;   - Lurgo Donato
;
; Fecha: 17/11/2026
; Microcontrolador: PIC16F887
;
; Descripcion:
;   Rutinas de multiplicacion sin signo para operar con valores
;   de 8 y 16 bits. Los resultados se almacenan en registros de 16 y 24 bits.
;
;===============================================================================

;===============================================================================
; @brief Multiplica dos valores de 8 bits sin signo.
;
; @details Utiliza un algoritmo de suma y desplazamiento.
;
; @param MUL_A = multiplicando.
;        MUL_B = multiplicador.
; @return RES_H:RES_L = producto de 16 bits.
; @modifica MUL_B, RES_L, RES_H, MC_L, MC_H, COUNT, W y STATUS.
;===============================================================================
mul8x8:
        CLRF    RES_L
        CLRF    RES_H
        MOVF    MUL_A,W
        MOVWF   MC_L
        CLRF    MC_H
        MOVLW   8
        MOVWF   COUNT
mul8_loop:
        BTFSS   MUL_B,0
        GOTO    mul8_skip
        MOVF    MC_L,W
        ADDWF   RES_L,F
        MOVF    MC_H,W
        BTFSC   STATUS,0
        ADDLW   1
        ADDWF   RES_H,F
mul8_skip:
        BCF     STATUS,0
        RLF     MC_L,F
        RLF     MC_H,F
        BCF     STATUS,0
        RRF     MUL_B,F
        DECFSZ  COUNT,F
        GOTO    mul8_loop
        RETURN
;===============================================================================
; @brief Multiplica un valor de 16 bits por otro de 8 bits.
;
; @details Divide el multiplicando en dos bytes y utiliza mul8x8
;          para obtener el producto completo.
;
; @param DELTA_H:DELTA_L = multiplicando.
;        MUL_B = multiplicador.
; @return RES_H:RES_M:RES_L = producto de 24 bits.
; @modifica MUL_A, MUL_B, RES_L, RES_M, RES_H, MC_L, MC_H,
;           COUNT, TMP, PROD_H, W y STATUS.
;===============================================================================
mul16x8:
        BANKSEL PROD_H
        MOVF    MUL_B,W
        MOVWF   PROD_H          ; Guarda el multiplicador.
        MOVF    DELTA_L,W
        MOVWF   MUL_A
        CALL    mul8x8
        MOVF    RES_L,W
        MOVWF   TMP             ; Guarda el byte bajo del producto.
        MOVF    RES_H,W
        MOVWF   RES_M           ; Guarda el byte alto del producto.
        MOVF    PROD_H,W
        MOVWF   MUL_B           ; Recupera el multiplicador.
        MOVF    DELTA_H,W
        MOVWF   MUL_A
        CALL    mul8x8
        MOVF    RES_L,W
        ADDWF   RES_M,F         ; Suma los bytes intermedios.
        BTFSC   STATUS,0
        INCF    RES_H,F         ; Propaga el acarreo al byte alto.
        MOVF    TMP,W
        MOVWF   RES_L           ; Recupera el byte bajo del producto.
        RETURN
