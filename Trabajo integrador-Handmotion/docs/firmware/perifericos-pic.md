# Periféricos del PIC16F887

| Periférico | Uso previsto | Datos pendientes |
|---|---|---|
| ADC | Leer LM35 en AN0 y eje X del ADXL335 | Canal de X, referencia, tiempos y conversión |
| TIMER0 | Base temporal de adquisición | Fosc, período, prescaler y precarga |
| TIMER1 | Temporización del multiplexado de tres displays | Fosc, período, prescaler y precarga |
| EUSART | Comunicación bidireccional con la GUI | Fosc, baud rate, formato y protocolo |
| GPIO | Displays, LED rojo y buzzer | Asignación de pines, polaridades y manejo eléctrico |
| Interrupciones | Eventos temporizados y recepción serie | Fuentes habilitadas y estrategia final |

## Reglas de configuración

- Verificar registros, bancos y bits en el datasheet oficial del PIC16F887.
- Configurar como digitales únicamente los pines que corresponda; conservar
  AN0 como entrada analógica del LM35.
- El canal de X debe ser distinto de AN0 y confirmarse con el esquema.
- Calcular tiempos y baud rate con la frecuencia real del oscilador.
- Verificar corrientes y compatibilidad eléctrica antes de conectar displays,
  LED, buzzer o GY-61.
- Mantener breves las ISR y procesar los datos en el programa principal cuando
  el diseño temporal lo permita.
