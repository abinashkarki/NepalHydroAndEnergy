---
title: NEA Retail Electricity Tariff Schedule
type: data
created: 2026-11-24
updated: 2026-11-25
reviewed: 2026-11-25
review_due: 2027-02-24
sources: [nea-annual-report-fy2025-26, nea-annual-report-fy2024-25, erc-nea-consumer-tariff-order-2078]
tags: [tariff, retail, erc, nea, time-of-day, ev-charging, csv]
excerpt: Row-level transcription of the retail tariff schedule printed in NEA's FY 2025/26 annual report, covering domestic slabs, low/medium/high-voltage categories, time-of-day rates, EV charging and community wholesale supply.
caveat: The schedule is transcribed from NEA's annual-report appendix and cross-checked against the ERC tariff order 2078, which applies from Mangsir 2078 consumption (recorded as 2021-11-17).
maturity: working-page
page_quality: record
---

# NEA Retail Electricity Tariff Schedule

## Summary

[erc_retail_tariffs.csv](../../../data/erc_retail_tariffs.csv) holds 223 rows transcribed from Appendix 4, "Electricity Tariff", of [[nea-annual-report-fy2025-26]] (PDF pp.179–184, printed pp.169–174). Each row is one charge cell: a customer category, voltage or ampere tier, season, time band and consumption slab, with its demand charge (NRs/kVA/month), energy charge (NRs/kWh) and minimum charge (NRs/month).

## What This Shows

| Block | Rows | Report table |
|---|---:|---|
| Domestic single-phase 5/15/30/60 A slabs | 24 | 1.1 |
| Domestic three-phase LV and 33/11 kV | 6 | 1.2–1.3 |
| Other consumers, low voltage (230/400 V) | 15 | 2.1 |
| Other consumers, 132/66/33/11 kV flat rates | 24 | 2.2 |
| Time-of-day, Baishakh–Mangsir (peak/off-peak/normal) | 72 | 3.1 |
| Time-of-day, Paush–Chaitra (peak/normal) | 48 | 3.2 |
| Swap-card transport without demand charge | 30 | 3.3 |
| Community wholesale consumers | 4 | 4 |

> [!finding]
> Every numeric value in the FY 2025/26 schedule also appears in the same tariff appendix of [[nea-annual-report-fy2024-25]], with the same count. The two reports print the same schedule.

> [!finding]
> At 132 kV, the industrial time-of-day energy charge from Baishakh to Mangsir is NRs 10.00/kWh at peak (17:00–23:00), NRs 8.20 at normal time and NRs 4.65 off-peak (23:00–05:00). From Paush to Chaitra the table prints no off-peak band.

> [!finding]
> Public EV charging-station rates are printed at NRs 5.60–5.75/kWh flat, against NRs 8.60–8.90 for "other transportation". A table note allows charging-station operators to add at most 20% when serving EVs.

## Coverage / Method

- Values were copied cell by cell from `pdftotext -layout` output and re-checked against per-page extraction of the PDF.
- The `season` field maps NEA's printed month ranges to `wet` (Ashad–Kartik or Baishakh–Mangsir) and `dry` (Marg–Jestha or Paush–Chaitra). The exact printed months are kept in `season_months`, because the domestic and time-of-day tables use different month boundaries.
- A blank demand or minimum charge means the cell is printed as "-" or does not exist. Every row carries `source_slug`, `source_locator` and `verified_on`.

## Caveats

- `effective_from` is `2021-11-17` for every row. The annual report prints the schedule without a date. The date comes from [[erc-nea-consumer-tariff-order-2078]], which the Commission set at its 140th meeting on 2078/07/08 BS for Mangsir 2078 consumption and bills from Paush 2078. Mangsir 1, 2078 BS is converted to 2021-11-17 (canonical lookup). Every non-zero demand, energy and minimum charge in the CSV appears in the order's tariff pages (PDF pp.74–83).
- As of 2026-11-25, the ERC charge-order page lists no later NEA consumer tariff order. Taxes such as VAT are not part of the order.
- In table 3.2 (Paush–Chaitra), the normal-time header is printed as 23.00–5.00. The swap-card table 3.3 prints normal time as 23.00–17.00, so normal time is read as all hours outside the peak.
- The worked example for the 15 A billing method mentions an NRs 10.00 band for 151–250 units that is not in table 1.1. The CSV records only the table values.
- The schedule does not include charges outside the tariff table, such as dedicated-line or trunk-line provisions, taxes or service fees.

## Linked Data

- [NEA retail tariff schedule (CSV)](../../../data/erc_retail_tariffs.csv)
- [[data-ppa-standard-rates]] — the purchase side of NEA's tariff book

## Sources

- [[nea-annual-report-fy2025-26]] — Appendix 4 Electricity Tariff, PDF pp.179–184
- [[nea-annual-report-fy2024-25]] — same schedule, used for the cross-year comparison
- [[erc-nea-consumer-tariff-order-2078]] — the ERC order behind the schedule, PDF pp.74–83, used for `effective_from`

## Related

[[ppa-pricing]] · [[data-industrial-electricity-consumers]] · [[data-domestic-demand]]
