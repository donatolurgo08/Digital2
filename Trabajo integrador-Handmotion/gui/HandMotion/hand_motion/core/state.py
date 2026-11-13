"""Estado observable de la GUI; una única fuente de verdad para datos PIC."""

from __future__ import annotations

from dataclasses import dataclass

from PySide6.QtCore import QObject, Signal

from hand_motion.communication.protocol import AckPacket, DataPacket, StatusPacket
from hand_motion.sensors.accelerometer import mg_to_g


@dataclass
class AppStateData:
    """Últimas mediciones y configuración recibidas del dispositivo."""

    connected: bool = False
    temperature_c: float | None = None
    accel_x: float | None = None  # g nominales convertidos desde X en mg
    accel_x_mg: int | None = None
    accel_y: float | None = None  # no enviado por protocolo v1
    accel_z: float | None = None  # no enviado por protocolo v1
    alarm_active: bool = False
    alarm_threshold_c: int = 40
    gesture: str | None = None
    sequence: int | None = None
    period_ms: int = 50
    x_offset_counts: int = 338
    streaming: bool = True
    protocol_version: int | None = None
    last_ack: AckPacket | None = None
    data_received: bool = False


class AppState(QObject):
    """Emite señales cuando cambia una medición o configuración del PIC."""

    connection_changed = Signal(bool)
    temperature_changed = Signal(float)
    accel_changed = Signal(float)
    alarm_changed = Signal(bool)
    data_packet_received = Signal(object)
    status_packet_received = Signal(object)
    ack_received = Signal(object)

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._data = AppStateData()

    @property
    def data(self) -> AppStateData:
        return self._data

    def set_connected(self, value: bool) -> None:
        self._data.connected = value
        if not value:
            self._data.data_received = False
            self._data.temperature_c = None
            self._data.accel_x = None
            self._data.accel_x_mg = None
            self._data.alarm_active = False
            self._data.sequence = None
        self.connection_changed.emit(value)

    def set_data_packet(self, packet: DataPacket) -> None:
        self._data.temperature_c = float(packet.temperature_c)
        self._data.accel_x_mg = packet.x_mg
        self._data.accel_x = mg_to_g(packet.x_mg)
        self._data.alarm_active = packet.alarm_active
        self._data.sequence = packet.sequence
        self._data.data_received = True
        self.temperature_changed.emit(float(packet.temperature_c))
        self.accel_changed.emit(mg_to_g(packet.x_mg))
        self.alarm_changed.emit(packet.alarm_active)
        self.data_packet_received.emit(packet)

    def set_status_packet(self, packet: StatusPacket) -> None:
        self._data.protocol_version = packet.version
        self._data.period_ms = packet.period_ms
        self._data.alarm_threshold_c = packet.threshold_c
        self._data.x_offset_counts = packet.x_offset_counts
        self._data.streaming = packet.streaming
        self.status_packet_received.emit(packet)

    def set_ack(self, packet: AckPacket) -> None:
        self._data.last_ack = packet
        self.ack_received.emit(packet)
