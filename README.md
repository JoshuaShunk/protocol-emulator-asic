![](../../workflows/gds/badge.svg) ![](../../workflows/docs/badge.svg) ![](../../workflows/test/badge.svg) ![](../../workflows/fpga/badge.svg)

# Protocol Emulator ASIC

An open-source, programmable protocol emulator for the
[Jane Street protocol emulator ASIC competition](https://blog.janestreet.com/protocol-emulator-asic-competition/),
targeting IHP SG13CMOS5L through [Tiny Tapeout](https://tinytapeout.com) in a 6x4 tile allocation.

Status: infrastructure only. The architecture is being specified in
[docs/spec/architecture.md](docs/spec/architecture.md); `src/project.v` is still the template placeholder.

- [Verification plan](docs/verification.md)
- [Timing contract](docs/spec/timing-contract.md)
- [Area budget](docs/spec/area-budget.md)
- [Datasheet source](docs/info.md)

## Development setup (macOS)

Tools: [OSS CAD Suite](https://github.com/YosysHQ/oss-cad-suite-build) in `~/opt/oss-cad-suite`,
and from Homebrew `sigrok-cli`, `icarus-verilog`, `uv`, `libpng qhull cairo`.

```sh
uv venv --python 3.11 .venv
source env.sh
uv pip install -r test/requirements.txt
python verif/preflight.py          # checks simulator, cocotb and sigrok versions
```

`env.sh` puts Homebrew's Icarus ahead of OSS CAD Suite's, because OSS CAD Suite's
`vvp` wrapper sets `PYTHONHOME` to its own bundled Python and cocotb.

## Running checks

```sh
source env.sh
(cd test && make -B && python ../verif/check_results.py results.xml)   # template test
python -m verif.smoke.run                                              # harness self-test
(cd verif/smoke/formal && sby -f uart_tx.sby)                         # harness formal self-test
./verif/smoke/mutation/run.sh                                          # harness mutation self-test
```

## Hardening locally

Matches the CMOS5L CI action (tt-support-tools `ihp-sg13cmos5l`, IHP-Open-PDK `2bbec755`,
LibreLane 3.1.0.dev3). Requires Docker.

```sh
./tools/setup_harden.sh
./tools/harden.sh
```

## Tiny Tapeout resources

- [FAQ](https://tinytapeout.com/faq/)
- [Local hardening guide](https://www.tinytapeout.com/guides/local-hardening/)
- [Enabling GitHub Pages for the results page](https://tinytapeout.com/faq/#my-github-action-is-failing-on-the-pages-part)
