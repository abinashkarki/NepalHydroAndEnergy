---
title: NEA Grid Infrastructure FY 2025/26
type: data
created: 2026-11-24
updated: 2026-11-24
reviewed: 2026-11-24
review_due: 2027-02-24
figure_type: table
sources: [nea-annual-report-fy2025-26, nea-annual-report-fy2024-25, nea-transmission-annual-book-2077]
tags: [transmission, substations, transformer-capacity, line-length, nea, grid, csv]
excerpt: Current NEA transmission circuit-km by voltage class and grid-substation transformer MVA by voltage ratio for FY 2024/25 and FY 2025/26, with the ten-year series and the FY 2076/77 baseline.
caveat: NEA's ten-year comparison table and its line-by-line inventory report different circuit-km totals; circuit-km and MVA measure installed assets, not transfer capability or congestion.
maturity: working-page
page_quality: record
---

# NEA Grid Infrastructure FY 2025/26

## Summary

This page records the current size of NEA's high-voltage grid: transmission circuit-km by voltage class and grid-substation transformer capacity by voltage ratio, for FY 2024/25 (2081/82) and FY 2025/26 (2082/83). It sets these beside the FY 2076/77 baseline recorded in [[data-nea-transmission-length-fy2076-77]] and [[data-nea-substation-capacity-fy2076-77]]. The machine-readable file also carries NEA's ten-year comparison series from FY 2072/73 to FY 2082/83.

## What This Shows

**Transmission circuit-km** (ten-year comparison table)

| Voltage | FY 2076/77 | FY 2081/82 (2024/25) | FY 2082/83 (2025/26) |
|---|---|---|---|
| 66 kV | 514 | 514 | 514 |
| 132 kV | 3,240 | 4,193 | 4,464 |
| 220 kV | 437 | 1,266 | 1,324 |
| 400 kV | 78 | 787 | 807 |
| **Total** | **4,269** | **6,760** | **7,110** |

**Grid-substation transformer capacity, MVA (number of transformers)**

| Voltage ratio | FY 2076/77 | FY 2081/82 (2024/25) | FY 2082/83 (2025/26) |
|---|---|---|---|
| 400/220 | — | 2,390 (9) | 2,390 (9) |
| 220/132 | 320 (2) | 4,350 (52) | 4,350 (52) |
| 220/33 | — | 186 (4) | 186 (4) |
| 132/66 | 522.9 (11) | 835 (14) | 1,098 (18) |
| 132/33 | 1,889 (51) | 3,729 (89) | 4,450 (100) |
| 132/11 | 462.5 (17) | 993 (31) | 1,270 (38) |
| 66/33 | 42.5 (2) | 60 (3) | 73 (3) |
| 66/11 | 584.5 (32) | 796 (34) | 848 (36) |
| 33/11 | 478.3 (37) | 784 (54) | 876 (58) |
| **Total** | **4,299.7 (152)** | **14,123 (290)** | **15,541 (318)** |

The DCSD distribution network, which is separate from the grid substations above:

| Year | 33 kV lines | 11 kV lines | 33/11 kV substations |
|---|---|---|---|
| FY 2024/25 | 8,145 circuit-km | 53,131 circuit-km | 210 substations, 2,997 MVA |
| FY 2025/26 | 8,388 circuit-km | 54,296 circuit-km | 221 substations, 3,048 MVA |

> [!finding]
> Between FY 2076/77 and FY 2082/83, transformer capacity grew from 4,299.7 to 15,541 MVA. The 400/220 kV and 220/132 kV ratios account for 6,420 MVA of the 11,241 MVA increase.

> [!finding]
> In FY 2082/83 all of the 1,418 MVA added was at 132 kV and below, with no change at 400/220 or 220/132 kV. Transmission length grew by 349 circuit-km, the increment NEA prints, of which 271 was at 132 kV.

## Coverage / Method

[`scripts/extract_nea_plant_and_grid_tables.py`](../../../scripts/extract_nea_plant_and_grid_tables.py) parses:

- **FY 2025/26 report:** ten-year line-length and substation tables (PDF p.205), voltage-rating summary of existing grid substations (p.222), line-inventory subtotals (pp.208–209) and DCSD figures (p.61).
- **FY 2024/25 report:** the same tables on p.170, p.184, pp.173–174 and p.49. These supply FY 2072/73, the FY 2080/81 ratio column and the FY 2081/82 transformer counts.
- **FY 2076/77 transmission annual book:** the baseline ratio table (PDF p.251).

For each year, the script checks that the voltage-ratio rows sum to the printed total. The output is [nea_grid_infrastructure_summary.csv](../../../data/nea_grid_infrastructure_summary.csv) in long format: one row per metric, voltage class and fiscal year, with source and page locator.

## Caveats

- **Two different circuit-km totals.** NEA's ten-year comparison table gives 7,110 circuit-km for FY 2082/83 (4,464 / 1,324 / 807 / 514). The line-by-line "Existing High Voltage Transmission Lines" inventory gives subtotals of 4,355 at 132 kV, 1,310 at 220 kV, 560 at 400 kV and 514.46 at 66 kV, which sum to 6,739.46. The FY 2081/82 figures are 6,760 and 6,158.33. Both are kept in the CSV under separate metrics. The difference is largest at 400 kV.
- **Baseline rounding.** The FY 2076/77 values in NEA's current ten-year table are rounded (4,269 circuit-km, 4,300 MVA). The 2077 annual book gives 4,269.7 circuit-km and 4,299.7 MVA.
- **Transformer counts for FY 2080/81.** The FY 2080/81 ratio values come from the prior-year column of the FY 2024/25 table, which has no transformer counts.

## Linked Data

- [NEA grid infrastructure summary (CSV)](../../../data/nea_grid_infrastructure_summary.csv)
- [[data-nea-transmission-length-fy2076-77]]
- [[data-nea-substation-capacity-fy2076-77]]

## Sources

- [[nea-annual-report-fy2025-26]]
- [[nea-annual-report-fy2024-25]]
- [[nea-transmission-annual-book-2077]]

## Related

[[data-nea-system-annual-timeseries]] · [[data-plant-annual-generation]] · [[nepal-transmission-landscape-2025]]
