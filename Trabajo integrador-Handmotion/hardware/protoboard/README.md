# Protoboard — dos placas de 830 lado a lado

Diagrama de armado de HAND MOTION sobre dos protoboards de 830 puntos unidas
por el lado largo, con las 63 columnas en vertical y los buses de alimentación
a los costados (orientación del MB-102).

- `protoboard.html`: diagrama interactivo, mapa de patas del PIC, tabla de
  redes y guía de armado. Se abre en cualquier navegador, sin dependencias.
- `generar_protoboard.py`: genera el HTML. La geometría, los pines y las redes
  salen de la netlist de `hardware/esquematico/conexiones.txt`.

## Regenerar

```
python generar_protoboard.py
```

El script imprime la ruta del HTML. No requiere librerías externas.

## Geometría adoptada

| Elemento | Ubicación |
|---|---|
| Placa A | PIC U1, R9–R16, LM35, C1/C2/C5–C8, R21–R23, D1/D2, BZ1, J2 |
| Placa B | DS1–DS3, Q1–Q3, R17–R19, C9–C11, J1 |
| U1 PIC16F887 | columnas 22–41; patas 1–20 en fila c, patas 21–40 en fila g |
| DS1 / DS2 / DS3 | filas e–f, columnas 6–10 / 12–16 / 18–22 |
| R9–R16 | placa A, columnas 42–49, cruzando el canal (fila e a fila f) |
| LM35 | placa A, fila a, columnas 56–58 |
| MOD1 | fuera de placa, sobre adaptador, 10 cables a las columnas 2–10 |
| Buses | A izquierda +5V/GND, A derecha GND/+5V, B izquierda +3V3/GND, B derecha GND/+5V |

En esta orientación cada columna de cinco agujeros (a–e o f–j) es **un solo
nodo**. Por eso ningún componente se apoya en una columna ya usada por otra red:
el generador verifica que no haya dos redes en el mismo nodo y que no haya dos
pines en el mismo agujero.

## Buses partidos

Cada bus de cada placa está cortado a la altura de la columna 31/32. Hay que
puentear los 8 tramos (2 por placa y por lado) o media placa queda sin
alimentación.
