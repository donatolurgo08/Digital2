"""Conversión auxiliar del LM35 para datos ADC crudos.

La telemetría real del protocolo ya llega en °C, convertida por el PIC usando
su referencia VDD; esta función queda para análisis offline de cuentas ADC.
"""

from __future__ import annotations


def raw_to_celsius(raw: int, vref: float = 5.0, resolution: int = 1024) -> float:
    """Convierte cuentas ADC a °C suponiendo LM35 a 10 mV/°C."""
    voltage = raw * vref / resolution
    return voltage / 0.01  # 10 mV/°C
