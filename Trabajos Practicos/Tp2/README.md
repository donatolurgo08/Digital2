# TP2 - Sistema de Alarmas

**Materia:** Electrónica Digital 2
**Trabajo Práctico de Laboratorio N°2**
**Fuente:** Consigna oficial TPL2, Ing. Emiliano Migliore, Rev. 2.0, UNC-FCEFyN, 2026.

## Objetivo

Utilizar un microcontrolador **PIC16F887** (clock externo de 4 MHz) para
implementar un sistema de alarmas con:

- Alarmas visuales: **8 LEDs** en PORTD.
- Alarma acústica: **1 buzzer piezoeléctrico activo** en RC0.
- **1 pulsador** con resistencia pull-up en RE0.

## Asignación de pines

| Señal    | Pin  |
|----------|------|
| LED0-7   | RD0-RD7 |
| BUZZER   | RC0  |
| SWITCH   | RE0  |
| Clock    | 4 MHz externo |

## Comportamiento general

- **Pulsador ABIERTO (no presionado):** los 8 LEDs ejecutan `TEST_LEDS`
  de forma indefinida. El buzzer permanece apagado.
- **Pulsador CERRADO (presionado):** se activa el buzzer 200 ms y los LEDs
  muestran secuencialmente:
  1. `RUNNING_LIGHT`
  2. `BIDIRECTIONAL_RUNNING_LIGHT`
  3. `CRAWLING`

  Cada patrón se repite **3 veces** y respeta su período de intermitencia.

## Efectos

| Efecto | Período | ON / OFF | Notas |
|--------|---------|----------|-------|
| `TEST_LEDS` | 2 s | 1 s ON / 1 s OFF | Parpadeo sincronizado de todos los LEDs. |
| `RUNNING_LIGHT` | 600 ms | 300 ms ON / 300 ms OFF | LED se desplaza Izq → Der. |
| `BIDIRECTIONAL_RUNNING_LIGHT` | 400 ms | 200 ms ON / 200 ms OFF | Desplazamiento Izq→Der y Der→Izq. |
| `CRAWLING` | 200 ms* | 200 ms ON / 200 ms OFF | Arrastre progresivo hacia la derecha. |

> **Nota:** la consigna tiene una discrepancia en `CRAWLING`: el texto
> indica 200 ms, pero el diagrama usa `CFG_DELAY_100ms`. Confirmar con el
> docente qué valor utilizar.

## Delays (fórmula, f_clk = 4 MHz)

```
t_DELAY [us] = 3·p·n·m + 4·n·m + 4·m + 5
```

| Delay | p | n | m | Resultado |
|-------|---|---|---|-----------|
| 1 s | 37 | 189 | 46 | ~999999 us |
| 300 ms | 117 | 169 | 5 | 300000 us |
| 200 ms | 139 | 95 | 5 | 200000 us |
| 100 ms | 167 | 198 | 1 | ~99999 us |

## Macros y rutinas a implementar

- **Configuración:** `CFG_SWITCH`, `CFG_LEDS`, `CFG_BUZZER`, `CFG_SEQUENCES`
- **Delays:** `CFG_DELAY_100ms`, `CFG_DELAY_200ms`, `CFG_DELAY_300ms`, `CFG_DELAY_1s`
- **LEDs:** `LEDS_ON`, `LEDS_OFF`, `LEDS_RLF`, `LEDS_RRF`
- **Buzzer:** `BUZZER_ON`, `BUZZER_OFF`
- **Rutinas:** `DELAY_3LOOP`, `TEST_LEDS`, `BUZZER_BIP`, `RUNNING_LIGHT`,
  `FORWARD_LED`, `BIDIRECTIONAL_RUNNING_LIGHT`, `BACKWARD_LED`, `CRAWLING`,
  `PROGRESSIVE_LED_ON`, `PROGRESSIVE_LED_OFF`, `SEQUENCES`, `MAIN_LOOP`

## Variables (según consigna)

| Variable | Dirección |
|----------|-----------|
| DELAY1_Init | 0x20 |
| DELAY2_Init | 0x21 |
| DELAY3_Init | 0x22 |
| DELAY1 | 0x23 |
| DELAY2 | 0x24 |
| DELAY3 | 0x25 |
| COUNTER_LED | 0x26 |
| COUNTER_SEQUENCES | 0x27 |

## Archivos de la carpeta

- `TP2.asm` — código fuente del grupo (G6: Conde, Lauc, Bertalot, Lurgo, Goicoechea).

## Notas

- RLF/RRF usan el bit Carry: `SET FLAG C` antes de `LEDS_RLF`, `CLR FLAG C`
  antes de `LEDS_RRF`.
- `CFG_DELAY_x` solo carga los contadores; el retardo lo ejecuta `DELAY_3LOOP`.
- El tiempo de 200 ms del buzzer NO va dentro de `BUZZER_ON/OFF`, sino en la
  rutina que los usa (`BUZZER_BIP` con `CFG_DELAY_200ms`).
