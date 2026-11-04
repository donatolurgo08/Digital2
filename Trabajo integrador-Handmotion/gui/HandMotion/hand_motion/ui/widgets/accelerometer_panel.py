"""Panel del acelerómetro (eje X)."""

from __future__ import annotations

from PySide6.QtWidgets import QWidget, QVBoxLayout, QProgressBar, QLabel

from hand_motion.ui.widgets.sensor_card import SensorCard
from hand_motion.ui.styles.palette import ACCENT_CYAN, TEXT_SECONDARY, WARNING_AMBER


class AccelerometerPanel(QWidget):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._card = SensorCard(
            title="Acelerómetro — Eje X",
            value="0.12 g",
            unit="ADXL335 (GY-61)",
            status="LECTURA SIMULADA",
            status_color=WARNING_AMBER,
            value_color=ACCENT_CYAN,
            parent=self,
        )

        self.bar = QProgressBar()
        self.bar.setRange(-100, 100)
        self.bar.setValue(12)
        self.bar.setTextVisible(False)
        # Estilos centralizados en theme.qss

        # Agregados en orden explícito (sin depender de índices)
        self._card.add_widget(self.bar)

        note = QLabel("⚠ Valor simulado (Y/Z reservados)")
        note.setStyleSheet(f"color: {WARNING_AMBER}; font-size: 11px;")
        self._card.add_widget(note)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(self._card)

    def update_value(self, value_g: float) -> None:
        self._card.set_value(f"{value_g:.2f} g", ACCENT_CYAN)
        self.bar.setValue(int(value_g * 100))