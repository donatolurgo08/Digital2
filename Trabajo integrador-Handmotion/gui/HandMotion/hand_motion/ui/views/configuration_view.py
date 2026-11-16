"""Preferencias locales y estado de adquisición de la aplicación."""

from __future__ import annotations

from PySide6.QtCore import Signal, Qt
from PySide6.QtWidgets import (
    QDoubleSpinBox,
    QFormLayout,
    QGridLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from hand_motion.preferences import (
    GuiPreferences,
    MAX_GESTURE_HOLD_SAMPLES,
    MAX_GESTURE_THRESHOLD_G,
    MAX_GESTURE_WINDOW_SAMPLES,
    MAX_SIMULATION_RATE_HZ,
    MIN_GESTURE_HOLD_SAMPLES,
    MIN_GESTURE_THRESHOLD_G,
    MIN_GESTURE_WINDOW_SAMPLES,
    MIN_SIMULATION_RATE_HZ,
)
from hand_motion.ui.styles.palette import TEXT_SECONDARY, WARNING_AMBER
from hand_motion.ui.widgets.card import Card


class ConfigurationView(QWidget):
    """Ajustes compartidos de simulación y del clasificador XYZ."""

    preferences_changed = Signal(object)
    reset_baseline_requested = Signal()
    open_recognition_requested = Signal()

    def __init__(self, preferences: GuiPreferences, parent=None) -> None:
        super().__init__(parent)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        outer.addWidget(scroll)

        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(16)
        scroll.setWidget(content)

        acquisition = Card("Adquisición")
        acquisition_layout = QFormLayout()
        self.simulation_rate_spin = QSpinBox()
        self.simulation_rate_spin.setRange(
            MIN_SIMULATION_RATE_HZ, MAX_SIMULATION_RATE_HZ
        )
        self.simulation_rate_spin.setSuffix(" Hz")
        self.simulation_rate_spin.setToolTip(
            "Solo afecta la fuente SIMULACIÓN; no cambia la tasa del PIC."
        )
        acquisition_layout.addRow("Tasa de simulación", self.simulation_rate_spin)
        self.source_label = QLabel("Fuente activa: SIMULACIÓN")
        acquisition_layout.addRow("Fuente", self.source_label)
        self.device_period_label = QLabel(
            "El período del PIC se consulta mediante STATUS y se cambia en Monitor serial."
        )
        self.device_period_label.setWordWrap(True)
        self.device_period_label.setStyleSheet(
            f"color:{TEXT_SECONDARY}; font-size:11px;"
        )
        acquisition_layout.addRow("Dispositivo", self.device_period_label)
        self.serial_label = QLabel(
            "UART 9600 Bd · 8N1 (fijo por compatibilidad con el firmware)"
        )
        self.serial_label.setWordWrap(True)
        self.serial_label.setStyleSheet(
            f"color:{TEXT_SECONDARY}; font-size:11px;"
        )
        acquisition_layout.addRow("Comunicación", self.serial_label)
        acquisition.content_layout().addLayout(acquisition_layout)
        layout.addWidget(acquisition)

        recognition = Card("Reconocimiento")
        recognition_layout = QVBoxLayout()
        thresholds = QGridLayout()
        thresholds.addWidget(QLabel("Umbral (g)"), 0, 0)
        for column, axis in enumerate("XYZ", start=1):
            label = QLabel(axis)
            label.setAlignment(Qt.AlignCenter)
            thresholds.addWidget(label, 0, column)
        self.threshold_spins: list[QDoubleSpinBox] = []
        for column, axis in enumerate("XYZ", start=1):
            spin = QDoubleSpinBox()
            spin.setRange(MIN_GESTURE_THRESHOLD_G, MAX_GESTURE_THRESHOLD_G)
            spin.setSingleStep(0.05)
            spin.setDecimals(2)
            spin.setSuffix(" g")
            spin.setToolTip(
                f"Desviación mínima respecto del reposo para el eje {axis}"
            )
            thresholds.addWidget(spin, 1, column)
            self.threshold_spins.append(spin)
        recognition_layout.addLayout(thresholds)

        recognition_form = QFormLayout()
        self.window_spin = QSpinBox()
        self.window_spin.setRange(
            MIN_GESTURE_WINDOW_SAMPLES, MAX_GESTURE_WINDOW_SAMPLES
        )
        self.window_spin.setSuffix(" muestras")
        recognition_form.addRow("Ventana promedio", self.window_spin)
        self.hold_spin = QSpinBox()
        self.hold_spin.setRange(
            MIN_GESTURE_HOLD_SAMPLES, MAX_GESTURE_HOLD_SAMPLES
        )
        self.hold_spin.setSuffix(" muestras")
        self.hold_spin.setToolTip(
            "Clasificaciones consecutivas necesarias para confirmar un gesto"
        )
        recognition_form.addRow("Confirmación sostenida", self.hold_spin)
        recognition_layout.addLayout(recognition_form)

        self.baseline_label = QLabel("Reposo activo: sin capturar")
        self.baseline_label.setWordWrap(True)
        self.baseline_label.setStyleSheet(
            f"color:{TEXT_SECONDARY}; font-size:11px;"
        )
        recognition_layout.addWidget(self.baseline_label)
        self.baseline_note = QLabel(
            "El reposo se captura o edita en Reconocimiento. No se persiste: "
            "depende de la fuente y se limpia al cambiar entre simulación y dispositivo."
        )
        self.baseline_note.setWordWrap(True)
        self.baseline_note.setStyleSheet(
            f"color:{WARNING_AMBER}; font-size:11px;"
        )
        recognition_layout.addWidget(self.baseline_note)
        self.open_recognition_button = QPushButton("Abrir Reconocimiento")
        self.open_recognition_button.setObjectName("Secondary")
        self.open_recognition_button.clicked.connect(
            self.open_recognition_requested
        )
        recognition_layout.addWidget(self.open_recognition_button)
        recognition.content_layout().addLayout(recognition_layout)
        layout.addWidget(recognition)

        footer = QWidget()
        footer_layout = QFormLayout(footer)
        self.persistence_label = QLabel(
            "Tasa de simulación y parámetros del reconocedor se guardan localmente."
        )
        self.persistence_label.setWordWrap(True)
        self.persistence_label.setStyleSheet(
            f"color:{TEXT_SECONDARY}; font-size:11px;"
        )
        footer_layout.addRow(self.persistence_label)
        self.restore_button = QPushButton("Restaurar valores predeterminados")
        self.restore_button.setObjectName("Secondary")
        self.restore_button.clicked.connect(self._confirm_restore_defaults)
        footer_layout.addRow(self.restore_button)
        layout.addWidget(footer)
        layout.addStretch(1)

        self._connect_changes()
        self.set_preferences(preferences)

    def preferences(self) -> GuiPreferences:
        x_g, y_g, z_g = (spin.value() for spin in self.threshold_spins)
        return GuiPreferences(
            simulation_rate_hz=self.simulation_rate_spin.value(),
            threshold_x_g=x_g,
            threshold_y_g=y_g,
            threshold_z_g=z_g,
            window_samples=self.window_spin.value(),
            hold_samples=self.hold_spin.value(),
        )

    def set_preferences(self, preferences: GuiPreferences) -> None:
        widgets = [
            self.simulation_rate_spin,
            *self.threshold_spins,
            self.window_spin,
            self.hold_spin,
        ]
        previous_states = [widget.blockSignals(True) for widget in widgets]
        try:
            self.simulation_rate_spin.setValue(preferences.simulation_rate_hz)
            for spin, value in zip(
                self.threshold_spins,
                (
                    preferences.threshold_x_g,
                    preferences.threshold_y_g,
                    preferences.threshold_z_g,
                ),
            ):
                spin.setValue(value)
            self.window_spin.setValue(preferences.window_samples)
            self.hold_spin.setValue(preferences.hold_samples)
        finally:
            for widget, was_blocked in zip(widgets, previous_states):
                widget.blockSignals(was_blocked)

    def set_runtime_context(
        self,
        *,
        source_name: str,
        device_period_ms: int | None,
        baseline: tuple[float, float, float | None] | None,
    ) -> None:
        self.source_label.setText(f"Fuente activa: {source_name}")
        if device_period_ms is None:
            self.device_period_label.setText(
                "Período del dispositivo: esperando STATUS; "
                "se ajusta desde Monitor serial."
            )
        else:
            self.device_period_label.setText(
                f"Período informado por el PIC: {device_period_ms} ms; "
                "se ajusta desde Monitor serial (20–250 ms)."
            )
        if baseline is None:
            self.baseline_label.setText("Reposo activo: sin capturar")
        else:
            x_g, y_g, z_g = baseline
            z_text = (
                "Z -- (no disponible en v2)"
                if z_g is None
                else f"Z {z_g:+.3f} g"
            )
            self.baseline_label.setText(
                f"Reposo de {source_name.lower()}: X {x_g:+.3f} · "
                f"Y {y_g:+.3f} · {z_text}"
            )

    def restore_defaults(self, *, confirmed: bool) -> bool:
        """Restaura preferencias; el llamador persiste/aplica la señal emitida."""
        if not confirmed:
            return False
        preferences = GuiPreferences()
        self.set_preferences(preferences)
        self.preferences_changed.emit(preferences)
        self.reset_baseline_requested.emit()
        return True

    def _connect_changes(self) -> None:
        self.simulation_rate_spin.valueChanged.connect(self._emit_preferences)
        for spin in self.threshold_spins:
            spin.valueChanged.connect(self._emit_preferences)
        self.window_spin.valueChanged.connect(self._emit_preferences)
        self.hold_spin.valueChanged.connect(self._emit_preferences)

    def _emit_preferences(self, _value=None) -> None:
        self.preferences_changed.emit(self.preferences())

    def _confirm_restore_defaults(self) -> None:
        result = QMessageBox.question(
            self,
            "Restaurar valores",
            "Se restaurarán las preferencias locales y se borrará el reposo "
            "activo. ¿Continuar?",
            QMessageBox.Yes | QMessageBox.Cancel,
            QMessageBox.Cancel,
        )
        self.restore_defaults(confirmed=result == QMessageBox.Yes)
