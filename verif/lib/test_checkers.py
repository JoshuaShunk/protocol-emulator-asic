"""Unit tests for the waveform checkers: python -m pytest verif/lib"""

import pytest

from verif.lib import sigrok, timing

T = 100  # ns per bit


def uart_events(frames, start=1000, gap=300, stop_units=1, start_units=1, channel="tx"):
    """Probe events for 8N1 frames; start_units/stop_units let tests distort timing."""
    events = [(0, channel, 1)]
    t = start
    level = 1
    for byte in frames:
        bits = [0] * start_units + [(byte >> i) & 1 for i in range(8)] + [1] * stop_units
        for b in bits:
            if b != level:
                events.append((t, channel, b))
                level = b
            t += T
        t += gap
    return events, t


def write_vcd(path, events, end):
    with open(path, "w") as f:
        f.write("$timescale 1ns $end\n$scope module probe $end\n$var wire 1 ! tx $end\n$upscope $end\n$enddefinitions $end\n")
        for t, _, v in events:
            f.write(f"#{t}\n{v}!\n")
        f.write(f"#{end}\n")


def test_frames_pass():
    events, _ = uart_events([0x00, 0xFF, 0x55, 0xA5])
    assert timing.check_frames(events, "tx", T, 10) == 4


def test_short_start_bit_fails():
    events, _ = uart_events([0x01])
    shifted = [(t - 20 if t > 1000 else t, c, v) for t, c, v in events]
    with pytest.raises(AssertionError, match="not a multiple"):
        timing.check_frames(shifted, "tx", T, 10)


def test_missing_stop_bit_fails():
    events, _ = uart_events([0x80], stop_units=0, gap=0)
    events.append((events[-1][0] + 2 * T, "tx", 1))
    with pytest.raises(AssertionError):
        timing.check_frames(events, "tx", T, 10)


def test_no_frames_fails():
    with pytest.raises(AssertionError, match="no frames"):
        timing.check_frames([(0, "tx", 1)], "tx", T, 10)


def test_sigrok_decodes_bytes(tmp_path):
    events, end = uart_events([0x41, 0x5A, 0x00, 0xFF])
    vcd = tmp_path / "ok.vcd"
    write_vcd(vcd, events, end + 2000)
    decoded = sigrok.uart(vcd, "tx", 1_000_000_000 // T).check()
    assert [int(v, 16) for v in decoded.values()] == [0x41, 0x5A, 0x00, 0xFF]


def test_sigrok_reports_framing_error(tmp_path):
    events, end = uart_events([0x41], stop_units=0, gap=0)
    events.append((end + 3 * T, "tx", 1))
    vcd = tmp_path / "bad.vcd"
    write_vcd(vcd, events, end + 4000)
    with pytest.raises(AssertionError, match="Frame error"):
        sigrok.uart(vcd, "tx", 1_000_000_000 // T).check()
