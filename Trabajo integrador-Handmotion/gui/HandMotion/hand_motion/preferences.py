"""Preferencias locales de la GUI, persistidas con QSettings."""

from __future__ import annotations

import math
from dataclasses import dataclass

from PySide6.QtCore import QSettings

from hand_motion.config import (
    GESTURE_HOLD_SAMPLES,
    GESTURE_THRESHOLD_G,
    GESTURE_WINDOW_SAMPLES,
    SIMULATION_SAMPLE_RATE_HZ,
)

MIN_SIMULATION_RATE_HZ = 1
MAX_SIMULATION_RATE_HZ = 200
MIN_GESTURE_THRESHOLD_G = 0.05
MAX_GESTURE_THRESHOLD_G = 2.0
MIN_GESTURE_WINDOW_SAMPLES = 1
MAX_GESTURE_WINDOW_SAMPLES = 25
MIN_GESTURE_HOLD_SAMPLES = 1
MAX_GESTURE_HOLD_SAMPLES = 20


@dataclass(frozen=True)
class GuiPreferences:
    """Preferencias de simulación y clasificación; el reposo no se persiste."""

    simulation_rate_hz: int = int(SIMULATION_SAMPLE_RATE_HZ)
    threshold_x_g: float = GESTURE_THRESHOLD_G
    threshold_y_g: float = GESTURE_THRESHOLD_G
    threshold_z_g: float = GESTURE_THRESHOLD_G
    window_samples: int = GESTURE_WINDOW_SAMPLES
    hold_samples: int = GESTURE_HOLD_SAMPLES

    def __post_init__(self) -> None:
        if not MIN_SIMULATION_RATE_HZ <= self.simulation_rate_hz <= MAX_SIMULATION_RATE_HZ:
            raise ValueError("La tasa de simulación debe estar entre 1 y 200 Hz")
        for axis, threshold in (
            ("X", self.threshold_x_g),
            ("Y", self.threshold_y_g),
            ("Z", self.threshold_z_g),
        ):
            value = float(threshold)
            if not math.isfinite(value) or not (
                MIN_GESTURE_THRESHOLD_G <= value <= MAX_GESTURE_THRESHOLD_G
            ):
                raise ValueError(f"El umbral de {axis} debe estar entre 0.05 y 2 g")
        if not MIN_GESTURE_WINDOW_SAMPLES <= self.window_samples <= MAX_GESTURE_WINDOW_SAMPLES:
            raise ValueError("La ventana debe estar entre 1 y 25 muestras")
        if not MIN_GESTURE_HOLD_SAMPLES <= self.hold_samples <= MAX_GESTURE_HOLD_SAMPLES:
            raise ValueError("La confirmación debe estar entre 1 y 20 muestras")


class GuiPreferencesStore:
    """Carga y guarda preferencias; admite QSettings o un backend compatible."""

    def __init__(self, settings=None) -> None:
        self._settings = settings or QSettings("ED2 - Hand Motion", "Hand Motion")

    def load(self) -> GuiPreferences:
        defaults = GuiPreferences()
        return GuiPreferences(
            simulation_rate_hz=self._read_int(
                "acquisition/simulation_rate_hz",
                defaults.simulation_rate_hz,
                MIN_SIMULATION_RATE_HZ,
                MAX_SIMULATION_RATE_HZ,
            ),
            threshold_x_g=self._read_float(
                "recognition/threshold_x_g", defaults.threshold_x_g
            ),
            threshold_y_g=self._read_float(
                "recognition/threshold_y_g", defaults.threshold_y_g
            ),
            threshold_z_g=self._read_float(
                "recognition/threshold_z_g", defaults.threshold_z_g
            ),
            window_samples=self._read_int(
                "recognition/window_samples",
                defaults.window_samples,
                MIN_GESTURE_WINDOW_SAMPLES,
                MAX_GESTURE_WINDOW_SAMPLES,
            ),
            hold_samples=self._read_int(
                "recognition/hold_samples",
                defaults.hold_samples,
                MIN_GESTURE_HOLD_SAMPLES,
                MAX_GESTURE_HOLD_SAMPLES,
            ),
        )

    def save(self, preferences: GuiPreferences) -> None:
        if not isinstance(preferences, GuiPreferences):
            raise TypeError("preferences debe ser GuiPreferences")
        self._settings.setValue(
            "acquisition/simulation_rate_hz", preferences.simulation_rate_hz
        )
        self._settings.setValue(
            "recognition/threshold_x_g", preferences.threshold_x_g
        )
        self._settings.setValue(
            "recognition/threshold_y_g", preferences.threshold_y_g
        )
        self._settings.setValue(
            "recognition/threshold_z_g", preferences.threshold_z_g
        )
        self._settings.setValue(
            "recognition/window_samples", preferences.window_samples
        )
        self._settings.setValue(
            "recognition/hold_samples", preferences.hold_samples
        )
        self._settings.sync()

    def reset(self) -> GuiPreferences:
        preferences = GuiPreferences()
        self.save(preferences)
        return preferences

    def _read_int(self, key: str, default: int, minimum: int, maximum: int) -> int:
        try:
            value = int(self._settings.value(key, default))
        except (TypeError, ValueError):
            return default
        return value if minimum <= value <= maximum else default

    def _read_float(self, key: str, default: float) -> float:
        try:
            value = float(self._settings.value(key, default))
        except (TypeError, ValueError):
            return default
        return (
            value
            if math.isfinite(value)
            and MIN_GESTURE_THRESHOLD_G <= value <= MAX_GESTURE_THRESHOLD_G
            else default
        )
