"""Puerto serie USB-TTL con lectura incremental no bloqueante para la GUI."""

from __future__ import annotations

from dataclasses import dataclass

import serial
from serial.tools import list_ports
from PySide6.QtCore import QObject, QTimer, Signal

from hand_motion.communication.protocol import FrameParser, Packet


@dataclass(frozen=True)
class PortInfo:
    """Identificación de un puerto serie disponible."""

    device: str
    description: str


class SerialPortManager(QObject):
    """Abre 9600-8N1, sondea RX con QTimer y escribe tramas pequeñas."""

    connection_changed = Signal(bool)
    error_occurred = Signal(str)
    frame_received = Signal(object)

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._serial: serial.Serial | None = None
        self._parser = FrameParser()
        self._poll_timer = QTimer(self)
        self._poll_timer.setInterval(5)
        self._poll_timer.timeout.connect(self._poll)

    @property
    def connected(self) -> bool:
        return self._serial is not None and self._serial.is_open

    @property
    def parser(self) -> FrameParser:
        return self._parser

    def refresh_ports(self) -> list[PortInfo]:
        """Devuelve los puertos serie disponibles en el sistema."""
        ports: list[PortInfo] = []
        for port in list_ports.comports():
            ports.append(
                PortInfo(device=port.device, description=port.description or "Puerto serie")
            )
        return ports

    def open(self, device: str, baud_rate: int = 9600) -> bool:
        """Abre el puerto según el formato de enlace confirmado, 9600-8N1."""
        if baud_rate != 9600:
            self.error_occurred.emit("El protocolo del PIC requiere 9600 Bd.")
            return False
        if self.connected:
            self.close()

        self._parser.reset()
        try:
            self._serial = serial.Serial(
                port=device,
                baudrate=baud_rate,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                timeout=0,
                write_timeout=0.2,
                xonxoff=False,
                rtscts=False,
                dsrdtr=False,
            )
        except (serial.SerialException, ValueError, OSError) as exc:
            self._serial = None
            self.error_occurred.emit(f"No se pudo abrir {device}: {exc}")
            self.connection_changed.emit(False)
            return False

        self._poll_timer.start()
        self.connection_changed.emit(True)
        return True

    def write(self, data: bytes) -> bool:
        """Escribe una trama pequeña; devuelve False si falla o está cerrado."""
        if not self.connected:
            self.error_occurred.emit("No hay un puerto serie conectado.")
            return False
        try:
            written = self._serial.write(data)
            if written != len(data):
                raise serial.SerialTimeoutException("Escritura serie incompleta")
        except (serial.SerialException, OSError) as exc:
            self.error_occurred.emit(f"Error al transmitir por serie: {exc}")
            self.close()
            return False
        return True

    def close(self) -> None:
        """Detiene el sondeo y cierra el puerto si estaba abierto."""
        self._poll_timer.stop()
        port, self._serial = self._serial, None
        if port is not None:
            try:
                if port.is_open:
                    port.close()
            except (serial.SerialException, OSError) as exc:
                self.error_occurred.emit(f"Error al cerrar el puerto: {exc}")
        self.connection_changed.emit(False)

    def _poll(self) -> None:
        if not self.connected:
            return
        try:
            available = self._serial.in_waiting
            if not available:
                return
            chunk = self._serial.read(min(available, 512))
            for packet in self._parser.feed(chunk):
                self.frame_received.emit(packet)
        except (serial.SerialException, OSError) as exc:
            self.error_occurred.emit(f"Error al recibir por serie: {exc}")
            self.close()
