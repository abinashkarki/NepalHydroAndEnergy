---
title: Upper Tamakoshi - Project Registry
mode: project-registry
subject: upper-tamakoshi
record_checked: 2026-07-10
data_files:
  - registry-data/facts.csv
  - registry-data/events.csv
  - registry-data/open_items.csv
---

# Upper Tamakoshi - Project Registry

*Rendered view of three CSV files. Do not edit numbers here; append rows to the CSVs.*

## Record

| Field | Value |
|---|---|
| Canonical name | Upper Tamakoshi Hydroelectric Project |
| Slug | `upper-tamakoshi` |
| Aliases | UTKHPL (Upper Tamakoshi Hydropower Limited), UKHLL / UKHL (spellings used in research compilations and older wiki pages) |
| Type | Run-of-river, peaking, underground powerhouse |
| Status | Operating |
| Capacity | 456 MW |
| River | Tama Koshi |
| Basin | [[koshi-basin]] (eastern) |
| District | Dolakha |
| Operator / owner | Upper Tamakoshi Hydropower Limited, NEA-established company; NEA shareholding 41% (grade research-compilation) |
| Record last checked | 2026-07-10 |

## Grade key

`P` primary-filing (company filing) | `U` utility-report | `RT` rating-report | `R` research-compilation | `D` derived. Source keys used in tables: **[F]** `utkhpl-disclosures-2026`, **[C]** `ukhl-financials-generation-fy2079-82`, **[S]** `project-specs-csv`, **[W]** existing wiki page `upper-tamakoshi` (no linked source), **[H]** `hydro-insurance`.

## Specifications

| Metric | Value | Source | Grade |
|---|---|---|---|
| Capacity | 456 MW | [S] | R |
| Gross head | 822 m | [S] | R |
| Headrace tunnel | 7.2 km | [W] | R |
| Units | 6 x 76 MW Pelton | [W] | R |
| Design discharge (Q design) | 66 m3/s | [W] | R |
| Annual design energy | 2,281 GWh | [S] | R |
| Plant load factor | 65% | [S] | R |
| PPA rate, wet / dry (first-year) | NPR 3.74 / 6.96 per kWh | [S] | R |
| Debt/equity, original model | 75/25 | [S] | R |
| Debt/equity, effective at COD | 88:12 | [C] | R |
| Project cost at COD | NPR 87-89.4 bn | [C] | R |
| Interest during construction | ~NPR 14 bn | [W] | R |
| COD | 2021 (August per [W]) | [S] | R |
| Construction duration | ⚠ ~7 years vs 11 years (see Conflicts) | [W] two sections | R |
| Rolwaling project | 22 MW; 105.04 GWh own generation | [F] | P |
| Rolwaling diversion added energy | ⚠ 216.51 GWh [F, P] vs 212 GWh [C, R] | [F], [C] | P / R |

## Time series

### Generation by fiscal year

| Fiscal year | Generation (GWh) | % of 2,281 contracted | Source | Grade |
|---|---|---|---|---|
| FY2079/80 | 1,945.83 | 85.3% | [C] | R |
| FY2080/81 | 2,058.36 | 90.2% | [C] | R |
| FY2081/82 | 1,529.07 | 67.0% (88-day shutdown) | [C] | R |

No primary generation filing is ingested yet; all three rows are research-compilation.

### Finances by fiscal year (NPR bn)

| Metric | FY2079/80 | FY2080/81 | FY2081/82 | FY2082/83 Q3 (unaudited) |
|---|---|---|---|---|
| Revenue | ⚠ ~8.68 [W, R] (year possibly mis-assigned) | ⚠ **8.679** [F, P] vs 9.3-9.5 [W, D] | ~6.9 [C, R] | 7.718 [F, P] (period basis unconfirmed) |
| Net profit / (loss) | (2.52) [C, R] | (1.39) [C, R] | (2.57) [C, R] | 0.2868 [F, P] |
| Interest / finance cost | ~6.68 [C, R] | ~6.7 [W, R] | not recorded | 4.052 finance cost [F, P] |
| Total debt | ~78.6 [C, R] | ~78.6 [W, R] (same as prior year) | not recorded | not recorded |
| Accumulated losses | not recorded | not recorded | 12.18 [C, R] | not recorded |
| DSCR | <1.0x [W, R] | <1.0x [W, R] | <1.0x [W, R] | not recorded |
| Rating | not recorded | "Distressed" [W, R] | ICRA D [C, R] | not recorded |
| Insurance expense | not recorded | 0.0993 [F, P] (1.14% of revenue [H, D]) | not recorded | not recorded |

### Flood loss and Rolwaling (point observations)

| Metric | Value | Source | Grade |
|---|---|---|---|
| Flood physical damage (Sep 2024) | NPR 1.79 bn | [C] | R |
| Flood business-interruption loss | NPR 1.43 bn | [C] | R |
| Insurance claim | NPR 2.0 bn (compilation range 2.0-3.22; 3.22 = 1.79 + 1.43) | [C] | R |
| Insurance amount paid | not established | none | none |
| Rolwaling capital work in progress, FY2082/83 Q3 | NPR 2.103 bn (no progress % given) | [F] | P |

## Events log

| Date | Type | Summary | Source | Grade |
|---|---|---|---|---|
| 2015 | construction | Gorkha earthquake cited as a construction interruption | [W] | R |
| 2021-08 | commissioning | Commercial operation (COD) | [W] | R |
| 2023-spring | hydrology | Flow at 45.12% of historical expectation | [W] | R |
| FY2080/81 | financing | 100% right share; paid-up capital NPR 10.59 bn to 21.18 bn | [C] | R |
| 2024-09 | incident | Flood damage; 88-day generation suspension | [C] | R |
| 2024-09 | insurance | Property and lost-revenue claims lodged; in settlement processing at annual report date | [F] | P |
| 2025-01 | operations | Partial generation resumes (left desander) | [W] | R |
| 2025-mid | operations | Full dual-desander operation restored | [W] | R |
| FY2081/82 | rating | ICRA Nepal downgrade to D | [C] | R |
| 2026-04-06 | disclosure | 16th/17th annual reports (FY2079/80, FY2080/81) published | [F] | P |
| 2026-05-13 | disclosure | FY2082/83 Q3 report published | [F] | P |

## Open items / monitoring

| Item | Status | Last checked | What would close it |
|---|---|---|---|
| Insurance claim settlement outcome and amount paid | open | 2026-07-10 | Filing or notice stating amount received or rejected |
| Transmission exclusion in loss-of-profit cover | open | 2026-07-10 | Policy wording or company statement |
| Rolwaling progress and commissioning schedule | monitoring | 2026-07-10 | Progress % and commissioning date in a company update |
| FY2079/80 revenue: mis-assigned year? | open | 2026-07-10 | Transcribe FY2079/80 revenue from the 2026 annual report PDF |
| FY2080/81 net result, interest, debt from primary statements | open | 2026-07-10 | Transcribe from annual report PDF; add primary-filing rows |
| FY2081/82 audited results | open | 2026-07-10 | Audited accounts published and ingested |
| Construction start date (7 vs 11 years) | open | 2026-07-10 | Dated construction-start record |
| Q3 FY2082/83 period basis | open | 2026-07-10 | Statement header, or Q4/annual comparison |
| Current ICRA rating | open | 2026-07-10 | Latest ICRA rationale ingested |
| Debt restructuring | monitoring | 2026-07-10 | Lender or company disclosure |
| Rolwaling diversion energy 216.51 vs 212 GWh | open | 2026-07-10 | Confirm in annual report text; retire 212 |
| FY2082/83 annual report | monitoring | 2026-07-10 | Publication of the report |

## Conflicts register

| # | Metric | Observations | Preferred now | Why |
|---|---|---|---|---|
| 1 | Revenue FY2080/81 | 8.679 [F, P] vs 9.3-9.5 [W, D] | 8.679 | Newest primary filing wins; 9.3-9.5 is a computed ceiling, not a reported figure |
| 2 | Revenue FY2079/80 | ~8.68 [W, R] | none | Matches the primary FY2080/81 figure, so likely mis-assigned; no primary FY2079/80 value ingested |
| 3 | Debt/equity | 75/25 original model [S] and 88:12 effective at COD [C] | both | Different metrics (model vs outcome), kept under distinct names; not a true conflict |
| 4 | Construction duration | ~7 years [W schedule] vs 11 years [W financial] | none | Both research-compilation; no start date in evidence to compute from |
| 5 | Rolwaling diversion energy | 216.51 GWh [F, P] vs 212 GWh [C, R] | 216.51 | Primary filing outranks compilation |
| 6 | Insurance claim | 2.0 bn vs 3.22 bn [C] | 2.0 as claim | 3.22 equals damage plus interruption loss, a loss total not a claim amount |
| 7 | Generation and ICRA D | Only research-compilation observations exist | [C] values, flagged | No conflicting source; grade limits confidence |

## How to update this record

When the FY2082/83 annual report is published, append rows like these to `registry-data/facts.csv`. Nothing on this page is edited by hand.

```csv
entity,metric,period,value,unit,as_of,source_slug,evidence_grade,note
upper-tamakoshi,revenue_npr_bn,FY2082/83,<value>,NPR bn,<publication date>,<annual-report source slug>,primary-filing,
upper-tamakoshi,net_profit_loss_npr_bn,FY2082/83,<value>,NPR bn,<publication date>,<annual-report source slug>,primary-filing,
upper-tamakoshi,total_debt_npr_bn,FY2082/83,<value>,NPR bn,<publication date>,<annual-report source slug>,primary-filing,
upper-tamakoshi,generation_gwh,FY2082/83,<value>,GWh,<publication date>,<annual-report source slug>,primary-filing,
```

Then add one row to `events.csv` (the publication) and update or close the matching rows in `open_items.csv`. Older observations stay; a newer primary row simply becomes the preferred one.

The same pattern works for every company: use the same metric names (`revenue_npr_bn`, `net_profit_loss_npr_bn`) with a different `entity`. "Latest quarterly earnings for every hydropower company" then becomes a query over `facts.csv` grouped by entity, not edits to many pages.

## Related

- [[koshi-basin]]
- [[nea-triple-authority]]
- [[ppa-pricing]]
- [[hydro-insurance]]
- [[q-design-discharge]]
- [[glof-risk]]
- [[utkhpl-disclosures-2026]]
- [[ukhl-financials-generation-fy2079-82]]
- [[ukhl-annual-report]]
- [[nea-annual-report-fy2024-25]]
