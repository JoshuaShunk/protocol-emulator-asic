"""Decode probe VCDs with sigrok-cli.

sigrok-cli exits 0 even when a decoder reports errors, so each decode also
collects the decoder's error annotations and check() fails on them.
"""

from __future__ import annotations

import os
import re
import shutil
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Sequence

ERROR_CLASSES: Dict[str, Sequence[str]] = {
    "uart": ("rx-warnings", "tx-warnings", "rx-parity-err", "tx-parity-err"),
    "spi": ("warnings",),
    "i2c": ("warnings",),
}

_LINE = re.compile(r"^(\d+)-(\d+) [\w-]+: (.*)$")


@dataclass
class Annotation:
    start_ns: int
    end_ns: int
    text: str


@dataclass
class Decode:
    data: List[Annotation] = field(default_factory=list)
    errors: List[Annotation] = field(default_factory=list)

    def values(self) -> List[str]:
        return [a.text for a in self.data]

    def check(self) -> "Decode":
        if self.errors:
            listing = "; ".join(f"{e.start_ns}ns: {e.text}" for e in self.errors)
            raise AssertionError(f"sigrok reported protocol errors: {listing}")
        return self


def _sigrok_cli() -> str:
    path = shutil.which("sigrok-cli")
    if path is None:
        raise RuntimeError("sigrok-cli not found on PATH (brew install sigrok-cli)")
    return path


def _run(vcd: Path, decoder_spec: str, decoder: str, classes: Sequence[str]) -> List[Annotation]:
    cmd = [
        _sigrok_cli(),
        "-i", str(vcd),
        "-I", "vcd",
        "-P", decoder_spec,
        "-A", f"{decoder}=" + ":".join(classes),
        "--protocol-decoder-samplenum",
    ]
    # sigrok-cli embeds Python; the simulator's PYTHON* variables break it.
    env = {k: v for k, v in os.environ.items() if not k.startswith("PYTHON")}
    proc = subprocess.run(cmd, capture_output=True, text=True, env=env)
    if proc.returncode != 0:
        raise RuntimeError(f"sigrok-cli failed ({proc.returncode}): {' '.join(cmd)}\n{proc.stderr}")
    out = []
    for line in proc.stdout.splitlines():
        m = _LINE.match(line)
        if not m:
            raise RuntimeError(f"unexpected sigrok-cli output line: {line!r}")
        out.append(Annotation(int(m.group(1)), int(m.group(2)), m.group(3)))
    return out


def decode(
    vcd: Path,
    decoder: str,
    channels: Dict[str, str],
    data_classes: Sequence[str],
    options: Dict[str, object] | None = None,
) -> Decode:
    """channels maps decoder channel names to probe channel names, e.g. {"rx": "uart_tx"}."""
    if decoder not in ERROR_CLASSES:
        raise ValueError(f"no error classes registered for decoder {decoder!r}")
    args = [f"{k}={v}" for k, v in channels.items()]
    args += [f"{k}={v}" for k, v in (options or {}).items()]
    spec = ":".join([decoder] + args)
    return Decode(
        data=_run(Path(vcd), spec, decoder, data_classes),
        errors=_run(Path(vcd), spec, decoder, ERROR_CLASSES[decoder]),
    )


def uart(vcd: Path, line: str, baudrate: int, direction: str = "rx", **options) -> Decode:
    return decode(vcd, "uart", {direction: line}, [f"{direction}-data"],
                  {"baudrate": baudrate, **options})


def spi(vcd: Path, clk: str, mosi: str | None = None, miso: str | None = None,
        cs: str | None = None, **options) -> Decode:
    channels = {"clk": clk}
    classes = []
    if mosi:
        channels["mosi"] = mosi
        classes.append("mosi-data")
    if miso:
        channels["miso"] = miso
        classes.append("miso-data")
    if cs:
        channels["cs"] = cs
    return decode(vcd, "spi", channels, classes, options)


def i2c(vcd: Path, scl: str, sda: str, **options) -> Decode:
    return decode(vcd, "i2c", {"scl": scl, "sda": sda},
                  ["start", "repeat-start", "stop", "ack", "nack",
                   "address-read", "address-write", "data-read", "data-write"],
                  options)
