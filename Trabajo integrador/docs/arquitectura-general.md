# Arquitectura general

## Propósito

HAND MOTION reconoce movimientos de la mano a partir de la señal analógica X de
un ADXL335 en un módulo GY-61. Un PIC16F887 adquiere y procesa esa señal y se
comunica con una GUI de PC. En forma independiente, el PIC mide temperatura con
un LM35 conectado a AN0 y la presenta localmente.

## Bloques funcionales

```text
GY-61 / ADXL335 (X) ── ADC ── reconocimiento ──┐
                                               ├── EUSART / USB-TTL ── GUI PC
LM35 (AN0) ─────────── ADC ── temperatura ─────┤
                                               └── tres displays multiplexados
                                                    LED rojo + buzzer si T > 40 °C
```

La GUI enviará parámetros/comandos acordados y mostrará movimientos reconocidos
e información de estado. La supervisión térmica no participa en el reconocimiento.

## Decisiones confirmadas

- Microcontrolador PIC16F887 y firmware Assembler con `pic-as` (XC8).
- Solo eje X para la primera versión; el canal ADC de X está pendiente.
- LM35 obligatoriamente en AN0.
- Tres displays: dos dígitos de temperatura y un indicador de °C.
- LED rojo y buzzer activo simultáneos cuando T > 40 °C.
- No se usará teclado matricial ni habrá etapa de potencia para actuadores externos.

## Pendientes de integración

Frecuencia/fuente de reloj, configuration bits, pines, tipo y manejo eléctrico
de displays, alimentación del GY-61, baud rate, protocolo GUI, parámetros,
períodos de adquisición y criterios de reconocimiento. Ver
[`firmware/perifericos-pic.md`](firmware/perifericos-pic.md) y
[`comunicacion/README.md`](comunicacion/README.md).
