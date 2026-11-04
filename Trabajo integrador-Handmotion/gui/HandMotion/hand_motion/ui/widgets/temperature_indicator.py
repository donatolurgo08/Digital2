"""Indicador de temperatura (LM35)."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel

from hand_motion.config import TEMP_ALARM_THRESHOLD_C
from hand_motion.ui.styles.palette import ACCENT_CYAN, ALARM_RED, OK_GREEN, TEXT_PRIMARY, TEXT_SECONDARY
from hand_motion.ui.widgets.sensor_card import SensorCard


class TemperatureIndicator(SensorCard):
    def __init__(self, parent=None) -> None:
        super().__init__(
            title="Temperatura",
            value="27.5",
            unit="°C  (LM35 / AN0)",
            status="NORMAL",
            status_color=OK_GREEN,
            value_color=ACCENT_CYAN,
            parent=parent,
        )

        threshold_label = QLabel(f"Umbral: {TEMP_ALARM_THRESHOLD_C:.0f} °C")
        threshold_label.setStyleSheet(f"color:{TEXT_SECONDARY}; font-size:11px;")
        threshold_label.setAlignment(Qt.AlignCenter)
        self.content_layout().addWidget(threshold_label)

    def update_temperature(self, value: float) -> None:
        if value > TEMP_ALARM_THRESHOLD_C:
            self.set_status("ALARMA", ALARM_RED)
            self.set_value(f"{value:.1f}", ALARM_RED)
        else:
            self.set_status("NORMAL", OK_GREEN)
            self.set_value(f"{value:.1f}", ACCENT_CYAN)