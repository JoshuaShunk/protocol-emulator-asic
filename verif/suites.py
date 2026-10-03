"""Simulation suites. Source paths are relative to the repository root."""

from verif.lib.runner import Suite

SUITES = {
    s.name: s
    for s in [
        Suite(
            name="smoke",
            sources=["verif/smoke/uart_tx.v"],
            toplevel="uart_tx",
            test_module="verif.smoke.test_uart_tx",
        ),
    ]
}
