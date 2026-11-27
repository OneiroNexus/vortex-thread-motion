"""Bit-reversible baseline transforms, not a flow predictor or a new codec.

Canonical input is a C-order (files, points, components) little-endian uint64
view of IEEE-754 binary64 coordinates/values. XOR preserves every bit, including
negative zero and NaN payloads; no floating-point arithmetic is used to decode.
"""
import bz2
import gzip
import hashlib
import json
import lzma
import struct
import numpy as np

MAGIC = b'VTM1'
TRANSFORMS = ('none', 'previous_file_xor', 'previous_point_xor')
CODECS = ('gzip', 'bz2', 'lzma')

def transform(words, method):
    a = np.asarray(words, dtype='<u8')
    if a.ndim != 3 or any(n < 1 for n in a.shape):
        raise ValueError('Expected nonempty (files, points, components) array')
    out = a.copy()
    if method == 'previous_file_xor':
        out[1:] = a[1:] ^ a[:-1]
    elif method == 'previous_point_xor':
        out[:, 1:] = a[:, 1:] ^ a[:, :-1]
    elif method != 'none':
        raise ValueError('Unknown transform')
    return out

def inverse(words, method):
    a = np.asarray(words, dtype='<u8')
    if method == 'none':
        return a.copy()
    if method == 'previous_file_xor':
        return np.bitwise_xor.accumulate(a, axis=0)
    if method == 'previous_point_xor':
        return np.bitwise_xor.accumulate(a, axis=1)
    raise ValueError('Unknown transform')

def encode(words, method, codec):
    a = np.asarray(words, dtype='<u8')
    raw = a.tobytes(order='C')
    residual = transform(a, method).tobytes(order='C')
    if codec == 'gzip':
        body = gzip.compress(residual, compresslevel=6, mtime=0)
    elif codec == 'bz2':
        body = bz2.compress(residual, compresslevel=9)
    elif codec == 'lzma':
        body = lzma.compress(residual, format=lzma.FORMAT_XZ, preset=6)
    else:
        raise ValueError('Unknown codec')
    metadata = {'codec': codec, 'dtype': '<f8', 'order': 'C', 'shape': list(a.shape),
                'transform': method, 'sha256': hashlib.sha256(raw).hexdigest()}
    header = json.dumps(metadata, sort_keys=True, separators=(',', ':')).encode('ascii')
    return MAGIC + struct.pack('<I', len(header)) + header + body

def decode(packet):
    """Decode trusted benchmark packets. This is not an untrusted-input service."""
    if len(packet) < 8 or packet[:4] != MAGIC:
        raise ValueError('Invalid packet magic')
    length = struct.unpack('<I', packet[4:8])[0]
    if length > 4096 or len(packet) <= 8 + length:
        raise ValueError('Invalid header length')
    meta = json.loads(packet[8:8 + length])
    shape = meta.get('shape')
    if not isinstance(shape, list) or len(shape) != 3 or not all(type(n) is int and n > 0 for n in shape):
        raise ValueError('Invalid dimensions')
    if meta.get('dtype') != '<f8' or meta.get('order') != 'C' or meta.get('transform') not in TRANSFORMS:
        raise ValueError('Unsupported canonical representation')
    count = shape[0] * shape[1] * shape[2]
    if count > 10_000_000:
        raise ValueError('Packet exceeds benchmark size limit')
    body = packet[8 + length:]
    codec = meta.get('codec')
    if codec == 'gzip':
        residual = gzip.decompress(body)
    elif codec == 'bz2':
        residual = bz2.decompress(body)
    elif codec == 'lzma':
        residual = lzma.decompress(body)
    else:
        raise ValueError('Unsupported codec')
    if len(residual) != count * 8:
        raise ValueError('Residual size mismatch')
    a = np.frombuffer(residual, dtype='<u8').reshape(shape)
    raw = inverse(a, meta['transform']).astype('<u8', copy=False).tobytes(order='C')
    if hashlib.sha256(raw).hexdigest() != meta['sha256']:
        raise ValueError('Decoded checksum mismatch')
    return raw
