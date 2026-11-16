"""Pruebas de preferencias persistidas y de la vista Configuración."""

from __future__ import annotations

import os
import unittest
from unittest.mock import patch

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication, QMessageBox

from hand_motion.preferences import GuiPreferences, GuiPreferencesStore
from hand_motion.ui.views.configuration_view import ConfigurationView
from preferences_helpers import MemorySettings


class PreferencesStoreTests(unittest.TestCase):
    def test_preferences_round_trip_and_invalid_values_fall_back(self) -> None:
        settings = MemorySettings()
        store = GuiPreferencesStore(settings)
        preferences = GuiPreferences(
            simulation_rate_hz=75,
            threshold_x_g=0.3,
            threshold_y_g=0.4,
            threshold_z_g=0.5,
            window_samples=9,
            hold_samples=4,
        )
        store.save(preferences)
        self.assertEqual(GuiPreferencesStore(settings).load(), preferences)

        settings.values["acquisition/simulation_rate_hz"] = 999
        settings.values["recognition/threshold_x_g"] = float("nan")
        loaded = GuiPreferencesStore(settings).load()
        self.assertEqual(loaded.simulation_rate_hz, 50)
        self.assertEqual(loaded.threshold_x_g, 0.25)
        self.assertEqual(loaded.threshold_y_g, 0.4)


class ConfigurationViewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.app = QApplication.instance() or QApplication([])

    def test_controls_emit_preferences_and_restore_requires_confirmation(self) -> None:
        view = ConfigurationView(GuiPreferences())
        changes: list[GuiPreferences] = []
        reset_requests: list[bool] = []
        opened_recognition: list[bool] = []
        view.preferences_changed.connect(changes.append)
        view.reset_baseline_requested.connect(lambda: reset_requests.append(True))
        view.open_recognition_requested.connect(
            lambda: opened_recognition.append(True)
        )

        view.simulation_rate_spin.setValue(80)
        view.threshold_spins[1].setValue(0.45)
        view.window_spin.setValue(8)
        view.hold_spin.setValue(4)
        self.app.processEvents()
        self.assertEqual(changes[-1].simulation_rate_hz, 80)
        self.assertEqual(changes[-1].threshold_y_g, 0.45)
        self.assertEqual(changes[-1].window_samples, 8)
        self.assertEqual(changes[-1].hold_samples, 4)

        view.simulation_rate_spin.setValue(999)
        view.threshold_spins[0].setValue(-1)
        view.window_spin.setValue(100)
        view.hold_spin.setValue(100)
        self.assertEqual(view.simulation_rate_spin.value(), 200)
        self.assertEqual(view.threshold_spins[0].value(), 0.05)
        self.assertEqual(view.window_spin.value(), 25)
        self.assertEqual(view.hold_spin.value(), 20)

        view.set_runtime_context(
            source_name="DISPOSITIVO",
            device_period_ms=100,
            baseline=(0.01, -0.02, 0.98),
        )
        self.assertIn("100 ms", view.device_period_label.text())
        self.assertIn("X +0.010", view.baseline_label.text())
        self.assertIn("no se persiste", view.baseline_note.text().lower())

        with patch(
            "hand_motion.ui.views.configuration_view.QMessageBox.question",
            return_value=QMessageBox.Cancel,
        ):
            view.restore_button.click()
        self.assertEqual(changes[-1].simulation_rate_hz, 200)

        with patch(
            "hand_motion.ui.views.configuration_view.QMessageBox.question",
            return_value=QMessageBox.Yes,
        ):
            view.restore_button.click()
        self.assertEqual(changes[-1], GuiPreferences())
        self.assertEqual(reset_requests, [True])
        view.open_recognition_button.click()
        self.assertEqual(opened_recognition, [True])
        view.close()


if __name__ == "__main__":
    unittest.main()
