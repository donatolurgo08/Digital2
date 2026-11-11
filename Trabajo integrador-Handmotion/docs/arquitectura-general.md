# Arquitectura general

## Propósito

HAND MOTION reconoce movimientos de la mano a partir de las señales analógicas de
un acelerómetro MMA7361 de tres ejes (módulo con salidas analógicas). Las
salidas X, Y y Z se conectan **directamente** al ADC del PIC16F887, sin
amplificadores operacionales; el filtrado y la calibración se hacen en software.
El PIC adquiere y procesa las señales y se comunica con una GUI de PC. En forma
independiente, mide temperatura con un LM35 conectado a AN0 y la presenta
localmente.

## Bloques funcionales

```text
Módulo MMA7361 (3,3 V)
  X ── AN1 ──┐
  Y ── AN5   ├── ADC ── filtrado/calibración ── reconocimiento ──┐
  Z ── AN6 ──┘                                                   ├── EUSART / USB-TTL ── GUI PC
LM35 ── AN0 ────────────── ADC ── temperatura ───────────────────┤
                                                                 └── tres displays multiplexados
                                                                      LED rojo + buzzer si T > 40 °C
```

La GUI enviará parámetros/comandos acordados y mostrará movimientos reconocidos
e información de estado. La supervisión térmica no participa en el reconocimiento.

## Decisiones confirmadas

- Microcontrolador PIC16F887 y firmware Assembler con `pic-as` (XC8).
- Oscilador interno a **8 MHz** (`OSCCON = 0x70`, `FOSC = INTRC_NOCLKOUT`);
  configuration bits ya verificados en el DFP.
- Sensor: módulo **MMA7361** de tres ejes, salidas analógicas, rango inicial de
  ±1,5 g (sensibilidad nominal 800 mV/g). Alimentación y patillaje del módulo
  pendientes de verificar. No se usan amplificadores operacionales.
- Canales ADC asignados en la Rev E del esquema: **AN0 = LM35**, **AN1 = X**,
  **AN5 = Y**, **AN6 = Z**, todos directos. Referencia `VREF+ = VDD`,
  `VREF- = VSS`; RA3/AN3 queda libre.
- Alcance de la primera versión: se adquieren los tres ejes; el algoritmo de
  reconocimiento y los gestos se definen con mediciones reales. La conversión
  de X a mg usa offset y sensibilidad nominales hasta calibrar.
- LM35 obligatoriamente en AN0.
- Tres displays rojos de **ánodo común** multiplexados: dos dígitos de temperatura
  y una `C` estándar. Segmentos en RD0–RD7 (a, b, c, d, e, f, g, dp), activos
  en bajo; selección en RC0–RC2 mediante Q1–Q3 BC337, activos en alto.
  La propuesta de Q1–Q3 como seguidores de emisor del lado alto tiene una caída
  aproximada VBE; el brillo y la corriente siguen pendientes de validar en banco.
  R17–R19 = 330 Ω, R21–R22 = 220 Ω y R23 = 10 kΩ; el cálculo está en la nota
  6.14 del netlist. R9–R16 = 150 Ω es provisional y se confirma midiendo Vf.
- LED rojo y buzzer activo simultáneos cuando T > 40 °C. LED1 en RA2, LED2 en
  RA5. El buzzer es un módulo de 3 terminales (VCC, GND, I/O): VCC a +5 V, GND
  a GND e I/O directo a RC3. No lleva Q4 ni R20.
- No se usará teclado matricial ni habrá etapa de potencia para actuadores externos.

## Pendientes de integración

Baud rate, protocolo GUI, parámetros, períodos de adquisición y criterios de
reconocimiento. También quedan pendientes la verificación de R9–R16 (150 Ω
provisionales), la alimentación y el patillaje del MMA7361, y la calibración de
offset/sensibilidad con el módulo real. Las resistencias de base (R17–R19),
LED (R21–R22) y MCLR (R23) ya están calculadas. Ver
[`firmware/perifericos-pic.md`](firmware/perifericos-pic.md) y
[`comunicacion/README.md`](comunicacion/README.md).
