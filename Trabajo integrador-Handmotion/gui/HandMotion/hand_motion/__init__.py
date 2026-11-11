"""Paquete principal de la aplicación Hand Motion.

Hand Motion es una aplicación de escritorio (PySide6) que se comunica con un
microcontrolador PIC16F887 mediante comunicación serial (EUSART/USB-TTL) para
supervisar temperatura (LM35) y adquirir el eje X del acelerómetro MMA7361.
El reconocimiento de gestos y la transmisión de Y/Z quedan para etapas futuras.
"""

__version__ = "0.1.0"
__all__ = ["app"]
