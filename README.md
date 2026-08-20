# Electronica digital 2

Repositorio (carpeta) para subir todo tipo de material útil de la materia **Electrónica Digital 2**.

Es una carpeta **colaborativa** para compartir los trabajos de la materia junto con los archivos correspondientes **.hex** para poder compilar en MPLAB.

---

## Índice

- [Apuntes](./Apuntes)
- [Diapositivas de clase](./Diapositivas%20de%20clase)
- [Ejercicios](./Ejercicios)
- [Parciales](./Parciales)
- [Tareas](./Tareas)
- [Trabajos practicos](./Trabajos%20practicos)

## Contenido

```
ED2/
├── README.md                # este archivo
├── Apuntes/                 # apuntes y material de estudio
├── Diapositivas de clase/   # diapositivas de clase
│   ├── Teorico/
│   └── Practico/
├── Ejercicios/              # ejercicios de la materia
├── parciales/               # parciales
├── Tareas/                  # tareas de la materia
└── Trabajos practicos/      # trabajos prácticos de la materia
```

## Estructura de archivos

El repositorio está dividido en apartados:

| Apartado | Carpeta | Contenido |
|----------|---------|-----------|
| Apuntes | [`Apuntes/`](./Apuntes) | Apuntes y material de estudio |
| Diapositivas de clase | [`Diapositivas de clase/`](./Diapositivas%20de%20clase) | Diapositivas teóricas y prácticas |
| Ejercicios | [`Ejercicios/`](./Ejercicios) | Ejercicios de la materia |
| Parciales | [`Parciales/`](./Parciales) | Parciales |
| Tareas | [`Tareas/`](./Tareas) | Tareas de la materia |
| Trabajos Prácticos | [`Trabajos practicos/`](./Trabajos%20practicos) | Trabajos prácticos de la materia |

Cada ejercicio/tarea debe incluir:

- El **código fuente**: `.S`, `.asm` o `.c`
- El **archivo .hex** compilado, para poder ejecutarlo en MPLAB

> No se suben archivos de compilación intermedios (`.elf`, `.map`, `build/`, `dist/`, etc.).

## Convención de nombres

Para evitar que los archivos se pisen entre participantes, agregar el nombre de quien lo hizo:

```
Tarea_1_Nombre.asm
Ejercicio3_Nombre.S
```

## Cómo colaborar

1. **Clonar** el repositorio:
   ```powershell
   git clone https://github.com/donatolurgo08/Digital2.git
   ```

2. **Agregar tus archivos** en la carpeta correspondiente.

3. **Subir los cambios**:
   ```powershell
   git add .
   git commit -m "Descripción del cambio"
   git push
   ```

4. **Actualizar tu copia** con lo que subieron los demás:
   ```powershell
   git pull
   ```

## Material

- [MPLAB X IDE](https://www.microchip.com/en-us/tools-resources/develop/mplab-x-ide)
