---
title: Listed Hydropower Performance (Starter)
type: data
created: 2026-11-25
updated: 2026-11-25
reviewed: 2026-11-25
review_due: 2027-02-25
sources: [nea-annual-report-fy2025-26, nea-annual-report-fy2024-25, utkhpl-disclosures-2026]
tags: [nepse, hydropower, generation, financial-performance, ipp, csv]
excerpt: "A strictly sourced starter table of delivered energy against design energy for public hydropower companies. It currently covers two NEA-linked companies (five company-years) and lists what is still missing for the rest of the listed sector."
caveat: This is a two-company sample, not a sector census. Company-year rows appear only where NEA's annual report or a company filing states the figure. Net profit and total debt are blank because no primary annual figure was located on disk.
maturity: working-page
page_quality: analysis
---

# Listed Hydropower Performance (Starter)

## Summary

[nepse_hydro_performance.csv](../../../data/nepse_hydro_performance.csv) records how much energy public hydropower companies actually delivered compared with their design or contracted energy, together with financial results where a primary document states them. NEA's annual report gives design energy for every project but does not itemise actual output for independent power producers, so company disclosures are needed to fill the gap.

The starter covers **two companies and five company-years**. Every value carries a page-level locator.

## What This Shows

| Company | Fiscal year | Design / contracted GWh | Delivered GWh | Delivered vs. design | Electricity revenue |
|---|---|---:|---:|---:|---:|
| Upper Tamakoshi Hydropower Ltd, [[upper-tamakoshi]] (456 MW) | 2079/80 | 2,281 | 1,945.83 | 85.3% | — |
| | 2080/81 | 2,281 | 2,058.37 | 90.2% | NPR 8,679 m |
| | 2081/82 | 2,281 | 1,527.77 | 67.0% | — |
| | 2082/83 | 2,281 | 2,388.02 | 104.7% | ≈ NPR 10,660 m |
| Madhya Bhotekoshi Jalavidhyut Co., [[madhya-bhotekoshi]] (102 MW) | 2082/83 (from COD, 6 Oct 2025) | not printed | > 413.75 | 103.24% of deemed target | — |

> [!finding]
> Upper Tamakoshi delivered more than its 2,281 GWh design energy for the first time in FY 2082/83 (2,388.02 GWh, 104.7%). The year before, which included the shutdown after the September 2024 flood, it delivered 67% of design.

> [!finding]
> From commercial operation on 6 October 2025 to the end of Ashadh 2083 (mid-July 2026), Middle Bhotekoshi beat its deemed energy target by 3.24%, according to NEA.

## Method and Coverage

- **Delivered energy** is NEA's published figure for energy delivered to NEA ([[nea-annual-report-fy2025-26]], PDF p.111 for Upper Tamakoshi and PDF p.117 for Middle Bhotekoshi). For FY 2081/82, NEA's previous report gives 1,529.07 GWh *generated* (PDF p.92); the table keeps the later report's delivered series and records the difference in the CSV notes.
- **Delivered vs. design** is calculated as delivered ÷ design energy. For Middle Bhotekoshi, NEA states the percentage against a "deemed energy generation target" that it does not print, so the contracted column is left blank.
- **Revenue.** FY 2080/81 comes from UTKHPL's annual statements ([[utkhpl-disclosures-2026]]). FY 2082/83 is NEA's rounded statement ("approximately 10.66 Arab"), not an audited figure.
- **Tickers** are left blank because neither source states a NEPSE trading symbol.

## Not Yet Covered

Primary figures were not found on disk for the following companies, and the public web results checked were unaudited quarterly summaries that disagree with each other, so they are excluded:

- **Chilime Hydropower Company** — NEA's report confirms the NEPSE listing but gives no annual generation.
- **Sanjen Jalavidhyut Company** — NEA gives only cumulative generation since COD (90.79 GWh and 96.96 GWh to Ashadh 2082), not annual figures.
- **Rasuwagadhi Hydropower Company** — output was interrupted by flood damage, and NEA gives restart dates but no annual GWh.
- **Private listed IPPs** (for example Sahas Urja, Sanima Mai, Butwal Power, Arun Valley) — need audited annual reports or rating rationales. The ICRA-based compilation in [[sahas-urja-benchmark-icra-2026]] is a secondary research summary and has not been used here.

## Limitations

- Two companies are not a sample of the listed sector. Both are NEA-linked, so they may not represent private IPPs.
- Delivered energy reflects grid curtailment and outages as well as hydrology.
- Net profit and total debt are blank throughout. Quarterly unaudited results were not used.

## Related

- [[data-plant-annual-generation]]
- [[data-major-developers]]
- [[upper-tamakoshi]]
- [[madhya-bhotekoshi]]
- [[data-open-data-catalog]]
