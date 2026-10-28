"""Manim entry point for the verified twelve-stage Fredholm route.

The stages and source references are defined once in ../src and reused by the
notebook renderer and this Scene.
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from manim_full_reduction_pipeline import FullReductionPipelineScene as _FullReductionPipelineScene  # noqa: E402


class FullReductionPipelineScene(_FullReductionPipelineScene):
    """Expose the canonical Scene to Manim's module-local discovery."""
