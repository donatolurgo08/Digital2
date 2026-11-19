# HAND MOTION

Aplicación de escritorio para recibir temperatura y los ejes X/Y/Z de un MMA7361
desde un PIC16F887 vía EUSART/USB-TTL. La sección **Reconocimiento** clasifica
inclinaciones por eje (X+/X-/Y+/Y-/Z+/Z-/REPOSO) con umbrales, ventana y reposo
ajustables. El firmware todavía solo transmite las muestras; el reconocimiento
corre en la GUI y sus umbrales iniciales son provisionales.

La GUI acepta DATA de los protocolos v2 (X/Y) y v3 (X/Y/Z), con CRC-8, y mantiene
compatibilidad con STATUS, ACK y comandos a 9600 Bd, 8N1. Permite PING, START/STOP,
consultar estado, fijar el umbral de alarma y calibrar el offset de X. Las
aceleraciones se muestran en g nominales; Z sigue pendiente de calibración física.
La navegación incluye Dashboard, Adquisición, Reconocimiento y Configuración; no
hay sección Historial ni persistencia de sesiones. Configuración guarda localmente
con QSettings la tasa de simulación y los parámetros del reconocedor.

La aplicación abre en pantalla completa. Usá **F11** para alternar entre
pantalla completa y ventana; **Esc** sale de pantalla completa.

## Ejecutar

Hacé doble clic en `run_hand_motion.bat`. La primera vez crea `.venv` e instala
las dependencias de `requirements.txt`; luego inicia la GUI usando ese entorno.

Para ejecutarla manualmente después de preparar el entorno:

```powershell
.\.venv\Scripts\python.exe -m hand_motion
```

## Estructura

Ver `docs/architecture.md`.
