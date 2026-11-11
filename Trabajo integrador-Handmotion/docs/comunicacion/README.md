# Comunicación con la GUI

El PIC16F887 y la computadora se comunican en ambos sentidos mediante EUSART
y un conversor USB-TTL. El protocolo v1 está definido e implementado tanto en
el firmware como en la GUI:

- PC → PIC: PING, START, STOP, SET_THRESHOLD, GET_STATUS y SET_OFFSET.
- PIC → PC: DATA (temperatura, X y alarma), STATUS y ACK.

La especificación completa está en [`protocolo.md`](protocolo.md). El enlace es
9600 Bd, 8N1; FOSC y el divisor están confirmados. La versión actual transmite
solo X; Y/Z se incorporarán después. Verificar niveles TTL, GND común y
conexión TX/RX; no conectar RS-232 directamente al PIC. La comunicación todavía
requiere pruebas de banco con el PIC y el adaptador reales.
