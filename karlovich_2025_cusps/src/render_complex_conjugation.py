"""A short geometric proof that complex conjugation is only real-linear."""

from __future__ import annotations

from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt

from animation_export import export_animation
from visual_style import COLORS


plt.rcParams.update({"font.family": "STIXGeneral", "mathtext.fontset": "stix",
                     "font.size": 14, "pdf.fonttype": 42})


def conjugation_figure(progress: float) -> plt.Figure:
    if not 0 <= progress <= 1:
        raise ValueError("progress must be in [0,1]")
    t = np.linspace(0, 2 * np.pi, 500)
    u = 1.0 + 0.48 * np.cos(t)
    v = 0.55 + 0.30 * np.sin(t)
    reflected_fraction = min(1.0, progress / 0.56)
    current_v = (1 - 2 * reflected_fraction) * v
    relation_visible = progress >= 0.59
    verdict_visible = progress >= 0.78

    fig = plt.figure(figsize=(12.8, 7.2), facecolor="white")
    fig.text(0.055, 0.950, "WHY IS COMPLEX CONJUGATION ONLY REAL-LINEAR?",
             color=COLORS["main"], fontsize=17, fontweight="bold", va="top")
    fig.text(0.945, 0.950, r"$C f=\overline{f}$",
             color=COLORS["symbol"], fontsize=22, ha="right", va="top")
    left = fig.add_axes([0.07, 0.23, 0.43, 0.59])
    right = fig.add_axes([0.57, 0.23, 0.36, 0.59])
    left.plot(u, v, color=COLORS["geometry"], lw=2.0, ls="--", alpha=0.70,
              label=r"original $f(t)$")
    left.plot(u, current_v, color=COLORS["symbol"], lw=3.5,
              label=r"moving image under $C$")
    left.axhline(0, color=COLORS["rule"], lw=1.3)
    left.axvline(0, color=COLORS["rule"], lw=1.0)
    left.set_xlim(0.25, 1.75)
    left.set_ylim(-1.05, 1.05)
    left.set_aspect("equal", adjustable="box")
    left.set_xlabel(r"$\operatorname{Re}z$", fontsize=16)
    left.set_ylabel(r"$\operatorname{Im}z$", fontsize=16)
    left.set_title(r"curve in the complex plane", color=COLORS["symbol"], fontsize=17)
    left.legend(loc="center left", frameon=False, fontsize=11)
    left.spines[["top", "right"]].set_visible(False)

    right.plot(t, u, color=COLORS["geometry"], lw=2.7,
               label=r"real part $u(t)$")
    right.plot(t, current_v, color=COLORS["symbol"], lw=3,
               label=r"imaginary part $(1-2a)v(t)$")
    right.axhline(0, color=COLORS["rule"], lw=1.3)
    right.set_xlim(0, 2 * np.pi)
    right.set_ylim(-1.10, 1.60)
    right.set_xticks([0, np.pi, 2 * np.pi])
    right.set_xticklabels(["0", r"$\pi$", r"$2\pi$"])
    right.set_xlabel("parameter t", fontsize=16)
    right.set_title(r"$f(t)=u(t)+i v(t)$", color=COLORS["geometry"], fontsize=17)
    right.legend(loc="center right", frameon=False, fontsize=11)
    right.grid(color=COLORS["rule"], alpha=0.37, linewidth=0.7)
    right.spines[["top", "right"]].set_visible(False)

    if relation_visible:
        fig.text(0.50, 0.130,
                 r"$C(\lambda f)=\overline{\lambda}\,Cf$",
                 ha="center", va="center", fontsize=23,
                 color=COLORS["symbol"])
    else:
        fig.text(0.50, 0.130,
                 r"$u(t)+iv(t)\longrightarrow u(t)-iv(t)$",
                 ha="center", va="center", fontsize=23,
                 color=COLORS["symbol"])
    if verdict_visible:
        fig.text(0.34, 0.052, "R-linear  ✓", ha="center", va="center",
                 fontsize=18, fontfamily="DejaVu Sans", color=COLORS["proved"])
        fig.text(0.67, 0.052, "C-linear  ✗", ha="center", va="center",
                 fontsize=18, fontfamily="DejaVu Sans", color=COLORS["warning"])
    else:
        fig.text(0.50, 0.052, "C denotes complex conjugation here.",
                 ha="center", va="center", fontsize=13,
                 color=COLORS["muted"])
    return fig


def render_complex_conjugation(output_dir: Path, *, fps: int = 24,
                               duration: float = 6.0,
                               speed_factor: float = 1.0) -> dict:
    if speed_factor <= 0:
        raise ValueError("SPEED_FACTOR must be positive")
    frames = max(2, round(fps * duration / speed_factor))
    return export_animation(
        lambda i, n: conjugation_figure(i / (n - 1)),
        lambda: conjugation_figure(1.0),
        output_dir, "complex_conjugation_v1", frames=frames, fps=fps,
        review_drawers={
            "conjugation_original": lambda: conjugation_figure(0.0),
            "conjugation_reflected": lambda: conjugation_figure(0.56),
            "conjugation_verdict": lambda: conjugation_figure(1.0),
        },
    )
