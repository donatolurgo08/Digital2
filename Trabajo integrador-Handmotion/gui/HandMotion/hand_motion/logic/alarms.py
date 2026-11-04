"""Evaluación de alarmas (sobretemperatura).

Umbral fijo de 40 °C (DEC-008). Independiente del reconocimiento de
movimientos.
"""

from __future__ import annotations

from hand_motion.config import TEMP_ALARM_THRESHOLD_C


def is_over_temperature(temp_c: float) -> bool:
    return temp_c > TEMP_ALARM_THRESHOLD_C