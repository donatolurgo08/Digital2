"""Gráfico en tiempo real del acelerómetro (eje X)."""

from __future__ import annotations

from collections import deque

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QCheckBox,
    QDoubleSpinBox, QSpinBox,
)
import pyqtgraph as pg

from hand_motion.processing.simulated_source import SimulatedAccelSource
from hand_motion.ui.styles.palette import (
    ACCENT_CYAN, ACCENT_MAGENTA, BG_SECONDARY, TEXT_PRIMARY, WARNING_AMBER,
)


class AccelerometerGraph(QWidget):
    """Visualización del eje X con datos en tiempo real (estilo osciloscopio)."""

    def __init__(self, buffer_size: int = 300, source=None, parent=None) -> None:
        super().__init__(parent)
        if buffer_size <= 0:
            raise ValueError("buffer_size debe ser mayor que cero")
        self.buffer_size = buffer_size
        self._values: deque[float] = deque(maxlen=buffer_size)
        self._times: deque[float] = deque(maxlen=buffer_size)
        self._counter = 0
        self._elapsed = 0.0
        self._scale_update_counter = 0

        self.source = source if source is not None else SimulatedAccelSource()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        # Controles
        controls = QHBoxLayout()
        self.start_btn = QPushButton("Iniciar")
        self.stop_btn = QPushButton("Detener")
        self.stop_btn.setObjectName("Danger")
        self.auto_scale_cb = QCheckBox("Auto escala")
        self.auto_scale_cb.setChecked(True)
        self.ymin_spin = QDoubleSpinBox()
        self.ymin_spin.setRange(-10.0, 10.0)
        self.ymin_spin.setValue(-2.0)
        self.ymax_spin = QDoubleSpinBox()
        self.ymax_spin.setRange(-10.0, 10.0)
        self.ymax_spin.setValue(2.0)
        self.rate_spin = QSpinBox()
        self.rate_spin.setRange(1, 200)
        self.rate_spin.setValue(50)
        self.rate_spin.setSuffix(" Hz")

        controls.addWidget(self.start_btn)
        controls.addWidget(self.stop_btn)
        controls.addWidget(QLabel("Rate"))
        controls.addWidget(self.rate_spin)
        controls.addWidget(self.auto_scale_cb)
        controls.addWidget(QLabel("Y min"))
        controls.addWidget(self.ymin_spin)
        controls.addWidget(QLabel("Y max"))
        controls.addWidget(self.ymax_spin)
        controls.addStretch()
        layout.addLayout(controls)

        # Gráfico
        self.plot = pg.PlotWidget()
        self.plot.setBackground(BG_SECONDARY)
        self.plot.showGrid(x=True, y=True, alpha=0.15)
        self.plot.setLabel("left", "Amplitud (eje X, unidades sin verificar)")
        self.plot.setLabel("bottom", "Tiempo (s, estimado)")
        self.curve = self.plot.plot(
            pen=pg.mkPen(ACCENT_CYAN, width=2, antialias=False)
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
        self.last_value_label = QLabel("Último valor: -- (unidades simuladas)")
        self.last_value_label.setStyleSheet(f"color:{TEXT_PRIMARY}; font-weight:600;")
        layout.addWidget(self.last_value_label)

        note = QLabel("⚠ Datos simulados (sin comunicación con el PIC)")
        note.setStyleSheet(f"color:{WARNING_AMBER}; font-size:11px;")
        layout.addWidget(note)

        # Conexiones
        self.start_btn.clicked.connect(self.start)
        self.stop_btn.clicked.connect(self.stop)
        self.rate_spin.valueChanged.connect(lambda v: self.source.set_sample_rate(float(v)))
        self.auto_scale_cb.toggled.connect(self._update_scale)
        self.ymin_spin.valueChanged.connect(self._update_scale)
        self.ymax_spin.valueChanged.connect(self._update_scale)
        self.source.sample.connect(self._on_sample)

    def start(self) -> None:
        self.source.start()
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)

    def stop(self) -> None:
        self.source.stop()
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)

    def _on_sample(self, value: float) -> None:
        rate = max(1.0, float(self.source.sample_rate_hz))
        self._elapsed += 1.0 / rate
        self._values.append(value)
        self._times.append(self._elapsed)
        self._counter += 1

        # Actualización fluida con buffer deslizante
        self.curve.setData(list(self._times), list(self._values))
        self.last_value_label.setText(f"Último valor: {value:.3f} (unidades simuladas)")

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