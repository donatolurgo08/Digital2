# D-01 — Investigación del sistema de interrupciones del PIC16F887

**Responsable:** Donato Lurgo  
**Estado:** TIMER0 usa una ISR mínima; validar temporización en hardware

## Funcionamiento general

El PIC16F887 tiene un único vector de interrupción en `0x0004`. Al aceptar una
interrupción, el hardware guarda el PC en la pila y limpia `GIE`; el programa
debe consultar las flags para identificar una o varias fuentes, atenderlas y
limpiar las flags que correspondan. No hay prioridades configurables entre
fuentes. `RETFIE` retorna y vuelve a habilitar `GIE`.

Solo se guarda automáticamente el PC. El firmware debe preservar el contexto
que use (`W`, `STATUS` y, si corresponde, `PCLATH`) antes de modificar bancos o
registros. La hoja de datos recomienda ubicar temporales como `W_TEMP` y
`STATUS_TEMP` en RAM común, compartida entre bancos (`0x70–0x7F`).

## Registros principales

| Registro | Banco/dirección | Función |
|---|---:|---|
| `INTCON` | 0 / `0x0B` | Habilitación global `GIE`, periféricos `PEIE`, enable/flags de TIMER0 y fuentes externas/PORTB. |
| `PIE1` / `PIR1` | 1 / `0x8C`; 0 / `0x0C` | Enables y flags de ADC, EUSART, TIMER1 y TIMER2, entre otras fuentes. |
| `PIE2` / `PIR2` | 1 / `0x8D`; 0 / `0x0D` | Enables y flags de comparadores, EEPROM, oscilador y otras fuentes. |
| `IOCB` | 3 / `0x196` | Habilita individualmente interrupt-on-change de PORTB; se combina con `RBIE`/`RBIF` en `INTCON`. |

Las flags se activan cuando ocurre el evento aunque su enable o `GIE` estén
deshabilitados. Limpiar la flag pendiente antes de habilitar la interrupción
evita entrar inmediatamente por un evento anterior.

## Fuentes relevantes para HAND MOTION

| Fuente | Flag | Enable individual | Enable adicional |
|---|---|---|---|
| TIMER0 overflow | `INTCON.T0IF` | `INTCON.T0IE` | `GIE` |
| TIMER1 overflow | `PIR1.TMR1IF` | `PIE1.TMR1IE` | `PEIE`, `GIE` |
| TIMER2 match con PR2 | `PIR1.TMR2IF` | `PIE1.TMR2IE` | `PEIE`, `GIE` |
| Conversión ADC completa | `PIR1.ADIF` | `PIE1.ADIE` | `PEIE`, `GIE` |
| EUSART recepción | `PIR1.RCIF` | `PIE1.RCIE` | `PEIE`, `GIE` |
| EUSART transmisión | `PIR1.TXIF` | `PIE1.TXIE` | `PEIE`, `GIE` |

`RCIF` baja al leer los bytes de `RCREG`; `TXIF` es de solo lectura, indica que
`TXREG` está vacío y baja automáticamente al cargarlo. `T0IF`, `TMR1IF`,
`TMR2IF` y `ADIF` deben limpiarse por software. Para EUSART TX, habilitar `TXIE` solo
mientras haya datos pendientes evita interrupciones repetidas con la cola vacía.

En HAND MOTION, TIMER0 es actualmente la única fuente con interrupción
habilitada: la ISR actualiza el tick/flag de muestreo de X. TIMER1 y EUSART se
atienden por polling; la conversión ADC, el parseo de protocolo y el
reconocimiento se ejecutan fuera de la ISR.

## Flujo recomendado de una ISR

1. Guardar `W` y `STATUS` (y `PCLATH` si el código lo requiere).
2. Revisar cada flag habilitada, pues puede haber más de una fuente pendiente.
3. Limpiar la flag de la fuente atendida y ejecutar solo el servicio mínimo:
   recargar un timer si corresponde, copiar un byte recibido o levantar una
   bandera de trabajo.
4. Restaurar contexto y salir con `RETFIE`.

### Fragmento Assembly ilustrativo

Esquema parcial de polling de flags dentro de la ISR; no es una ISR completa ni
compilable hasta definir vector, temporales y banderas del firmware.

```asm
    BANKSEL INTCON
    BTFSS   INTCON, T0IF
    GOTO    REVISAR_TMR1
    BCF     INTCON, T0IF       ; Limpiar TIMER0
    ; Marcar evento ADC en una bandera RAM

REVISAR_TMR1
    BANKSEL PIR1
    BTFSS   PIR1, TMR1IF
    GOTO    FIN_ISR
    BCF     PIR1, TMR1IF       ; Limpiar TIMER1
    ; Avanzar selección del display

FIN_ISR
    ; Restaurar W/STATUS y ejecutar RETFIE
```

## Pendiente de definir

- Validar en hardware la recarga/latencia de TIMER0 y el período de muestreo.
- Definir si otras fuentes necesitarán interrupciones; por ahora TIMER1 y
  EUSART permanecen por polling.

## Fuente

Microchip, *PIC16F882/883/884/886/887 Data Sheet*, DS41291D, secciones 2.2.2,
14.3 y 14.4; tablas de `INTCON`, `PIE1/2`, `PIR1/2`, pp. 26–35 y 216–219.
[PDF oficial](https://ww1.microchip.com/downloads/en/DeviceDoc/41291D.pdf).
