"""Run the uart_tx self-test: python -m verif.smoke.run [verilog_source]

Exit status: 0 all passed, 1 a test failed, 2 nothing ran.
"""

import os
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

from cocotb_tools.runner import get_runner

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def main() -> int:
    source = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else HERE / "uart_tx.v"
    build_dir = Path(os.environ.get("BUILD_DIR", HERE / "sim_build")).resolve()
    runner = get_runner("icarus")
    runner.build(
        sources=[source],
        hdl_toplevel="uart_tx",
        build_dir=build_dir,
        timescale=("1ns", "1ps"),
        always=True,
    )
    results = runner.test(
        test_module="verif.smoke.test_uart_tx",
        hdl_toplevel="uart_tx",
        build_dir=build_dir,
        test_dir=build_dir,
        extra_env={
            "PYTHONPATH": os.pathsep.join(filter(None, [str(ROOT), os.environ.get("PYTHONPATH")])),
            "PROBE_DIR": str(build_dir / "probe"),
        },
    )
    tree = ET.parse(results)
    cases = tree.findall(".//testcase")
    failed = [c.get("name") for c in cases if c.find("failure") is not None or c.find("error") is not None]
    if not cases:
        print("no test cases ran", file=sys.stderr)
        return 2
    print(f"{len(cases) - len(failed)}/{len(cases)} passed" + (f"; failed: {failed}" if failed else ""))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
