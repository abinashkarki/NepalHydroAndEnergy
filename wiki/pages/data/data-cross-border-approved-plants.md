---
title: Cross-Border Export Approvals Ledger
type: data
created: 2026-11-24
updated: 2026-11-24
reviewed: 2026-11-24
review_due: 2027-02-24
sources: [nea-annual-report-fy2025-26, nea-annual-report-fy2024-25]
tags: [trade, export, india, bangladesh, iex, csv]
excerpt: NEA's published count and quantum of hydropower capacity approved for sale to India and Bangladesh, by market channel, for FY 2024/25 and FY 2025/26.
caveat: NEA publishes approvals by channel only; the ledger has no plant-by-plant rows because no per-plant official list was retrievable. Approved quantum is permission to sell, not delivered energy.
maturity: working-page
page_quality: record
---

# Cross-Border Export Approvals Ledger

## Summary

This ledger records the approved export quantum NEA reports for sale of Nepali power to India and Bangladesh, split by market channel. Between the FY 2024/25 and FY 2025/26 annual reports, the approved total rose from 936.72 MW across 28 approvals to 1,200.01 MW across 37.

## What This Shows

| Channel | Route | FY 2024/25 (No. / MW) | FY 2025/26 (No. / MW) |
|---|---|---:|---:|
| IEX day-ahead / real-time | Dhalkebar-Muzaffarpur 400 kV | 9 / 451.62 | 11 / 486.57 |
| IEX day-ahead / real-time | Tanakpur-Mahendranagar 132 kV | 2 / 70.00 | 2 / 70.00 |
| Medium-term bilateral (Nepal-India) | Dhalkebar-Muzaffarpur 400 kV; Bihar/UP 132 kV | 15 / 375.10 | 22 / 603.44 |
| Medium-term bilateral (Nepal-Bangladesh) | Dhalkebar-Muzaffarpur 400 kV | 2 / 40.00 | 2 / 40.00 |
| **Total** | | **28 / 936.72** | **37 / 1,200.01** |

> [!finding]
> Most of the FY 2025/26 increase is in medium-term bilateral sales to India: +228.34 MW and +7 approvals. The IEX channels added +34.95 MW, and the Bangladesh channel was unchanged at 40 MW.

> [!finding]
> NEA reports the IEX day-ahead and real-time markets as one combined row. The ledger therefore uses a single `iex-dam-rtm` channel value and does not split them.

## Coverage / Method

The machine-readable [cross_border_approved_plants.csv](../../../data/cross_border_approved_plants.csv) has one row per channel and fiscal year (`record_level = channel-aggregate`). Each row has a PDF page locator and `verified_on` date. The plant-level columns (`project_name`, `project_slug`, `installed_mw`, `valid_until`) are there so that per-plant rows can be added later. They stay blank until a primary approval record is on file.

## Caveats

- The approvals are permissions to sell, granted per approval. They do not measure energy exported, which NEA reports separately (3,817 GWh to India and 148 GWh to Bangladesh in FY 2025/26).
- The Indian approval letters that name individual plants were not retrievable, so no plant is attributed an approval here.
- Approvals have validity windows and renewals that this table does not capture.

## Linked Data

- [Cross-border export approvals (CSV)](../../../data/cross_border_approved_plants.csv)

## Sources

- [[nea-annual-report-fy2025-26]]
- [[nea-annual-report-fy2024-25]]

## Related

[[india-energy-relationship]] · [[bangladesh-trade-route]] · [[dhalkebar-muzaffarpur]]
