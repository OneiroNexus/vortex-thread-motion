# Recovered original demonstrations

Aaron Michael Weis | OneiroNexus

Status checked November 26, 2026. Research edition 1.0.0. These materials preserve the project's authored visual starting point. The current [paper](Vortex-Thread-Motion-v1.0.0.md), subtitled *A Research Framework for Particle Collection and Motion Compression*, and saved reports distinguish numerical verification, procedural replay and the external snapshot experiment.

## Open the viewers

- [Inkline Vector Lab](../demos/inkline/index.html) displays the known decaying two-dimensional Taylor-Green velocity field and numerically integrated passive paths. Its arrows evaluate the analytic law; it does not evolve a numerical pressure/velocity PDE solution.
- [Juicy Donut Lab](../demos/torus/index.html) shows synchronized side and end projections of three curves from a prescribed three-dimensional shape sequence. It labels the geometry as scripted. The embedded data are a reduced, rounded trace, not measured fluid trajectories.
- [Recovered recipe sources](../legacy/recipe/) contain the procedural decoder, recipe, reference renderer sources and historical documentation/results. The historical result describes its original environment; it is not a report of the current rerun.

Both viewers use inline JavaScript, CSS and SVG. Static inspection identified no external script, font or stylesheet imports and no network request APIs. Inkline retains its acknowledgment of layout inspiration from [Inkline Town development notes](https://github.com/SandroMaglione/inkline-town/blob/main/DEVELOPMENT.md); no imported game code or assets were identified. This source inspection does not replace real-browser testing or establish ownership of third-party projects.

## Recovered archive provenance

Two supplied archives restored the original manuscript, demonstrations, tests and recipe bundle. Their original bytes remain preserved locally; the public edition selects materials from them rather than adopting their older publishing metadata as current instructions.

| Source archive | Bytes | SHA-256 |
|---|---:|---|
| Vortex-Thread Motion - Part 1 - Paper Demos and Research.zip | 13,325,631 | `fe188894250dd02fbb55ca01fd33b06b354b6ca9298c544e993773a9321f7397` |
| Vortex-Thread Motion - Part 2 - Original Torus Video.zip | 13,884,140 | `df77ce6fce9054ceec1c6c7b35a3611d0ae0fbf6a2e364ab7015142f8c0d3481` |

The nested original `Vortex Threads - Recipe Benchmark.zip` is 10,040 bytes, SHA-256 `59b695d24b2d6438b1f14119f0df8a1bb777074bbac2b4b6664da7c9b4d0012c`. It supplies recipe and decoder source, reference renderer source, README and historical results. It does not contain a baked 117 MB coordinate file; that target is generated during reproduction.

The three original MP4s remain local-only and are not rehosted in this edition:

| Preserved film | Bytes | SHA-256 |
|---|---:|---|
| Navier-Stokes - Taylor-Green Vortex.mp4 | 879,037 | `3a7a60ea62eb9b6623622df08897781925c280e51c14b292a1f5db744f5a74a9` |
| Vortex Threads - Matched Comparison.mp4 | 11,888,686 | `e6b9d8c9835525d904a2e88af64b2e03147d5d1c702e1d0432a4b29700f7a76f` |
| Vortex Threads - Sphere to Torus.mp4 | 13,882,469 | `eff9036d5bb6c7f4a66384f1feb414e04064f92b9792f3f2c36bbded52e3fad4` |

Container inspection found video tracks and no audio-track handlers. This metadata check is not a fresh video render or visual-content verification.

## What the recovered checks establish

The original small checks were rerun successfully:

- Inkline: 225 arrows, 144 model cases, maximum sampled finite-difference divergence `3.608224830031759e-11` and momentum residual `6.90236123812582e-8`; probe/UI checks passed using a DOM substitute.
- Passive segments: RK4 agreed with the closed-form widths `0.073628945914` and `0.540790665188` at the displayed precision.
- Torus viewer: embedded trace equality, both axis projections, three curve paths, scrub/step/playback, boundary controls and malformed-input rejection passed using a DOM substitute.

These checks concern the known field, numerical trajectories and viewer contracts. A live-browser visual check was attempted but blocked when the local HTTP server's socket was denied. DOM-substitute checks passed; browser rendering remains unverified. These checks do not establish a general CFD solver, physical torus formation or independent compression gains.

## Native coordinate replay and platform boundary

The canonical target is pre-camera XYZ geometry: 240 frames, two panels, 71 curves with 141 samples plus 204 tracers per panel, serialized as little-endian binary64 triples. The total is 117,676,800 bytes. Both panels share planar chart advection; an imposed shape map changes the right-hand geometry.

A fresh Windows rerun used Python 3.12.14 and NumPy 2.3.5. Coordinates generated from the recovered renderer's mathematical definitions matched the original decoder's output by full byte comparison. Renderer-source hashes also matched the archived result record. The checking adapter omitted rendering-only imports and font initialization; the coordinate definitions were retained. The original optional benchmark also assumes a Linux font path and GNU libc, so it should not be presented as an unchanged portable Windows command.

| Quantity | Fresh Windows result | Historical Linux report |
|---|---|---|
| Canonical bytes | 117,676,800 | 117,676,800 |
| Coordinate SHA-256 | `8ae57764f83a5ffd5c9009b6d6856ac673317938736861c11cbfe0990edb2e7e` | `d1aa661c76182cd6784a53b127185db4e2d55e7011b1a4564fa53571e401bfa8` |
| gzip level 6 bytes | 75,882,403 | 75,882,043 |
| Recipe bytes | 177 | 177 |
| Decoder source bytes | 2,739 | 2,739 |
| Two-entry recipe + decoder ZIP bytes | 1,597 | 1,597 |

The local Windows reference and decoder agree with each other, but that stream does **not** reproduce the historical Linux hash. A subsequent [original-replay CI run](https://github.com/OneiroNexus/vortex-thread-motion/actions/runs/45927857214) at commit `e83e507` passed native full-byte reference/decoder checks on both Ubuntu and Windows. The fresh Linux run **did** reproduce the historical Linux coordinate hash and gzip size.

| Current result record | Runtime | Historical hash matched | gzip level 6 bytes |
|---|---|---|---:|
| [Local Windows](../results/original-replay/local-windows.json) | Python 3.12.14, NumPy 2.3.5, zlib 1.3.2 | No; native hash `8ae57764f83a5ffd5c9009b6d6856ac673317938736861c11cbfe0990edb2e7e` | 75,882,403 |
| [CI Linux](../results/original-replay/ci-linux.json) | Python 3.12.16, NumPy 2.3.5, zlib 1.3.1 | Yes; `d1aa661c76182cd6784a53b127185db4e2d55e7011b1a4564fa53571e401bfa8` | 75,882,043 |
| [CI Windows](../results/original-replay/ci-windows.json) | Python 3.12.10, NumPy 2.3.5, zlib 1.3.1 | No; native hash `8ae57764f83a5ffd5c9009b6d6856ac673317938736861c11cbfe0990edb2e7e` | 75,882,403 |

This is a demonstrated platform boundary. These runs do not isolate its cause; neither Python version differences nor any particular math library has been established as responsible. Native byte identity and historical-digest agreement are separate outcomes, both retained in the reports. To repeat the check, follow the [portable recipe instructions](../legacy/recipe/README.md).

Changing the seed changed the digest, and a one-bit coordinate edit was detected. The size comparison illustrates shared structure in an authored target deliberately generated by the recipe. The 177-byte case assumes an available compatible decoder; the 1,597-byte ZIP includes decoder source but excludes Python, NumPy and other runtime dependencies. It is not a self-contained executable or a general lossless codec result. No MP4 or pixel compression claim follows from it.

## The embedded trace has a different fidelity contract

The torus viewer uses 60 selected frames, three selected curves and 64 selected samples per curve: 11,520 XYZ triples rounded to six decimals. Its standalone archived trace is 348,717 bytes, SHA-256 `55938d8a15313045aa7b04be3349a877b669145314f4cfc0bde415471425a964`. That is a lossy interactive preview of authored geometry. It is neither the complete bit-exact coordinate target nor the rendered film. Its time values are dimensionless model times, not film timestamps.

## Keep the older snapshot pilot separate

The recovered manuscript also reports an earlier PIVPy pilot with packet sizes 103,698, 91,404, 93,052 and 92,096 bytes. Its particular canonicalizer and pilot benchmark source were not recovered in the recipe bundle, and this pilot has not been reproduced here. Those numbers must not replace the current independently checked 18-packet binary64 experiment. The latter has its own canonical representation, complete packet accounting, result files and independent checker.

The framework connects two proposed uses of organized motion, with separate tests. Physical particle collection must demonstrate retained mass, mass balance and energy cost; collecting particles does not compress the fluid's volume. Data compression must demonstrate that a prespecified flow predictor plus reversible residuals beats fair baselines on independent held-out runs at identical reconstruction fidelity. Neither goal is proven by these demonstrations. The shape map is authored, its hole is prescribed, and no physical three-dimensional settling-cloud simulation is established. Code, paper, external data and third-party dependencies retain their separately stated licenses and attribution.
