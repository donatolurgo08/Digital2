# Arquitectura general

## Propósito

HAND MOTION reconoce movimientos de la mano a partir de la señal analógica del
eje X de un acelerómetro ADXL335 (módulo LilyPad, alimentado a 3,3 V). Las
señales de los tres ejes pasan por amplificadores no inversores MCP6002 y llegan
al PIC16F887, que adquiere y procesa la señal y se comunica con una GUI de PC.
En forma independiente, el PIC mide temperatura con un LM35 conectado a AN0 y la
presenta localmente.

## Bloques funcionales

```text
LilyPad ADXL335 (3,3 V)
  X ── MCP6002 A ── AN1 ──┐
  Y ── MCP6002 B ── AN5   ├── ADC ── reconocimiento (X) ──┐
  Z ── MCP6002 A ── AN6 ──┘                               ├── EUSART / USB-TTL ── GUI PC
LM35 ── AN0 ────────────── ADC ── temperatura ───────────┤
                                                          └── tres displays multiplexados
                                                               LED rojo + buzzer si T > 40 °C
```

La GUI enviará parámetros/comandos acordados y mostrará movimientos reconocidos
e información de estado. La supervisión térmica no participa en el reconocimiento.

## Decisiones confirmadas

- Microcontrolador PIC16F887 y firmware Assembler con `pic-as` (XC8).
- Oscilador interno a **8 MHz** (`OSCCON = 0x70`, `FOSC = INTRC_NOCLKOUT`);
  configuration bits ya verificados en el DFP.
- Sensor: módulo LilyPad ADXL335 alimentado a **3,3 V** (no admite 5 V).
- Canales ADC asignados en la Rev D del esquema: **AN0 = LM35**, **AN1 = X**,
  **AN5 = Y**, **AN6 = Z**.
- Alcance de la primera versión: se adquiere y procesa **solo X**. Y y Z quedan
  cableados y se incorporarán si el tiempo lo permite.
- LM35 obligatoriamente en AN0.
- Tres displays de cátodo común multiplexados: dos dígitos de temperatura y un
  indicador de °C. Segmentos en RD0–RD7 (a, b, c, d, e, f, g, dp) y selección de
  dígitos en RC0–RC2 mediante Q1–Q3.
- LED rojo y buzzer activo simultáneos cuando T > 40 °C. LED1 en RA2, LED2 en
  RA5. El buzzer es un módulo de 3 terminales (VCC, GND, I/O): VCC a +5 V, GND
  a GND e I/O directo a RC3. No lleva Q4 ni R20.
- No se usará teclado matricial ni habrá etapa de potencia para actuadores externos.

## Pendientes de integración

Baud rate, protocolo GUI, parámetros, períodos de adquisición y criterios de
reconocimiento. También quedan pendientes los valores de R9–R19 y R21–R23 (segmentos,
bases de transistores, LED y pull-up de MCLR), que dependen de los componentes
reales. Ver
[`firmware/perifericos-pic.md`](firmware/perifericos-pic.md) y
[`comunicacion/README.md`](comunicacion/README.md).
