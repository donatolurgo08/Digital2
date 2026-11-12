# HAND MOTION — Checklist de pendientes

Actualizada: 2026-11-12

## Firmware

- [ ] **Etapa 2:** probar en hardware la lectura del LM35 y de los tres ejes del MMA7361. La conversión supone una referencia real de 5 V; el offset y la sensibilidad de X son nominales.
- [ ] Verificar que `Y_H:Y_L` y `Z_H:Z_L` reciban cuentas coherentes al inclinar el módulo en cada eje.
- [ ] **Etapa 3:** comprobar que la alarma se apague con `TEMP_C <= 40` y se active con `TEMP_C > 40`; verificar la polaridad y corriente de la entrada del buzzer.
- [x] Firmware RC3 actualizado a activo-bajo según la serigrafía del buzzer y recompilado.
- [ ] **Etapa 4:** probar los displays de cátodo común, el refresco y el brillo. El firmware usa segmentos activos altos; aún falta validar en banco.
- [ ] **Validar Q1–Q3 BC337 como selectores de cátodo lado bajo:** probar un dígito y un segmento, corriente de base/saturación y brillo.
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

- [ ] **PS1 (HW-131/HW-130):** usar provisionalmente la entrada USB de 5 V. La entrada DC-IN existe pero queda sin usar hasta confirmar tensión y polaridad del jack. No conectar USB y DC-IN a la vez.
- [ ] Ajustar los dos jumpers de PS1 para obtener simultáneamente 5 V y 3,3 V; medir ambas salidas, corriente de 5 V y GND común.
- [ ] Confirmar en la serigrafía el orden del header Candy-Ho y si SLP/ST/GS están fijados por puentes/pullups. Objetivo: SLP alto, ST bajo, GS bajo o sin conectar. El módulo está especificado a 3–5 V y se cablea a +3V3.
- [ ] **Decidir pines Y/Z:** el documento de respuestas propone Y→AN2 (pin 4) y Z→AN3 (pin 5), pero la Rev E usa AN5 (pin 8) y AN6 (pin 9) porque RA2/AN2 es LED1. No cablear hasta confirmar.
- [ ] Medir X, Y y Z en reposo y con inclinación; comprobar que no superen VDD y que la impedancia de salida sea apta para el ADC.
- [ ] Confirmar en el carrier que GS quede bajo/puenteado o sin conectar para ±1,5 g.
- [ ] Confirmar C5–C7 = 3,3 nF en las salidas X/Y/Z (valor de datasheet) y C9 = 100 nF en +3V3.
- [ ] Identificar el patillaje físico de los displays genéricos.
- [x] Pinout BC337 según la imagen: C-B-E visto de frente, cara plana hacia el observador.
- [ ] Aprobar el candidato R9–R16 = 220 Ω para cátodo común después de medir Vf/VOH y el brillo; el antiguo 150 Ω era para ánodo común.
- [ ] Verificar en banco R17–R19 (330 Ω), R21–R22 (220 Ω) y R23 (10 kΩ), calculadas en la nota 6.14 del netlist.
- [ ] Medir la caída del riel de 5 V con los tres displays multiplexando: debería quedar por debajo de ~50 mV. C10 la reduce; sin ella la lectura del ADC (VREF = VDD) se corre.
- [ ] Verificar la polaridad de C10 antes de energizar: positivo a +5 V.
- [ ] Medir la corriente de la entrada I/O del buzzer MDU1095 y validar el modelo y el trigger activo-bajo. Los 30 mA son consumo del módulo, no la corriente de control. Q4 y R20 fueron eliminados.
- [ ] Conectar USB-TTL por GND/TXD/RXD, dejar sus salidas 3V3/+5V aisladas y medir el nivel lógico de TXD.

## Documentación y GUI

- [x] Actualizar la GUI a MMA7361 y protocolo v1; solo presenta X por ahora.
- [x] Definir el protocolo v1 para temperatura, eje X y alarma. Y/Z quedan para una etapa posterior.

## Repositorio

- [x] Rev E (MMA7361 sin amplificadores) commiteada y pusheada: `cf985c3`.
- [x] Valores de R17–R19, R21–R22 y R23 (`99c2e55`) y R9–R16 (`a8c728c`) commiteados y pusheados.
- [x] Reserva de carga C10/C11 pusheada: `c6b8f61`.
- [x] Protocolo serie y firmware de Etapa 6 pusheados: `0cc73bb`.
- [x] Integración de la GUI con el protocolo v1 publicada en esta etapa.
