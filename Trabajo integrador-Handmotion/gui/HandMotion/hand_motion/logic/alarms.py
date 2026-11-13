"""Comparación auxiliar de temperatura con umbral configurable."""

from __future__ import annotations

from hand_motion.config import TEMP_ALARM_THRESHOLD_C


def is_over_temperature(
    temp_c: float, threshold_c: float = TEMP_ALARM_THRESHOLD_C
) -> bool:
    return temp_c > threshold_c
