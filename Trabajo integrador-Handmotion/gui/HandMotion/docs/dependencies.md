# Dependencias — HAND MOTION

## Python

- Versión mínima: 3.10
- Entorno actual validado: 3.15 (wheels `cp310-abi3` compatibles)

## Runtime

| Paquete | Versión mínima | Uso |
|---|---|---|
| PySide6 | 6.6 | Interfaz gráfica (Qt) |
| pyserial | 3.5 | Comunicación serial |
| pyqtgraph | 0.13 | Gráficos en tiempo real |
| numpy | 1.26 | Procesamiento de señales |

## Desarrollo (opcional)

| Paquete | Versión mínima | Uso |
|---|---|---|
| pytest | 8 | Pruebas unitarias |
| ruff | 0.6 | Linting / formato |

## Instalación

```powershell
py -m pip install -r requirements.txt
```

## Notas

- PySide6 provee `pyside6-uic` y herramientas de diseño, no requeridas
  para el esqueleto.
- `pyserial` abre el enlace 9600-8N1 y la GUI sondea RX con un `QTimer` de 5 ms;
  el protocolo CRC-8 v1 está implementado en `communication/protocol.py`.
- `pytest` se necesita para ejecutar las pruebas unitarias del codec y parser.
