"""Estado global de la aplicación (fuente única de verdad).

Se expone mediante señales de Qt para que la UI se actualice sin acoplarse
a los módulos de negocio.
"""

from __future__ import annotations

from dataclasses import dataclass

from PySide6.QtCore import QObject, Signal


@dataclass
class AppStateData:
    """Datos crudos del estado actual del sistema."""

    connected: bool = False
    temperature_c: float | None = None
    accel_x: float | None = None
    # Reservado para futuros ejes Y/Z (DEC-001).
    accel_y: float | None = None
    accel_z: float | None = None
    alarm_active: bool = False
    gesture: str | None = None


class AppState(QObject):
    """Estado observable de la aplicación.

    Emite señales cuando cambian los valores relevantes para la UI.
    """

    connection_changed = Signal(bool)
    temperature_changed = Signal(float)
    accel_changed = Signal(float)  # eje X en la primera etapa
    alarm_changed = Signal(bool)
    gesture_changed = Signal(str)

    def __init__(self) -> None:
        super().__init__()
        self._data = AppStateData()

    @property
    def data(self) -> AppStateData:
        return self._data

    def set_connected(self, value: bool) -> None:
        self._data.connected = value
        self.connection_changed.emit(value)

    # Los demás setters se implementarán junto con la integración
    # de comunicación y sensores (tareas posteriores).