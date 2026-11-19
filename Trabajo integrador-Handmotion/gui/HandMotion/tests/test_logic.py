"""Pruebas de lógica de alarmas."""

from hand_motion.logic.alarms import is_over_temperature
from hand_motion.config import TEMP_ALARM_THRESHOLD_C


def test_alarm_threshold() -> None:
    assert is_over_temperature(TEMP_ALARM_THRESHOLD_C + 0.1) is True
    assert is_over_temperature(TEMP_ALARM_THRESHOLD_C - 0.1) is False
    assert is_over_temperature(TEMP_ALARM_THRESHOLD_C) is False