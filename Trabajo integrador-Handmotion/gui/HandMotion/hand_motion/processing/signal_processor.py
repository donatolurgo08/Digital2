"""Procesamiento de señales del acelerómetro.

Funciones puras basadas en NumPy. Se implementarán filtros, suavizado y
cálculo de features para el reconocimiento de gestos (tarea A-02).
"""

from __future__ import annotations

import numpy as np


def moving_average(samples: np.ndarray, window: int = 5) -> np.ndarray:
    """Media móvil simple. Placeholder inicial."""
    if window <= 0:
        raise ValueError("window debe ser positivo")
    kernel = np.ones(window) / window
    return np.convolve(samples, kernel, mode="same")