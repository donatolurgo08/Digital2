# Firmware HAND MOTION — PIC16F887

## Fuente de trabajo

Para continuar el desarrollo de adquisición XYZ y de futuros gestos, usar:

- `src/handmotion_work.S`: fuente principal activa de desarrollo, configurada
  para el PIC16F887 y el protocolo v3.
- `src/modules/` y `src/modular/modules/`: módulos incluidos por esa fuente.

`src/handmotion.S` es la fuente original protegida. No es la fuente de trabajo
v3 y no debe reemplazarse ni confundirse con `handmotion_work.S`.

No hay un proyecto MPLAB X (`.X`) ni un Makefile compartible en este repositorio.
La compilación reproducible se hace con PIC-AS desde la línea de comandos; no se
debe usar la tarea local de VS Code que apunta a `prueba_pic/main.S`.

## Herramientas

- Microcontrolador: PIC16F887.
- MPLAB X: 6.35.
- MPLAB XC8 / PIC-AS: 3.10.
- Device Family Pack: `PIC16Fxxx_DFP` 1.8.167.

PIC-AS y el DFP deben estar instalados. En los comandos siguientes, ajustar
`$picAs` y `$dfp` a sus rutas de instalación locales; esas rutas no se guardan
en el repositorio.

## Compilar el firmware de trabajo

Desde la raíz del repositorio, en PowerShell:

```powershell
$picAs = "<ruta XC8 3.10>\pic-as\bin\pic-as.exe"
$dfp = "<ruta MPLAB X>\packs\Microchip\PIC16Fxxx_DFP\1.8.167\xc8"
$src = (Resolve-Path ".\firmware\src").Path
$out = Join-Path $env:TEMP ("handmotion-work-v3-" + (Get-Date -Format "yyyyMMdd-HHmmss"))
New-Item -ItemType Directory -Path $out | Out-Null

Push-Location $src
try {
    & $picAs -mcpu=16F887 "-mdfp=$dfp" "-I$src" `
        -o (Join-Path $out "handmotion_work_v3") "handmotion_work.S"
    if ($LASTEXITCODE -ne 0) { throw "PIC-AS terminó con error $LASTEXITCODE" }
} finally {
    Pop-Location
}
```

El HEX recién compilado queda en
`$out\handmotion_work_v3.hex`; los demás productos PIC-AS también quedan en esa
carpeta temporal. Así no se sobrescriben los HEX versionados de referencia.
La fuente incluye `xc.inc`, provisto por el DFP indicado, y los módulos
relativos a `firmware/src`; no requiere otros archivos fuente fuera de
`firmware/src`.

Como comprobación en el entorno donde se preparó esta publicación, PIC-AS 3.10
compiló sin errores: 1072 palabras de programa y 92 bytes de RAM. El HEX
resultante coincidió byte a byte con `src/handmotion_work_v3.hex`.

## Módulos incluidos

- `modules/display.inc`: multiplexado de los displays y servicio de TIMER1.
- `modules/uart.inc`: EUSART, comandos, respuestas y tramas del protocolo.
- `modular/modules/init.inc`: inicialización de periféricos y estado.
- `modular/modules/timers.inc`: inicialización y cadencia de muestreo.
- `modular/modules/adc.inc`: lectura de canales analógicos.
- `modular/modules/matematicas.inc`: rutinas aritméticas compartidas.
- `modular/modules/temperatura.inc`: conversión de la entrada del LM35.
- `modular/modules/acelerometro.inc`: conversión de aceleraciones X/Y/Z a mg.
- `modular/modules/alarmas.inc`: procesamiento de la alarma térmica.

## UART y versiones

Enlace serial: 9600 Bd, 8N1. DATA usa CRC-8/ATM (polinomio `0x07`, inicial
`0x00`, sin reflexión ni XOR final); el CRC cubre desde LEN hasta el último dato.

- DATA v2, `LEN=8`: secuencia, temperatura, X/Y signed little-endian y flags.
  Z no está presente.
- DATA v3, `LEN=10`: los campos de v2 más Z signed little-endian.
- STATUS conserva `LEN=7`; ACK conserva `LEN=3`. STATUS informa la versión del
  firmware; DATA se identifica por su LEN y no depende de que STATUS llegue
  primero.

## HEX de referencia

- `src/handmotion_work_v2.hex`: referencia v2; SHA-256
  `1C8A894435384AF8BB0C52274F7D9711B25C7B2B9DB52D352FF4EBF6DE40FC37`.
- `src/handmotion_work_v3.hex`: referencia v3 de la fuente de trabajo; SHA-256
  `FE9F41D0BE57F731573ABF9E734CF73898CDFC422F19757F4E4628E192DDC679`.

Los HEX son referencias versionadas; no son la fuente editable. Para programar
el PIC, seleccionar el dispositivo PIC16F887 y usar el HEX generado con un
programador compatible. Los pasos concretos dependen del programador y del
hardware disponible.

## Estado y límites

`handmotion_work.S` implementa adquisición XYZ y transmisión DATA v3; no
implementa reconocimiento de gestos completos. La publicación deja una base
para continuar ese desarrollo.

Según el estado informado por el usuario, X/Y fueron validados físicamente y Z
respondió en una prueba física; Z aún no está calibrado. El offset de cero-g y
el factor de conversión de Z en `handmotion_work.S` están marcados como
provisionales. Esta compilación no prueba hardware ni gestos.
