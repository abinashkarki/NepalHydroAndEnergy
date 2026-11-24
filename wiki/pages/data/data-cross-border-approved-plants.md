---
title: Cross-Border Export Approvals Ledger
type: data
created: 2026-11-24
updated: 2026-11-25
reviewed: 2026-11-25
review_due: 2027-02-24
sources: [nea-annual-report-fy2025-26, nea-annual-report-fy2024-25, kathmandupost-india-approves-additional-200mw-2025, ekantipur-additional-80mw-export-approval-2025, kathmandupost-nvvn-200mw-five-year-deal-2023, kathmandupost-export-approval-renewals-2026, spotlightnepal-nea-594mw-iex-approval-2026]
tags: [trade, export, india, bangladesh, iex, csv]
excerpt: NEA's published count and quantum of hydropower capacity approved for sale to India and Bangladesh, by market channel, for FY 2024/25 and FY 2025/26, plus press-reported plant-level approvals.
caveat: NEA publishes approvals by channel only. Plant-level rows come from news reports and cover 16 of 37 FY 2025/26 approvals; they are never summed with the channel totals. Approved quantum is permission to sell, not delivered energy.
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

## Plant-Level Approvals

The CSV also has 28 `record_level = plant-approval` rows, one per named plant, channel and report. They come from news reports, because the Indian Designated Authority's approval letters and the CEA cross-border page returned HTTP 404.

| Fiscal year | Source | Rows | What is named |
|---|---|---:|---|
| FY 2022/23 | [[kathmandupost-nvvn-200mw-five-year-deal-2023]] | 5 | Five plants in NEA's five-year 200 MW NVVN sale, with export quantum |
| FY 2025/26 | [[kathmandupost-india-approves-additional-200mw-2025]] | 16 | 14 plants selling in IEX DAM/RTM (capacity only), and the 2 Bangladesh supply plants with quantum |
| FY 2025/26 | [[ekantipur-additional-80mw-export-approval-2025]] | 2 | Mewa Khola 48.5 MW and Karuwa Seti 31.04 MW |
| FY 2026/27 | [[kathmandupost-export-approval-renewals-2026]] | 4 | Renewals for Upper Chameliya, Seti river, Upper Tadi Khola and Upper Dordi A |
| FY 2026/27 | [[spotlightnepal-nea-594mw-iex-approval-2026]] | 1 | Seti Khola, an additional 21.34 MW on IEX valid to 2027-08-31 |

> [!finding]
> For FY 2025/26, the plant rows name 16 distinct plants out of the 37 approvals in NEA's table. Approved quantum is known for 119.54 MW of the 1,200.01 MW total: the 40.00 MW Bangladesh channel in full (Trishuli 18.60 and Chilime 21.40) and 79.54 MW for Mewa Khola and Karuwa Seti.

> [!finding]
> The Kathmandu Post names 14 plants selling in IEX DAM/RTM, with 580.89 MW combined capacity. NEA's FY 2025/26 table counts 13 IEX approvals (11 via Dhalkebar-Muzaffarpur, 2 via Tanakpur-Mahendranagar). The ledger keeps both counts as printed and does not reconcile them.

## Coverage / Method

- Each `channel-aggregate` row is one channel and fiscal year, with a PDF page locator and `verified_on` date. Totals must be computed from `channel-aggregate` rows only. `plant-approval` rows are a partial attribution layer, so summing them with the channel rows double-counts.
- On `plant-approval` rows, `installed_mw` is the capacity as printed in the article, and `approved_export_mw` is filled only where the article states a per-plant quantum. `approval_status` records what was reported: `approved-reported-in-press`, `renewed-reported-in-press` or `sale-agreement-reported`.
- `project_slug` is set only where the plant name matches one registry plant without doubt. It is blank for Devighat, Solu Khola (22.80 MW), Upper Kaligandaki, Seti river, Upper Tadi Khola and Seti Khola.
- `market_channel = india-unspecified` means the article does not say whether the sale is through IEX or a bilateral agreement.

## Caveats

- The approvals are permissions to sell, granted per approval. They do not measure energy exported, which NEA reports separately (3,817 GWh to India and 148 GWh to Bangladesh in FY 2025/26).
- The Indian approval letters that name individual plants were not retrievable. Plant attributions rest on news reports. The Haryana and Bihar bilateral supplier plants for FY 2025/26 (435.2 MW and 125.004 MW in the press) are not named in any source retrieved.
- Approvals have validity windows and renewals that this table does not capture.

## Linked Data

- [Cross-border export approvals (CSV)](../../../data/cross_border_approved_plants.csv)

## Sources

- [[nea-annual-report-fy2025-26]]
- [[nea-annual-report-fy2024-25]]
- [[kathmandupost-india-approves-additional-200mw-2025]]
- [[ekantipur-additional-80mw-export-approval-2025]]
- [[kathmandupost-nvvn-200mw-five-year-deal-2023]]
- [[kathmandupost-export-approval-renewals-2026]]
- [[spotlightnepal-nea-594mw-iex-approval-2026]]

## Related

[[india-energy-relationship]] · [[bangladesh-trade-route]] · [[dhalkebar-muzaffarpur]]
