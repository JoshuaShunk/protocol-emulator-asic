# Architecture

A programmable protocol engine that resolves time below the system clock period.
Firmware-programmed lanes transmit and receive serial protocols, including
self-clocked ones; a capture unit records pin activity with timestamps for
analysis in sigrok/PulseView; time-to-digital converters and fine-delay outputs
measure and place edges at a resolution well below the 20 ns clock period.

## Blocks

| Block | Function |
|-------|----------|
| Lanes (4 at 8x4, 2 at 6x4) | Deterministic sequencers with pin I/O, shifters, line coding, clock recovery and timers |
| Pin matrix | Maps the 24 user pins to lanes, capture unit and timing channels; per-pin open-drain and polarity |
| Timebase | Free-running cycle counter shared by all blocks |
| TDC channels | Sub-cycle timestamps for edges on selected input pins |
| Fine-delay outputs | Sub-cycle placement of edges on selected output pins |
| Calibration | Code-density measurement of TDC bins against the clock; output delay measurement by pad loopback |
| Capture unit | Change-driven pin recording with timestamps and pattern triggers into SRAM |
| Host link | Serial command interface: firmware load, configuration, capture readout (SUMP-compatible subset for PulseView) |

## Decisions

| # | Decision | Choice | Status |
|---|----------|--------|--------|
| A1 | Execution model | Per-lane single-issue sequencer with a fixed cycle count for every instruction; receive path in hardware (sampler, clock recovery, line decode) feeding a shift register | Decided |
| A2 | Lanes and pins | 4 lanes at 8x4, 2 at 6x4; each lane addresses the 24 pins through configurable pin windows | Decided |
| A3 | Host interface | UART command link: `ui_in[3]` receive, `uo_out[4]` transmit. On demo board v3 these are RP2350 GPIO20 (UART1 TX) and GPIO37 (UART1 RX) (tt-micropython-firmware `gpio_map_dbv3.py`; RP2350 datasheet GPIO function table) | Decided; command set pending SUMP details |
| A4 | Instruction memory | One IHP SRAM macro per lane (256x32 or 512x16); fallback 64x32 flip-flop memory | Pending: SRAM hardening test on CMOS5L |
| A5 | Clock | 50 MHz | Decided |
| A6 | Input synchronisation | Two flip-flops on every input to the lanes; TDC channels sample the unsynchronised pad signal | Decided |
| A7 | Open-drain | Per-pin mode: data held low, output enable driven by the inverted data bit | Decided |
| A8 | Hardware assists | 32-bit in/out shift registers with auto push/pull; chainable NRZI, bit stuffing (programmable run length), Manchester and CRC (programmable polynomial) | Decided |
| A9 | Protocol targets | UART, SPI, I2C; USB low-speed TX and RX; Manchester TX and RX; JTAG, SWD, PS/2, CAN as firmware | Decided |
| A10 | HDL | Verilog-2005 plus the SystemVerilog subset accepted by Yosys, Icarus and Verilator | Decided |
| A11 | 6x4 configuration | Lane count, TDC channel count and memory sizes are top-level parameters; a 6x4 build hardens in CI until 8x4 is confirmed | Decided |
| A12 | Sub-cycle timing | TDC: 2 channels at 8x4, 1 at 6x4; fine-delay outputs: 2 at 8x4, 1 at 6x4; standard cells first | Pending: SPICE characterisation, architecture study |
| A13 | Capture memory | Dedicated SRAM macro, change-driven records of (time delta, pin state) | Pending: SRAM hardening test |

## Fixed constraints

- Process: IHP SG13CMOS5L through Tiny Tapeout, `ttihp-verilog-template` `cmos5l` branch.
- Area: 8x4 tiles = 1724.16 x 710.64 um die. The competition maximum is currently 6x4
  (1289.28 x 710.64 um); 8x4 is under consideration by the organisers. Sizes from
  tt-support-tools `tech/ihp-sg13cmos5l/tile_sizes.yaml`.
- Pins: `ui_in[7:0]`, `uo_out[7:0]`, `uio_in/uio_out/uio_oe[7:0]`, `clk`, `rst_n`.
- Deadline: 2027-01-18. Target shuttle: March 2027 CMOS5L.

## Measured process data

Standard-cell stage delay in a self-loaded chain with one flip-flop tap, from the
Liberty tables (pre-layout, no wire load; SPICE values to follow):

| Cell | typ 1.20 V 25 C | slow 1.08 V 125 C | fast 1.32 V -40 C |
|------|-----------------|-------------------|-------------------|
| inv_1 | 30 ps | 48 ps | 21 ps |
| buf_1 | 61 ps | 96 ps | 41 ps |
| dlygate4sd1_1 | 132 ps | 212 ps | 87 ps |

Pad delays from `sg13cmos5l_io` Liberty (typ 1.2 V / 3.3 V, 25 C):

| Path | Delay |
|------|-------|
| IOPadIn pad to core, rising | 0.08 to 0.23 ns |
| IOPadIn pad to core, falling | 0.45 to 0.61 ns |
| IOPadInOut4mA core to pad, 1 to 10 pF | 1.5 to 5.4 ns |
| IOPadInOut16mA core to pad, 1 to 10 pF | 1.4 to 2.6 ns |

The input pad delays rising and falling edges differently by about 0.4 ns, so TDC
calibration is kept per edge polarity. The output delay depends on the external
load, so absolute output edge placement is calibrated by reading the pad back
through a TDC channel. The pad cells and mux delays used by the Tiny Tapeout
CMOS5L chip are not yet published.
