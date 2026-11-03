# HAND MOTION
## README técnico y guía de desarrollo

**Proyecto:** Trabajo Práctico Integrador — Electrónica Digital II  
**Microcontrolador:** Microchip PIC16F887  
**Firmware:** Assembler para PIC16F887  
**Toolchain:** `pic-as` (XC8)  
**Entorno:** MPLAB X; VS Code como alternativa para ejecutar la compilación configurada  
**Estado:** especificación de trabajo. Los datos marcados como pendientes deben confirmarse antes de fijarlos en firmware o hardware.

> ## Instrucciones para OpenCode
> Leer este README completo antes de modificar el repositorio. Inspeccionar primero los archivos existentes y conservar todo lo que ya funcione.
>
> El firmware debe escribirse en **Assembler para PIC16F887**, compatible con `pic-as`. No convertir el proyecto a C ni copiar ejemplos MPASM antiguos sin verificar su compatibilidad.
>
> No inventar frecuencia de oscilador, configuration bits, pines, baud rate, prescalers, precargas, polaridad de displays ni protocolo serie. Si un dato necesario no está confirmado, marcarlo como pendiente y consultar antes de tomar una decisión que afecte al hardware.
>
> Trabajar por etapas pequeñas. Compilar después de cada cambio importante y distinguir entre código escrito, compilado y probado físicamente.

---

## 1. Descripción general

**HAND MOTION** es un sistema electrónico programable destinado a reconocer movimientos e inclinaciones de la mano. La adquisición se realiza mediante un acelerómetro analógico **ADXL335**, incorporado en el módulo **GY-61**. En la primera versión, el reconocimiento utilizará exclusivamente la señal del **eje X**. Los ejes Y y Z quedan como posible ampliación futura, fuera del alcance inicial.

El microcontrolador **PIC16F887** adquiere y digitaliza la señal analógica, procesa sus variaciones y las asocia con los movimientos o comandos definidos para el sistema. La información reconocida se intercambia con una computadora mediante comunicación serie. Desde una interfaz gráfica (GUI), la computadora permitirá configurar y ajustar el sistema, además de visualizar los datos recibidos.

De manera independiente al reconocimiento de movimientos, el sistema supervisará la temperatura del PIC16F887 mediante un sensor LM35. La temperatura se visualizará localmente en tres displays de siete segmentos. Si supera los 40 °C, se activará una alarma visual y acústica.

El proyecto es educativo y experimental; no debe presentarse como un dispositivo médico ni atribuirle capacidades de diagnóstico.

### Objetivos

1. Adquirir la señal analógica del eje X del ADXL335 mediante el ADC del PIC16F887.
2. Procesar las variaciones de esa señal para reconocer los movimientos definidos.
3. Configurar y ajustar el sistema desde una GUI en la computadora.
4. Intercambiar información con la computadora mediante EUSART y un conversor USB-TTL.
5. Visualizar localmente la temperatura del LM35 mediante tres displays.
6. Activar un LED rojo y un buzzer activo cuando la temperatura supere los 40 °C.
7. Utilizar temporizadores e interrupciones para organizar la adquisición y la visualización.

---

## 2. Requisitos y decisiones confirmadas

### 2.1 Hardware

| Elemento | Función |
|---|---|
| PIC16F887 | Control y procesamiento |
| GY-61 con ADXL335 | Sensor analógico de movimiento |
| Eje X del ADXL335 | Único eje de reconocimiento en la primera versión |
| LM35 | Supervisión térmica del PIC |
| Tres displays de siete segmentos | Visualización local de temperatura |
| LED rojo | Alarma visual |
| Buzzer activo | Alarma acústica |
| Conversor USB-TTL | Comunicación serie con la computadora |
| Computadora con GUI | Configuración y visualización |

### 2.2 Decisiones funcionales confirmadas

- **No se utilizará teclado matricial ni otro teclado físico.**
- Toda configuración y ajuste del sistema se realizará desde la computadora mediante la GUI y el enlace serie.
- La comunicación deberá permitir que la PC envíe parámetros/comandos de configuración y que el PIC devuelva movimientos reconocidos e información de estado.
- El reconocimiento inicial utilizará solamente el eje X del ADXL335. Y y Z quedan para una posible ampliación.
- El LM35 se utiliza exclusivamente para supervisión térmica; no interviene en el reconocimiento de gestos.
- La salida del LM35 se conectará obligatoriamente al canal **AN0**.
- Si la temperatura medida es **mayor que 40 °C**, se activarán simultáneamente el LED rojo y el buzzer activo.
- Se utilizarán **tres displays de siete segmentos**: dos para los dígitos numéricos de temperatura y el tercero para indicar la unidad °C mediante la letra C y el punto decimal, según la disposición definida para el montaje.
- No se incorpora una etapa de potencia para cargas o actuadores externos.

### 2.3 Datos pendientes: no inventar

Confirmar antes de implementar:
- Frecuencia y fuente del oscilador del PIC16F887.
- Configuration bits correspondientes al circuito real.
- Pines para eje X, displays, selección de dígitos, segmentos, LED y buzzer.
- Tipo de displays (ánodo común o cátodo común), transistores de multiplexado y resistencias.
- Tensión admitida por el módulo GY-61 concreto y compatibilidad de su salida con el ADC.
- Baud rate de EUSART.
- Formato y comandos del protocolo entre GUI y PIC.
- Parámetros configurables desde la GUI y sus rangos.
- Período de adquisición y criterios/umbrales de reconocimiento.
- Prescalers y precargas definitivos de TIMER0 y TIMER1.
- Esquema de alimentación y consumo de los módulos.

No asignar pines ni valores eléctricos por suposición.

---

## 3. Arquitectura de hardware

### 3.1 PIC16F887

El PIC16F887 será el núcleo de control. Se prevé utilizar:
- **ADC:** digitalización del eje X del ADXL335 y del LM35 conectado a AN0.
- **EUSART:** recepción de configuración desde la GUI y transmisión de movimientos reconocidos/estado hacia la PC.
- **TIMER0:** base de tiempo para la adquisición periódica de señales analógicas.
- **TIMER1:** temporización del multiplexado de los tres displays.
- **GPIO:** control de displays, LED rojo y buzzer activo.
- **Interrupciones:** atención de eventos temporizados y coordinación de tareas periódicas.

### 3.2 Sensor de movimiento: GY-61 / ADXL335

El módulo GY-61 incorpora el acelerómetro analógico ADXL335. En la primera versión se utilizará únicamente su salida **X**, conectada a un canal ADC del PIC distinto de AN0, reservado para el LM35. El canal concreto para X queda pendiente de asignación.

El firmware deberá adquirir muestras periódicas, analizar las variaciones de la señal y aplicar los criterios definidos para reconocer movimientos. Los umbrales y el algoritmo no deben inventarse: deberán definirse y ajustarse mediante pruebas con el sensor real.

**Precauciones:**
- Verificar la tensión admitida por el módulo GY-61 concreto; no asumir que cualquier placa puede alimentarse con 5 V.
- Verificar que la salida X no supere el rango permitido por la entrada ADC del PIC.
- Compartir GND entre sensor y microcontrolador.
- Consultar la documentación del módulo y del ADXL335 antes de conectarlo.

### 3.3 Sensor térmico LM35

El LM35 medirá la temperatura en las proximidades del PIC16F887, para representar razonablemente sus condiciones térmicas de funcionamiento.
- Salida analógica conectada obligatoriamente a **AN0**.
- El ADC convierte la señal y el firmware obtiene la temperatura.
- La supervisión térmica es independiente del reconocimiento de movimientos.
- Cuando T > 40 °C, se activan simultáneamente el LED rojo y el buzzer activo.

No utilizar el LM35 para reconocer gestos ni mezclar la alarma térmica con los eventos de movimiento.

### 3.4 Displays de siete segmentos

Se utilizarán **tres displays individuales**:
- Dos displays para representar los dígitos numéricos de la temperatura.
- Un tercer display para indicar la unidad °C, representando la letra C y utilizando el punto decimal según la disposición definida.

Los tres displays se actualizarán mediante multiplexado. TIMER1 será la referencia temporal prevista para alternar su activación. La rutina deberá ser breve y periódica para evitar parpadeos visibles.

Pendiente de confirmar: ánodo/cátodo común, pines de segmentos y selección, circuito de excitación, resistencias y convención exacta para la letra C y el punto decimal. Verificar corrientes y transistores de manejo antes de conectar directamente al PIC.

### 3.5 Alarma térmica

La alarma está formada por un LED rojo y un buzzer activo. Ambos se activarán simultáneamente cuando la temperatura medida por el LM35 supere los 40 °C. Los pines y la etapa de manejo deben definirse según los componentes reales. No asumir que el buzzer puede alimentarse directamente desde un GPIO.

### 3.6 Comunicación con la computadora

El PIC se comunicará mediante **EUSART** y un conversor **USB-TTL**. La comunicación será funcionalmente bidireccional:
- La GUI enviará parámetros y ajustes de configuración.
- El PIC recibirá e interpretará esos comandos.
- El PIC transmitirá los movimientos reconocidos y la información de estado acordada.
- La GUI mostrará los datos recibidos y permitirá modificar los parámetros disponibles.

El protocolo, los comandos, el formato de mensajes y el baud rate todavía deben especificarse. No inventar un protocolo definitivo.

Verificar niveles lógicos compatibles, GND común y conexión cruzada TX/RX. El baud rate se calculará a partir de la frecuencia real del oscilador. No conectar señales RS-232 directamente a los pines TTL del PIC.

---

## 4. Arquitectura del firmware

Organizar el firmware por responsabilidades. Al principio puede mantenerse en un único archivo fuente si eso facilita la compilación; separar en módulos cuando el proyecto esté estable.

Módulos lógicos sugeridos:
1. `init`: inicialización del microcontrolador, reloj, puertos y periféricos.
2. `adc`: selección de canal, adquisición y conversión.
3. `sensor_motion`: lectura y procesamiento de la señal X del ADXL335.
4. `temperature`: conversión de AN0 a temperatura.
5. `display`: codificación y multiplexado de los tres displays.
6. `alarm`: control del LED rojo y el buzzer.
7. `uart`: transmisión y recepción mediante EUSART.
8. `protocol`: interpretación de comandos de la GUI y armado de respuestas.
9. `timer`: configuración y atención de TIMER0 y TIMER1.
10. `main`: bucle principal y coordinación de tareas.

No es obligatorio crear un archivo por módulo al inicio. La prioridad es una implementación incremental, compilable y verificable.

---

## 5. Uso previsto de periféricos

| Periférico | Uso |
|---|---|
| ADC | Digitalización del eje X del ADXL335 y del LM35 en AN0 |
| EUSART | Recepción de configuración desde GUI y transmisión de movimientos/estado a PC |
| TIMER0 | Base de tiempo para adquisición periódica de señales analógicas |
| TIMER1 | Temporización del multiplexado de los tres displays |
| GPIO | Control de segmentos, selección de displays, LED y buzzer |
| Interrupciones | Atención de eventos temporizados y coordinación de tareas periódicas |

La asignación concreta de registros, bits, canales y pines debe verificarse en el datasheet del PIC16F887.

---

## 6. Secuencia de desarrollo

No desarrollar todo el sistema de una sola vez. Completar, compilar y verificar cada etapa antes de continuar.

### Etapa 0 — Inspección del entorno
1. Inspeccionar los archivos existentes y preservar lo que funcione.
2. Identificar el comando/tarea de compilación actual.
3. Confirmar PIC16F887, versión de `pic-as` y Device Family Pack.
4. Confirmar oscilador y configuration bits.

**Salida:** procedimiento reproducible para compilar un programa mínimo.

### Etapa 1 — Esqueleto mínimo
1. Crear o revisar vector de reset e inicialización.
2. Configurar puertos cuando los pines estén confirmados.
3. Configurar reloj y configuration bits con los datos reales.
4. Compilar y corregir errores.

**Salida:** programa mínimo compilado correctamente.

### Etapa 2 — ADC y LM35
1. Configurar el ADC para leer AN0.
2. Realizar conversiones y comprobar resultados.
3. Convertir la lectura a temperatura según la referencia y resolución ADC reales.
4. Verificar la medición con un procedimiento de prueba apropiado.

**Salida:** lectura estable del LM35 y conversión documentada a °C.

### Etapa 3 — Alarma térmica
1. Configurar GPIO de LED y buzzer.
2. Comparar la temperatura con 40 °C.
3. Activar ambos simultáneamente cuando T > 40 °C.
4. Verificar activación y desactivación alrededor del umbral.

**Salida:** alarma visual y acústica comprobada.

### Etapa 4 — Displays multiplexados
1. Confirmar tipo de displays y circuito de manejo.
2. Implementar codificación de dígitos y letra C.
3. Implementar multiplexado de tres displays con TIMER1.
4. Mostrar la temperatura del LM35.
5. Comprobar legibilidad, parpadeo y corrientes.

**Salida:** visualización correcta de temperatura y unidad.

### Etapa 5 — Adquisición del eje X
1. Confirmar canal ADC y conexión X.
2. Configurar adquisición periódica mediante TIMER0.
3. Leer y almacenar muestras del eje X.
4. Observar variaciones al inclinar y mover la mano.
5. Definir y probar criterios de reconocimiento.

**Salida:** muestras coherentes y reconocimiento inicial reproducible.

### Etapa 6 — EUSART y protocolo GUI
1. Confirmar baud rate y conexiones.
2. Implementar transmisión PIC → PC.
3. Implementar recepción PC → PIC.
4. Definir formato, comandos, delimitadores, validación y manejo de errores.
5. Probar con una terminal serie.
6. Integrar la GUI para configurar parámetros y visualizar movimientos/estado.

**Salida:** intercambio bidireccional estable y protocolo documentado.

### Etapa 7 — Integración y validación
1. Integrar adquisición, reconocimiento, temperatura, alarma, displays y comunicación.
2. Evitar que la interfaz o UART bloqueen la adquisición.
3. Mantener breves las rutinas de interrupción.
4. Verificar que la alarma térmica funcione independientemente.
5. Probar que la configuración desde GUI no interfiera con la operación.
6. Registrar resultados y limitaciones reales.

---

## 7. Temporizadores e interrupciones

### TIMER0 — Adquisición

TIMER0 será la base temporal para programar adquisiciones periódicas de las señales analógicas. El período dependerá de la frecuencia del oscilador, prescaler y objetivo de muestreo.

La interrupción deberá realizar el mínimo trabajo: actualizar una bandera o contador de evento y, si corresponde, preparar la siguiente temporización. La conversión ADC y el procesamiento se realizarán en el programa principal siempre que el diseño temporal lo permita.

### TIMER1 — Multiplexado

TIMER1 temporizará la alternancia de los tres displays. La rutina seleccionará el display correspondiente y actualizará el patrón de segmentos sin demoras largas.

### Reglas para las ISR

- Identificar la fuente de interrupción y limpiar el flag correspondiente.
- Guardar y restaurar el contexto necesario.
- Mantener la ISR breve y predecible.
- No ejecutar procesamiento complejo de gestos, formateo de mensajes, esperas UART ni operaciones bloqueantes dentro de la ISR.
- Evitar perder eventos silenciosamente; utilizar contadores cuando sea necesario.
- Documentar períodos, prescalers y precargas cuando se confirme el oscilador.

No fijar valores numéricos de temporizadores hasta conocer Fosc y los parámetros definitivos.

---

## 8. Reglas para Assembler y `pic-as`

- Mantener como dispositivo objetivo el PIC16F887.
- Utilizar sintaxis compatible con la versión instalada de `pic-as`.
- Consultar la documentación antes de definir directivas, secciones y vectores.
- Verificar bancos de RAM y selección de banco en cada acceso.
- Definir nombres simbólicos para registros y variables.
- Documentar registros modificados y valores devueltos por cada subrutina.
- En operaciones de más de 8 bits, documentar orden de bytes, signo y acarreo.
- No copiar código de PIC16F877, MPASM clásico u otras familias sin verificar diferencias.
- Compilar después de cada etapa y reportar el resultado real.
- No afirmar que el hardware fue probado si solo se compiló el firmware.

---

## 9. Criterios generales de aceptación

La primera versión podrá considerarse integrada cuando:
1. El PIC16F887 adquiere la señal X del ADXL335.
2. El firmware reconoce los movimientos definidos para la primera versión.
3. La GUI permite configurar los parámetros acordados mediante comunicación serie.
4. El PIC transmite movimientos reconocidos e información de estado a la PC.
5. El LM35 conectado a AN0 mide la temperatura.
6. Los tres displays muestran los dos dígitos y la indicación °C.
7. Ante T > 40 °C, LED rojo y buzzer activo se encienden simultáneamente.
8. La supervisión térmica funciona independientemente del reconocimiento.
9. El funcionamiento integrado se prueba y documenta con el hardware real.

---

## 10. Datos a solicitar cuando sean necesarios

No pedir todo de una vez. Solicitar únicamente los datos que bloqueen la etapa inmediata:
- Frecuencia y fuente del oscilador.
- Asignación definitiva de pines.
- Canal ADC para el eje X.
- Tipo y conexión de los tres displays.
- Tensión de alimentación/compatibilidad del GY-61.
- Baud rate de EUSART.
- Comandos y formato del protocolo GUI.
- Parámetros configurables.
- Período de adquisición y criterios de reconocimiento.

---

## 11. Forma de trabajo esperada de OpenCode

Para cada etapa, informar:
1. Objetivo.
2. Archivos que se crearán o modificarán.
3. Datos confirmados y pendientes.
4. Código completo de los archivos modificados.
5. Comando real de compilación.
6. Resultado real de compilación.
7. Procedimiento de prueba y resultado esperado.
8. Limitaciones y siguiente paso.

Antes de modificar un archivo, leerlo. Evitar reescrituras innecesarias y mantener el proyecto compilable en cada hito.

---

## 12. Fuentes técnicas

Consultar como referencias primarias:
- Datasheet oficial del **PIC16F887**: ADC, EUSART, TIMER0, TIMER1, interrupciones, puertos, oscilador y bancos de memoria.
- Documentación oficial de **XC8 / `pic-as`** correspondiente a la versión instalada.
- Datasheet del **ADXL335** y documentación del módulo **GY-61** concreto.
- Datasheet del **LM35**.
- Datasheets de los displays y componentes utilizados para multiplexarlos.
- Datasheet del conversor USB-TTL utilizado.

Los manuales y documentos de la cátedra adjuntos al proyecto deben utilizarse para los requisitos académicos. Diferenciar los requisitos de la cátedra de las decisiones de diseño.

---

**Fin del README de HAND MOTION.**
