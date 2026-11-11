"""Panel del acelerómetro (eje X)."""

from __future__ import annotations

from PySide6.QtWidgets import QWidget, QVBoxLayout, QProgressBar, QLabel

from hand_motion.ui.widgets.sensor_card import SensorCard
from hand_motion.ui.styles.palette import (
    ACCENT_CYAN, OK_GREEN, WARNING_AMBER,
)


class AccelerometerPanel(QWidget):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._card = SensorCard(
            title="Acelerómetro — Eje X",
            value="--",
            unit="MMA7361 · g nominales",
            status="SIN DATOS",
            status_color=WARNING_AMBER,
            value_color=ACCENT_CYAN,
            parent=self,
        )

        self.bar = QProgressBar()
        self.bar.setRange(-150, 150)
        self.bar.setValue(0)
        self.bar.setTextVisible(False)
        # Estilos centralizados en theme.qss

        # Agregados en orden explícito (sin depender de índices)
        self._card.add_widget(self.bar)

        self.note = QLabel("X usa sensibilidad nominal; Y/Z no se envían en protocolo v1.")
        self.note.setWordWrap(True)
        self.note.setStyleSheet(f"color: {WARNING_AMBER}; font-size: 11px;")
        self._card.add_widget(self.note)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(self._card)

    def update_value(self, value_g: float, live: bool = False) -> None:
        color = ACCENT_CYAN if live else WARNING_AMBER
        self._card.set_value(f"{value_g:+.3f} g", color)
        self._card.set_status("PIC · X nominal" if live else "SIMULACIÓN", OK_GREEN if live else WARNING_AMBER)
        self.bar.setValue(max(-150, min(150, round(value_g * 100))))

    def clear_value(self) -> None:
        self._card.set_value("--", ACCENT_CYAN)
        self._card.set_status("SIN DATOS", WARNING_AMBER)
        self.bar.setValue(0)
