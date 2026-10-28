"""Verified stages of the Karlovich (2025) Fredholm reduction.

The sequence is deliberately a mathematical sequence, not a list of drawing
coordinates.  ``formula`` is LaTeX for Manim MathTex.  An asset is only a
visual aid; the cited equations, not the image, carry exact or compact claims.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import PurePath
from typing import Sequence


@dataclass(frozen=True)
class PipelineStage:
    key: str
    title: str
    formula: str
    source: str
    layer: str
    asset_stem: str | None
    detail_formula: str | None = None


PIPELINE_STAGES: tuple[PipelineStage, ...] = (
    PipelineStage(
        key="geometry",
        title="Mixed star Γ",
        formula=(
            r"\gamma_k(x)=(x-ic_k)^{-1}\ (k\leq s),\quad"
            r"\gamma_k(x)=e^{i\beta_k}/x\ (k>s)"
        ),
        source="Karlovich 2025, (1.1)–(1.2), p. 2",
        layer="exact",
        asset_stem="branch_interactions_v1",
    ),
    PipelineStage(
        key="real_algebra",
        title="Real algebra B",
        formula=(
            r"\mathfrak{B}=\mathrm{alg}\{aI,S_\Gamma,C\}"
        ),
        source="Karlovich 2025, (1.4), pp. 2–3: a in SO^diamond(Gamma), operators on real Lp; Section 7, p. 25",
        layer="exact",
        asset_stem="complex_conjugation_v1",
    ),
    PipelineStage(
        key="real_operator",
        title="N = A + BC",
        formula=r"N=A+BC,\quad A,B\in\mathfrak{A},\quad Cf=\overline{f}",
        source="Karlovich 2025, (7.1), p. 25",
        layer="exact",
        asset_stem="complex_conjugation_v1",
    ),
    PipelineStage(
        key="exact_linearization",
        title="Exact 2×2 lift",
        formula=r"\widetilde N=\Theta(A+BC)",
        source="Karlovich 2025, (7.2)–(7.4), Theorem 7.1, pp. 25–26: exact block matrix with rows (A,B) and (CBC,CAC)",
        layer="exact",
        asset_stem=None,
        detail_formula=r"\widetilde N=\begin{pmatrix}A&B\\ CBC&CAC\end{pmatrix}",
    ),
    PipelineStage(
        key="transport",
        title="Isometry σ",
        formula=(
            r"\sigma:L^p(\Gamma,\widetilde w)\to\,"
            r"L_m^p(\mathbb{R}_+,w_\delta)"
        ),
        source="Karlovich 2025, (3.5), p. 7",
        layer="exact",
        asset_stem="branch_interactions_v1",
    ),
    PipelineStage(
        key="exact_blocks",
        title="Exact matrix T",
        formula=r"\sigma S_\Gamma\sigma^{-1}=[T_{k,j}]_{k,j=1}^{m}",
        source="Karlovich 2025, (3.6), p. 8; column j input, row k output",
        layer="exact",
        asset_stem="branch_interactions_v1",
    ),
    PipelineStage(
        key="compact_model",
        title="Model mod K",
        formula=(
            r"\sigma S_\Gamma\sigma^{-1}=[S_{k,j}]+K,"
            r"\quad K\in\mathcal{K}"
        ),
        source="Karlovich 2025, Lemmas 3.1–3.2, Corollary 3.3, (3.21)–(3.23), pp. 8–14",
        layer="modK",
        asset_stem=None,
    ),
    PipelineStage(
        key="wh_mellin",
        title="WH + Mellin blocks",
        formula=(
            r"S_{k,j}\in\{\chi_\infty W(b)\chi_\infty,"
            r"M^0(c),\chi_\infty M^0(c)\chi_\infty\}"
        ),
        source="Karlovich 2025, (3.24)–(3.28), pp. 13–15",
        layer="modK",
        asset_stem="mellin_fourier_pipeline",
    ),
    PipelineStage(
        key="localization",
        title="Local domain Ω-hat",
        formula=r"\omega=(\xi,\eta,x)\in\widehat{\Omega}",
        detail_formula=(
            r"\begin{aligned}\widehat\Omega={}&"
            r"M_0(SO^\diamond)\times\{\infty\}\times\overline{\mathbb R}\\"
            r"&\cup\bigcup_{t>0}M_t(SO^\diamond)\times\{\pm\infty\}"
            r"\times\overline{\mathbb R}\\"
            r"&\cup M_\infty(SO^\diamond)\times\mathbb R\times"
            r"\overline{\mathbb R}\\"
            r"&\cup M_\infty(SO^\diamond)\times\{\infty\}"
            r"\times\{\pm\infty\}\end{aligned}"
        ),
        source="Karlovich 2025, (6.5), p. 20; overline R includes ±infinity",
        layer="symbol",
        asset_stem=None,
    ),
    PipelineStage(
        key="auxiliary_symbol",
        title="Finite m×m symbol",
        formula=(
            r"\Phi(A)(\omega)=[A](\omega)\in M_m(\mathbb{C}),"
            r"\quad\omega\in\widehat{\Omega}"
        ),
        source="Karlovich 2025, (6.18)–(6.19), Theorem 6.2, pp. 24–25",
        layer="symbol",
        asset_stem="fredholm_symbol_curve",
    ),
    PipelineStage(
        key="doubled_symbol",
        title="Finite 2m×2m symbol",
        formula=r"\mathcal{Y}(N)(\omega)\in M_{2m}(\mathbb{C})",
        source="Karlovich 2025, (7.3)–(7.6), pp. 25–26; conjugate second diagonal",
        layer="symbol",
        asset_stem=None,
        detail_formula=(
            r"\begin{gathered}"
            r"\Theta(aI)=\operatorname{diag}(aI,\overline a I),\\"
            r"\mathcal Y(N)(\omega)\in M_{2m}(\mathbb C)"
            r"\end{gathered}"
        ),
    ),
    PipelineStage(
        key="fredholm_test",
        title="Fredholm determinant",
        formula=(
            r"N\ \mathrm{Fredholm}\Leftrightarrow"
            r"\det\mathcal{Y}(N)(\omega)\ne0\ (\forall\omega\in\widehat{\Omega})"
        ),
        source="Karlovich 2025, Theorem 7.2, p. 26: ordinary determinant of the finite 2m-by-2m symbol at every omega in Omega-hat",
        layer="symbol",
        asset_stem=None,
        detail_formula=(
            r"\begin{gathered}N\text{ Fredholm}\iff"
            r"\det\mathcal Y(N)(\omega)\ne0\quad"
            r"\forall\omega\in\widehat\Omega,\\"
            r"\mathcal Y(N)(\omega)\in M_{2m}(\mathbb C)"
            r"\end{gathered}"
        ),
    ),
)


EXPECTED_KEYS = (
    "geometry", "real_algebra", "real_operator", "exact_linearization",
    "transport", "exact_blocks", "compact_model", "wh_mellin",
    "localization", "auxiliary_symbol", "doubled_symbol", "fredholm_test",
)
EXPECTED_LAYERS = ("exact",) * 6 + ("modK",) * 2 + ("symbol",) * 4


def validate_pipeline_stages(
    stages: Sequence[PipelineStage] = PIPELINE_STAGES,
) -> None:
    """Reject omitted, reordered or mathematically mistyped storyboard stages."""
    keys = tuple(stage.key for stage in stages)
    if len(keys) != len(set(keys)) or keys != EXPECTED_KEYS:
        raise ValueError(f"Pipeline keys must be unique and ordered as {EXPECTED_KEYS!r}")
    if tuple(stage.layer for stage in stages) != EXPECTED_LAYERS:
        raise ValueError("Pipeline layers must progress exact → modK → symbol")
    for stage in stages:
        if not stage.title.strip() or not stage.formula.strip() or not stage.source.strip():
            raise ValueError(f"Stage {stage.key!r} lacks title, formula or source")
        if stage.asset_stem is not None and (
            not stage.asset_stem or PurePath(stage.asset_stem).name != stage.asset_stem
            or "." in stage.asset_stem
        ):
            raise ValueError(f"Stage {stage.key!r} has an unsafe asset stem")
    if "\\mathcal{K}" not in stages[6].formula:
        raise ValueError("Compact-model stage must name its compact remainder")
    if "M_m" not in stages[9].formula:
        raise ValueError("The auxiliary symbol must be m×m")
    if any("2m" in stage.formula for stage in stages[:10]):
        raise ValueError("A 2m symbol may appear only after the auxiliary m symbol")
    if "2m" not in stages[10].formula or "2m" not in (stages[11].detail_formula or ""):
        raise ValueError("The final symbol and determinant must use finite 2m matrices")
    if stages[10].detail_formula is None or "\\overline a I" not in stages[10].detail_formula:
        raise ValueError("Theta(aI) must conjugate the second diagonal")
    if "\\det" not in stages[11].formula or "\\widehat\\Omega" not in (stages[11].detail_formula or ""):
        raise ValueError("Theorem 7.2 must test the finite symbol on Omega-hat")


validate_pipeline_stages()


if __name__ == "__main__":
    print(f"{len(PIPELINE_STAGES)} verified stages: " + " → ".join(EXPECTED_KEYS))
