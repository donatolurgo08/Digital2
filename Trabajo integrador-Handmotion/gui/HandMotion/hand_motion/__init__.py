"""Paquete principal de la aplicación Hand Motion.

Hand Motion es una aplicación de escritorio (PySide6) que se comunica con un
microcontrolador PIC16F887 mediante comunicación serial (EUSART/USB-TTL) para
supervisar temperatura (LM35) y adquirir X/Y/Z del acelerómetro MMA7361.
La GUI reconoce inclinaciones por eje con umbrales ajustables; el firmware
todavía solo transmite las muestras.
"""

__version__ = "0.1.0"
__all__ = ["app"]
