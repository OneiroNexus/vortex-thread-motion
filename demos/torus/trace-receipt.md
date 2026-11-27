# Scripted Vortex preview: trace receipt

- Source: exact delivered `Vortex Threads - Recipe Benchmark.zip` (10,040 bytes); SHA-256 `59b695d24b2d6438b1f14119f0df8a1bb777074bbac2b4b6664da7c9b4d0012c`.
- Canonical full geometry replay: 117,676,800 bytes, SHA-256 `d1aa661c76182cd6784a53b127185db4e2d55e7011b1a4564fa53571e401bfa8`. Verified by the trace exporter on Linux x86-64, Python 3.12.14 and NumPy 2.3.5.
- Preview `trace.json`: 348,717 bytes, SHA-256 `55938d8a15313045aa7b04be3349a877b669145314f4cfc0bde415471425a964`. A fresh export matched every byte; a mismatched input archive was rejected before emitting output.
- Right-hand scripted panel. Source frame index `round(j*239/59)`, `j=0…59`; dimensionless simulation time is `index*4.2/239` rounded to nine decimals, not the rendered film's timestamp. The frame indices strictly increase and include 0 and 239.
- Curves: fixed source rows 7 (latitude-07), 41 (meridian-07), 64 (spiral-05); source point index `round(j*140/63)`, `j=0…63`. All 11,520 triples are finite, including the coincident endpoints. XYZ is dimensionless, Z is the ring axis, and the observed overall coordinate interval is [-1.515149, 1.519117]. No tracers or video bytes.
- The reduced, six-decimal payload is a lossy interactive preview of the verified source geometry. It is not a fluid simulation, a new benchmark, or evidence of compression of captured video.
