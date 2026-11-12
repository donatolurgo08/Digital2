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
| 1 | Módulo acelerómetro Candy-Ho con MMA7361L | Salidas X/Y/Z directas al ADC. La publicación declara VCC de 3–5 V; el diseño lo alimenta a +3V3. Confirmar serigrafía/orden del conector y puentes GS/SLP antes del dibujo físico. |
| 1 | LM35 | Temperatura. Salida a AN0. Alimentación 4–30 V; en este circuito, 5 V. |
| 3 | Capacitores de filtrado, 100 nF | Uno por eje, de la entrada a GND. |
| 3 | Displays rojos de 7 segmentos, ánodo común | Decenas, unidades y `C` estándar. Verificar patillaje y especificación de corriente. |
| 3 | Transistores NPN BC337 | Seguidores de emisor para ánodos comunes. Pinout de la imagen: C-B-E de izquierda a derecha mirando la cara plana; confirmar el lote antes de soldar. |
| 1 | Módulo buzzer activo 3,3–5 V, 3 pines rotulados (GND, I/O, VCC) | La imagen indica trigger activo-bajo; firmware RC3 actualizado. Confirmar corriente en banco antes de conectarlo. El módulo incluye driver. |
| 2 | LED rojos | Alarma visual. |
| 3 | Resistencias de 330 Ω, 1/4 W | Base de Q1–Q3 (R17–R19), para 10 mA de pico por segmento. |
| 2 | Resistencias de 220 Ω, 1/4 W | Limitadoras de LED1 y LED2 (R21–R22), ~11 mA. |
| 1 | Resistencia de 10 kΩ, 1/4 W | Pull-up de MCLR (R23). |
| 8 | Resistencias de 150 Ω, 1/4 W (provisional) | Segmentos R9–R16; ≈10 mA por segmento. Confirmar midiendo Vf y el ánodo real. |
| 1 | Capacitor electrolítico 220 µF / 16 V | Reserva del riel de 5 V (C10), junto al PIC y los displays. Respetar polaridad. |
| 1 | Capacitor 10 µF / 10 V | Reserva del riel de 3,3 V (C11), junto al módulo acelerómetro. |
| 2 | Capacitores cerámicos de 100 nF | Desacople de las dos alimentaciones del PIC. |
| 1 | Fuente/cable de entrada para PS1 | Conectar solo al puerto que la serigrafía/manual identifique como entrada (la foto muestra DC-IN y conectores USB). Confirmar tensión y polaridad. |
| 1 | Módulo de alimentación de protoboard PS1 | Tiene dos selectores de rail independientes; ajustar uno a 5 V y otro a 3,3 V. Confirmar cuál de sus conectores es entrada antes de alimentar. |
| 1 | Conversor USB–TTL, header de 5 pines | Etiquetas 3V3, TXD, RXD, GND, +5V. Usar TXD/RXD cruzados y GND; aislar 3V3/+5V y verificar niveles lógicos. |
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
