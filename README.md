# manim-figures-bk

Repositorio de experimentos visuales, notebooks y materiales de referencia para figuras matematicas inspiradas en Böttcher y Karlovich.

El objetivo de este repositorio es conservar y curar materiales utiles para tesis, articulos, presentaciones y futuras escenas de ManimGL. La carpeta principal del proyecto matematico vive en `notebooks/math/`; el resto de notebooks de Colab, clases, audio, visualizacion general y pruebas queda separado en `notebooks/archive/`.

## Contenido

- Notebooks matematicos sobre curvas estrelladas, geometria, cuspides, pesos de Muckenhoupt, Carleson, Karlovich y shifts.
- Experimentos visuales que pueden servir como inspiracion, pero que no son parte del nucleo matematico actual.
- Notebooks de ensenanza, audio y pruebas historicas conservados como archivo.
- Espacios preparados para scripts, escenas Manim, assets y outputs finales seleccionados.

## Estructura

```text
manim-figures-bk/
├── notebooks/
│   ├── math/
│   └── archive/
│       ├── duplicates/
│       ├── non_math/
│       └── raw_exports/
├── src/
│   ├── manim_scenes/
│   └── utils/
├── assets/
│   ├── images/
│   ├── gifs/
│   ├── videos/
│   └── references/
├── outputs/
│   ├── images/
│   ├── gifs/
│   └── videos/
└── docs/
    ├── index.md
    ├── inventory.md
    └── rename_map.md
```

## Instalacion basica

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Las dependencias instaladas por defecto cubren los notebooks matematicos basicos. Dependencias de audio, datos, visualizacion avanzada y ManimGL quedan comentadas en `requirements.txt` para no forzar una instalacion pesada.

## Uso

Abrir los notebooks principales:

```bash
jupyter lab notebooks/math
```

Si en el futuro se agregan escenas Manim reutilizables, deben vivir en `src/manim_scenes/`. Este repositorio aun no intenta convertir todos los experimentos a Manim.

## Notas de curaduria

Algunos notebooks son experimentales, tienen outputs guardados o nombres genericos heredados de Colab. No se eliminaron archivos durante la primera organizacion: los materiales no matematicos se movieron a `notebooks/archive/non_math/`, las copias claras a `notebooks/archive/duplicates/` y los ZIP originales a `notebooks/archive/raw_exports/`.

Consulta `docs/inventory.md` para el inventario inicial y `docs/rename_map.md` para la trazabilidad de renombrados y movimientos.
