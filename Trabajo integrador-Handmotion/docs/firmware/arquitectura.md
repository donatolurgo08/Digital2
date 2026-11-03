# Arquitectura del firmware

## Organización

El firmware se iniciará en un archivo fuente Assembler para PIC16F887 compatible
con `pic-as`. Se mantendrá la organización comentada usada en los TP del repo
(encabezado, directivas, configuración, constantes, variables, vectores,
inicialización, programa principal, ISR y subrutinas). La sintaxis relocatable
de `pic-as` se tomará como referencia del TP1; no se copiarán directivas MPASM
de TP3/TP4 sin verificar compatibilidad.

Cuando el firmware esté estable, las responsabilidades podrán separarse en:

1. Inicialización y configuración de periféricos.
2. Adquisición y conversión ADC.
3. Procesamiento de temperatura y alarma.
4. Adquisición/procesamiento de movimiento X.
5. Codificación y actualización de displays.
6. Temporizadores e interrupciones.
7. EUSART, buffers y protocolo.
8. Bucle principal e integración de eventos.

## Flujo de ejecución previsto

Las interrupciones señalarán eventos o atenderán operaciones breves. El bucle
principal procesará muestras, temperatura, reconocimiento y mensajes de GUI sin
esperas bloqueantes largas. El multiplexado se temporizará con TIMER1; TIMER0
servirá de base para la adquisición periódica según el período que se defina.

Las rutinas de interrupción deberán ser cortas, guardar/restaurar el contexto
necesario, atender y limpiar la fuente correspondiente. El análisis de gestos,
el parseo de mensajes y el formateo de respuestas no se realizarán dentro de la
ISR.

## Dependencias pendientes

No fijar registros de temporizador, precargas, prescalers, baud rate, pines,
configuración del oscilador ni configuración del PIC hasta confirmar los datos
del circuito y la frecuencia real.
