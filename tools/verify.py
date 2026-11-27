#!/usr/bin/env python3
"""Run independently reproduced 2D checks and write a fresh evidence directory.

From the release root: python tools/verify.py --output results/run-new
The analytic/trajectory diagnostics use the standard library; the integrated
compression tests require NumPy (install requirements.txt). Exit 0 means all
unit tests and numerical acceptance checks passed with no skipped, expected-
failure or unexpected-success cases; exit 1 means verification failed; exit 2
means CLI usage/output-path failure. An existing output path is never reused.
"""
import argparse
import hashlib
import io
import json
from pathlib import Path
import platform
import sys
import unittest
from importlib.metadata import PackageNotFoundError, version

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT / "src"))
from vortex_thread.diagnostics import build_report


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output",required=True,type=Path,help="new output directory; must not exist")
    args = parser.parse_args(argv)
    output = args.output.resolve()
    try:
        output.mkdir(parents=True,exist_ok=False)
    except OSError as exc:
        parser.error(f"cannot create a fresh output directory: {exc}")
    stream = io.StringIO()
    suite = unittest.defaultTestLoader.discover(str(ROOT / "tests"),pattern="test_*.py")
    def collect_test_ids(group):
        for item in group:
            if isinstance(item,unittest.TestSuite):
                yield from collect_test_ids(item)
            else:
                yield item.id()
    test_ids = list(collect_test_ids(suite))
    test_groups = {}
    for test_id in test_ids:
        group = test_id.rsplit(".",1)[0]
        test_groups[group] = test_groups.get(group,0)+1
    result = unittest.TextTestRunner(stream=stream,verbosity=2).run(suite)
    report = None
    diagnostic_error = None
    try:
        report = build_report()
    except Exception as exc:
        diagnostic_error = f"{type(exc).__name__}: {exc}"
    passed = bool(result.wasSuccessful() and result.testsRun > 0
                  and not result.skipped and not result.expectedFailures
                  and not result.unexpectedSuccesses
                  and report and report["all_numerical_checks_passed"])
    summary = {"schema_version":1,"status":"PASS" if passed else "FAIL",
               "test_methods_run":result.testsRun,"failures":len(result.failures),
               "test_groups":test_groups,
               "errors":len(result.errors),"skipped":len(result.skipped),
               "expected_failures":len(result.expectedFailures),
               "unexpected_successes":len(result.unexpectedSuccesses),
               "numerical_acceptance_checks":len(report["numerical_acceptance_checks"]) if report else 0,
               "numerical_acceptance_failures":[k for k,v in report["numerical_acceptance_checks"].items() if not v] if report else [],
               "diagnostic_error":diagnostic_error,
               "counting_policy":"Each unittest method counts once. Samples, grid points, time steps, and acceptance checks are not extra tests.",
               "scope":"Discovered unittest methods are grouped by class; numerical acceptance checks cover the analytic 2D field, finite differences, passive RK4 trajectories, deformation and decay."}
    try:
        public_output = str(output.relative_to(ROOT)).replace("\\","/")
    except ValueError:
        public_output = "<external-output-directory>"
    try:
        numpy_version = version("numpy")
    except PackageNotFoundError:
        numpy_version = None
    environment = {"python_version":platform.python_version(),"python_implementation":platform.python_implementation(),
                   "platform":platform.platform(),"python_executable":sys.executable,
                   "dependencies":{"analytic_and_trajectory_diagnostics":"Python standard library",
                                   "integrated_compression_tests":{"numpy":numpy_version}},
                   "invocation":["python","tools/verify.py","--output",public_output],
                   "sources_sha256":{str(path.relative_to(ROOT)).replace("\\","/"):hashlib.sha256(path.read_bytes()).hexdigest()
                       for folder in ("src","tests","tools") for path in sorted((ROOT/folder).rglob("*.py"))}}
    # The exact machine command belongs in a private session log. Public evidence
    # needs versions and source hashes, without local account or install paths.
    environment["python_executable"] = Path(sys.executable).name
    for name,data in (("test-summary.json",summary),("environment.json",environment),("verification.json",report)):
        (output/name).write_text(json.dumps(data,indent=2,sort_keys=True,allow_nan=False)+"\n",encoding="utf-8")
    (output/"unittest.txt").write_text(stream.getvalue(),encoding="utf-8")
    print(f"{summary['status']}: {result.testsRun} test methods; {summary['numerical_acceptance_checks']} separate numerical acceptance checks")
    print(f"Evidence: {output}")
    if not passed:
        print(stream.getvalue(),file=sys.stderr)
        if diagnostic_error: print(diagnostic_error,file=sys.stderr)
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
