# Comunicación con la GUI

El PIC16F887 y la computadora se comunicarán en ambos sentidos mediante EUSART
y un conversor USB-TTL:

- PC → PIC: parámetros y comandos de configuración acordados.
- PIC → PC: movimientos reconocidos e información de estado acordada.

Baud rate, formato, comandos, delimitadores, validación, manejo de errores y
parámetros configurables quedan pendientes. El baud rate se calculará con la
frecuencia real del oscilador. Verificar niveles TTL, GND común y conexión TX/RX;
no conectar RS-232 directamente al PIC.
