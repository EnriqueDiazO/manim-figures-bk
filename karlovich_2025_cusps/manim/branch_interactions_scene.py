"""Manim entry point for the validated branch-interaction storyboard.

Mathematics and animation code live in ../src; this file exposes the Scene at
the requested manim/ path without duplicating branch formulas or cell logic.
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from manim_branch_interactions import BranchInteractionsScene as _BranchInteractionsScene  # noqa: E402


class BranchInteractionsScene(_BranchInteractionsScene):
    """Expose the canonical Scene to Manim's module-local discovery."""
