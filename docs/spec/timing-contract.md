# Timing contract

This table is the specification the RTL is checked against. Every row names
its source and the check that enforces it. Values for external protocols are
taken from the cited document.

## Instruction timing

| Instruction | Cycles | Pin effect timing (cycle of change relative to issue) | Checked by |
|-------------|--------|--------------------------------------------------------|------------|
| _(defined once A1 in architecture.md is decided)_ | | | formal property |

## Input path

| Item | Value | Checked by |
|------|-------|------------|
| Pin-to-readable latency (synchronizer depth) | _(A6)_ | formal property |

## Protocol timing requirements

| Protocol | Parameter | Min | Max | Source (document, revision, table) | Checked by |
|----------|-----------|-----|-----|------------------------------------|------------|
| I2C | tHD;STA, tSU;STA, tSU;DAT, tHD;DAT, tSU;STO, tBUF, tLOW, tHIGH | | | NXP UM10204, to be read | timing checker on probe VCD |
| SPI | per target device datasheet | | | device datasheet | timing checker on probe VCD |
| UART | bit period tolerance | | | | sigrok decode + timing checker |
