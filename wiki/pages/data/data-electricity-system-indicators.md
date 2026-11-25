---
title: Electricity System Indicator Register
type: data
created: 2026-07-19
updated: 2026-11-24
reviewed: 2026-11-04
review_due: 2027-02-04
sources: [nea-annual-report-fy2025-26, nea-annual-report-fy2024-25, wb-country-economic-memo-2025, wb-household-electric-cooking-nepal-2025]
tags: [indicators, distribution, demand, flexibility, csv]
excerpt: A compact, source-linked register of headline distribution, demand and flexibility observations used by the wiki's core branch pages.
caveat: The register contains dated public observations, not interpolated current values; unlike metrics are not combined into a composite score.
maturity: working-page
page_quality: brief
---

# Electricity System Indicator Register

## Summary

This compact, source-linked register collects headline distribution, demand and flexibility observations used by the wiki's core branch pages. It reduces repeated headline values while keeping distinctions such as grid coverage versus reliability, and national peak versus system peak. FY 2025/26 rows from [[nea-annual-report-fy2025-26]] sit alongside the FY 2024/25 rows. Earlier rows are kept as history, not overwritten. For an eleven-year national series, see [[data-nea-system-annual-timeseries]].

## What This Shows

- Distribution: grid coverage, aggregate loss, distribution loss across all DCSD offices, nine administrative-office loss observations per year, and dated enterprise outage evidence.
- Demand: sales, consumers, sector shares, per-capita use, peak definitions and the electric-cooking baseline.
- Flexibility: Kulekhani capacity and annual generation.

## Key Data Points

| Indicator | FY 2024/25 | FY 2025/26 |
|---|---|---|
| Total system loss | 12.26% | 12.16% (provisional) |
| DCSD distribution loss, all offices | 10.39% | 10.44% |
| Highest office loss | Surkhet 17.02% | Surkhet (Karnali PO) 17.68% |
| Customer sales incl. internal use | 11,288 GWh | 12,376 GWh |
| Registered consumers | 5,707,528 | 5,927,440 |
| National peak / system peak | 2,409 / 2,901 MW | 2,479 / 3,226 MW |
| Per-capita consumption | 465 kWh | 496 kWh |
| Kulekhani cascade generation | 279.8 GWh | 92.4 GWh |

> [!finding]
> Kulekhani cascade generation in FY 2025/26 was 92.4 GWh, about one third of the FY 2024/25 figure, with installed cascade capacity unchanged at 106 MW. The figure comes from the Generation Directorate's monthly table.

## Coverage / Method

The machine-readable [electricity_system_indicators.csv](../../../data/electricity_system_indicators.csv) records value, unit, period, geography, scope, source slug, locator, verification date, confidence and caveat. FY 2025/26 rows carry PDF page locators.

## Caveats

The register contains dated public observations, not interpolated current values, and unlike metrics are not combined into a composite score.

The FY 2025/26 DCSD loss table (Appendix 9) labels offices by province, for example Bagmati PO and Bagmati PDO. Each column is mapped to an existing office in the register because the column's printed 2024/025 value equals that office's FY 2024/25 value.

The FY 2025/26 DCSD narrative gives a 42.02% domestic sales share, which is the previous year's figure. Its own table shows 41.76%, and the register uses the table value.

The register intentionally remains a Working Page because it is not a continuous operating dashboard.

## Linked Data

- [Electricity-system indicator register (CSV)](../../../data/electricity_system_indicators.csv)

## Sources

- [[nea-annual-report-fy2025-26]]
- [[nea-annual-report-fy2024-25]]
- [[wb-country-economic-memo-2025]]
- [[wb-household-electric-cooking-nepal-2025]]

## Related

[[distribution-and-reliability]] · [[demand-and-electrification]] · [[storage-and-flexibility]] · [[data-electricity-system-evidence-gaps]] · [[data-nea-system-annual-timeseries]]
