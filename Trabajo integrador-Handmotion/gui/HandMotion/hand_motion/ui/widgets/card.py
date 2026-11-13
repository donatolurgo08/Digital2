"""Tarjeta reutilizable para paneles de la interfaz."""

from __future__ import annotations

from PySide6.QtWidgets import QFrame, QVBoxLayout, QLabel, QWidget


class Card(QFrame):
    """Contenedor con borde redondeado y título opcional."""

    def __init__(self, title: str = "", parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("Card")
        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(16, 14, 16, 14)
        self._layout.setSpacing(8)

        if title:
            title_label = QLabel(title.upper())
            title_label.setObjectName("CardTitle")
            self._layout.addWidget(title_label)

    def content_layout(self) -> QVBoxLayout:
        return self._layout