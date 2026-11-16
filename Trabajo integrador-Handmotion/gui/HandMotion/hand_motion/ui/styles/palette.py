"""Paleta de colores y tipografías de Hand Motion (Etapa 1).

Centraliza la identidad visual Cyberpunk Industrial. Los valores se usan
tanto en ``theme.qss`` (como referencia) como en estilos dinámicos de Python.
"""

from __future__ import annotations

# Fondos
BG_PRIMARY = "#0a0f1a"
BG_SECONDARY = "#111827"
SURFACE = "#151b2b"
SURFACE_ALT = "#1e2536"

# Bordes y separadores
BORDER = "#2a3348"
SEPARATOR = "#1f2937"

# Textos
TEXT_PRIMARY = "#e6edf3"
TEXT_SECONDARY = "#94a3b8"
TEXT_MUTED = "#64748b"

# Colores fijos de ejes
ACCENT_CYAN = "#28C7FF"       # X
ACCENT_MAGENTA = "#DF55F5"    # Y
ACCENT_VIOLET = "#9165FF"     # Z

# Estados
OK_GREEN = "#22D98A"
WARNING_AMBER = "#F5B942"
ALARM_RED = "#F05252"

GESTURE_COLORS = {
    "X_POSITIVE": ACCENT_CYAN,
    "X_NEGATIVE": ACCENT_CYAN,
    "Y_POSITIVE": ACCENT_MAGENTA,
    "Y_NEGATIVE": ACCENT_MAGENTA,
    "Z_POSITIVE": ACCENT_VIOLET,
    "Z_NEGATIVE": ACCENT_VIOLET,
    "REST": OK_GREEN,
}

# Tipografías (sin dependencias adicionales)
FONT_TITLE = '"Exo 2", "Bahnschrift", "Segoe UI Variable", "Segoe UI", sans-serif'
FONT_BODY = '"Segoe UI", "Inter", sans-serif'
FONT_MONO = '"Cascadia Code", "Consolas", "Lucida Console", monospace'
