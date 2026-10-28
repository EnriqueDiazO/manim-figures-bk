"""Point correspondence and E_{p,wδ} under x=e^t."""

from __future__ import annotations

from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt

from animation_export import export_animation
from visual_style import COLORS


plt.rcParams.update({"font.family": "STIXGeneral", "mathtext.fontset": "stix",
                     "font.size": 14, "pdf.fonttype": 42})


def log_transport_figure(progress: float, *, p: float = 2.0,
                         delta: float = 0.0) -> plt.Figure:
    if not 0 <= progress <= 1 or p <= 1 or not (-1 / p < delta < 1 - 1 / p):
        raise ValueError("Require 0<=progress<=1, p>1 and admissible δ")
    nu = 1 / p + delta
    t_values = np.linspace(-3.4, 3.4, 500)
    x_values = np.exp(t_values)
    f_values = np.exp(-x_values)
    transformed = np.exp(nu * t_values - np.exp(t_values))
    point_t = -3.2 + 6.4 * min(progress / 0.50, 1.0) if progress <= 0.50 else 0.0
    point_x = np.exp(point_t)
    reveal = 0.0 if progress <= 0.50 else min(1.0, (progress - 0.50) / 0.50)

    fig = plt.figure(figsize=(12.8, 7.2), facecolor="white")
    fig.text(0.055, 0.954, "WHY DOES MELLIN APPEAR?",
             color=COLORS["main"], fontsize=17, fontweight="bold", va="top")
    fig.text(0.945, 0.954, r"$x=e^t,\quad t=\log x$",
             color=COLORS["transport"], fontsize=20, ha="right", va="top")
    fig.text(0.50, 0.865,
             rf"one point: $x={point_x:.2f}\ \longleftrightarrow\ t={point_t:+.2f}$",
             ha="center", fontsize=16, color=COLORS["ink"])

    left = fig.add_axes([0.075, 0.57, 0.345, 0.21])
    right = fig.add_axes([0.58, 0.57, 0.345, 0.21])
    for ax in (left, right):
        ax.set_ylim(-0.26, 0.26)
        ax.set_yticks([])
        ax.spines[["top", "right", "left"]].set_visible(False)
        ax.spines["bottom"].set_color(COLORS["rule"])
        ax.axhline(0, color=COLORS["rule"], lw=1.2)
    left.set_xscale("log")
    left.set_xlim(np.exp(-3.4), np.exp(3.4))
    left.set_xticks([np.exp(-3), 1, np.exp(3)])
    left.set_xticklabels([r"$e^{-3}$", "$1$", r"$e^3$"])
    left.set_xlabel(r"positive half-line $x$", fontsize=14)
    right.set_xlim(-3.4, 3.4)
    right.set_xticks([-3, 0, 3])
    right.set_xlabel(r"real line $t$", fontsize=14)
    left.scatter([point_x], [0], color=COLORS["geometry"], s=140, zorder=5)
    right.scatter([point_t], [0], color=COLORS["mellin"], s=140, zorder=5)
    fig.text(0.50, 0.675, r"$\leftrightarrow$", fontsize=30,
             ha="center", va="center", color=COLORS["transport"])

    if reveal > 0:
        ax_f = fig.add_axes([0.075, 0.185, 0.345, 0.255])
        ax_e = fig.add_axes([0.58, 0.185, 0.345, 0.255])
        n = max(2, int(reveal * len(t_values)))
        ax_f.plot(x_values[:n], f_values[:n], color=COLORS["geometry"], lw=3)
        ax_e.plot(t_values[:n], transformed[:n], color=COLORS["mellin"], lw=3)
        ax_f.set_xscale("log")
        ax_f.set_xlim(np.exp(-3.4), np.exp(3.4))
        ax_f.set_ylim(0, 1.08)
        ax_e.set_xlim(-3.4, 3.4)
        ax_e.set_ylim(0, max(0.6, 1.08 * float(transformed.max())))
        ax_f.set_title(r"$f(x)=e^{-x}$", fontsize=17, color=COLORS["geometry"])
        ax_e.set_title(rf"$(E_{{p,w_\delta}}f)(t)=e^{{\nu t-e^t}},\quad\nu={nu:.2f}$",
                       fontsize=17, color=COLORS["mellin"])
        ax_f.set_xlabel("x (log scale)", fontsize=13)
        ax_e.set_xlabel("t", fontsize=13)
        for ax in (ax_f, ax_e):
            ax.grid(color=COLORS["rule"], alpha=0.40, linewidth=0.7)
            ax.spines[["top", "right"]].set_visible(False)
        fig.text(0.50, 0.318, r"$E_{p,w_\delta}$", fontsize=19,
                 color=COLORS["transport"], ha="center")
    else:
        fig.text(0.50, 0.338, "First follow corresponding points; the functions appear next.",
                 ha="center", fontsize=15, color=COLORS["muted"])

    fig.text(0.50, 0.065,
             r"$x\to0^+\Rightarrow t\to-\infty$     ·     $x=1\Leftrightarrow t=0$     ·     $x\to+\infty\Rightarrow t\to+\infty$",
             ha="center", fontsize=15, color=COLORS["ink"])
    return fig


def render_log_transport(output_dir: Path, *, p: float = 2.0, delta: float = 0.0,
                         fps: int = 24, duration: float = 7.0,
                         speed_factor: float = 1.0) -> dict:
    if speed_factor <= 0:
        raise ValueError("SPEED_FACTOR must be positive")
    frames = max(2, round(fps * duration / speed_factor))
    return export_animation(
        lambda i, n: log_transport_figure(i / (n - 1), p=p, delta=delta),
        lambda: log_transport_figure(1.0, p=p, delta=delta),
        output_dir, "log_transport_v1", frames=frames, fps=fps,
        review_drawers={
            "log_point_only": lambda: log_transport_figure(0.05, p=p, delta=delta),
            "log_at_one": lambda: log_transport_figure(0.50, p=p, delta=delta),
            "log_transformed": lambda: log_transport_figure(1.0, p=p, delta=delta),
        },
    )
