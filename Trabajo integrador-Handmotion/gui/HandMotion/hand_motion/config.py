"""Configuración y constantes globales de Hand Motion.

Los valores definitivos de varios parámetros dependen del firmware y del
hardware (frecuencia de oscilador, baud rate, canales ADC, etc.) y se
ajustarán cuando se definan. Por ahora se usan valores iniciales razonables.
"""

from __future__ import annotations


# --- Comunicación serial ---
DEFAULT_BAUD_RATE: int = 9600
DEFAULT_TIMEOUT_S: float = 1.0

# --- Supervisión térmica ---
TEMP_ALARM_THRESHOLD_C: float = 40.0  # umbral fijo (DEC-008)

# --- Acelerómetro ---
# Eje principal en la primera etapa (DEC-001).
PRIMARY_ACCEL_AXIS: str = "X"

# --- Muestreo / visualización (valores preliminares) ---
SAMPLE_RATE_HZ: float = 50.0
DISPLAY_REFRESH_HZ: float = 30.0