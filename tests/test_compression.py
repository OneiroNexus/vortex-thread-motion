"""Checks exact word reversibility, special bit patterns and corruption rejection."""
from pathlib import Path
import sys
import unittest
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from vortex_thread.compression import CODECS, TRANSFORMS, transform, inverse, encode, decode

class CompressionTests(unittest.TestCase):
    def test_transform_inverses_random_words(self):
        rng = np.random.default_rng(2601)
        words = rng.integers(0, 2**64, size=(5, 37, 5), dtype=np.uint64)
        for method in TRANSFORMS:
            with self.subTest(method=method):
                self.assertEqual(inverse(transform(words, method), method).tobytes(), words.tobytes())

    def test_exact_special_ieee_bit_patterns(self):
        words = np.array([0, 0x8000000000000000, 0x7ff0000000000000, 0xfff0000000000000,
                          0x7ff8000000000001, 0x7ff8000000000002, 1, 0x8000000000000001,
                          0x3ff0000000000000, 0x3fefffffffffffff, 0x0010000000000000,
                          0x000fffffffffffff], dtype='<u8').reshape(2, 2, 3)
        for codec in CODECS:
            for method in TRANSFORMS:
                with self.subTest(codec=codec, method=method):
                    self.assertEqual(decode(encode(words, method, codec)), words.tobytes())

    def test_singleton_axes(self):
        for shape in [(1, 1, 1), (1, 7, 2), (3, 1, 4)]:
            a = np.arange(np.prod(shape), dtype='<u8').reshape(shape)
            for method in TRANSFORMS:
                self.assertEqual(decode(encode(a, method, 'gzip')), a.tobytes())

    def test_bad_input_rejected(self):
        for a in [np.zeros(3, dtype='<u8'), np.zeros((1, 0, 1), dtype='<u8')]:
            with self.assertRaises(ValueError):
                encode(a, 'none', 'gzip')
        a = np.zeros((1, 1, 1), dtype='<u8')
        with self.assertRaises(ValueError):
            encode(a, 'unknown', 'gzip')
        with self.assertRaises(ValueError):
            encode(a, 'none', 'unknown')

    def test_corrupt_header_and_digest_rejected(self):
        a = np.arange(12, dtype='<u8').reshape(2, 2, 3)
        packet = encode(a, 'previous_file_xor', 'gzip')
        for bad in [b'', b'xxxx' + packet[4:], packet[:5], packet[:-10]]:
            with self.assertRaises((ValueError, EOFError, OSError)):
                decode(bad)
        import hashlib
        digest = hashlib.sha256(a.tobytes()).hexdigest().encode()
        wrong = (b'0' if digest[:1] != b'0' else b'1') + digest[1:]
        with self.assertRaisesRegex(ValueError, 'checksum'):
            decode(packet.replace(digest, wrong))

if __name__ == '__main__':
    unittest.main()
