"""Orquesta el transporte serie, el protocolo v1 y el estado de la aplicación."""

from __future__ import annotations

from PySide6.QtCore import QObject, Signal

from hand_motion.communication.protocol import (
    AckPacket,
    Command,
    DataPacket,
    Packet,
    StatusPacket,
    UnknownPacket,
    encode_command,
)
from hand_motion.communication.serial_port import SerialPortManager
from hand_motion.core.state import AppState


class AppController(QObject):
    """Coordina comandos y actualizaciones recibidas desde el PIC."""

    message = Signal(str)

    def __init__(self, state: AppState, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self.state = state
        self.serial = SerialPortManager(self)
        self.serial.connection_changed.connect(self.state.set_connected)
        self.serial.error_occurred.connect(self.message.emit)
        self.serial.frame_received.connect(self.handle_packet)

    def open(self, device: str) -> bool:
        return self.serial.open(device, 9600)

    def close(self) -> None:
        self.serial.close()

    def send_command(self, command: Command | str, payload: bytes = b"") -> bool:
        try:
            frame = encode_command(command, payload)
        except (TypeError, ValueError) as exc:
            self.message.emit(f"Comando no válido: {exc}")
            return False
        return self.serial.write(frame)

    def start_stream(self, period_ms: int = 0) -> bool:
        try:
            payload = bytes((period_ms,))
        except (TypeError, ValueError) as exc:
            self.message.emit(f"Período no válido: {exc}")
            return False
        return self.send_command(Command.START, payload)

    def stop_stream(self) -> bool:
        return self.send_command(Command.STOP)

    def set_threshold(self, threshold_c: int) -> bool:
        try:
            payload = bytes((threshold_c,))
        except (TypeError, ValueError) as exc:
            self.message.emit(f"Umbral no válido: {exc}")
            return False
        return self.send_command(Command.SET_THRESHOLD, payload)

    def set_x_offset(self, offset_counts: int) -> bool:
        try:
            payload = int(offset_counts).to_bytes(2, "little", signed=False)
        except (OverflowError, ValueError) as exc:
            self.message.emit(f"Offset X no válido: {exc}")
            return False
        return self.send_command(Command.SET_OFFSET, payload)

    def request_status(self) -> bool:
        return self.send_command(Command.GET_STATUS)

    def ping(self) -> bool:
        return self.send_command(Command.PING)

    def handle_packet(self, packet: Packet) -> None:
        """Actualiza estado solo con paquetes conocidos y CRC ya validados."""
        if isinstance(packet, DataPacket):
            self.state.set_data_packet(packet)
            return
        if isinstance(packet, StatusPacket):
            self.state.set_status_packet(packet)
            if packet.version != 1:
                self.message.emit(
                    f"Versión de protocolo no reconocida: {packet.version}"
                )
            return
        if isinstance(packet, AckPacket):
            self.state.set_ack(packet)
            return
        if isinstance(packet, UnknownPacket):
            self.message.emit(
                f"Tipo de trama PIC no reconocido: 0x{packet.frame_type:02X}"
            )
