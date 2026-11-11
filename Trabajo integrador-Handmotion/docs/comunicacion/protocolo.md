# Protocolo serie HAND MOTION — versión 1

## Estado y alcance

La especificación está implementada en el firmware Assembly y en la GUI. El
firmware compila, pero el enlace todavía no está probado con el PIC y el
adaptador USB-TTL reales.

Esta versión transmite temperatura y **solo el eje X**. Y y Z permanecen
cableados y la adquisición existente del PIC se conserva, pero no forman parte
de las tramas de esta versión.

## Enlace físico

- UART asíncrona, **9600 Bd, 8N1**, sin control de flujo.
- `FOSC = 8 MHz`, `BRGH = 1`, `BRG16 = 0`, `SPBRG = 51`.
- Baud calculado: 9615,4 Bd; error respecto de 9600: aproximadamente +0,16 %.
- PIC RC6/TX → RX del USB-TTL; PIC RC7/RX ← TX del USB-TTL; GND común.
- Confirmar los niveles lógicos del conversor antes de conectarlo. No usar una
  interfaz RS-232 directamente.

## Formato común de trama

```text
AA 55 | LEN | TIPO | DATOS (LEN - 1 bytes) | CRC8
```

- `LEN` cuenta los bytes desde `TIPO` hasta el último dato; no incluye los dos
  bytes de sincronismo, el propio `LEN` ni el CRC.
- Longitud total: `LEN + 4` bytes.
- El CRC es CRC-8/ATM: polinomio `0x07`, valor inicial `0x00`, sin reflexión ni
  XOR final. Se calcula en orden sobre `LEN`, `TIPO` y todos los datos.
- Los enteros de varios bytes viajan **little-endian**.
- El receptor busca `AA 55`; una longitud no válida, CRC incorrecto o error de
  framing descarta la trama y vuelve a buscar sincronismo. El firmware recupera
  el receptor si detecta overrun. No se envía NAK por CRC inválido.

Ejemplos CRC verificados:

```text
PING:  AA 55 01 81 9B
START: AA 55 02 82 32 D4   (período 50 ms)
```

## Tramas PIC → PC

### `0x01 DATA` — `LEN = 6`, 10 bytes totales

| Orden | Campo | Tamaño | Significado |
|---:|---|---:|---|
| 1 | `TIPO = 0x01` | 1 | DATA |
| 2 | `SEQ` | 1 | Contador de trama; incrementa y vuelve a cero tras 255. |
| 3 | `TEMP_C` | 1 | Temperatura entera en °C, rango transmitido 0–99. |
| 4 | `X_L` | 1 | Byte bajo de X en mg con signo. |
| 5 | `X_H` | 1 | Byte alto de X en complemento a dos de 16 bits. |
| 6 | `FLAGS` | 1 | Bit 0: alarma térmica activa; bits 1–7 reservados en cero. |

El período inicial es **50 ms (20 Hz)** y el envío periódico está habilitado al
arrancar. La trama ocupa 10 bytes de UART (10 bits por byte en 8N1), por lo que
utiliza aproximadamente el 21 % de un enlace de 9600 Bd a 20 Hz.

### `0x02 STATUS` — `LEN = 7`, 11 bytes totales

Datos: `VERSION`, `PERIOD_MS`, `THRESHOLD_C`, `X_OFFSET_L`, `X_OFFSET_H`,
`MODO`.

- `VERSION = 1`.
- `MODO` bit 0: streaming DATA activo; bits 1–7 reservados en cero.
- Los offsets son cuentas ADC de 10 bits, little-endian.

### `0x03 ACK` — `LEN = 3`, 7 bytes totales

Datos: `CMD`, `RESULT`.

| `RESULT` | Significado |
|---:|---|
| `0` | Comando aceptado. |
| `1` | Parámetros o longitud no válidos. |
| `2` | Tipo de comando desconocido. |

## Comandos PC → PIC

| Tipo | Comando | `LEN` | Datos / resultado |
|---:|---|---:|---|
| `0x81` | PING | 1 | Sin datos; responde ACK. |
| `0x82` | START | 2 | Un byte de período en ms. `0` conserva el período actual; valores válidos 20–250. Habilita DATA y responde ACK. |
| `0x83` | STOP | 1 | Sin datos; detiene DATA periódico, pero conserva la recepción de comandos. Responde ACK. |
| `0x84` | SET_THRESHOLD | 2 | Umbral de alarma en °C, 0–99; responde ACK. |
| `0x85` | GET_STATUS | 1 | Sin datos; responde con una trama STATUS (sin ACK separado). |
| `0x86` | SET_OFFSET | 3 | Offset X en cuentas ADC: `X_L`, `X_H`; valor 0–1023; responde ACK. |

Las respuestas ACK repiten el byte de tipo del comando recibido en `CMD`.
Los tipos desconocidos reciben ACK con `RESULT = 2`. Las longitudes incorrectas
de comandos conocidos reciben ACK con `RESULT = 1`.

## Implementación actual

- Código PIC en `firmware/src/modules/uart.inc`; incluido desde
  `firmware/src/handmotion.S`. Todo permanece en Assembler y produce un solo
  HEX.
- TX usa un buffer circular de 32 bytes; RX se atiende por polling en el bucle
  principal, junto con TX y el temporizador del multiplexado. No se usan
  interrupciones EUSART ni esperas de transmisión por byte.
- La trama DATA contiene temperatura, X en mg con signo y estado de alarma.
- `SET_OFFSET` cambia el offset de X usado por la conversión a mg. La
  sensibilidad sigue siendo nominal y requiere calibración física.
- Y/Z no se transmiten todavía. Se añadirán en una etapa posterior sin cambiar
  la definición de DATA v1; si se requiere un formato ampliado, se publicará
  una versión/tipo nuevo.
- Pruebas de banco pendientes: RX/TX, formato real del adaptador USB-TTL,
  recepción de comandos, CRC y cadencia efectiva. La GUI fue verificada con
  pruebas locales, no con el hardware real.
