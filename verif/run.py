"""Run simulation suites.

    python -m verif.run                      # all suites
    python -m verif.run smoke other          # named suites
    python -m verif.run smoke --replace verif/smoke/uart_tx.v=mutated.v

Exit status: 0 all passed, 1 a test failed, 2 a suite ran no tests.
"""

import argparse
import os
import sys
from pathlib import Path

from verif.lib import runner
from verif.suites import SUITES


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("suites", nargs="*")
    ap.add_argument("--replace", action="append", default=[], metavar="SRC=FILE")
    ap.add_argument("--build-dir", default=os.environ.get("BUILD_DIR", "sim_build"))
    ap.add_argument("--testcase")
    ap.add_argument("--seed", type=int)
    args = ap.parse_args()

    names = args.suites or sorted(SUITES)
    unknown = [n for n in names if n not in SUITES]
    if unknown:
        ap.error(f"unknown suites: {', '.join(unknown)}; known: {', '.join(sorted(SUITES))}")
    replace = dict(r.split("=", 1) for r in args.replace)

    worst = runner.PASSED
    for name in names:
        status = runner.run(SUITES[name], Path(args.build_dir), replace=replace,
                            testcase=args.testcase, seed=args.seed)
        worst = max(worst, status)
    return worst


if __name__ == "__main__":
    sys.exit(main())
