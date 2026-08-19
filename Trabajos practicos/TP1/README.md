# TPL1 — Programación del MCU (Blink LED)

**Electrónica Digital 2** · Ing. Emiliano Migliore · 2026 (Rev. 2.0)

## Objetivo

Implementar el "Hola Mundo" del hardware: verificar que el microcontrolador
está vivo haciendo parpadear un LED sobre un pin configurado como salida digital.

## Consigna

- Programar el **PIC16F887** con **clock externo (cristal) de 4 MHz**.
- Controlar **1 LED en el pin RC0** con **periodo de intermitencia de 2 s**
  (1 s encendido + 1 s apagado).
- Generar el firmware **`TPL1.hex`**.

## Archivos

| Archivo       | Descripción                                  |
|---------------|----------------------------------------------|
| `TPL1.S`      | Código fuente en Assembly (pic-as / XC8)    |
| `TPL1.hex`    | Firmware compilado para cargar por bootloader|

## Cálculo de la resistencia limitadora (R3)

```
R3 = (V_RC0 - V_D) / I_D = (5 V - 2,24 V) / 6 mA ≅ 470 Ω
```

> Límites del PIC: máx. 25 mA por pin. El LED verde consume ~6 mA → OK.

## Retardo de 1 s (cálculo)

Cristal 4 MHz → clock de instrucción = FOSC/4 = 1 MHz → 1 instrucción = 1 µs.

```
1 s = 1.000.000 µs = 1.000.000 ciclos de instrucción
```

Se usa un retardo por software de 3 bucles anidados (DECFSZ + GOTO):

```
ciclos = (K3-1)·(3·K1·K2 + 4·K2 + 4) + 3·K1·K2 + 4·K2 + 5
```

Con `K1=147`, `K2=107`, `K3=21` → **1.000.000 ciclos = 1 s exacto**.

## Montaje en protoboard

1. PIC16F887 en el zócalo de la placa.
2. Cristal de **4 MHz** en **RA7/OSC1** y **RA6/OSC2**, con capacitores (~22 pF) a GND.
3. Alimentación **5 V** en VDD/VSS y **MCLR (RE3) a VDD** (habilitado).
4. LED verde + R3 (**470 Ω**) en serie entre **RC0** y GND.
5. Cargar `TPL1.hex` mediante bootloader (instructivo "Bootloader y primer programa ED 2").

## Verificación con instrumental

Con el LED encendido, medir con multímetro:

| Medición   | Valor esperado          |
|------------|-------------------------|
| V_RC0      | ~5 V (pin en alto)     |
| V_D        | ~2,24 V (LED verde)    |
| I_D        | ~6 mA = (V_RC0 - V_D)/R3|

Verificar también que el **periodo de intermitencia sea 2 s** (osciloscopio o
cronómetro).

## Cargar el programa con el bootloader

El bootloader es un mini-programa que ya viene grabado en el PIC y permite
cargar el firmware `.hex` sin necesidad de un grabador externo (Pickit).

**Importante:** el PIC16F887 no tiene puerto USB. Para comunicar la PC con el
PIC se necesita un **adaptador USB-UART** externo (módulo CP2102, CH340 o FTDI),
que aparece como un puerto COM en Windows.

### Materiales

- `TPL1.hex` (compilado).
- **Adaptador USB-UART** (CP2102 / CH340 / FTDI).
- Cable USB para conectar el adaptador a la PC.
- Software del bootloader (AN1310 Serial Bootloader, TinyBootloader o el de la placa).

### Conexión del adaptador al PIC

| Adaptador USB-UART | PIC16F887 |
|--------------------|-----------|
| TXD                | RC7/RX    |
| RXD                | RC6/TX    |
| GND                | GND       |

> Las líneas van **cruzadas** (TX→RX y RX→TX). Conectar también el **GND común**
> entre adaptador y placa.

### Pasos

1. Conectar el adaptador USB-UART a la PC con el cable USB.
   Windows instala el driver y le asigna un **puerto COM** (ej. COM3).
   (Administrador de dispositivos → Puertos COM y LPT).
2. Conectar el adaptador al PIC según la tabla: TXD→RC7, RXD→RC6, GND→GND.
3. Abrir el software del bootloader y seleccionar el **puerto COM** asignado.
4. Configurar el **baudrate** (ver abajo).
5. Poner el PIC en **modo bootloader**:
   - Presionar **Reset** mientras el software espera, o
   - el PIC entra solo en modo bootloader durante unos segundos tras encenderse.
   - El software debe mostrar "Connected" / "Found PIC16F887".
6. Abrir el archivo: botón **Open** / **Open Hex** → seleccionar `TPL1.hex`.
7. Grabar: botón **Write** / **Write Flash** / **Program**.
8. Ejecutar: botón **Run** / **Run application** (o reset).
   - Si todo salió bien, el LED en RC0 parpadea (1 s on / 1 s off).

### Datos típicos de comunicación

- Baudrate: normalmente **9600** o **115200** (según el bootloader).
- Pines UART del PIC: **RC6/TX** y **RC7/RX**.

### Advertencias

- El PIC permanece en modo bootloader **solo unos segundos** tras el reset:
  hay que hacer el **Write** dentro de esa ventana de tiempo.
- **No** usar un grabador ICSP (Pickit) para programas comunes: puede
  **borrar el bootloader** del PIC y dejar de poder cargar por USB.

## Compilación

Desde la carpeta `TP1`:

```
pic-as -mcpu=16F887 -mdfp=<DFP> -Wl,-presetVec=0h -o TPL1.hex TPL1.S
```