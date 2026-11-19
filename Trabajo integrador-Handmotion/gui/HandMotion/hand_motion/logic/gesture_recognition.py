"""Clasificación de inclinaciones X/Y/Z del MMA7361.

La GUI usa :class:`GestureRecognizer` para convertir muestras X/Y/Z en gestos
de inclinación sostenida (X+, X-, Y+, Y-, Z+, Z-) o reposo. Los umbrales y el
reposo los aporta el llamador: no hay valores de calibración del sensor
incorporados. El clasificador de X (``recognize_gesture``) se conserva como
modelo de referencia y por compatibilidad con las pruebas existentes.

Este módulo es puro: no depende de Qt ni de la interfaz.
"""

from __future__ import annotations

import math
from collections import deque
from dataclasses import dataclass
from statistics import fmean
from typing import Sequence


X_NEGATIVE = "X_NEGATIVE"
X_NEUTRAL = "X_NEUTRAL"
X_POSITIVE = "X_POSITIVE"
Y_NEGATIVE = "Y_NEGATIVE"
Y_POSITIVE = "Y_POSITIVE"
Z_NEGATIVE = "Z_NEGATIVE"
Z_POSITIVE = "Z_POSITIVE"
REST = "REST"

GESTURE_LABELS = {
    REST: "REPOSO",
    X_POSITIVE: "X+",
    X_NEGATIVE: "X-",
    Y_POSITIVE: "Y+",
    Y_NEGATIVE: "Y-",
    Z_POSITIVE: "Z+",
    Z_NEGATIVE: "Z-",
}

GESTURE_DESCRIPTIONS = {
    REST: "Sin inclinación dominante",
    X_POSITIVE: "Inclinación sostenida · eje X positivo",
    X_NEGATIVE: "Inclinación sostenida · eje X negativo",
    Y_POSITIVE: "Inclinación sostenida · eje Y positivo",
    Y_NEGATIVE: "Inclinación sostenida · eje Y negativo",
    Z_POSITIVE: "Inclinación sostenida · eje Z positivo",
    Z_NEGATIVE: "Inclinación sostenida · eje Z negativo",
}


def _finite(value: float, name: str) -> float:
    """Convierte a float y rechaza NaN/infinito con un mensaje explícito."""
    try:
        number = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{name} debe ser numérico") from exc
    if not math.isfinite(number):
        raise ValueError(f"{name} debe ser finito")
    return number


@dataclass(frozen=True)
class TiltBaseline:
    """Lectura de reposo en g; la captura la decide el usuario o la GUI."""

    x_g: float = 0.0
    y_g: float = 0.0
    z_g: float = 0.0

    def __post_init__(self) -> None:
        _finite(self.x_g, "baseline.x_g")
        _finite(self.y_g, "baseline.y_g")
        _finite(self.z_g, "baseline.z_g")


@dataclass(frozen=True)
class TiltThresholds:
    """Umbral mínimo de desviación por eje, en g. No son valores calibrados."""

    x_g: float
    y_g: float
    z_g: float

    def __post_init__(self) -> None:
        for name, value in (
            ("thresholds.x_g", self.x_g),
            ("thresholds.y_g", self.y_g),
            ("thresholds.z_g", self.z_g),
        ):
            if _finite(value, name) <= 0:
                raise ValueError(f"{name} debe ser mayor que cero")


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


def classify_tilt(
    x_g: float,
    y_g: float,
    z_g: float | None,
    *,
    baseline: TiltBaseline,
    thresholds: TiltThresholds,
) -> str:
    """Devuelve el eje/signo dominante o ``REST`` si nadie supera su umbral.

    ``z_g=None`` (DATA v2 sin Z) hace que solo se evalúen X e Y. El eje con la
    mayor desviación absoluta respecto del reposo gana; el empate se resuelve
    en el orden X, Y, Z.
    """
    x = _finite(x_g, "x_g")
    y = _finite(y_g, "y_g")
    z = None if z_g is None else _finite(z_g, "z_g")

    candidates = [
        (
            X_POSITIVE if x - baseline.x_g >= 0 else X_NEGATIVE,
            abs(x - baseline.x_g),
            thresholds.x_g,
        ),
        (
            Y_POSITIVE if y - baseline.y_g >= 0 else Y_NEGATIVE,
            abs(y - baseline.y_g),
            thresholds.y_g,
        ),
    ]
    if z is not None:
        candidates.append(
            (
                Z_POSITIVE if z - baseline.z_g >= 0 else Z_NEGATIVE,
                abs(z - baseline.z_g),
                thresholds.z_g,
            )
        )

    gesture, deviation, threshold = max(candidates, key=lambda item: item[1])
    if deviation < threshold:
        return REST
    return gesture


class GestureRecognizer:
    """Convierte una secuencia de muestras X/Y/Z en un gesto confirmado.

    - Promedia ``window_samples`` muestras para reducir ruido.
    - Exige ``hold_samples`` clasificaciones consecutivas iguales antes de
      confirmar un cambio (antirrebote).
    - Sin ``baseline`` no clasifica: la GUI debe capturar el reposo primero.
    """

    def __init__(
        self,
        *,
        thresholds: TiltThresholds,
        baseline: TiltBaseline | None = None,
        window_samples: int = 5,
        hold_samples: int = 3,
    ) -> None:
        if not isinstance(thresholds, TiltThresholds):
            raise TypeError("thresholds debe ser TiltThresholds")
        if baseline is not None and not isinstance(baseline, TiltBaseline):
            raise TypeError("baseline debe ser TiltBaseline o None")
        if window_samples < 1:
            raise ValueError("window_samples debe ser mayor que cero")
        if hold_samples < 1:
            raise ValueError("hold_samples debe ser mayor que cero")

        self._thresholds = thresholds
        self._baseline = baseline
        self._window_samples = window_samples
        self._hold_samples = hold_samples
        self._samples: deque[tuple[float, float, float | None]] = deque(
            maxlen=window_samples
        )
        self._candidate: str | None = None
        self._candidate_count = 0
        self._gesture: str | None = None

    @property
    def thresholds(self) -> TiltThresholds:
        return self._thresholds

    @property
    def baseline(self) -> TiltBaseline | None:
        return self._baseline

    @property
    def calibrated(self) -> bool:
        return self._baseline is not None

    @property
    def gesture(self) -> str | None:
        return self._gesture

    @property
    def window_samples(self) -> int:
        return self._window_samples

    @property
    def hold_samples(self) -> int:
        return self._hold_samples

    def set_thresholds(self, thresholds: TiltThresholds) -> None:
        if not isinstance(thresholds, TiltThresholds):
            raise TypeError("thresholds debe ser TiltThresholds")
        self._thresholds = thresholds
        self._reset_candidate()

    def set_window_samples(self, window_samples: int) -> None:
        if window_samples < 1:
            raise ValueError("window_samples debe ser mayor que cero")
        if window_samples == self._window_samples:
            return
        self._window_samples = window_samples
        self._samples = deque(maxlen=window_samples)
        self._reset_candidate()

    def set_hold_samples(self, hold_samples: int) -> None:
        if hold_samples < 1:
            raise ValueError("hold_samples debe ser mayor que cero")
        if hold_samples == self._hold_samples:
            return
        self._hold_samples = hold_samples
        self._reset_candidate()

    def set_baseline(self, baseline: TiltBaseline) -> None:
        if not isinstance(baseline, TiltBaseline):
            raise TypeError("baseline debe ser TiltBaseline")
        self._baseline = baseline
        self.reset()

    def clear_baseline(self) -> None:
        self._baseline = None
        self.reset()

    def reset(self) -> None:
        """Descarta muestras, candidato y gesto; conserva umbrales y reposo."""
        self._samples.clear()
        self._reset_candidate()
        self._gesture = None

    def current_mean(self) -> tuple[float, float, float | None] | None:
        """Media de las muestras retenidas; sirve para capturar el reposo."""
        if not self._samples:
            return None
        mean_x = fmean(sample[0] for sample in self._samples)
        mean_y = fmean(sample[1] for sample in self._samples)
        z_values = [sample[2] for sample in self._samples if sample[2] is not None]
        mean_z = fmean(z_values) if z_values else None
        return mean_x, mean_y, mean_z

    def add_sample(
        self, x_g: float, y_g: float, z_g: float | None = None
    ) -> str | None:
        """Agrega una muestra y devuelve el gesto confirmado o ``None``.

        Devuelve ``None`` mientras no haya reposo capturado o la ventana no
        esté completa. El gesto confirmado se conserva hasta que otro distinto
        supere el antirrebote.
        """
        x = _finite(x_g, "x_g")
        y = _finite(y_g, "y_g")
        z = None if z_g is None else _finite(z_g, "z_g")
        self._samples.append((x, y, z))

        if self._baseline is None or len(self._samples) < self._window_samples:
            return None

        mean_x, mean_y, mean_z = self.current_mean()  # type: ignore[misc]
        candidate = classify_tilt(
            mean_x,
            mean_y,
            mean_z,
            baseline=self._baseline,
            thresholds=self._thresholds,
        )

        if candidate == self._candidate:
            self._candidate_count += 1
        else:
            self._candidate = candidate
            self._candidate_count = 1

        if self._candidate_count >= self._hold_samples:
            self._gesture = candidate
        return self._gesture

    def _reset_candidate(self) -> None:
        self._candidate = None
        self._candidate_count = 0
