# Vortex-Thread Motion

A Navier-Stokes Benchmark and a Compression Hypothesis

Aaron Michael Weis | OneiroNexus
ORCID: 0009-0002-1906-148X
Research edition 1.0.0 | November 26, 2026

### Abstract

Can a compact description of motion help encode a changing geometry? This paper develops a reproducible starting point for that question. It derives a known decaying two-dimensional Taylor-Green solution, checks passive-trajectory integration against exact segment widths, and measures reversible baseline transforms on five external velocity-snapshot fixtures. Fresh tests recover second-order centered-difference behavior and approximately fourth-order Runge-Kutta behavior over the tested refinements. All 18 compressed packets reconstruct their canonical binary64 targets byte-for-byte. Plain XZ gives the smallest packets in the measured panel; previous-file XOR improves gzip on the all-column target but worsens every velocity-only comparison. The results support a verification harness and a bounded baseline experiment. They do not demonstrate a successful flow-based compressor or physical sphere-to-torus evolution. A previously described authored 3D replay remains outside the reproduced evidence because its original stream and decoder were not supplied for this edition. The paper specifies what a subsequent held-out flow-prediction experiment must measure.

### What this edition contributes

The contribution is a transparent research package: an independently checked derivation, executable numerical diagnostics, bit-exact baseline coding, source-linked figures, and explicit boundaries between completed checks and proposed experiments. The Taylor-Green field and predictive residual coding are established methods [1,7-10]. This paper makes no new-solution or codec-priority claim.

### Three distinct questions

First, does the stated field satisfy the equations, and does the trajectory integrator converge? Second, which simple reversible transforms help on a defined external fixture? Third, can a physically informed predictor outperform strong baselines on unseen runs? The first two receive fresh evidence here. The third remains a research hypothesis.

Code, numerical reports, figures and this manuscript are versioned together. AI assistance is disclosed on page 7. This is a technical preprint with internal computational review; no independent human peer review is claimed.


---

## 1. The exact field

Use dimensionless coordinates on the periodic square [0, 2π)², unit density, constant kinematic viscosity ν ≥ 0, and no forcing. Pressure is kinematic pressure. The equations and chosen stream-function convention are

∂ₜu + (u · ∇)u = -∇p + νΔu,       ∇ · u = 0,
ψ = A(t) cos x cos y,       u = (-∂ᵧψ, ∂ₓψ).

Writing u = (u₁,u₂) gives the velocity and a zero-spatial-mean pressure:

u = A(t)(cos x sin y, -sin x cos y),
p = -A(t)²[cos(2x) + cos(2y)]/4.                                  (1)

An arbitrary spatially constant C(t) can be added to p. Direct differentiation gives ∂ₓu₁ = -A sin x sin y and ∂ᵧu₂ = A sin x sin y, so divergence vanishes. The velocity Laplacian is Δu = -2u. The convective term and pressure gradient are

(u · ∇)u = -(A²/2)(sin 2x, sin 2y),
∇p = (A²/2)(sin 2x, sin 2y).                                      (2)

The nonlinear term is canceled by -∇p. The remaining equation is A′ = -2νA. Taking A(0) = 1 gives A(t) = exp(-2νt). This derives the known field in the phase convention used here. It neither introduces a new Navier-Stokes solution nor proves the accuracy of an unrelated numerical solver [1].

### Invariants, strain and normalization

For passive paths, dX/dt = u(X,t), the scalar q(x,y) = cos x cos y obeys u · ∇q = 0. Its value stays constant along an exact path, although ψ = A(t)q changes with time when ν > 0. The vorticity is ω = ∂ₓu₂ - ∂ᵧu₁ = -2A cos x cos y.

E = mean(|u|²)/2 = A²/4,       Z = mean(ω²)/2 = A²/2,
dE/dt = -4νE = -2νZ.                                              (3)

Here mean denotes a spatial mean. Domain-integrated energy and enstrophy multiply these values by 4π². The symmetric strain tensor is diag(-A sin x sin y, A sin x sin y), with zero trace. Material deformation F satisfies F′ = (∇u)F and det F = 1 in the exact flow. Directional stretching can therefore coexist with area preservation.


---

## 2. A segment with a known answer

Start two horizontal segments with endpoints x = π/2 ± δ₀, using δ₀ = 0.10. Put one at y = +π/2 and the other at y = -π/2 (equivalently 3π/2). Their centers are stationary. On these lines the transverse velocity vanishes, while the positive endpoint half-width contracts or expands according to

dδ/ds = -sin δ  at y = +π/2;     dδ/ds = +sin δ  at y = -π/2,
s(t) = ∫₀ᵗ A(r)dr = [1 - exp(-2νt)]/(2ν)  for ν > 0;  s = t for ν = 0.

Separating variables yields exact full widths. Coordinates are kept unwrapped so that crossing a periodic display seam does not create a false length jump.

L±(t) = 4 arctan[tan(δ₀/2) exp(±s(t))].                          (4)

For ν = 0.25 and t = 2 ln 2, A = 0.5 and s = 1. The initial widths are both 0.20; the contracting width is 0.0736289459135128 and the expanding width is 0.5407906651876966. The signs and values were independently recalculated in this review.

![Scientific figure](../figures/field-and-segments.png)

Figure 1. Left: samples of the exact field, not a numerical PDE solution. Right: the closed-form segment widths at ν = 0.25. Curves come from equation (4); the initial geometry and all units are dimensionless.

### What a visible thread represents

These segments are material curves transported by the in-plane velocity. They are not vortex lines: this two-dimensional field has vorticity normal to the plane. A short line can contract while nearby directions expand. Neither this demonstration nor a prescribed three-dimensional morph establishes physical creation of a hole.


---

## 3. Fresh numerical verification

The harness checks the known field, parameter boundaries, passive RK4 paths, deformation and reversible coding. Twenty unittest methods and eight separately counted numerical checks passed on Windows (Python 3.12.14, NumPy 2.3.5). The saved report includes sample points and thresholds.

![Scientific figure](../figures/numerical-convergence.png)

Figure 2. Pointwise centered-difference diagnostics at ν = 0.25 and t = 0.7 (four stated points), with h = dt. The right panel compares exact segment widths and generic paths against an 8,192-step RK4 reference. The latter reference shares the integrator and is not an exact generic trajectory.

| At 64 RK4 steps | Maximum absolute error |
| --- | --- |
| Contracting exact width | 5.278e-11 |
| Expanding exact width | 3.663e-10 |
| Generic paths vs refined RK4 | 4.860e-10 |
| First-integral drift | 1.700e-10 |
| Material det F minus 1 | 6.137e-10 |

Halving h from 0.20 through 0.025 reduced the maximum sampled momentum residual from 5.08×10⁻³ to 8.00×10⁻⁵, with orders 1.991, 1.998 and 1.999. Exact-segment errors approached fourth order over 8, 16, 32 and 64 RK4 steps. Invariant and deformation errors met the 10⁻⁸ thresholds at 64 steps.

Finite-difference divergence is particularly small because this field and matched centered stencils cancel algebraically. That value alone is not a broad solver-quality metric. A wrong-pressure negative control was detected. The command refuses an existing output directory and fails when checks are skipped.

Evidence boundary: this is verification of field evaluation, derivative stencils and trajectory integration. No velocity/pressure PDE discretization is evolved. A future CFD implementation must demonstrate its own spatial and temporal refinement, stability, boundary handling and conservation.


---

## 4. A byte-exact snapshot control

Five TSI Insight .vec fixtures were fetched from a fixed PIVPy commit [6]. Git blob identities and SHA-256 hashes were verified. Each file contains 3,969 rows and five numeric columns: X, Y, U, V and CHC. Parsing these 99,225 tokens as C-order little-endian binary64 gives 793,800 bytes. A velocity-only target gives 317,520 bytes. Headers and original decimal spelling are excluded; signed zero is retained. No CHC filtering is applied.

The reversible transforms are none, XOR with the same point in the previous file, and XOR with the previous point in each file. The first file or point is stored without a predecessor. XOR acts on uint64 representations, not on floating-point differences. Sequential XOR inversion exactly recovers each target word, including special IEEE-754 bit patterns tested separately.

| Target / codec | No transform | Prior-file XOR | Prior-point XOR |
| --- | --- | --- | --- |
| All columns / gzip | 337,927 | 314,186 | 347,471 |
| All columns / bz2 | 201,120 | 292,438 | 321,258 |
| All columns / lzma | 165,896 | 271,401 | 289,362 |
| Velocity / gzip | 219,464 | 273,189 | 285,399 |
| Velocity / bz2 | 161,457 | 275,800 | 289,256 |
| Velocity / lzma | 147,460 | 258,881 | 278,750 |

Table 2. Complete packet bytes, including magic, dimensions, type/order, transform, checksum and compressed body. Gzip uses level 6, bz2 level 9 and XZ/LZMA preset 6. Shared decoder and runtime are excluded consistently. The raw targets differ and should not be compared as equivalent payloads.

![Scientific figure](../figures/snapshot-packet-sizes.png)

Figure 3. Zero-based packet-size comparison from the saved JSON. All 18 packets decoded byte-for-byte. An independent standard-library checker reconstructed both targets directly from the source fixtures and separately decoded every packet.


---

## 5. What the results mean

### The simplest transform did not win generally

XZ without an XOR transform produced the smallest packet for both targets: 165,896 bytes for all columns and 147,460 bytes for velocity alone. Previous-file XOR reduced gzip size by 7.03% on all columns, but worsened every velocity-only comparison. Repeated spatial coordinates and CHC values affect the all-column result. These observations argue for comparing a proposed predictor with several fair baselines rather than assuming that motion structure must improve a compressor.

The fixtures are ordered by filename. Their acquisition headers do not establish the time between files. Previous-file XOR is therefore a file-order baseline, not a demonstrated temporal predictor. The velocity values are unfiltered: CHC counts across the five files are -1: 1,462; 1: 17,954; and -3: 429. This experiment tests a defined numeric representation, not a quality-screened physical flow reconstruction.

### Prior art and the remaining compression question

Predictive floating-point coding predates this work. FPC uses prediction and XOR residuals [7]; Gorilla, Chimp and Elf offer complementary approaches [8-10]. Those specialized codecs were not run in this edition. The measured panel cannot establish superiority over them. Ordinary floating-point subtraction and addition do not guarantee bit-exact recovery; a flow predictor must define deterministic prediction bits and reversible residuals, or explicitly count corrections for platform differences.

### The authored morph and physical clouds

The earlier draft described a scripted sphere-to-torus morph and exact replay of authored coordinates. Its original stream, decoder and videos were not available in the supplied publishing kit. The stated byte-count arithmetic is consistent: 240 × 2 × (71 × 141 + 204) × 3 × 8 = 117,676,800. That arithmetic does not verify the actual stream, its checksum, or the earlier compressed sizes; those results are not included as fresh measurements here.

For a smooth velocity field with unique trajectories, the finite-time flow map is invertible. It preserves the topology of an intact embedded material surface. A thresholded particle-concentration envelope is a different object and can develop an apparent opening as particles redistribute. Settling-cloud experiments [2-4] motivate a future physical comparison, but their mechanisms and parameters do not validate a prescribed shape map. Dagan’s low-Stokes particle solutions [5] offer a possible intermediate benchmark under their own assumptions.


---

## 6. A testable next experiment

### Physical data without prescribing the answer

Select a documented settling-cloud case, beginning with a quiescent comparison [2], and obtain the full methods, geometry, initial conditions and particle-interaction model. Reproduce macroscopic statistics across initializations before interpreting a central opening. Define first persistent opening separately from breakup, and test sensitivity to projection, concentration threshold and resolution. A driven cellular-flow case [4] adds a different forcing regime. No such physical simulation was completed in this edition.

### Freeze the prediction test before using held-out runs

Hold out whole runs or initial conditions before choosing the predictor or tuning its parameters. Freeze the canonical bytes, trajectory IDs, timestamps, masks and layout. Compare the flow predictor with raw coding, general-purpose codecs, previous-value and spatial baselines, and pinned specialized implementations such as FPC and Chimp128. Give baselines equivalent preprocessing and count any reordering map.

Count first states, parameters, resets, corrections, residuals, masks, time values and headers. Report shared decoder/runtime requirements separately. Decode and compare bytes before measuring savings. Record encoding and decoding time, peak process memory and hardware; preserve failures. The present timings measure resident-packet decoding, inverse transform and checksum after a correctness preflight and one designated warmup, with five measured repetitions. Python-traced peak allocation is recorded separately and is not whole-process memory.

The hypothesis gains support only when a frozen flow-informed method beats the best prespecified baseline on held-out data at identical fidelity and honestly counted cost. A correct analytic solution, an attractive morph or replay of self-authored data cannot supply that result.

### Reproduce this edition

python -m pip install -r requirements.txt
python tools/verify.py --output results/my-verification
python tools/fetch_reference_data.py --output .reference-data
python tools/benchmark_compression.py --data .reference-data --output results/my-compression
python tools/independent_compression_check.py --data .reference-data --results results/my-compression

Fresh output directories are required. requirements-build.txt and tools/build_figures.py / tools/build_paper.py rebuild the figures and manuscript. README and REVIEW_STATUS identify exact release evidence and CI status.

Authorship and review: Aaron Michael Weis is the author. AI assistance supported drafting, programming, literature lookup and internal review. Three specialist passes and an integrating pass checked bounded claims; this is not independent human peer review. Sources retain their authorship. Publication does not establish the untested physical or compression hypothesis.


---

## References

Targeted source review conducted November 26, 2026. This is a bounded literature check, not an exhaustive novelty search. The 2011 settling-cloud source was checked at abstract/metadata level; the other paper references were inspected through publisher or author full text. Third-party articles and raw fixtures are linked, not repackaged.

1. Ondrej Kincl, Ilya Peshkov, Walter Boscheri (2025). [Semi-implicit Lagrangian Voronoi approximation for the incompressible Navier-Stokes equations](https://doi.org/10.1002/fld.5339). International Journal for Numerical Methods in Fluids 97(1), 88-115. Section 5.1.

2. Bloen Metzger, Maxime Nicolas, Elisabeth Guazzelli (2007). [Falling clouds of particles in viscous fluids](https://doi.org/10.1017/S0022112007005381). Journal of Fluid Mechanics 580, 283-301. Published-layout author PDF inspected.

3. Florent Pignatel, Maxime Nicolas, Elisabeth Guazzelli (2011). [A falling cloud of particles at a small but finite Reynolds number](https://doi.org/10.1017/S0022112010005501). Journal of Fluid Mechanics 671, 34-51. Publisher abstract and metadata inspected.

4. Benjamin Marchetti, Laurence Bergougnoux, Elisabeth Guazzelli (2021). [Falling clouds of particles in vortical flows](https://doi.org/10.1017/jfm.2020.883). Journal of Fluid Mechanics 908, A30. Author PDF inspected; figures 4 and 6, Table 4.

5. Yuval Dagan (2025). [Analytical solutions for particle dispersion in Taylor-Green vortex flows](https://doi.org/10.1007/s00162-024-00731-z). Theoretical and Computational Fluid Dynamics 39, article 14. First online December 24, 2024.

6. PIVPy contributors. [TSI Insight demonstration fixtures](https://github.com/alexlib/pivpy/tree/be5e26a17e0d61f7113ec87e98ffcc0d443c297f/pivpy/data/Insight). Five Run000001-Run000005 .vec files; commit be5e26a17e0d61f7113ec87e98ffcc0d443c297f. Retrieved November 26, 2026. Exact source paths and hashes are recorded in the release.

7. Martin Burtscher, Paruj Ratanaworabhan (2009). [FPC: A High-Speed Compressor for Double-Precision Floating-Point Data](https://doi.org/10.1109/TC.2008.131). IEEE Transactions on Computers 58(1), 18-31. Author manuscript and software page inspected.

8. Tuomas Pelkonen et al. (2015). [Gorilla: A Fast, Scalable, In-Memory Time Series Database](https://doi.org/10.14778/2824032.2824078). Proceedings of the VLDB Endowment 8(12), 1816-1827. Sections 4.1.1-4.1.2.

9. Panagiotis Liakos, Katia Papakonstantinopoulou, Yannis Kotidis (2022). [Chimp: Efficient Lossless Floating Point Compression for Time Series Databases](https://doi.org/10.14778/3551793.3551852). Proceedings of the VLDB Endowment 15(11), 3058-3070.

10. Ruiyuan Li, Zheng Li, Yi Wu, Chao Chen, Yu Zheng (2023). [Elf: Erasing-based Lossless Floating-Point Compression](https://doi.org/10.14778/3587136.3587149). Proceedings of the VLDB Endowment 16(7), 1763-1776.
