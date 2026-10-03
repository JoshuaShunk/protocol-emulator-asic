# Lane instruction set (draft 0)

Status: draft. Encodings change until the assembler, golden model and RTL agree
and are under test.

## Execution model

- Each lane executes one 32-bit instruction per clock cycle from its own
  instruction memory. The next program counter is computed in the same cycle
  and presented to the memory address, so the memory output register is the
  instruction register. Taken and not-taken branches both take one cycle.
- An instruction occupies `1 + delay` cycles, where `delay` is the 5-bit field
  in every instruction. Stalling instructions (`WAIT`, blocking `PULL`/`PUSH`)
  add the stall time before the delay starts.
- The cycle in which an instruction's pin effect becomes visible on the pad,
  relative to its issue cycle, is fixed per instruction class and listed in
  `docs/spec/timing-contract.md`.

## State per lane

| State | Width | Notes |
|-------|-------|-------|
| `pc` | 9 | Up to 512 instructions |
| `r0`-`r7` | 16 | General registers; `r7` is the loop counter used by `JMP r7--` |
| `osr`, `isr` | 32 | Output and input shift registers, with shift counters |
| TX FIFO, RX FIFO | 4 x 32 each | Host or lane-to-lane |
| `deadline` | 32 | Absolute time for `WAIT TIME` and scheduled edges |
| NCO | 32-bit phase, 32-bit increment | Bit-rate generator and clock-recovery phase |
| Pin windows | | `out_base/out_count`, `in_base`, `set_base/set_count`, `side_base/side_count` over the 24 user pins |
| Coding chain | | TX: stuff, NRZI, Manchester, CRC. RX: Manchester, NRZI, unstuff, CRC, pattern match |
| `flags` | 8 | Shared between lanes for synchronisation |

## Encoding

```
31     27 26   22 21                                   0
+--------+-------+--------------------------------------+
| opcode | delay |              operands                |
+--------+-------+--------------------------------------+
```

| Opcode | Mnemonic | Operands | Effect |
|--------|----------|----------|--------|
| 00 | `JMP cond, target` | cond[3:0], target[8:0] | Branch if condition |
| 01 | `WAIT src, arg` | src[3:0], polarity, arg | Stall until condition: pin level or edge, NCO sample strobe, `deadline` reached, FIFO state, flag, coding event |
| 02 | `SET dst, imm` | dst, imm[15:0] | Pins (set window), pin directions, register, `deadline` (relative to timebase or absolute) |
| 03 | `OUT dst, n` | dst, n[5:0] | Shift `n` bits from `osr` to pins, TX coding chain, register |
| 04 | `IN src, n` | src, n[5:0] | Shift `n` bits into `isr` from pins, RX coding chain, register, timestamp |
| 05 | `PULL block` | block | TX FIFO to `osr` |
| 06 | `PUSH block` | block | `isr` to RX FIFO |
| 07 | `MOV dst, op, src` | dst, op, src | Copy with optional invert or bit reverse |
| 08-0F | ALU | dst, srcA, srcB or imm | `ADD SUB AND OR XOR SHL SHR CMP` |
| 10 | `CFG reg, src` | reg, src | Write lane configuration (coding chain, NCO increment, pin windows) |
| 11 | `FLAG op, n` | op, n | Set, clear or wait on a shared flag |
| 12 | `EDGE ch, t` | channel, time source | Schedule an output edge on a fine-delay channel at `deadline` plus a fractional cycle |
| 13 | `MARK v` | v[15:0] | Insert a marker record into the capture stream |

Conditions for `JMP`: always, `x == 0`, `x != 0`, `r7-- != 0`, pin high, pin low,
`osr` empty, `isr` full, compare flag, coding event.

## Receive path

```
pin(s) -> sync -> [edge detect, TDC timestamp] -> sampler -> RX coding chain -> isr
                              |                      ^
                              +----> NCO phase ------+
```

Sampler modes:

- Direct: `IN PINS` reads the synchronised pin.
- Recovered clock: the NCO advances by `increment` each cycle; a sample strobe
  fires at phase 1/2; each input edge corrects the phase by a programmable gain.
  With a TDC channel on the pin, the correction uses the sub-cycle edge time.
- Edge timestamps: each edge pushes (polarity, coarse time, fine time) into the
  RX FIFO. Used for pulse-width protocols, auto-baud and measurement.

Differential pairs (USB low speed) are read as two pins and decoded to J, K and SE0.

## Transmit path

```
osr -> TX coding chain -> bit timing (NCO strobe) -> pin
                                  |
                                  +-> fine-delay channel (fractional NCO phase)
```

When a fine-delay channel is attached, each bit edge is placed at the NCO's
fractional phase, not at the next whole cycle, so bit rates that are not an
integer number of clock cycles (USB low speed is 33 1/3 cycles at 50 MHz) are
produced without one-cycle jitter.
