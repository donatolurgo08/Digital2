# Arquitectura general — HAND MOTION

## 1. Objetivo

Aplicación de escritorio (Python + PySide6) conectada a un PIC16F887. La GUI
acepta DATA de firmware v2 (ejes X/Y) y v3 (ejes X/Y/Z). En v2, Z se representa
como no disponible; el reconocimiento de gestos queda para una etapa posterior.

## 2. Estructura de directorios

```
HandMotion/
├── hand_motion/          # paquete principal
│   ├── __main__.py       # punto de entrada
│   ├── app.py            # bootstrap de QApplication
│   ├── config.py         # constantes y valores por defecto
│   ├── core/             # estado y orquestación
│   ├── communication/    # serial + protocolo
│   ├── sensors/          # modelos de sensores
│   ├── processing/       # procesamiento numérico (NumPy)
│   ├── logic/            # alarmas y reconocimiento de gestos
│   └── ui/               # interfaz PySide6 (solo presentación)
├── tests/                # pruebas de módulos puros
├── docs/                 # documentación
├── resources/            # íconos e imágenes
└── requirements.txt
```

## 3. Responsabilidades por módulo

| Módulo | Responsabilidad | Dependencias permitidas |
|---|---|---|
| `ui/` | Mostrar datos, capturar acciones, gráficos. Sin lógica de negocio. | `core` (vía señales) |
| `core/controller.py` | Enviar comandos y aplicar paquetes al estado. | communication, sensors, state |
| `core/state.py` | Fuente única de verdad; emite señales Qt. | Qt, modelos de protocolo |
| `communication/serial_port.py` | Abrir/cerrar 9600-8N1 y sondear RX cada 5 ms. | pyserial, Qt |
| `communication/protocol.py` | Codec binario, CRC-8 y parser incremental puro. | ninguna |
| `sensors/` | Convertir aceleraciones X/Y/Z disponibles de mg a g; sensibilidad viene del firmware. | ninguna |
| `processing/` | Filtrado, suavizado, features. | NumPy |
| `logic/` | Alarmas, gestos, calibración. | sensors, processing |
| `config.py` | Constantes y defaults. | ninguna |

## 4. Flujo de datos

Adquisición (PIC → GUI):

    PIC → USB-TTL → serial_port (sondeo no bloqueante)
      → FrameParser / CRC → controller → AppState → señales Qt → UI

Configuración (GUI → PIC):

    ui (acción) → controller → protocol.encode (comando)
      → serial_port.write → PIC

## 5. Principios

- La UI no accede directamente al serial ni a los sensores.
- El codec y parser (`communication/protocol.py`) y las conversiones de unidad
  (`sensors/`) son puros y testeables.
- El acoplamiento se hace con señales/slots de Qt o callbacks.
- DATA se decodifica según LEN: v2 contiene X/Y y v3 contiene X/Y/Z. La versión
  informada por STATUS se conserva por separado; DATA no depende de que STATUS
  haya llegado primero. Z queda como no disponible en v2.

## 6. Dependencias

Ver `docs/dependencies.md`.

## 7. Estado de implementación

La conexión serial, el codec v2/v3, el parser incremental con CRC-8, los comandos
y la visualización en vivo de temperatura/X/Y/Z están implementados. La GUI ofrece
PING, START/STOP, GET_STATUS, SET_THRESHOLD y SET_OFFSET. Hay un clasificador
Python de referencia probado con ventanas sintéticas de X; no está integrado a
la UI ni reemplaza el futuro reconocimiento Assembler del PIC. Pendientes:
validar con el PIC físico, calibrar los ejes X/Y/Z y definir los
criterios/implementación de gestos reales.

## 8. Protocolo PIC v2/v3

La especificación compartida está en
[`../../../docs/comunicacion/protocolo.md`](../../../docs/comunicacion/protocolo.md).
La GUI recibe DATA v2 con LEN=8 (secuencia, °C, X/Y con signo y flags) o DATA v3
con LEN=10 (los mismos campos más Z), además de STATUS y ACK. X/Y/Z se decodifican
como enteros signed little-endian en mg; Z es `None` cuando DATA usa v2. STATUS
informa la versión del firmware y no es requisito para decodificar DATA.

La GUI transmite PING, START, STOP, SET_THRESHOLD, GET_STATUS y SET_OFFSET. El
enlace es 9600-8N1. Las tramas se validan con CRC-8 y pueden llegar divididas en
varios bloques del puerto serie.
