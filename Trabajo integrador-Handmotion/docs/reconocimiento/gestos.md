# Reconocimiento de gestos

## Alcance implementado en la GUI

La GUI reconoce **inclinaciones sostenidas por eje** con las señales X/Y/Z del
MMA7361 (AN1/AN5/AN6). El clasificador vive en
`gui/HandMotion/hand_motion/logic/gesture_recognition.py` y se usa desde la
sección **Reconocimiento**:

- Promedia una ventana de N muestras (5 por defecto) para reducir ruido.
- Compara cada eje contra un **reposo capturado** por el usuario.
- El eje con la mayor desviación absoluta define el gesto: `X+`, `X-`, `Y+`,
  `Y-`, `Z+`, `Z-`; si ninguno supera su umbral, el resultado es `REPOSO`.
- Exige varias clasificaciones consecutivas iguales (3 por defecto) antes de
  confirmar un cambio.
- Con DATA v2 (sin Z) solo se evalúan X e Y.

Los umbrales por eje, la ventana y el reposo se ajustan desde la GUI y viven
solo en memoria. Los valores iniciales (0,25 g) son **provisionales de
interfaz**, no una calibración del sensor. El reposo se captura con el botón
**Capturar reposo** o se ingresa manualmente.

## Limitaciones

- `Z+` requiere que el reposo deje margen en Z; con el sensor horizontal
  (Z ≈ 1 g) solo es alcanzable con inversión o aceleración dinámica.
- La orientación de montaje del módulo no está medida. El reposo capturado
  absorbe el offset, pero la sensibilidad real de cada eje sigue pendiente.
- El firmware no implementa gestos: solo transmite X/Y/Z. El reconocimiento
  corre en la GUI.
- No hay calibración física ni validación en banco de umbrales.

## Pendiente

- Medir el período/jitter real del muestreo y la sensibilidad de X/Y/Z.
- Calibrar umbrales con el módulo real y registrar los valores usados.
- Decidir si el reconocimiento se porta al PIC en Assembler y con qué
  protocolo/comandos.
