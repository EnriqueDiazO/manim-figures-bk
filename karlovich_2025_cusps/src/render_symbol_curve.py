#!/usr/bin/env python3
"""Render the Fredholm lens from Karlovich (2025), equations (5.5), (5.7), (6.5).

The curve is generated from mu_nu(x) = (1 + coth(pi (x + i nu))) / 2.
The chosen stratum determines which nu is mathematically relevant.
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
import subprocess
import tempfile

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image

try:
    from visual_style import COLORS
except ModuleNotFoundError:
    COLORS = {
        "mellin": "#B13F91", "symbol": "#684CAE",
        "main": "#1C375A", "muted": "#586069", "rule": "#CDD3DA",
    }


STRATUM_TITLES = {
    "zero_fiber": "zero fiber",
    "finite_t": "finite t",
    "infinity_finite_eta": "infinity fiber, finite eta",
    "infinity_endpoint": "infinity fiber, endpoints",
}


@dataclass(frozen=True)
class SymbolCurveParams:
    p: float = 2.0
    delta: float = -0.15
    stratum: str = "zero_fiber"
    marker_x: float = 0.4
    x_extent: float = 3.5
    frames: int = 72
    fps: int = 12
    show_reflection: bool = True

    def validate(self) -> None:
        if not self.p > 1:
            raise ValueError("p must be greater than 1")
        if not -1 / self.p < self.delta < 1 - 1 / self.p:
            raise ValueError("delta must lie in (-1/p, 1-1/p)")
        if self.stratum not in STRATUM_TITLES:
            raise ValueError(f"unknown stratum: {self.stratum}")
        if not np.isfinite(self.marker_x):
            raise ValueError("marker_x must be finite")
        if not self.x_extent > 1:
            raise ValueError("x_extent must be greater than 1")
        if self.frames < 12 or self.fps < 1:
            raise ValueError("frames must be >= 12 and fps >= 1")
        nu = self.nu
        if not 0 < nu < 1:
            raise ValueError("the selected nu must lie in (0,1)")

    @property
    def nu(self) -> float:
        if self.stratum == "finite_t":
            return 1 / self.p
        return 1 / self.p + self.delta

    @property
    def reflected_nu(self) -> float:
        return 1 - self.nu

    @property
    def interpretation(self) -> str:
        if self.stratum == "finite_t":
            return ("Theorem 5.1 uses L_(1/p). On the final domain (6.5), "
                    "the S and CSC symbols at finite t have no x-dependence.")
        if self.stratum == "infinity_endpoint":
            return ("The final stratum fixes x = -infinity or +infinity; "
                    "only endpoint values 0 and 1 are relevant.")
        if self.stratum == "infinity_finite_eta":
            return ("Theorem 5.1 uses L_(1/p+delta) after the reflection "
                    "identity (5.6); the original whole-line form uses "
                    "L_(1/q-delta). The final symbol retains x.")
        return ("The final zero-fiber symbol uses x in extended R and "
                "nu = 1/p + delta.")


def mu_nu(x: np.ndarray | float, nu: float) -> np.ndarray:
    """Equation (5.5), evaluated stably on a finite x grid."""
    if not 0 < nu < 1:
        raise ValueError("nu must lie in (0,1)")
    z = np.asarray(x, dtype=float) + 1j * nu
    return 0.5 * (1 + np.cosh(np.pi * z) / np.sinh(np.pi * z))


def verify_identity(params: SymbolCurveParams) -> dict[str, float]:
    """Numerically check (5.6) and asymptotic endpoints."""
    params.validate()
    sample = np.linspace(-2.5, 2.5, 17)
    lhs = mu_nu(-sample, params.nu)
    rhs = 1 - mu_nu(sample, params.reflected_nu)
    error = float(np.max(np.abs(lhs - rhs)))
    left = float(abs(mu_nu(-8.0, params.nu)))
    right = float(abs(mu_nu(8.0, params.nu) - 1))
    if error > 1e-11 or max(left, right) > 1e-10:
        raise AssertionError((error, left, right))
    return {"reflection_error": error, "left_endpoint_error": left,
            "right_endpoint_error": right}


def _build_figure(params: SymbolCurveParams):
    nu = params.nu
    xs = np.linspace(-params.x_extent, params.x_extent, 700)
    vals = mu_nu(xs, nu)
    fig, ax = plt.subplots(figsize=(8, 5), dpi=120)
    fig.patch.set_facecolor("white")
    fig.subplots_adjust(left=.11, right=.97, top=.82, bottom=.20)
    ax.set_facecolor("white")
    ax.axhline(0, color=COLORS["rule"], lw=1.2, zorder=0)
    ax.axvline(0, color=COLORS["rule"], lw=1.2, zorder=0)

    if params.stratum != "infinity_endpoint":
        ax.plot(vals.real, vals.imag, color=COLORS["mellin"], lw=3.3,
                zorder=2)
        ax.text(.48, float(vals.imag[np.argmin(np.abs(xs))]) +
                (.025 if nu < .5 else -.04),
                rf"$\mathcal{{L}}_{{{nu:.2f}}}$", ha="center",
                fontsize=12, color=COLORS["mellin"])
        if params.show_reflection and abs(nu - .5) > 1e-9:
            reflected = mu_nu(xs, params.reflected_nu)
            ax.plot(reflected.real, reflected.imag, color=COLORS["symbol"],
                    lw=1.9, ls="--", alpha=.75, zorder=1)
            ax.text(.5, float(reflected.imag[np.argmin(np.abs(xs))]) +
                    (.025 if params.reflected_nu < .5 else -.04),
                    rf"$\mathcal{{L}}_{{{params.reflected_nu:.2f}}}$",
                    ha="center", fontsize=12, color=COLORS["symbol"])
    else:
        ax.plot([0, 1], [0, 0], color=COLORS["rule"], lw=1.4, ls="--", zorder=1)

    ax.scatter([0, 1], [0, 0], s=90, color=COLORS["main"], zorder=4)
    ax.annotate("0  ($x=-\\infty$)", (0, 0), xytext=(8, 10),
                textcoords="offset points", fontsize=11, color=COLORS["main"])
    ax.annotate("1  ($x=+\\infty$)", (1, 0), xytext=(-105, 10),
                textcoords="offset points", fontsize=11, color=COLORS["main"])

    mark = ax.scatter([], [], s=170, facecolor="white",
                      edgecolor=COLORS["mellin"], linewidth=3, zorder=5)
    status = ax.text(.99, .97, "", transform=ax.transAxes, ha="right", va="top",
                     fontsize=13, color=COLORS["main"],
                     bbox={"boxstyle": "round,pad=.32", "fc": "white",
                           "ec": COLORS["rule"]})

    immax = float(np.max(np.abs(vals.imag)))
    ylim = max(.16, immax + .06)
    ax.set_xlim(-.08, 1.08)
    ax.set_ylim(-ylim, ylim)
    ax.set_aspect("equal", adjustable="box")
    ax.set_xlabel(r"$\Re\,\mu_\nu(x)$", fontsize=13, color=COLORS["main"])
    ax.set_ylabel(r"$\Im\,\mu_\nu(x)$", fontsize=13, color=COLORS["main"])
    ax.tick_params(labelsize=11, colors=COLORS["muted"])
    ax.grid(color=COLORS["rule"], alpha=.35)
    for spine in ax.spines.values():
        spine.set_color(COLORS["rule"])

    fig.suptitle(rf"Fredholm lens $\mathcal{{L}}_\nu$  ·  {STRATUM_TITLES[params.stratum]}",
                 fontsize=17, color=COLORS["main"], fontweight="bold", y=.96)
    fig.text(.11, .045, rf"$\mu_\nu(x)=\frac{{1+\coth[\pi(x+i\nu)]}}{{2}}$"
             + rf"   ·   $p={params.p:g}$, $\delta={params.delta:+.2f}$, $\nu={nu:.2f}$"
             + "   ·   Karlovich (5.5), (5.7), (6.5)",
             fontsize=11, color=COLORS["muted"])
    return fig, mark, status


def _set_marker(mark, status, params: SymbolCurveParams, x: float) -> None:
    if np.isneginf(x):
        point, label = 0 + 0j, r"$x=-\infty$"
    elif np.isposinf(x):
        point, label = 1 + 0j, r"$x=+\infty$"
    else:
        point = complex(mu_nu(x, params.nu))
        label = rf"$x={x:+.2f}$"
    mark.set_offsets(np.array([[point.real, point.imag]]))
    status.set_text(label)


def render_assets(params: SymbolCurveParams, output_dir: Path,
                  basename: str = "fredholm_symbol_curve") -> dict[str, Path]:
    """Export vector PDF, PNG, animated GIF and MP4 from the same formula."""
    params.validate()
    verify_identity(params)
    if not basename.replace("_", "").isalnum():
        raise ValueError("basename must contain only letters, digits and underscores")
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    paths = {ext: output_dir / f"{basename}.{ext}"
             for ext in ("pdf", "png", "gif", "mp4")}

    fig, mark, status = _build_figure(params)
    _set_marker(mark, status, params, params.marker_x)
    fig.savefig(paths["pdf"])
    fig.savefig(paths["png"], dpi=120)

    if params.stratum == "infinity_endpoint":
        xs = np.array([-np.inf if k % 2 == 0 else np.inf
                       for k in range(params.frames)])
    else:
        xs = np.linspace(-params.x_extent, params.x_extent, params.frames)

    with tempfile.TemporaryDirectory(prefix="symbol_curve_", dir=output_dir) as work:
        frame_dir = Path(work)
        frame_paths = []
        for i, x in enumerate(xs):
            _set_marker(mark, status, params, float(x))
            frame_path = frame_dir / f"frame_{i:04d}.png"
            fig.savefig(frame_path, dpi=120)
            frame_paths.append(frame_path)
        images = [Image.open(path).convert("RGB") for path in frame_paths]
        try:
            images[0].save(paths["gif"], save_all=True, append_images=images[1:],
                           duration=round(1000 / params.fps), loop=0,
                           optimize=False)
        finally:
            for im in images:
                im.close()
        command = [
            "ffmpeg", "-y", "-v", "error", "-framerate", str(params.fps),
            "-i", str(frame_dir / "frame_%04d.png"),
            "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "20",
            str(paths["mp4"]),
        ]
        subprocess.run(command, check=True, capture_output=True, text=True)
    plt.close(fig)
    return paths


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path,
                        default=Path(__file__).resolve().parents[1] / "outputs")
    parser.add_argument("--basename", default="fredholm_symbol_curve")
    parser.add_argument("--p", type=float, default=2.0)
    parser.add_argument("--delta", type=float, default=-0.15)
    parser.add_argument("--stratum", choices=STRATUM_TITLES,
                        default="zero_fiber")
    parser.add_argument("--marker-x", type=float, default=.4)
    parser.add_argument("--frames", type=int, default=72)
    parser.add_argument("--fps", type=int, default=12)
    args = parser.parse_args()
    params = SymbolCurveParams(p=args.p, delta=args.delta,
                               stratum=args.stratum, marker_x=args.marker_x,
                               frames=args.frames, fps=args.fps)
    print(params.interpretation)
    print(verify_identity(params))
    for kind, path in render_assets(params, args.output_dir, args.basename).items():
        print(f"{kind}: {path}")


if __name__ == "__main__":
    main()
