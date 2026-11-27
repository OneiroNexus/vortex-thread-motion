# Vortex-Thread Motion 1.0.0

**A Research Framework for Particle Collection and Motion Compression**

Research edition 1.0.0. This framework connects two goals through organized motion while requiring separate tests: retained mass, mass balance and energy cost for physical particle collection; held-out gains from a flow predictor plus reversible residuals for motion compression. Neither goal is proven by the current supporting checks. Collecting particles is not compression of fluid volume.

The edition supplies reproducible analytic-field verification, authored-geometry replay and a compression-baseline experiment. It preserves the pressure and segment-width formulas, makes nondimensionalization and energy normalization explicit, and separates completed checks from both unvalidated test plans.

Included: a nine-page PDF and editable manuscript, [plain-language introduction](docs/PLAIN_LANGUAGE.md), ten research references, three source-driven figures in PNG and SVG, exact-field and RK4 code, reversible XOR packet baselines, pinned-fixture fetcher, separate standard-library packet checker, two offline viewers and recovered recipe sources. Original MP4s remain local-only. See [original demonstrations](docs/ORIGINAL-DEMONSTRATIONS.md).

Local core validation passed 20 unittest methods and eight separately counted numerical checks. All 18 snapshot packets reconstructed their canonical targets byte-for-byte; an independent decoder verified them. Wrong-pressure and skipped-suite negative controls correctly failed.

At commit `e83e507`, the [core CI run](https://github.com/OneiroNexus/vortex-thread-motion/actions/runs/45927857198) and [original-replay CI run](https://github.com/OneiroNexus/vortex-thread-motion/actions/runs/45927857214) passed on Ubuntu and Windows. The recovered recipe produced 117,676,800 bytes with full native reference/decoder agreement on both platforms. Linux reproduced historical coordinate hash `d1aa661c...` and 75,882,043-byte gzip; Windows produced `8ae57764...` and 75,882,403-byte gzip. This platform difference is retained explicitly; its cause has not been isolated. Later artifact integration requires separate manifest/link checks.

Original viewer contract checks passed using DOM substitutes. Live-browser visual checking was blocked by a denied localhost socket. The rounded torus trace is a lossy preview; coordinate replay neither reconstructs an MP4 nor demonstrates physical matter collection or a physical 3D cloud transition. The older snapshot pilot remains unreproduced and separate from the new measured table. No held-out flow predictor, general compression advantage or independent human peer review is claimed.

The author approved [MIT for author code](LICENSE) and [CC BY 4.0 for the paper and original scientific figures](LICENSE-PAPER.md). Third-party terms remain separate. Edition identifiers are the [repository](https://github.com/OneiroNexus/vortex-thread-motion), release tag `v1.0.0`, and [Zenodo DOI 10.5281/zenodo.24574783](https://doi.org/10.5281/zenodo.24574783).
