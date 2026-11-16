"""Pruebas de integración del reconocimiento de gestos en la GUI."""

from __future__ import annotations

import os
import math
import unittest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import QAbstractAnimation, Qt
from PySide6.QtWidgets import QApplication

from hand_motion.communication.protocol import DataPacket
from hand_motion.logic.gesture_recognition import REST, X_POSITIVE
from hand_motion.preferences import GuiPreferencesStore
from hand_motion.ui.main_window import MainWindow
from hand_motion.ui.widgets.connection_indicator import ConnectionIndicator
from preferences_helpers import MemorySettings


class GestureGuiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self) -> None:
        self.preference_store = GuiPreferencesStore(MemorySettings())
        self.window = MainWindow(preferences_store=self.preference_store)
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

    def test_dashboard_gesture_summary_shows_data_calibration_and_rest_states(self) -> None:
        summary = self.window.gesture_summary
        self.assertEqual(summary.result_label.text(), "SIN DATOS")

        self._feed(0, 0, 1000, count=1)
        self.assertEqual(summary.result_label.text(), "SIN CALIBRAR")

        self._feed(0, 0, 1000, count=5)
        self.window._capture_gesture_rest()
        self.assertEqual(summary.result_label.text(), "RECONOCIENDO")

        self._feed(0, 0, 1000, count=10)
        self.assertEqual(summary.result_label.text(), "Gesto: REPOSO")

    def test_v2_without_z_is_limited_to_xy_and_rest(self) -> None:
        self._feed(0, 0, 1000, count=5)
        self.window._capture_gesture_rest()
        self.assertIn(
            "Z +1.000 g",
            self.window.configuration_page.baseline_label.text(),
        )
        self._feed(0, 0, None, count=10)
        self.assertIn(
            "Z -- (no disponible en v2)",
            self.window.configuration_page.baseline_label.text(),
        )
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
        self.assertEqual(self.window.stack.count(), 4)
        expected_pages = (
            self.window.dashboard_page,
            self.window.acquisition_page,
            self.window.recognition_page,
            self.window.configuration_page,
        )
        for index, page in enumerate(expected_pages):
            self.window.sidebar.select_section(index)
            self.assertIs(self.window.stack.currentWidget(), page)
        self.assertEqual(
            [button.toolTip() for button in self.window.sidebar._buttons],
            ["Dashboard", "Adquisición", "Reconocimiento", "Configuración"],
        )
        self.window.configuration_page.open_recognition_button.click()
        self.assertIs(self.window.stack.currentWidget(), self.window.recognition_page)
        self.window.sidebar.select_section(2)
        self.assertIs(self.window.stack.currentWidget(), self.window.recognition_page)

    def test_history_is_not_in_navigation_or_stack(self) -> None:
        labels = [button.toolTip() for button in self.window.sidebar._buttons]
        self.assertEqual(
            labels,
            ["Dashboard", "Adquisición", "Reconocimiento", "Configuración"],
        )
        self.assertNotIn("Historial", labels)
        self.assertEqual(self.window.stack.count(), 4)

    def test_sidebar_expands_without_overlay_and_collapses(self) -> None:
        sidebar = self.window.sidebar
        sidebar.set_expanded(True)
        sidebar._animations.setCurrentTime(180)
        self.app.processEvents()
        self.assertEqual(sidebar.width(), sidebar._expanded_width)
        self.assertEqual(
            sidebar._buttons[0].toolButtonStyle(), Qt.ToolButtonTextBesideIcon
        )
        self.assertTrue(self.window._dashboard_compact)

        sidebar.set_expanded(False)
        sidebar._animations.setCurrentTime(180)
        self.app.processEvents()
        self.assertEqual(sidebar.width(), sidebar._collapsed_width)
        self.assertEqual(
            sidebar._buttons[0].toolButtonStyle(), Qt.ToolButtonIconOnly
        )
        self.assertFalse(self.window._dashboard_compact)

    def test_connection_dot_pulses_only_while_connected(self) -> None:
        indicator = ConnectionIndicator()
        indicator.set_connected(True)
        self.assertEqual(indicator._pulse.state(), QAbstractAnimation.Running)
        indicator.set_connected(False)
        self.assertEqual(indicator._pulse.state(), QAbstractAnimation.Stopped)
        self.assertEqual(indicator._dot_effect.opacity(), 1.0)
        indicator.close()

    def test_axis_activity_dots_follow_live_data_and_stop_when_cleared(self) -> None:
        self._feed(100, 200, 300)
        self.assertEqual(
            self.window.accel_panel._activity_pulse.state(),
            QAbstractAnimation.Running,
        )
        self.assertEqual(
            self.window.accel_y_panel._activity_pulse.state(),
            QAbstractAnimation.Running,
        )
        self.assertEqual(
            self.window.accel_z_panel._activity_pulse.state(),
            QAbstractAnimation.Running,
        )
        self.window.state.set_connected(False)
        self.assertEqual(
            self.window.accel_z_panel._activity_pulse.state(),
            QAbstractAnimation.Stopped,
        )

    def test_label_backgrounds_are_transparent_but_inputs_keep_their_surface(self) -> None:
        stylesheet = self.window.styleSheet()
        self.assertIn("QLabel {", stylesheet)
        self.assertIn("background-color: transparent;", stylesheet)
        self.assertIn("QComboBox, QLineEdit, QSpinBox, QDoubleSpinBox", stylesheet)
        self.assertIn("QFrame#Card", stylesheet)

    def test_dashboard_graph_shares_source_and_marks_v2_z_unavailable(self) -> None:
        self.assertIs(self.window.dashboard_graph.source, self.window.accel_source)
        self.assertTrue(self.window.dashboard_graph.note.isHidden())
        self.assertFalse(self.window.accel_graph.note.isHidden())
        self.assertTrue(self.window.accel_panel.note.isHidden())
        self.assertTrue(self.window.accel_y_panel.note.isHidden())
        self.assertTrue(self.window.accel_z_panel.note.isHidden())

        self._feed(0, 0, 1000, count=5)
        self.window._capture_gesture_rest()
        self._feed(500, 0, 1000, count=10)
        self.assertEqual(self.window.dashboard_graph._z_values[-1], 1.0)

        packet = DataPacket(
            sequence=99,
            temperature_c=25,
            x_mg=0,
            y_mg=0,
            alarm_active=False,
            flags=0,
            z_mg=None,
        )
        self.window.state.set_data_packet(packet)
        self.assertTrue(math.isnan(self.window.dashboard_graph._z_values[-1]))
        self.assertIn("Z: --", self.window.dashboard_graph.last_value_label.text())

    def test_configuration_updates_shared_recognizer_and_simulation_rate(self) -> None:
        config = self.window.configuration_page
        self.window.accel_graph.rate_spin.setValue(60)
        self.assertEqual(self.window.preferences.simulation_rate_hz, 60)
        self.assertEqual(config.simulation_rate_spin.value(), 60)

        config.threshold_spins[0].setValue(0.45)
        config.window_spin.setValue(7)
        config.hold_spin.setValue(4)
        config.simulation_rate_spin.setValue(75)

        self.assertEqual(self.window.gesture_recognizer.thresholds.x_g, 0.45)
        self.assertEqual(self.window.gesture_recognizer.window_samples, 7)
        self.assertEqual(self.window.gesture_recognizer.hold_samples, 4)
        self.assertEqual(self.window.accel_source.sample_rate_hz, 75.0)
        self.assertEqual(self.window.accel_graph.rate_spin.value(), 75)
        self.assertEqual(self.window.dashboard_graph.rate_spin.value(), 75)
        self.assertEqual(self.window.gesture_panel.thresholds()[0], 0.45)
        self.assertEqual(self.preference_store.load().threshold_x_g, 0.45)
        self.window.gesture_panel.threshold_spins[1].setValue(0.55)
        self.assertEqual(config.threshold_spins[1].value(), 0.55)
        self.assertEqual(self.window.preferences.threshold_y_g, 0.55)

        self.assertTrue(config.restore_defaults(confirmed=True))
        self.assertEqual(self.window.preferences.simulation_rate_hz, 50)
        self.assertEqual(self.window.gesture_recognizer.window_samples, 5)
        self.assertIsNone(self.window.gesture_recognizer.baseline)

    def test_toast_shows_gesture_over_graph_and_hides_on_source_change(self) -> None:
        self.window.stack.setCurrentIndex(1)
        self.app.processEvents()

        self._feed(0, 0, 1000, count=5)
        self.window._capture_gesture_rest()
        self._feed(500, 0, 1000, count=10)
        self.app.processEvents()

        toast = self.window.gesture_toast
        self.assertIs(toast.parentWidget(), self.window.accel_graph)
        self.assertTrue(toast.testAttribute(Qt.WA_TransparentForMouseEvents))
        self.assertTrue(toast.isVisible())
        self.assertEqual(toast.gesture_label.text(), "X+")
        self.assertIn("X positivo", toast.detail_label.text())
        self.assertTrue(
            self.window.accel_graph.plot.geometry().contains(
                toast.geometry().center()
            )
        )

        self.window._set_mode(False)
        self.app.processEvents()
        self.assertFalse(toast.isVisible())

    def test_toast_shows_rest_with_green_accent(self) -> None:
        self.window.stack.setCurrentIndex(1)
        self._feed(0, 0, 1000, count=5)
        self.window._capture_gesture_rest()
        self._feed(0, 0, 1000, count=10)
        self.app.processEvents()

        toast = self.window.gesture_toast
        self.assertTrue(toast.isVisible())
        self.assertEqual(toast.gesture_label.text(), "REPOSO")
        self.assertIn("#22D98A", toast.styleSheet())


if __name__ == "__main__":
    unittest.main()
