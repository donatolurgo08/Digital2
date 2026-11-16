"""Pruebas unittest de compatibilidad v2/v3 y visualización XYZ."""

from __future__ import annotations

import math
import os
import unittest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication, QScrollArea

from hand_motion.communication.protocol import (
    AckPacket,
    DataPacket,
    FrameParser,
    StatusPacket,
    decode_frame,
    encode_frame,
)
from hand_motion.core.controller import AppController
from hand_motion.core.state import AppState
from hand_motion.preferences import GuiPreferencesStore
from hand_motion.processing.simulated_source import SimulatedAccelSource
from hand_motion.ui.main_window import MainWindow
from hand_motion.ui.widgets.accelerometer_graph import AccelerometerGraph
from hand_motion.ui.widgets.accelerometer_panel import AccelerometerPanel
from preferences_helpers import MemorySettings


def data_v2(
    sequence: int = 1,
    x_mg: int = -123,
    y_mg: int = 456,
    flags: int = 0,
) -> bytes:
    payload = (
        bytes((sequence, 25))
        + x_mg.to_bytes(2, "little", signed=True)
        + y_mg.to_bytes(2, "little", signed=True)
        + bytes((flags,))
    )
    return encode_frame(0x01, payload)


def data_v3(
    sequence: int = 2,
    x_mg: int = -123,
    y_mg: int = 456,
    z_mg: int = -789,
    flags: int = 1,
) -> bytes:
    payload = (
        bytes((sequence, 26))
        + x_mg.to_bytes(2, "little", signed=True)
        + y_mg.to_bytes(2, "little", signed=True)
        + z_mg.to_bytes(2, "little", signed=True)
        + bytes((flags,))
    )
    return encode_frame(0x01, payload)


class ProtocolCompatibilityTests(unittest.TestCase):
    def test_data_v2_has_signed_xy_and_no_z(self) -> None:
        frame = data_v2()
        packet = decode_frame(frame)
        self.assertEqual(frame[2], 8)
        self.assertEqual(len(frame), 12)
        self.assertEqual(packet, DataPacket(1, 25, -123, 456, False, 0))
        self.assertIsNone(packet.z_mg)
        self.assertIsNone(packet.z_g)
        self.assertEqual(packet.data_format_version, 2)

    def test_data_v3_has_signed_xyz(self) -> None:
        frame = data_v3()
        packet = decode_frame(frame)
        self.assertEqual(frame[2], 10)
        self.assertEqual(len(frame), 14)
        self.assertEqual(
            packet, DataPacket(2, 26, -123, 456, True, 1, z_mg=-789)
        )
        self.assertEqual((packet.x_mg, packet.y_mg, packet.z_mg), (-123, 456, -789))
        self.assertEqual(packet.z_g, -0.789)
        self.assertEqual(packet.data_format_version, 3)

    def test_parser_handles_fragments_noise_multiple_frames_and_bad_crc(self) -> None:
        first, second = data_v2(), data_v3()
        corrupted = bytearray(first)
        corrupted[-1] ^= 0x80
        parser = FrameParser()
        self.assertEqual(parser.feed(b"noise\xAA" + bytes(corrupted[:5])), [])
        packets = parser.feed(
            bytes(corrupted[5:]) + b"junk" + second[:4]
        )
        self.assertEqual(packets, [])
        packets = parser.feed(second[4:] + first)
        self.assertEqual(packets, [decode_frame(second), decode_frame(first)])
        self.assertEqual(parser.crc_errors, 1)

    def test_bad_data_length_and_unknown_type_are_rejected_and_recovered(self) -> None:
        invalid_data = encode_frame(0x01, bytes(range(8)))  # DATA LEN=9
        parser = FrameParser()
        self.assertEqual(parser.feed(invalid_data + data_v3()), [decode_frame(data_v3())])
        self.assertEqual(parser.malformed_frames, 1)
        with self.assertRaisesRegex(ValueError, "LEN=8.*LEN=10"):
            decode_frame(invalid_data)

        unknown = encode_frame(0x7F, b"\x01")
        with self.assertRaisesRegex(ValueError, "Tipo de trama desconocido"):
            decode_frame(unknown)
        unknown_parser = FrameParser()
        self.assertEqual(unknown_parser.feed(unknown + data_v2()), [decode_frame(data_v2())])
        self.assertEqual(unknown_parser.malformed_frames, 1)

    def test_status_v2_v3_and_ack_keep_their_lengths(self) -> None:
        for version in (2, 3):
            status_frame = encode_frame(
                0x02, bytes((version, 50, 40)) + (338).to_bytes(2, "little") + b"\x01"
            )
            self.assertEqual(status_frame[2], 7)
            self.assertEqual(decode_frame(status_frame).version, version)
        ack_frame = encode_frame(0x03, b"\x86\x00")
        self.assertEqual(ack_frame[2], 3)
        self.assertEqual(decode_frame(ack_frame), AckPacket(0x86, 0))


class StateAndControllerTests(unittest.TestCase):
    def test_data_before_status_does_not_infer_firmware_version(self) -> None:
        state = AppState()
        controller = AppController(state)
        messages: list[str] = []
        controller.message.connect(messages.append)
        packet = FrameParser().feed(data_v3())[0]
        controller.handle_packet(packet)
        self.assertIsNone(state.data.firmware_version)
        self.assertEqual(state.data.data_format_version, 3)
        self.assertEqual(state.data.data_source, "device")

        status = decode_frame(
            encode_frame(
                0x02, bytes((3, 50, 40)) + (338).to_bytes(2, "little") + b"\x01"
            )
        )
        controller.handle_packet(status)
        self.assertEqual(state.data.firmware_version, 3)
        self.assertEqual(state.data.data_format_version, 3)
        status_v2 = decode_frame(
            encode_frame(
                0x02, bytes((2, 50, 40)) + (338).to_bytes(2, "little") + b"\x01"
            )
        )
        controller.handle_packet(status_v2)
        self.assertEqual(state.data.firmware_version, 2)
        self.assertEqual(messages, [])
        controller.close()

    def test_v2_clears_previous_z_and_disconnect_clears_xyz(self) -> None:
        state = AppState()
        state.set_connected(True)
        state.set_status_packet(StatusPacket(3, 50, 40, 338, True, 1))
        state.set_data_packet(decode_frame(data_v3(z_mg=250)))
        self.assertEqual(state.data.accel_z, 0.25)
        self.assertEqual(state.data.data_format_version, 3)

        state.set_data_packet(decode_frame(data_v2()))
        self.assertIsNone(state.data.accel_z)
        self.assertIsNone(state.data.accel_z_mg)
        self.assertEqual(state.data.data_format_version, 2)

        state.set_data_packet(decode_frame(data_v3(z_mg=250)))
        state.set_connected(False)
        self.assertFalse(state.data.connected)
        self.assertFalse(state.data.data_received)
        self.assertIsNone(state.data.accel_x)
        self.assertIsNone(state.data.accel_y)
        self.assertIsNone(state.data.accel_z)
        self.assertIsNone(state.data.firmware_version)
        self.assertIsNone(state.data.data_source)


class UiAndSimulationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.app = QApplication.instance() or QApplication([])

    def test_panel_and_graph_accept_missing_and_present_z(self) -> None:
        panel = AccelerometerPanel("Z")
        panel.update_value(None, live=True)
        self.assertEqual(panel._card.value_label.text(), "--")
        panel.update_value(0.375, live=True)
        self.assertEqual(panel._card.value_label.text(), "+0.375 g")

        graph = AccelerometerGraph()
        graph.set_device_mode(True)
        graph.add_live_sample(0.1, y_g=-0.2, z_g=None)
        self.assertTrue(math.isnan(graph._z_values[-1]))
        self.assertIn("Z: --", graph.last_value_label.text())
        graph.add_live_sample(0.2, y_g=0.3, z_g=-0.4)
        self.assertEqual(graph._z_values[-1], -0.4)
        self.assertIn("Z: -0.400 g", graph.last_value_label.text())
        graph.set_device_mode(False)
        self.assertEqual(len(graph._z_values), 0)
        graph.source.set_scenario("rest")
        graph.source._emit_sample()
        self.assertIn("SIMULACIÓN", graph.last_value_label.text())
        self.assertIn("Z: +1.000 g", graph.last_value_label.text())
        panel.close()
        graph.close()

    def test_dashboard_shows_v3_z_and_marks_v2_z_unavailable(self) -> None:
        window = MainWindow(
            preferences_store=GuiPreferencesStore(MemorySettings())
        )
        window.resize(1180, 760)
        window.show()
        self.app.processEvents()
        scroll = window.dashboard_page.findChild(QScrollArea)
        self.assertEqual(scroll.horizontalScrollBar().maximum(), 0)
        window.resize(960, 640)
        self.app.processEvents()
        self.assertEqual(scroll.horizontalScrollBar().maximum(), 0)
        window._set_mode(True)
        window.state.set_data_packet(decode_frame(data_v3(z_mg=375)))
        self.assertEqual(window.accel_z_panel._card.value_label.text(), "+0.375 g")
        self.assertEqual(
            window.dashboard_graph._z_values[-1], 0.375
        )
        self.assertIn("Z +375 mg", window.status_bar.message.text())

        window.state.set_data_packet(decode_frame(data_v2()))
        self.assertEqual(window.accel_z_panel._card.value_label.text(), "--")
        self.assertIn("Z --", window.status_bar.message.text())
        self.assertIn("Z: --", window.accel_graph.last_value_label.text())
        self.assertTrue(math.isnan(window.dashboard_graph._z_values[-1]))
        window.close()

    def test_simulator_is_repeatable_and_supports_rest_and_movement(self) -> None:
        def collect(source: SimulatedAccelSource, count: int) -> list[tuple[float, ...]]:
            samples: list[tuple[float, ...]] = []
            source.sample_xyz.connect(lambda x, y, z: samples.append((x, y, z)))
            for _ in range(count):
                source._emit_sample()
            return samples

        first = SimulatedAccelSource(noise_g=0.03)
        second = SimulatedAccelSource(noise_g=0.03)
        self.assertEqual(collect(first, 4), collect(second, 4))
        first.set_scenario("rest")
        self.assertEqual(collect(first, 1), [(0.0, 0.0, 1.0)])
        with self.assertRaises(ValueError):
            first.set_scenario("unknown")


if __name__ == "__main__":
    unittest.main()
