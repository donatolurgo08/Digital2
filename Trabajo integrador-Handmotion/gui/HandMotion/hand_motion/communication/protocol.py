"""Codec del protocolo binario v1 entre el PIC16F887 y la GUI.

Formato: ``AA 55 | LEN | TIPO | DATOS | CRC8``. LEN incluye TIPO y DATOS;
CRC-8/ATM (poly 0x07, init 0, MSB-first) cubre LEN hasta el último dato.
El firmware v1 transmite temperatura y eje X; Y/Z se reservan para después.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum


SYNC = b"\xAA\x55"
PROTOCOL_VERSION = 1
MAX_FRAME_LENGTH = 8  # igual al máximo aceptado por el firmware PIC
DEFAULT_DATA_PERIOD_MS = 50
MIN_DATA_PERIOD_MS = 20
MAX_DATA_PERIOD_MS = 250


class FrameType(IntEnum):
    DATA = 0x01
    STATUS = 0x02
    ACK = 0x03


class Command(IntEnum):
    PING = 0x81
    START = 0x82
    STOP = 0x83
    SET_THRESHOLD = 0x84
    GET_STATUS = 0x85
    SET_OFFSET = 0x86


@dataclass(frozen=True)
class DataPacket:
    sequence: int
    temperature_c: int
    x_mg: int
    alarm_active: bool
    flags: int

    @property
    def x_g(self) -> float:
        """X expresado en g a partir del valor nominal de mg enviado por PIC."""
        return self.x_mg / 1000.0


@dataclass(frozen=True)
class StatusPacket:
    version: int
    period_ms: int
    threshold_c: int
    x_offset_counts: int
    streaming: bool
    mode: int


@dataclass(frozen=True)
class AckPacket:
    command: int
    result: int


@dataclass(frozen=True)
class UnknownPacket:
    frame_type: int
    payload: bytes


Packet = DataPacket | StatusPacket | AckPacket | UnknownPacket


def crc8(data: bytes | bytearray | memoryview) -> int:
    """Calcula CRC-8/ATM, polinomio 0x07, sin reflexión ni XOR final."""
    crc = 0
    for byte in data:
        crc ^= byte
        for _ in range(8):
            if crc & 0x80:
                crc = ((crc << 1) ^ 0x07) & 0xFF
            else:
                crc = (crc << 1) & 0xFF
    return crc


def encode_frame(frame_type: int, payload: bytes = b"") -> bytes:
    """Construye una trama con LEN y CRC calculados."""
    if not 0 <= int(frame_type) <= 0xFF:
        raise ValueError("El tipo debe caber en un byte")
    length = 1 + len(payload)
    if length > 0xFF:
        raise ValueError("La trama excede el tamaño representable por LEN")
    body = bytes((length, int(frame_type))) + bytes(payload)
    return SYNC + body + bytes((crc8(body),))


def _validate_command(command: Command, payload: bytes) -> None:
    if command in (Command.PING, Command.STOP, Command.GET_STATUS):
        if payload:
            raise ValueError(f"{command.name} no lleva datos")
    elif command is Command.START:
        if len(payload) != 1:
            raise ValueError("START requiere un byte de período")
        period_ms = payload[0]
        if period_ms != 0 and not MIN_DATA_PERIOD_MS <= period_ms <= MAX_DATA_PERIOD_MS:
            raise ValueError("El período START debe ser 0 o estar entre 20 y 250 ms")
    elif command is Command.SET_THRESHOLD:
        if len(payload) != 1 or payload[0] > 99:
            raise ValueError("SET_THRESHOLD requiere un valor entre 0 y 99 °C")
    elif command is Command.SET_OFFSET:
        if len(payload) != 2:
            raise ValueError("SET_OFFSET requiere un entero little-endian de 16 bits")
        if int.from_bytes(payload, "little") > 1023:
            raise ValueError("El offset ADC debe estar entre 0 y 1023")


def encode_command(command: Command | int | str, payload: bytes = b"") -> bytes:
    """Codifica un comando validando su longitud y rango según protocolo v1.

    ``command`` admite un miembro de :class:`Command`, su byte o su nombre
    (por ejemplo ``"START"``). Para SET_OFFSET el payload son dos bytes
    little-endian; para START el período 0 significa conservar el actual.
    """
    if isinstance(command, str):
        try:
            command = Command[command.upper()]
        except KeyError as exc:
            raise ValueError(f"Comando desconocido: {command}") from exc
    try:
        command = Command(command)
    except ValueError as exc:
        raise ValueError(f"Comando desconocido: {command}") from exc
    payload = bytes(payload)
    _validate_command(command, payload)
    return encode_frame(command, payload)


def decode_frame(frame: bytes) -> Packet:
    """Valida una trama completa y decodifica los tipos PIC→GUI conocidos."""
    if len(frame) < 5 or not frame.startswith(SYNC):
        raise ValueError("Sincronismo de trama inválido")
    length = frame[2]
    if not 1 <= length <= MAX_FRAME_LENGTH:
        raise ValueError("LEN fuera del rango admitido")
    if len(frame) != length + 4:
        raise ValueError("Longitud física de trama incorrecta")
    if crc8(frame[2:-1]) != frame[-1]:
        raise ValueError("CRC-8 incorrecto")

    frame_type = frame[3]
    payload = frame[4:-1]
    if frame_type == FrameType.DATA:
        if length != 6 or len(payload) != 5:
            raise ValueError("La trama DATA v1 debe contener cinco bytes")
        flags = payload[4]
        return DataPacket(
            sequence=payload[0],
            temperature_c=payload[1],
            x_mg=int.from_bytes(payload[2:4], "little", signed=True),
            alarm_active=bool(flags & 0x01),
            flags=flags,
        )
    if frame_type == FrameType.STATUS:
        if length != 7 or len(payload) != 6:
            raise ValueError("La trama STATUS v1 debe contener seis bytes")
        mode = payload[5]
        return StatusPacket(
            version=payload[0],
            period_ms=payload[1],
            threshold_c=payload[2],
            x_offset_counts=int.from_bytes(payload[3:5], "little"),
            streaming=bool(mode & 0x01),
            mode=mode,
        )
    if frame_type == FrameType.ACK:
        if length != 3 or len(payload) != 2:
            raise ValueError("La trama ACK v1 debe contener dos bytes")
        return AckPacket(command=payload[0], result=payload[1])
    return UnknownPacket(frame_type=frame_type, payload=payload)


class FrameParser:
    """Parser incremental que acepta fragmentos y descarta ruido/CRC erróneo."""

    def __init__(self) -> None:
        self._buffer = bytearray()
        self.crc_errors = 0
        self.malformed_frames = 0

    def reset(self) -> None:
        self._buffer.clear()
        self.crc_errors = 0
        self.malformed_frames = 0

    def feed(self, data: bytes) -> list[Packet]:
        self._buffer.extend(data)
        packets: list[Packet] = []

        while True:
            sync_at = self._buffer.find(SYNC)
            if sync_at < 0:
                # Conserva AA al final por si 55 llega en el próximo fragmento.
                keep_sync_prefix = self._buffer[-1:] == SYNC[:1]
                self._buffer[:] = SYNC[:1] if keep_sync_prefix else b""
                break
            if sync_at:
                del self._buffer[:sync_at]
            if len(self._buffer) < 3:
                break

            length = self._buffer[2]
            if not 1 <= length <= MAX_FRAME_LENGTH:
                self.malformed_frames += 1
                del self._buffer[0]
                continue
            total_length = length + 4
            if len(self._buffer) < total_length:
                break

            candidate = bytes(self._buffer[:total_length])
            try:
                packet = decode_frame(candidate)
            except ValueError as exc:
                if "CRC" in str(exc):
                    self.crc_errors += 1
                else:
                    self.malformed_frames += 1
                # Avanza un byte para buscar sincronismo dentro del remanente.
                del self._buffer[0]
                continue

            packets.append(packet)
            del self._buffer[:total_length]

        return packets
