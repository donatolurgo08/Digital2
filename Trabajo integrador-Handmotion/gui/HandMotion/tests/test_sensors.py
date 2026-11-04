"""Pruebas de funciones puras de sensores."""

from hand_motion.sensors.temperature import raw_to_celsius
from hand_motion.sensors.accelerometer import raw_to_g
from hand_motion.processing.signal_processor import moving_average
import numpy as np


def test_raw_to_celsius() -> None:
    assert abs(raw_to_celsius(0) - 0.0) < 1e-9
    # 1023 counts con Vref 5V -> ~5V -> 500 °C (LM35 10mV/°C)
    assert raw_to_celsius(1023) > 499


def test_raw_to_g_zero() -> None:
    assert abs(raw_to_g(512) - 0.0) < 1e-9


def test_moving_average() -> None:
    samples = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
    out = moving_average(samples, window=3)
    assert out.shape == samples.shape


def test_moving_average_invalid_window() -> None:
    try:
        moving_average(np.array([1.0, 2.0]), window=0)
    except ValueError:
        return
    raise AssertionError("Se esperaba ValueError")