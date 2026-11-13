"""Fuente de datos simulada para el acelerómetro.

Genera muestras del eje X sin depender de comunicación serial.
El procesamiento/generación vive aquí, separado de la visualización.
"""

from __future__ import annotations

import math
import random

from PySide6.QtCore import QObject, QTimer, Signal


class SimulatedAccelSource(QObject):
    """Genera muestras simuladas del eje X a una tasa configurable."""

    sample = Signal(float)

    def __init__(
        self,
        sample_rate_hz: float = 50.0,
        amplitude_g: float = 1.0,
        noise_g: float = 0.05,
        frequency_hz: float = 0.5,
        parent=None,
    ) -> None:
        super().__init__(parent)
        self.sample_rate_hz = sample_rate_hz
        self.amplitude_g = amplitude_g
        self.noise_g = noise_g
        self.frequency_hz = frequency_hz

        self._timer = QTimer(self)
        self._timer.timeout.connect(self._emit_sample)
        self._t = 0.0
        self._running = False

    @property
    def running(self) -> bool:
        return self._running

    def start(self) -> None:
        if self._running:
            return
        self._running = True
        self._timer.start(max(1, int(1000.0 / self.sample_rate_hz)))

    def stop(self) -> None:
        self._running = False
        self._timer.stop()

    def set_sample_rate(self, hz: float) -> None:
        self.sample_rate_hz = hz
        if self._running:
            self.stop()
            self.start()

    def _emit_sample(self) -> None:
        value = self.amplitude_g * math.sin(
            2 * math.pi * self.frequency_hz * self._t
        ) + random.uniform(-self.noise_g, self.noise_g)
        self._t += 1.0 / self.sample_rate_hz
        self.sample.emit(value)