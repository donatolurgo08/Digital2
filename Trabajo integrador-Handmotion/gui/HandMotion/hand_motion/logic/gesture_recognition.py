"""Clasificador de estados sintéticos del eje X (modelo de referencia).

Este módulo todavía no se conecta a la GUI ni al firmware. Los umbrales son
obligatorios para que no se confundan los fixtures de prueba con la
calibración real del MMA7361. La salida describe dirección de X, no un gesto
final de la mano.
"""

from __future__ import annotations

import math
from statistics import fmean
from typing import Sequence


X_NEGATIVE = "X_NEGATIVE"
X_NEUTRAL = "X_NEUTRAL"
X_POSITIVE = "X_POSITIVE"


def recognize_gesture(
    samples: Sequence[float],
    *,
    negative_threshold_g: float,
    positive_threshold_g: float,
) -> str | None:
    """Clasifica una ventana como X negativo, neutro o positivo.

    Se usa la media de la ventana para tolerar ruido sintético. Los umbrales
    pertenecen al llamador: no hay valores por defecto ni valores calibrados
    para el sensor real. Devuelve ``None`` para una ventana vacía.
    """
    if not math.isfinite(negative_threshold_g) or not math.isfinite(positive_threshold_g):
        raise ValueError("Los umbrales deben ser valores finitos")
    if negative_threshold_g >= positive_threshold_g:
        raise ValueError("El umbral negativo debe ser menor que el positivo")
    if len(samples) == 0:
        return None
    if any(not math.isfinite(float(value)) for value in samples):
        raise ValueError("Las muestras deben ser valores finitos")

    average_x_g = fmean(samples)
    if average_x_g <= negative_threshold_g:
        return X_NEGATIVE
    if average_x_g >= positive_threshold_g:
        return X_POSITIVE
    return X_NEUTRAL
