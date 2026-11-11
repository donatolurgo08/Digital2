# Periféricos del PIC16F887

| Periférico | Uso previsto | Datos pendientes |
|---|---|---|
| ADC | Leer LM35 en AN0 y los tres ejes del MMA7361 en AN1 (X), AN5 (Y) y AN6 (Z), directos y sin amplificadores | Configurado: FOSC/32, VDD/VSS, ADFM=1; calibración pendiente |
| TIMER0 | Base temporal de adquisición | Derivado: 1 ms, 1:8, recarga 6; aún no implementado |
| TIMER1 | Temporización del multiplexado de tres displays | Etapa 4: 1 ms, 1:1, recarga 0xF830, polling |
| EUSART | Comunicación bidireccional con la GUI | 9600 Bd confirmado; formato/protocolo pendientes |
| GPIO | Displays rojos de ánodo común, LED rojo y buzzer | R9–R16 pendientes; R17–R19 (330 Ω), R21–R22 (220 Ω) y R23 (10 kΩ) calculadas; validar driver de dígitos |
| Interrupciones | Eventos temporizados y recepción serie | Fuentes habilitadas y estrategia final |

## Mapa de pines (Rev E)

| Función | Pin | Red |
|---|---|---|
| LM35 | 2 / RA0 / AN0 | AN0 |
| Eje X del MMA7361 | 3 / RA1 / AN1 | X_IN (directo) |
| Eje Y del MMA7361 | 8 / RE0 / AN5 | Y_IN (directo) |
| Eje Z del MMA7361 | 9 / RE1 / AN6 | Z_IN (directo) |
| LED1 | 4 / RA2 | LED1 |
| LED2 | 7 / RA5 / AN4 | LED2 |
| Dígitos | 15–17 / RC0–RC2 | DIG1–DIG3 (bases Q1–Q3) |
| Buzzer | 18 / RC3 | BZ_CTRL (módulo VCC/GND/I/O, I/O directo) |
| Segmentos | 19–22, 27–30 / RD0–RD7 | a, b, c, d, e, f, g, dp |
| TX / RX | 25 / RC6, 26 / RC7 | TX_TTL / RX_TTL |
| MCLR | 1 / RE3 | R23 a +5 V |
| ICSP | 36, 39, 40 / RB3, RB6, RB7 | PGM, PGC, PGD |

Pines 5, 6, 10, 13, 14, 23, 24, 33–35, 37 y 38 quedan sin conectar. RA4 (pin 6)
queda libre porque es open-drain y no puede entregar corriente al LED.

## Reglas de configuración

- Verificar registros, bancos y bits en el datasheet oficial del PIC16F887.
- Configurar como digitales únicamente los pines que corresponda; conservar
  AN0, AN1, AN5 y AN6 como entradas analógicas, con sus TRIS en entrada.
- Las salidas del MMA7361 tienen que quedar dentro de 0–VDD del PIC. Medir
  X, Y y Z en reposo y con inclinación antes de conectarlas.
- El oscilador interno está confirmado como fuente, a **8 MHz** (`OSCCON = 0x70`,
  `FOSC = INTRC_NOCLKOUT`). TCY = 0,5 µs.
- Calcular tiempos y baud rate con la frecuencia real del oscilador.
- Displays de ánodo común: RD0–RD7 son activos en bajo; RC0–RC2 altos activan
  Q1–Q3 BC337 como seguidores de emisor del lado alto. La pérdida VBE puede
  limitar el margen de tensión y el brillo; validar con un solo dígito primero.
- Verificar corrientes y compatibilidad eléctrica antes de conectar displays,
  LED o buzzer. R17–R19 = 330 Ω, R21–R22 = 220 Ω y R23 = 10 kΩ ya están
  calculadas; R9–R16 dependen de Vf y de la corriente por segmento.
- Buzzer: el módulo es de 3 terminales y su I/O va directo a RC3. Confirmar la
  polaridad; el firmware actual supone activo-alto (RC3 = 0 apagado).

## Alarma térmica (Etapa 3)

- Se evalúa `TEMP_C > 40` después de cada conversión de AN0.
- `TEMP_C <= 40`: RA2 (LED1), RA5 (LED2) y RC3 (señal del buzzer) en bajo.
- `TEMP_C > 40`: las tres salidas en alto. El buzzer activo de 3,3–5 V está
  conectado por su entrada de señal; la polaridad lógica queda pendiente de
  verificación física.
- Estado: escrito y compilado; falta probar temperaturas a ambos lados del
  umbral y confirmar la corriente/polaridad de la entrada del módulo.

## Displays multiplexados (Etapa 4)

- Patrones para display de ánodo común: `0` en RDx enciende el segmento y `1`
  lo apaga. RD0–RD7 representan a, b, c, d, e, f, g y dp.
- RC0–RC2 habilitan un único dígito por vez; el firmware rota decenas, unidades
  y `C` estándar a intervalos nominales de 1 ms usando TIMER1 por polling.
- Estado: escrito y compilado; falta validar el circuito BC337/display y el
  brillo en hardware. Valores de resistencias y patillaje físico pendientes.
- Mantener breves las ISR y procesar los datos en el programa principal cuando
  el diseño temporal lo permita.

## ADC configurado (Etapa 2)

- `ADCON1 = 0x80`: justificación a la derecha y referencias `VDD`/`VSS`.
- `ADCON0 = (canal << 2) | 0x81`: `ADCS = 10` (`FOSC/32`, `TAD = 4 µs`) y
  `ADON = 1`.
- `leer_adc` recibe el canal en `W` y devuelve 10 bits en `ADC_H:ADC_L`.
- `TEMP_C = cuentas × 125 / 256`, saturado a 99 °C.
- X del MMA7361: `DELTA = (cuentas − 338) × 49 / 8` mg, con signo
  (6,125 mg/cuenta). Offset de 0 g y sensibilidad de 800 mV/g **nominales**;
  calibrar con el módulo real y con su VCC medido.
- Y y Z se guardan como cuentas crudas de 10 bits en `Y_H:Y_L` y `Z_H:Z_L`;
  todavía no se convierten a mg.
- Las tres entradas del acelerómetro se conectan directo al ADC, sin
  amplificadores. Si el módulo tiene regulador propio, su salida máxima ronda
  3,3 V y solo se usa parte del fondo de escala de 5 V.
