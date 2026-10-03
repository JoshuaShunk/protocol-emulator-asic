# Area budget

| Allocation | Die (um) | Area |
|------------|----------|------|
| 8x4 (target) | 1724.16 x 710.64 | 1.225 mm2 |
| 6x4 (current competition maximum) | 1289.28 x 710.64 | 0.916 mm2 |

Sizes from tt-support-tools `ihp-sg13cmos5l` branch, `tech/ihp-sg13cmos5l/tile_sizes.yaml`.
Jane Street's guidance for 6x4: about 0.7 mm2 nominal tile area, roughly 1K logic cells per tile.

## SRAM macros

The CMOS5L PDK links its SRAM library to IHP's SG13G2 macros
(`ihp-sg13cmos5l/libs.ref/sg13cmos5l_sram -> ../../ihp-sg13g2/libs.ref/sg13g2_sram`,
IHP-Open-PDK rev `2bbec755`). Sizes below are the LEF `SIZE` values; the
percentages are macro area over die area, before halo and routing.

| Macro | Size (um) | Share of 8x4 | Share of 6x4 |
|-------|-----------|--------------|--------------|
| RM_IHPSG13_1P_64x16_c2 | 236.8 x 64.36 | 1.2% | 1.7% |
| RM_IHPSG13_1P_256x8_c3_bm_bist | 236.8 x 74.1 | 1.4% | 1.9% |
| RM_IHPSG13_1P_256x16_c2_bm_bist | 236.8 x 118.78 | 2.3% | 3.1% |
| RM_IHPSG13_1P_512x16_c2_bm_bist | 236.8 x 191.34 | 3.7% | 4.9% |
| RM_IHPSG13_1P_1024x16_c2_bm_bist | 236.8 x 336.46 | 6.5% | 8.7% |

Not yet verified: that a macro hardens through the Tiny Tapeout CMOS5L flow.

## Measured hardening results

| Date | Commit | Tiles | Design | Cells | Utilisation | WNS @ clock | Notes |
|------|--------|-------|--------|-------|-------------|-------------|-------|
