"""Recompute a descriptive PIVPy snapshot control with fully counted packets.

No flow predictor, training, holdout or time-series cadence is established here.
Inputs are the five files verified by fetch_reference_data.py.
"""
from pathlib import Path
import argparse
import hashlib
import io
import json
import platform
import statistics
import sys
import time
import tracemalloc
import zlib
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from vortex_thread.compression import CODECS, TRANSFORMS, encode, decode
from fetch_reference_data import BLOBS, COMMIT

def read_data(directory):
    arrays, sources = [], []
    for n, expected in enumerate(BLOBS, 1):
        name = f'Run{n:06}.T000.D000.P000.H001.L.vec'
        raw = (directory / name).read_bytes()
        if hashlib.sha1(f'blob {len(raw)}\0'.encode() + raw).hexdigest() != expected:
            raise ValueError(f'Source identity mismatch: {name}')
        lines = raw.decode('ascii').splitlines()
        if 'ZONE I=63, J=63' not in lines[0]:
            raise ValueError('Unexpected fixture dimensions')
        a = np.loadtxt(io.StringIO('\n'.join(lines[1:])), delimiter=',', dtype='<f8')
        if a.shape != (3969, 5) or not np.all(np.isfinite(a)):
            raise ValueError('Unexpected numeric fixture')
        arrays.append(a)
        sources.append({'file': name, 'git_blob': expected, 'sha256': hashlib.sha256(raw).hexdigest(), 'bytes': len(raw)})
    return np.asarray(arrays, dtype='<f8'), sources

def run(directory, output, repetitions=5):
    if repetitions < 3:
        raise ValueError('Use at least three measured repetitions')
    if output.exists():
        raise FileExistsError('Output exists; choose a new directory')
    data, sources = read_data(directory)
    output.mkdir(parents=True)
    rows = []
    for target, values in [('all_columns', data), ('velocity_only', data[:, :, 2:4])]:
        a = np.ascontiguousarray(values, dtype='<f8').view('<u8')
        raw = a.tobytes(order='C')
        for codec in CODECS:
            for method in TRANSFORMS:
                packet = encode(a, method, codec)
                if decode(packet) != raw:
                    raise AssertionError('Decode is not byte-identical')
                # One warmup; comparisons are outside timing; trace memory separately.
                decode(packet)
                durations = []
                for _ in range(repetitions):
                    start = time.perf_counter_ns()
                    decoded = decode(packet)
                    durations.append((time.perf_counter_ns() - start) / 1e6)
                    if decoded != raw:
                        raise AssertionError('Timed decode mismatch')
                tracemalloc.start()
                decoded = decode(packet)
                _, peak = tracemalloc.get_traced_memory()
                tracemalloc.stop()
                rows.append({'target': target, 'shape': list(a.shape), 'raw_bytes': len(raw),
                             'codec': codec, 'transform': method, 'packet_bytes': len(packet),
                             'packet_sha256': hashlib.sha256(packet).hexdigest(),
                             'canonical_sha256': hashlib.sha256(raw).hexdigest(), 'byte_identity': True,
                             'decode_ms': durations, 'median_decode_ms': statistics.median(durations),
                             'python_traced_peak_bytes': peak})
                (output / f'{target}-{codec}-{method}.vtm').write_bytes(packet)
    result = {'protocol_version': '1.0.0', 'source_commit': COMMIT, 'sources': sources,
              'environment': {'python': platform.python_version(), 'numpy': np.__version__,
                              'system': platform.system(), 'machine': platform.machine(), 'zlib': zlib.ZLIB_VERSION},
              'repetitions': repetitions, 'warmups': 1,
              'scope': 'Descriptive fixture comparison. Files are ordered by name, not verified chronological frames. No flow predictor or held-out evaluation.',
              'canonicalization': 'All numeric tokens parsed as little-endian binary64 in file,row,column order. Headers and original decimal formatting excluded. Velocity-only retains columns U,V without filtering CHC. Negative zero retained.',
              'accounting': 'Packet bytes include magic, metadata, checksum, transform identifier and compressed residual. Shared decoder/runtime excluded and reported as dependencies. Timing includes decode, transform inversion and checksum. Tracemalloc is Python-traced peak, not whole-process RSS.',
              'results': rows}
    (output / 'compression.json').write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    return result

if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--data', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--repetitions', type=int, default=5)
    args = p.parse_args()
    r = run(args.data, args.output, args.repetitions)
    print(json.dumps({'status': 'PASS', 'packets': len(r['results']), 'all_byte_identical': all(v['byte_identity'] for v in r['results']), 'results': str(args.output / 'compression.json')}))
