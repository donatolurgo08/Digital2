"""Indicador de temperatura (LM35)."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel

from hand_motion.config import TEMP_ALARM_THRESHOLD_C
from hand_motion.ui.styles.palette import (
    ACCENT_CYAN, ALARM_RED, OK_GREEN, TEXT_SECONDARY, WARNING_AMBER,
)
from hand_motion.ui.widgets.sensor_card import SensorCard


class TemperatureIndicator(SensorCard):
    def __init__(self, parent=None) -> None:
        super().__init__(
            title="Temperatura",
            value="--",
            unit="°C  (LM35 / AN0)",
            status="SIN DATOS",
            status_color=WARNING_AMBER,
            value_color=ACCENT_CYAN,
            parent=parent,
        )

        self.threshold_c = TEMP_ALARM_THRESHOLD_C
        self.threshold_label = QLabel()
        self.threshold_label.setStyleSheet(f"color:{TEXT_SECONDARY}; font-size:11px;")
        self.threshold_label.setAlignment(Qt.AlignCenter)
        self.content_layout().addWidget(self.threshold_label)
        self.set_threshold(self.threshold_c)

    def update_temperature(self, value: float, alarm_active: bool | None = None) -> None:
        active = value > self.threshold_c if alarm_active is None else alarm_active
        if active:
            self.set_status("ALARMA", ALARM_RED)
            self.set_value(f"{value:.0f}", ALARM_RED)
        else:
            self.set_status("NORMAL", OK_GREEN)
            self.set_value(f"{value:.0f}", ACCENT_CYAN)

    def set_threshold(self, threshold_c: int) -> None:
        self.threshold_c = int(threshold_c)
        self.threshold_label.setText(f"Umbral PIC: {self.threshold_c} °C")

    def clear_reading(self) -> None:
        self.set_value("--", ACCENT_CYAN)
        self.set_status("SIN DATOS", WARNING_AMBER)
