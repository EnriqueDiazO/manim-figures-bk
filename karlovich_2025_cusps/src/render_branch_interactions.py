"""First functional Matplotlib animation of Karlovich 2025 branch interactions.

The geometry, classification and formula strings come from the shared modules.
This renderer exports GIF, MP4, PNG and vector PDF with a fixed visual frame.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
import shutil
import subprocess
import tempfile

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Rectangle
import numpy as np
from PIL import Image

from geometry import BranchParameters, branch_points
from interactions import cells, count_by_class, index_caption
from operator_metadata import INTERACTIONS
from visual_style import COLORS, TYPE_COLORS


plt.rcParams.update({
    "font.family": "STIXGeneral",
    "mathtext.fontset": "stix",
    "font.size": 13,
    "text.color": COLORS["ink"],
    "pdf.fonttype": 42,
    "pdf.compression": 9,
})

PDF_META = {
    "Title": "Karlovich 2025 branch interactions",
    "Author": "Enrique Diaz Ocampo",
    "Creator": "render_branch_interactions.py",
    "CreationDate": datetime(2000, 1, 1, tzinfo=timezone.utc),
    "ModDate": datetime(2000, 1, 1, tzinfo=timezone.utc),
}

STAGE_TITLES = {
    1: "1  GEOMETRY",
    2: "2  ISOMETRIC TRANSPORT",
    3: "3  VECTOR REPRESENTATION",
    4: "4  EXACT OPERATOR MATRIX",
    5: "5  BLOCK CLASSES",
    6: "6  CUSP → CUSP  (CC)",
    7: "7  RAY → CUSP  (CR)",
    8: "8  CUSP → RAY  (RC)",
    9: "9  RAY → RAY  (RR)",
    10: "10  SUMMARY",
}


@dataclass(frozen=True)
class AnimationTiming:
    fps: int
    hold_start: float
    draw_geometry: float
    hold_geometry: float
    transport: float
    vector: float
    matrix_duration: float
    block_highlight_duration: float
    formula_hold_duration: float
    hold_end: float

    def __post_init__(self) -> None:
        if self.fps < 1 or any(v <= 0 for v in (
            self.hold_start, self.draw_geometry, self.hold_geometry,
            self.transport, self.vector, self.matrix_duration,
            self.block_highlight_duration, self.formula_hold_duration,
            self.hold_end,
        )):
            raise ValueError("FPS and all stage durations must be positive.")

    def schedule(self) -> tuple[tuple[int, float, float, float], ...]:
        """Stage, seconds, initial progress, final progress. Holds are explicit."""
        return (
            (1, self.hold_start, 0.05, 0.05),
            (1, self.draw_geometry, 0.05, 1.0),
            (1, self.hold_geometry, 1.0, 1.0),
            (2, self.transport, 0.0, 1.0),
            (3, self.vector, 1.0, 1.0),
            (4, self.matrix_duration, 0.0, 1.0),
            (5, self.block_highlight_duration, 1.0, 1.0),
            # Each class has a distinct exact, model, and class-reading pause.
            *tuple(item for stage in (6, 7, 8, 9) for item in (
                (stage, 0.20 * self.formula_hold_duration, 0.0, 0.40),
                (stage, 0.22 * self.formula_hold_duration, 0.43, 0.69),
                (stage, 0.58 * self.formula_hold_duration, 1.0, 1.0),
            )),
            (10, self.hold_end, 1.0, 1.0),
        )

    @property
    def duration(self) -> float:
        return sum(seconds for _, seconds, _, _ in self.schedule())


def _card(fig: plt.Figure, bounds: tuple[float, float, float, float],
          title: str, color: str, active: bool) -> plt.Axes:
    x, y, w, h = bounds
    edge = color if active else COLORS["rule"]
    fig.add_artist(FancyBboxPatch(
        (x, y), w, h, boxstyle="round,pad=0.007,rounding_size=0.011",
        transform=fig.transFigure, edgecolor=edge,
        facecolor="white", linewidth=1.0, zorder=0,
    ))
    fig.text(x + 0.015, y + h - 0.036, title, fontsize=11.6,
             color=edge if active else COLORS["muted"],
             va="center", fontweight="bold")
    return fig.add_axes([x + 0.013, y + 0.018, w - 0.026, h - 0.072])


def _geometry(ax: plt.Axes, params: BranchParameters, stage: int, progress: float) -> None:
    ax.set_xlim(-2.05, 1.13)
    ax.set_ylim(-1.92, 1.92)
    ax.set_aspect("equal", adjustable="box")
    ax.axis("off")
    ax.axhline(0, color=COLORS["rule"], linewidth=0.75)
    ax.axvline(0, color=COLORS["rule"], linewidth=0.75)
    ax.scatter([0], [0], color=COLORS["ink"], s=18, zorder=10)
    ax.text(0.04, -0.08, "$0$", fontsize=10, color=COLORS["ink"])
    reveal = params.m * progress if stage == 1 else float(params.m)
    for k in range(1, params.m + 1):
        fraction = np.clip(reveal - (k - 1), 0, 1)
        if fraction <= 0:
            continue
        z = branch_points(params, k)
        number = max(2, int(len(z) * fraction))
        color = COLORS["geometry"] if k <= params.s else COLORS["wiener"]
        ax.plot(z[:number].real, z[:number].imag, color=color, lw=2.2,
                solid_capstyle="round")
        if fraction > 0.75:
            # x increases along each parametrization; arrows therefore point
            # toward the common point 0.  Sampling indices depend only on the
            # branch type, never on hand-placed curve coordinates.
            a, b = ((5, 18) if k <= params.s else
                    (int(0.25 * len(z)), int(0.50 * len(z))))
            ax.annotate("", xy=(z[b].real, z[b].imag),
                        xytext=(z[a].real, z[a].imag),
                        arrowprops={"arrowstyle": "-|>", "lw": 1.4,
                                    "color": color, "mutation_scale": 12},
                        zorder=8)
            start = z[0]
            dx = 0.04 if k <= params.s else -0.08
            ax.text(start.real + dx, start.imag + 0.06 * np.sign(start.imag),
                    rf"$\Gamma_{{{k}}}$", fontsize=10.5, color=color,
                    ha="left" if k <= params.s else "right")


def _half_lines(ax: plt.Axes, params: BranchParameters,
                stage: int, progress: float) -> None:
    ax.set_xlim(0, 1)
    ax.set_ylim(0, params.m + 0.8)
    ax.axis("off")
    reveal = params.m * progress if stage == 2 else float(params.m)
    for k in range(1, params.m + 1):
        fraction = np.clip(reveal - (k - 1), 0, 1)
        if fraction <= 0:
            continue
        y = params.m - k + 0.64
        color = COLORS["geometry"] if k <= params.s else COLORS["wiener"]
        ax.plot([0.49, 0.49 + 0.37 * fraction], [y, y], color=color, lw=2.1)
        if fraction > 0.75:
            ax.annotate("", xy=(0.89, y), xytext=(0.77, y),
                        arrowprops={"arrowstyle": "-|>", "lw": 1.2,
                                    "color": color, "mutation_scale": 9})
            ax.text(0.02, y, rf"$\Gamma_{k}\to\varphi_{k}$", ha="left", va="center",
                    fontsize=10.4, color=color)
    ax.text(0.50, 0.10, r"schematic isometry; $m$ copies of $\mathbb{R}_+$", ha="center", fontsize=9.6,
            color=COLORS["muted"])


def _matrix(ax: plt.Axes, params: BranchParameters, stage: int,
            progress: float) -> None:
    m = params.m
    ax.set_xlim(-0.75, m + 0.10)
    ax.set_ylim(-0.30, m + 0.76)
    ax.set_aspect("equal", adjustable="box")
    ax.axis("off")
    ax.text(m / 2, m + 0.58, "INPUT  $j$  →", fontsize=10.3,
            color=COLORS["muted"], ha="center")
    ax.text(-0.68, m / 2, "OUTPUT  $k$  ↓", fontsize=10.3,
            color=COLORS["muted"], ha="center", rotation=90)
    if stage >= 5:
        ax.text(m / 2, -0.23, "C = cusp     R = ray", fontsize=9.2,
                color=COLORS["muted"], ha="center")
    for j in range(1, m + 1):
        ax.text(j - 0.5, m + 0.15, rf"$j={j}$", ha="center", fontsize=9.5,
                color=COLORS["geometry"] if j <= params.s else COLORS["wiener"])
    for k in range(1, m + 1):
        ax.text(-0.12, m - k + 0.50, rf"$k={k}$", va="center", ha="right",
                fontsize=9.5,
                color=COLORS["geometry"] if k <= params.s else COLORS["wiener"])
    limit = int(np.ceil(params.m * params.m * progress)) if stage == 4 else m * m
    focus = {6: "CC", 7: "CR", 8: "RC", 9: "RR"}.get(stage)
    for n, cell in enumerate(cells(params)):
        if n >= limit:
            break
        x, y = cell.j - 1 + 0.03, m - cell.k + 0.03
        class_color = TYPE_COLORS[cell.kind]
        highlighted = focus is None or cell.kind == focus
        fill = class_color if stage >= 5 and highlighted else COLORS["soft"]
        alpha = 0.13 if stage >= 5 and highlighted else 0.65
        ax.add_patch(Rectangle((x, y), 0.94, 0.94, facecolor=fill,
                               edgecolor=class_color if stage >= 5 and highlighted else COLORS["rule"],
                               linewidth=1.05, alpha=alpha if highlighted else 0.30))
        label = cell.kind if stage >= 5 else rf"$T_{{{cell.k},{cell.j}}}$"
        ax.text(cell.j - 0.5, m - cell.k + 0.5, label, ha="center", va="center",
                fontsize=11 if m <= 5 else 8.5,
                color=class_color if stage >= 5 and highlighted else COLORS["ink"],
                fontweight="bold" if stage >= 5 else "normal",
                alpha=1 if highlighted else 0.30)


def _math_text(ax: plt.Axes, x: float, y: float, text: str,
               size: float = 16, color: str | None = None, **kwargs: object) -> None:
    ax.text(x, y, text, transform=ax.transAxes, fontsize=size,
            color=color or COLORS["ink"], va="center", **kwargs)


def _details(ax: plt.Axes, params: BranchParameters,
             stage: int, progress: float,
             show_exact_kernel: bool, show_compact_model: bool,
             show_operator_class: bool) -> None:
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    if stage == 1:
        _math_text(ax, 0.03, 0.77, "EXACT GEOMETRY", 11.5, COLORS["geometry"], fontweight="bold")
        _math_text(ax, 0.03, 0.47,
                   r"$\gamma_k(x)=(x-ic_k)^{-1}\quad(1\leq k\leq s)$", 17)
        _math_text(ax, 0.53, 0.47,
                   r"$\gamma_k(x)=e^{i\beta_k}/x\quad(s<k\leq m)$", 17)
        _math_text(ax, 0.03, 0.16,
                   r"All branches approach the common point $0$ as $x\to+\infty$.",
                   12.5, COLORS["muted"])
    elif stage == 2:
        _math_text(ax, 0.03, 0.76, "SCHEMATIC REPRESENTATION OF ISOMETRIC TRANSPORT", 11.5,
                   COLORS["transport"], fontweight="bold")
        _math_text(ax, 0.03, 0.46,
                   r"$\sigma:L^p(\Gamma,\widetilde w)\longrightarrow [L^p(\mathbb{R}_+,w_\delta)]^m$", 19)
        _math_text(ax, 0.03, 0.15,
                   "The arrow denotes a function-space isomorphism, not a literal deformation of the curve.",
                   12.5, COLORS["muted"])
    elif stage == 3:
        _math_text(ax, 0.03, 0.73, "ONE VECTOR COMPONENT PER BRANCH", 11.5,
                   COLORS["transport"], fontweight="bold")
        _math_text(ax, 0.03, 0.39,
                   r"$\varphi=\{\varphi_k\}_{k=1}^m,\qquad "
                   r"\varphi_k=\Upsilon_k(f|_{\Gamma_k})$", 20)
    elif stage == 4:
        _math_text(ax, 0.03, 0.77, "EXACT TRANSPORTED OPERATOR", 11.5,
                   COLORS["geometry"], fontweight="bold")
        _math_text(ax, 0.03, 0.44,
                   r"$\sigma S_\Gamma\sigma^{-1}=[T_{k,j}]_{k,j=1}^{m}$",
                   20)
        _math_text(ax, 0.53, 0.44,
                   r"$T_{k,j}=\Upsilon_k S_{\Gamma_j}\Upsilon_j^{-1}$", 17)
        _math_text(ax, 0.03, 0.14,
                   "Column j: input branch. Row k: output component.", 12.5, COLORS["muted"])
    elif stage == 5:
        _math_text(ax, 0.03, 0.76, "INDEX-BASED CLASSES", 11.5,
                   COLORS["symbol"], fontweight="bold")
        counts = count_by_class(params)
        for n, code in enumerate(("CC", "CR", "RC", "RR")):
            _math_text(ax, 0.07 + 0.23 * n, 0.46,
                       rf"$\mathrm{{{code}}}: {counts[code]}$ cells", 16,
                       TYPE_COLORS[code])
        _math_text(ax, 0.03, 0.15,
                   "First letter = output k; second letter = input j.", 12.5, COLORS["muted"])
    elif stage in (6, 7, 8, 9):
        code = {6: "CC", 7: "CR", 8: "RC", 9: "RR"}[stage]
        spec = INTERACTIONS[code]
        j_range, k_range = index_caption(code, params)
        color = TYPE_COLORS[code]
        _math_text(ax, 0.03, 0.86,
                   f"{code}  ·  INPUT {j_range}  ·  OUTPUT {k_range}", 11.7,
                   color, fontweight="bold")
        if show_exact_kernel:
            _math_text(ax, 0.50, 0.86,
                       rf"$T_{{k,j}}\varphi_j(x)=\frac{{1}}{{\pi i}}\int_0^\infty "
                       rf"K^{{\mathrm{{ex}}}}_{{k,j}}(x,\tau)\varphi_j(\tau)\,d\tau$",
                       13.0)
            _math_text(ax, 0.03, 0.61,
                       rf"$K^{{\mathrm{{ex}}}}_{{k,j}}={spec.exact_kernel}$",
                       20.0, color)
        if show_compact_model and progress >= 0.42:
            if code == "RR":
                _math_text(ax, 0.62, 0.61,
                           "MODEL = EXACT  ·  NO LOCAL CORRECTION", 11.7,
                           COLORS["proved"], fontweight="bold")
            else:
                _math_text(ax, 0.67, 0.61,
                           r"$T_{k,j}-S_{k,j}\in\mathcal{K}(X)$", 14.5,
                           COLORS["warning"])
            _math_text(ax, 0.03, 0.32,
                       rf"$K^{{\mathrm{{mod}}}}_{{k,j}}={spec.model_kernel}$",
                       17.0 if code == "CC" else 19.0, COLORS["proved"])
        if show_operator_class and progress >= 0.70:
            _math_text(ax, 0.03, 0.10,
                       f"MODEL CLASS: {spec.class_name}", 12.5,
                       COLORS["symbol"], fontweight="bold")
        if code in ("CC", "RR"):
            _math_text(ax, 0.79, 0.10, "PV when k = j", 11.5, COLORS["muted"])
    else:
        _math_text(ax, 0.03, 0.81, "THREE DISTINCT LAYERS", 11.5,
                   COLORS["symbol"], fontweight="bold")
        _math_text(ax, 0.03, 0.53,
                   r"$\Gamma_k\ \longrightarrow\ T_{k,j}\ \simeq\ S_{k,j}$",
                   20)
        _math_text(ax, 0.48, 0.53,
                   r"$\longrightarrow\ [S_\Gamma](\omega)\in\mathbb{C}^{m\times m}$", 18,
                   COLORS["symbol"])
        _math_text(ax, 0.03, 0.15,
                   r"$A\simeq B\Longleftrightarrow A-B$ is compact.  "
                   r"For $N=A+BC$, double first; then $\mathcal{Y}_N(\omega)$ is $2m\times2m$ on $\widehat\Omega$.",
                   12.0, COLORS["muted"])


def render_frame(params: BranchParameters, stage: int,
                 progress: float = 1.0, *,
                 show_exact_kernel: bool = True,
                 show_compact_model: bool = True,
                 show_operator_class: bool = True) -> plt.Figure:
    if stage not in STAGE_TITLES or not 0 <= progress <= 1:
        raise ValueError("stage must be 1..10 and progress must be in [0,1].")
    fig = plt.figure(figsize=(12.8, 7.2), facecolor="white")
    fig.text(0.041, 0.964, "KARLOVICH 2025  /  BRANCH INTERACTIONS",
             fontsize=10.5, color=COLORS["main"], fontweight="bold", va="top")
    fig.text(0.041, 0.924, STAGE_TITLES[stage], fontsize=19.0,
             color=COLORS["main"], fontweight="bold", va="top")
    values = ", ".join(f"{v:g}" for v in params.c_values)
    betas = ", ".join(f"{np.degrees(v):.0f}°" for v in params.beta_values)
    fig.text(0.956, 0.961, f"s={params.s}   r={params.r}   m={params.m}",
             ha="right", va="top", fontsize=10.8, color=COLORS["main"])
    fig.text(0.956, 0.924, f"c=[{values}]   β=[{betas}]",
             ha="right", va="top", fontsize=9.7, color=COLORS["muted"])
    fig.add_artist(plt.Line2D([0.04, 0.96], [0.882, 0.882],
                              transform=fig.transFigure, color=COLORS["rule"], lw=0.9))
    geometry_ax = _card(fig, (0.041, 0.379, 0.303, 0.467), "CURVE  Γ",
                        COLORS["geometry"], True)
    half_ax = _card(fig, (0.365, 0.379, 0.224, 0.467), "TRANSPORT  σ",
                    COLORS["transport"], stage >= 2)
    matrix_ax = _card(fig, (0.610, 0.379, 0.348, 0.467), "OPERATOR MATRIX",
                      COLORS["symbol"], stage >= 4)
    bottom = _card(fig, (0.041, 0.044, 0.917, 0.302), "KERNELS AND REDUCTION",
                   COLORS["proved"], stage >= 6)
    _geometry(geometry_ax, params, stage, progress)
    if stage >= 2:
        _half_lines(half_ax, params, stage, progress)
        fig.add_artist(FancyArrowPatch((0.346, 0.605), (0.362, 0.605),
                                       transform=fig.transFigure, arrowstyle="-|>",
                                       mutation_scale=15, lw=1.5,
                                       color=COLORS["transport"]))
    else:
        half_ax.axis("off")
    if stage >= 4:
        _matrix(matrix_ax, params, stage, progress)
        fig.add_artist(FancyArrowPatch((0.590, 0.605), (0.607, 0.605),
                                       transform=fig.transFigure, arrowstyle="-|>",
                                       mutation_scale=15, lw=1.5,
                                       color=COLORS["symbol"]))
    else:
        matrix_ax.axis("off")
    _details(bottom, params, stage, progress,
             show_exact_kernel, show_compact_model, show_operator_class)
    return fig


def _stage_frame_count(seconds: float, fps: int) -> int:
    return max(2, int(round(seconds * fps)))


def render_static_compact(params: BranchParameters) -> plt.Figure:
    """Title-free vector fallback sized for inclusion below a Beamer frametitle."""
    fig = plt.figure(figsize=(12.8, 5.3), facecolor="white")
    fig.text(0.044, 0.949, "EXACT GEOMETRY  →  SCHEMATIC TRANSPORT  →  BLOCK CLASSES",
             fontsize=11.3, color=COLORS["main"], fontweight="bold", va="top")
    fig.add_artist(plt.Line2D([0.04, 0.96], [0.901, 0.901],
                              transform=fig.transFigure, color=COLORS["rule"], lw=0.9))
    ga = _card(fig, (0.041, 0.134, 0.303, 0.729), "CURVE  Γ", COLORS["geometry"], True)
    ha = _card(fig, (0.365, 0.134, 0.224, 0.729), "TRANSPORT  σ", COLORS["transport"], True)
    ma = _card(fig, (0.610, 0.134, 0.348, 0.729), "BLOCK MATRIX", COLORS["symbol"], True)
    _geometry(ga, params, 5, 1.0)
    _half_lines(ha, params, 5, 1.0)
    _matrix(ma, params, 5, 1.0)
    fig.add_artist(FancyArrowPatch((0.346, 0.52), (0.362, 0.52),
                                   transform=fig.transFigure, arrowstyle="-|>",
                                   mutation_scale=15, lw=1.5, color=COLORS["transport"]))
    fig.add_artist(FancyArrowPatch((0.590, 0.52), (0.607, 0.52),
                                   transform=fig.transFigure, arrowstyle="-|>",
                                   mutation_scale=15, lw=1.5, color=COLORS["symbol"]))
    fig.text(0.045, 0.068,
             r"$\sigma S_\Gamma\sigma^{-1}=[T_{k,j}]_{k,j=1}^m$"
             "     ·     column $j$ = input     ·     row $k$ = output     ·     C = cusp, R = ray",
             fontsize=13.0, color=COLORS["ink"], va="center")
    return fig


def render_beamer_compact(params: BranchParameters) -> plt.Figure:
    """Large three-panel visual, aspect 2.42:1, for a Beamer content area."""
    fig = plt.figure(figsize=(12.8, 5.3), facecolor="white")
    ga = _card(fig, (0.038, 0.122, 0.314, 0.842), "CURVE  Γ", COLORS["geometry"], True)
    ha = _card(fig, (0.373, 0.122, 0.225, 0.842), "TRANSPORT  σ", COLORS["transport"], True)
    ma = _card(fig, (0.619, 0.122, 0.343, 0.842), "BLOCK MATRIX", COLORS["symbol"], True)
    _geometry(ga, params, 5, 1.0)
    _half_lines(ha, params, 5, 1.0)
    _matrix(ma, params, 5, 1.0)
    fig.add_artist(FancyArrowPatch((0.353, 0.56), (0.370, 0.56),
                                   transform=fig.transFigure, arrowstyle="-|>",
                                   mutation_scale=15, lw=1.5, color=COLORS["transport"]))
    fig.add_artist(FancyArrowPatch((0.600, 0.56), (0.617, 0.56),
                                   transform=fig.transFigure, arrowstyle="-|>",
                                   mutation_scale=15, lw=1.5, color=COLORS["symbol"]))
    fig.text(0.045, 0.060,
             r"$\sigma S_\Gamma\sigma^{-1}=[T_{k,j}]$"
             "   ·   column $j$: input   ·   row $k$: output   ·   C = cusp, R = ray",
             fontsize=13.2, color=COLORS["ink"], va="center")
    return fig


def render_assets(params: BranchParameters, timing: AnimationTiming,
                  output_dir: Path, output_name: str = "branch_interactions_v1",
                  *, output_gif: str | None = None,
                  output_mp4: str | None = None,
                  show_exact_kernel: bool = True,
                  show_compact_model: bool = True,
                  show_operator_class: bool = True,
                  dpi: int = 80) -> dict[str, Path | float | int]:
    output_dir.mkdir(parents=True, exist_ok=True)
    review_dir = output_dir / "review_frames"
    review_dir.mkdir(exist_ok=True)
    static_fig = render_static_compact(params)
    static_pdf = output_dir / "branch_interactions_static.pdf"
    static_alias = output_dir / "branch_interactions_static_v1.pdf"
    static_png = output_dir / f"{output_name}.png"
    static_fig.savefig(static_pdf, format="pdf", metadata=PDF_META)
    shutil.copyfile(static_pdf, static_alias)
    static_fig.savefig(static_png, format="png", dpi=160)
    plt.close(static_fig)
    beamer_pdf = output_dir / "branch_interactions_beamer.pdf"
    beamer_fig = render_beamer_compact(params)
    beamer_fig.savefig(beamer_pdf, format="pdf", metadata=PDF_META)
    plt.close(beamer_fig)

    stage_indices: dict[int, list[int]] = {stage: [] for stage in STAGE_TITLES}
    with tempfile.TemporaryDirectory(prefix="k25-branch-frames-") as frame_tmp:
        frame_dir = Path(frame_tmp)
        index = 0
        for stage, seconds, start_progress, end_progress in timing.schedule():
            total = _stage_frame_count(seconds, timing.fps)
            for local in range(total):
                progress = start_progress + (end_progress - start_progress) * (local + 1) / total
                fig = render_frame(params, stage, progress,
                                   show_exact_kernel=show_exact_kernel,
                                   show_compact_model=show_compact_model,
                                   show_operator_class=show_operator_class)
                frame = frame_dir / f"frame-{index:05d}.png"
                fig.savefig(frame, format="png", dpi=dpi)
                plt.close(fig)
                stage_indices[stage].append(index)
                index += 1

        selected = {
            "first": stage_indices[1][-1],
            "matrix": stage_indices[4][-1],
            "cc": stage_indices[6][int(0.90 * (len(stage_indices[6]) - 1))],
            "cr": stage_indices[7][int(0.90 * (len(stage_indices[7]) - 1))],
            "rc": stage_indices[8][int(0.90 * (len(stage_indices[8]) - 1))],
            "rr": stage_indices[9][int(0.90 * (len(stage_indices[9]) - 1))],
            "last": stage_indices[10][-1],
        }
        for name, number in selected.items():
            shutil.copyfile(frame_dir / f"frame-{number:05d}.png",
                            review_dir / f"{name}.png")

        mp4_name = output_mp4 or f"{output_name}.mp4"
        if Path(mp4_name).name != mp4_name or not mp4_name.endswith(".mp4"):
            raise ValueError("output_mp4 must be a .mp4 filename, without directories")
        mp4 = output_dir / mp4_name
        subprocess.run([
            "ffmpeg", "-y", "-loglevel", "error", "-framerate", str(timing.fps),
            "-i", str(frame_dir / "frame-%05d.png"), "-c:v", "libx264",
            "-pix_fmt", "yuv420p", "-crf", "21", "-movflags", "+faststart",
            str(mp4),
        ], check=True)

        gif_name = output_gif or f"{output_name}.gif"
        if Path(gif_name).name != gif_name or not gif_name.endswith(".gif"):
            raise ValueError("output_gif must be a .gif filename, without directories")
        gif = output_dir / gif_name
        stride = 2 if timing.fps >= 18 else 1
        gif_frames = []
        for number in range(0, index, stride):
            with Image.open(frame_dir / f"frame-{number:05d}.png") as frame:
                gif_frames.append(frame.convert("RGB").quantize(colors=96))
        gif_frames[0].save(gif, save_all=True, append_images=gif_frames[1:],
                           duration=int(round(1000 * stride / timing.fps)),
                           loop=0, optimize=False, disposal=2)

    return {
        "gif": gif,
        "mp4": mp4,
        "png": static_png,
        "pdf": static_pdf,
        "pdf_v1": static_alias,
        "beamer_pdf": beamer_pdf,
        "frames": index,
        "duration_seconds": index / timing.fps,
    }
