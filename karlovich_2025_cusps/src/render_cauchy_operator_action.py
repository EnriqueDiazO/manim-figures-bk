"""Numerical Hilbert/Cauchy action on a Gaussian test function.

Hf(x) = (1/pi) PV integral_R f(t)/(x-t) dt; on the oriented real line
the paper's Cauchy convention gives Sf=iHf. This is an illustration.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import math
import subprocess
import tempfile

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
from visual_style import COLORS

plt.rcParams.update({"font.family": "STIXGeneral", "mathtext.fontset": "stix",
                     "pdf.fonttype": 42})


@dataclass(frozen=True)
class ActionConfig:
    x_min: float = -3.5
    x_max: float = 3.5
    n_plot: int = 701
    fps: int = 24
    hold_input: float = 1.0
    reveal_output: float = 2.8
    hold_comparison: float = 2.0
    hold_end: float = 0.8

    def __post_init__(self) -> None:
        if not self.x_min < 0 < self.x_max or self.n_plot < 101 or self.fps < 1:
            raise ValueError("Choose a plotted interval around zero, n>=101, FPS>=1.")
        if min(self.hold_input, self.reveal_output,
               self.hold_comparison, self.hold_end) <= 0:
            raise ValueError("Durations must be positive.")


def gaussian(x: np.ndarray | float) -> np.ndarray:
    return np.exp(-np.asarray(x, dtype=float) ** 2)


def dawson(x: np.ndarray | float, n: int = 30000) -> np.ndarray:
    """D(x)=exp(-x²) integral_0^x exp(u²)du, computed by trapezoids."""
    xx = np.asarray(x, dtype=float)
    u = np.linspace(0, max(float(np.max(np.abs(xx))), 1e-6), n)
    values = np.exp(u*u)
    cumulative = np.r_[0.0, np.cumsum(
        (values[1:] + values[:-1])*np.diff(u)/2.0)]
    return np.sign(xx)*np.exp(-xx*xx)*np.interp(np.abs(xx), u, cumulative)


def gaussian_hilbert(x: np.ndarray | float) -> np.ndarray:
    return (2.0/math.sqrt(math.pi))*dawson(x)


def pv_hilbert_at(x: float, truncation: float = 9.0,
                  n: int = 200001) -> float:
    """Independent finite-interval PV quadrature via singularity subtraction."""
    if not -truncation < x < truncation:
        raise ValueError("The PV sample must lie inside the interval.")
    tau = np.linspace(-truncation, truncation, n)
    fx = math.exp(-x*x)
    denominator = x-tau
    numerator = np.exp(-tau*tau)-fx
    integrand = np.divide(
        numerator, denominator, out=np.full_like(tau, 2*x*fx),
        where=np.abs(denominator)>1e-12)
    correction = fx*math.log((x+truncation)/(truncation-x))
    return float((np.trapezoid(integrand, tau)+correction)/math.pi)


def verify_normalization(tolerance: float = 2e-5) -> dict[str, float]:
    samples = np.array([-2., -1., -.5, 0., .5, 1., 2.])
    pv = np.array([pv_hilbert_at(float(x)) for x in samples])
    exact = gaussian_hilbert(samples)
    error = float(np.max(np.abs(pv-exact)))
    if error > tolerance or pv[4] <= 0 or pv[2] >= 0:
        raise AssertionError(
            f"Gaussian Hilbert normalization/sign failed: {error:.3g}")
    return {"max_abs_error": error, "tolerance": tolerance,
            "sample_count": int(samples.size)}


def render_frame(config: ActionConfig, progress: float) -> plt.Figure:
    if not 0 <= progress <= 1:
        raise ValueError("Progress must be in [0,1].")
    x = np.linspace(config.x_min, config.x_max, config.n_plot)
    f, h = gaussian(x), gaussian_hilbert(x)
    fig, (left, right) = plt.subplots(
        1, 2, figsize=(12.8, 7.2), dpi=80,
        gridspec_kw={"left": .07, "right": .95, "top": .73,
                     "bottom": .19, "wspace": .23})
    fig.patch.set_facecolor("white")
    fig.text(.07, .95, "WHAT DOES A SINGULAR INTEGRAL DO TO A FUNCTION?",
             fontsize=18, fontweight="bold", color=COLORS["main"], va="top")
    fig.text(.07, .865,
             r"$Hf(x)=\frac{1}{\pi}\operatorname{p.v.}\!\int_{\mathrm{R}}"
             r"\frac{f(\tau)}{x-\tau}\,d\tau$"
             r"       $S=iH$ for this orientation",
             fontsize=19, color=COLORS["ink"], va="top")
    fig.text(.07, .075,
             "NUMERICAL ILLUSTRATION · Gaussian input · not part of the proof",
             fontsize=11.5, color=COLORS["muted"])
    for ax in (left, right):
        ax.set_xlim(config.x_min, config.x_max)
        ax.set_ylim(-.75, 1.14)
        ax.axhline(0, color=COLORS["rule"], lw=1)
        ax.axvline(0, color=COLORS["rule"], lw=1)
        ax.grid(alpha=.18, color=COLORS["rule"])
        ax.set_xlabel("$x$", fontsize=13)
        ax.spines[["top", "right"]].set_visible(False)
    left.set_title("INPUT FUNCTION", loc="left", fontsize=16,
                   fontweight="bold", color=COLORS["geometry"])
    right.set_title("OUTPUT OF $H$", loc="left", fontsize=16,
                    fontweight="bold", color=COLORS["symbol"])
    left.plot(x, f, color=COLORS["geometry"], lw=3.4)
    left.text(.05, .87, r"$f(x)=e^{-x^2}$", transform=left.transAxes,
              fontsize=17, color=COLORS["geometry"])
    fig.text(.50, .46, r"$\longrightarrow$", fontsize=23, ha="center",
             color=COLORS["transport"])
    if progress > 0:
        count = max(2, int(round(config.n_plot*progress)))
        right.plot(x[:count], h[:count], color=COLORS["symbol"], lw=3.4)
        if progress >= .95:
            right.text(.05, .87, r"$Hf(x)=\frac{2}{\sqrt{\pi}}D(x)$",
                       transform=right.transAxes, fontsize=17,
                       color=COLORS["symbol"])
            right.text(.05, .76, r"$Sf(x)=iHf(x)$",
                       transform=right.transAxes, fontsize=15,
                       color=COLORS["symbol"])
    return fig


def render_assets(config: ActionConfig, output_dir: Path,
                  stem: str = "cauchy_operator_action") -> dict[str, object]:
    verify_normalization()
    output_dir.mkdir(parents=True, exist_ok=True)
    sequence = (
        [0.0]*max(1, round(config.hold_input*config.fps))
        + list(np.linspace(0, 1, max(2, round(config.reveal_output*config.fps))))
        + [1.0]*max(1, round(
            (config.hold_comparison+config.hold_end)*config.fps)))
    png, pdf = output_dir/f"{stem}.png", output_dir/f"{stem}.pdf"
    still = render_frame(config, 1.0)
    still.savefig(png, dpi=160, facecolor="white")
    still.savefig(pdf, format="pdf", facecolor="white")
    plt.close(still)
    with tempfile.TemporaryDirectory(prefix="k25-cauchy-frames-") as directory:
        frame_dir = Path(directory)
        for i, progress in enumerate(sequence):
            fig = render_frame(config, float(progress))
            fig.savefig(frame_dir/f"frame-{i:05d}.png", dpi=80,
                        facecolor="white")
            plt.close(fig)
        mp4 = output_dir/f"{stem}.mp4"
        subprocess.run([
            "ffmpeg", "-y", "-loglevel", "error", "-framerate",
            str(config.fps), "-i", str(frame_dir/"frame-%05d.png"),
            "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "21",
            "-movflags", "+faststart", str(mp4)], check=True)
        gif = output_dir/f"{stem}.gif"
        stride = 2 if config.fps >= 18 else 1
        images = []
        for i in range(0, len(sequence), stride):
            with Image.open(frame_dir/f"frame-{i:05d}.png") as frame:
                images.append(frame.convert("RGB").quantize(colors=96))
        images[0].save(
            gif, save_all=True, append_images=images[1:],
            duration=round(1000*stride/config.fps), loop=0,
            optimize=False, disposal=2)
    return {"gif": gif, "mp4": mp4, "png": png, "pdf": pdf,
            "frames": len(sequence),
            "duration_seconds": len(sequence)/config.fps}


if __name__ == "__main__":
    print("Hilbert normalization:", verify_normalization())
