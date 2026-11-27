# Vortex Threads: deterministic recipe benchmark

This is an authored procedural animation, not a general-purpose or MP4 compression test. The canonical output is the pre-camera 3D point sequence behind both panels of the Vortex Threads Matched Comparison: 240 frames, 2 panels, 71 threads of 141 sampled points plus 204 tracer points per panel. Each frame stores left panel then right, threads then tracers, C-order XYZ little-endian binary64 triples. There is no container header. Both panels share Taylor–Green chart advection; the right morph is separate and scripted.

## Reconstruct and verify

Use Linux x86_64 with Python 3.12.14 and NumPy 2.3.5 for the tested decoder environment. No installation or network action is performed by these scripts. From this folder:

```sh
python3 decode.py recipe.json --expect d1aa661c76182cd6784a53b127185db4e2d55e7011b1a4564fa53571e401bfa8
```

Add `--output reconstructed.xyz64le` to save the exact 117,676,800 bytes at a new path. There is no promise of bit-exact output on other CPUs or NumPy/libm builds; the checksum is the test. This output is geometry, not the film, camera, styling, pixels, or original encoded video container.

## Re-run the control

`OPENBLAS_NUM_THREADS=1 python3 benchmark.py` extracts the baseline math and initialization from the included exact renderer sources, serializes the independent reference in a scratch directory, and compares its full bytes to fresh-process reconstruction. For this optional path the renderer's import prelude also uses Pillow 13.0.0. It needs around 313 MB of temporary space. No frames or MP4 are rendered. It compares default-workflow gzip level 6 vs generator in the same process with streamed SHA-256 consumers, alternating timing order across three runs. Warm cache and machine-specific, not network or production latency; optional recipe-to-disk time includes a fresh process and is reported separately. A one-bit edit and a changed seed demonstrate what the recipe does not reproduce.

## Measured original run

| Representation | Bytes |
|---|---:|
| Baked binary64 XYZ | 117,676,800 |
| gzip level 6 of the same bytes | 75,882,043 |
| Recipe assuming a compatible shared decoder | 177 |
| Recipe + Python decoder source, no ZIP yet | 2,916 |
| Recipe + decoder, two-entry ZIP including ZIP overhead | 1,597 |

Medians on the tested cloud host: gzip 0.591 s vs recipe 0.867 s to the same hash. A fresh recipe process wrote the full file in 1.197 s; no matched fresh gzip-to-disk timing was collected. The full ZIP includes code, docs, reference renderer sources and results, not runtime dependencies or the original video. It is a download package, not a self-contained executable runtime. There is no claim that gzip is optimal, that mesh samples are arbitrary data, or that the recipe preserves unrelated captured content. No lossy quantization was performed. For a modified capture, independently changed bytes need extra residual data or fail exact comparison.
