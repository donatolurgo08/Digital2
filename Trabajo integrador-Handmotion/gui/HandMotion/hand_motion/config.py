"""Configuración de enlace v1 y valores iniciales de la GUI."""

from __future__ import annotations

from hand_motion.communication.protocol import (
    DEFAULT_DATA_PERIOD_MS as PROTOCOL_DEFAULT_DATA_PERIOD_MS,
    MAX_DATA_PERIOD_MS as PROTOCOL_MAX_DATA_PERIOD_MS,
    MIN_DATA_PERIOD_MS as PROTOCOL_MIN_DATA_PERIOD_MS,
)


# --- Comunicación serial ---
DEFAULT_BAUD_RATE: int = 9600
SERIAL_FRAME_FORMAT: str = "8N1"
DEFAULT_DATA_PERIOD_MS: int = PROTOCOL_DEFAULT_DATA_PERIOD_MS  # PIC arranca a 20 Hz
MIN_DATA_PERIOD_MS: int = PROTOCOL_MIN_DATA_PERIOD_MS
MAX_DATA_PERIOD_MS: int = PROTOCOL_MAX_DATA_PERIOD_MS

# --- Supervisión térmica ---
TEMP_ALARM_THRESHOLD_C: float = 40.0  # valor inicial del firmware, configurable

# --- Acelerómetro ---
# Eje principal en la primera etapa (DEC-001).
PRIMARY_ACCEL_AXIS: str = "X"

# --- Simulación local (no representa el período del PIC) ---
SIMULATION_SAMPLE_RATE_HZ: float = 50.0
DISPLAY_REFRESH_HZ: float = 30.0
