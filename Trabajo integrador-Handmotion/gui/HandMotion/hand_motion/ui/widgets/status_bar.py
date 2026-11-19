"""Barra de estado inferior."""

from __future__ import annotations

from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel

from hand_motion.ui.styles.palette import BG_SECONDARY, SEPARATOR, TEXT_SECONDARY, WARNING_AMBER, ACCENT_CYAN


class StatusBar(QWidget):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setStyleSheet(f"background:{BG_SECONDARY}; border-top:1px solid {SEPARATOR};")
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 6, 12, 6)

        self.message = QLabel("Listo")
        self.message.setStyleSheet(f"color:{TEXT_SECONDARY}; font-size:11px;")
        layout.addWidget(self.message)
        layout.addStretch()

        self.mode = QLabel("MODO: SIMULACIÓN")
        self.mode.setStyleSheet(f"color:{WARNING_AMBER}; font-size:11px; font-weight:600;")
        layout.addWidget(self.mode)

    def set_message(self, text: str) -> None:
        self.message.setText(text)

    def set_mode(self, text: str, color: str) -> None:
        self.mode.setText(text)
        self.mode.setStyleSheet(f"color:{color}; font-size:11px; font-weight:600;")