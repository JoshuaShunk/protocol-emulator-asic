"""Exit non-zero if the simulator, cocotb, or sigrok-cli on PATH is not the pinned one."""

import shutil
import subprocess
import sys

EXPECTED_COCOTB = "2.0.1"
EXPECTED_ICARUS = "Icarus Verilog runtime version 13.0 (stable)"


def main() -> int:
    problems = []

    import cocotb

    if cocotb.__version__ != EXPECTED_COCOTB:
        problems.append(f"cocotb {cocotb.__version__} from {cocotb.__file__}, expected {EXPECTED_COCOTB}")

    vvp = shutil.which("vvp")
    if vvp is None:
        problems.append("vvp not on PATH")
    else:
        with open(vvp, "rb") as f:
            if f.read(2) == b"#!":
                problems.append(f"vvp at {vvp} is a wrapper script (OSS CAD Suite?), not the Icarus binary")
        proc = subprocess.run([vvp, "-V"], capture_output=True, text=True)
        version = (proc.stdout + proc.stderr).splitlines()[:1]
        if not version or not version[0].startswith(EXPECTED_ICARUS):
            problems.append(f"vvp reports {version}, expected {EXPECTED_ICARUS!r}")

    if shutil.which("sigrok-cli") is None:
        problems.append("sigrok-cli not on PATH")

    for p in problems:
        print(f"preflight: {p}", file=sys.stderr)
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
