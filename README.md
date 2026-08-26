# Electronica digital 2

Repositorio (carpeta) para subir todo tipo de material util de la materia **Electronica Digital 2**.

Es una carpeta **colaborativa** para compartir los trabajos de la materia junto con los archivos correspondientes **.hex** para poder compilar en MPLAB.

---

## Rama dev-Trabajos_conjuntos

Esta rama es una linea de trabajo **separada del main**, creada para avanzar en conjunto (co-work) en los **Trabajos Practicos** sin modificar los archivos principales del repositorio.

- Todo lo que se hace aca queda aislado del `main`: los cambios no afectan la version oficial hasta que se decida fusionarlos (mediante un Pull Request).
- Su objetivo es permitir que dos o mas personas trabajen en paralelo sobre los TP, probando y editando, sin romper lo que ya esta en el main.
- Al finalizar un TP, se sube un Pull Request para revisar y unir los cambios al `main`.

> Mientras trabajamos en esta rama, el `main` permanece intacto y estable.

---

## Indice

- [Apuntes](./Apuntes)
- [Diapositivas de clase](./Diapositivas%20de%20clase)
- [Ejercicios](./Ejercicios)
- [Parciales](./Parciales)
- [Tareas](./Tareas)
- [Trabajos Practicos](./Trabajos%20Practicos)

## Contenido

```
ED2/
├── README.md                # este archivo
├── Apuntes/                 # apuntes y material de estudio
├── Diapositivas de clase/   # diapositivas de clase
│   ├── Teorico/
│   └── Practico/
├── Ejercicios/              # ejercicios de la materia
├── Parciales/               # parciales
├── Tareas/                  # tareas de la materia
└── Trabajos Practicos/      # trabajos practicos de la materia
    ├── Tp1/
    └── Tp2/
```

## Estructura de archivos

El repositorio esta dividido en apartados:

| Apartado | Carpeta | Contenido |
|----------|---------|-----------|
| Apuntes | [`Apuntes/`](./Apuntes) | Apuntes y material de estudio |
| Diapositivas de clase | [`Diapositivas de clase/`](./Diapositivas%20de%20clase) | Diapositivas teoricas y practicas |
| Ejercicios | [`Ejercicios/`](./Ejercicios) | Ejercicios de la materia |
| Parciales | [`Parciales/`](./Parciales) | Parciales |
| Tareas | [`Tareas/`](./Tareas) | Tareas de la materia |
| Trabajos Practicos | [`Trabajos Practicos/`](./Trabajos%20Practicos) | Trabajos practicos de la materia |

Cada ejercicio/tarea debe incluir:

- El **codigo fuente**: `.S`, `.asm` o `.c`
- El **archivo .hex** compilado, para poder ejecutarlo en MPLAB

> No se suben archivos de compilacion intermedios (`.elf`, `.map`, `build/`, `dist/`, etc.).

## Convencion de nombres

Para evitar que los archivos se pisen entre participantes, agregar el nombre de quien lo hizo:

```
Tarea_1_Nombre.asm
Ejercicio3_Nombre.S
```

## Como colaborar

1. **Clonar** el repositorio:
   ```powershell
   git clone https://github.com/donatolurgo08/Digital2.git
   ```

2. **Posicionarse en esta rama**:
   ```powershell
   git checkout dev-Trabajos_conjuntos
   ```

3. **Agregar tus archivos** en la carpeta correspondiente.

4. **Subir los cambios**:
   ```powershell
   git add .
   git commit -m "Descripcion del cambio"
   git push
   ```

5. **Actualizar tu copia** con lo que subieron los demas:
   ```powershell
   git pull
   ```

## Material

- [MPLAB X IDE](https://www.microchip.com/en-us/tools-resources/develop/mplab-x-ide)
