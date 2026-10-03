"""Receiver models: edge-timestamp decoding with and without sub-cycle timestamps.

Times are in nanoseconds. The chip clock has period CLK_NS; an input edge is seen
by the synchroniser at the first clock edge after it. A TDC channel also
reports where in that clock period the edge occurred, quantised to tdc_lsb_ns.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass
from typing import List, Sequence, Tuple

CLK_NS = 20.0


@dataclass
class Link:
    bit_ns: float          # nominal bit period
    ppm: float = 0.0       # transmitter frequency error
    jitter_ns: float = 0.0  # Gaussian edge jitter (sigma)
    min_pulse_ns: float = 0.0  # input path bandwidth: shorter pulses are swallowed


@dataclass
class Receiver:
    tdc_lsb_ns: float | None = None   # None: whole-cycle timestamps only
    tdc_cal_err_ns: float = 0.0       # sigma of residual calibration error per edge
    multi_hit: bool = False           # delay line covers a full cycle: every edge is kept


def manchester_edges(bits: Sequence[int], link: Link, rng: random.Random, t0: float) -> List[float]:
    """IEEE 802.3 convention: 0 = high-to-low at mid-bit, 1 = low-to-high at mid-bit."""
    period = link.bit_ns * (1.0 + link.ppm * 1e-6)
    levels: List[int] = []
    for b in bits:
        levels += [0, 1] if b else [1, 0]
    edges = []
    for i in range(1, len(levels)):
        if levels[i] != levels[i - 1]:
            edges.append(t0 + i * period / 2 + rng.gauss(0.0, link.jitter_ns))
    return edges


def nrz_edges(bits: Sequence[int], link: Link, rng: random.Random, t0: float) -> List[float]:
    period = link.bit_ns * (1.0 + link.ppm * 1e-6)
    edges = []
    for i in range(1, len(bits)):
        if bits[i] != bits[i - 1]:
            edges.append(t0 + i * period + rng.gauss(0.0, link.jitter_ns))
    return edges


def band_limit(edges: Sequence[float], min_pulse_ns: float) -> List[float]:
    """Remove pulses narrower than min_pulse_ns (both of their edges)."""
    out: List[float] = []
    for t in sorted(edges):
        if out and t - out[-1] < min_pulse_ns:
            out.pop()
        else:
            out.append(t)
    return out


def timestamp(edges: Sequence[float], rx: Receiver, rng: random.Random, clk_phase_ns: float) -> List[float]:
    """Edge times as the chip reports them."""
    out = []
    last_cycle = None
    for t in edges:
        local = t - clk_phase_ns
        cycle = math.floor(local / CLK_NS) + 1          # first clock edge after the input edge
        if cycle == last_cycle and not (rx.multi_hit and rx.tdc_lsb_ns is not None):
            continue                                     # one edge per channel per cycle
        last_cycle = cycle
        if rx.tdc_lsb_ns is None:
            out.append(cycle * CLK_NS + clk_phase_ns)
            continue
        before = cycle * CLK_NS - local                  # time from edge to that clock edge
        measured = round((before + rng.gauss(0.0, rx.tdc_cal_err_ns)) / rx.tdc_lsb_ns) * rx.tdc_lsb_ns
        out.append(cycle * CLK_NS + clk_phase_ns - measured)
    return out


def decode_manchester(stamps: Sequence[float], bit_ns: float) -> List[int]:
    """Decode Manchester from edge times. The first edge must be the mid-bit
    (falling) edge of a 0 bit. Returns the bits after that one; a timing
    violation ends decoding."""
    threshold = 0.75 * bit_ns
    out: List[int] = []
    level = 0
    mid = True
    for a, b in zip(stamps, stamps[1:]):
        long = (b - a) > threshold
        level ^= 1
        if mid and long:
            out.append(level)
        elif mid:
            mid = False
        elif long:
            break
        else:
            out.append(level)
            mid = True
    return out


def manchester_trial(n_bits: int, link: Link, rx: Receiver, rng: random.Random) -> Tuple[int, int]:
    """Returns (bit errors, bits compared) for one random frame."""
    bits = [0] + [rng.randrange(2) for _ in range(n_bits)]
    edges = band_limit(manchester_edges(bits, link, rng, t0=1000.0), link.min_pulse_ns)
    stamps = timestamp(edges, rx, rng, clk_phase_ns=rng.uniform(0.0, CLK_NS))
    got = decode_manchester(stamps, link.bit_ns)
    want = bits[1:]
    n = min(len(got), len(want))
    errors = sum(1 for g, w in zip(got[:n], want[:n]) if g != w) + (len(want) - n)
    return errors, len(want)
