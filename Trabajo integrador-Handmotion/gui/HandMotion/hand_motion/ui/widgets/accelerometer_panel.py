"""Panel reutilizable de un eje del acelerómetro."""

from __future__ import annotations

from PySide6.QtCore import (
    QAbstractAnimation,
    QEasingCurve,
    QPropertyAnimation,
    QSequentialAnimationGroup,
    Qt,
)
from PySide6.QtWidgets import (
    QGraphicsOpacityEffect,
    QWidget,
    QVBoxLayout,
    QProgressBar,
    QLabel,
)

from hand_motion.ui.widgets.sensor_card import SensorCard
from hand_motion.ui.styles.palette import (
    ACCENT_CYAN,
    ACCENT_MAGENTA,
    ACCENT_VIOLET,
    OK_GREEN,
    TEXT_MUTED,
    WARNING_AMBER,
)


class AccelerometerPanel(QWidget):
    def __init__(
        self, axis: str = "X", parent=None, show_note: bool = True
    ) -> None:
        super().__init__(parent)
        if axis not in {"X", "Y", "Z"}:
            raise ValueError("axis debe ser X, Y o Z")
        self.axis = axis
        self._accent = {
            "X": ACCENT_CYAN,
            "Y": ACCENT_MAGENTA,
            "Z": ACCENT_VIOLET,
        }[axis]
        self._card = SensorCard(
            title=f"Acelerómetro — Eje {axis}",
            value="--",
            unit="MMA7361 · g nominales",
            status="SIN DATOS",
            status_color=WARNING_AMBER,
            value_color=self._accent,
            parent=self,
        )
        # Permite acomodar tres tarjetas de eje en el dashboard sin imponer
        # un ancho mínimo mayor que el área disponible.
        for label in self._card.findChildren(QLabel):
            if label.objectName() in {"CardTitle", "CardUnit"}:
                label.setWordWrap(True)

        self.bar = QProgressBar()
        self.bar.setRange(-150, 150)
        self.bar.setValue(0)
        self.bar.setTextVisible(False)
        self.bar.setStyleSheet(
            "QProgressBar::chunk {"
            f" background-color: {self._accent}; border-radius: 7px;"
            " }"
        )

        # Agregados en orden explícito (sin depender de índices)
        self._card.add_widget(self.bar)

        self.activity_dot = QLabel("●")
        self.activity_dot.setAlignment(Qt.AlignCenter)
        self.activity_dot.setFixedHeight(12)
        self._activity_effect = QGraphicsOpacityEffect(self.activity_dot)
        self._activity_effect.setOpacity(1.0)
        self.activity_dot.setGraphicsEffect(self._activity_effect)
        self._activity_pulse = QSequentialAnimationGroup(self)
        for start, end in ((1.0, 0.55), (0.55, 1.0)):
            animation = QPropertyAnimation(
                self._activity_effect, b"opacity", self._activity_pulse
            )
            animation.setDuration(700)
            animation.setStartValue(start)
            animation.setEndValue(end)
            animation.setEasingCurve(QEasingCurve.InOutSine)
            self._activity_pulse.addAnimation(animation)
        self._card.add_widget(self.activity_dot)
        self._set_activity(False)

        notes = {
            "X": "Offset ajustable; sensibilidad nominal.",
            "Y": "Offset 0 g nominal: 338 cuentas; calibración física pendiente.",
            "Z": "Parámetros provisionales; calibración física pendiente.",
        }
        note = notes[axis]
        self.note = QLabel(note)
        self.note.setWordWrap(True)
        self.note.setStyleSheet(f"color: {WARNING_AMBER}; font-size: 11px;")
        self._card.add_widget(self.note)
        self.note.setVisible(show_note)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(self._card)

    def update_value(self, value_g: float | None, live: bool = False) -> None:
        if value_g is None:
            self.clear_value()
            return
        self._set_activity(True)
        color = self._accent if live else WARNING_AMBER
        self._card.set_value(f"{value_g:+.3f} g", color)
        label = f"PIC · {self.axis} nominal" if live else "SIMULACIÓN"
        self._card.set_status(label, OK_GREEN if live else WARNING_AMBER)
        self.bar.setValue(max(-150, min(150, round(value_g * 100))))

    def clear_value(self) -> None:
        self._set_activity(False)
        self._card.set_value("--", self._accent)
        self._card.set_status("SIN DATOS", WARNING_AMBER)
        self.bar.setValue(0)

    def _set_activity(self, active: bool) -> None:
        color = self._accent if active else TEXT_MUTED
        self.activity_dot.setStyleSheet(
            f"color:{color}; font-size:10px; background:transparent;"
        )
        if active:
            if self._activity_pulse.state() != QAbstractAnimation.Running:
                self._activity_pulse.setLoopCount(-1)
                self._activity_pulse.start()
        else:
            self._activity_pulse.stop()
            self._activity_effect.setOpacity(1.0)
