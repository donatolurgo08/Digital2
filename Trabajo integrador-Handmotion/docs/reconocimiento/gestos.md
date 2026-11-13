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

## Prototipo sintético de X

La GUI contiene un modelo de referencia Python (`logic/gesture_recognition.py`)
que clasifica una ventana por su media como `X_NEGATIVE`, `X_NEUTRAL` o
`X_POSITIVE`. Recibe los umbrales negativo y positivo como argumentos
obligatorios; no hay umbrales por defecto. Las pruebas usan ventanas y umbrales
artificiales solo para verificar la lógica, no como calibración ni criterio del
MMA7361 real. El modelo aún no está conectado a la interfaz ni portado al PIC.

El reconocimiento real queda pendiente de definir gestos/umbrales con
mediciones y, una vez aprobada la lógica, implementarla en Assembler para el PIC.
