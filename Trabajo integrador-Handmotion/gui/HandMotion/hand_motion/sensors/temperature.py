"""Sensor de temperatura LM35 (conectado a AN0).

Conversión preliminar: el LM35 entrega 10 mV/°C. El escalado final
dependerá de la referencia ADC del PIC (pendiente D-01).
"""

from __future__ import annotations


def raw_to_celsius(raw: int, vref: float = 5.0, resolution: int = 1024) -> float:
    """Convierte un valor ADC crudo a grados Celsius (placeholder)."""
    voltage = raw * vref / resolution
    return voltage / 0.01  # 10 mV/°C