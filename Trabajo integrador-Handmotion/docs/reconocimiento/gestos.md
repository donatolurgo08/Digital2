# Reconocimiento de gestos

## Alcance inicial

El reconocimiento utilizará las señales de los tres ejes del MMA7361,
conectadas directamente a AN1 (X), AN5 (Y) y AN6 (Z), sin amplificadores. El
LM35 y la alarma térmica son funciones independientes.

Los gestos, umbrales y ejes efectivamente usados se definirán con mediciones del
módulo real. El firmware ahora muestrea X cada 20 ms (50 Hz); falta verificar el
período real en banco. Y/Z se incorporarán al muestreo periódico más adelante.

## Diseño pendiente

Definir los movimientos/comandos, procedimiento de calibración, filtros,
umbrales, histéresis y parámetros que podrá ajustar la GUI. El período de X ya
está fijado en 20 ms; las decisiones para Y/Z y el reconocimiento se establecerán
con mediciones del sensor real, sin suponer gestos ni valores.

La implementación deberá ser reproducible y documentar las limitaciones
observadas durante las pruebas.
