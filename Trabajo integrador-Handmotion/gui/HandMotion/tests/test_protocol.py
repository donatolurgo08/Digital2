"""Pruebas del codec y parser incremental del protocolo PIC v1."""

from hand_motion.communication.protocol import (
    AckPacket,
    Command,
    DataPacket,
    FrameParser,
    StatusPacket,
    crc8,
    decode_frame,
    encode_command,
    encode_frame,
)


def test_crc_and_firmware_command_vectors() -> None:
    assert crc8(b"123456789") == 0xF4
    assert encode_command(Command.PING) == bytes.fromhex("AA 55 01 81 9B")
    assert encode_command("START", b"\x32") == bytes.fromhex("AA 55 02 82 32 D4")


def test_decode_data_signed_x_and_alarm() -> None:
    payload = bytes((7, 42)) + (-123).to_bytes(2, "little", signed=True) + b"\x01"
    packet = decode_frame(encode_frame(0x01, payload))
    assert packet == DataPacket(7, 42, -123, True, 1)
    assert packet.x_g == -0.123


def test_decode_status_and_ack() -> None:
    status_payload = bytes((1, 50, 40)) + (338).to_bytes(2, "little") + b"\x01"
    status = decode_frame(encode_frame(0x02, status_payload))
    assert status == StatusPacket(1, 50, 40, 338, True, 1)
    ack = decode_frame(encode_frame(0x03, bytes((Command.SET_OFFSET, 0))))
    assert ack == AckPacket(Command.SET_OFFSET, 0)


def test_parser_handles_fragmentation_noise_and_bad_crc() -> None:
    frame = encode_frame(0x01, bytes((1, 25, 0, 0, 0)))
    parser = FrameParser()
    bad = bytearray(frame)
    bad[-1] ^= 0x01
    assert parser.feed(b"noise" + bytes(bad[:4])) == []
    packets = parser.feed(bytes(bad[4:]) + frame)
    assert len(packets) == 1
    assert packets[0] == DataPacket(1, 25, 0, False, 0)
    assert parser.crc_errors == 1


def test_command_range_validation() -> None:
    invalid = (
        (Command.PING, b"\x00"),
        (Command.START, b"\x01"),
        (Command.START, b"\xFB"),
        (Command.SET_THRESHOLD, b"\x64"),
        (Command.SET_OFFSET, (1024).to_bytes(2, "little")),
    )
    for command, payload in invalid:
        try:
            encode_command(command, payload)
        except ValueError:
            continue
        raise AssertionError(f"Se aceptó un comando inválido: {command}")
