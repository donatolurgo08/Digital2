# D-01 — Investigación de temporizadores del PIC16F887

**Responsable:** Donato Lurgo  
**Estado:** TIMER0/TIMER1 configurados en firmware; validar tiempos en hardware

**Base temporal:** `TOSC=1/FOSC`; `TCY=4/FOSC`.

`FOSC = 8 MHz` está confirmado. TIMER0 usa el tick nominal aceptado de 1 ms;
TIMER1 conserva el período nominal de 1 ms para el barrido de displays.

## TIMER0

Temporizador/contador de 8 bits (`TMR0`). En modo temporizador usa `FOSC/4`,
seleccionado con `OPTION_REG.T0CS=0`. El prescaler se comparte con WDT:
`OPTION_REG.PSA=0` lo asigna a TIMER0 y `PS<2:0>` selecciona 1:2–1:256. No tiene
postscaler propio.

- **Registros/bits:** `TMR0`; `OPTION_REG.T0CS`, `T0SE`, `PSA`, `PS<2:0>`;
  `INTCON.T0IF` y `T0IE`.
- **Desborde:** `0xFF → 0x00`; `T0IF` se activa y se limpia por software. Con
  precarga `N`, el intervalo nominal interno es
  `((256−N) × prescaler × TCY)`. Escribir `TMR0` inhibe el conteo durante dos
  ciclos y limpia el prescaler si está asignado a TIMER0; considerar esto al
  ajustar el período.
- **Aplicación actual:** ISR cada tick nominal de 1 ms; cada 20 ticks levanta
  una bandera para muestrear AN1/X cada 20 ms (50 Hz). El ADC y la conversión se
  hacen en foreground, no en la ISR.

## TIMER1

Temporizador/contador de 16 bits (`TMR1H:TMR1L`). Con `T1CON.TMR1CS=0` usa
`FOSC/4`; `T1CKPS<1:0>` selecciona prescaler 1:1, 1:2, 1:4 o 1:8. También admite
reloj externo, no elegido para esta propuesta.

- **Registros/bits:** `TMR1H`, `TMR1L`, `T1CON.TMR1ON`, `TMR1CS`, `T1CKPS`;
  bandera `PIR1.TMR1IF`, habilitación `PIE1.TMR1IE`.
- **Desborde:** `0xFFFF → 0x0000`; con precarga `N`, el intervalo nominal interno
  es `((65536−N) × prescaler × TCY)`. Para interrupción: limpiar `TMR1IF` y
  habilitar `TMR1IE`, `INTCON.PEIE` e `INTCON.GIE`.
- **Aplicación actual:** temporiza el barrido de los tres displays con polling
  de `TMR1IF`, activando un dígito por evento.

## TIMER2

Temporizador de 8 bits con registro de período `PR2`; usa `FOSC/4`.
`T2CON.T2CKPS<1:0>` selecciona prescaler 1:1, 1:4 o 1:16. Al coincidir `TMR2`
con `PR2`, se reinicia el contador y avanza el postscaler (1:1–1:16).

- **Registros/bits:** `TMR2`, `PR2`, `T2CON.TMR2ON`, `T2CKPS<1:0>` y
  `TOUTPS<3:0>`; bandera `PIR1.TMR2IF`, habilitación `PIE1.TMR2IE`.
- **Período de interrupción:**
  `((PR2+1) × prescaler × postscaler × TCY)`. Para interrupción: limpiar
  `TMR2IF` y habilitar `TMR2IE`, `INTCON.PEIE` e `INTCON.GIE`.
- **Aplicación propuesta:** reservarlo al inicio y evaluar su uso si TIMER0 y
  TIMER1 quedan asignados a ADC y displays.

## Pendiente de definir

- Medir el período y jitter reales de TIMER0/TIMER1; el cálculo es nominal y
  debe verificarse con el hardware.
- Definir la cadencia para Y/Z y reconocimiento de gestos a partir de mediciones.
- Decidir si TIMER2 queda reservado o se asigna a otra tarea.

## Fuente

Microchip, *PIC16F882/883/884/886/887 Data Sheet*, DS41291D, secciones 5.0–7.0,
tablas de registros asociadas, pp. 73–82. [PDF oficial](https://ww1.microchip.com/downloads/en/DeviceDoc/41291D.pdf).
