"""Fetch five pinned public PIVPy fixtures and verify Git object identities.

The fixture files remain separate from the release archive. Their headers include
an acquisition pulse interval; this does not establish spacing between files.
"""
from pathlib import Path
import argparse
import hashlib
import json
import urllib.request

COMMIT = 'be5e26a17e0d61f7113ec87e98ffcc0d443c297f'
BLOBS = ['8597bf2dbcaa9e31ac70b508016e83db2ac84192', '207c98a3b98569f962cfc95bba39e99ac2b37b21', '59abbb5b4821137af6b28f86fa0796168030c9bd', '120b7f7e14fb6a637309c2c701f369040dacd5a7', '280b5e79978446849cabe6621848f04700791c06']

def fetch(destination):
    destination.mkdir(parents=True, exist_ok=True)
    rows = []
    for n, expected in enumerate(BLOBS, 1):
        name = f'Run{n:06}.T000.D000.P000.H001.L.vec'
        url = f'https://raw.githubusercontent.com/alexlib/pivpy/{COMMIT}/pivpy/data/Insight/{name}'
        path = destination / name
        data = path.read_bytes() if path.exists() else urllib.request.urlopen(url, timeout=60).read()
        actual = hashlib.sha1(f'blob {len(data)}\0'.encode() + data).hexdigest()
        if actual != expected:
            raise ValueError(f'Pinned Git blob mismatch: {name}')
        if not path.exists():
            with path.open('xb') as f:
                f.write(data)
        rows.append({'file': name, 'url': url, 'git_blob': actual, 'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest()})
    manifest = {'source_commit': COMMIT, 'files': rows}
    out = destination / 'source-manifest.json'
    payload = json.dumps(manifest, indent=2) + '\n'
    if out.exists() and out.read_text(encoding='utf-8') != payload:
        raise ValueError('Existing manifest differs; choose a new directory.')
    if not out.exists():
        out.write_text(payload, encoding='utf-8')
    return manifest

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    result = fetch(args.output)
    print(json.dumps({'status': 'PASS', 'files': len(result['files']), 'source_commit': COMMIT}))
