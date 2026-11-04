# HAND MOTION

Aplicación de escritorio para supervisar temperatura (LM35) y reconocer
movimientos (ADXL335) comunicándose con un PIC16F887 vía EUSART/USB-TTL.

## Ejecutar

Hacé doble clic en `run_hand_motion.bat`. La primera vez crea `.venv` e instala
las dependencias de `requirements.txt`; luego inicia la GUI usando ese entorno.

Para ejecutarla manualmente después de preparar el entorno:

```powershell
.\.venv\Scripts\python.exe -m hand_motion
```

## Estructura

Ver `docs/architecture.md`.
