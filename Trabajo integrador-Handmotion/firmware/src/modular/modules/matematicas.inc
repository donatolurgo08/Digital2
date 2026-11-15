;*******************************************************************************
; MODULO MATEMATICAS - Multiplicacion sin signo
;
; Rutinas trasladadas sin cambios de logica desde firmware/src/handmotion.S
; (referencia original, no modificada): mul8x8 y mul16x8.
;
; Dependencias:
;   - Las variables de RAM (MUL_A, MUL_B, RES_L, RES_M, RES_H, MC_L, MC_H,
;     COUNT, TMP, DELTA_L, DELTA_H y PROD_H) NO se declaran en este archivo.
;     Deben estar definidas en el archivo que lo incluya, con la misma
;     ubicacion que en handmotion.S (MUL_A...COUNT, TMP, DELTA_* en RAM comun
;     0x70-0x7F; PROD_H en banco 0).
;   - Las rutinas usan las banderas C, DC y Z de STATUS, y la seleccion de
;     banco mediante RP1:RP0 de STATUS (BANKSEL) para acceder a PROD_H.
;   - Este archivo debe incluirse dentro de un PSECT de codigo (p. ej.
;     PSECT code,class=CODE,delta=2), igual que en handmotion.S.
;   - No incluir este archivo junto con handmotion.S sin antes eliminar sus
;     copias de mul8x8 y mul16x8: las etiquetas se repetirian.
;*******************************************************************************

;*******************************************************************************
; @brief    Multiplica dos valores de 8 bits sin signo.
;
; @details  Algoritmo de suma y desplazamiento. El producto maximo
;           255 * 255 = 65025 cabe en 16 bits.
;
; @param    MUL_A = multiplicando, MUL_B = multiplicador
; @return   RES_H:RES_L = producto de 16 bits
; @modifica MUL_B, RES_L, RES_H, MC_L, MC_H, COUNT, W, STATUS (C, DC, Z)
;*******************************************************************************
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

;*******************************************************************************
; @brief    Multiplica un valor de 16 bits por otro de 8 bits.
;
; @details  Separa el multiplicando en dos bytes y reutiliza mul8x8. El mayor
;           caso de este proyecto es 685 * 49 = 33565, que entra en 16 bits,
;           pero se devuelve el producto completo de 24 bits.
;
; @param    DELTA_H:DELTA_L = multiplicando, MUL_B = multiplicador
; @return   RES_H:RES_M:RES_L = producto de 24 bits
; @modifica MUL_A, MUL_B, RES_L, RES_M, RES_H, MC_L, MC_H, COUNT,
;           TMP, PROD_H, W, STATUS (RP1:RP0, C, DC, Z)
;*******************************************************************************
mul16x8:
        BANKSEL PROD_H
        MOVF    MUL_B,W
        MOVWF   PROD_H          ; guarda el multiplicador
        MOVF    DELTA_L,W
        MOVWF   MUL_A
        CALL    mul8x8
        MOVF    RES_L,W
        MOVWF   TMP             ; producto bajo P_L
        MOVF    RES_H,W
        MOVWF   RES_M           ; producto alto P_H
        MOVF    PROD_H,W
        MOVWF   MUL_B           ; restaura el multiplicador
        MOVF    DELTA_H,W
        MOVWF   MUL_A
        CALL    mul8x8
        MOVF    RES_L,W
        ADDWF   RES_M,F         ; medio = P_H + Q_L
        BTFSC   STATUS,0
        INCF    RES_H,F         ; acarreo al byte alto
        MOVF    TMP,W
        MOVWF   RES_L           ; bajo = P_L
        RETURN
