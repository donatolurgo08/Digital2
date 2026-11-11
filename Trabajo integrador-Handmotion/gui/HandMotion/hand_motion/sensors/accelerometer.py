"""Unidades de aceleración recibidas del protocolo PIC.

El firmware transmite X en mg después de aplicar su offset y sensibilidad
nominales del MMA7361. Esta capa solo cambia unidades; no recalibra el sensor.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class AccelReading:
    x: float | None = None
    y: float | None = None  # futuro
    z: float | None = None  # futuro


def mg_to_g(acceleration_mg: int) -> float:
    """Convierte miligravedad a g; la exactitud depende de calibrar el MMA7361."""
    return acceleration_mg / 1000.0
