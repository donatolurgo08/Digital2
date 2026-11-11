# HAND MOTION — Checklist de pendientes

Actualizada: 2026-11-11

## Firmware

- [ ] **Etapa 2:** probar en hardware la lectura del LM35 y de los tres ejes del MMA7361. La conversión supone una referencia real de 5 V; el offset y la sensibilidad de X son nominales.
- [ ] Verificar que `Y_H:Y_L` y `Z_H:Z_L` reciban cuentas coherentes al inclinar el módulo en cada eje.
- [ ] **Etapa 3:** comprobar que la alarma se apague con `TEMP_C <= 40` y se active con `TEMP_C > 40`; verificar la polaridad y corriente de la entrada del buzzer.
- [ ] **Etapa 4:** probar los displays de ánodo común, el refresco y el brillo. El código está escrito y compilado, pero no probado físicamente.
- [ ] **Validar el driver BC337:** probar primero un dígito y un segmento. La conexión propuesta como seguidor de emisor pierde tensión; si no funciona bien, decidir otro driver antes de completar el montaje.
- [ ] **Etapa 5:** implementar el muestreo periódico de X, Y y Z con TIMER0. Definir el período de muestreo con mediciones reales.
- [ ] Calibrar offset y sensibilidad de cada eje y definir filtros, umbrales y gestos reconocibles.
- [ ] **Etapa 6:** definir el protocolo de la GUI e implementar recepción y transmisión EUSART. El baud rate de 9600 está confirmado.
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

- [ ] Actualizar la GUI, que todavía menciona el ADXL335, cuando se autorice modificar la aplicación. El firmware ya usa MMA7361.
- [ ] Revisar que el protocolo serie incluya los tres ejes y no solo X.

## Repositorio

- [x] Rev E (MMA7361 sin amplificadores) commiteada y pusheada: `cf985c3`.
- [x] Valores de R17–R19, R21–R22 y R23 (`99c2e55`) y R9–R16 (`a8c728c`) commiteados y pusheados.
- [ ] Commitear y pushear la reserva de carga (C10, C11) y los cambios de esta etapa.
