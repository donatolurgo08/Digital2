# HAND MOTION — Checklist de pendientes

Actualizada: 2026-11-06

## Firmware

- [ ] **Etapa 2:** probar en hardware la lectura del LM35 y del eje X. La conversión supone una referencia real de 5 V; el offset y la sensibilidad de X son nominales.
- [ ] **Etapa 3:** comprobar que la alarma se apague con `TEMP_C <= 40` y se active con `TEMP_C > 40`; verificar la polaridad y corriente de la entrada del buzzer.
- [ ] **Etapa 4:** probar los displays de ánodo común, el refresco y el brillo. El código está escrito y compilado, pero no probado físicamente.
- [ ] **Validar el driver BC337:** probar primero un dígito y un segmento. La conexión propuesta como seguidor de emisor pierde tensión; si no funciona bien, decidir otro driver antes de completar el montaje.
- [ ] **Etapa 5:** implementar el muestreo periódico de X con TIMER0. Definir el período de muestreo con mediciones reales.
- [ ] Calibrar X y definir filtros, umbrales y gestos reconocibles.
- [ ] **Etapa 6:** definir el protocolo de la GUI e implementar recepción y transmisión EUSART. El baud rate de 9600 está confirmado.
- [ ] **Etapa 7:** integrar y probar adquisición, alarma, displays, reconocimiento y comunicación.
- [ ] Separar ADC y alarma en módulos si se completa la modularización; por ahora, el módulo separado es el del display.

## Hardware

- [ ] Medir las salidas de 5 V y 3,3 V de PS1 y verificar GND común.
- [ ] Identificar el patillaje de los displays y de los BC337.
- [ ] Calcular y verificar R9–R19 para segmentos y bases, y R21–R23 para LED y MCLR. No asignar valores por suposición.
- [ ] Verificar RX/TX y los niveles eléctricos del USB–TTL.
- [ ] Medir la corriente y confirmar la polaridad del buzzer; el firmware supone activo-alto. Q4 y R20 fueron eliminados.

## Repositorio

- [ ] Revisar, commitear y pushear los cambios recientes de la Etapa 4 cuando estén listos; conservar las eliminaciones indicadas por el usuario.
