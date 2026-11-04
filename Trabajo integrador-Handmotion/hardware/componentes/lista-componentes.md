# Lista preliminar de componentes — HAND MOTION

Lista inicial basada en los requisitos confirmados. Las cantidades y
características marcadas como pendientes se cierran al definir encapsulado,
esquema y componentes concretos.

## Componentes confirmados

| Cant. | Componente | Uso / estado |
|---:|---|---|
| 1 | PIC16F887 | Microcontrolador; falta confirmar encapsulado. |
| 1 | Módulo GY-61 con acelerómetro ADXL335 | Movimiento; inicialmente se usa el eje X. Verificar la versión y tensión del módulo. |
| 1 | Sensor LM35 | Temperatura; salida conectada a AN0. |
| 3 | Displays individuales de 7 segmentos, cátodo común | Dos dígitos numéricos y un display para C/punto decimal. |
| 1 | LED rojo | Alarma de temperatura. |
| 1 | Buzzer activo | Alarma acústica; confirmar tensión y corriente. |
| 1 | Conversor USB-TTL | Enlace serie bidireccional con la computadora; tensión lógica pendiente. |
| 1 | Computadora | Ejecuta la GUI y se comunica por puerto serie. |
| 1 | Programador compatible con PIC16F887 | Para cargar el firmware; modelo pendiente. |

No se incluye teclado matricial ni actuadores externos.

## Componentes de soporte por definir en el esquema

- Fuente regulada y distribución de alimentación compatibles con el PIC y los
  módulos. No asumir una tensión hasta verificar el GY-61 concreto y el resto
  del circuito.
- Capacitores de desacople cerca de los pines de alimentación del PIC y módulos;
  cantidad y valores según datasheets y montaje.
- Se usará el oscilador interno del PIC; no hace falta cristal/resonador externo.
  La frecuencia interna y los configuration bits siguen pendientes.
- Circuito de reset/MCLR si la configuración del PIC lo requiere.
- Resistencias limitadoras para los segmentos de los displays y para el LED.
- Transistores/etapa de manejo para seleccionar los dígitos y sus resistencias
  asociadas, según la topología de cátodo común, corriente y esquema de multiplexado.
- Driver para el buzzer únicamente si sus requisitos eléctricos superan los que
  puede manejar con seguridad un GPIO.
- Conectores, headers, cables/jumpers y placa de prototipado o PCB.

## Pendiente de especificar antes de comprar o conectar

- Encapsulado del PIC16F887 y números físicos de pin.
- Pines, transistores/driver, resistencias y corrientes adecuados para los
  displays de cátodo común.
- Tensión de alimentación admitida por el GY-61 concreto y del conversor USB-TTL.
- Corriente del buzzer y estrategia de manejo.
- Frecuencia del oscilador interno, configuration bits y circuito de reset.
- Corrientes por segmento, selección de dígitos y distribución de alimentación.

## Instrumental útil para pruebas

- Multímetro.
- Fuente de laboratorio con límite de corriente ajustable.
- Osciloscopio o analizador lógico para revisar multiplexado y EUSART (opcional).
- Terminal serie para pruebas iniciales del enlace USB-TTL.
