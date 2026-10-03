"""Check uart_tx output with cocotbext-uart and with sigrok."""

import os
import random
from pathlib import Path

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles, RisingEdge, Timer
from cocotbext.uart import UartSink

from verif.lib import sigrok, timing
from verif.lib.probe import Probe, bit

CLK_NS = 20
CLKS_PER_BIT = int(os.environ.get("CLKS_PER_BIT", "8"))
BAUD = 1_000_000_000 // (CLK_NS * CLKS_PER_BIT)
OUT_DIR = Path(os.environ.get("PROBE_DIR", "."))
TIMEOUT_US = 1000


async def reset(dut):
    cocotb.start_soon(Clock(dut.clk, CLK_NS, unit="ns").start())
    dut.valid.value = 0
    dut.data.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 3)
    dut.rst_n.value = 1
    await ClockCycles(dut.clk, 2)


async def send(dut, payload):
    for byte in payload:
        dut.data.value = byte
        dut.valid.value = 1
        await RisingEdge(dut.clk)
        while not int(dut.ready.value) or not int(dut.valid.value):
            await RisingEdge(dut.clk)
        dut.valid.value = 0
        await RisingEdge(dut.clk)
        while not int(dut.ready.value):
            await RisingEdge(dut.clk)


async def run_and_check(dut, payload, name):
    await reset(dut)
    probe = Probe({"uart_tx": bit(dut.tx)}, watch=[dut.tx]).start()
    sink = UartSink(dut.tx, baud=BAUD, bits=8)

    await send(dut, payload)
    await Timer(4 * CLKS_PER_BIT * CLK_NS, unit="ns")
    probe.stop()

    got_model = bytes(sink.read_nowait(sink.count()))
    assert got_model == bytes(payload), f"cocotbext-uart: {got_model.hex()} != {bytes(payload).hex()}"

    frames = timing.check_frames(probe.events, "uart_tx", CLKS_PER_BIT * CLK_NS, frame_units=10)
    assert frames == len(payload), f"{frames} frames on the line, {len(payload)} sent"

    vcd = probe.write_vcd(OUT_DIR / f"{name}.vcd")
    decoded = sigrok.uart(vcd, "uart_tx", BAUD).check()
    got_sigrok = bytes(int(v, 16) for v in decoded.values())
    assert got_sigrok == bytes(payload), f"sigrok: {got_sigrok.hex()} != {bytes(payload).hex()}"


@cocotb.test(timeout_time=TIMEOUT_US, timeout_unit="us")
async def test_edge_bytes(dut):
    await run_and_check(dut, [0x00, 0xFF, 0x55, 0xAA, 0x01, 0x80], "edge_bytes")


@cocotb.test(timeout_time=TIMEOUT_US, timeout_unit="us")
async def test_random_bytes(dut):
    rng = random.Random(int(os.environ.get("SEED", "1")))
    await run_and_check(dut, [rng.randrange(256) for _ in range(32)], "random_bytes")
