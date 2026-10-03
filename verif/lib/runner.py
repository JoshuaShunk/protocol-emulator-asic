"""Build and run one cocotb suite with Icarus."""

from __future__ import annotations

import os
import sys
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Sequence

from cocotb_tools.runner import get_runner

ROOT = Path(__file__).resolve().parents[2]

PASSED, FAILED, NOTHING_RAN = 0, 1, 2


@dataclass
class Suite:
    name: str
    sources: Sequence[str]
    toplevel: str
    test_module: str
    parameters: Dict[str, object] = field(default_factory=dict)
    defines: Dict[str, object] = field(default_factory=dict)
    includes: Sequence[str] = ()


def run(suite: Suite, build_root: Path, replace: Dict[str, Path] | None = None,
        testcase: str | None = None, seed: int | None = None) -> int:
    """Return PASSED, FAILED or NOTHING_RAN. replace maps a source path (as listed
    in the suite, relative to the repository root) to a substitute file."""
    replace = {k: Path(v).resolve() for k, v in (replace or {}).items()}
    unknown = set(replace) - set(suite.sources)
    if unknown:
        raise ValueError(f"{suite.name}: replacement for unknown sources {sorted(unknown)}")
    sources = [replace.get(s, ROOT / s) for s in suite.sources]
    build_dir = (build_root / suite.name).resolve()

    runner = get_runner("icarus")
    runner.build(
        sources=sources,
        hdl_toplevel=suite.toplevel,
        build_dir=build_dir,
        parameters=suite.parameters,
        defines=suite.defines,
        includes=[ROOT / i for i in suite.includes],
        timescale=("1ns", "1ps"),
        always=True,
    )
    results = runner.test(
        test_module=suite.test_module,
        hdl_toplevel=suite.toplevel,
        build_dir=build_dir,
        test_dir=build_dir,
        testcase=testcase,
        seed=seed,
        extra_env={
            "PYTHONPATH": os.pathsep.join(filter(None, [str(ROOT), os.environ.get("PYTHONPATH")])),
            "PROBE_DIR": str(build_dir / "probe"),
        },
    )
    cases = ET.parse(results).findall(".//testcase")
    failed = [c.get("name") for c in cases if c.find("failure") is not None or c.find("error") is not None]
    if not cases:
        print(f"{suite.name}: no test cases ran", file=sys.stderr)
        return NOTHING_RAN
    print(f"{suite.name}: {len(cases) - len(failed)}/{len(cases)} passed"
          + (f"; failed: {', '.join(failed)}" if failed else ""))
    return FAILED if failed else PASSED
