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
- Valores derivados para las etapas siguientes: ADC `FOSC/32` (`TAD = 4 µs`),
  TIMER0 1:8 con recarga 6 (1 ms), TIMER1 1:1 con recarga `0xF830` (1 ms por
  dígito), EUSART 9600 Bd con `BRGH = 1` y `SPBRG = 51`.

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
- El bucle principal adquiere AN0, AN1, AN5 y AN6 en forma continua. Los
  resultados quedan en `TEMP_C`, `DELTA_H:DELTA_L`, `Y_H:Y_L` y `Z_H:Z_L`.
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
- La salida RC3 se implementó activo-alto de manera provisional. La foto y la
  publicación identifican un módulo activo de 3,3–5 V con tres pines (VCC,
  GND y señal); no confirman la polaridad lógica ni la corriente de la entrada.
- Estado: **escrita y compilada**, no probada en hardware. Si la prueba confirma
  un módulo activo-bajo, invertir los niveles de RC3 en firmware, sin modificar
  el conexionado.

## Etapa 4: displays multiplexados

- El código del multiplexado está separado en `firmware/src/modules/display.inc`
  y se incorpora a `handmotion.S` durante el ensamblado.
- TIMER1 usa reloj interno `FOSC/4`, prescaler 1:1 y recarga `0xF830` para un
  periodo nominal de 1 ms; el programa sondea `TMR1IF` sin ISR.
- Muestra decenas, unidades y `C` estándar (`a`, `d`, `e`, `f`). En displays
  rojos de ánodo común, los patrones de RD0–RD7 son activos en bajo y RC0–RC2
  habilitan cada dígito en alto.
- Q1–Q3 BC337 se plantean como seguidores de emisor de lado alto. La caída VBE,
  la corriente, el brillo y R9–R19 siguen pendientes de validación eléctrica.
- Estado: **escrita y compilada**, no probada en hardware.

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

## Flujo de ejecución previsto

Las interrupciones señalarán eventos o atenderán operaciones breves. El bucle
principal procesará muestras, temperatura, reconocimiento y mensajes de GUI sin
esperas bloqueantes largas. El multiplexado se temporizará con TIMER1; TIMER0
servirá de base para la adquisición periódica.

Las rutinas de interrupción deberán ser cortas, guardar/restaurar el contexto
necesario, atender y limpiar la fuente correspondiente. El análisis de gestos,
el parseo de mensajes y el formateo de respuestas no se realizarán dentro de la
ISR.

## Dependencias pendientes

Baud rate y protocolo serie (T-03), período de adquisición, criterios de
reconocimiento, calibración del offset/sensibilidad de X, referencia real de
5 V y valores de R9–R19 y R21–R23. Ninguno de estos datos bloquea las etapas 1
a 4 del firmware.
