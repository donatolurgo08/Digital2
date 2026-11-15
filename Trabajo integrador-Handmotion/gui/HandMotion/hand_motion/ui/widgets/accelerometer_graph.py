"""Gráfico en tiempo real de los ejes X, Y y Z del acelerómetro."""

from __future__ import annotations

from collections import deque

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QGridLayout, QLabel, QPushButton, QCheckBox,
    QDoubleSpinBox, QSpinBox, QComboBox,
)
import pyqtgraph as pg

from hand_motion.processing.simulated_source import SimulatedAccelSource
from hand_motion.ui.styles.palette import (
    ACCENT_CYAN, ACCENT_MAGENTA, ACCENT_VIOLET, BG_SECONDARY, TEXT_PRIMARY,
    WARNING_AMBER,
)


class AccelerometerGraph(QWidget):
    """Visualización en tiempo real de X/Y/Z (estilo osciloscopio)."""

    def __init__(self, buffer_size: int = 300, source=None, parent=None) -> None:
        super().__init__(parent)
        if buffer_size <= 0:
            raise ValueError("buffer_size debe ser mayor que cero")
        self.buffer_size = buffer_size
        self._values: deque[float] = deque(maxlen=buffer_size)
        self._y_values: deque[float] = deque(maxlen=buffer_size)
        self._z_values: deque[float] = deque(maxlen=buffer_size)
        self._times: deque[float] = deque(maxlen=buffer_size)
        self._counter = 0
        self._elapsed = 0.0
        self._scale_update_counter = 0
        self._device_mode = False

        self.source = source if source is not None else SimulatedAccelSource()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        # Controles
        controls = QGridLayout()
        self.start_btn = QPushButton("Iniciar")
        self.stop_btn = QPushButton("Detener")
        self.stop_btn.setObjectName("Danger")
        self.start_btn.setFixedWidth(82)
        self.stop_btn.setFixedWidth(82)
        self.stop_btn.setEnabled(False)
        self.auto_scale_cb = QCheckBox("Auto")
        self.auto_scale_cb.setToolTip("Escala vertical automática")
        self.auto_scale_cb.setChecked(True)
        self.ymin_spin = QDoubleSpinBox()
        self.ymin_spin.setRange(-10.0, 10.0)
        self.ymin_spin.setValue(-2.0)
        self.ymin_spin.setFixedWidth(76)
        self.ymax_spin = QDoubleSpinBox()
        self.ymax_spin.setRange(-10.0, 10.0)
        self.ymax_spin.setValue(2.0)
        self.ymax_spin.setFixedWidth(76)
        self.rate_spin = QSpinBox()
        self.rate_spin.setRange(1, 200)
        self.rate_spin.setValue(50)
        self.rate_spin.setFixedWidth(76)
        self.rate_spin.setSuffix(" Hz")
        self.scenario_combo = QComboBox()
        self.scenario_combo.addItem("Movimiento", "movement")
        self.scenario_combo.addItem("Reposo", "rest")
        self.scenario_combo.setCurrentIndex(
            self.scenario_combo.findData(self.source.scenario)
        )
        self.scenario_combo.setToolTip(
            "Escenario determinista de la fuente simulada"
        )
        self.scenario_combo.setFixedWidth(112)

        controls.addWidget(self.start_btn, 0, 0)
        controls.addWidget(self.stop_btn, 0, 1)
        controls.addWidget(QLabel("Tasa sim."), 0, 2)
        controls.addWidget(self.rate_spin, 0, 3)
        controls.addWidget(self.auto_scale_cb, 0, 4)
        controls.addWidget(QLabel("Mín."), 1, 0)
        controls.addWidget(self.ymin_spin, 1, 1)
        controls.addWidget(QLabel("Máx."), 1, 2)
        controls.addWidget(self.ymax_spin, 1, 3)
        controls.addWidget(self.scenario_combo, 1, 4)
        controls.setColumnStretch(5, 1)
        layout.addLayout(controls)

        # Gráfico
        self.plot = pg.PlotWidget()
        self.plot.setBackground(BG_SECONDARY)
        self.plot.showGrid(x=True, y=True, alpha=0.15)
        self.plot.setLabel("left", "Aceleración (g nominales)")
        self.plot.setLabel("bottom", "Tiempo (s, estimado)")
        self.plot.addLegend()
        self.curve = self.plot.plot(
            pen=pg.mkPen(ACCENT_CYAN, width=2, antialias=False),
            name="X",
        )
        self.curve_y = self.plot.plot(
            pen=pg.mkPen(ACCENT_MAGENTA, width=2, antialias=False),
            name="Y",
        )
        self.curve_z = self.plot.plot(
            pen=pg.mkPen(ACCENT_VIOLET, width=2, antialias=False),
            name="Z",
        )
        # Línea de referencia sutil en 0 (magenta, discreta)
        self.ref_line = pg.InfiniteLine(
            pos=0,
            angle=0,
            pen=pg.mkPen(ACCENT_MAGENTA, width=1, style=Qt.DashLine),
        )
        self.plot.addItem(self.ref_line)
        layout.addWidget(self.plot, 1)

        # Último valor
        self.last_value_label = QLabel(
            "Últimos valores — X: -- · Y: -- · Z: --"
        )
        self.last_value_label.setStyleSheet(f"color:{TEXT_PRIMARY}; font-weight:600;")
        layout.addWidget(self.last_value_label)

        self.note = QLabel(
            "Simulación XYZ determinista · PIC: calibración de Z pendiente."
        )
        self.note.setStyleSheet(f"color:{WARNING_AMBER}; font-size:11px;")
        layout.addWidget(self.note)

        # Conexiones
        self.start_btn.clicked.connect(self.start)
        self.stop_btn.clicked.connect(self.stop)
        self.rate_spin.valueChanged.connect(lambda v: self.source.set_sample_rate(float(v)))
        self.scenario_combo.currentIndexChanged.connect(
            lambda _: self.source.set_scenario(
                self.scenario_combo.currentData()
            )
        )
        self.auto_scale_cb.toggled.connect(self._update_scale)
        self.ymin_spin.valueChanged.connect(self._update_scale)
        self.ymax_spin.valueChanged.connect(self._update_scale)
        self.source.sample_xyz.connect(self._on_simulated_sample)

    def start(self) -> None:
        if self._device_mode:
            return
        self.source.start()
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)

    def stop(self) -> None:
        self.source.stop()
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)

    def set_device_mode(self, active: bool) -> None:
        """Selecciona la fuente PIC o simulada y no mezcla ambas series."""
        if active != self._device_mode:
            self._values.clear()
            self._y_values.clear()
            self._z_values.clear()
            self._times.clear()
            self._elapsed = 0.0
            self.curve.setData([], [])
            self.curve_y.setData([], [])
            self.curve_z.setData([], [])
            self.last_value_label.setText(
                "Últimos valores — X: -- · Y: -- · Z: --"
            )
        self._device_mode = active
        if active:
            self.source.stop()
            self.start_btn.setEnabled(False)
            self.stop_btn.setEnabled(False)
            self.rate_spin.setEnabled(False)
            self.scenario_combo.setEnabled(False)
            self.note.setText(
                "PIC · XYZ en g nominales; calibración de Z pendiente."
            )
            self.note.setStyleSheet(f"color:{WARNING_AMBER}; font-size:11px;")
        else:
            self.start_btn.setEnabled(not self.source.running)
            self.stop_btn.setEnabled(self.source.running)
            self.rate_spin.setEnabled(True)
            self.scenario_combo.setEnabled(True)
            self.note.setText(
                "Simulación XYZ determinista · PIC: calibración de Z pendiente."
            )
            self.note.setStyleSheet(f"color:{WARNING_AMBER}; font-size:11px;")

    def add_live_sample(
        self,
        x_g: float,
        period_ms: int = 50,
        y_g: float | None = None,
        z_g: float | None = None,
    ) -> None:
        if not self._device_mode:
            return
        rate = 1000.0 / max(1, period_ms)
        self._append_sample(x_g, rate, "PIC", y_g, z_g)

    def _on_simulated_sample(self, x_g: float, y_g: float, z_g: float) -> None:
        self._append_sample(
            x_g, float(self.source.sample_rate_hz), "SIMULACIÓN", y_g, z_g
        )

    def _append_sample(
        self,
        value: float,
        rate_hz: float,
        source_name: str,
        y_value: float | None,
        z_value: float | None,
    ) -> None:
        rate = max(1.0, rate_hz)
        self._elapsed += 1.0 / rate
        self._values.append(value)
        self._y_values.append(float("nan") if y_value is None else y_value)
        self._z_values.append(float("nan") if z_value is None else z_value)
        self._times.append(self._elapsed)
        self._counter += 1

        # Actualización fluida con buffer deslizante
        self.curve.setData(list(self._times), list(self._values))
        self.curve_y.setData(list(self._times), list(self._y_values))
        self.curve_z.setData(list(self._times), list(self._z_values))
        y_text = "--" if y_value is None else f"{y_value:+.3f} g"
        z_text = "--" if z_value is None else f"{z_value:+.3f} g"
        self.last_value_label.setText(
            f"Últimos valores ({source_name}) — X: {value:+.3f} g · "
            f"Y: {y_text} · Z: {z_text}"
        )

        # Auto-escala vertical con throttling para evitar saltos
        self._scale_update_counter += 1
        if self.auto_scale_cb.isChecked() and self._scale_update_counter % 30 == 0:
            self.plot.enableAutoRange(axis=pg.ViewBox.YAxis)
        elif not self.auto_scale_cb.isChecked():
            self.plot.setYRange(
                self.ymin_spin.value(), self.ymax_spin.value(), padding=0
            )

        # Seguimiento horizontal continuo
        if self._times:
            self.plot.setXRange(
                self._times[0], self._times[-1], padding=0.02
            )

    def _update_scale(self) -> None:
        if self.auto_scale_cb.isChecked():
            self.plot.enableAutoRange(axis=pg.ViewBox.YAxis)
        else:
            self.plot.setYRange(self.ymin_spin.value(), self.ymax_spin.value(), padding=0)
