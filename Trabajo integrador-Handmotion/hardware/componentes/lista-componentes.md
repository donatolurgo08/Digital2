# Lista de materiales — HAND MOTION

Componentes definidos para el prototipo. El conexionado está en
[`../esquematico/conexiones.txt`](../esquematico/conexiones.txt). Las
resistencias todavía no tienen valor: no comprarlas por suposición.

## Circuito

| Cant. | Componente | Función |
|---:|---|---|
| 1 | PIC16F887, PDIP-40 | Control, ADC, displays, alarmas y EUSART. |
| 1 | Zócalo DIP-40 | Montaje del PIC. |
| 1 | Módulo LilyPad ADXL335 | Ejes X, Y y Z. Solo 3,3 V: no tiene regulador propio. |
| 1 | LM35 | Temperatura. Salida a AN0. Alimentación 4–30 V; en este circuito, 5 V. |
| 2 | MCP6002, DIP-8 | Acondicionamiento de X, Y y Z, más referencia. |
| 3 | Capacitores de filtrado, 100 nF | Uno por eje. |
| — | Resistencias de ganancia y referencia | Valores pendientes. |
| 3 | Displays de 7 segmentos, cátodo común | Decenas, unidades y símbolo °C. |
| 3 | Transistores NPN BC337 | Multiplexado de los cátodos. Verificar patillaje. |
| 1 | Módulo buzzer activo 3,3–5 V, 3 terminales (VCC, GND, I/O) | Alarma acústica. El I/O va directo a RC3; el módulo incluye el driver. |
| 2 | LED rojos | Alarma visual. |
| — | Resistencias de segmentos, LED y bases | Valores pendientes. |
| 2 | Capacitores cerámicos de 100 nF | Desacople de las dos alimentaciones del PIC. |
| 1 | Batería de 9 V | Alimentación del módulo de protoboard. |
| 1 | Módulo de alimentación de protoboard | Entrega 5 V y 3,3 V, con GND común. |
| 1 | Conversor USB–TTL | Enlace con la PC. No es RS-232 y su VCC no se une al riel. |
| 1 | Programador PICkit | Carga del firmware por ICSP. |

## Montaje disponible

Protoboard, cables Dupont y multímetro.

## Agregar al armar, aunque no estén en la lista inicial

- Resistencia de pull-up en `MCLR`, si el reset externo queda habilitado.
- Capacitor de 100 nF entre alimentación y GND de cada MCP6002.
- Capacitor de 100 nF entre +3V3 y GND, junto al módulo acelerómetro.
- Capacitor de 100 nF entre `+VS` y GND del LM35.

No hace falta cristal externo: el PIC usa su oscilador interno a 8 MHz. Los
configuration bits están definidos en el firmware.
