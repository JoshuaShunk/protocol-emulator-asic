# Verification plan

## Reference checks

Tests pass or fail against references that are independent of the design:

- sigrok protocol decoders, run on a VCD of the pins (`verif/lib/sigrok.py`).
  sigrok-cli exits 0 even when a decoder reports errors, so the wrapper also
  collects error annotations and fails on them.
- Bus models from cocotbext-uart, cocotbext-i2c and cocotbext-spi. cocotbext-spi
  is installed from upstream commit `67857d0c` because the PyPI release does not
  support cocotb 2.x. Its issue #29 reports wrong CPHA=0 behaviour, so SPI
  results are always cross-checked with sigrok.
- The timing contract in `docs/spec/timing-contract.md`, checked with formal properties.
- Real devices on an FPGA, captured with a logic analyser and decoded with the same sigrok decoders.

Tests are written from the specification and datasheets before the RTL.

## Gates

| Gate | Tool | Pass condition |
|------|------|----------------|
| Simulation | cocotb 2.0.1, Icarus 13.0, `verif/preflight.py` | All tests pass against both reference checks; `verif/check_results.py` requires at least one test case |
| Test strength | MCY (`verif/*/mutation/run.sh`) | Unmutated design passes, no ERROR results, mutation coverage at or above the agreed threshold |
| Timing contract | SymbiYosys | Properties proved (`mode prove`), every property has a reachable cover, a planted bug makes the proof fail |
| Timing refactors | EQY | Optimised RTL is equivalent to the last verified RTL |
| Physical | `tools/harden.sh`, CI | Hardens at 6x4 with no DRC/LVS errors; cells, utilisation and WNS recorded in `docs/spec/area-budget.md` |

## Formal tool limits

Open-source Yosys (`read_verilog -formal`) supports immediate `assert`, `assume`
and `cover`, and `$past`, `$stable`, `$rose`, `$fell`. It does not support SVA
sequences or implication (`|->`, `|=>`, `##N`), so timing properties are written
as checkers with explicit cycle counters, as in `verif/smoke/formal/uart_tx_props.sv`.

## Flow self-test

`verif/smoke/` contains a small UART transmitter used to check that the
simulation, formal and mutation flows detect bugs. It is not part of the chip.
