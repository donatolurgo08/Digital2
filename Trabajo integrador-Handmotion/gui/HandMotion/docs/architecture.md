# Arquitectura general — HAND MOTION

## 1. Objetivo

Aplicación de escritorio (Python + PySide6) conectada a un PIC16F887. La GUI
recibe temperatura y eje X mediante el protocolo serie v1; la interpretación de
Y/Z y el reconocimiento de gestos se dejan para etapas posteriores.

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
| `sensors/` | Convertir X de mg a g; sensibilidad viene del firmware. | ninguna |
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
- Y/Z permanecen como campos reservados; el protocolo v1 transmite X, no Y/Z.

## 6. Dependencias

Ver `docs/dependencies.md`.

## 7. Estado de implementación

La conexión serial, el codec v1, el parser incremental con CRC-8, los comandos y
la visualización en vivo de temperatura/X están implementados. La GUI ofrece
PING, START/STOP, GET_STATUS, SET_THRESHOLD y SET_OFFSET. Pendientes: validar
con el PIC físico, confirmar niveles del adaptador, calibrar sensibilidad de X
y completar Y/Z y reconocimiento de gestos.

## 8. Protocolo PIC v1

La especificación compartida está en
[`../../../docs/comunicacion/protocolo.md`](../../../docs/comunicacion/protocolo.md).
La GUI recibe `DATA` (secuencia, °C, X en mg con signo, alarma), `STATUS` y
`ACK`; transmite PING, START, STOP, SET_THRESHOLD, GET_STATUS y SET_OFFSET.
El enlace es 9600-8N1. Las tramas se parsean con CRC-8 y pueden llegar divididas
en varios bloques del puerto serie.
