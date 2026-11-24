---
title: Department of Customs Foreign Trade Statistics, FY 2080/81–2082/83
type: source
created: 2026-11-24
updated: 2026-11-24
source_type: official statistics (XLSX)
source_author: Department of Customs, Government of Nepal
source_date: 2026-07-23
source_url: https://www.customs.gov.np/content/450/foreign-trade-statistics-came-208-83/
accessed: 2026-11-24
page_quality: record
tags: [source, customs, trade, imports, electric-vehicles, official]
---

# Department of Customs Foreign Trade Statistics, FY 2080/81–2082/83

## Summary

The Department of Customs publishes annual (Shrawan–Ashadh) foreign-trade workbooks on customs.gov.np. Three annual files were read on 24 November 2026:

| Fiscal year | Workbook URL |
|---|---|
| FY 2080/81 | https://giwmscdnone.gov.np/media/files/FTS_2080_81_06vgtkv.xlsx |
| FY 2081/82 | https://giwmscdnone.gov.np/media/files/FTS_Annual_2081_82_twybrul.xlsx |
| FY 2082/83 (up to Ashadh) | https://giwmscdnone.gov.np/media/files/FTS_Upto_Ashadh_82_83_gdfkmo9.xlsx |

Table 5, "Imports by Commodities", gives quantity, import value (NRs thousand) and import revenue for each 8-digit national HS code. The workbooks are linked from the customs pages `/content/45/` (FY 2080/81), `/content/10/` (FY 2081/82) and `/content/450/` (FY 2082/83).

## Key Findings

The electric-vehicle codes, aggregated with `scripts/extract_customs_ev_imports.py`:

| Category (Table 5 HS codes) | FY 2080/81 | FY 2081/82 | FY 2082/83 |
|---|---:|---:|---:|
| Electric car, jeep and van (8703.80.21–89) | 11,701 | 13,578 | 10,847 |
| Electric three-wheelers (8703.80.11/19) | 12,171 | 16,505 | 19,864 |
| Electric buses, minibuses and microbuses (8702.40.10–30) | 884 | 3,106 | 2,408 |
| Electric motorcycles, scooters and mopeds (8711.60.2x–9x) | 7,747 | 11,320 | 26,557 |

Figures are units (PCS).

## Limitations

- The index sheet of each workbook states that the tables come from ASYCUDA World data at major customs offices: 29 offices in FY 2080/81 and 24 in FY 2081/82 and FY 2082/83. Imports through other customs points are excluded.
- The FY 2082/83 workbook is labelled preliminary and subject to revision.
- Import counts are not registrations or vehicles in use.
- HS code splits change between years; for example, 8703.80.21 appears only from FY 2081/82.
- The workbooks are not committed to this repository; the script takes their local paths as arguments.
