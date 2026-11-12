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
Módulo MMA7361 (5 V→3,0/3,3 V a bordo)
  X ── AN1 ──┐
  Y ── AN5   ├── ADC ── filtrado/calibración ── reconocimiento ──┐
  Z ── AN6 ──┘                                                   ├── EUSART / USB-TTL ── GUI PC
LM35 ── AN0 ────────────── ADC ── temperatura ───────────────────┤
                                                                 └── tres displays multiplexados
                                                                      LED rojo + buzzer si T > 40 °C
```

El protocolo serie v1 define comandos de configuración y transmite temperatura,
eje X y alarma; la GUI está integrada. Y/Z y los gestos se incorporarán después.
La supervisión térmica no participa en el reconocimiento.

## Decisiones confirmadas

- Microcontrolador PIC16F887 y firmware Assembler con `pic-as` (XC8).
- Oscilador interno a **8 MHz** (`OSCCON = 0x70`, `FOSC = INTRC_NOCLKOUT`);
  configuration bits ya verificados en el DFP.
- Sensor: módulo **MMA7361** de tres ejes, salidas analógicas, rango inicial de
  ±1,5 g (sensibilidad nominal 800 mV/g). Módulo de 2×5 pines con regulador U2
  (LP2985-3V) y jumper J1 del módulo: se alimenta con **+5 V en el pin 5V**
  (jumper abierto); el pin 3V3 es la salida del regulador (3,0 o 3,3 V) y
  alimenta Sleep. Los pines GS/ST/SLP son de 3 V. No se usan amplificadores
  operacionales.
- Canales ADC asignados en la Rev E del esquema: **AN0 = LM35**, **AN1 = X**,
  **AN5 = Y**, **AN6 = Z**, todos directos. Referencia `VREF+ = VDD`,
  `VREF- = VSS`; RA3/AN3 queda libre. Decisión del 2026-11-12: se mantiene
  este mapeo (Y/Z no pasan a AN2/AN3 porque RA2 es LED1).
- Alcance de la primera versión: se adquieren los tres ejes; el algoritmo de
  reconocimiento y los gestos se definen con mediciones reales. La conversión
  de X a mg usa offset y sensibilidad nominales hasta calibrar.
- LM35 obligatoriamente en AN0.
- Tres displays rojos de **cátodo común** multiplexados: dos dígitos de temperatura
  y una `C` estándar. Segmentos en RD0–RD7 (a, b, c, d, e, f, g, dp), activos
  en alto; RC0–RC2 activan Q1–Q3 BC337 como selectores de cátodo lado bajo.
  R17–R19 = 330 Ω, R21–R22 = 220 Ω y R23 = 10 kΩ. R9–R16 tienen 220 Ω como
  candidato para cátodo común; confirmar con Vf/VOH y corriente en banco.
- LED rojo y buzzer activo simultáneos cuando T > 40 °C. LED1 en RA2, LED2 en
  RA5. El buzzer es un módulo MDU1095 de 3 terminales (VCC, GND, I/O): VCC a
  +5 V, GND a GND e I/O directo a RC3. No lleva Q4 ni R20. Se activa en bajo:
  RC3 alto en reposo y bajo durante la alarma.
- Reserva de carga en los rieles: C10 = 220 µF en +5 V y C11 = 10 µF en +3V3,
  además de los 100 nF de desacople. El ADC usa `VREF+ = VDD`, así que los
  pulsos de 80 mA del multiplexado no deben mover el riel.
- No se usará teclado matricial ni habrá etapa de potencia para actuadores externos.

## Pendientes de integración

Probar la comunicación de la GUI con el PIC real, validar el muestreo X de 20 ms,
y definir filtros y criterios de reconocimiento para gestos y el muestreo futuro
de Y/Z. También quedan pendientes la verificación de R9–R16 (150 Ω
provisionales), la alimentación y el patillaje del MMA7361, y la calibración de
offset/sensibilidad con el módulo real. Las
resistencias de base (R17–R19), LED (R21–R22) y MCLR (R23) ya están calculadas. Ver
[`firmware/perifericos-pic.md`](firmware/perifericos-pic.md) y
[`comunicacion/README.md`](comunicacion/README.md).
