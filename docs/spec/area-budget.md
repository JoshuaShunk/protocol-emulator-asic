# Area budget

Die: 6x4 tiles = 1289.28 x 710.64 um = 0.916 mm2
(tt-support-tools `ihp-sg13cmos5l` branch, `tech/ihp-sg13cmos5l/tile_sizes.yaml`).
Jane Street's guidance: about 0.7 mm2 nominal tile area, roughly 1K logic cells per tile.

## SRAM macros

The CMOS5L PDK links its SRAM library to IHP's SG13G2 macros
(`ihp-sg13cmos5l/libs.ref/sg13cmos5l_sram -> ../../ihp-sg13g2/libs.ref/sg13g2_sram`,
IHP-Open-PDK rev `2bbec755`). Sizes below are the LEF `SIZE` values; the
percentage is macro area over die area, before halo and routing.

| Macro | Size (um) | Share of die |
|-------|-----------|--------------|
| RM_IHPSG13_1P_64x16_c2 | 236.8 x 64.36 | 1.7% |
| RM_IHPSG13_1P_256x8_c3_bm_bist | 236.8 x 74.1 | 1.9% |
| RM_IHPSG13_1P_256x16_c2_bm_bist | 236.8 x 118.78 | 3.1% |
| RM_IHPSG13_1P_512x16_c2_bm_bist | 236.8 x 191.34 | 4.9% |
| RM_IHPSG13_1P_1024x16_c2_bm_bist | 236.8 x 336.46 | 8.7% |

Not yet verified: that a macro hardens through the Tiny Tapeout CMOS5L flow.

## Measured hardening results

| Date | Commit | Design | Cells | Utilisation | WNS @ clock | Notes |
|------|--------|--------|-------|-------------|-------------|-------|
