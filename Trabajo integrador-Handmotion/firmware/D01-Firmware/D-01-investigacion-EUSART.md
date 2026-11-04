# D-01 — Investigación de EUSART del PIC16F887

**Responsable:** Donato Lurgo  
**Estado:** En investigación  
**Uso previsto:** comunicación asíncrona bidireccional con la GUI mediante USB-TTL.

## Funcionamiento

En modo asíncrono, el EUSART transmite y recibe en full-duplex, sin una línea de
reloj compartida. El formato habitual es reposo alto, bit de inicio bajo, datos
LSB primero y bit(s) de parada alto(s). Puede manejar caracteres de 8 o 9 bits;
el protocolo y formato definitivos todavía están pendientes.

En HAND MOTION, la PC enviará comandos/parámetros acordados y el PIC devolverá
temperatura, mediciones, gestos reconocidos e información de estado.

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
RC7/RX. La asignación física de pines depende del encapsulado; confirmar el
encapsulado real antes de documentar números de pata. El enlace requiere TX del
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

Se despeja `n` para el baud rate requerido y se calcula el baud rate real/error
con el divisor entero elegido. No se pueden fijar `SPBRG`, `SPBRGH`, `BRGH` ni
`BRG16` hasta confirmar `FOSC` y el baud rate acordado con la GUI.

## Flujo de uso

**Inicialización:** configurar el generador con `FOSC` y baud rate confirmados;
seleccionar `SYNC=0`; habilitar `SPEN`; activar `TXEN` para transmitir y `CREN`
para recepción continua. Los detalles del divisor quedan pendientes.

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
- Definir baud rate, formato de carácter, protocolo, delimitadores, comandos,
  validación y estrategia de errores junto con Ana.
- Confirmar `FOSC`, encapsulado y tensión lógica del conversor USB-TTL antes de
  cerrar la configuración eléctrica y de baud rate.

## Fuente

Microchip, *PIC16F882/883/884/886/887 Data Sheet*, DS41291D, secciones 1.0 y
12.0–12.3; tablas de EUSART y baud rate, pp. 149–165. [PDF oficial](https://ww1.microchip.com/downloads/en/DeviceDoc/41291D.pdf).
