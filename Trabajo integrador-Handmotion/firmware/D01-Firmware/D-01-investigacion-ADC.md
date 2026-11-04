# D-01 — Investigación de periféricos del PIC16F887

**Responsable:** Donato Lurgo  
**Estado:** En investigación — D-01.1 (ADC) documentado; resto pendiente.  
**Dispositivo:** PIC16F887  
**Toolchain del proyecto:** Assembler `pic-as` (XC8)

## D-01.1 — ADC (conversor analógico-digital)

### Función y aplicación

El ADC del PIC16F887 convierte una tensión analógica en un resultado binario de
**10 bits** mediante aproximaciones sucesivas. Sus entradas analógicas se
multiplexan hacia un único circuito de sample-and-hold y el resultado se guarda
en `ADRESH:ADRESL`. El PIC16F887 dispone de los canales AN0–AN13.

Para HAND MOTION:

- El LM35 se conecta obligatoriamente a **AN0/RA0**.
- El eje X del ADXL335 debe conectarse a otro canal ADC; el canal todavía no está
  asignado.
- La rutina de adquisición debería aceptar un canal como parámetro, para permitir
  agregar Y y Z posteriormente sin cambiar el esquema general de lectura.

### Registros y bits principales

| Registro | Función relevante |
|---|---|
| `ANSEL` | Selecciona como analógicas las entradas AN0–AN7 (bits implementados según el dispositivo). `ANS0=1` habilita RA0/AN0 como entrada analógica. |
| `ANSELH` | Selecciona las entradas analógicas AN8–AN13 mediante `ANS8`–`ANS13`. |
| `TRISA`, `TRISB`, `TRISE` | El pin del canal usado debe configurarse como entrada (`TRIS=1`). El puerto depende del canal. |
| `ADCON0` | `ADCS<1:0>` selecciona el reloj ADC; `CHS<3:0>` selecciona el canal; `GO/DONE` inicia/indica el estado de la conversión; `ADON` enciende el módulo. |
| `ADCON1` | `ADFM` selecciona el formato del resultado; `VCFG1:VCFG0` seleccionan las referencias negativa y positiva. |
| `ADRESH:ADRESL` | Registros con el resultado de 10 bits; la distribución depende de `ADFM`. |
| `PIR1.ADIF`, `PIE1.ADIE` | Bandera y habilitación de la interrupción ADC, si se decide usarla. `ADIF` se limpia por software. |

Los SFR están distribuidos en bancos; el código debe seleccionar el banco antes
de accederlos, por ejemplo con `BANKSEL` en `pic-as`.

### Selección de canal y pin

`CHS<3:0>` en `ADCON0` conecta un canal al sample-and-hold. La codificación es
directa para los canales: `0000 = AN0`, `0001 = AN1`, …, `1101 = AN13`.

Mapa de canales disponible en el PIC16F887:

| Canal | Pin del puerto |
|---|---|
| AN0 | RA0 — asignado al LM35 |
| AN1–AN4 | RA1, RA2, RA3, RA5 |
| AN5–AN7 | RE0, RE1, RE2 |
| AN8–AN13 | RB2, RB3, RB1, RB4, RB0, RB5 |

Son canales candidatos, no asignaciones del proyecto. El pin físico depende del
encapsulado concreto del PIC. Para una entrada analógica, el pin correspondiente
debe tener el driver de salida deshabilitado (`TRIS=1`) y su bit analógico
habilitado en `ANSEL` o `ANSELH`. Las entradas configuradas como analógicas se
leen como cero a través de `PORT`; se debe leer el resultado convertido en
`ADRESH:ADRESL`.

### Referencias y formato

`VCFG0=0` selecciona `VDD` como referencia positiva y `VCFG0=1` selecciona el
pin `VREF+`. `VCFG1=0` selecciona `VSS` como referencia negativa y `VCFG1=1`
selecciona `VREF-`. Esos pines de referencia comparten funciones con RA3/AN3
(`VREF+`) y RA2/AN2 (`VREF-`). La referencia a usar en el montaje todavía debe
confirmarse; no se fija una en este documento.

`ADFM=1` deja el resultado justificado a la derecha: `ADRESL` contiene los bits
7–0 y `ADRESH<1:0>` contiene los bits 9–8. `ADFM=0` lo justifica a la izquierda.
El fragmento de abajo usa justificación a la derecha solo para ilustrar cómo
guardar los diez bits; la decisión definitiva se puede tomar al diseñar el
procesamiento.

Idealmente, un LSB corresponde a `(VREF+ − VREF−) / 1024`. Por lo tanto, la
conversión a voltios requiere conocer las referencias reales y aplicar las
características eléctricas y errores especificados por Microchip; no se fijan
valores de tensión aquí.

### Reloj de conversión y adquisición

Las opciones seleccionables por `ADCS<1:0>` son `FOSC/2`, `FOSC/8`, `FOSC/32`
y `FRC` (oscilador interno dedicado al ADC). La conversión de 10 bits requiere
**11 períodos `TAD`**, además del tiempo de adquisición previo.

Microchip especifica para `TAD` un rango de 1.6–9 µs cuando `VREF ≥ 3.0 V` y
3–9 µs para el rango completo de referencia. Por eso, el divisor no se puede
elegir hasta conocer `FOSC` y la referencia; hay que contrastarlo con la tabla
de relojes ADC y las especificaciones eléctricas. El modo `FRC` no se adopta
automáticamente: la hoja de datos lo recomienda especialmente para conversiones
durante Sleep cuando `FOSC > 1 MHz`.

Después de seleccionar o cambiar de canal, el capacitor interno de sample-and-
hold necesita tiempo para adquirir la nueva tensión. La hoja de datos recomienda
una impedancia máxima de fuente analógica de **10 kΩ**; el tiempo de adquisición
depende, entre otros factores, de la impedancia de fuente, tensión y temperatura.
El ejemplo de cálculo del datasheet no se toma como constante del proyecto.

### Procedimiento de lectura de un canal

1. Configurar como entrada el pin seleccionado (`TRIS=1`).
2. Habilitar su función analógica en `ANSEL` o `ANSELH`.
3. Configurar referencias, formato y reloj en `ADCON1`/`ADCON0` según el circuito
   y `FOSC` reales.
4. Seleccionar el canal con `CHS<3:0>` y habilitar el ADC con `ADON=1`.
5. Esperar el tiempo de adquisición requerido; repetirlo después de cambiar de
   canal.
6. Iniciar la conversión poniendo `GO/DONE=1`.
7. Esperar a que `GO/DONE` vuelva a cero, o atender `ADIF` si se implementa la
   interrupción ADC.
8. Leer `ADRESH:ADRESL` y almacenar los bits del resultado.
9. Si se habilitó la interrupción, limpiar `ADIF` por software. La bandera se
   activa al terminar cada conversión incluso si la interrupción no está
   habilitada.

### Fragmento Assembly de referencia

El siguiente fragmento muestra el inicio, espera y lectura para un canal ya
seleccionado. **No es compilable por sí solo:** presupone que el pin, `ANSEL`,
las referencias, `ADFM`, `ADCS`, el canal y el tiempo de adquisición se
configuraron previamente. Esos valores no se inventan mientras falten los datos
del circuito.

```asm
; ADC ya habilitado y canal seleccionado; adquisición ya cumplida.
    BANKSEL ADCON0
    BSF     ADCON0, GO         ; Inicia conversión

ESPERA_ADC
    BTFSC   ADCON0, GO         ; GO=1 mientras convierte
    GOTO    ESPERA_ADC

    BANKSEL ADRESL
    MOVF    ADRESL, W          ; ADFM=1: bits 7..0
    MOVWF   ADC_RESULT_L
    BANKSEL ADRESH
    MOVF    ADRESH, W          ; ADFM=1: bits 9..8 en ADRESH<1:0>
    MOVWF   ADC_RESULT_H
```

`ADC_RESULT_L` y `ADC_RESULT_H` representan variables RAM que deberán definirse
en el firmware. Si se usa polling, no hace falta habilitar `ADIE`; si se usa
interrupción, se debe tratar `PIR1.ADIF` y habilitar las máscaras necesarias de
interrupciones periféricas/globales.

### Aplicaciones del ADC en HAND MOTION

- Leer el LM35 por AN0 para obtener la temperatura, mostrarla en los displays y
  activar la alarma cuando supere 40 °C.
- Leer la salida X del ADXL335 por un canal diferente de AN0 y entregar las
  muestras al reconocimiento de movimientos y a la GUI.
- Mantener la lectura seleccionable por canal para poder sumar Y y Z en una
  ampliación futura.

### Fuentes consultadas — ADC

1. Microchip, *PIC16F882/883/884/886/887 Data Sheet*, DS41291D, secciones 3.1,
   3.2.1, 3.4.1 y 9.0–9.3; tablas 1-2, 9-1 y 9-2; características ADC en
   sección 17.0, pp. 99–109 y 257–258 del documento. [PDF oficial](https://ww1.microchip.com/downloads/en/DeviceDoc/41291D.pdf).
