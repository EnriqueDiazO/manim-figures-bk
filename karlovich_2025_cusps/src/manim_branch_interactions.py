"""Manim version of the ten-stage branch-interaction storyboard.

Render from this directory with::

    manim -pql manim_branch_interactions.py BranchInteractionsScene

Set K25_S, K25_R and K25_SPEED_FACTOR to change the illustration.  Geometry,
cell classes and kernel formulae are imported from the same modules used by
07_branch_interactions.ipynb.  The Matplotlib notebook render is the tested
GIF/MP4 release; this Manim source awaits an environment with Manim installed.
"""

from __future__ import annotations

import os
import numpy as np
from manim import (
    Arrow, Create, FadeIn, FadeOut, Line, MathTex, Rectangle, Scene, Text,
    Transform, VGroup, VMobject, WHITE,
)

from geometry import (
    BranchParameters, branch_points, default_beta_values, default_c_values,
)
from interactions import cells, count_by_class
from operator_metadata import INTERACTIONS
from visual_style import COLORS, TYPE_COLORS


def scene_parameters() -> BranchParameters:
    """Build a valid illustrative star from configurable branch counts."""
    s = int(os.getenv("K25_S", "2"))
    r = int(os.getenv("K25_R", "2"))
    c_raw = os.getenv("K25_C_VALUES", "")
    beta_raw = os.getenv("K25_BETA_VALUES", "")
    c_values = tuple(float(v) for v in c_raw.split(",")) if c_raw else default_c_values(s)
    beta_values = tuple(float(v) for v in beta_raw.split(",")) if beta_raw else default_beta_values(r)
    return BranchParameters(
        s=s, r=r, c_values=c_values, beta_values=beta_values,
        p=2.0, delta=0.0,
    )


def _small_label(value: str, color: str, size: int = 24) -> Text:
    return Text(value, font_size=size, color=color, weight="BOLD")


def _cap_width(obj, max_width: float):
    """Shrink long formulae without enlarging short ones into collisions."""
    if obj.width > max_width:
        obj.scale_to_fit_width(max_width)
    return obj


class BranchInteractionsScene(Scene):
    """Γ → σ → exact T[k,j] → CC/CR/RC/RR → compact model."""

    def construct(self) -> None:
        params = scene_parameters()
        speed = float(os.getenv("K25_SPEED_FACTOR", "1"))
        if speed <= 0:
            raise ValueError("K25_SPEED_FACTOR must be positive")
        self.camera.background_color = WHITE

        title = _small_label("BRANCH INTERACTIONS", COLORS["main"], 31)
        title.move_to(np.array([-3.80, 3.54, 0]))
        counts = _small_label(f"s={params.s}   r={params.r}   m={params.m}", COLORS["muted"], 19)
        counts.move_to(np.array([5.60, 3.54, 0]))
        self.add(title, counts)

        panel_bounds = (
            (-4.92, 0.75, 3.60, 4.25),
            (-0.54, 0.75, 2.74, 4.25),
            (4.20, 0.75, 4.18, 4.25),
        )
        panel_titles = (("CURVE Γ", COLORS["geometry"]),
                        ("TRANSPORT σ", COLORS["transport"]),
                        ("OUTPUT k × INPUT j", COLORS["symbol"]))
        panels = VGroup()
        for (cx, cy, width, height), (label, color) in zip(panel_bounds, panel_titles):
            box = Rectangle(width=width, height=height, stroke_color=COLORS["rule"],
                            stroke_width=1.3, fill_color=WHITE, fill_opacity=1)
            box.move_to(np.array([cx, cy, 0]))
            caption = _small_label(label, color, 20)
            caption.move_to(np.array([cx, cy + height / 2 - 0.36, 0]))
            panels.add(box, caption)
        self.add(panels)

        # Stage 1.  The polyline points are sampled from γ_k(x), not from
        # hand-coded Bézier paths.  The same branch_points feeds the notebook.
        curves = VGroup()
        for k in range(1, params.m + 1):
            z = branch_points(params, k)
            xy = np.column_stack((z.real, z.imag, np.zeros_like(z.real)))
            xy[:, 0] = -4.92 + 1.10 * xy[:, 0]
            xy[:, 1] = 0.63 + 1.10 * xy[:, 1]
            curve = VMobject(stroke_color=(COLORS["geometry"] if k <= params.s else COLORS["wiener"]),
                              stroke_width=4)
            curve.set_points_as_corners(xy)
            curves.add(curve)
            a, b = ((5, 18) if k <= params.s else
                    (int(0.25 * len(xy)), int(0.50 * len(xy))))
            orientation = Arrow(xy[a], xy[b], buff=0, tip_length=0.13,
                                stroke_width=4,
                                color=COLORS["geometry"] if k <= params.s else COLORS["wiener"])
            self.play(Create(curve), FadeIn(orientation), run_time=0.32 / speed)
        exact_geometry = MathTex(
            r"\gamma_k(x)=(x-ic_k)^{-1}\ (k\le s),\qquad"
            r"\gamma_k(x)=e^{i\beta_k}/x\ (k>s)",
            color=COLORS["ink"], font_size=30,
        )
        _cap_width(exact_geometry, 12.4)
        exact_geometry.move_to(np.array([0, -2.33, 0]))
        self.play(FadeIn(exact_geometry), run_time=0.3 / speed)
        self.wait(0.35 / speed)

        # Stages 2–3.  σ denotes the isometry of function spaces; the copies
        # of R_+ are schematic and are built from the number of branches.
        arrow_left = Arrow(start=np.array([-2.99, 0.75, 0]),
                           end=np.array([-2.05, 0.75, 0]), buff=0,
                           color=COLORS["transport"], stroke_width=4)
        self.play(Create(arrow_left), run_time=0.35 / speed)
        half_lines = VGroup()
        usable_height = 2.75
        for k in range(1, params.m + 1):
            y = 0.64 + (params.m + 1 - 2 * k) * usable_height / (2 * params.m)
            color = COLORS["geometry"] if k <= params.s else COLORS["wiener"]
            line = Line(np.array([-0.70, y, 0]), np.array([0.30, y, 0]),
                        color=color, stroke_width=4)
            label = MathTex(rf"\Gamma_{{{k}}}\mapsto\varphi_{{{k}}}",
                            color=color, font_size=20)
            label.move_to(np.array([-1.31, y, 0]))
            half_lines.add(line, label)
            self.play(Create(line), FadeIn(label), run_time=0.24 / speed)
        isometry_label = _small_label("SCHEMATIC ISOMETRIC TRANSPORT", COLORS["transport"], 14)
        isometry_label.move_to(np.array([-0.54, -1.05, 0]))
        self.play(FadeIn(isometry_label), run_time=0.2 / speed)
        sigma_formula = MathTex(
            r"\sigma:L^p(\Gamma,\widetilde w)\to[L^p(\mathbb R_+,w_\delta)]^m",
            color=COLORS["transport"], font_size=29,
        )
        _cap_width(sigma_formula, 12.4)
        sigma_formula.move_to(exact_geometry)
        self.play(Transform(exact_geometry, sigma_formula), run_time=0.45 / speed)
        self.wait(0.22 / speed)
        vector_formula = MathTex(
            r"\varphi=(\varphi_1,\ldots,\varphi_m),\qquad"
            r"\varphi_k=\Upsilon_k(f|_{\Gamma_k})",
            color=COLORS["transport"], font_size=31,
        )
        vector_formula.move_to(exact_geometry)
        self.play(Transform(exact_geometry, vector_formula), run_time=0.45 / speed)

        # Stages 4–5.  Matrix locations, labels and colors follow the index
        # convention from interactions.cells: row k output, column j input.
        arrow_right = Arrow(start=np.array([0.90, 0.75, 0]),
                            end=np.array([1.93, 0.75, 0]), buff=0,
                            color=COLORS["symbol"], stroke_width=4)
        self.play(Create(arrow_right), run_time=0.3 / speed)
        # Keep the column labels below the INPUT heading as m grows.
        side = min(0.59, 2.35 / params.m)
        grid = VGroup()
        indices = VGroup()
        input_heading = _small_label("INPUT j →", COLORS["muted"], 16)
        input_heading.move_to(np.array([4.18, 2.25, 0]))
        output_heading = _small_label("OUTPUT k ↓", COLORS["muted"], 16)
        output_heading.rotate(np.pi / 2)
        output_heading.move_to(np.array([2.31, 0.65, 0]))
        indices.add(input_heading, output_heading)
        for j in range(1, params.m + 1):
            label = MathTex(rf"j={j}",
                            color=COLORS["geometry"] if j <= params.s else COLORS["wiener"],
                            font_size=18)
            label.move_to(np.array([4.18 + (j - (params.m + 1) / 2) * side,
                                    0.65 + params.m * side / 2 + 0.14, 0]))
            indices.add(label)
        for k in range(1, params.m + 1):
            label = MathTex(rf"k={k}",
                            color=COLORS["geometry"] if k <= params.s else COLORS["wiener"],
                            font_size=18)
            label.move_to(np.array([4.18 - params.m * side / 2 - 0.19,
                                    0.65 + ((params.m + 1) / 2 - k) * side, 0]))
            indices.add(label)
        self.play(FadeIn(indices), run_time=0.22 / speed)
        cell_labels: dict[tuple[int, int], MathTex] = {}
        cell_rects: dict[tuple[int, int], Rectangle] = {}
        for cell in cells(params):
            x = 4.18 + (cell.j - (params.m + 1) / 2) * side
            y = 0.65 + ((params.m + 1) / 2 - cell.k) * side
            rect = Rectangle(width=side * 0.94, height=side * 0.94,
                             stroke_color=COLORS["rule"], stroke_width=1.5,
                             fill_color=COLORS["soft"], fill_opacity=1)
            rect.move_to(np.array([x, y, 0]))
            label = MathTex(rf"T_{{{cell.k},{cell.j}}}", color=COLORS["ink"],
                            font_size=19 if params.m <= 5 else 15)
            label.move_to(rect)
            grid.add(rect, label)
            cell_rects[cell.k, cell.j] = rect
            cell_labels[cell.k, cell.j] = label
        self.play(*[FadeIn(obj) for obj in grid], run_time=1.05 / speed)
        exact_matrix = MathTex(
            r"\sigma S_\Gamma\sigma^{-1}=[T_{k,j}]_{k,j=1}^{m}",
            color=COLORS["ink"], font_size=34,
        )
        exact_matrix.move_to(exact_geometry)
        self.play(Transform(exact_geometry, exact_matrix), run_time=0.42 / speed)
        self.wait(0.25 / speed)

        for cell in cells(params):
            rect = cell_rects[cell.k, cell.j]
            new_label = MathTex(rf"\mathrm{{{cell.kind}}}",
                                color=TYPE_COLORS[cell.kind], font_size=22)
            new_label.move_to(rect)
            self.play(Transform(cell_labels[cell.k, cell.j], new_label),
                      rect.animate.set_fill(TYPE_COLORS[cell.kind], opacity=0.14)
                      .set_stroke(TYPE_COLORS[cell.kind], width=1.5),
                      run_time=0.06 / speed)
        legend = _small_label("C = cusp     R = ray", COLORS["muted"], 20)
        legend.move_to(np.array([4.19, -1.08, 0]))
        self.play(FadeIn(legend), run_time=0.25 / speed)
        count = count_by_class(params)
        block_count = Text(
            "   ".join(f"{code}: {count[code]}" for code in ("CC", "CR", "RC", "RR")),
            font_size=28, color=COLORS["symbol"],
        )
        block_count.move_to(exact_geometry)
        self.play(Transform(exact_geometry, block_count), run_time=0.45 / speed)

        # Stages 6–9.  The exact kernels are from (3.6); each model is a
        # separate line.  The model is equal to the exact entry in RR.
        for code in ("CC", "CR", "RC", "RR"):
            spec = INTERACTIONS[code]
            color = TYPE_COLORS[code]
            for cell in cells(params):
                rect = cell_rects[cell.k, cell.j]
                rect.set_fill(color if cell.kind == code else COLORS["soft"],
                              opacity=0.21 if cell.kind == code else 0.48)
            banner = _small_label(
                f"{code}: output k = {code[0]}, input j = {code[1]}", color, 22,
            )
            banner.move_to(np.array([0, -1.78, 0]))
            exact = MathTex(
                r"K^{\mathrm{ex}}_{k,j}(x,\tau)=" + spec.exact_kernel,
                color=color, font_size=32,
            )
            _cap_width(exact, 12.3)
            exact.move_to(np.array([0, -2.37, 0]))
            source = _small_label("EXACT TRANSPORTED KERNEL · (3.6)",
                                  COLORS["muted"], 17)
            source.move_to(np.array([0, -3.10, 0]))
            opening = [FadeIn(banner), FadeIn(exact), FadeIn(source)]
            if code == "CC":
                opening.insert(0, FadeOut(exact_geometry))
            self.play(*opening, run_time=0.42 / speed)
            self.wait(0.35 / speed)
            model_title = ("MODEL = EXACT" if code == "RR" else
                           "COMPACT MODEL · DIFFERENCE IS COMPACT")
            model_note = _small_label(model_title, COLORS["proved"], 20)
            model_note.move_to(np.array([0, -1.78, 0]))
            model = MathTex(
                r"K^{\mathrm{mod}}_{k,j}(x,\tau)=" + spec.model_kernel,
                color=COLORS["proved"], font_size=30,
            )
            _cap_width(model, 12.3)
            model.move_to(np.array([0, -2.37, 0]))
            operator_class = _small_label(spec.class_name.upper(),
                                          COLORS["symbol"], 17)
            _cap_width(operator_class, 12.3)
            operator_class.move_to(np.array([0, -3.10, 0]))
            self.play(Transform(banner, model_note), Transform(exact, model),
                      Transform(source, operator_class), run_time=0.48 / speed)
            self.wait(1.5 / speed)
            self.play(FadeOut(banner), FadeOut(exact), FadeOut(source),
                      run_time=0.24 / speed)

        # Stage 10.  Symbol construction is a later step, after reduction
        # modulo compact operators; conjugation doubles the matrix size.
        for cell in cells(params):
            rect = cell_rects[cell.k, cell.j]
            rect.set_fill(TYPE_COLORS[cell.kind], opacity=0.14)
        summary = MathTex(
            r"T_{k,j}\ \simeq\ S_{k,j}\quad\longrightarrow\quad"
            r"[S_\Gamma](\omega)\in\mathbb C^{m\times m}",
            color=COLORS["symbol"], font_size=34,
        )
        _cap_width(summary, 12.3)
        summary.move_to(np.array([0, -2.34, 0]))
        doubled = _small_label(
            "For A + BC, double first: the final symbol is 2m × 2m on Ω-hat.",
            COLORS["muted"], 20,
        )
        _cap_width(doubled, 12.3)
        doubled.move_to(np.array([0, -3.10, 0]))
        self.play(FadeIn(summary), FadeIn(doubled), run_time=0.55 / speed)
        self.wait(1.2 / speed)
