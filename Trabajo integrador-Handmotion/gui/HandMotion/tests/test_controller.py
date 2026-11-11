"""Pruebas del enrutamiento entre controlador, codec y estado."""

from hand_motion.communication.protocol import DataPacket, StatusPacket
from hand_motion.core.controller import AppController
from hand_motion.core.state import AppState


class _FakePort:
    is_open = True

    def __init__(self) -> None:
        self.writes: list[bytes] = []

    def write(self, data: bytes) -> int:
        self.writes.append(data)
        return len(data)


def test_controller_encodes_commands_and_updates_state() -> None:
    state = AppState()
    controller = AppController(state)
    fake_port = _FakePort()
    controller.serial._serial = fake_port  # fake pyserial port; no physical I/O

    assert controller.start_stream(50)
    assert fake_port.writes[-1] == bytes.fromhex("AA 55 02 82 32 D4")
    assert controller.set_threshold(42)
    assert controller.set_x_offset(338)

    controller.handle_packet(DataPacket(4, 41, -250, True, 1))
    assert state.data.temperature_c == 41.0
    assert state.data.accel_x == -0.25
    assert state.data.accel_x_mg == -250
    assert state.data.alarm_active is True
    assert state.data.accel_y is None and state.data.accel_z is None

    controller.handle_packet(StatusPacket(1, 50, 42, 338, True, 1))
    assert state.data.alarm_threshold_c == 42
    assert state.data.x_offset_counts == 338

    controller.serial._serial = None
