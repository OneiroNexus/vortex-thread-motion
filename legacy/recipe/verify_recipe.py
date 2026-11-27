#!/usr/bin/env python3
"""Verify preserved authored-coordinate replay without rendering media.

Native full-byte agreement is required. The historical Linux checksum is a
separate comparison and may differ on another platform; the JSON states both.
"""
import argparse
import ast
import gzip
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import tempfile
import zipfile
import zlib
import numpy as np

ROOT = Path(__file__).resolve().parent
EXPECTED_SOURCES = {
    "decode.py":"471b052b49d988d6d51f12b5a392cd942a32b56c2d5d71b22a88cb01a6cc8aee",
    "recipe.json":"892616e432d3b1e423684d8899c6d14bf6c48b3401a8768430da6c3b681de6a1",
    "reference/render.py":"f9f7a7fe55731a6a00f7e31e972e5290e92ff2e8fa277836095b3cc0de1bd921",
    "reference/compare.py":"858ff9b21beb3c002849ddfe592662f7a8cef613e12a743df1e9be54be9b8fd1",
    "results.json":"c883c91503803faa78388cf4b0f82cf207680af96b7429d02b175731fc428997",
    "HISTORICAL-README.md":"e5a12a2d247320ac4f3cc5df2b7a4c8b02360ba808f2f5fcfe7c09964da905a3"}


def digest(items):
    h,size = hashlib.sha256(),0
    for item in items:
        h.update(item)
        size += len(item)
    return h.hexdigest(),size


def renderer_math():
    source = (ROOT/"reference/render.py").read_text()
    preamble = source.split("proc=subprocess.Popen",1)[0]
    tree = ast.parse(preamble)
    nodes,excluded = [],[]
    font_names = {"font","title","subtitle","f","small","pill"}
    for node in tree.body:
        if isinstance(node,ast.ImportFrom) and node.module == "PIL":
            excluded.append("PIL import")
            continue
        names = {t.id for t in getattr(node,"targets",[]) if isinstance(t,ast.Name)}
        if names and names <= font_names:
            excluded.extend(sorted(names))
            continue
        nodes.append(node)
    if set(excluded) != font_names | {"PIL import"}:
        raise ValueError("Unexpected renderer prelude; refusing to adapt it")
    namespace = {}
    exec(compile(ast.Module(body=nodes,type_ignores=[]),"preserved-renderer-math","exec"),namespace)
    return namespace,excluded


def reference(namespace):
    # Same two-panel sampling and override n=240 used by archived benchmark.py.
    p,seeds = namespace["P"].copy(),namespace["seeds"].copy()
    n = 240
    dt = namespace["tf"]/(n-1)
    for i in range(n):
        s,t = i/(n-1),i*dt
        for surface in (0,s):
            for points in (p,seeds):
                yield np.asarray(np.stack(namespace["shape"](points,surface),axis=-1),dtype="<f8",order="C").tobytes()
        p,seeds = namespace["step"](p,t,dt),namespace["step"](seeds,t,dt)


def verify():
    sources = {name:hashlib.sha256((ROOT/name).read_bytes()).hexdigest() for name in EXPECTED_SOURCES}
    if sources != EXPECTED_SOURCES:
        raise ValueError("Preserved source checksum mismatch")
    history = json.loads((ROOT/"results.json").read_text())
    recipe = json.loads((ROOT/"recipe.json").read_text())
    namespace,excluded = renderer_math()
    loader = importlib.util.spec_from_file_location("preserved_decoder",ROOT/"decode.py")
    decoder = importlib.util.module_from_spec(loader)
    loader.loader.exec_module(decoder)
    checks = {"preserved_source_hashes":True}
    with tempfile.TemporaryDirectory(prefix="vortex-replay-") as scratch:
        work = Path(scratch)
        refpath,decoded = work/"reference.xyz64le",work/"decoded.xyz64le"
        with refpath.open("xb") as output:
            for item in reference(namespace): output.write(item)
        with refpath.open("rb") as f:
            refhash = hashlib.file_digest(f,"sha256").hexdigest()
        # An isolated process executes the exact preserved decoder without edits.
        run = subprocess.run([sys.executable,str(ROOT/"decode.py"),str(ROOT/"recipe.json"),
                              "--output",str(decoded)],capture_output=True,text=True,check=True)
        with refpath.open("rb") as a,decoded.open("rb") as b:
            checks["full_native_reference_decoder_byte_identity"] = all(
                chunk == b.read(len(chunk)) for chunk in iter(lambda:a.read(1<<20),b"")) and not b.read(1)
        native_bytes = refpath.stat().st_size
        checks["canonical_size_matches_history"] = native_bytes == history["reference_bytes"] == decoded.stat().st_size
        gzpath = work/"reference.gz"
        with gzpath.open("xb") as f,gzip.GzipFile(filename="",fileobj=f,mode="wb",compresslevel=6,mtime=0) as gz,refpath.open("rb") as data:
            shutil.copyfileobj(data,gz,1<<20)
        def read_gzip():
            with gzip.open(gzpath,"rb") as f:
                yield from iter(lambda:f.read(1<<20),b"")
        checks["gzip_round_trip_hash_and_size"] = digest(read_gzip()) == (refhash,native_bytes)
        gzip_bytes = gzpath.stat().st_size
        checks["changed_seed_changes_hash"] = digest(decoder.generate({**recipe,"seed":118}))[0] != refhash
        edited = hashlib.sha256()
        with decoded.open("rb") as data:
            first = bytearray(data.read(1<<20)); first[8] ^= 1; edited.update(first)
            for chunk in iter(lambda:data.read(1<<20),b""): edited.update(chunk)
        checks["one_bit_coordinate_edit_changes_hash"] = edited.hexdigest() != refhash
        archive = io.BytesIO()
        with zipfile.ZipFile(archive,"w",compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
            for name in ("recipe.json","decode.py"): z.writestr(name,(ROOT/name).read_bytes())
        zip_bytes = len(archive.getvalue())
    match = refhash == history["expected_sha256"]
    return {"schema_version":1,"status":"PASS" if all(checks.values()) else "FAIL",
            "scope":"Authored pre-camera geometry replay only; no video rendering, physical cloud simulation, external-data flow predictor or general compression validation.",
            "environment":{"python":platform.python_version(),"numpy":np.__version__,
                           "system":platform.system(),"machine":platform.machine(),"zlib_runtime":zlib.ZLIB_RUNTIME_VERSION},
            "adapter":{"excluded_statements":excluded,"coordinate_math_unchanged":True,
                       "description":"PIL/font initialization and the rendering loop are not executed; preserved renderer coordinate definitions feed the archived two-panel sampling order."},
            "source_sha256":sources,"checker_sha256":hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            "native_checks":checks,"native_bytes":native_bytes,"native_sha256":refhash,
            "decoder_stdout":run.stdout.strip(),
            "historical_sha256":history["expected_sha256"],"historical_digest_matched":match,
            "historical_comparison_note":"Historical checksum matched on this runtime." if match else "Historical Linux checksum NOT reproduced on this runtime; native decoder/reference identity is a separate result.",
            "native_gzip_level6_bytes":gzip_bytes,"historical_gzip_level6_bytes":history["gzip_level6_bytes"],
            "recipe_bytes":(ROOT/"recipe.json").stat().st_size,"decoder_bytes":(ROOT/"decode.py").stat().st_size,
            "recipe_plus_decoder_zip_bytes":zip_bytes,"historical_recipe_plus_decoder_zip_bytes":1597,
            "accounting":"Recipe assumes a shared compatible decoder. Two-entry ZIP includes recipe and decoder source, excluding Python/NumPy/runtime dependencies. Temporary coordinate streams are removed after checking."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output",type=Path,required=True,help="fresh report directory; must not exist")
    args = parser.parse_args()
    try:
        args.output.mkdir(parents=True,exist_ok=False)
    except OSError as exc:
        parser.error(f"Cannot create fresh output directory: {exc}")
    try:
        report = verify()
    except Exception as exc:
        report = {"schema_version":1,"status":"FAIL","error_type":type(exc).__name__,
                  "error":"Replay failed; inspect the local process error. Absolute machine paths are omitted from the public report."}
        print(f"{type(exc).__name__}: {exc}",file=sys.stderr)
    (args.output/"replay.json").write_text(json.dumps(report,indent=2,sort_keys=True)+"\n",encoding="utf8")
    print(json.dumps({"status":report["status"],"historical_digest_matched":report.get("historical_digest_matched"),
                      "native_sha256":report.get("native_sha256")}))
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
