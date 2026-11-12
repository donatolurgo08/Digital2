# Arquitectura del firmware

## Organización

El firmware está escrito en Assembler para PIC16F887 compatible con `pic-as`.
`firmware/src/handmotion.S` contiene el vector, la configuración, los datos
compartidos y el bucle principal; el multiplexado está separado en
`firmware/src/modules/display.inc`, incluido durante el ensamblado. Así se
mantiene un único HEX de salida y se separan las responsabilidades por módulo.
La sintaxis relocatable de `pic-as` se toma como referencia del TP1; no se copian
directivas MPASM de TP3/TP4 sin verificar compatibilidad.

Los siguientes módulos podrán extraerse cuando cada etapa esté estable:

1. Inicialización y configuración de periféricos.
2. Adquisición y conversión ADC.
3. Procesamiento de temperatura y alarma.
4. Adquisición/procesamiento de movimiento X.
5. Codificación y actualización de displays.
6. Temporizadores e interrupciones.
7. EUSART, buffers y protocolo.
8. Bucle principal e integración de eventos.

## Reloj y configuración confirmados

- Oscilador **interno a 8 MHz**: `OSCCON = 0x70` (`IRCF<2:0> = 111`, `SCS = 00`).
- `TCY = 4 / FOSC = 0,5 µs`.
- Configuration bits: `FOSC = INTRC_NOCLKOUT`, `WDTE = OFF`, `PWRTE = ON`,
  `MCLRE = ON`, `CP = OFF`, `CPD = OFF`, `BOREN = ON`, `IESO = OFF`,
  `FCMEN = OFF`, `LVP = OFF`, `DEBUG = OFF`, `BOR4V = BOR40V`, `WRT = OFF`.
- ADC `FOSC/32` (`TAD = 4 µs`); TIMER0 `FOSC/4`, prescaler 1:8, precarga 6
  (tick nominal de 1 ms); TIMER1 1:1 con recarga `0xF830` (1 ms por dígito);
  EUSART 9600 Bd con `BRGH = 1` y `SPBRG = 51` (9615 Bd, error aproximado
  +0,16 %).

## Etapa 2: ADC

- `ADCON1 = 0x80`: resultado justificado a la derecha (`ADFM = 1`) y
  referencias `VREF+ = VDD`, `VREF- = VSS` (`VCFG1:VCFG0 = 00`).
- `ADCON0 = (canal << 2) | 0x81`: `ADCS<1:0> = 10` (`FOSC/32`, `TAD = 4 µs`
  a 8 MHz) y `ADON = 1`.
- La adquisición se espera con un lazo de 14 iteraciones (~23 µs), suficiente
  para fuentes de hasta 10 kΩ. La salida del MMA7361 va directa: verificar su
  impedancia de salida antes de reducir el margen.
- `leer_adc` recibe el número de canal en `W` (0 = AN0/LM35, 1 = AN1/X,
  5 = AN5/Y, 6 = AN6/Z) y deja el resultado de 10 bits en `ADC_H:ADC_L`,
  justificado a la derecha.
- Temperatura: `TEMP_C = cuentas × 125 / 256`, redondeado y saturado a 99 °C.
  Para 40 °C se esperan 82 cuentas; `TEMP_C = 40`.
- Eje X del MMA7361 (±1,5 g): `DELTA = (cuentas − 338) × 49 / 8` mg, con signo
  en complemento a dos de 16 bits. Equivale a 6,125 mg/cuenta (6,10 mg/cuenta
  nominal). El offset de 338 cuentas supone 0 g = VCC/2 con VCC = 3,3 V; el
  offset y la sensibilidad son **nominales** y se ajustan por calibración.
- Y y Z se adquieren y quedan como cuentas crudas en `Y_H:Y_L` y `Z_H:Z_L`.
- El bucle principal adquiere AN0, AN5 y AN6 como antes; AN1/X se adquiere con
  el período separado de la Etapa 5. Los resultados quedan en `TEMP_C`,
  `DELTA_H:DELTA_L`, `Y_H:Y_L` y `Z_H:Z_L`.
- Estado de la Etapa 2: **escrita y compilada**, no probada en hardware. La
  referencia real es el riel de 5 V de PS1; si no es exactamente 5,000 V, la
  conversión en °C y mg escala en proporción. Antes de usar X para gestos hay
  que medir el offset de 0 g, la sensibilidad y la tensión real del módulo.

## Etapa 3: alarma térmica

- Después de convertir la lectura de AN0, `procesar_alarma` compara `TEMP_C`
  con 40 °C. La alarma se activa estrictamente si `TEMP_C > 40`; con 40 °C o
  menos, todas las salidas quedan apagadas.
- LED1: RA2 (pin 4); LED2: RA5 (pin 7); señal del módulo buzzer: RC3 (pin 18).
  Los dos LED y el buzzer cambian juntos.
- La salida RC3 se implementó activo-alto de manera provisional. La foto del
  buzzer indica disparo activo-bajo; invertir RC3 antes de conectarlo al PIC y
  medir la corriente del I/O en banco. El cableado directo no cambia.
- Estado: **escrita y compilada**, polaridad de firmware por corregir; falta
  probar corriente y activación en hardware.

## Etapa 4: displays multiplexados

- El código del multiplexado está separado en `firmware/src/modules/display.inc`
  y se incorpora a `handmotion.S` durante el ensamblado.
- TIMER1 usa reloj interno `FOSC/4`, prescaler 1:1 y recarga `0xF830` para un
  periodo nominal de 1 ms; el programa sondea `TMR1IF` sin ISR.
- Muestra decenas, unidades y `C` estándar (`a`, `d`, `e`, `f`). En displays
  rojos de ánodo común, los patrones de RD0–RD7 son activos en bajo y RC0–RC2
  habilitan cada dígito en alto.
- Q1–Q3 BC337 se plantean como seguidores de emisor de lado alto. La caída VBE,
  la corriente y el brillo siguen pendientes de validación eléctrica.
  R17–R19 = 330 Ω (base), R21–R22 = 220 Ω (LED) y R23 = 10 kΩ (MCLR); R9–R16
  = 150 Ω provisionales, a confirmar midiendo Vf.
- El multiplexado toma hasta 80 mA en pulsos de 1 ms sobre el mismo riel que el
  ADC usa como referencia (`VREF+ = VDD`). C10 de 220 µF sostiene el riel; si la
  caída supera ~50 mV, la lectura se corre.
- Estado: **escrita y compilada**, no probada en hardware.

## Etapa 5: muestreo periódico de X

- TIMER0 usa `FOSC/4`, prescaler `1:8` y precarga `6`: intervalo nominal de
  `((256-6) × 8 × 0,5 µs) = 1 ms`. El intervalo real puede variar por la
  latencia de la ISR y la inhibición de dos ciclos al escribir `TMR0`.
- La ISR preserva `W` y `STATUS`, recarga TIMER0 y cada 20 ticks levanta una
  bandera de muestra. La conversión ADC de AN1 se ejecuta en foreground, no en
  la ISR.
- AN1/X se muestrea cada **20 ms (50 Hz)**. El muestreo de temperatura y la
  adquisición ya existente de Y/Z no se modifican; Y/Z siguen fuera del
  protocolo serie v1.
- La telemetría conserva su período independiente: 50 ms (20 Hz) por defecto,
  configurable desde GUI entre 20 y 250 ms.
- Estado: **escrita y compilada**, falta verificar en hardware el período y el
  jitter reales antes de usarlos para reconocimiento de gestos.

## Etapa 6: EUSART y protocolo serie

- EUSART asíncrono 9600 Bd, 8N1, sin control de flujo: `TXSTA = 0x24`,
  `RCSTA = 0x90`, `BRG16 = 0`, `SPBRG = 51`.
- Protocolo binario `AA 55 | LEN | TIPO | DATOS | CRC8`; CRC-8/ATM con
  polinomio `0x07`, inicial `0x00`, sin reflexión ni XOR final. `LEN` incluye
  tipo y datos, CRC cubre `LEN` hasta el último dato.
- PIC→PC transmite `DATA` con secuencia, temperatura, X en mg con signo y
  bandera de alarma; `STATUS` informa versión, período, umbral, offset de X y
  modo; `ACK` confirma comandos.
- PC→PIC admite PING, START, STOP, SET_THRESHOLD, GET_STATUS y SET_OFFSET.
  Streaming inicia activo a 20 Hz; START permite períodos de 20–250 ms y 0
  conserva el período actual.
- RX y TX se atienden por polling en `modules/uart.inc`, usando buffer TX de
  32 bytes y sin bloquear la actualización de displays con esperas por byte.
  Se descartan CRC/framing inválidos y se recupera el receptor ante overrun.
- Y y Z siguen cableados y su adquisición previa se conserva, pero **no se
  transmiten en esta versión**; se incorporarán después sin alterar DATA v1.
- Especificación: [`../comunicacion/protocolo.md`](../comunicacion/protocolo.md).
- Estado: **escrita y compilada**, GUI integrada; falta probar en hardware.

## Detalle de `pic-as` V4.00 verificado

- El compilador empaqueta los PSECT de código desde el final de la página 0 hacia
  abajo. Por eso el vector de reset se declara absoluto:

  ```asm
          PSECT   resetVec,class=CODE,delta=2,abs
          ORG     0
  resetVec:
          GOTO    main
  ```

- Sin `abs` y `ORG 0`, `handmotion.hex` arranca en 0x07E0 y no en 0x0000.
- El PSECT `code` se ubica en la página 0 (0x0000–0x07FF) y **crece desde
  0x07FF hacia abajo**. Un único PSECT no puede superar las 2048 palabras: un
  programa mayor falla con «can't find N words for psect code». Si el firmware
  se acerca a ese límite habrá que separar el código en páginas y administrar
  `PCLATH` explícitamente.
- El `END` debe indicar el símbolo de entrada: `END resetVec`.

## Flujo de ejecución

TIMER0 genera el tick nominal de 1 ms y su ISR levanta una bandera cada 20 ticks.
El bucle principal consume la bandera y adquiere/convirtiere AN1/X fuera de la
ISR. TIMER1 y EUSART siguen atendidos por polling; el análisis de gestos y el
parseo/formateo de mensajes no se realizan dentro de la ISR.

## Dependencias pendientes

Validar en hardware la cadencia de TIMER0 y la comunicación GUI↔PIC; definir
filtros/criterios de gestos y el futuro muestreo periódico de Y/Z; calibrar la
sensibilidad de X y medir la referencia real de 5 V. También falta validar
R9–R16. El offset de X se configura por serie. R17–R19, R21–R22 y R23 ya están
calculadas. Las Etapas 5 y 6 están escritas y compiladas, no probadas en banco.
