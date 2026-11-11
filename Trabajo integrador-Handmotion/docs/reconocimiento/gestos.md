# Reconocimiento de gestos

## Alcance inicial

El reconocimiento utilizará las señales de los tres ejes del MMA7361,
conectadas directamente a AN1 (X), AN5 (Y) y AN6 (Z), sin amplificadores. El
LM35 y la alarma térmica son funciones independientes.

Los gestos, umbrales y ejes efectivamente usados se definirán con mediciones del
módulo real. La primera versión puede apoyarse en un solo eje, pero la
adquisición ya cubre X, Y y Z.

## Diseño pendiente

Definir los movimientos/comandos, período de muestreo, procedimiento de
calibración, filtros, umbrales, histéresis y parámetros que podrá ajustar la GUI.
Los criterios se establecerán con mediciones del sensor real; no se fijan
valores ni gestos por suposición.

La implementación deberá ser reproducible y documentar las limitaciones
observadas durante las pruebas.
