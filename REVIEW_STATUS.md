# Review status — version 1.0.0

Aaron Michael Weis · Local release preparation · 2026-11-26

This edition is being assembled for review. Local numerical verification is evidence for the bounded implementation below. Remote CI execution, public release, persistent identifiers, metadata and licensing require separate completion; no remote CI pass is claimed here.

| Item | Evidence and limit |
|---|---|
| Analytic 2D field | Direct identity checks and centered finite-difference convergence; known Taylor–Green solution, not a new solution or evolved PDE solver. |
| Passive trajectories | RK4 convergence against exact segment widths and a refined RK4 generic reference; first-integral and material deformation checks. |
| Energy and enstrophy | Exact mean-density decay and independent periodic-grid quadrature. |
| Unit/integration checks | `results/verification-v1.0.0/test-summary.json`; each method counts once. Samples, stages and eight separate numerical acceptance checks do not inflate that count. A passing run requires zero failures, errors, skips, expected failures and unexpected successes. |
| Snapshot compression | `results/compression-2026-11-26/compression.json`: 18 newly measured packets on five pinned public PIVPy files, with exact canonical byte reconstruction, counted packet overhead, timing and Python-traced memory. No flow predictor or held-out result. |
| Independent packet validation | A separate standard-library checker independently verified five source fixtures and all 18 packets. See `results/independent-compression.json`. |
| Workflow | Ubuntu/Windows Python 3.12 workflow supplied; remote CI pass is unverified until an actual run is inspected. |
| Paper and figures | Eight-page PDF/Markdown and three source-driven figures; math and source reviews passed. All pages were rendered and visually checked after layout corrections. |
| Historical archive/media | The complete original reproduction archive and original viewers/videos have not been recovered in this workspace; fresh checks do not verify their historical execution. |
| Physical interpretation | No 3D cloud simulation, physical torus formation, general compression advantage, or independent experimental validation is claimed. |
| Publication and licensing | Awaiting author choices and final integration; no DOI, repository URL or license is invented here. |

The public evidence selection is `results/verification-v1.0.0/` and `results/compression-2026-11-26/compression.json`. Intermediate logs, private intake/reviews/reference downloads, and generated `.vtm` packets are excluded from that selection. Commands in the README regenerate packets and verify their identity.

Before publication, inspect the assembled paper and figures, confirm selected evidence matches current source hashes, inspect actual CI outcomes, and complete the author's metadata/licensing decisions. The live paper's physical comparisons and future research plan remain distinct from the computations completed here.
