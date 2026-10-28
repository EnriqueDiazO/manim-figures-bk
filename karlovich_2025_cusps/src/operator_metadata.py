"""Exact transported kernels and compact models from Karlovich 2025.

Convention throughout: column j is input; row k is output.  The scalar kernel
below is defined so that T[k,j] phi_j(x) = (pi i)^(-1) integral K(x,tau) phi_j(tau) d tau.
The integral is principal value when k=j.  Exact entries are (3.6).  Models
and classes follow (3.21)-(3.28), Lemmas 3.1-3.2 and Corollary 3.3.
This module is shared by notebook, renderer and Manim scene.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Interaction:
    code: str
    input_j: str
    output_k: str
    exact_kernel: str
    model_kernel: str
    class_name: str
    source: str
    compact_note: str


INTERACTIONS: dict[str, Interaction] = {
    "CC": Interaction(
        "CC", r"j\leq s", r"k\leq s",
        r"\frac{1}{\tau+i(c_k-c_j)-x}",
        r"k=j:\ K^{\mathrm{ex}}_{k,j};\ k\ne j:\ \frac{\chi_\infty(x)\chi_\infty(\tau)}{\tau+i(c_k-c_j)-x}",
        "diagonal Mellin; off-diagonal localized Wiener–Hopf",
        "Karlovich 2025 exact (3.6); model (3.22), (3.24)-(3.28), Lemma 3.1, Corollary 3.3",
        "PV on the diagonal; the off-diagonal difference is compact",
    ),
    "CR": Interaction(
        "CR", r"j>s", r"k\leq s",
        r"\frac{e^{i\beta_j}}{\tau+i c_k e^{i\beta_j}-e^{i\beta_j}x}",
        r"\chi_\infty(x)\chi_\infty(\tau)\frac{e^{i\beta_j}}{\tau-e^{i\beta_j}x}",
        "localized Mellin convolution",
        "Karlovich 2025 exact (3.6); model (3.22), (3.24)-(3.28), Lemma 3.1, Corollary 3.3",
        "exact transported CR entry differs from this model by a compact operator",
    ),
    "RC": Interaction(
        "RC", r"j\leq s", r"k>s",
        r"\frac{e^{-i\beta_k}}{\tau-i c_j-e^{-i\beta_k}x}",
        r"\chi_\infty(x)\chi_\infty(\tau)\frac{e^{-i\beta_k}}{\tau-e^{-i\beta_k}x}",
        "localized Mellin convolution",
        "Karlovich 2025 exact (3.6); model (3.22), (3.24)-(3.28), Lemma 3.1, Corollary 3.3",
        "exact transported RC entry differs from this model by a compact operator",
    ),
    "RR": Interaction(
        "RR", r"j>s", r"k>s",
        r"\frac{e^{i(\beta_j-\beta_k)}}{\tau-e^{i(\beta_j-\beta_k)}x}",
        r"K^{\mathrm{ex}}_{k,j}",
        "Mellin convolution",
        "Karlovich 2025 exact (3.6); model (3.22), (3.24)-(3.28), Corollary 3.3",
        "no compact subtraction for this model; PV when k=j",
    ),
}


def interaction_table_markdown() -> str:
    head = (
        "| Interaction | input $j$ | output $k$ | exact $K^{\\rm ex}_{k,j}$ | "
        "compact model $K^{\\rm mod}_{k,j}$ | operator class | source |\n"
        "|---|---|---|---|---|---|---|"
    )
    rows = [head]
    for spec in INTERACTIONS.values():
        rows.append(
            f"| {spec.code} | ${spec.input_j}$ | ${spec.output_k}$ | "
            f"${spec.exact_kernel}$ | ${spec.model_kernel}$ | "
            f"{spec.class_name} | {spec.source} |"
        )
    return "\n".join(rows)


def selected_pair(code: str, s: int, r: int) -> tuple[int, int]:
    """Representative (k,j), always row output and column input."""
    if s < 1 or r < 1:
        raise ValueError("A mixed star needs at least one cusp and one ray branch.")
    return {
        "CC": (1, 1 if s == 1 else 2),
        "CR": (1, s + 1),
        "RC": (s + 1, 1),
        "RR": (s + 1, s + 1 if r == 1 else s + 2),
    }[code]
