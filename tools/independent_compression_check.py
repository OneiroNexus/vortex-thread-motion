"""Independently check the pinned fixture and all 18 saved benchmark packets.

Uses only Python's standard library; imports neither production code nor NumPy.
This is a trusted local artifact check, not an untrusted-input decoder, a codec
benchmark rerun, a flow-model validation, or a held-out compression evaluation.
All numeric tokens are parsed independently with float() and packed with struct;
headers and original decimal formatting are deliberately outside the target.
"""
from pathlib import Path
import argparse
from collections import Counter
import bz2
import gzip
import hashlib
import itertools
import json
import lzma
import math
import platform
import struct
import sys
import zlib

# Independent pins for the five files at this public PIVPy revision. These are
# intentionally duplicated rather than imported from the production fetcher.
COMMIT = 'be5e26a17e0d61f7113ec87e98ffcc0d443c297f'
BLOBS = (
    '8597bf2dbcaa9e31ac70b508016e83db2ac84192',
    '207c98a3b98569f962cfc95bba39e99ac2b37b21',
    '59abbb5b4821137af6b28f86fa0796168030c9bd',
    '120b7f7e14fb6a637309c2c701f369040dacd5a7',
    '280b5e79978446849cabe6621848f04700791c06',
)
CODECS = ('gzip', 'bz2', 'lzma')
METHODS = ('none', 'previous_file_xor', 'previous_point_xor')
TARGET_SHAPES = {'all_columns': [5, 3969, 5], 'velocity_only': [5, 3969, 2]}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def read_targets(directory, records):
    """Check source identities and parse canonical targets without NumPy."""
    require(isinstance(records, list) and len(records) == 5, 'Expected five source records')
    all_values, velocity_values = bytearray(), bytearray()
    source_checks, quality_counts = [], Counter()
    positive_zero = negative_zero = 0
    for index, expected_blob in enumerate(BLOBS, 1):
        name = f'Run{index:06}.T000.D000.P000.H001.L.vec'
        record = records[index - 1]
        require(isinstance(record, dict), 'Invalid source record')
        require(record.get('file') == name, 'Unexpected source record order/name')
        raw = (directory / name).read_bytes()
        blob = hashlib.sha1(f'blob {len(raw)}\0'.encode('ascii') + raw).hexdigest()
        sha256 = digest(raw)
        require(blob == expected_blob == record.get('git_blob'), f'Git blob mismatch: {name}')
        require(sha256 == record.get('sha256'), f'Source SHA-256 mismatch: {name}')
        require(len(raw) == record.get('bytes'), f'Source length mismatch: {name}')
        lines = raw.decode('ascii').splitlines()
        require(bool(lines) and 'ZONE I=63, J=63' in lines[0], f'Unexpected header: {name}')
        require(len(lines[1:]) == 3969, f'Unexpected point count: {name}')
        for line in lines[1:]:
            values = [float(token) for token in line.split(',')]
            require(len(values) == 5 and all(math.isfinite(x) for x in values),
                    f'Unexpected numeric row: {name}')
            all_values.extend(struct.pack('<5d', *values))
            velocity_values.extend(struct.pack('<2d', *values[2:4]))
            quality_counts[str(values[4])] += 1
            for value in values[2:4]:
                if value == 0.0:
                    if math.copysign(1.0, value) < 0:
                        negative_zero += 1
                    else:
                        positive_zero += 1
        source_checks.append({'file': name, 'git_blob': blob, 'sha256': sha256,
                              'bytes': len(raw), 'identity': True})
    targets = {'all_columns': bytes(all_values), 'velocity_only': bytes(velocity_values)}
    diagnostics = {'chc_counts': dict(sorted(quality_counts.items())),
                   'velocity_positive_zero_values': positive_zero,
                   'velocity_negative_zero_values': negative_zero}
    return targets, source_checks, diagnostics


def decode_independent(packet, expected_shape, codec, method):
    """Invert packet XORs with separate sequential Python integer loops."""
    require(len(packet) >= 8 and packet[:4] == b'VTM1', 'Invalid packet magic')
    header_size = struct.unpack('<I', packet[4:8])[0]
    require(0 < header_size <= 4096 and 8 + header_size < len(packet), 'Invalid header length')
    meta = json.loads(packet[8:8 + header_size])
    require(isinstance(meta, dict), 'Invalid packet metadata')
    require(meta.get('shape') == expected_shape, 'Packet shape mismatch')
    require(meta.get('codec') == codec and meta.get('transform') == method,
            'Packet codec/transform mismatch')
    require(meta.get('dtype') == '<f8' and meta.get('order') == 'C',
            'Packet canonical representation mismatch')
    decompressor = {'gzip': gzip.decompress, 'bz2': bz2.decompress, 'lzma': lzma.decompress}[codec]
    # Packets are trusted benchmark artifacts. No bounded-decompression claim.
    residual = decompressor(packet[8 + header_size:])
    files, points, components = expected_shape
    require(len(residual) == files * points * components * 8, 'Residual length mismatch')
    words = [item[0] for item in struct.iter_unpack('<Q', residual)]
    if method == 'previous_file_xor':
        stride = points * components
        for i in range(stride, len(words)):
            words[i] ^= words[i - stride]
    elif method == 'previous_point_xor':
        for frame in range(files):
            for point in range(1, points):
                for component in range(components):
                    i = (frame * points + point) * components + component
                    words[i] ^= words[i - components]
    else:
        require(method == 'none', 'Unknown transform')
    decoded = b''.join(struct.pack('<Q', word) for word in words)
    require(digest(decoded) == meta.get('sha256'), 'Packet canonical checksum mismatch')
    return decoded


def check(data_directory, results_path):
    results_file = results_path / 'compression.json' if results_path.is_dir() else results_path
    report = json.loads(results_file.read_text(encoding='utf-8'))
    require(isinstance(report, dict), 'Invalid benchmark report')
    require(report.get('protocol_version') == '1.0.0', 'Unsupported protocol version')
    require(report.get('source_commit') == COMMIT, 'Source commit mismatch')
    targets, sources, diagnostics = read_targets(data_directory, report.get('sources'))
    rows = report.get('results')
    require(isinstance(rows, list) and len(rows) == 18, 'Expected exactly 18 packet records')
    expected = set(itertools.product(TARGET_SHAPES, CODECS, METHODS))
    seen, checked = set(), []
    for row in rows:
        require(isinstance(row, dict), 'Invalid packet result record')
        key = (row.get('target'), row.get('codec'), row.get('transform'))
        require(key in expected and key not in seen, 'Unexpected or duplicate packet record')
        seen.add(key)
        target, codec, method = key
        shape, raw = TARGET_SHAPES[target], targets[target]
        require(row.get('shape') == shape and row.get('raw_bytes') == len(raw),
                f'Result dimensions/length mismatch: {key}')
        require(row.get('canonical_sha256') == digest(raw), f'Result target checksum mismatch: {key}')
        require(row.get('byte_identity') is True, f'Result does not claim identity: {key}')
        name = f'{target}-{codec}-{method}.vtm'
        packet = (results_file.parent / name).read_bytes()
        require(len(packet) == row.get('packet_bytes'), f'Packet length mismatch: {name}')
        require(digest(packet) == row.get('packet_sha256'), f'Packet checksum mismatch: {name}')
        decoded = decode_independent(packet, shape, codec, method)
        require(decoded == raw, f'Independent byte comparison failed: {name}')
        checked.append({'file': name, 'packet_bytes': len(packet),
                        'packet_sha256': digest(packet), 'byte_identity': True})
    require(seen == expected, 'Incomplete packet matrix')
    return {'status': 'PASS', 'checker': 'independent-stdlib-1.0.0',
            'python': platform.python_version(), 'source_commit': COMMIT,
            'source_files_checked': len(sources), 'packets_checked': len(checked),
            'all_byte_identical': True, 'sources': sources,
            'canonical_targets': {name: {'bytes': len(raw), 'sha256': digest(raw)}
                                  for name, raw in targets.items()},
            'diagnostics': diagnostics, 'packets': checked,
            'scope': 'Trusted saved artifact identities and independent canonical-byte decoding only; '
                     'does not verify timing, memory, chronology, physical accuracy, or held-out gains.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data', type=Path, required=True)
    parser.add_argument('--results', type=Path, required=True,
                        help='Benchmark result directory or its compression.json file')
    parser.add_argument('--output', type=Path,
                        help='Optional new JSON file outside the benchmark results directory; never overwritten')
    args = parser.parse_args()
    try:
        if args.output:
            result_directory = args.results if args.results.is_dir() else args.results.parent
            require(not args.output.resolve().is_relative_to(result_directory.resolve()),
                    '--output must be outside the benchmark results directory')
            require(not args.output.exists(), '--output already exists; choose a new path')
        result = check(args.data, args.results)
        if args.output:
            # Deliberately do not create directories or mutate benchmark artifacts.
            with args.output.open('x', encoding='utf-8') as stream:
                json.dump(result, stream, indent=2)
                stream.write('\n')
        print(json.dumps({'status': result['status'], 'source_files_checked': 5,
                          'packets_checked': 18, 'all_byte_identical': True,
                          'output': str(args.output) if args.output else None}))
        return 0
    except (OSError, ValueError, KeyError, TypeError, EOFError, struct.error,
            lzma.LZMAError, zlib.error) as error:
        print(json.dumps({'status': 'FAIL', 'error': str(error)}))
        return 1


if __name__ == '__main__':
    sys.exit(main())
