"""python3 -m pytest analysis/cdr"""

import random

import model as m


def test_decoder_ideal_timestamps():
    rng = random.Random(1)
    for bit_ns in (1000.0, 100.0, 25.0):
        bits = [0] + [rng.randrange(2) for _ in range(500)]
        edges = m.manchester_edges(bits, m.Link(bit_ns=bit_ns), rng, 0.0)
        assert m.decode_manchester(edges, bit_ns) == bits[1:]


def test_whole_cycle_timestamps_are_on_the_clock_grid():
    rng = random.Random(2)
    stamps = m.timestamp([3.0, 47.5, 101.0], m.Receiver(), rng, clk_phase_ns=0.0)
    assert stamps == [20.0, 60.0, 120.0]


def test_tdc_timestamps_recover_edge_time():
    rng = random.Random(3)
    stamps = m.timestamp([3.0, 47.5, 101.0], m.Receiver(tdc_lsb_ns=0.06), rng, clk_phase_ns=0.0)
    assert all(abs(s - t) <= 0.03 + 1e-9 for s, t in zip(stamps, [3.0, 47.5, 101.0]))


def test_single_hit_drops_second_edge_in_a_cycle():
    rng = random.Random(4)
    assert len(m.timestamp([1.0, 9.0], m.Receiver(tdc_lsb_ns=0.06), rng, 0.0)) == 1
    assert len(m.timestamp([1.0, 9.0], m.Receiver(tdc_lsb_ns=0.06, multi_hit=True), rng, 0.0)) == 2


def test_band_limit_removes_narrow_pulses():
    assert m.band_limit([0.0, 5.0, 20.0, 40.0], 7.5) == [20.0, 40.0]
