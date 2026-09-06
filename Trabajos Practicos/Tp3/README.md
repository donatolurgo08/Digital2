# TP3 — Interfaz de Multiplexado (Grupo 6)

**Materia:** Electrónica Digital 2
**Trabajo Práctico de Laboratorio N°3**
**Fuente:** Instructivo TP3 Grupo 6 + Requisitos de Diseño para TPL3, PIC16F877, Rev. 2026.

## Asignación Grupo 6

| Parámetro | Valor |
|-----------|-------|
| Interfaz | **Multiplexado** |
| Lógica | **Positiva** |
| Transistor | **BC337 (NPN)** |

> **Lógica positiva:** `1` lógico → transistor conduce / display habilitado. `0` lógico → transistor en corte / display deshabilitado. No confundir con lógica negativa.

El BC337 se usa como interruptor **low-side**: con nivel alto en base conduce y habilita el dígito correspondiente. El conexionado exacto debe respetar el esquema entregado por la cátedra.

## Objetivo

Implementar el control de **varios displays de 7 segmentos** mediante **multiplexado** con el **PIC16F877** en Assembly. El PIC no enciende todos los dígitos a la vez: hace un barrido rápido habilitando **un solo display por vez**, colocando su patrón de segmentos, esperando un tiempo corto y pasando al siguiente. El ojo humano percibe los dígitos como si estuvieran encendidos simultáneamente.

Referencia experimental del material *Proyectos con PIC*: **~3 ms por dígito**.

```
D1 → dato 1 → 3 ms → off → D2 → dato 2 → 3 ms → off → D3 → ... → ciclo
```

Para 4 displays: `4 × 3 ms = 12 ms` → `1 / 0,012 s ≈ 83,3 Hz`.

## Concepto de multiplexado

- Las líneas de **segmentos** (`a b c d e f g dp`) se comparten entre todos los displays.
- Se agregan líneas de **selección de dígito** (`D1 D2 D3 D4 ...`), una por transistor BC337.
- En cada instante solo un `Dn = 1`, el resto `0` (lógica positiva).

> Conviene **deshabilitar el display antes de cambiar el patrón** de segmentos para evitar "fantasmas" (números incorrectos durante la transición).

## Distribución funcional de puertos

La distribución **exacta** sale del esquema del TPL3. No copiar ejemplos de otros circuitos.

| Función | Señales |
|---------|---------|
| Segmentos | `a b c d e f g dp` (si se usa punto) |
| Selección | `D1 D2 D3 D4 ...` → bases de BC337 |

> Verificar en el esquema qué puerto/bit corresponde a cada segmento y a cada `Dn`.

## Configuración de puertos (PIC16F877)

Regla `TRIS`:

```
TRIS = 1 → ENTRADA
TRIS = 0 → SALIDA
```

```asm
    bsf STATUS,RP0      ; banco 1
    bcf STATUS,RP1
    clrf TRISB          ; PORTB como salida (segmentos, ej.)
    clrf TRISD          ; PORTD selección (ej.)
    bcf STATUS,RP0      ; banco 0
    bcf STATUS,RP1
    clrf PORTB
    clrf PORTD
```

| Banco | RP1 | RP0 |
|-------|-----|-----|
| 0 | 0 | 0 |
| 1 | 0 | 1 |
| 2 | 1 | 0 |
| 3 | 1 | 1 |

## Tabla de decodificación 7 segmentos

El PIC no envía el decimal, envía el **patrón de bits**. Para orden `bit0=a, bit1=b, ... bit6=g, bit7=dp` (activo en alto):

| Dígito | Segmentos | Patrón |
|--------|-----------|--------|
| 0 | a b c d e f | `0b00111111` |
| 1 | b c | `0b00000110` |
| 2 | a b d e g | `0b01011011` |
| 3 | a b c d g | `0b01001111` |
| 4 | b c f g | `0b01100110` |
| 5 | a c d f g | `0b01101101` |
| 6 | a c d e f g | `0b01111101` |
| 7 | a b c | `0b00000111` |
| 8 | a b c d e f g | `0b01111111` |
| 9 | a b c d f g | `0b01101111` |

> Los valores reales dependen del orden de bits, tipo de display (ánodo/cátodo común) y polaridad del circuito. La tabla **final debe calibrarse con el esquema real**.

### Implementación en ASM

```asm
TABLA:
    addwf PCL,F
    retlw b'00111111'  ; 0
    retlw b'00000110'  ; 1
    retlw b'01011011'  ; 2
    retlw b'01001111'  ; 3
    retlw b'01100110'  ; 4
    retlw b'01101101'  ; 5
    retlw b'01111101'  ; 6
    retlw b'00000111'  ; 7
    retlw b'01111111'  ; 8
    retlw b'01101111'  ; 9
; uso: movf DIGITO,W / call TABLA → W = patrón
```

## Estructura general del programa

```
ORG 0x000        ; vector de reset
    goto INICIO
; ORG 0x004      ; vector interrupciones (si no se usa, no necesario)

INICIO:
    configurar TRIS/PORT
    inicializar variables RAM
LOOP:
    actualizar datos (contador → separar decenas/unidades → tabla)
    multiplexar displays
    goto LOOP

Subrutinas recomendadas: INICIO, MULTIPLEX, TABLA, RETARDO
Si hay contador: CONTADOR + separación de dígitos
```

### Multiplexado paso a paso (Grupo 6)

```asm
; mostrar "1 2 3 4" — lógica positiva
    bcf PORTC,0     ; deshabilitar todos (precaución)
    bcf PORTC,1
    ; D1
    movlw PATRON_1
    movwf PORTB     ; segmentos
    bsf PORTC,0     ; D1 = 1 → BC337 ON
    call RETARDO_3MS
    bcf PORTC,0     ; D1 = 0 → OFF
    ; D2
    movlw PATRON_2
    movwf PORTB
    bsf PORTC,1
    call RETARDO_3MS
    bcf PORTC,1
    ; repetir D3, D4 ...
```

**Orden recomendado para evitar fantasmas:**

1. Deshabilitar display actual
2. Cambiar dato de segmentos
3. Habilitar nuevo display
4. Esperar visualización
5. Repetir

**Regla:** solo un display habilitado por vez:

```
D1=1 D2=0 D3=0 D4=0
D1=0 D2=1 D3=0 D4=0
...
```

## Retardos

Ejemplo del `CONTADOR.ASM` (dos contadores, `DECFSZ`):

```asm
RETARDO:
    movlw D'100'
    movwf CNT1
R1: movlw D'100'
    movwf CNT2
R2: decfsz CNT2,F
    goto R2
    decfsz CNT1,F
    goto R1
    return
```

Para multiplexado usar retardo corto (~3 ms). El tiempo se ajusta con `DECFSZ` anidados o con `TMR0/TMR1` si la consigna lo exige.

## Variables en RAM (ejemplo)

| Variable | Dir. | Uso |
|----------|------|-----|
| CONTADOR | 0x20 | valor a mostrar |
| DIGITO1 | 0x21 | decenas |
| DIGITO2 | 0x22 | unidades |
| RET1 | 0x23 | contador retardo 1 |
| RET2 | 0x24 | contador retardo 2 |
| INDICE | 0x25 | índice de display |

> No usar direcciones de SFR. El PIC16F877 distingue SFR (registros especiales) y GFR (propósito general) por bancos.

## Instrucciones a dominar

`MOVLW`, `MOVWF`, `MOVF`, `CLRF`, `INCF`, `DECF`, `DECFSZ`, `BCF`, `BSF`, `BTFSC`, `BTFSS`, `GOTO`, `CALL`, `RETURN`, `ADDWF`, `RETLW` — y para tablas: `ADDWF PCL,F` + `RETLW`.

## Qué probar en simulación

- [ ] Compila sin errores
- [ ] `TRIS` configurado, solo salidas donde corresponde
- [ ] Solo un transistor activo por vez
- [ ] Tabla entrega patrón correcto
- [ ] Orden de dígitos correcto
- [ ] Sin segmentos fantasmas
- [ ] Tiempo ~3 ms por dígito, sin parpadeo visible
- [ ] Lógica positiva: `1` → BC337 ON, `0` → OFF

## Flujo de trabajo MPLAB

```
Idea → Algoritmo → Diagrama de flujo → Código ASM → Ensamblar
→ Simular → Corregir → Generar HEX → Programar PIC → Probar hardware
```

## Orden recomendado

1. Copiar datos exactos del circuito de la cátedra. 2. Anotar Grupo 6 / lógica positiva / BC337. 3. Dibujar bloques PIC → segmentos / selección → BC337 → display. 4. Identificar puertos/bits de segmentos y `Dn`. 5. Hacer tabla de decodificación. 6. Diagrama de flujo. 7. Definir variables RAM. 8. Programar INIT de puertos. 9. Probar tabla. 10. Probar multiplexado de 1 dígito. 11. Verificar BC337 con nivel alto. 12. Agregar resto de dígitos. 13. Agregar contador/función de consigna. 14. Ajustar retardos. 15. Simular. 16. Corregir. 17. Generar HEX. 18. Programar PIC. 19. Probar hardware.

## Archivos de la carpeta

| Archivo | Descripción |
|---------|-------------|
| `Tp3.S` / `Tp3.asm` | Código fuente Assembly (pic-as / MPASM) |
| `Tp3.hex` | Firmware compilado para MPLAB / bootloader |
| `Instructivo_TP3_Grupo_6_PIC.txt` | Hoja de ruta base (no sustituir por este README) |

> No subir intermedios (`.o`, `.elf`, `build/`, `dist/`).

## Qué NO hacer

- Cambiar BC337 sin autorización, invertir lógica, asumir polaridad de segmentos, copiar tabla de otro circuito, habilitar dos displays a la vez, cambiar puertos de la consigna, usar RAM de SFR, olvidar volver al banco 0, cambiar de PIC.

## Checklist final Grupo 6

- [ ] Grupo 6 / lógica positiva / BC337
- [ ] Pines del esquema anotados
- [ ] Tabla y diagrama hechos
- [ ] `TRIS`/`PORT` inicializados
- [ ] Multiplexado con un solo `Dn=1` por vez
- [ ] Retardo probado (~3 ms)
- [ ] HEX generado y hardware probado

## Fuentes

`Ejercicio PIC - ASSEMBLER.docx` (CONTADOR.ASM) · `REQ_TPL3_GRUPOS.pdf` (Grupo 6) · `PIC16F877.pdf` · `PIC16F877-solo-perifericos.pdf` · `manualPic.pdf` · `Proyectos con PIC.pdf` (multiplexado y tabla).

> Este README resume el instructivo. Ante discrepancias, prevalece el esquema y la consigna entregados por la cátedra.
