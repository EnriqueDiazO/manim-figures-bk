"""Numerical Mellin/Fourier pipeline for a half-line test function.

The log-coordinate isometry E_nu and Fourier convention are explicit.
The smooth symbol is a numerical demo; paper_coth is the multiplier in
Karlovich (2025), (3.25), with its admissible shift 0<nu<1.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
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
class PipelineConfig:
    p: float = 2.0
    delta: float = 0.0
    t_min: float = -7.0
    t_max: float = 7.0
    n_grid: int = 1024
    sigma: float = 1.1
    symbol_mode: str = "smooth_demo"
    fps: int = 24
    stage_duration: float = 1.5
    hold_end: float = 1.2

    def __post_init__(self) -> None:
        if self.p <= 1 or not (-1/self.p < self.delta < 1-1/self.p):
            raise ValueError("Require p>1 and -1/p<delta<1-1/p.")
        if not self.t_min < 0 < self.t_max or self.n_grid < 256:
            raise ValueError("Use a log interval around 0 and at least 256 points.")
        if self.sigma <= 0 or self.fps < 1:
            raise ValueError("sigma and FPS must be positive.")
        if self.symbol_mode not in {"smooth_demo", "paper_coth"}:
            raise ValueError("SYMBOL_MODE must be smooth_demo or paper_coth.")
        if self.stage_duration <= 0 or self.hold_end <= 0:
            raise ValueError("Durations must be positive.")

    @property
    def nu(self) -> float:
        return 1/self.p+self.delta


@dataclass(frozen=True)
class PipelineData:
    x: np.ndarray
    t: np.ndarray
    lam: np.ndarray
    f: np.ndarray
    g: np.ndarray
    g_hat: np.ndarray
    multiplier: np.ndarray
    product: np.ndarray
    output_x: np.ndarray
    norm_relative_error: float
    inverse_relative_error: float


def compute_pipeline(config: PipelineConfig) -> PipelineData:
    t = np.linspace(config.t_min, config.t_max, config.n_grid,
                    endpoint=False)
    dt = float(t[1]-t[0])
    x = np.exp(t)
    g = np.exp(-.5*(t/config.sigma)**2)
    f = np.exp(-config.nu*t)*g
    lam = 2*np.pi*np.fft.fftshift(np.fft.fftfreq(config.n_grid, d=dt))
    g_hat = np.fft.fftshift(np.fft.fft(np.fft.ifftshift(g)))*dt
    inverse = np.fft.fftshift(np.fft.ifft(np.fft.ifftshift(g_hat)))/dt
    inverse_error = float(np.max(np.abs(inverse-g))/
                          max(1e-14, np.max(np.abs(g))))
    if inverse_error > 1e-11:
        raise AssertionError(f"Fourier inversion failed: {inverse_error:.3g}")
    if config.symbol_mode == "smooth_demo":
        multiplier = .20+.80*np.exp(-.5*(lam/.70)**2)
    else:
        multiplier = 1/np.tanh(np.pi*(lam+1j*config.nu))
    if not np.all(np.isfinite(multiplier)):
        raise FloatingPointError(
            "paper_coth produced nonfinite values; change admissible nu/grid.")
    product = multiplier*g_hat
    output_t = np.fft.fftshift(np.fft.ifft(np.fft.ifftshift(product)))/dt
    output_x = np.exp(-config.nu*t)*output_t
    norm_t = np.trapezoid(np.abs(g)**config.p, t)
    norm_x = np.trapezoid(np.abs(f*x**config.delta)**config.p, x)
    norm_error = float(abs(norm_x-norm_t)/norm_t)
    if norm_error > 1e-3:
        raise AssertionError(f"Log-coordinate norm check failed: {norm_error:.3g}")
    return PipelineData(
        x=x, t=t, lam=lam, f=f, g=g, g_hat=g_hat,
        multiplier=multiplier, product=product, output_x=output_x,
        norm_relative_error=norm_error,
        inverse_relative_error=inverse_error,
    )


def render_frame(config: PipelineConfig, data: PipelineData,
                 stage: int) -> plt.Figure:
    if not 0 <= stage <= 5:
        raise ValueError("stage must be 0..5.")
    fig = plt.figure(figsize=(12.8, 7.2), facecolor="white")
    fig.text(.055, .965, "MELLIN / FOURIER PIPELINE", color=COLORS["main"],
             fontsize=18, fontweight="bold", va="top")
    fig.text(.055, .907,
             r"$f(x)\ \to\ g(t)\ \to\ \widehat g(\lambda)"
             r"\ \to\ a(\lambda)\widehat g(\lambda)\ \to\ h(x)$",
             color=COLORS["ink"], fontsize=17, va="top")
    gs = fig.add_gridspec(
        2, 6, left=.055, right=.96, top=.77, bottom=.18,
        wspace=.75, hspace=.75)
    axes = [
        fig.add_subplot(gs[0, 0:2]),
        fig.add_subplot(gs[0, 2:4]),
        fig.add_subplot(gs[0, 4:6]),
        fig.add_subplot(gs[1, 1:3]),
        fig.add_subplot(gs[1, 3:5]),
    ]
    colors = [COLORS["geometry"], COLORS["transport"],
              COLORS["mellin"], COLORS["wiener"], COLORS["symbol"]]
    titles = ["1  INPUT $f(x)$", "2  LOG FUNCTION $g(t)$",
              "3  FOURIER $\\widehat g$", "4  MULTIPLIED $a\\widehat g$",
              "5  OUTPUT ON $\\mathrm{R}_+$"]
    for i, ax in enumerate(axes):
        ax.set_title(titles[i], loc="left", color=colors[i],
                     fontsize=13.2, fontweight="bold")
        ax.grid(color=COLORS["rule"], alpha=.22)
        ax.spines[["top", "right"]].set_visible(False)
        if i >= stage:
            ax.set_facecolor(COLORS["soft"])
            ax.text(.5, .5, "next step", transform=ax.transAxes,
                    ha="center", va="center", fontsize=13,
                    color=COLORS["muted"])
    if stage >= 1:
        axes[0].semilogx(data.x, data.f, lw=2.7, color=colors[0])
    if stage >= 2:
        axes[1].plot(data.t, data.g, lw=2.7, color=colors[1])
    if stage >= 3:
        axes[2].plot(data.lam, np.abs(data.g_hat), lw=2.7,
                     color=colors[2])
    if stage >= 4:
        axes[3].plot(data.lam, np.abs(data.product), lw=2.7,
                     color=colors[3])
    if stage >= 5:
        axes[4].semilogx(data.x, data.output_x.real, lw=2.7,
                         color=colors[4], label="Re")
        if np.max(np.abs(data.output_x.imag)) > 1e-4:
            axes[4].semilogx(data.x, data.output_x.imag, lw=2.1,
                             ls="--", color=COLORS["warning"], label="Im")
            axes[4].legend(frameon=False, fontsize=9, loc="upper right")
    for i, ax in enumerate(axes):
        if i in (0, 4):
            ax.set_xlim(np.exp(config.t_min), np.exp(config.t_max))
            ax.set_xlabel("$x$ (log scale)", fontsize=10.5)
        elif i == 1:
            ax.set_xlim(config.t_min, config.t_max)
            ax.set_xlabel("$t=\\log x$", fontsize=10.5)
        else:
            ax.set_xlim(-8, 8)
            ax.set_xlabel("$\\lambda$", fontsize=10.5)
        if i < 4:
            values = [data.f, data.g, np.abs(data.g_hat),
                      np.abs(data.product)][i]
            ax.set_ylim(-.06*float(np.max(values)),
                        1.15*float(np.max(values)))
        else:
            amplitude = max(float(np.max(np.abs(data.output_x.real))),
                            float(np.max(np.abs(data.output_x.imag))), .01)
            ax.set_ylim(-1.18*amplitude, 1.18*amplitude)
    if config.symbol_mode == "smooth_demo":
        symbol_note = (r"Numerical demo: $a(\lambda)=0.20+0.80e^{-(\lambda/0.70)^2/2}$."
                       r" Paper identity: $a_{\mathrm{K25}}(\lambda)="
                       r"\coth\pi(\lambda+i\nu)$.")
    else:
        symbol_note = (r"Paper multiplier (3.25): $a_{\mathrm{K25}}(\lambda)"
                       r"=\coth\pi(\lambda+i\nu)$; "
                       rf"$\nu={config.nu:.3f}$, $\max|a|="
                       rf"{float(np.max(np.abs(data.multiplier))):.3g}$.")
    fig.text(.055, .095, symbol_note, fontsize=11.2,
             color=COLORS["muted"])
    fig.text(.055, .055,
             r"$E_\nu f(t)=e^{\nu t}f(e^t)$; "
             r"$M^0(a)=E_\nu^{-1}\mathcal{F}^{-1}a\mathcal{F}E_\nu$."
             " Numerical illustration, not a proof.",
             fontsize=11.0, color=COLORS["muted"])
    return fig


def render_assets(config: PipelineConfig, output_dir: Path,
                  stem: str = "mellin_fourier_pipeline") -> dict[str, object]:
    data = compute_pipeline(config)
    output_dir.mkdir(parents=True, exist_ok=True)
    final = render_frame(config, data, 5)
    png, pdf = output_dir/f"{stem}.png", output_dir/f"{stem}.pdf"
    final.savefig(png, dpi=160)
    final.savefig(pdf, format="pdf")
    plt.close(final)
    sequence = []
    for stage in range(1, 6):
        sequence.extend([stage]*max(1, round(
            config.stage_duration*config.fps)))
    sequence.extend([5]*max(1, round(config.hold_end*config.fps)))
    with tempfile.TemporaryDirectory(prefix="k25-mellin-frames-") as directory:
        frames_dir = Path(directory)
        for index, stage in enumerate(sequence):
            fig = render_frame(config, data, stage)
            fig.savefig(frames_dir/f"frame-{index:05d}.png", dpi=80)
            plt.close(fig)
        mp4 = output_dir/f"{stem}.mp4"
        subprocess.run([
            "ffmpeg", "-y", "-loglevel", "error",
            "-framerate", str(config.fps), "-i",
            str(frames_dir/"frame-%05d.png"), "-c:v", "libx264",
            "-pix_fmt", "yuv420p", "-crf", "21",
            "-movflags", "+faststart", str(mp4)], check=True)
        gif = output_dir/f"{stem}.gif"
        stride = 2 if config.fps >= 18 else 1
        images = []
        for index in range(0, len(sequence), stride):
            with Image.open(frames_dir/f"frame-{index:05d}.png") as frame:
                images.append(frame.convert("RGB").quantize(colors=96))
        images[0].save(
            gif, save_all=True, append_images=images[1:],
            duration=round(1000*stride/config.fps), loop=0,
            optimize=False, disposal=2)
    return {"gif": gif, "mp4": mp4, "png": png, "pdf": pdf,
            "frames": len(sequence), "duration_seconds": len(sequence)/config.fps,
            "norm_relative_error": data.norm_relative_error,
            "inverse_relative_error": data.inverse_relative_error,
            "max_symbol_abs": float(np.max(np.abs(data.multiplier)))}


if __name__ == "__main__":
    for mode in ("smooth_demo", "paper_coth"):
        example = compute_pipeline(PipelineConfig(symbol_mode=mode))
        print(mode, "norm error", example.norm_relative_error,
              "FFT inverse error", example.inverse_relative_error)
