# D-01 — Investigación de EUSART del PIC16F887

**Responsable:** Donato Lurgo  
**Estado:** Investigación cerrada para la configuración y el protocolo v1; pruebas de banco pendientes
**Uso previsto:** comunicación asíncrona bidireccional con la GUI mediante USB-TTL.

## Funcionamiento

En modo asíncrono, el EUSART transmite y recibe en full-duplex, sin una línea de
reloj compartida. El formato habitual es reposo alto, bit de inicio bajo, datos
LSB primero y bit(s) de parada alto(s). HAND MOTION usa caracteres de 8 bits,
un bit de parada y sin paridad (8N1).

En la versión 1, la PC envía comandos de control/configuración y el PIC devuelve
temperatura, eje X, estado de alarma y configuración. Los ejes Y/Z y los gestos
se incorporarán en etapas posteriores.

## Registros principales

| Registro | Banco/dirección | Función |
|---|---:|---|
| `TXSTA` | 1 / `0x98` | Control/transmisión. `SYNC=0` selecciona asíncrono; `TXEN` habilita TX; `BRGH` selecciona velocidad alta/baja; `TX9` activa 9 bits. |
| `RCSTA` | 0 / `0x18` | Habilitación y recepción. `SPEN` habilita el puerto serie; `CREN` habilita recepción continua; `FERR` y `OERR` indican errores. |
| `BAUDCTL` | 3 / `0x187` | `BRG16` selecciona generador de baud rate de 8/16 bits; también contiene funciones de auto-baud y wake-up no requeridas por ahora. |
| `SPBRG`, `SPBRGH` | 1 / `0x99`, `0x9A` | Divisor del generador de baud rate; `SPBRGH:SPBRG` se usa en modo de 16 bits. |
| `TXREG` | 0 / `0x19` | Buffer de un byte para transmitir. |
| `RCREG` | 0 / `0x1A` | Lectura del byte recibido; el receptor tiene FIFO de dos caracteres. |
| `PIR1`, `PIE1` | 0 / `0x0C`, 1 / `0x8C` | `TXIF`/`TXIE` para TX y `RCIF`/`RCIE` para RX. `TXIF` se limpia al escribir `TXREG`; `RCIF` baja al vaciar la recepción leyendo `RCREG`. |
| `INTCON` | 0 / `0x0B` | `PEIE` y `GIE` habilitan las interrupciones periféricas y globales. |

Al activar `SPEN`, el módulo toma control de las funciones serie de RC6/TX y
RC7/RX. El circuito usa PIC16F887 PDIP-40. El enlace requiere TX del
conversor conectado a RX del PIC, RX del conversor a TX del PIC y GND común.
Verificar niveles lógicos compatibles; USB-TTL no es una interfaz RS-232.

## Baud rate

Para asíncrono, con `n = SPBRGH:SPBRG` (o solo `SPBRG` en modo de 8 bits):

| `BRG16` | `BRGH` | Baud rate |
|---:|---:|---|
| 0 | 0 | `FOSC / (64 × (n+1))` |
| 0 | 1 | `FOSC / (16 × (n+1))` |
| 1 | 0 | `FOSC / (16 × (n+1))` |
| 1 | 1 | `FOSC / (4 × (n+1))` |

Con `FOSC = 8 MHz`, 9600 Bd, `BRGH = 1` y `BRG16 = 0`, se fija `SPBRG = 51`.
El baud calculado es 9615,4 Bd, con error aproximado de +0,16 %.

## Flujo de uso

**Inicialización:** `TXSTA = 0x24`, `RCSTA = 0x90`, `BRG16 = 0`, `SPBRG = 51`;
`SYNC=0`, `SPEN=1`, `TXEN=1`, `CREN=1`. El firmware v1 atiende TX y RX por polling.

**Transmisión:** escribir el byte en `TXREG` cuando `TXIF=1`. `TXIF` indica que
`TXREG` está vacío y preparado; `TRMT` indica que el registro de desplazamiento
terminó de enviar el último bit. En la aplicación integrada se evitarán esperas
bloqueantes.

**Recepción:** cuando `RCIF=1`, leer `RCREG` y procesar el byte. La FIFO guarda
hasta dos caracteres; si llega un tercero antes de atenderla, se activa `OERR`
y la recepción se detiene hasta reiniciar el receptor (por ejemplo, bajar y
volver a subir `CREN`). Leer `FERR` antes de `RCREG`, porque informa el estado del
carácter superior de la FIFO.

## Fragmentos Assembly de referencia

Asumen que el EUSART ya fue inicializado. Son ejemplos de polling para estudiar,
no la estrategia bloqueante prevista para el firmware integrado.

```asm
; Transmitir el byte que ya está en W
TX_ESPERA
    BTFSS   PIR1, TXIF
    GOTO    TX_ESPERA
    MOVWF   TXREG

; Recibir un byte; al salir queda en W
RX_ESPERA
    BTFSS   PIR1, RCIF
    GOTO    RX_ESPERA
    MOVF    RCREG, W
```

Para RX por interrupción se habilitan `RCIE`, `PEIE` y `GIE`; la ISR debe leer
los bytes a tiempo y guardarlos en un buffer para que el programa principal
interprete comandos. Para TX, `TXIE` se habilita mientras haya datos pendientes
y se deshabilita al vaciar el buffer.

## Aplicación y pendientes

- Implementar enlace PIC↔GUI para comandos/configuración y para transmitir
  temperatura, muestras, gestos y estado.
- Protocolo v1 documentado en `docs/comunicacion/protocolo.md`: trama binaria
  con CRC-8, comandos de configuración y datos de temperatura/X.
- Pendiente: probar RX/TX, niveles lógicos del conversor USB-TTL, CRC y
  recuperación ante errores con hardware real. La GUI ya implementa el codec.
- `FOSC` está confirmado en 8 MHz; el encapsulado eléctrico sigue siendo
  PDIP-40 según el esquema.

## Fuente

Microchip, *PIC16F882/883/884/886/887 Data Sheet*, DS41291D, secciones 1.0 y
12.0–12.3; tablas de EUSART y baud rate, pp. 149–165. [PDF oficial](https://ww1.microchip.com/downloads/en/DeviceDoc/41291D.pdf).
