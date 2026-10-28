# Branch interaction checkpoint

Source: Karlovich (2025), (1.1)–(1.2), (3.6), Lemmas 3.1–3.2, Corollary 3.3 and (3.21)–(3.28). Let `m=s+r`, with cusp indices `1,…,s` and ray indices `s+1,…,m`. **Column `j` is the input branch; row `k` is the output branch.** Thus `(σS_Γσ⁻¹ φ)_k=Σ_j T_{kj}φ_j`. In the labels below, C means *cusp* and R means *ray*, while `C f=\bar f` elsewhere denotes complex conjugation.

Every exact entry has the form

`(T_{kj}φ_j)(x) = (1/(π i)) ∫₀^∞ φ_j(τ) K^{exact}_{kj}(x,τ) dτ`,

with principal value on the diagonal. In the table, `χχ` abbreviates `χ_∞(x)χ_∞(τ)`; the factor `1/(π i)` and integral are common to exact and model kernels.

| Interaction | Input `j` | Output `k` | Exact kernel `K^{exact}_{kj}` in (3.6) | Compact model kernel in (3.22) | Operator class from (3.24)–(3.28) | Source |
|---|---|---|---|---|---|---|
| CC | `1≤j≤s` | `1≤k≤s` | `1/[τ+i(c_k−c_j)−x]` (PV if `k=j`) | if `k=j`: `1/(τ−x)`; if `k≠j`: `χχ/[τ+i(c_k−c_j)−x]` | diagonal Mellin convolution (`M⁰(coth)`); off diagonal localized Wiener–Hopf | (3.6), (3.22), (3.24)–(3.25), (3.27) |
| CR | `s<j≤m` | `1≤k≤s` | `e^{iβ_j}/[τ+i c_k e^{iβ_j}−e^{iβ_j}x]` | `χχ e^{iβ_j}/[τ−e^{iβ_j}x]` | cutoff Mellin type (`R_{β_j}`) | (3.6), (3.22), (3.26)–(3.27) |
| RC | `1≤j≤s` | `s<k≤m` | `e^{−iβ_k}/[τ−i c_j−e^{−iβ_k}x]` | `χχ e^{−iβ_k}/[τ−e^{−iβ_k}x]` | cutoff Mellin type (`R_{2π−β_k}` after phase convention) | (3.6), (3.22), (3.26)–(3.27) |
| RR | `s<j≤m` | `s<k≤m` | `e^{i(β_j−β_k)}/[τ−e^{i(β_j−β_k)}x]` (PV if `k=j`) | same as exact | Mellin convolution; diagonal `M⁰(coth)` | (3.6), (3.22), (3.25)–(3.27) |

The exact transport is `σS_Γσ⁻¹=[T_{kj}]`. Corollary 3.3 says

`σS_Γσ⁻¹ = [S_{kj}] + K`, with `K` compact.

Write `A ≃ B` **only** when `A−B` is compact. This is the passage from the exact transported operator to the model matrix. The Fredholm symbol comes **after** this passage and lives on the reduced domain `\widehat\Omega` of (6.5); Theorems 6.2 and 7.2 then use finite `m×m` and `2m×2m` complex matrices, respectively. A determinant is never assigned directly to `[S_{kj}]` as an operator matrix.

## Comparison with the existing TikZ storyboard

`../haseman-candidacy-2026/figures/transported-block-matrix.tex` shows the useful composition: transported operator, indexed matrix, branch input/output direction. That drawing is for a **pure cusp** Haseman presentation: it marks diagonal entries as Mellin and the remaining entries as Wiener–Hopf. It does not specify the mixed-star CR, RC, RR formulas required here. Thus the new animation keeps its compositional logic but derives the four interaction types from the index predicates `k≤s` and `j≤s`, and its kernel labels from Karlovich (2025), (3.6). No claim about mixed-star kernels is imported from the TikZ.

The local thesis transcription `secciones/03_Metodologia.tex`, lines 317–319, appears to put `+i(c_k−c_j)` in the off-diagonal CC denominator for the **CSC compact model**. Karlovich (2025), (3.23), uses `−i(c_k−c_j)` at that place. The animation of `S` follows (3.6)/(3.22); any later CSC visual must follow the article's (3.23), not the local transcription. This discrepancy is recorded so the sign is never changed silently.

## Three levels shown in the animation

1. **Exact transport:** `T_{kj}=\Upsilon_k S_{\Gamma_j}\Upsilon_j^{-1}` and `σS_Γσ⁻¹=[T_{kj}]`, article (3.6).
2. **Compact model:** `σS_Γσ⁻¹=[S_{kj}]+K`, `K∈\mathcal K`, article Corollary 3.3 and (3.21)–(3.23).
3. **Operator representation and symbol:** (3.24)–(3.28) place the models in the Wiener–Hopf/Mellin algebra; the finite Fredholm symbol is evaluated over `\widehat\Omega` from (6.5), using Theorems 6.2 and 7.2.

## Full reduction animation and visual scope

`09_full_reduction_pipeline.ipynb` and its Manim Scene use one ordered table of twelve stages in `src/full_pipeline_metadata.py`: six exact definitions/identities, two model stages after compact reduction, and four local-symbol stages. The first six include the exact complex-linear lift `\widetilde N=\Theta(A+BC)` from (7.2)–(7.4), the isometry (3.5), and the exact transported matrix (3.6). The model equality with compact `K` is a separate stage. The Wiener–Hopf/Mellin classes are then read from (3.24)–(3.28), before entering the four strata of `\widehat\Omega` in (6.5). The auxiliary `m×m` symbol of Theorem 6.2 and final `2m×2m` symbol of Theorem 7.2 are distinct stages; `\Theta(aI)=\operatorname{diag}(aI,\overline a I)` keeps the conjugate second diagonal.

The reused conjugation PNG reflects values of `f(t)` and does not deform `\Gamma`. The reused Mellin/Fourier PNG is a numerical operator-action illustration and does not prove compactness. The `\mu_\nu` PNG is one scalar local arc at the zero fiber, not the entire `m×m` symbol or the domain `\widehat\Omega`. The `\Gamma_k\mapsto\mathbb R_+` drawing represents the exact isometric transport **schematically**. The final determinant is the ordinary determinant of `\mathcal Y(N)(\omega)\in M_{2m}(\mathbb C)` for `\omega\in\widehat\Omega`, never of an operator-valued matrix.

The Manim branch Scene was rendered at `s=2,r=2` and `s=3,r=2`; the latter produced the indexed `5×5` matrix with nine CC, six CR, six RC, and four RR entries. Its full video was inspected at the CC/CR/RC/RR kernel stages. The notebook export supplies the Beamer MP4/PDF; the Scene preview is a separate artifact.
