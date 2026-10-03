"""Edge-timing checks on probe events (protocol decoders tolerate timing errors)."""

from __future__ import annotations

from typing import Iterable, List, Tuple

Event = Tuple[int, str, int]


def edges(events: Iterable[Event], channel: str) -> List[Tuple[int, int]]:
    """(time_ns, new_value) for each change of one probe channel, initial value excluded."""
    out = [(t, v) for t, name, v in events if name == channel]
    return out[1:]


def check_frames(events: Iterable[Event], channel: str, unit_ns: int, frame_units: int,
                 idle: int = 1, tolerance_ns: int = 0) -> int:
    """Start-bit framed timing (UART-style). A frame starts on an edge leaving the
    idle level; every edge inside the frame lies a whole number of units after the
    start, the last unit is at the idle level, and no frame starts before the
    previous one ends. Returns the number of frames checked."""
    changes = edges(events, channel)
    problems = []
    frames = 0
    i = 0
    while i < len(changes):
        t0, v0 = changes[i]
        if v0 == idle:
            problems.append(f"edge to idle level at {t0} ns outside a frame")
            i += 1
            continue
        frames += 1
        end = t0 + frame_units * unit_ns
        i += 1
        level = v0
        while i < len(changes) and changes[i][0] < end - tolerance_ns:
            t, v = changes[i]
            offset = t - t0
            k = round(offset / unit_ns)
            if abs(offset - k * unit_ns) > tolerance_ns:
                problems.append(f"edge at {t} ns is {offset} ns into a frame, not a multiple of {unit_ns} ns")
            if k >= frame_units:
                break
            if k == frame_units - 1 and v != idle:
                problems.append(f"frame starting at {t0} ns leaves the idle level in its last unit")
            level = v
            i += 1
        if level != idle:
            problems.append(f"frame starting at {t0} ns does not end at the idle level")
    if problems:
        raise AssertionError(f"{channel}: {len(problems)} timing problem(s): " + "; ".join(problems[:6]))
    if frames == 0:
        raise AssertionError(f"{channel}: no frames seen")
    return frames
