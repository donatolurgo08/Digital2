"""Unidades de aceleración recibidas del protocolo PIC.

El firmware transmite los ejes disponibles en mg después de aplicar sus offsets
y sensibilidades nominales/provisionales. Esta capa solo cambia unidades; no
recalibra el sensor.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class AccelReading:
    x: float | None = None
    y: float | None = None
    z: float | None = None


def mg_to_g(acceleration_mg: int) -> float:
    """Convierte miligravedad a g; la exactitud depende de calibrar el MMA7361."""
    return acceleration_mg / 1000.0
