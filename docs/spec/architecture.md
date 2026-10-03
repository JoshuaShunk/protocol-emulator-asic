# Architecture decisions

Nothing here is decided until the Status column says so. RTL work starts only
after the decisions marked Blocking are made.

| # | Decision | Options under consideration | Blocking | Status |
|---|----------|-----------------------------|----------|--------|
| A1 | Execution model | PIO-style independent state machines / single time-triggered core / barrel-threaded core / other | Yes | Open |
| A2 | Number of protocol lanes and pins per lane | Bounded by 8 in + 8 out + 8 bidirectional pins, minus the programming interface | Yes | Open |
| A3 | Programming / control interface | Which pins, which protocol, and whether it is itself firmware-defined | Yes | Open |
| A4 | Instruction memory | IHP SRAM macro (sizes in `docs/spec/area-budget.md`) vs flip-flops; words x width | Yes | Open |
| A5 | Target clock | 50 MHz template default vs higher; sets the fastest protocol achievable | Yes | Open |
| A6 | Input synchronisation | Synchronizer depth on every input and how its latency appears in the timing contract | Yes | Open |
| A7 | Open-drain support | How `uio_oe` is driven for I2C-style wired-AND lines | Yes | Open |
| A8 | Hardware assists | Which, if any: shift/serdes, CRC, NRZI/bit-stuffing, Manchester, edge/glitch capture | No | Open |
| A9 | Stretch goals targeted | Low-speed USB, 10BASE-T, JTAG, SWD, CAN, PS/2, debug/sniffer features | No | Open |
| A10 | HDL | Verilog (template) / Hardcaml / Amaranth; every flow here consumes generated Verilog | No | Open |

## Fixed constraints

- Process: IHP SG13CMOS5L through Tiny Tapeout, `ttihp-verilog-template` `cmos5l` branch.
- Area: 6x4 tiles = 1289.28 x 710.64 um die (tt-support-tools `tech/ihp-sg13cmos5l/tile_sizes.yaml`).
- Pins: `ui_in[7:0]`, `uo_out[7:0]`, `uio_in/uio_out/uio_oe[7:0]`, `clk`, `rst_n`.
- Deadline: 2027-01-18. Target shuttle: March 2027 CMOS5L.
