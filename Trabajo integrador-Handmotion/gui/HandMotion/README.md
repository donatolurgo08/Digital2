# HAND MOTION

Aplicación de escritorio para recibir temperatura y eje X de un MMA7361 desde
un PIC16F887 vía EUSART/USB-TTL. El reconocimiento de gestos y la comunicación
de Y/Z quedan pendientes; no se muestran ejes que el protocolo v1 no transmite.

La GUI implementa el protocolo binario v1 `AA 55 / LEN / TIPO / DATOS / CRC-8`
a 9600 Bd, 8N1. Permite PING, START/STOP, consultar estado, fijar el umbral de
alarma y calibrar el offset de X. La sensibilidad del acelerómetro sigue siendo
nominal hasta medir el módulo real.

## Ejecutar

Hacé doble clic en `run_hand_motion.bat`. La primera vez crea `.venv` e instala
las dependencias de `requirements.txt`; luego inicia la GUI usando ese entorno.

Para ejecutarla manualmente después de preparar el entorno:

```powershell
.\.venv\Scripts\python.exe -m hand_motion
```

## Estructura

Ver `docs/architecture.md`.
