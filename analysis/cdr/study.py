"""Manchester receive bit error rate versus bit rate at a 50 MHz clock.

    python3 study.py [trials] [min_pulse_ns]
"""

import random
import sys

import model as m

RATES_MBPS = [2, 5, 10, 14, 16, 18, 20, 22, 25, 30, 35, 40, 50, 60]
RECEIVERS = {
    "whole-cycle timestamps": m.Receiver(tdc_lsb_ns=None),
    "TDC 60 ps": m.Receiver(tdc_lsb_ns=0.060),
    "TDC 60 ps, 100 ps cal error": m.Receiver(tdc_lsb_ns=0.060, tdc_cal_err_ns=0.100),
    "multi-hit TDC 60 ps, 100 ps cal error": m.Receiver(tdc_lsb_ns=0.060, tdc_cal_err_ns=0.100, multi_hit=True),
}
LINK_JITTER_NS = 0.5
LINK_PPM = 100.0
MIN_PULSE_NS = float(sys.argv[2]) if len(sys.argv) > 2 else 0.0
BITS_PER_TRIAL = 1000


def main() -> None:
    trials = int(sys.argv[1]) if len(sys.argv) > 1 else 20
    rng = random.Random(2026)
    print(f"jitter {LINK_JITTER_NS} ns rms, {LINK_PPM} ppm, input minimum pulse {MIN_PULSE_NS} ns, "
          f"{trials} x {BITS_PER_TRIAL} bits per point")
    print("rate Mb/s | " + " | ".join(RECEIVERS))
    for rate in RATES_MBPS:
        link = m.Link(bit_ns=1000.0 / rate, ppm=LINK_PPM, jitter_ns=LINK_JITTER_NS,
                      min_pulse_ns=MIN_PULSE_NS)
        cells = []
        for rx in RECEIVERS.values():
            errors = total = 0
            for _ in range(trials):
                e, n = m.manchester_trial(BITS_PER_TRIAL, link, rx, rng)
                errors += e
                total += n
            cells.append(f"{errors / total:.2e}")
        print(f"{rate:9} | " + " | ".join(cells))


if __name__ == "__main__":
    main()
