"""Manejo del puerto serie (pyserial) para la comunicación con el PIC.

Expone una API simple para listar puertos y abrir/cerrar la conexión, y
notifica cambios mediante una señal de Qt. La lectura de tramas y el protocolo
se integrarán cuando se defina T-03.
"""

from __future__ import annotations

from dataclasses import dataclass

import serial
from serial.tools import list_ports
from PySide6.QtCore import QObject, Signal


@dataclass(frozen=True)
class PortInfo:
    """Identificación de un puerto serie disponible."""

    device: str
    description: str


class SerialPortManager(QObject):
    """Administra la conexión serie sin bloquear la UI."""

    connection_changed = Signal(bool)
    error_occurred = Signal(str)

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._serial: serial.Serial | None = None

    @property
    def connected(self) -> bool:
        return self._serial is not None and self._serial.is_open

    def refresh_ports(self) -> list[PortInfo]:
        """Devuelve los puertos serie disponibles en el sistema."""
        ports: list[PortInfo] = []
        for port in list_ports.comports():
            description = port.description or "Puerto serie"
            ports.append(PortInfo(device=port.device, description=description))
        return ports

    def open(self, device: str, baud_rate: int) -> bool:
        """Abre el puerto indicado. Devuelve True si quedó conectado."""
        if self.connected:
            self.close()

        try:
            self._serial = serial.Serial(
                port=device,
                baudrate=baud_rate,
                timeout=0.1,
                write_timeout=0.5,
            )
        except (serial.SerialException, ValueError, OSError) as exc:
            self._serial = None
            self.error_occurred.emit(f"No se pudo abrir {device}: {exc}")
            self.connection_changed.emit(False)
            return False

        self.connection_changed.emit(True)
        return True

    def close(self) -> None:
        """Cierra la conexión activa, si existe."""
        if self._serial is not None and self._serial.is_open:
            self._serial.close()
        self._serial = None
        self.connection_changed.emit(False)
