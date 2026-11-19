"""Fuente XYZ simulada para el acelerómetro.

Genera muestras deterministas X/Y/Z sin depender de comunicación serial.
El procesamiento/generación vive aquí, separado de la visualización.
"""

from __future__ import annotations

import math

from PySide6.QtCore import QObject, QTimer, Signal


class SimulatedAccelSource(QObject):
    """Genera aceleración XYZ reproducible en reposo o durante movimiento."""

    sample = Signal(float)
    sample_xyz = Signal(float, float, float)

    def __init__(
        self,
        sample_rate_hz: float = 50.0,
        amplitude_g: float = 1.0,
        noise_g: float = 0.05,
        frequency_hz: float = 0.5,
        scenario: str = "movement",
        parent=None,
    ) -> None:
        super().__init__(parent)
        if scenario not in {"rest", "movement"}:
            raise ValueError("scenario debe ser 'rest' o 'movement'")
        self.sample_rate_hz = sample_rate_hz
        self.amplitude_g = amplitude_g
        self.noise_g = noise_g
        self.frequency_hz = frequency_hz
        self.scenario = scenario

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
        self._t = 0.0
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

    def set_scenario(self, scenario: str) -> None:
        if scenario not in {"rest", "movement"}:
            raise ValueError("scenario debe ser 'rest' o 'movement'")
        self.scenario = scenario
        self._t = 0.0

    def _emit_sample(self) -> None:
        phase = 2 * math.pi * self.frequency_hz * self._t
        if self.scenario == "rest":
            x, y, z = 0.0, 0.0, 1.0
        else:
            # Suaves variaciones periódicas deterministas; no representan una
            # calibración ni una orientación física concreta del sensor.
            ripple_x = self.noise_g * math.sin(phase * 3.0)
            ripple_y = self.noise_g * math.sin(phase * 3.0 + 1.2)
            ripple_z = self.noise_g * math.sin(phase * 2.0 + 2.4)
            x = self.amplitude_g * math.sin(phase) + ripple_x
            y = 0.75 * self.amplitude_g * math.sin(phase + 2.1) + ripple_y
            z = 0.65 + 0.35 * self.amplitude_g * math.sin(phase * 0.5 + 4.2)
            z += ripple_z
        self._t += 1.0 / self.sample_rate_hz
        self.sample.emit(x)  # señal X histórica para consumidores existentes
        self.sample_xyz.emit(x, y, z)
