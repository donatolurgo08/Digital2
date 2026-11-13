# HAND MOTION

Trabajo Práctico Integrador de Electrónica Digital II. Proyecto educativo y
experimental para reconocer movimientos de la mano usando un PIC16F887 y un
acelerómetro analógico MMA7361 de tres ejes.

## Alcance confirmado

- Adquisición de los tres ejes del MMA7361, conectados directamente al ADC.
- Reconocimiento de movimientos a definir con mediciones del sensor real.
- Lectura del LM35 por AN0, independiente del reconocimiento de movimientos.
- Visualización de temperatura en tres displays multiplexados.
- Activación simultánea de LED rojo y buzzer activo cuando la temperatura sea
  mayor que 40 °C.
- Comunicación bidireccional con una GUI de PC mediante EUSART y un conversor
  USB-TTL.
- Firmware en Assembler para PIC16F887, compatible con `pic-as` (XC8).
- Tres displays rojos de siete segmentos de cátodo común (decisión del 2026-11-12).
- Sin amplificadores operacionales en la etapa analógica.
- Oscilador interno a 8 MHz; configuration bits definidos en el firmware.

Los pines, frecuencia y configuración del PIC están documentados. El protocolo
serie v1 está implementado en el firmware y la GUI (9600 Bd, trama binaria con
CRC-8; temperatura y eje X). Falta probar el enlace en hardware, calibrar el
sensor y definir los criterios de gestos. Y/Z no se transmiten todavía.
El eje X se muestrea cada 20 ms (50 Hz) mediante TIMER0; el envío de DATA mantiene
su período independiente de 50 ms por defecto.

## Organización

- [`docs/`](docs/): anteproyecto, arquitectura y especificaciones funcionales.
- [`firmware/`](firmware/): fuente, inclusiones y pruebas del firmware.
- [`gui/`](gui/): interfaz para PC y sus pruebas.
- [`simulation/`](simulation/): archivos y resultados de simulación.
- [`hardware/`](hardware/): esquemáticos, conexiones y componentes.

## Entorno

Abrir `Trabajo integrador.code-workspace` desde esta carpeta. El
entorno instalado incluye MPLAB X 6.35, XC8 4.00 (`pic-as`) y la extensión
PIC Assembly para VS Code. La configuración de compilación del proyecto se
documentará junto con el primer firmware compilable.

## Estado

Especificación en desarrollo. Consultar la [lista de pendientes](Tareas/checklist.md)
y los documentos de cada subsistema. Distinguir siempre entre implementación,
compilación y prueba en hardware real.
