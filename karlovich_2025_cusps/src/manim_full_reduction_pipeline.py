"""Manim scene for the twelve mathematical stages of Karlovich (2025).

Render when Manim is available::

    manim -pql manim_full_reduction_pipeline.py FullReductionPipelineScene

``K25_ASSET_DIR`` may point to a directory of existing PNG teaching assets;
missing images produce a labelled placeholder.  ``K25_SPEED_FACTOR`` changes
only pacing.  The route and formulae come from ``full_pipeline_metadata``.
Manim is not installed in the current authoring environment, so this scene
has passed syntax checks but still requires a render and visual inspection.
"""

from __future__ import annotations

import os
from pathlib import Path

import numpy as np
from manim import (
    Arrow, Create, FadeIn, FadeOut, Group, ImageMobject, MathTex, Rectangle,
    Scene, Text, VGroup, WHITE,
)

from full_pipeline_metadata import PIPELINE_STAGES, PipelineStage, validate_pipeline_stages
from visual_style import COLORS


LAYER_COLORS = {
    "exact": COLORS["geometry"],
    "modK": COLORS["warning"],
    "symbol": COLORS["symbol"],
}
LAYER_LABELS = {
    "exact": "EXACT DEFINITION / IDENTITY",
    "modK": "MODEL MODULO COMPACTS",
    "symbol": "FINITE LOCAL SYMBOL",
}
ASSET_CAPTIONS = {
    "branch_interactions_v1": "Parametric curve; schematic function transport",
    "complex_conjugation_v1": "Conjugation reflects values at fixed curve points",
    "mellin_fourier_pipeline": "Logarithmic-coordinate explanation",
    "fredholm_symbol_curve": "Local arc mu_nu; not the whole Omega-hat",
}


def _asset_directory() -> Path:
    configured = os.getenv("K25_ASSET_DIR")
    return Path(configured).expanduser() if configured else Path(__file__).resolve().parents[1] / "outputs"


def _speed_factor() -> float:
    speed = float(os.getenv("K25_SPEED_FACTOR", "1"))
    if not np.isfinite(speed) or speed <= 0:
        raise ValueError("K25_SPEED_FACTOR must be a finite positive number")
    return speed


def _route_position(index: int) -> np.ndarray:
    """Two-row snake: 01–06 left-to-right, 07–12 right-to-left."""
    if not 0 <= index < len(PIPELINE_STAGES):
        raise IndexError(index)
    column = index if index < 6 else 11 - index
    row_y = 2.58 if index < 6 else 1.62
    return np.array([-5.83 + 2.33 * column, row_y, 0.0])


def _route_node(stage: PipelineStage, index: int) -> VGroup:
    color = LAYER_COLORS[stage.layer]
    box = Rectangle(
        width=2.02, height=0.68,
        stroke_color=color, stroke_width=1.45,
        fill_color=color, fill_opacity=0.055,
    )
    label = Text(f"{index + 1:02d}  {stage.title}",
                 color=COLORS["ink"], font_size=17, weight="BOLD")
    label.scale_to_fit_width(min(label.width, 1.82))
    label.move_to(box)
    node = VGroup(box, label)
    node.move_to(_route_position(index))
    return node


def _route_arrows(nodes: list[VGroup]) -> VGroup:
    arrows = VGroup()
    for first, second in zip(nodes, nodes[1:]):
        if abs(first.get_center()[1] - second.get_center()[1]) < 0.1:
            sign = 1 if second.get_center()[0] > first.get_center()[0] else -1
            start = first.get_center() + np.array([sign * 1.03, 0, 0])
            end = second.get_center() - np.array([sign * 1.03, 0, 0])
        else:
            start = first.get_center() + np.array([0, -0.36, 0])
            end = second.get_center() + np.array([0, 0.36, 0])
        arrows.add(Arrow(start, end, buff=0, tip_length=0.105,
                         stroke_width=2.0, color=COLORS["muted"]))
    return arrows


def _asset_visual(stage: PipelineStage, asset_dir: Path) -> Group | None:
    if stage.asset_stem is None:
        return None
    panel = Rectangle(width=4.20, height=1.86,
                      stroke_color=COLORS["rule"], stroke_width=1.1,
                      fill_color=WHITE, fill_opacity=1)
    panel.move_to(np.array([4.20, -0.60, 0]))
    asset_path = asset_dir / f"{stage.asset_stem}.png"
    if asset_path.is_file():
        visual = ImageMobject(str(asset_path))
        visual.scale_to_fit_width(3.95)
        if visual.height > 1.40:
            visual.scale_to_fit_height(1.40)
        visual.move_to(np.array([4.20, -0.52, 0]))
        caption = ASSET_CAPTIONS.get(stage.asset_stem, "Visual aid; cited formula is authoritative")
    else:
        visual = Text(f"PNG pending: {stage.asset_stem}",
                      font_size=18, color=COLORS["muted"])
        visual.scale_to_fit_width(min(visual.width, 3.75))
        visual.move_to(np.array([4.20, -0.52, 0]))
        caption = "Formula and source remain available"
    caption_mobject = Text(caption, font_size=13, color=COLORS["muted"])
    caption_mobject.scale_to_fit_width(min(caption_mobject.width, 3.95))
    caption_mobject.move_to(np.array([4.20, -1.40, 0]))
    return Group(panel, visual, caption_mobject)


def _stage_content(stage: PipelineStage, asset_dir: Path) -> Group:
    """MathTex carries claims; PNGs are visibly labelled as teaching aids."""
    color = LAYER_COLORS[stage.layer]
    content = Group()

    heading = Text(stage.title, font_size=25, weight="BOLD", color=color)
    heading.scale_to_fit_width(min(heading.width, 7.5))
    heading.move_to(np.array([-5.58 + heading.width / 2, 0.39, 0]))
    content.add(heading)

    status = Text(LAYER_LABELS[stage.layer], font_size=16,
                  weight="BOLD", color=color)
    status.scale_to_fit_width(min(status.width, 4.55))
    status.move_to(np.array([5.50 - status.width / 2, 0.39, 0]))
    content.add(status)

    asset = _asset_visual(stage, asset_dir)
    formula_width = 7.72 if asset is not None else 12.30
    formula_x = -2.42 if asset is not None else 0.0
    formula = MathTex(stage.detail_formula or stage.formula,
                      font_size=31, color=COLORS["ink"])
    if formula.width > formula_width:
        formula.scale_to_fit_width(formula_width)
    if formula.height > 1.63:
        formula.scale_to_fit_height(1.63)
    formula.move_to(np.array([formula_x, -0.57, 0]))
    content.add(formula)
    if asset is not None:
        content.add(asset)

    source = Text(stage.source, font_size=14, color=COLORS["muted"])
    source.scale_to_fit_width(min(source.width, 12.45))
    source.move_to(np.array([0, -1.91, 0]))
    content.add(source)
    return content


class FullReductionPipelineScene(Scene):
    """Γ → real algebra → exact transport → compact model → finite test."""

    def construct(self) -> None:
        validate_pipeline_stages()
        speed = _speed_factor()
        asset_dir = _asset_directory()
        self.camera.background_color = WHITE

        title = Text("KARLOVICH 2025  /  FULL FREDHOLM REDUCTION",
                     font_size=30, weight="BOLD", color=COLORS["main"])
        title.scale_to_fit_width(min(title.width, 12.6))
        title.move_to(np.array([0, 3.55, 0]))
        subtitle = Text("Blue: exact data    Red: compact reduction    Violet: finite symbol",
                        font_size=17, color=COLORS["muted"])
        subtitle.move_to(np.array([0, 3.13, 0]))
        self.add(title, subtitle)

        nodes = [_route_node(stage, index) for index, stage in enumerate(PIPELINE_STAGES)]
        arrows = _route_arrows(nodes)
        self.play(*[FadeIn(node) for node in nodes],
                  *[Create(arrow) for arrow in arrows], run_time=0.9 / speed)

        card = Rectangle(width=13.35, height=2.68,
                         stroke_color=COLORS["rule"], stroke_width=1.35,
                         fill_color=WHITE, fill_opacity=1)
        card.move_to(np.array([0, -0.78, 0]))
        self.play(FadeIn(card), run_time=0.25 / speed)

        previous_content: Group | None = None
        for index, stage in enumerate(PIPELINE_STAGES):
            node_box = nodes[index][0]
            animations = [
                node_box.animate.set_fill(LAYER_COLORS[stage.layer], opacity=0.23)
                .set_stroke(LAYER_COLORS[stage.layer], width=2.8),
            ]
            if index:
                previous = PIPELINE_STAGES[index - 1]
                animations.append(
                    nodes[index - 1][0].animate
                    .set_fill(LAYER_COLORS[previous.layer], opacity=0.09)
                    .set_stroke(LAYER_COLORS[previous.layer], width=1.45)
                )
            if previous_content is not None:
                animations.append(FadeOut(previous_content))
            self.play(*animations, run_time=0.38 / speed)
            content = _stage_content(stage, asset_dir)
            self.play(FadeIn(content), run_time=0.45 / speed)
            self.wait((1.75 if stage.key in {"localization", "fredholm_test"} else 1.15) / speed)
            previous_content = content

        self.wait(0.9 / speed)
