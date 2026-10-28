"""Deterministic GIF/MP4/vector-PDF export for the short teaching animations."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import shutil
import subprocess
import tempfile
from typing import Callable

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from PIL import Image


PDF_META = {
    "Author": "Enrique Diaz Ocampo",
    "Creator": "karlovich_2025_cusps animation renderer",
    "CreationDate": datetime(2000, 1, 1, tzinfo=timezone.utc),
    "ModDate": datetime(2000, 1, 1, tzinfo=timezone.utc),
}


def export_animation(
    frame_drawer: Callable[[int, int], plt.Figure],
    static_drawer: Callable[[], plt.Figure],
    output_dir: Path,
    stem: str,
    *,
    frames: int,
    fps: int,
    review_drawers: dict[str, Callable[[], plt.Figure]] | None = None,
    dpi: int = 80,
) -> dict[str, Path | float | int]:
    if frames < 2 or fps < 1 or Path(stem).name != stem:
        raise ValueError("frames >= 2, fps >= 1, and a simple output stem are required")
    output_dir.mkdir(parents=True, exist_ok=True)
    review_dir = output_dir / "review_frames"
    review_dir.mkdir(exist_ok=True)

    static_fig = static_drawer()
    pdf = output_dir / f"{stem}_static.pdf"
    png = output_dir / f"{stem}.png"
    static_fig.savefig(pdf, format="pdf", metadata=PDF_META)
    static_fig.savefig(png, format="png", dpi=160)
    plt.close(static_fig)

    for name, drawer in (review_drawers or {}).items():
        fig = drawer()
        fig.savefig(review_dir / f"{name}.png", format="png", dpi=120)
        plt.close(fig)

    with tempfile.TemporaryDirectory(prefix=f"{stem}-frames-") as tmp:
        folder = Path(tmp)
        for index in range(frames):
            fig = frame_drawer(index, frames)
            fig.savefig(folder / f"frame-{index:05d}.png", format="png", dpi=dpi)
            plt.close(fig)

        mp4 = output_dir / f"{stem}.mp4"
        subprocess.run([
            "ffmpeg", "-y", "-loglevel", "error", "-framerate", str(fps),
            "-i", str(folder / "frame-%05d.png"), "-c:v", "libx264",
            "-pix_fmt", "yuv420p", "-crf", "21", "-movflags", "+faststart",
            str(mp4),
        ], check=True)

        gif = output_dir / f"{stem}.gif"
        stride = 2 if fps >= 18 else 1
        images = []
        for index in range(0, frames, stride):
            with Image.open(folder / f"frame-{index:05d}.png") as im:
                images.append(im.convert("RGB").quantize(colors=96))
        images[0].save(gif, save_all=True, append_images=images[1:],
                       duration=int(round(1000 * stride / fps)), loop=0,
                       optimize=False, disposal=2)

    return {"gif": gif, "mp4": mp4, "png": png, "pdf": pdf,
            "frames": frames, "fps": fps, "duration_seconds": frames / fps}
