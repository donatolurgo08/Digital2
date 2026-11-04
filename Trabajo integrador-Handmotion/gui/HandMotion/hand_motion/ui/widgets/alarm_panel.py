"""Panel de alarmas (datos simulados)."""

from __future__ import annotations

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QFrame

from hand_motion.ui.widgets.card import Card
from hand_motion.ui.styles.palette import WARNING_AMBER


class AlarmPanel(QWidget):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        card = Card("Alarmas")
        layout = card.content_layout()

        self.banner = QFrame()
        self.banner.setObjectName("AlarmBanner")
        banner_layout = QVBoxLayout(self.banner)
        banner_layout.setContentsMargins(12, 8, 12, 8)
        self.banner_label = QLabel("Sin alarmas activas")
        self.banner_label.setStyleSheet("color: #fecaca; font-weight: 600;")
        banner_layout.addWidget(self.banner_label)
        layout.addWidget(self.banner)

        note = QLabel("⚠ Umbral fijo 40 °C (simulado)")
        note.setStyleSheet(f"color: {WARNING_AMBER}; font-size: 11px;")
        layout.addWidget(note)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(card)