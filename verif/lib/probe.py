"""Record 1-bit channels during a cocotb test and write them to a 1 ns VCD."""

from __future__ import annotations

from pathlib import Path
from typing import Callable, Dict, Iterable, List, Tuple

import cocotb
from cocotb.triggers import ReadOnly
from cocotb.utils import get_sim_time


def bit(handle, index: int | None = None) -> Callable[[], int]:
    """One bit of a signal; x/z raises."""

    def read() -> int:
        value = handle.value
        if index is not None:
            value = value[index]
        if not value.is_resolvable:
            raise ValueError(f"{handle._name}[{index}] is {value}, not 0/1")
        return int(value)

    return read


def open_drain(*drivers: Callable[[], int]) -> Callable[[], int]:
    """Open-drain line with pull-up: low if any driver is low."""

    def read() -> int:
        return int(all(d() for d in drivers))

    return read


class Probe:
    def __init__(self, channels: Dict[str, Callable[[], int]], watch: Iterable):
        self.channels = channels
        self.watch = list(watch)
        self.events: List[Tuple[int, str, int]] = []
        self._last: Dict[str, int] = {}
        self._tasks = []

    def start(self) -> "Probe":
        self._sample()
        for handle in self.watch:
            self._tasks.append(cocotb.start_soon(self._follow(handle)))
        return self

    def stop(self) -> None:
        for task in self._tasks:
            task.cancel()
        self._tasks.clear()

    async def _follow(self, handle) -> None:
        while True:
            await handle.value_change
            await ReadOnly()
            self._sample()

    def _sample(self) -> None:
        now = int(get_sim_time("ns"))
        for name, read in self.channels.items():
            value = read()
            if self._last.get(name) != value:
                self._last[name] = value
                self.events.append((now, name, value))

    def write_vcd(self, path: Path, end_ns: int | None = None) -> Path:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        ids = {name: chr(33 + i) for i, name in enumerate(self.channels)}
        end = int(get_sim_time("ns")) if end_ns is None else end_ns
        with path.open("w") as f:
            f.write("$timescale 1ns $end\n$scope module probe $end\n")
            for name, ident in ids.items():
                f.write(f"$var wire 1 {ident} {name} $end\n")
            f.write("$upscope $end\n$enddefinitions $end\n")
            current = None
            for t, name, value in self.events:
                if t != current:
                    f.write(f"#{t}\n")
                    current = t
                f.write(f"{value}{ids[name]}\n")
            if current is None or end > current:
                f.write(f"#{end}\n")
        return path
