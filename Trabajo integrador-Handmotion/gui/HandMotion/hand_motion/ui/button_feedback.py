"""Feedback visual breve para hover/pressed sin temporizadores propios."""

from __future__ import annotations

from PySide6.QtCore import QEasingCurve, QEvent, QObject, QPropertyAnimation
from PySide6.QtWidgets import QAbstractButton, QGraphicsOpacityEffect


class ButtonFeedback(QObject):
    """Anima levemente la opacidad de un botón al interactuar con él."""

    def __init__(self, button: QAbstractButton) -> None:
        super().__init__(button)
        self._button = button
        self._effect = QGraphicsOpacityEffect(button)
        self._effect.setOpacity(1.0)
        button.setGraphicsEffect(self._effect)

        self._animation = QPropertyAnimation(self._effect, b"opacity", self)
        self._animation.setDuration(100)
        self._animation.setEasingCurve(QEasingCurve.OutCubic)
        button.installEventFilter(self)

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:
        if watched is not self._button or not self._button.isEnabled():
            return super().eventFilter(watched, event)

        target = None
        if event.type() == QEvent.Enter:
            target = 0.94
        elif event.type() == QEvent.Leave:
            target = 1.0
        elif event.type() == QEvent.MouseButtonPress:
            target = 0.82
        elif event.type() == QEvent.MouseButtonRelease:
            target = 0.94 if self._button.underMouse() else 1.0

        if target is not None:
            self._animation.stop()
            self._animation.setStartValue(self._effect.opacity())
            self._animation.setEndValue(target)
            self._animation.start()
        return super().eventFilter(watched, event)
