"""Render the validated 12-step Karlovich 2025 reduction storyboard.

The stages and source equations come from full_pipeline_metadata. This
renderer reuses already exported PNG assets; it does not recalculate their
geometry or replace exact identities by compact models.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import subprocess
import tempfile
import textwrap

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Circle
import numpy as np
from PIL import Image

from full_pipeline_metadata import PIPELINE_STAGES, PipelineStage, validate_pipeline_stages
from visual_style import COLORS

plt.rcParams.update({"font.family": "STIXGeneral", "mathtext.fontset": "stix",
                     "pdf.fonttype": 42})

LAYER_COLOR = {
    "exact": COLORS["geometry"],
    "modK": COLORS["warning"],
    "symbol": COLORS["symbol"],
}
LAYER_LABEL = {
    "exact": "EXACT GEOMETRY / IDENTITY / DEFINITION",
    "modK": "EQUIVALENCE MODULO COMPACT OPERATORS",
    "symbol": "LOCAL FINITE SYMBOL",
}
ASSET_CAPTION = {
    "geometry": "Branches generated from their parametrizations",
    "real_algebra": "C reflects values f(t); the curve Γ is unchanged",
    "real_operator": "C reflects values f(t); the curve Γ is unchanged",
    "transport": "Schematic view of the exact isometric transport",
    "exact_blocks": "Matrix entry (k,j): input j, output k",
    "wh_mellin": "Numerical Mellin/Fourier illustration; not a compactness proof",
    "auxiliary_symbol": "Scalar zero-fiber arc; not the full m×m symbol or Ω-hat",
}


@dataclass(frozen=True)
class ReductionTiming:
    fps: int = 24
    hold_stage: float = 0.9
    transition_duration: float = 0.35
    hold_end: float = 1.2

    def __post_init__(self) -> None:
        if self.fps < 1 or min(self.hold_stage, self.transition_duration,
                               self.hold_end) <= 0:
            raise ValueError("FPS and all stage durations must be positive.")


def _source_line(source: str) -> str:
    return "\n".join(textwrap.wrap(source, width=112, break_long_words=False))


def _asset_image(stage: PipelineStage, asset_dir: Path) -> Image.Image | None:
    if stage.asset_stem is None:
        return None
    path = asset_dir / f"{stage.asset_stem}.png"
    if not path.is_file():
        raise FileNotFoundError(
            f"Validated asset {path} is required for stage {stage.key}")
    return Image.open(path).convert("RGB")


def _rail(fig: plt.Figure, active: int) -> None:
    count = len(PIPELINE_STAGES)
    positions = np.linspace(.065, .935, count)
    fig.add_artist(plt.Line2D(
        [positions[0], positions[-1]], [.815, .815],
        transform=fig.transFigure, color=COLORS["rule"], lw=1.5))
    for index, stage in enumerate(PIPELINE_STAGES):
        selected = index == active
        color = LAYER_COLOR[stage.layer] if index <= active else COLORS["rule"]
        fig.add_artist(Circle(
            (positions[index], .815), .013 if selected else .009,
            transform=fig.transFigure,
            facecolor=color, edgecolor="white", lw=.8, zorder=5))
        fig.text(positions[index], .785, f"{index+1:02d}",
                 ha="center", va="top", fontsize=8.8,
                 color=color if index <= active else COLORS["muted"])


STAGE_EXPLANATION = {
    "exact_linearization": (
        "Upper row: A, B.  Lower row: CBC, CAC.",
        "An exact complex-linear lift of the real-linear operator N.",
    ),
    "compact_model": (
        "The exact transported matrix equals its model plus K.",
        "This is the first step taken modulo compact operators.",
    ),
    "localization": (
        "Four strata of the local parameter domain (6.5).",
        "The parameter ω includes the boundary faces at 0 and infinity.",
    ),
    "doubled_symbol": (
        "Θ(aI) = diag(aI, āI).",
        "Conjugation acts on the second diagonal of the lift.",
    ),
    "fredholm_test": (
        "Pointwise test at every ω in Ω-hat.",
        "The determinant is taken only after obtaining a finite 2m×2m matrix.",
    ),
}


def render_stage(stage_index: int, asset_dir: Path) -> plt.Figure:
    """Large current stage plus 12-step progress rail."""
    validate_pipeline_stages()
    if not 0 <= stage_index < len(PIPELINE_STAGES):
        raise IndexError(stage_index)
    stage = PIPELINE_STAGES[stage_index]
    fig = plt.figure(figsize=(12.8, 7.2), facecolor="white")
    fig.text(.055, .965, "FROM THE MIXED STAR TO A FINITE DETERMINANT",
             fontsize=18, fontweight="bold", color=COLORS["main"], va="top")
    fig.text(.055, .905, f"{stage_index+1:02d} / 12    {stage.title}",
             fontsize=24, fontweight="bold", color=LAYER_COLOR[stage.layer],
             va="top")
    layer_label = ("MODEL BLOCK CLASSES AFTER COMPACT REDUCTION"
                   if stage.key == "wh_mellin" else LAYER_LABEL[stage.layer])
    fig.text(.94, .904, layer_label,
             fontsize=9.5, color=LAYER_COLOR[stage.layer],
             ha="right", va="top")
    _rail(fig, stage_index)

    image = _asset_image(stage, asset_dir)
    if image is not None:
        left = fig.add_axes([.055, .22, .45, .48])
        left.imshow(image)
        left.axis("off")
        fig.add_artist(FancyBboxPatch(
            (.053, .217), .454, .486, boxstyle="round,pad=.003",
            transform=fig.transFigure, facecolor="none",
            edgecolor=LAYER_COLOR[stage.layer], lw=1.2))
        fig.text(.28, .19, ASSET_CAPTION[stage.key], ha="center", va="center",
                 fontsize=10.5, color=COLORS["muted"])
        formula_x, formula_width = .535, .40
    else:
        formula_x, formula_width = .085, .83
    formula_ax = fig.add_axes([formula_x, .35 if image is None else .21,
                               formula_width, .33 if image is None else .49])
    formula_ax.axis("off")
    font_size = 22 if len(stage.formula) > 74 else 27
    formula_ax.text(
        .5, .58, "$"+stage.formula+"$", ha="center", va="center",
        transform=formula_ax.transAxes, fontsize=font_size,
        color=COLORS["ink"])
    if stage.key == "transport":
        note = "Schematic picture of an exact isometry of function spaces"
    elif stage.key == "compact_model":
        note = "Only here is the compact remainder removed"
    elif stage.key == "fredholm_test":
        note = "Ordinary determinant of a finite 2m×2m matrix"
    elif stage.key == "exact_blocks":
        note = "Column j = input; row k = output"
    else:
        note = LAYER_LABEL[stage.layer].capitalize()
    if image is not None:
        formula_ax.text(.5, .18, note, ha="center", va="center",
                        transform=formula_ax.transAxes, fontsize=12,
                        color=COLORS["muted"])
    else:
        details = STAGE_EXPLANATION.get(stage.key)
        if details is None:
            raise ValueError(f"Missing explanatory panel for {stage.key}")
        if stage.key == "localization":
            fig.add_artist(FancyBboxPatch(
                (.135, .17), .73, .23, boxstyle="round,pad=.006",
                transform=fig.transFigure, facecolor=COLORS["soft"],
                edgecolor=LAYER_COLOR[stage.layer], lw=1.1, zorder=-1))
            strata = (
                r"M_0(SO^\diamond)\times\{\infty\}\times\overline{\mathbb{R}}",
                r"\bigcup_{t>0}M_t(SO^\diamond)\times\{\pm\infty\}\times\overline{\mathbb{R}}",
                r"M_\infty(SO^\diamond)\times\mathbb{R}\times\overline{\mathbb{R}}",
                r"M_\infty(SO^\diamond)\times\{\infty\}\times\{\pm\infty\}",
            )
            for stratum_index, expression in enumerate(strata):
                fig.text(.19, .365-.052*stratum_index,
                         f"{stratum_index+1}.  $"+expression+"$",
                         ha="left", va="center", fontsize=14.5,
                         color=COLORS["ink"])
        else:
            fig.add_artist(FancyBboxPatch(
                (.135, .215), .73, .16, boxstyle="round,pad=.006",
                transform=fig.transFigure, facecolor=COLORS["soft"],
                edgecolor=LAYER_COLOR[stage.layer], lw=1.1, zorder=-1))
            fig.text(.5, .305, details[0], ha="center", va="center",
                     fontsize=17, color=COLORS["ink"])
            fig.text(.5, .252, details[1], ha="center", va="center",
                     fontsize=12.5, color=COLORS["muted"])
    fig.text(.055, .115, "SOURCE", fontsize=9.5,
             fontweight="bold", color=LAYER_COLOR[stage.layer])
    fig.text(.055, .075, _source_line(stage.source), fontsize=10.5,
             color=COLORS["muted"], va="center")
    return fig


def render_static_overview() -> plt.Figure:
    """One programmatic 4×3 vector overview for Beamer and study guide."""
    validate_pipeline_stages()
    fig = plt.figure(figsize=(12.8, 7.2), facecolor="white")
    fig.text(.045, .965, "FREDHOLM REDUCTION: 12 MATHEMATICAL STEPS",
             fontsize=18, color=COLORS["main"], va="top",
             fontweight="bold")
    fig.text(.045, .913,
             "Exact transport → compact model → WH/Mellin classes → local finite symbol",
             fontsize=12.8, color=COLORS["muted"], va="top")
    fig.text(.955, .913, "READ LEFT TO RIGHT, TOP TO BOTTOM",
             fontsize=8.5, color=COLORS["muted"], ha="right", va="top")
    columns, rows = 4, 3
    x0, y_top, x_gap, y_gap = .045, .81, .012, .037
    width = (1-.09-(columns-1)*x_gap)/columns
    height = (.69-(rows-1)*y_gap)/rows
    for index, stage in enumerate(PIPELINE_STAGES):
        row, col = divmod(index, columns)
        x = x0+col*(width+x_gap)
        y = y_top-(row+1)*height-row*y_gap
        color = LAYER_COLOR[stage.layer]
        fig.add_artist(FancyBboxPatch(
            (x,y),width,height,boxstyle="round,pad=.004",
            transform=fig.transFigure, facecolor="white",
            edgecolor=color,lw=1.25,zorder=-1))
        fig.text(x+.012,y+height-.034,f"{index+1:02d}  {stage.title}",
                 fontsize=11.2,fontweight="bold",color=color,va="top")
        ax=fig.add_axes([x+.010,y+.023,width-.020,height-.075])
        ax.axis("off")
        size=10 if len(stage.formula)>74 else 11.5
        ax.text(.5,.57,"$"+stage.formula+"$",ha="center",va="center",
                transform=ax.transAxes,fontsize=size,color=COLORS["ink"])
        if col<columns-1:
            fig.text(x+width+.004,y+height/2,"→",color=COLORS["muted"],
                     ha="center",va="center",fontsize=12)
    fig.text(.045,.052,
             "Karlovich 2025: (1.1), (3.5)–(3.28), (6.5), Theorems 6.2 and 7.2. "
             "The final determinant belongs to the 2m×2m symbol on Ω-hat.",
             fontsize=10.7,color=COLORS["muted"])
    return fig


def render_assets(timing: ReductionTiming, asset_dir: Path,
                  output_dir: Path,
                  stem: str = "full_reduction_pipeline") -> dict[str, object]:
    """Render static overview and crossfaded stage animation."""
    validate_pipeline_stages()
    output_dir.mkdir(parents=True, exist_ok=True)
    overview = render_static_overview()
    png, pdf = output_dir/f"{stem}.png", output_dir/f"{stem}.pdf"
    overview.savefig(png, dpi=160)
    overview.savefig(pdf, format="pdf")
    plt.close(overview)
    with tempfile.TemporaryDirectory(prefix="k25-full-pipeline-") as directory:
        temp = Path(directory)
        stills: list[Image.Image] = []
        for index in range(len(PIPELINE_STAGES)):
            figure = render_stage(index, asset_dir)
            path=temp/f"stage-{index:02d}.png"
            figure.savefig(path,dpi=80)
            plt.close(figure)
            with Image.open(path) as image:
                stills.append(image.convert("RGB"))
        frame_dir=temp/"frames"
        frame_dir.mkdir()
        hold=max(1,round(timing.hold_stage*timing.fps))
        transition=max(2,round(timing.transition_duration*timing.fps))
        end=max(1,round(timing.hold_end*timing.fps))
        frame_count=0
        def write(image: Image.Image) -> None:
            nonlocal frame_count
            image.save(frame_dir/f"frame-{frame_count:05d}.png")
            frame_count+=1
        for index, still in enumerate(stills):
            for _ in range(hold):
                write(still)
            if index+1<len(stills):
                for n in range(1,transition+1):
                    write(Image.blend(still,stills[index+1],
                                      n/(transition+1)))
        for _ in range(end):
            write(stills[-1])
        mp4=output_dir/f"{stem}.mp4"
        subprocess.run([
            "ffmpeg","-y","-loglevel","error","-framerate",str(timing.fps),
            "-i",str(frame_dir/"frame-%05d.png"),"-c:v","libx264",
            "-pix_fmt","yuv420p","-crf","21","-movflags","+faststart",
            str(mp4)],check=True)
        gif=output_dir/f"{stem}.gif"
        stride=2 if timing.fps>=18 else 1
        images=[]
        for index in range(0,frame_count,stride):
            with Image.open(frame_dir/f"frame-{index:05d}.png") as image:
                images.append(image.convert("RGB").quantize(colors=96))
        images[0].save(
            gif,save_all=True,append_images=images[1:],
            duration=round(1000*stride/timing.fps),loop=0,
            optimize=False,disposal=2)
    return {"gif":gif,"mp4":mp4,"png":png,"pdf":pdf,
            "frames":frame_count,"duration_seconds":frame_count/timing.fps,
            "stages":len(PIPELINE_STAGES)}


if __name__ == "__main__":
    validate_pipeline_stages()
    print(f"Validated {len(PIPELINE_STAGES)} full-reduction stages; "
          "exact → mod K → finite symbol")
