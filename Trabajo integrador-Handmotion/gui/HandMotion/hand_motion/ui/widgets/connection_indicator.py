"""Indicador de conexión con el PIC."""

from __future__ import annotations

from PySide6.QtCore import (
    QAbstractAnimation,
    QEasingCurve,
    QPropertyAnimation,
    QSequentialAnimationGroup,
)
from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel, QGraphicsOpacityEffect

from hand_motion.ui.styles.palette import ALARM_RED, OK_GREEN


class ConnectionIndicator(QWidget):
    def __init__(self, text: str = "Desconectado", connected: bool = False,
                 parent=None) -> None:
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)

        self._dot = QLabel("●")
        self._dot.setObjectName("StatusDot")
        self._dot_effect = QGraphicsOpacityEffect(self._dot)
        self._dot_effect.setOpacity(1.0)
        self._dot.setGraphicsEffect(self._dot_effect)
        self._pulse = QSequentialAnimationGroup(self)
        for start, end in ((1.0, 0.55), (0.55, 1.0)):
            animation = QPropertyAnimation(
                self._dot_effect, b"opacity", self._pulse
            )
            animation.setDuration(700)
            animation.setStartValue(start)
            animation.setEndValue(end)
            animation.setEasingCurve(QEasingCurve.InOutSine)
            self._pulse.addAnimation(animation)
        self._label = QLabel(text)
        layout.addWidget(self._dot)
        layout.addWidget(self._label)
        self.set_connected(connected)

    def set_connected(self, connected: bool, text: str | None = None) -> None:
        color = OK_GREEN if connected else ALARM_RED
        self._dot.setStyleSheet(f"color: {color}; font-size: 16px;")
        if connected:
            if self._pulse.state() != QAbstractAnimation.Running:
                self._pulse.setLoopCount(-1)
                self._pulse.start()
        else:
            self._pulse.stop()
            self._dot_effect.setOpacity(1.0)
        if text is not None:
            self._label.setText(text)
        else:
            self._label.setText("Conectado" if connected else "Desconectado")
