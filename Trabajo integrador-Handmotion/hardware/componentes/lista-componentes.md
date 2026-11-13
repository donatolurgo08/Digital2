# Lista de materiales — HAND MOTION

Componentes definidos para el prototipo. El conexionado está en
[`../esquematico/conexiones.txt`](../esquematico/conexiones.txt). Quedan
definidas: R9–R16 adoptadas y R17–R19, R21–R22 y R23 calculadas; conviene
confirmar en banco Vf/VOH, brillo y saturación antes de soldar.

## Circuito

| Cant. | Componente | Función |
|---:|---|---|
| 1 | PIC16F887, PDIP-40 | Control, ADC, displays, alarmas y EUSART. |
| 1 | Zócalo DIP-40 | Montaje del PIC. |
| 1 | Módulo acelerómetro MMA7361L, 2×5 pines | Salidas X/Y/Z directas al ADC. Trae regulador U2 (LP2985-3V) y jumper J1 del módulo: alimentar por 5V con el jumper abierto, o por 3V3 con el jumper puenteado. No usar ambas entradas. Los pines GS/ST/SLP son de 3 V. Confirmar la tensión real del pin 3V3. |
| 1 | LM35 | Temperatura. Salida a AN0. Alimentación 4–30 V; en este circuito, 5 V. |
| 3 | Capacitores de filtrado, 3,3 nF | Uno por eje, de la salida X/Y/Z a GND. Valor recomendado por la datasheet del MMA7361L. |
| 3 | Displays rojos de 7 segmentos, cátodo común | Decenas, unidades y `C` estándar. Patillaje físico adoptado: 1=e, 2=d, 3=CC, 4=c, 5=dp, 6=b, 7=a, 8=CC, 9=f, 10=g; contrastar con datasheet o multímetro antes de soldar. |
| 3 | Transistores NPN BC337 | Selectores de cátodo por lado bajo. Lote verificado por el usuario: todos C-B-E, cara plana al frente. No invertir colector y emisor. |
| 1 | Módulo buzzer activo MDU1095 (3,5–5,5 V, 3 pines) | Alimentación 5 V; consumo del módulo 30 mA, 2500 Hz, activo-bajo. El módulo incluye driver. Confirmar modelo y corriente de I/O en banco. |
| 2 | LED rojos | Alarma visual. |
| 3 | Resistencias de 330 Ω, 1/4 W | Base de Q1–Q3 (R17–R19), para 10 mA de pico por segmento. |
| 2 | Resistencias de 220 Ω, 1/4 W | Limitadoras de LED1 y LED2 (R21–R22), ~11 mA. |
| 1 | Resistencia de 10 kΩ, 1/4 W | Pull-up de MCLR (R23). |
| 8 | Resistencias de segmento R9–R16 | 220 Ω adoptado para cátodo común (~10 mA con VOH/Vf/VCEsat supuestos, netlist 6.5). Confirmar Vf/VOH y brillo en banco. |
| 1 | Capacitor electrolítico 220 µF / 16 V | Reserva del riel de 5 V (C10), junto al PIC y los displays. Respetar polaridad. |
| 1 | Capacitor 10 µF / 10 V | Reserva del riel de 3,3 V (C11). Queda como reserva si MOD1 se alimenta por 5V; útil si se elige la alternativa por 3V3. |
| 2 | Capacitores cerámicos de 100 nF | Desacople de las dos alimentaciones del PIC. |
| 1 | Fuente regulada de 9 V DC para PS1 | Entrada por el jack DC-IN. Confirmar polaridad del jack y que el módulo admita 9 V DC antes de energizar. Usar fuente DC regulada, nunca AC. |
| 1 | Módulo de alimentación de protoboard HW-131 / MB102 (PS1) | Dos selectores de rail independientes; ajustar uno a 5 V y otro a 3,3 V. Entrada DC-IN de 9 V DC; el USB-A hembra es salida de 5 V y no se usa como entrada. No conectar DC-IN y USB a la vez. |
| 1 | Conversor USB–TTL, header de 5 pines | Etiquetas 3V3, TXD, RXD, GND, +5V. Usar TXD/RXD cruzados y GND; aislar 3V3/+5V y verificar que TXD/RXD sean TTL de 5 V. |
| 1 | Programador PICkit | Carga del firmware por ICSP. |

## Montaje disponible

Protoboard, cables Dupont y multímetro.

## Agregar al armar, aunque no estén en la lista inicial

- C9 = 100 nF entre +3V3 y GND: reserva del riel de 3,3 V, porque MOD1 se
  alimenta por 5 V en la conexión recomendada.
- C8 = 100 nF entre `+VS` y GND del LM35.

C10 (220 µF) no es opcional: sostiene el riel de 5 V durante los pulsos del
multiplexado y evita que el ADC lea de menos. C11 (10 µF) solo se usa si se
elige la alternativa de alimentar MOD1 por +3V3.

No hace falta cristal externo: el PIC usa su oscilador interno a 8 MHz. Los
configuration bits están definidos en el firmware.
