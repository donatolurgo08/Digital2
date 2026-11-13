"""Tarjeta genérica reutilizable para mostrar el valor de un sensor."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel

from hand_motion.ui.widgets.card import Card
from hand_motion.ui.styles.palette import TEXT_PRIMARY, TEXT_SECONDARY


class SensorCard(QWidget):
    """Tarjeta configurable para un sensor (título, valor, unidad, estado)."""

    def __init__(
        self,
        title: str,
        value: str = "--",
        unit: str = "",
        status: str = "",
        status_color: str = TEXT_SECONDARY,
        value_color: str = TEXT_PRIMARY,
        parent=None,
    ) -> None:
        super().__init__(parent)
        self.card = Card(title)
        layout = self.card.content_layout()

        self.value_label = QLabel(value)
        self.value_label.setObjectName("CardValue")
        self.value_label.setStyleSheet(f"color: {value_color};")
        self.value_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.value_label)

        if unit:
            unit_label = QLabel(unit)
            unit_label.setObjectName("CardUnit")
            unit_label.setAlignment(Qt.AlignCenter)
            layout.addWidget(unit_label)

        if status:
            self.status_label = QLabel(status)
            self.status_label.setStyleSheet(f"color: {status_color};")
            self.status_label.setAlignment(Qt.AlignCenter)
            layout.addWidget(self.status_label)
        else:
            self.status_label = None

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(self.card)

    def content_layout(self):
        return self.card.content_layout()

    def add_widget(self, widget) -> None:
        self.card.content_layout().addWidget(widget)

    def set_value(self, value: str, value_color: str | None = None) -> None:
        self.value_label.setText(value)
        if value_color:
            self.value_label.setStyleSheet(f"color: {value_color};")

    def set_status(self, status: str, color: str | None = None) -> None:
        if self.status_label is not None:
            self.status_label.setText(status)
            if color:
                self.status_label.setStyleSheet(f"color: {color};")