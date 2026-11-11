"""Área reservada al reconocimiento de gestos aún no definido."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QTextEdit

from hand_motion.ui.widgets.card import Card
from hand_motion.ui.styles.palette import ACCENT_CYAN


class GesturePanel(QWidget):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        card = Card("Reconocimiento de movimientos")
        layout = card.content_layout()

        self.result_label = QLabel("Gesto: --")
        self.result_label.setObjectName("CardValue")
        self.result_label.setStyleSheet(f"font-size: 22px; color: {ACCENT_CYAN};")
        self.result_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.result_label)

        self.log = QTextEdit()
        self.log.setReadOnly(True)
        self.log.setPlaceholderText("El reconocimiento de gestos aún no está implementado.")
        # Estilos centralizados en theme.qss
        self.log.append("Pendiente: definir gestos y calibrar el MMA7361.")
        layout.addWidget(self.log)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(card)
