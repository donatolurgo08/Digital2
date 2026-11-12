# HAND MOTION — Checklist de pendientes

Actualizada: 2026-11-12

## Firmware

- [ ] **Etapa 2:** probar en hardware la lectura del LM35 y de los tres ejes del MMA7361. La conversión supone una referencia real de 5 V; el offset y la sensibilidad de X son nominales.
- [ ] Verificar que `Y_H:Y_L` y `Z_H:Z_L` reciban cuentas coherentes al inclinar el módulo en cada eje.
- [ ] **Etapa 3:** comprobar que la alarma se apague con `TEMP_C <= 40` y se active con `TEMP_C > 40`; verificar la polaridad y corriente de la entrada del buzzer.
- [ ] **Etapa 4:** probar los displays de ánodo común, el refresco y el brillo. El código está escrito y compilado, pero no probado físicamente.
- [ ] **Validar el driver BC337:** probar primero un dígito y un segmento. La conexión propuesta como seguidor de emisor pierde tensión; si no funciona bien, decidir otro driver antes de completar el montaje.
- [x] **Etapa 5:** TIMER0 con tick nominal de 1 ms; AN1/X muestreado cada 20 ms (50 Hz). Firmware compilado.
- [ ] Medir/verificar el período y jitter de TIMER0 en hardware antes de usar X para gestos. Y/Z quedan para una etapa posterior.
- [x] Prototipo Python de X para datos sintéticos: X negativo/neutro/positivo con umbrales parametrizados; pruebas unitarias.
- [ ] Definir y calibrar gestos/umbrales reales y portar la lógica aprobada a Assembler para el PIC.
- [x] **Etapa 6 — especificación y firmware:** protocolo binario v1 y EUSART 9600 Bd implementados y compilados; falta probar RX/TX en banco.
- [x] Integrar la GUI con el protocolo v1: codec CRC-8, RX serial y controles de comandos.
- [ ] Probar comandos/respuestas de la GUI con el PIC y el USB-TTL reales.
- [ ] **Etapa 7:** integrar y probar adquisición, alarma, displays, reconocimiento y comunicación.
- [ ] Separar ADC y alarma en módulos si se completa la modularización; por ahora, el módulo separado es el del display.

## Hardware

- [ ] Verificar el rango de entrada admitido por PS1 y la polaridad del conector del alimentador externo.
- [ ] Medir las salidas de 5 V y 3,3 V de PS1, la corriente disponible en 5 V y verificar GND común.
- [ ] Confirmar la alimentación admitida por el módulo MMA7361 y su patillaje real (VCC, GND, X, Y, Z, GS, ST, 0G). No unir un pin de salida 3V3 al riel.
- [ ] Medir X, Y y Z en reposo y con inclinación; comprobar que no superen VDD y que la impedancia de salida sea apta para el ADC.
- [ ] Confirmar cómo se selecciona el rango de ±1,5 g en el módulo (pin GS o puente).
- [ ] Identificar el patillaje de los displays y de los BC337.
- [ ] Confirmar en banco R9–R16 (150 Ω provisionales): depende de Vf y de la corriente por segmento.
- [ ] Verificar en banco R17–R19 (330 Ω), R21–R22 (220 Ω) y R23 (10 kΩ), calculadas en la nota 6.14 del netlist.
- [ ] Medir la caída del riel de 5 V con los tres displays multiplexando: debería quedar por debajo de ~50 mV. C10 la reduce; sin ella la lectura del ADC (VREF = VDD) se corre.
- [ ] Verificar la polaridad de C10 antes de energizar: positivo a +5 V.
- [ ] Medir la corriente y confirmar la polaridad del buzzer; el firmware supone activo-alto. Q4 y R20 fueron eliminados.
- [ ] Verificar RX/TX y los niveles eléctricos del USB–TTL.

## Documentación y GUI

- [x] Actualizar la GUI a MMA7361 y protocolo v1; solo presenta X por ahora.
- [x] Definir el protocolo v1 para temperatura, eje X y alarma. Y/Z quedan para una etapa posterior.

## Repositorio

- [x] Rev E (MMA7361 sin amplificadores) commiteada y pusheada: `cf985c3`.
- [x] Valores de R17–R19, R21–R22 y R23 (`99c2e55`) y R9–R16 (`a8c728c`) commiteados y pusheados.
- [x] Reserva de carga C10/C11 pusheada: `c6b8f61`.
- [x] Protocolo serie y firmware de Etapa 6 pusheados: `0cc73bb`.
- [x] Integración de la GUI con el protocolo v1 publicada en esta etapa.
