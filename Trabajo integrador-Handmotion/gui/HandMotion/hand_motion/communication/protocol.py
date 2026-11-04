"""Codificación y decodificación de tramas del protocolo PIC ↔ GUI.

Funciones puras (sin I/O), para facilitar pruebas unitarias.
El protocolo definitivo se definirá en la tarea T-03; por ahora se dejan
las firmas como placeholder.
"""

from __future__ import annotations


def encode_command(name: str, payload: bytes = b"") -> bytes:
    """Codifica un comando hacia el PIC. Pendiente de definición del protocolo."""
    raise NotImplementedError("Protocolo no definido aún (T-03).")


def decode_frame(data: bytes) -> object:
    """Decodifica una trama recibida del PIC. Pendiente de definición del protocolo."""
    raise NotImplementedError("Protocolo no definido aún (T-03).")