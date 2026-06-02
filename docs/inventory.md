# Inventario inicial

Este inventario corresponde a la primera organizacion basica del repositorio. No se borro ningun archivo; los materiales se movieron para separar el proyecto matematico de los notebooks no matematicos, copias y exports crudos.

## Resumen

| Seccion | Archivos | Tamano aprox. | Comentario |
|---|---:|---:|---|
| `notebooks/math/` | 8 | 2.44 MB | Nucleo matematico curado. |
| `notebooks/archive/non_math/visualization/` | 5 | 1.57 MB | Visualizacion general e inspiracion no central. |
| `notebooks/archive/non_math/teaching/` | 15 | 1.01 MB | Clases, pandas, sesiones y ejercicios. |
| `notebooks/archive/non_math/audio/` | 3 | 0.06 MB | Parselmouth, TTS y audio. |
| `notebooks/archive/non_math/unknown/` | 64 | 12.95 MB | Notebooks genericos o pendientes de revisar. |
| `notebooks/archive/duplicates/` | 11 | 0.92 MB | Copias claras, notebooks vacios o casi duplicados. |
| `notebooks/archive/raw_exports/` | 2 | 11.40 MB | ZIP originales de Colab. |

## Archivos importantes

| Archivo | Tema |
|---|---|
| `notebooks/math/all_geometries.ipynb` | Geometrias y modelos visuales del proyecto. |
| `notebooks/math/starlike_curves.ipynb` | Curvas estrelladas. |
| `notebooks/math/logarithm_star_carleson.ipynb` | Estrella logaritmica y condicion de Carleson. |
| `notebooks/math/muckenhoupt_weights.ipynb` | Pesos de Muckenhoupt. |
| `notebooks/math/slowly_oscillating_shift.ipynb` | Slowly oscillating shifts. |
| `notebooks/math/cusp_types.ipynb` | Tipos de cuspides. |
| `notebooks/math/karlovich_lemma_52.ipynb` | Lema 52 de Karlovich. |
| `notebooks/math/yuri_karlovich_experiments.ipynb` | Experimentos relacionados con Karlovich/Yuri. |

## Duplicados detectados

Duplicados normalizados significa que coinciden despues de ignorar metadata, execution counts y outputs.

| Grupo | Archivos |
|---|---|
| `all_geometries` | `notebooks/math/all_geometries.ipynb`, `notebooks/archive/duplicates/math/all_geometries_colab_copy.ipynb` |
| `logarithm_star_carleson` | `notebooks/math/logarithm_star_carleson.ipynb`, `notebooks/archive/duplicates/math/logarithm_star_carleson_colab_copy.ipynb` |
| `starlike_curves` | `notebooks/math/starlike_curves.ipynb`, `notebooks/archive/duplicates/math/starlike_curves_colab_copy.ipynb` |
| `factorial_inverse` | `notebooks/archive/non_math/teaching/factorial_inverse.ipynb`, `notebooks/archive/duplicates/teaching/factorial_inverse_copy.ipynb` |
| `princess_game` | `notebooks/archive/non_math/teaching/princess_game.ipynb`, `notebooks/archive/duplicates/teaching/princess_game_copy.ipynb` |
| `rose_curves` | `notebooks/archive/non_math/visualization/rose_curves.ipynb`, `notebooks/archive/duplicates/visualization/rose_curves_untitled_no_extension.ipynb` |
| Notebooks vacios | `notebooks/archive/duplicates/empty/` y varios `Untitled*.ipynb` en `unknown/` |

## Archivos grandes

| Tamano aprox. | Archivo |
|---:|---|
| 7.35 MB | `notebooks/archive/raw_exports/colab_notebooks_20260602T033732Z_3_001.zip` |
| 4.04 MB | `notebooks/archive/raw_exports/colab_notebooks_20260602T033554Z_3_001.zip` |
| 3.03 MB | `notebooks/archive/non_math/unknown/colab_20260602T033732Z_3_001/Untitled16.ipynb` |
| 2.30 MB | `notebooks/archive/non_math/unknown/colab_20260602T033732Z_3_001/Untitled21.ipynb` |
| 2.14 MB | `notebooks/archive/non_math/unknown/colab_20260602T033732Z_3_001/Untitled5.ipynb` |
| 0.84 MB | `notebooks/math/slowly_oscillating_shift.ipynb` |
| 0.84 MB | `notebooks/math/yuri_karlovich_experiments.ipynb` |
| 0.70 MB | `notebooks/archive/non_math/visualization/venn_diagram.ipynb` |

## Conviene renombrar o revisar

- `notebooks/archive/non_math/unknown/`: contiene `Untitled*`, `Metadata.ipynb`, `PDFExtractorKit.ipynb`, `Ejemplo*.ipynb` y otros notebooks que no se clasificaron como parte del proyecto matematico.
- Algunos `Untitled*` parecen contener visualizaciones o pruebas matematicas aisladas, pero el nombre no permite curarlos con seguridad sin revision humana.
- Los notebooks con outputs pesados pueden limpiarse en una segunda version con `nbstripout`, despues de decidir si los renders embebidos son utiles.

## Assets y outputs

No se encontraron imagenes, GIFs, videos o PDFs sueltos fuera de notebooks. Se prepararon las carpetas `assets/` y `outputs/` para futuras imagenes finales seleccionadas, GIFs, videos y referencias.

## Recomendaciones para `.gitignore`

Ya se ignoran caches de Python, checkpoints de Jupyter, entornos virtuales, outputs temporales y renders temporales de Manim. No se ignoran por defecto imagenes, GIFs, videos finales, notebooks curados ni scripts fuente.

## Pendiente para segunda version

- Revisar `notebooks/archive/non_math/unknown/` y rescatar cualquier notebook realmente matematico.
- Decidir si los ZIP crudos deben quedarse versionados o moverse a almacenamiento externo.
- Limpiar outputs pesados con `nbstripout` o una politica equivalente.
- Agregar escenas Manim reutilizables en `src/manim_scenes/` cuando el material ya este curado.
- Definir una licencia del repositorio.
