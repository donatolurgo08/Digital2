"""Panel de estado de la alarma térmica reportada por el PIC."""

from __future__ import annotations

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QFrame

from hand_motion.ui.widgets.card import Card
from hand_motion.ui.styles.palette import ALARM_RED, OK_GREEN, WARNING_AMBER


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
        self.banner_label.setWordWrap(True)
        self.banner_label.setStyleSheet("color: #fecaca; font-weight: 600;")
        banner_layout.addWidget(self.banner_label)
        layout.addWidget(self.banner)

        self.note = QLabel("Esperando estado de alarma del PIC")
        self.note.setWordWrap(True)
        self.note.setStyleSheet(f"color: {WARNING_AMBER}; font-size: 11px;")
        layout.addWidget(self.note)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(card)
        self.set_waiting()

    def update_alarm(self, active: bool, threshold_c: int) -> None:
        if active:
            self.banner_label.setText("Alarma térmica activa · LED y buzzer")
            self.banner_label.setStyleSheet(f"color: {ALARM_RED}; font-weight: 600;")
            self.note.setText(f"Umbral configurado en el PIC: {threshold_c} °C")
            self.note.setStyleSheet(f"color: {ALARM_RED}; font-size: 11px;")
        else:
            self.banner_label.setText("Sin alarmas activas")
            self.banner_label.setStyleSheet(f"color: {OK_GREEN}; font-weight: 600;")
            self.note.setText(f"Umbral configurado en el PIC: {threshold_c} °C")
            self.note.setStyleSheet(f"color: {WARNING_AMBER}; font-size: 11px;")

    def set_waiting(self) -> None:
        self.banner_label.setText("Sin datos de alarma")
        self.banner_label.setStyleSheet(f"color: {WARNING_AMBER}; font-weight: 600;")
        self.note.setText("La alarma se actualiza con tramas DATA del PIC")
        self.note.setStyleSheet(f"color: {WARNING_AMBER}; font-size: 11px;")
