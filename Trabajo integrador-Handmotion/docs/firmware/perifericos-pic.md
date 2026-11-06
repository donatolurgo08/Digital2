# Periféricos del PIC16F887

| Periférico | Uso previsto | Datos pendientes |
|---|---|---|
| ADC | Leer LM35 en AN0 y eje X del ADXL335 en AN1 (Y = AN5, Z = AN6 cableados, fuera del alcance inicial) | Configurado: FOSC/32, VDD/VSS, ADFM=1 |
| TIMER0 | Base temporal de adquisición | Período y recarga (Fosc = 8 MHz confirmado) |
| TIMER1 | Temporización del multiplexado de tres displays | Período y recarga (Fosc = 8 MHz confirmado) |
| EUSART | Comunicación bidireccional con la GUI | Baud rate, formato y protocolo |
| GPIO | Displays de cátodo común, LED rojo y buzzer | Valores de R9–R19 y R21–R23, manejo eléctrico |
| Interrupciones | Eventos temporizados y recepción serie | Fuentes habilitadas y estrategia final |

## Mapa de pines (Rev D)

| Función | Pin | Red |
|---|---|---|
| LM35 | 2 / RA0 / AN0 | AN0 |
| Eje X amplificado | 3 / RA1 / AN1 | X_AMP |
| Eje Y amplificado | 8 / RE0 / AN5 | Y_AMP |
| Eje Z amplificado | 9 / RE1 / AN6 | Z_AMP |
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
  AN0, AN1, AN5 y AN6 como entradas analógicas.
- El oscilador interno está confirmado como fuente, a **8 MHz** (`OSCCON = 0x70`,
  `FOSC = INTRC_NOCLKOUT`). TCY = 0,5 µs.
- Calcular tiempos y baud rate con la frecuencia real del oscilador.
- Displays de cátodo común: nivel alto en RC0–RC2 satura el NPN y habilita el
  dígito; los segmentos se manejan con nivel alto desde PORTD.
- Verificar corrientes y compatibilidad eléctrica antes de conectar displays,
  LED o buzzer. Los valores de R9–R19 y R21–R23 están pendientes.
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
- Mantener breves las ISR y procesar los datos en el programa principal cuando
  el diseño temporal lo permita.

## ADC configurado (Etapa 2)

- `ADCON1 = 0x80`: justificación a la derecha y referencias `VDD`/`VSS`.
- `ADCON0 = (canal << 2) | 0x81`: `ADCS = 10` (`FOSC/32`, `TAD = 4 µs`) y
  `ADON = 1`.
- `leer_adc` recibe el canal en `W` y devuelve 10 bits en `ADC_H:ADC_L`.
- `TEMP_C = cuentas × 125 / 256`, saturado a 99 °C.
- X: `DELTA = (cuentas − 547) × 73 / 8` mg, con signo.
- Offset y sensibilidad de X son nominales; calibrar con la placa real.
