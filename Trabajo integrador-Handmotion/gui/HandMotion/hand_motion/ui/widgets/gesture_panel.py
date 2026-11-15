"""Panel de reconocimiento de inclinaciones y resumen para el dashboard."""

from __future__ import annotations

from PySide6.QtCore import Qt, QTime, Signal
from PySide6.QtWidgets import (
    QDoubleSpinBox,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSpinBox,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from hand_motion.config import (
    GESTURE_THRESHOLD_G,
    GESTURE_WINDOW_SAMPLES,
)
from hand_motion.logic.gesture_recognition import (
    GESTURE_DESCRIPTIONS,
    GESTURE_LABELS,
)
from hand_motion.ui.styles.palette import (
    ACCENT_CYAN,
    OK_GREEN,
    TEXT_SECONDARY,
    WARNING_AMBER,
)
from hand_motion.ui.widgets.card import Card


def _axis_spin(minimum: float, maximum: float, step: float, decimals: int) -> QDoubleSpinBox:
    spin = QDoubleSpinBox()
    spin.setRange(minimum, maximum)
    spin.setSingleStep(step)
    spin.setDecimals(decimals)
    spin.setSuffix(" g")
    spin.setAlignment(Qt.AlignRight)
    spin.setMinimumWidth(82)
    return spin


class GesturePanel(QWidget):
    """Gesto actual, valores en vivo y parámetros ajustables del clasificador."""

    thresholds_changed = Signal()
    baseline_changed = Signal()
    capture_rest_requested = Signal()
    reset_requested = Signal()

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._calibrated = False
        self._has_data = False
        self._gesture: str | None = None
        self._last_logged: str | None = None

        card = Card("Reconocimiento de gestos")
        layout = card.content_layout()

        self.result_label = QLabel("Gesto: --")
        self.result_label.setObjectName("CardValue")
        self.result_label.setStyleSheet(f"font-size: 30px; color: {ACCENT_CYAN};")
        self.result_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.result_label)

        self.detail_label = QLabel("Sin gesto confirmado")
        self.detail_label.setWordWrap(True)
        self.detail_label.setAlignment(Qt.AlignCenter)
        self.detail_label.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 12px;")
        layout.addWidget(self.detail_label)

        self.live_label = QLabel("X -- · Y -- · Z -- g")
        self.live_label.setAlignment(Qt.AlignCenter)
        self.live_label.setStyleSheet(
            f"color: {TEXT_SECONDARY}; font-family: 'Cascadia Code', 'Consolas', monospace;"
        )
        layout.addWidget(self.live_label)

        self.status_label = QLabel("SIN DATOS")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet(
            f"color: {WARNING_AMBER}; font-size: 11px; font-weight: 700;"
        )
        layout.addWidget(self.status_label)

        controls = QGridLayout()
        controls.setHorizontalSpacing(8)
        controls.setVerticalSpacing(6)
        for column, axis in enumerate("XYZ", start=1):
            header = QLabel(axis)
            header.setAlignment(Qt.AlignCenter)
            header.setStyleSheet(f"color: {TEXT_SECONDARY}; font-weight: 700;")
            controls.addWidget(header, 0, column)

        controls.addWidget(QLabel("Umbral"), 1, 0)
        self.threshold_spins = [
            _axis_spin(0.05, 2.0, 0.05, 2) for _ in range(3)
        ]
        for column, spin in enumerate(self.threshold_spins, start=1):
            spin.setValue(GESTURE_THRESHOLD_G)
            spin.setToolTip("Desviación mínima respecto del reposo para este eje")
            controls.addWidget(spin, 1, column)

        controls.addWidget(QLabel("Reposo"), 2, 0)
        self.baseline_spins = [
            _axis_spin(-2.0, 2.0, 0.01, 3) for _ in range(3)
        ]
        for column, spin in enumerate(self.baseline_spins, start=1):
            spin.setToolTip("Lectura de reposo de este eje; se puede capturar automáticamente")
            controls.addWidget(spin, 2, column)

        controls.addWidget(QLabel("Ventana"), 3, 0)
        self.window_spin = QSpinBox()
        self.window_spin.setRange(1, 25)
        self.window_spin.setValue(GESTURE_WINDOW_SAMPLES)
        self.window_spin.setSuffix(" muestras")
        self.window_spin.setToolTip(
            "Cantidad de muestras promediadas antes de clasificar"
        )
        controls.addWidget(self.window_spin, 3, 1, 1, 3)
        layout.addLayout(controls)

        buttons = QHBoxLayout()
        self.capture_button = QPushButton("Capturar reposo")
        self.capture_button.setObjectName("Primary")
        self.capture_button.setToolTip(
            "Toma la media de las últimas muestras como posición de reposo"
        )
        self.reset_button = QPushButton("Reiniciar")
        self.reset_button.setObjectName("Secondary")
        self.reset_button.setToolTip("Descarta la ventana y el gesto confirmado")
        buttons.addWidget(self.capture_button)
        buttons.addWidget(self.reset_button)
        buttons.addStretch(1)
        layout.addLayout(buttons)

        self.log = QTextEdit()
        self.log.setReadOnly(True)
        self.log.setMaximumHeight(96)
        self.log.setPlaceholderText(
            "El historial de gestos aparece al capturar el reposo."
        )
        layout.addWidget(self.log)

        note = QLabel(
            "Umbrales y reposo provisionales: ajustalos con el sensor real. "
            "El gesto se calcula en la GUI; el firmware solo transmite X/Y/Z."
        )
        note.setWordWrap(True)
        note.setStyleSheet(f"color: {WARNING_AMBER}; font-size: 11px;")
        layout.addWidget(note)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(card)

        for spin in self.threshold_spins:
            spin.valueChanged.connect(self._emit_thresholds_changed)
        self.window_spin.valueChanged.connect(self._emit_thresholds_changed)
        for spin in self.baseline_spins:
            spin.valueChanged.connect(self._emit_baseline_changed)
        self.capture_button.clicked.connect(self.capture_rest_requested)
        self.reset_button.clicked.connect(self.reset_requested)

    def thresholds(self) -> tuple[float, float, float]:
        return tuple(spin.value() for spin in self.threshold_spins)  # type: ignore[return-value]

    def baseline(self) -> tuple[float, float, float]:
        return tuple(spin.value() for spin in self.baseline_spins)  # type: ignore[return-value]

    def window_samples(self) -> int:
        return self.window_spin.value()

    def set_baseline(self, x_g: float, y_g: float, z_g: float) -> None:
        """Actualiza los campos de reposo sin reemitir ``baseline_changed``."""
        for spin, value in zip(self.baseline_spins, (x_g, y_g, z_g)):
            spin.blockSignals(True)
            spin.setValue(value)
            spin.blockSignals(False)

    def reset_baseline(self) -> None:
        """Vuelve los campos de reposo a cero sin emitir ``baseline_changed``."""
        for spin in self.baseline_spins:
            spin.blockSignals(True)
            spin.setValue(0.0)
            spin.blockSignals(False)

    def set_calibrated(self, calibrated: bool) -> None:
        self._calibrated = calibrated
        self._refresh_status()

    def set_live_values(self, x_g: float, y_g: float, z_g: float | None) -> None:
        z_text = "--" if z_g is None else f"{z_g:+.3f}"
        self.live_label.setText(f"X {x_g:+.3f} · Y {y_g:+.3f} · Z {z_text} g")
        self._has_data = True
        self._refresh_status()

    def set_data_unavailable(self) -> None:
        self._has_data = False
        self.live_label.setText("X -- · Y -- · Z -- g")
        self._refresh_status()

    def set_gesture(self, gesture: str | None) -> None:
        self._gesture = gesture
        if gesture is None:
            self._last_logged = None
            self.result_label.setText("Gesto: --")
            self.detail_label.setText("Sin gesto confirmado")
            return

        label = GESTURE_LABELS.get(gesture, gesture)
        description = GESTURE_DESCRIPTIONS.get(gesture, gesture)
        self.result_label.setText(f"Gesto: {label}")
        self.detail_label.setText(description)
        if gesture != self._last_logged:
            self._last_logged = gesture
            stamp = QTime.currentTime().toString("HH:mm:ss")
            self.append_log(f"{stamp} · {label} · {description}")

    def append_log(self, text: str) -> None:
        self.log.append(text)

    def _refresh_status(self) -> None:
        if not self._calibrated:
            text, color = "SIN CALIBRAR", WARNING_AMBER
        elif not self._has_data:
            text, color = "SIN DATOS", WARNING_AMBER
        else:
            text, color = "RECONOCIENDO", OK_GREEN
        self.status_label.setText(text)
        self.status_label.setStyleSheet(
            f"color: {color}; font-size: 11px; font-weight: 700;"
        )

    def _emit_thresholds_changed(self, _value=None) -> None:
        self.thresholds_changed.emit()

    def _emit_baseline_changed(self, _value=None) -> None:
        self.baseline_changed.emit()


class GestureSummary(QWidget):
    """Tarjeta compacta del dashboard con el último gesto confirmado."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        card = Card("Gesto actual")
        layout = card.content_layout()
        layout.addStretch(1)

        self.result_label = QLabel("Gesto: --")
        self.result_label.setObjectName("CardValue")
        self.result_label.setStyleSheet(f"font-size: 26px; color: {ACCENT_CYAN};")
        self.result_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.result_label)

        self.detail_label = QLabel("Sin datos · ver sección Reconocimiento")
        self.detail_label.setWordWrap(True)
        self.detail_label.setAlignment(Qt.AlignCenter)
        self.detail_label.setStyleSheet(
            f"color: {TEXT_SECONDARY}; font-size: 11px;"
        )
        layout.addWidget(self.detail_label)
        layout.addStretch(1)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(card)

    def set_gesture(self, gesture: str | None) -> None:
        if gesture is None:
            self.result_label.setText("Gesto: --")
            self.detail_label.setText("Sin datos · ver sección Reconocimiento")
            return
        self.result_label.setText(f"Gesto: {GESTURE_LABELS.get(gesture, gesture)}")
        self.detail_label.setText(GESTURE_DESCRIPTIONS.get(gesture, gesture))
