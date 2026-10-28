"""Question-driven power-weight animation: what does δ do to x^δ?"""

from __future__ import annotations

from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt

from animation_export import export_animation
from visual_style import COLORS


plt.rcParams.update({"font.family": "STIXGeneral", "mathtext.fontset": "stix",
                     "font.size": 14, "pdf.fonttype": 42})


def weight_figure(delta: float | None, *, p: float = 2.0) -> plt.Figure:
    """Fixed logarithmic x-axis and fixed y-limits for every animation frame."""
    if p <= 1 or not (-1 / p < -0.45 and 0.45 < 1 - 1 / p):
        raise ValueError("This illustration requires p with (-0.45,0.45) inside the admissible δ range")
    if delta is not None and not (-1 / p < delta < 1 - 1 / p):
        raise ValueError("δ must satisfy -1/p < δ < 1-1/p")
    fig = plt.figure(figsize=(12.8, 7.2), facecolor="white")
    fig.text(0.055, 0.950, r"WHAT DOES $\delta$ DO TO $w_\delta(x)=x^\delta$?",
             color=COLORS["main"], fontsize=17, fontweight="bold", va="top")
    fig.text(0.945, 0.950, rf"$p={p:g}$; admissible $-1/p<\delta<1-1/p$",
             color=COLORS["muted"], fontsize=13, ha="right", va="top")
    ax = fig.add_axes([0.095, 0.18, 0.835, 0.66])
    x = np.geomspace(1e-2, 1e2, 600)
    ax.set_xscale("log")
    ax.set_xlim(1e-2, 1e2)
    ax.set_ylim(0, 8.4)
    ax.set_xlabel(r"$x>0$  (logarithmic scale)", fontsize=16)
    ax.set_ylabel(r"$w_\delta(x)$", fontsize=17, rotation=0, labelpad=36)
    ax.axvline(1, color=COLORS["rule"], lw=1.4)
    ax.axhline(1, color=COLORS["rule"], lw=1.4)
    ax.grid(which="major", color=COLORS["rule"], alpha=0.56, linewidth=0.8)
    ax.grid(which="minor", color=COLORS["rule"], alpha=0.20, linewidth=0.5)
    ax.spines[["top", "right"]].set_visible(False)
    if delta is None:
        for value, color in ((-0.4, COLORS["wiener"]),
                             (0.0, COLORS["muted"]),
                             (0.4, COLORS["geometry"])):
            ax.plot(x, x ** value, color=color, lw=3.3,
                    label=rf"$\delta={value:+.1f}$")
        ax.legend(loc="upper center", ncol=3, frameon=False, fontsize=15)
        fig.text(0.50, 0.075,
                 r"$\delta<0$: large near $0^+$     ·     $\delta=0$: constant     ·     $\delta>0$: large for $x\gg1$",
                 ha="center", color=COLORS["ink"], fontsize=15)
    else:
        color = COLORS["wiener"] if delta < -0.015 else (
            COLORS["geometry"] if delta > 0.015 else COLORS["muted"])
        ax.plot(x, x ** delta, color=color, lw=3.8)
        delta_label = "0" if delta == 0 else f"{delta:+.2f}"
        ax.text(0.52, 0.83, rf"$\delta={delta_label}$", transform=ax.transAxes,
                color=color, fontsize=26, fontweight="bold")
        fig.text(0.50, 0.075,
                 r"At $x=1$, every curve equals $1$.  The two sides move in opposite directions as $\delta$ changes.",
                 ha="center", color=COLORS["ink"], fontsize=14.5)
    return fig


def render_power_weights(output_dir: Path, *, p: float = 2.0, fps: int = 24,
                         duration: float = 6.0, speed_factor: float = 1.0,
                         delta_start: float = -0.45,
                         delta_end: float = 0.45) -> dict:
    if speed_factor <= 0:
        raise ValueError("SPEED_FACTOR must be positive")
    if not (-1 / p < delta_start <= -0.4 < 0.4 <= delta_end < 1 - 1 / p):
        raise ValueError("The chosen range must contain -0.4 and 0.4 and lie inside the admissible interval")
    frames = max(2, round(fps * duration / speed_factor))
    values = np.linspace(delta_start, delta_end, frames)
    values[np.argmin(np.abs(values))] = 0.0
    reviews = {f"weight_delta_{tag}": (lambda value=value: weight_figure(value, p=p))
               for tag, value in (("minus_04", -0.4), ("zero", 0.0), ("plus_04", 0.4))}
    return export_animation(
        lambda i, n: weight_figure(float(values[i]), p=p),
        lambda: weight_figure(None, p=p),
        output_dir, "power_weights_v1", frames=frames, fps=fps,
        review_drawers=reviews,
    )
