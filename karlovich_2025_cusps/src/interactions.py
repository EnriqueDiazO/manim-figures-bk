"""Algorithmic matrix classification: output row k, input column j."""

from __future__ import annotations

from dataclasses import dataclass
from geometry import BranchParameters


@dataclass(frozen=True)
class Cell:
    k: int
    j: int
    kind: str


def cells(params: BranchParameters) -> tuple[Cell, ...]:
    return tuple(
        Cell(k, j, params.interaction(k, j))
        for k in range(1, params.m + 1)
        for j in range(1, params.m + 1)
    )


def index_caption(code: str, params: BranchParameters) -> tuple[str, str]:
    """Human-readable j input range and k output range for a class."""
    if code not in {"CC", "CR", "RC", "RR"}:
        raise ValueError(code)
    j = f"j = 1,...,{params.s}" if code[1] == "C" else f"j = {params.s+1},...,{params.m}"
    k = f"k = 1,...,{params.s}" if code[0] == "C" else f"k = {params.s+1},...,{params.m}"
    return j, k


def count_by_class(params: BranchParameters) -> dict[str, int]:
    counts = {code: 0 for code in ("CC", "CR", "RC", "RR")}
    for cell in cells(params):
        counts[cell.kind] += 1
    return counts
