"""Pruebas de integración del reconocimiento de gestos en la GUI."""

from __future__ import annotations

import os
import unittest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication

from hand_motion.communication.protocol import DataPacket
from hand_motion.logic.gesture_recognition import REST, X_POSITIVE
from hand_motion.ui.main_window import MainWindow


class GestureGuiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self) -> None:
        self.window = MainWindow()
        self.window.resize(1180, 760)
        self.window.show()
        self.app.processEvents()
        self.window._set_mode(True)

    def tearDown(self) -> None:
        self.window.close()
        self.app.processEvents()

    def _feed(self, x_mg: int, y_mg: int, z_mg: int | None, count: int = 1) -> None:
        for index in range(count):
            packet = DataPacket(
                sequence=index + 1,
                temperature_c=25,
                x_mg=x_mg,
                y_mg=y_mg,
                alarm_active=False,
                flags=0,
                z_mg=z_mg,
            )
            self.window.state.set_data_packet(packet)
        self.app.processEvents()

    def test_capture_rest_and_confirm_x_gesture(self) -> None:
        self._feed(0, 0, 1000, count=5)
        self.window._capture_gesture_rest()
        self.assertTrue(self.window._gesture_calibrated)
        self.assertEqual(self.window.gesture_panel.baseline_spins[2].value(), 1.0)

        self._feed(500, 0, 1000, count=10)
        self.assertEqual(self.window.state.data.gesture, X_POSITIVE)
        self.assertEqual(self.window.gesture_panel.result_label.text(), "Gesto: X+")
        self.assertEqual(
            self.window.gesture_summary.result_label.text(), "Gesto: X+"
        )

    def test_v2_without_z_is_limited_to_xy_and_rest(self) -> None:
        self._feed(0, 0, 1000, count=5)
        self.window._capture_gesture_rest()
        self._feed(0, 0, None, count=10)
        self.assertEqual(self.window.state.data.gesture, REST)
        self.assertEqual(
            self.window.gesture_panel.result_label.text(), "Gesto: REPOSO"
        )
        self.assertIn("Z --", self.window.gesture_panel.live_label.text())

    def test_threshold_change_updates_recognizer_and_disconnect_clears(self) -> None:
        self.window.gesture_panel.threshold_spins[0].setValue(0.40)
        self.app.processEvents()
        self.assertEqual(self.window.gesture_recognizer.thresholds.x_g, 0.40)

        self._feed(0, 0, 1000, count=5)
        self.window._capture_gesture_rest()
        self._feed(500, 0, 1000, count=10)
        self.assertEqual(self.window.state.data.gesture, X_POSITIVE)

        self.window.state.set_connected(False)
        self.app.processEvents()
        self.assertIsNone(self.window.state.data.gesture)
        self.assertEqual(self.window.gesture_panel.result_label.text(), "Gesto: --")

    def test_recognition_page_is_in_the_stack(self) -> None:
        self.assertIs(self.window.stack.widget(2), self.window.recognition_page)


if __name__ == "__main__":
    unittest.main()
