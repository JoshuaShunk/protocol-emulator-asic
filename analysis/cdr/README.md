# Receive timing study

Bit error rate of Manchester decoding from edge timestamps at a 50 MHz system
clock, for three ways of timestamping input edges:

- whole-cycle: the cycle in which the synchroniser sees the edge;
- TDC, one edge per cycle: sub-cycle timestamp, at most one edge per channel per cycle;
- multi-hit TDC: a delay line at least one clock period long sampled every cycle,
  so every edge in the period is kept.

`model.py` holds the transmitter, input path and decoder models; `study.py`
sweeps the bit rate. These are model results, not silicon measurements.

```
python3 study.py 20 7.5     # 20 trials of 1000 bits, 7.5 ns minimum input pulse
python -m pytest analysis/cdr
```

## Result

Link: 0.5 ns rms edge jitter, 100 ppm frequency error. Input path passes pulses
of 7.5 ns or longer (about the 66 MHz input rating of sky130 Tiny Tapeout pads;
the IHP figure is not published). TDC: 60 ps LSB, 100 ps rms calibration error.

| Rate (Mb/s) | Whole-cycle | TDC, one edge per cycle | Multi-hit TDC |
|-------------|-------------|-------------------------|---------------|
| 16 | 0 | 0 | 0 |
| 18 | 0.99 | 0 | 0 |
| 22 | 1.00 | 0 | 0 |
| 25 | 0.30 | 0.15 | 0 |
| 30 | 1.00 | 0.95 | 0 |
| 40 | 0.50 | 1.00 | 0 |
| 50 | 0.50 | 0.82 | 0.11 |

Error-free limit: 16 Mb/s with whole-cycle timestamps, 22 Mb/s with a TDC that
keeps one edge per cycle, 40 Mb/s with a multi-hit TDC, where the input pulse
width limit takes over. An error rate near 0.5 means the decoder output is
uncorrelated with the data.
