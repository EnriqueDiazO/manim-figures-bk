# Disco móvil en arcos y espirales logarítmicas

Dos scripts autónomos basados en el ZIP `manim figures bk.zip` entregado en esta conversación. No se modificaron los notebooks de origen ni se incluyó el historial `.git`.

## Abrir directamente los resultados

`outputs/gifs/arcos_sin_rayos.gif` y `outputs/gifs/estrella_logaritmica.gif` incluyen ejes, título y leyenda. Sus versiones terminadas en `_limpio.gif` sólo muestran la geometría, el disco, el punto y su etiqueta: están destinadas a insertarse en una diapositiva sin repetir los títulos.

Las versiones de arcos duran 20 segundos y recorren las cinco ramas. Las de la estrella logarítmica duran 48 segundos y recorren sus 24 ramas. Los cuatro GIF se repiten indefinidamente y se programaron a 25 cuadros por segundo.

`outputs/videos/` contiene las mismas animaciones en MP4. `outputs/images/` contiene fotogramas PNG y SVG; los PNG y SVG terminados en `_limpio` o `_geometria` tienen fondo transparente. Los archivos `_geometria` muestran únicamente la curva, sin el disco ni el punto. **Los PNG y SVG de este paquete son estáticos; no son animaciones.** Los GIF y MP4 tienen fondo opaco.

## Ejecutar los scripts

Se requiere Python 3.10 o posterior. No se necesita Manim, LaTeX, SciPy ni ImageMagick.

```bash
python -m pip install -r requirements.txt
python 01_arcos_sin_rayos.py
python 02_estrella_logaritmica.py
```

Cada script contiene todas sus funciones. No necesita importar el otro script ni ejecutar previamente los notebooks del repositorio. Por defecto genera las versiones anotada y limpia, además de PNG/SVG, bajo `outputs/`, en el directorio de ejecución.

```bash
# Sólo la versión para insertar en una diapositiva:
python 01_arcos_sin_rayos.py --modo limpio
python 02_estrella_logaritmica.py --modo limpio

# Cambiar duración y resolución:
python 01_arcos_sin_rayos.py --duracion 30 --dpi 160

# Exportar también MP4; el ejecutable FFmpeg debe estar instalado:
python 02_estrella_logaritmica.py --mp4

# Revisar rápidamente la composición sin renderizar los GIF:
python 01_arcos_sin_rayos.py --solo-imagenes

# Guardar en otra carpeta:
python 02_estrella_logaritmica.py --salida mis_animaciones
```

El código comprueba la disponibilidad real de FFmpeg. Si falta, omite el video y conserva las otras exportaciones. En Ubuntu, se puede instalar el ejecutable opcional con `sudo apt install ffmpeg`.

`requirements-tested.txt` registra las versiones utilizadas para esta entrega; `requirements.txt` expresa los mínimos de API previstos, no una matriz completa de versiones verificadas.

## Usar en Jupyter o Colab

Abre uno de los dos archivos de `notebooks/` y ejecuta sus celdas en orden. Cada notebook incluye instalación de dependencias, parámetros editables, todo el código de generación y una celda para mostrar el GIF. No requiere los scripts `.py` a su lado.

Para una prueba corta, cambia `RAMAS_RECORRIDO = [0]` en la celda de configuración y vuelve a ejecutar las celdas siguientes. Después usa:

```python
resumen = generar(duracion=4, fps=15, dpi=90)
```

## Cambios más frecuentes

Los parámetros están al principio de cada script y en la tercera celda de cada notebook.

```python
# Comunes:
EPS_BASE = 0.25              # Radio medio del disco.
EPS_AMP = 0.60               # Variación relativa; 0 da un radio constante.
EPS_FREQ = 1.0               # Ciclos del radio durante toda la animación.
DURACION = 20.0              # Duración TOTAL, no por rama.
FPS = 25
ESTELA = 0.0                 # 0 la desactiva; 0.08 deja una estela corta.
RAMAS_RECORRIDO = None       # None: todas las ramas; [0]: sólo la primera.
MODO = "ambos"              # "anotado", "limpio" o "ambos".
```

Para los arcos:

```python
C_VALORES = [-1.2, -1.0, -0.6, 0.5, 0.9]
```

Son los valores de la animación de origen. No hay una lista de ángulos para rayos: el primer script no los construye.

Para la estrella logarítmica:

```python
N = 24
DELTA = 0.6
R_MIN = 0.03
R_MAX = 3.0
DURACION = 48.0
```

Para dibujar y explorar **una sola espiral**, cambia `N = 1` y `DURACION = 12.0`. Para mantener las 24 espirales visibles pero mover el punto únicamente por la primera, conserva `N = 24` y cambia `RAMAS_RECORRIDO = [0]`. Los índices de esta lista comienzan en cero; las etiquetas matemáticas comienzan en uno.

`DELTA` debe ser distinto de cero en este script para que no aparezcan rayos. `MULTICOLOR = True` usa el ciclo de colores predeterminado de Matplotlib para distinguir las ramas; `False` dibuja toda la curva con un solo estilo base.

## Qué representa la animación

La geometría se mantiene fija. El punto t recorre una rama y el radio epsilon varía. Se resalta la aproximación muestreada de

    Gamma(t, epsilon) = {z en Gamma: |z-t| < epsilon}.

Se evalúa la distancia a t sobre **todas las ramas**, no sólo sobre la que contiene el centro. Por eso varias porciones disjuntas pueden quedar resaltadas simultáneamente. El borde discontinuo representa la circunferencia |z-t| = epsilon; no se rellena el disco.

El programa utiliza epsilon(s) = EPS_BASE * (1 + EPS_AMP * sin(2*pi*EPS_FREQ*s)), donde s es el tiempo normalizado del video. Es un cronograma visual y no una hipótesis del manuscrito ni una función prescrita sobre toda la curva. Con los valores entregados, epsilon varía entre 0.10 y 0.40.

Los tramos se aproximan con 3000 muestras por rama. El resaltado usa la desigualdad estricta. Los cortes con la circunferencia tienen el error de discretización del muestreo; no se afirma haber calculado intersecciones analíticas exactas. Los extremos del trazo pueden verse algo más gruesos por el ancho del pincel.

## Geometría conservada y cambios numéricos

Para los arcos se conserva z = 1/(x-i*c_k), con x entre 10^-3 y 10^3. Se utiliza la reparametrización theta = 2*arctan(x/|c_k|) para repartir mejor las muestras en longitud de arco. No cambia la curva y evita dedicar casi toda la animación a puntos visualmente indistinguibles junto a sus extremos.

Para las espirales se conserva z_k(r) = r*exp(i*(beta_k + delta*log(r))), con beta_k = 2*pi*k/N y los cortes originales 0.03 <= r <= 3. La curva matemática está definida para r>0; la imagen muestra sólo esa ventana radial. **No se añade un segmento recto entre r=0.03 y el origen.**

El punto explora los arcos hacia el extremo próximo al origen; en las espirales va del radio exterior al interior. El recorrido se suaviza al empezar y terminar. Al cambiar de rama, el marcador y el disco se desvanecen brevemente y reaparecen: no se dibuja una trayectoria que atraviese el plano. Este movimiento visual no pretende fijar la orientación de un operador integral.

La estela, cuando se activa, está limitada a la rama actual y se reinicia al cambiar de rama. El marco incluye un margen mayor que el radio máximo para no cortar el disco.

La animación ilustra una porción local de la curva. No calcula la integral de Cauchy, la longitud exacta de dicha porción ni verifica por sí sola una condición de Carleson.

## Integración con las diapositivas

Para el movimiento, utiliza los GIF o los MP4 en el reproductor de la presentación. Para componer una figura estática con fórmulas y anotaciones, utiliza los PNG transparentes o los SVG.

No se probó la reproducción de estos GIF dentro de Mathcha. Su documentación pública de exportación enumera SVG, PNG y PDF, pero no garantiza preservar el movimiento de un GIF en esas exportaciones. No debe suponerse que una exportación estática contenga la animación.

## Revisión y pruebas

`revision/REVISION_REPOSITORIO.md` identifica las celdas de origen y distingue los hallazgos de los cambios añadidos. Los extractos de esas dos celdas están en la misma carpeta. `test_animaciones.py` comprueba la geometría, la separación de ramas, el radio y los márgenes:

```bash
python test_animaciones.py
```

En la entrega se ejecutaron nueve pruebas numéricas, además de la revisión de fotogramas y de las exportaciones. Los logs están en `revision/`.

## Documentación de las herramientas

- Matplotlib, escritores de animación: https://matplotlib.org/stable/api/animation_api.html
- Pillow, lectura y escritura de GIF: https://pillow.readthedocs.io/en/stable/handbook/image-file-formats.html#gif
- Mathcha, exportación e importación: https://cdn.mathcha.io/documentation/export-import/
