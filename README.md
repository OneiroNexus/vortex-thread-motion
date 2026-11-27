# Vortex-Thread Motion

**A Research Framework for Particle Collection and Motion Compression**  
Aaron Michael Weis · OneiroNexus · Version 1.0.0

This work connects two goals through organized motion: collecting particles in a physical system and representing motion with fewer data bytes. They require separate tests. Physical collection must demonstrate retained mass, a closed mass balance and measured energy cost. Motion compression must show that a flow predictor plus reversible residuals beats prespecified baselines on held-out data. Particle collection is not compression of the fluid's volume.

The current edition supplies supporting checks: a known decaying two-dimensional Taylor-Green field, numerical trajectory verification, authored-coordinate replay, and a descriptive lossless compression control on five public PIVPy snapshots. Neither a successful physical collection system nor a useful flow-informed compressor has been demonstrated. Research edition 1.0.0.

The analytic field is

```text
u(x,y,t) = A(t) (cos(x) sin(y), -sin(x) cos(y))
A(t)     = exp(-2 nu t)
p(x,y,t) = -A(t)^2 (cos(2x) + cos(2y)) / 4
```

The domain is the dimensionless periodic square `[0,2*pi)^2`, with unit density, viscosity `nu >= 0`, no forcing, and zero mean kinematic pressure. This is a known exact Navier–Stokes solution, evaluated here directly; the package does not evolve a discretized PDE.

## Read the paper and evidence

Start with the [plain-language introduction](docs/PLAIN_LANGUAGE.md), or read the nine-page paper as [PDF](docs/Vortex-Thread-Motion-v1.0.0.pdf) and [editable Markdown](docs/Vortex-Thread-Motion-v1.0.0.md). Three reproducible scientific figures are included in PNG and SVG. Explore the offline [Inkline field viewer](demos/inkline/index.html) and [scripted torus viewer](demos/torus/index.html). See [original demonstrations](docs/ORIGINAL-DEMONSTRATIONS.md) and [review status](REVIEW_STATUS.md) for the evidence boundaries.

Selected public evidence for this edition:

- [Verification results](results/verification-v1.0.0/verification.json), [test summary](results/verification-v1.0.0/test-summary.json), [environment and source hashes](results/verification-v1.0.0/environment.json), and [test log](results/verification-v1.0.0/unittest.txt).
- [Fresh compression control](results/compression-2026-11-26/compression.json), containing all 18 packet measurements, input identities, byte checks, decode timing samples, and Python-traced peak memory.
- [Independent packet check](results/independent-compression.json), using a separate standard-library decoder and source parser.
- Recovered coordinate recipe reports: [local Windows](results/original-replay/local-windows.json), [CI Linux](results/original-replay/ci-linux.json), and [CI Windows](results/original-replay/ci-windows.json).

The selected evidence excludes intermediate result directories and generated `.vtm` packet files. Reproduction commands below generate the packets afresh.

## Reproduce with Python 3.12

Run from the repository root. The numerical field/trajectory implementation uses Python's standard library. The integrated tests and compression control require the pinned NumPy dependency.

```sh
python -m pip install -r requirements.txt
python tools/verify.py --output results/my-verification
python tools/fetch_reference_data.py --output .reference-data
python tools/benchmark_compression.py --data .reference-data --output results/my-compression
python tools/independent_compression_check.py --data .reference-data --results results/my-compression
```

Choose new result directories on each run: verification and benchmark commands refuse an existing output directory. `verify.py` returns 0 only when all discovered tests and numerical acceptance checks pass, with zero skips, expected failures or unexpected successes. Verification failure returns 1; CLI/output-path failure returns 2. The fetcher accepts already downloaded files only after checking their pinned Git blob identities. Fetching the public fixtures requires internet access; verification itself does not.

The [core GitHub Actions run](https://github.com/OneiroNexus/vortex-thread-motion/actions/runs/45927857198) passed on Ubuntu and Windows at commit `e83e507`. The separate [original-replay run](https://github.com/OneiroNexus/vortex-thread-motion/actions/runs/45927857214) also passed both native checks. These runs verify that commit; later documentation and artifact integration are recorded separately. Build-only dependencies for paper and figure generation are pinned separately in [requirements-build.txt](requirements-build.txt); they are unnecessary for the numerical verification commands above.

To check the recovered authored coordinate recipe separately:

```sh
python legacy/recipe/verify_recipe.py --output results/my-original-replay
```

This command compares the native renderer reference and unchanged decoder in a fresh process. Its `historical_digest_matched` flag is a separate check: Linux CI matched the archived Linux hash, while Windows passed native byte identity with a different stream hash. It requires a new output directory and about 313 MB of temporary disk space. See the [recipe instructions](legacy/recipe/README.md).

## Rebuild the paper and figures

```sh
python -m pip install -r requirements-build.txt
python tools/build_figures.py
python tools/build_paper.py
```

The build uses the selected JSON evidence and bundled DejaVu fonts. Output paths are stable; rebuild in a working copy if preserving exact release PDF bytes. Generated PDF bytes can vary with build timestamps even when content matches.

## What the checks establish

The exact-field checks verify the pressure sign, incompressibility, vorticity, first integral, viscosity decay, energy/enstrophy accounting, and opposing directional strain. Centered finite differences show second-order derivative and momentum-residual convergence on fixed sample points. RK4 shows fourth-order trajectory convergence; generic trajectories use a refined RK4 reference, while two horizontal passive segments have exact width references.

The paper's segments start at `x=pi/2 +/- 0.10`: `y=+pi/2` contracts and `y=-pi/2` expands. At `nu=0.25` and `t=2 log(2)`, their widths are `0.0736289459135128` and `0.5407906651876966`, from initial width `0.20`. A separately integrated deformation gradient checks material area preservation. Shortening a line does not imply area loss.

The compression control uses public PIVPy files pinned to commit [`be5e26a17e0d61f7113ec87e98ffcc0d443c297f`](https://github.com/alexlib/pivpy/tree/be5e26a17e0d61f7113ec87e98ffcc0d443c297f/pivpy/data/Insight). It tests all numeric columns and a velocity-only subset, each with three reversible transforms (none, previous-file XOR, previous-point XOR) and three codecs (gzip, bzip2, LZMA): **18 packets**. Every decoded packet must match its canonical little-endian binary64 target byte for byte, including negative zero. Headers and original decimal formatting are excluded from the target; source file identities remain recorded separately.

Packet sizes include the packet header, transform identifier, checksum and compressed payload. The shared decoder, Python, NumPy and codec runtime are reported dependencies rather than charged per packet. Decode timings include reconstruction and checksum verification; memory measurements are Python-traced allocations, not total process memory. File ordering is by name, with no verified inter-file cadence.

The recovered authored-coordinate recipe now passes native full-byte reference/decoder comparison on Windows and Linux. Linux CI reproduced the historical coordinate hash and gzip size; Windows produced a different hash and gzip size despite matching its own native reference. The cause of that platform difference has not been isolated. The two offline viewers are included; original MP4s remain preserved locally and are not rehosted. Real-browser visual checking was blocked by a denied localhost socket; DOM-substitute tests passed.

No physical collection result, flow predictor, held-out compression advantage or physical 3D cloud simulation is established. The old snapshot pilot remains separate and unreproduced; the fresh 18-packet experiment has its own explicit canonical representation and accounting. Physical collection needs a separate mass-retention, mass-balance and energy test; motion compression needs a held-out comparison against prespecified baselines. An attractive ring or a smaller coordinate file cannot substitute for either test.

## Layout

- `src/vortex_thread/`: exact field, RK4 trajectories, diagnostics, and reversible packet baselines.
- `tests/`: analytic identities, numerical convergence and packet integrity checks.
- `tools/`: verification, pinned-data fetch, compression benchmark and independent packet check.
- `docs/` and `figures/`: paper and supporting figures.
- `results/`: selected public result records described above.
- `demos/`: recovered offline analytical-field and scripted-geometry viewers.
- `legacy/recipe/`: preserved original recipe, decoder, reference sources and portable checking adapter.

Author code is licensed under [MIT](LICENSE); the paper and original scientific figures are licensed under [CC BY 4.0](LICENSE-PAPER.md). Third-party sources retain their own authorship and terms; the PIVPy fixtures are fetched from their source rather than bundled. See [third-party notices](THIRD_PARTY_SOURCES.md).

Edition links: [GitHub repository](https://github.com/OneiroNexus/vortex-thread-motion), [release v1.0.0](https://github.com/OneiroNexus/vortex-thread-motion/releases/tag/v1.0.0), and [Zenodo DOI 10.5281/zenodo.24574783](https://doi.org/10.5281/zenodo.24574783). Research edition 1.0.0.  See [release notes](RELEASE_NOTES.md).
