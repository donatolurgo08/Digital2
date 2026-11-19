"""Pantalla provisional para secciones en desarrollo."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel

from hand_motion.ui.widgets.card import Card
from hand_motion.ui.styles.palette import TEXT_SECONDARY, ACCENT_CYAN


class PlaceholderView(QWidget):
    def __init__(self, title: str, parent=None) -> None:
        super().__init__(parent)
        outer = QVBoxLayout(self)
        outer.setContentsMargins(16, 16, 16, 16)

        card = Card(title)
        layout = card.content_layout()
        layout.addStretch(1)

        message = QLabel("Sección en desarrollo")
        message.setStyleSheet(f"color:{ACCENT_CYAN}; font-size:20px; font-weight:600;")
        message.setAlignment(Qt.AlignCenter)
        layout.addWidget(message)

        detail = QLabel("Esta funcionalidad se implementará en etapas posteriores.")
        detail.setStyleSheet(f"color:{TEXT_SECONDARY}; font-size:13px;")
        detail.setAlignment(Qt.AlignCenter)
        layout.addWidget(detail)

        layout.addStretch(1)
        outer.addWidget(card)