# Third-party sources

The paper bibliography and `docs/references.json` credit the underlying research. Those articles and their images are not redistributed in this package.

The optional snapshot control downloads five files from PIVPy at commit `be5e26a17e0d61f7113ec87e98ffcc0d443c297f`. Exact file paths, Git object identities, byte lengths and SHA-256 hashes are recorded in `results/compression-2026-11-26/compression.json`. The pinned upstream repository carries a BSD 3-clause license, copyright 2014- Turbulence Structure Laboratory, Tel Aviv University:

https://github.com/alexlib/pivpy/blob/be5e26a17e0d61f7113ec87e98ffcc0d443c297f/LICENSE

The upstream license and any applicable data terms remain with those sources. Raw `.vec` files and generated packets containing their values are not included in the published-file selection; users fetch the exact sources through the supplied integrity-checking command. This package contains independently written baseline code, measured summaries, and figures derived from aggregate results. No endorsement by PIVPy, TSI, the cited authors or their institutions is implied.

Python, NumPy, ReportLab, Matplotlib, pypdf and their dependencies retain their own licenses. They are installed separately and are not bundled into the release archive. The build embeds DejaVu font subsets from Matplotlib; the DejaVu fonts are distributed under the Bitstream Vera license with DejaVu changes in the public domain. See `docs/DEJAVU_FONT_LICENSE.txt`.

