#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Animación de la porción Gamma ∩ B(t, epsilon) en una estrella sólo de arcos.
Base: yuri_karlovich_experiments.ipynb, celda 22 del ZIP entregado.
Script autónomo: numpy, matplotlib y Pillow; no requiere Manim.
"""

from __future__ import annotations

import argparse
from contextlib import ExitStack
from dataclasses import dataclass
from io import BytesIO
from pathlib import Path
from typing import Callable
import json

import numpy as np
import matplotlib
matplotlib.use("Agg")  # Exporta sin abrir ventanas; funciona en Colab y sin escritorio.
import matplotlib.pyplot as plt
from matplotlib.animation import AbstractMovieWriter, FFMpegWriter, writers
from PIL import Image

# ---------------- GEOMETRÍA: SOLAMENTE ARCOS ----------------
C_VALORES = [-1.2, -1.0, -0.6, 0.5, 0.9]  # Mismos c_k que en la celda 22.
X_MIN = 1e-3
X_MAX = 1e3
MUESTRAS_POR_RAMA = 3000
RAMAS_RECORRIDO = None         # None: todas; [0]: primera; [0, 3]: primera y cuarta.
DURACION = 20.0                # Segundos para TODO el recorrido.
MULTICOLOR = False
TAMANO_LIMPIO = (3.6, 6.6)     # Recorte vertical, sin el espacio que ocupaban los rayos.
NOMBRE = "arcos_sin_rayos"
TITULO = "Estrella de arcos: disco móvil"
FORMULA = r"$\Gamma_k=\{(x-i c_k)^{-1}:x>0\}$"

# ---------------- ANIMACIÓN Y EXPORTACIÓN ----------------
FPS = 25
DPI = 130
EPS_BASE = 0.25
EPS_AMP = 0.60                 # 0 <= EPS_AMP < 1; usa 0 para un radio constante.
EPS_FREQ = 1.0
ESTELA = 0.0                  # Fracción de la rama actual; 0 desactiva la estela.
MODO = "ambos"               # "anotado", "limpio" o "ambos".
EXPORTAR_MP4 = False          # Necesita el ejecutable FFmpeg, no una librería Python.
CARPETA_SALIDA = Path("outputs")

@dataclass
class Rama:
    """Una rama, sus muestras y su parametrización exacta de movimiento."""
    nombre: str
    muestras: np.ndarray
    punto: Callable[[float], complex]


def unir_con_cortes(segmentos: list[np.ndarray]) -> np.ndarray:
    """Los NaN impiden dibujar segmentos entre ramas distintas."""
    partes = []
    for z in segmentos:
        partes.extend((np.asarray(z, dtype=complex), np.array([complex(np.nan, np.nan)])))
    return np.concatenate(partes) if partes else np.array([complex(np.nan, np.nan)])


def dentro_del_disco(z: np.ndarray, t: complex, epsilon: float) -> np.ndarray:
    """Resalta TODAS las ramas; mantiene NaN fuera del disco y entre componentes.

    Es una aproximación por muestreo de Gamma intersección B(t, epsilon).
    No se conectan partes separadas, ni siquiera dentro de una misma rama.
    """
    resultado = z.copy()
    resultado[~(np.abs(z - t) < epsilon)] = complex(np.nan, np.nan)
    return resultado


def radio(s: float) -> float:
    """s es el tiempo normalizado, NO el parámetro geométrico x o r."""
    return float(EPS_BASE * (1 + EPS_AMP * np.sin(2 * np.pi * EPS_FREQ * s)))


def estado(k: int, cuadros: int, recorrido: list[int]) -> tuple[int, float, float]:
    """Rama, posición local y opacidad; no interpola entre ramas distintas.

    El marcador termina una rama, se desvanece y reaparece en la siguiente.
    El sentido del recorrido sirve para explorar la curva; no fija por sí solo
    la orientación de un operador integral.
    """
    posicion = len(recorrido) * k / cuadros
    tramo = min(int(posicion), len(recorrido) - 1)
    local = posicion - tramo
    q = float(np.clip((local - 0.06) / 0.82, 0, 1))
    u = q * q * (3 - 2 * q)  # Suaviza inicio y final de cada recorrido.
    entrada = 1.0 if tramo == 0 else float(np.clip(local / 0.06, 0, 1))
    salida = float(np.clip((0.97 - local) / 0.09, 0, 1))
    return recorrido[tramo], u, min(entrada, salida)


class EscritorGIF(AbstractMovieWriter):
    """Guarda cada cuadro indexado para reducir memoria, sin depender de FFmpeg.

    Usa la interfaz pública de escritores de Matplotlib y la codificación GIF
    de Pillow. La paleta se obtiene del primer render; no define colores de dibujo.
    """
    def setup(self, fig, outfile, dpi=None):
        super().setup(fig, outfile, dpi)
        self.imagenes = []
        self.paleta = None
        self.fondo_rgb = None

    def grab_frame(self, **savefig_kwargs):
        with BytesIO() as buffer:
            self.fig.savefig(buffer, format="rgba", dpi=self.dpi, **savefig_kwargs)
            imagen = Image.frombuffer("RGBA", self.frame_size, buffer.getvalue(), "raw", "RGBA", 0, 1)
            rgb = imagen.convert("RGB")
            if self.paleta is None:
                self.fondo_rgb = rgb.getpixel((0, 0))
                # Paleta fija obtenida del primer cuadro: evita parpadeos y
                # permite guardar sólo los rectángulos que cambian entre cuadros.
                self.paleta = rgb.quantize(colors=256, method=Image.Quantize.MEDIANCUT)
            self.imagenes.append(rgb.quantize(palette=self.paleta, dither=Image.Dither.NONE))

    def finish(self):
        if not self.imagenes:
            raise RuntimeError("No se generaron cuadros para el GIF.")
        # Restituye el fondo exacto del render tras la cuantización.
        indice = self.imagenes[0].getpixel((0, 0))
        for cuadro in self.imagenes:
            paleta = cuadro.getpalette()
            paleta[3*indice:3*indice+3] = list(self.fondo_rgb)
            cuadro.putpalette(paleta)
        # GIF mide el tiempo en centésimas: esta lista evita deriva a otros FPS.
        bordes = np.rint(np.arange(len(self.imagenes) + 1) * 100 / self.fps).astype(int)
        duraciones = (10 * np.diff(bordes)).tolist()
        self.imagenes[0].save(
            self.outfile, format="GIF", save_all=True,
            append_images=self.imagenes[1:], duration=duraciones,
            loop=0, disposal=1, optimize=True)
        self.imagenes.clear()


def validar(ramas: list[Rama], recorrido: list[int], duracion: float, fps: int, dpi: int) -> None:
    if not ramas or not recorrido:
        raise ValueError("Debe haber al menos una rama y una rama en el recorrido.")
    if any(not isinstance(j, (int, np.integer)) or not 0 <= j < len(ramas) for j in recorrido):
        raise ValueError("RAMAS_RECORRIDO contiene un índice inválido (se cuenta desde 0).")
    if not np.isfinite(duracion) or duracion <= 0 or not 1 <= fps <= 50 or dpi < 50:
        raise ValueError("Duración positiva, 1 <= FPS <= 50 y DPI >= 50 requeridos.")
    if not np.isfinite(EPS_BASE) or EPS_BASE <= 0 or not 0 <= EPS_AMP < 1:
        raise ValueError("EPS_BASE debe ser positivo y 0 <= EPS_AMP < 1.")
    if not np.isfinite(EPS_FREQ) or EPS_FREQ < 0 or not 0 <= ESTELA <= 1:
        raise ValueError("EPS_FREQ debe ser no negativo y 0 <= ESTELA <= 1.")
    if any(len(b.muestras) < 2 or not np.isfinite(b.muestras).all() for b in ramas):
        raise ValueError("Las muestras de cada rama deben ser finitas y no vacías.")
    if round(duracion * fps) < 12 * len(recorrido):
        raise ValueError("Usa al menos 12 cuadros por rama: aumenta duración/FPS o reduce el recorrido.")


def preparar_figura(ramas: list[Rama], limpio: bool, cuadros: int, recorrido: list[int]):
    # Sólo se utiliza el ciclo de colores predeterminado de Matplotlib.
    fig, ax = plt.subplots(figsize=TAMANO_LIMPIO if limpio else (6.6, 6.6), dpi=DPI)
    z = unir_con_cortes([b.muestras for b in ramas])
    base, = ax.plot([], [], lw=1.5, alpha=0.85, label=r"$\Gamma$")
    resaltado, = ax.plot([], [], lw=2.8, solid_capstyle="round", zorder=4,
                         label=r"$\Gamma\cap B(t,\varepsilon)$")
    borde, = ax.plot([], [], "--", lw=1.6, zorder=5, label=r"$\partial B(t,\varepsilon)$")
    punto, = ax.plot([], [], marker="o", ls="", ms=6.3, zorder=7, label=r"$t$")
    estela, = ax.plot([], [], lw=2.0, alpha=0.45, zorder=3)
    etiqueta = ax.annotate(r"$t$", (0, 0), xytext=(7, 7),
                          textcoords="offset points", fontsize=12, zorder=8)
    if MULTICOLOR:
        ax.set_prop_cycle(None)  # Restaura el ciclo por defecto, no una paleta manual.
        for b in ramas:
            ax.plot(b.muestras.real, b.muestras.imag, lw=1.45, alpha=0.95, zorder=2)
    else:
        base.set_data(z.real, z.imag)

    zfin = z[np.isfinite(z)]
    epsilon_max = EPS_BASE * (1 + EPS_AMP)
    margen = epsilon_max + 0.045 * max(np.ptp(zfin.real), np.ptp(zfin.imag))
    ax.set_xlim(zfin.real.min() - margen, zfin.real.max() + margen)
    ax.set_ylim(zfin.imag.min() - margen, zfin.imag.max() + margen)
    ax.set_aspect("equal", adjustable="box")
    if limpio:
        ax.set_axis_off()
        fig.subplots_adjust(left=0.025, right=0.975, bottom=0.025, top=0.975)
        estado_texto = None
    else:
        fig.subplots_adjust(left=0.13, right=0.97, bottom=0.13, top=0.78)
        ax.grid(True, alpha=0.22, linewidth=0.6)
        ax.set_xlabel("Re(z)", fontsize=10)
        ax.set_ylabel("Im(z)", fontsize=10)
        ax.tick_params(labelsize=9)
        fig.suptitle(TITULO, y=0.963, fontsize=15)
        fig.text(0.5, 0.91, FORMULA, ha="center", fontsize=11)
        fig.legend(handles=[base, resaltado, borde, punto], ncol=2, frameon=False,
                   loc="upper center", bbox_to_anchor=(0.5, 0.875), fontsize=10)
        estado_texto = fig.text(0.5, 0.037, "", ha="center", fontsize=10)
    fase_circulo = np.exp(1j * np.linspace(0, 2 * np.pi, 361))

    def actualizar(k):
        j, u, alpha = estado(k, cuadros, recorrido)
        centro = ramas[j].punto(u)
        epsilon = radio(k / max(1, cuadros - 1))
        zh = dentro_del_disco(z, centro, epsilon)
        circ = centro + epsilon * fase_circulo
        resaltado.set_data(zh.real, zh.imag)
        borde.set_data(circ.real, circ.imag)
        punto.set_data([centro.real], [centro.imag])
        etiqueta.xy = (centro.real, centro.imag)
        for artista in (resaltado, borde, punto, etiqueta):
            artista.set_alpha(alpha)
        if ESTELA > 0:
            # Reinicio por rama: nunca se concatena la estela con otra rama.
            parametros = np.linspace(max(0, u - ESTELA), u, 100)
            trayectoria = np.array([ramas[j].punto(float(v)) for v in parametros])
            estela.set_data(trayectoria.real, trayectoria.imag)
            estela.set_alpha(0.45 * alpha)
        else:
            estela.set_data([], [])
        if estado_texto is not None:
            estado_texto.set_text(fr"$t\in\Gamma_{{{j+1}}}$     $\varepsilon={epsilon:.3f}$")
        return centro, epsilon

    # Ocultar sólo elementos móviles permite exportar también la geometría base.
    moviles = [resaltado, borde, punto, estela, etiqueta]
    return fig, ax, actualizar, moviles


def generar(modo=MODO, duracion=None, fps=FPS, dpi=DPI, salida=CARPETA_SALIDA,
            mp4=EXPORTAR_MP4, solo_imagenes=False):
    """Crea los GIF y PNG/SVG; puede llamarse directamente desde un notebook."""
    duracion = DURACION if duracion is None else duracion
    ramas = crear_ramas()
    recorrido = list(range(len(ramas))) if RAMAS_RECORRIDO is None else list(RAMAS_RECORRIDO)
    validar(ramas, recorrido, duracion, fps, dpi)
    if modo not in ("ambos", "anotado", "limpio"):
        raise ValueError("Modo válido: ambos, anotado o limpio.")
    salida = Path(salida)
    for sub in ("gifs", "images", "videos"):
        (salida / sub).mkdir(parents=True, exist_ok=True)
    cuadros = int(round(duracion * fps))
    modos = ["anotado", "limpio"] if modo == "ambos" else [modo]
    exportar_video = bool(mp4 and writers.is_available("ffmpeg"))
    if mp4 and not exportar_video:
        print("FFmpeg no está disponible. Se exportan GIF, PNG y SVG sin video.")
    resumen = []
    for version in modos:
        limpio = version == "limpio"
        nombre = NOMBRE + ("_limpio" if limpio else "")
        fig, ax, actualizar, moviles = preparar_figura(ramas, limpio, cuadros, recorrido)
        fig.set_dpi(dpi)
        # Fotograma de muestra cerca de la región de encuentro de las ramas.
        k_muestra = min(cuadros - 1, int(0.60 * cuadros / len(recorrido)))
        actualizar(k_muestra)
        fig.savefig(salida / "images" / (nombre + ".png"), dpi=2 * dpi,
                    transparent=limpio)
        fig.savefig(salida / "images" / (nombre + ".svg"), transparent=limpio)
        if limpio:
            for a in moviles:
                a.set_visible(False)
            fig.savefig(salida / "images" / (NOMBRE + "_geometria.svg"), transparent=True)
            fig.savefig(salida / "images" / (NOMBRE + "_geometria.png"), dpi=2 * dpi,
                        transparent=True)
            for a in moviles:
                a.set_visible(True)
        if not solo_imagenes:
            # Cada figura es independiente. Los cuadros GIF se guardan indexados.
            gif = EscritorGIF(fps=fps)
            with ExitStack() as pila:
                pila.enter_context(gif.saving(fig, str(salida / "gifs" / (nombre + ".gif")), dpi))
                video = None
                if exportar_video:
                    video = FFMpegWriter(fps=fps, codec="libx264", bitrate=2200,
                                         extra_args=["-pix_fmt", "yuv420p", "-vf", "pad=ceil(iw/2)*2:ceil(ih/2)*2"])
                    pila.enter_context(video.saving(fig, str(salida / "videos" / (nombre + ".mp4")), dpi))
                for k in range(cuadros):
                    actualizar(k)
                    gif.grab_frame()
                    if video is not None:
                        video.grab_frame()
                    if k % max(1, cuadros // 5) == 0:
                        print(f"{nombre}: {100*k/cuadros:.0f}%", flush=True)
            print(f"Generado: {salida / 'gifs' / (nombre + '.gif')}", flush=True)
        resumen.append({"archivo": nombre, "ramas_dibujadas": len(ramas),
                        "ramas_recorridas_indices_0": recorrido,
                        "cuadros_programados": cuadros, "fps": fps,
                        "duracion_segundos": cuadros / fps, "dpi": dpi,
                        "tamano_pixels": list(fig.canvas.get_width_height()),
                        "eps_base": EPS_BASE, "eps_amp": EPS_AMP,
                        "eps_freq": EPS_FREQ, "multicolor": MULTICOLOR,
                        "solo_imagenes": bool(solo_imagenes)})
        plt.close(fig)
    (salida / (NOMBRE + "_parametros.json")).write_text(
        json.dumps(resumen, indent=2, ensure_ascii=False), encoding="utf-8")
    return resumen


def crear_ramas() -> list[Rama]:
    """Misma geometría del repositorio, sin crear ningún rayo.

    Se reparametriza mediante theta = 2 arctan(x/|c|). Esto distribuye las
    muestras uniformemente en longitud de arco sin cambiar 1/(x-i*c).
    Se mantienen los cortes x_min=10^-3 y x_max=10^3 del código de origen.
    """
    cvals = np.asarray(C_VALORES, dtype=float)
    if cvals.ndim != 1 or not len(cvals) or not np.isfinite(cvals).all():
        raise ValueError("C_VALORES debe ser una lista no vacía de números reales finitos.")
    if np.any(cvals == 0) or len(np.unique(cvals)) != len(cvals):
        raise ValueError("Los c_k deben ser distintos y diferentes de cero.")
    if not np.isfinite([X_MIN, X_MAX]).all() or not 0 < X_MIN < X_MAX:
        raise ValueError("Se requiere 0 < X_MIN < X_MAX finitos.")
    if MUESTRAS_POR_RAMA < 200:
        raise ValueError("Usa al menos 200 muestras por rama.")
    ramas = []
    for j, ck in enumerate(cvals):
        theta0, theta1 = 2 * np.arctan(np.array([X_MIN, X_MAX]) / abs(ck))
        def evaluar(u, c=float(ck), a=float(theta0), b=float(theta1)):
            h = (a + (b - a) * np.asarray(u)) / 2
            # Equivale a 1/(x-i*c), con x=|c| tan(theta/2).
            return np.sin(h) * np.cos(h) / abs(c) + 1j * np.sign(c) * np.cos(h)**2 / abs(c)
        muestras = evaluar(np.linspace(0, 1, MUESTRAS_POR_RAMA))
        ramas.append(Rama(f"Gamma_{j+1}", muestras, lambda u, f=evaluar: complex(f(u))))
    return ramas

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--modo", choices=["ambos", "anotado", "limpio"], default=MODO)
    parser.add_argument("--duracion", type=float, default=DURACION)
    parser.add_argument("--fps", type=int, default=FPS)
    parser.add_argument("--dpi", type=int, default=DPI)
    parser.add_argument("--salida", type=Path, default=CARPETA_SALIDA)
    parser.add_argument("--mp4", action="store_true", default=EXPORTAR_MP4)
    parser.add_argument("--solo-imagenes", action="store_true")
    args = parser.parse_args()
    try:
        generar(modo=args.modo, duracion=args.duracion, fps=args.fps, dpi=args.dpi,
                salida=args.salida, mp4=args.mp4, solo_imagenes=args.solo_imagenes)
    except (ValueError, OSError, RuntimeError) as error:
        parser.exit(1, f"Error: {error}\n")


if __name__ == "__main__":
    main()
