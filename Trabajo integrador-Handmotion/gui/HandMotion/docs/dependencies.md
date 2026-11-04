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
- La comunicación serial real se implementará cuando se defina el protocolo
  (T-03); hasta entonces `pyserial` se mantiene como dependencia preparada.