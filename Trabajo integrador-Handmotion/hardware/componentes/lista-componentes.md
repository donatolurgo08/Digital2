# Lista de materiales — HAND MOTION

Componentes definidos para el prototipo. El conexionado está en
[`../esquematico/conexiones.txt`](../esquematico/conexiones.txt). R17–R19,
R21–R22 y R23 están calculadas; R9–R16 tienen un valor provisional de 150 Ω
que se confirma midiendo el display.

## Circuito

| Cant. | Componente | Función |
|---:|---|---|
| 1 | PIC16F887, PDIP-40 | Control, ADC, displays, alarmas y EUSART. |
| 1 | Zócalo DIP-40 | Montaje del PIC. |
| 1 | Módulo acelerómetro MMA7361, 3 ejes | Ejes X, Y y Z con salidas analógicas directas al ADC. Verificar alimentación y patillaje del módulo. |
| 1 | LM35 | Temperatura. Salida a AN0. Alimentación 4–30 V; en este circuito, 5 V. |
| 3 | Capacitores de filtrado, 100 nF | Uno por eje, de la entrada a GND. |
| 3 | Displays rojos de 7 segmentos, ánodo común | Decenas, unidades y `C` estándar. Verificar patillaje y especificación de corriente. |
| 3 | Transistores NPN BC337 | Selectores como seguidores de emisor para los ánodos comunes. Verificar margen de tensión, corriente y patillaje. |
| 1 | Módulo buzzer activo 3,3–5 V, 3 terminales (VCC, GND, I/O) | Alarma acústica. El I/O va directo a RC3; el módulo incluye el driver. |
| 2 | LED rojos | Alarma visual. |
| 3 | Resistencias de 330 Ω, 1/4 W | Base de Q1–Q3 (R17–R19), para 10 mA de pico por segmento. |
| 2 | Resistencias de 220 Ω, 1/4 W | Limitadoras de LED1 y LED2 (R21–R22), ~11 mA. |
| 1 | Resistencia de 10 kΩ, 1/4 W | Pull-up de MCLR (R23). |
| 8 | Resistencias de 150 Ω, 1/4 W (provisional) | Segmentos R9–R16; ≈10 mA por segmento. Confirmar midiendo Vf y el ánodo real. |
| 1 | Capacitor electrolítico 220 µF / 16 V | Reserva del riel de 5 V (C10), junto al PIC y los displays. Respetar polaridad. |
| 1 | Capacitor 10 µF / 10 V | Reserva del riel de 3,3 V (C11), junto al módulo acelerómetro. |
| 2 | Capacitores cerámicos de 100 nF | Desacople de las dos alimentaciones del PIC. |
| 1 | Batería de 9 V | Alimentación del módulo de protoboard. |
| 1 | Módulo de alimentación de protoboard | Entrega 5 V y 3,3 V, con GND común. |
| 1 | Conversor USB–TTL | Enlace con la PC. No es RS-232 y su VCC no se une al riel. |
| 1 | Programador PICkit | Carga del firmware por ICSP. |

## Montaje disponible

Protoboard, cables Dupont y multímetro.

## Agregar al armar, aunque no estén en la lista inicial

- Capacitor de 100 nF entre +3V3 y GND, junto al módulo acelerómetro.
- Capacitor de 100 nF entre `+VS` y GND del LM35.

Los capacitores de reserva C10 (220 µF) y C11 (10 µF) no son opcionales: sostienen
el riel durante los pulsos del multiplexado y evitan que el ADC lea de menos.

No hace falta cristal externo: el PIC usa su oscilador interno a 8 MHz. Los
configuration bits están definidos en el firmware.
