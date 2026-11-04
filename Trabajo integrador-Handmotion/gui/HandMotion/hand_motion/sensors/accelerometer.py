"""Acelerómetro ADXL335 (módulo GY-61).

Primera etapa: solo eje X (DEC-001). Y y Z quedan reservados para
ampliaciones futuras sin modificar el flujo general.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class AccelReading:
    x: float | None = None
    y: float | None = None  # futuro
    z: float | None = None  # futuro


def raw_to_g(raw: int, zero_g: int = 512, sensitivity_mv_per_g: float = 300.0,
            vref: float = 5.0, resolution: int = 1024) -> float:
    """Convierte un valor ADC crudo del eje a unidades g (placeholder)."""
    voltage = raw * vref / resolution
    zero_voltage = zero_g * vref / resolution
    return (voltage - zero_voltage) / (sensitivity_mv_per_g / 1000.0)