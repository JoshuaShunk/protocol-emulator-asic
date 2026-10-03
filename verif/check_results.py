"""Fail unless results.xml exists, has at least one test case, and none failed."""

import sys
import xml.etree.ElementTree as ET
from pathlib import Path


def main(path: str) -> int:
    results = Path(path)
    if not results.is_file():
        print(f"{results}: missing (simulation did not run)", file=sys.stderr)
        return 1
    cases = ET.parse(results).findall(".//testcase")
    bad = [c.get("name") for c in cases if c.find("failure") is not None or c.find("error") is not None]
    if not cases:
        print(f"{results}: no test cases ran", file=sys.stderr)
        return 1
    print(f"{results}: {len(cases) - len(bad)}/{len(cases)} passed")
    if bad:
        print(f"failed: {', '.join(bad)}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else "results.xml"))
