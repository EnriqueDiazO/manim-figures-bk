"""Parametric mixed cusp-ray star in Karlovich 2025, (1.1)-(1.2)."""

from __future__ import annotations

from dataclasses import dataclass
import numpy as np


@dataclass(frozen=True)
class BranchParameters:
    s: int
    r: int
    c_values: tuple[float, ...]
    beta_values: tuple[float, ...]
    p: float
    delta: float
    x_parameter_min: float = 1e-4
    x_parameter_max: float = 65.0
    n_geometry_points: int = 340

    def __post_init__(self) -> None:
        if not (1 <= self.s and 1 <= self.r and self.s + self.r <= 8):
            raise ValueError("Use positive s and r with m=s+r <= 8 for this visualization.")
        if len(self.c_values) != self.s or len(self.beta_values) != self.r:
            raise ValueError("len(c_values)=s and len(beta_values)=r are required.")
        if any(c == 0 for c in self.c_values) or any(
            b <= a for a, b in zip(self.c_values, self.c_values[1:])
        ):
            raise ValueError("c_values must be strictly increasing and nonzero.")
        if any(not (np.pi / 2 < beta < 3 * np.pi / 2) for beta in self.beta_values) or any(
            b <= a for a, b in zip(self.beta_values, self.beta_values[1:])
        ):
            raise ValueError("beta_values must increase strictly inside (pi/2, 3pi/2).")
        if self.p <= 1 or not (-1 / self.p < self.delta < 1 - 1 / self.p):
            raise ValueError("Require p>1 and -1/p<delta<1-1/p.")
        if not (0 < self.x_parameter_min < self.x_parameter_max) or self.n_geometry_points < 20:
            raise ValueError("Require 0<x_parameter_min<x_parameter_max and at least 20 samples.")

    @property
    def m(self) -> int:
        return self.s + self.r

    def kind(self, k: int) -> str:
        if not 1 <= k <= self.m:
            raise IndexError(k)
        return "C" if k <= self.s else "R"

    def interaction(self, k: int, j: int) -> str:
        """First letter is output row k; second is input column j."""
        return self.kind(k) + self.kind(j)

    def gamma(self, k: int, x: np.ndarray | float) -> np.ndarray | complex:
        """The k-th branch, oriented toward 0 as x increases."""
        x = np.asarray(x, dtype=float)
        if np.any(x <= 0):
            raise ValueError("The branch parameter x must be positive.")
        if k <= self.s:
            return 1.0 / (x - 1j * self.c_values[k - 1])
        return np.exp(1j * self.beta_values[k - self.s - 1]) / x


def default_c_values(s: int) -> tuple[float, ...]:
    """Illustrative valid values; no mathematical result depends on the sample."""
    n_negative = (s + 1) // 2
    n_positive = s - n_negative
    negatives = -np.linspace(1.45, 0.85, n_negative)
    positives = np.linspace(0.85, 1.45, n_positive)
    return tuple(float(v) for v in np.concatenate([negatives, positives]))


def default_beta_values(r: int) -> tuple[float, ...]:
    if r == 1:
        return (float(np.pi),)
    return tuple(float(v) for v in np.linspace(0.60 * np.pi, 1.40 * np.pi, r))


def branch_points(params: BranchParameters, k: int) -> np.ndarray:
    if params.kind(k) == "C":
        x = np.linspace(params.x_parameter_min, params.x_parameter_max,
                        params.n_geometry_points)
    else:
        # The ray is unbounded as x→0+.  Clip its displayed far end to the
        # fixed viewport while keeping the user range operative.
        x = np.geomspace(max(params.x_parameter_min, 0.60),
                         params.x_parameter_max, params.n_geometry_points)
    return np.asarray(params.gamma(k, x))


def cell_counts(params: BranchParameters) -> dict[str, int]:
    counts = {code: 0 for code in ("CC", "CR", "RC", "RR")}
    for k in range(1, params.m + 1):
        for j in range(1, params.m + 1):
            counts[params.interaction(k, j)] += 1
    return counts
