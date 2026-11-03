# Reconocimiento de gestos

## Alcance inicial

El reconocimiento utilizará exclusivamente la salida X del ADXL335 del módulo
GY-61. Los ejes Y y Z quedan fuera de la primera versión. El LM35 y la alarma
térmica son funciones independientes.

## Diseño pendiente

Definir los movimientos/comandos, período de muestreo, procedimiento de
calibración, filtros, umbrales, histéresis y parámetros que podrá ajustar la GUI.
Los criterios se establecerán con mediciones del sensor real; no se fijan
valores ni gestos por suposición.

La implementación deberá ser reproducible y documentar las limitaciones
observadas durante las pruebas.
