# Karlovich 2025: visual proof map

Eight executable notebooks turn specific questions in Karlovich (2025) into visual explanations. The notebook renderers generate the released GIF/MP4/PDF assets; two Manim entry points reuse their mathematical metadata.

| Notebook | Mathematical question | Default MP4 |
|---|---|---|
| `02_power_weights.ipynb` | How does the admissible exponent δ change `x^δ`? | 144 frames, 6 s |
| `03_log_transport.ipynb` | Why does `x=e^t` prepare Mellin convolution? | 168 frames, 7 s |
| `04_complex_conjugation.ipynb` | Why is `C f=bar f` real-linear? | 144 frames, 6 s |
| `05_cauchy_operator_action.ipynb` | What does a principal-value operator do to a Gaussian? | 158 frames, 6.58 s |
| `06_mellin_fourier.ipynb` | How does a function change through log transport, Fourier transform, multiplier and inverse? | 209 frames, 8.71 s |
| `07_branch_interactions.ipynb` | How do input `j` and output `k` determine CC/CR/RC/RR? | 406 frames, 16.92 s |
| `08_symbol_curve.ipynb` | What arc does the local scalar factor `μ_ν(x)` trace? | 72 frames, 6 s |
| `09_full_reduction_pipeline.ipynb` | Where does the finite Fredholm determinant become available? | 329 frames, 13.71 s |

Open a notebook from this project directory and run all cells with its `python3122` kernel. The first cell contains the user parameters. The renderers use NumPy, Matplotlib, Pillow and `ffmpeg`; the notebooks use Jupyter/IPython. The default videos use 24 fps except notebook 08's 12 fps symbol trace. Notebook 07 derives cusp and ray branches from (1.1), creates the `m×m` grid from `(k,j)`, and was checked with both `s=2,r=2` and `s=3,r=2`. Its `src/geometry.py`, `src/interactions.py` and `src/operator_metadata.py` are shared with the Manim Scene, so the grid and kernels are not duplicated as drawing coordinates.

## Mathematical scope

`visual_math_audit.md` records every exact kernel, compact model and operator class against Karlovich (2025), (3.6), Lemmas 3.1–3.2, Corollary 3.3, and (3.21)–(3.28). **Column `j` is input; row `k` is output.** The transport by `σ` is an exact isometry of function spaces; the picture mapping a branch to a horizontal copy of `R_+` is explicitly schematic. The compact model is introduced only after comparing exact kernels. The numerical Cauchy and Mellin/Fourier scenes illustrate operator action and are not parts of the proof.

The 09 route uses `src/full_pipeline_metadata.py` for twelve ordered stages: exact identities, model modulo compact operators, then local finite symbols. Equation (6.5) supplies the four strata of `Ω-hat`. The scalar `μ_ν` arc is only one local factor. The auxiliary symbol is `m×m`; the determinant in Theorem 7.2 is taken on the final finite `2m×2m` symbol of `N=A+BC`. The 09 renderer reuses PNGs from earlier notebooks, and exports `outputs/full_reduction_pipeline.pdf` as its Beamer fallback.

## Manim Scenes

The requested entry points are in `manim/`, with implementation in `src/`:

```bash
manim -pql manim/branch_interactions_scene.py BranchInteractionsScene
manim -pql manim/full_reduction_pipeline_scene.py FullReductionPipelineScene
```

`K25_S`, `K25_R` and `K25_SPEED_FACTOR` configure the branch scene; `K25_ASSET_DIR` and `K25_SPEED_FACTOR` configure the full route. Both Scenes were rendered with Manim Community 0.19.2 in a temporary environment and visually inspected. The 07 preview is `outputs/branch_interactions_manim_preview.mp4` (854×480, 15 fps, 345 frames, 23 s); `outputs/branch_interactions_manim_s3r2.png` records the successfully rendered five-branch variant. The 09 preview is `outputs/full_reduction_pipeline_manim_preview.mp4` (854×480, 15 fps, 409 frames, 27.27 s). Their final frames are the matching `_manim_preview.png` files. The 1024×576 notebook MP4s remain the media used in Beamer; the Manim files are separate Scene previews.

## Verification

The structural notebook validator and clean-kernel two-pass validator report `APROBADO` for notebooks 02–09: `verification_report_visuals.json` (02–04, 07), `verification_05_06_report.json`, the 08 report, and `verification_09_report.json`. The 05 Hilbert convention was independently checked against principal-value quadrature. The 06 FFT inverse and log-coordinate norm were numerically checked in both symbol modes. The MP4 dimensions, fps and frame counts were checked with `ffprobe`. The Beamer project receives copies of the final media in its `figures/` directory.
