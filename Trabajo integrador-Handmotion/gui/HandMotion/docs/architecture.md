# Arquitectura general — HAND MOTION

## 1. Objetivo

Definir la estructura modular de la aplicación de escritorio (Python + PySide6)
que se comunicará con un PIC16F887. La arquitectura separa interfaz,
comunicación, sensores, procesamiento y lógica, y permite incorporar en el
futuro comunicación serial real, lecturas del LM35, lecturas del acelerómetro,
gráficos en tiempo real y sistema de alarmas.

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
| `core/controller.py` | Orquestar comunicación, sensores, lógica y estado. | communication, sensors, processing, logic, state |
| `core/state.py` | Fuente única de verdad; emite señales Qt. | solo Qt |
| `communication/serial_port.py` | Abrir/cerrar puerto, leer/escribir bytes, señales. | pyserial, Qt |
| `communication/protocol.py` | Codificar/decodificar tramas (funciones puras). | ninguna |
| `sensors/` | Convertir valores crudos a unidades físicas. | ninguna |
| `processing/` | Filtrado, suavizado, features. | NumPy |
| `logic/` | Alarmas, gestos, calibración. | sensors, processing |
| `config.py` | Constantes y defaults. | ninguna |

## 4. Flujo de datos

Adquisición (PIC → GUI):

    PIC → USB-TTL → serial_port (bytes, hilo secundario)
      → protocol.decode (trama) → sensors (°C, g)
      → processing (filtrado) → logic (alarmas/gestos)
      → AppState (actualización) → señales Qt → ui

Configuración (GUI → PIC):

    ui (acción) → controller → protocol.encode (comando)
      → serial_port.write → PIC

## 5. Principios

- La UI no accede directamente al serial ni a los sensores.
- Los módulos inferiores (`sensors`, `processing`, `logic`, `protocol`) son
  puros (sin Qt ni I/O), testeables.
- El acoplamiento se hace con señales/slots de Qt o callbacks.
- Los ejes Y/Z se incorporarán agregando campos a `accelerometer.py` y
  `state.py` sin tocar el resto.

## 6. Dependencias

Ver `docs/dependencies.md`.

## 7. Estado de implementación

Esqueleto creado. Comunicación serial, lectura de sensores, gráficos y
reconocimiento de gestos se implementarán en tareas posteriores. El protocolo
definitivo está pendiente (T-03).