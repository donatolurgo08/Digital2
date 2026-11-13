# HAND MOTION — Checklist de pendientes

Actualizada: 2026-11-13

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

- [ ] **PS1 (HW-131/MB102):** entrada adoptada DC-IN con fuente regulada de 9 V DC; el USB-A hembra es salida de 5 V y no se usa como entrada. Confirmar polaridad del jack y compatibilidad con 9 V DC antes de energizar. No conectar DC-IN y USB a la vez.
- [ ] Ajustar los dos jumpers de PS1 para obtener simultáneamente 5 V y 3,3 V; medir ambas salidas, corriente de 5 V y GND común.
- [ ] Vigilar la temperatura del regulador de PS1 con 9 V de entrada durante la prueba integrada; no taparlo ni subir a 12 V.
- [x] **Pinout MOD1 confirmado por fotos (2×5):** izquierda 5V, 3V3, GND, g-Select, SelfTest; derecha X, Y, Z, Sleep, 0g-Detect. Trae regulador U2 (LP2985-3V) y jumper J1.
- [ ] **Alimentación de MOD1:** medir el jumper J1 del módulo y la tensión del pin 3V3. Recomendado: +5 V al pin 5V con el jumper abierto. Alternativa: +3V3 al pin 3V3 con el jumper puenteado. No conectar ambas entradas.
- [ ] Verificar que GS y ST queden a GND y Sleep a 3V3; no aplicar 5 V a los pines de control, que son de 3 V.
- [ ] **Pines Y/Z decididos:** se mantiene Y→AN5 (pin 8) y Z→AN6 (pin 9) de la Rev E; el documento de respuestas proponía AN2/AN3, pero RA2/AN2 es LED1 y RA3/AN3 queda libre.
- [ ] Medir X, Y y Z en reposo y con inclinación; comprobar que no superen VDD y que la impedancia de salida sea apta para el ADC.
- [ ] Confirmar C5–C7 = 3,3 nF en las salidas X/Y/Z (valor de datasheet) y C9 = 100 nF en +3V3.
- [x] **Patillaje físico de displays adoptado:** 1=e, 2=d, 3=CC, 4=c, 5=dp, 6=b, 7=a, 8=CC, 9=f, 10=g; patas 3 y 8 unidas al colector de Q1–Q3. Contrastar con datasheet o multímetro antes de soldar.
- [x] **Pinout BC337 verificado por el usuario:** lote completo C-B-E, cara plana al frente; no invertir colector y emisor.
- [x] **R9–R16 = 220 Ω adoptadas** para cátodo común (~10 mA). El antiguo 150 Ω era para ánodo común.
- [ ] Verificar en banco Vf/VOH, brillo y corriente por segmento con R9–R16 = 220 Ω.
- [ ] Verificar en banco R17–R19 (330 Ω), R21–R22 (220 Ω) y R23 (10 kΩ), calculadas en la nota 6.14 del netlist.
- [ ] Medir la caída del riel de 5 V con los tres displays multiplexando: debería quedar por debajo de ~50 mV. C10 la reduce; sin ella la lectura del ADC (VREF = VDD) se corre.
- [ ] Verificar la polaridad de C10 antes de energizar: positivo a +5 V.
- [ ] Medir la corriente de la entrada I/O del buzzer MDU1095 y validar el modelo y el trigger activo-bajo. Los 30 mA son consumo del módulo, no la corriente de control. Q4 y R20 fueron eliminados.
- [ ] Conectar USB-TTL por GND/TXD/RXD (etiquetas en orden 3V3, TXD, RXD, GND, +5V), dejar sus salidas 3V3/+5V aisladas y medir el nivel lógico de TXD.

## Documentación y GUI

- [x] Actualizar la GUI a MMA7361 y protocolo v1; solo presenta X por ahora.
- [x] Definir el protocolo v1 para temperatura, eje X y alarma. Y/Z quedan para una etapa posterior.

## Repositorio

- [x] Rev E (MMA7361 sin amplificadores) commiteada y pusheada: `cf985c3`.
- [x] Valores de R17–R19, R21–R22 y R23 (`99c2e55`) y R9–R16 (`a8c728c`) commiteados y pusheados.
- [x] Reserva de carga C10/C11 pusheada: `c6b8f61`.
- [x] Protocolo serie y firmware de Etapa 6 pusheados: `0cc73bb`.
- [x] Integración de la GUI con el protocolo v1 publicada en esta etapa.
- [x] Diseño de protoboard de dos placas de 830 lado a lado generado en `hardware/protoboard/protoboard.html` (diagrama + mapa de patas + redes + guía de armado). Verificado sin cortocircuitos de nodo.
- [ ] Probar el armado real sobre la protoboard y corregir ubicaciones si algún componente no entra.
