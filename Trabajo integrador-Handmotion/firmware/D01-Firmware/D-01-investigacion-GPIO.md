# D-01 — Investigación de GPIO del PIC16F887

**Responsable:** Donato Lurgo  
**Estado:** En investigación  
**Uso previsto:** displays, LED rojo, buzzer activo y señales de control.

## Registros y configuración

- `TRISx`: `1` configura el pin como entrada; `0`, como salida.
- `PORTx`: lectura del estado de los pines; al escribir, actualiza los latches
  de salida. El PIC16F887 no tiene registros `LATx`.
- `ANSEL`/`ANSELH`: en pines con función analógica, seleccionan entrada analógica
  (`1`) o digital (`0`). Para usarlos como GPIO digital hay que desactivar su
  función analógica; configurar solo `TRIS` no basta.
- Configurar primero el valor de salida seguro del puerto y después la dirección
  de los pines, una vez confirmado el mapa de pines y la polaridad del driver.

Las operaciones de bits sobre `PORTx` son read-modify-write: el PIC lee los
niveles de los pines, modifica el bit y vuelve a escribir el puerto. Si hay
cargas o pines que no reflejan el latch, conviene mantener una copia sombra en
RAM y escribir el patrón completo.

## Puertos y pines candidatos

El PIC16F887 dispone de hasta 35 I/O en los encapsulados de 40/44 pines. Sus
funciones alternas condicionan la disponibilidad:

| Puerto | Observaciones para el proyecto |
|---|---|
| `PORTA` | RA0–RA5 tienen funciones analógicas/referencia; RA6/RA7 pueden estar ocupados por el oscilador. |
| `PORTB` | RB0–RB5 también tienen funciones analógicas; RB6/RB7 se usan para ICSP; RB3 tiene función PGM. |
| `PORTC` | RC6/TX y RC7/RX se reservan para EUSART; RC0/RC1 pueden estar ligados a Timer1. |
| `PORTD` | RD0–RD7 son GPIO en el PIC16F887 y son candidatos para segmentos si el esquema y presupuesto de corriente lo permiten. |
| `PORTE` | RE0–RE2 también tienen función analógica; RE3 es entrada solamente y comparte MCLR/VPP. |

Son candidatos, no asignaciones. Confirmar encapsulado, pines de periféricos,
esquema y programación antes de asignar números de pata o señales.

## Aplicación en HAND MOTION

- GPIO para líneas de segmentos y selección de tres displays rojos de ánodo
  común. Los segmentos son activos en bajo. Se propone usar los BC337 como
  seguidores de emisor de lado alto para seleccionar los ánodos.
- GPIO de control para LED rojo y buzzer activo.
- Mantener separados los pines ADC del LM35 (AN0) y del acelerómetro X, y las
  líneas EUSART (RC6/TX, RC7/RX).

## Consideraciones eléctricas

- Cada LED necesita resistencia limitadora.
- Verificar corriente por pin y por puerto para los displays; usar resistencias
  y transistores/driver si el esquema o la corriente requerida lo exige.
- No conectar el buzzer directamente a un GPIO sin comprobar sus requisitos de
  corriente y tensión; usar un driver si supera las capacidades del pin.
- La hoja de datos da límites absolutos de 25 mA por I/O y 200 mA combinados por
  grupos de puertos. **No son corrientes de diseño recomendadas**; respetar las
  especificaciones normales `VOH`/`VOL` y márgenes eléctricos.
- El tipo ánodo común y los BC337 NPN están confirmados. La solución de seguidor
  de emisor pierde aproximadamente VBE; verificar margen, corriente y brillo.
  Valores de resistencias y patillaje físico siguen pendientes.

## Fuente

Microchip, *PIC16F882/883/884/886/887 Data Sheet*, DS41291D, secciones 3.0–3.7,
tablas de pines/registros y especificaciones DC, pp. 39–60, 239 y 245. [PDF oficial](https://ww1.microchip.com/downloads/en/DeviceDoc/41291D.pdf).
