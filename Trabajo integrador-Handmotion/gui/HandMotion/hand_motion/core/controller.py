"""Controlador de aplicación.

Orquesta la comunicación serial, el procesamiento de sensores y la lógica
de alarmas/gestos, actualizando el ``AppState``. Se implementará cuando se
defina el protocolo de comunicación (tarea T-03).
"""

from __future__ import annotations

from hand_motion.core.state import AppState


class AppController:
    """Coordinador principal de la aplicación."""

    def __init__(self, state: AppState) -> None:
        self.state = state

    # Métodos de orquestación se agregarán en tareas posteriores.