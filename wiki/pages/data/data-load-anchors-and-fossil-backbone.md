---
title: Load Anchors and Fossil Backbone Registry
type: data
created: 2026-11-24
updated: 2026-11-24
reviewed: 2026-11-24
review_due: 2027-02-24
sources: [nea-annual-report-fy2025-26, nea-annual-report-fy2024-25, customs-foreign-trade-statistics-2080-83, wecs-energy-synopsis-2024, indian-embassy-motihari-amlekhgunj-pipeline-2019, nepal-energy-institution-websites-2026]
tags: [demand, industry, sez, electric-vehicles, charging, petroleum, noc, csv]
excerpt: Starter tables for industrial load anchors, electric-vehicle imports and charging, and the petroleum import and storage backbone, each strictly sourced, with explicit gaps where official numbers are not public.
caveat: These are starter registries. Industrial anchors are taken from NEA transmission-project descriptions, not a load survey, and EV counts are customs imports, not registrations.
maturity: working-page
page_quality: record
---

# Load Anchors and Fossil Backbone Registry

## Summary

This page links three starter tables for future-load and fuel-substitution analysis:

| Table | Rows | Basis |
|---|---:|---|
| [industrial_load_anchors.csv](../../../data/industrial_load_anchors.csv) | 20 | 9 NEA-sourced anchors and 11 explicit gaps (10 industrial districts, Bhairahawa SEZ) |
| [ev_adoption_and_charging.csv](../../../data/ev_adoption_and_charging.csv) | 24 | 18 customs import rows (FY 2080/81–2082/83) and 6 charging rows from NEA reports |
| [fossil_infrastructure.csv](../../../data/fossil_infrastructure.csv) | 20 | 1 pipeline, 16 NOC storage locations plus a total row, and 2 unverified pipeline-extension gaps |

Each table has a `nearest_substation_name` column, filled only where the source names a substation. Its `substation_slug` column is left blank, to be joined to the substation registry after integration.

## What This Shows

> [!finding]
> Customs annual workbooks record 11,701, 13,578 and 10,847 electric cars, jeeps and vans (HS 8703.80) imported in FY 2080/81, 2081/82 and 2082/83. Electric two-wheeler imports (HS 8711.60.2x–9x) were 7,747, 11,320 and 26,557. The FY 2082/83 figures are preliminary.

> [!finding]
> NEA reports installing 62 of its own EV charging stations in FY 2024/25, with average sales of 35,000 kWh/day to about 2,500 customers/day. In the same year, NEA's Energy Efficiency and Loss Reduction Department facilitated about 750 public charging stations of any operator. The report gives no station-level inventory, so charger counts and kW are `unknown`.

> [!finding]
> NEA's FY 2025/26 report names steel makers (Jagdamba Steel, Jagdamba Wire, Ashok Steel, Hulas Steel, Hama Steel) as the loads behind the Amlekhgunj–Simara 66 kV upgrade. It names CG Cement and Maruti Cement as loads served by the Ridi and Sukhipur substation projects.

> [!finding]
> The NOC storage table reproduced by WECS (as of 2080/01/23 BS) totals 13,632 for petrol (MS), 2,695 for kerosene (SKO) and 8,815 for ATF. It has no diesel or LPG column and states no unit.

<figure class="wiki-inline-figure">
  <img src="../assets/figures/ev_import_surge.svg" alt="Grouped bars of electric car, three-wheeler and bus imports by unit count and customs value for FY 2080/81 to 2082/83">
  <figcaption>Electric car, jeep and van imports went from 12,147 to 10,949 units, and electric bus imports from 884 to 2,408, while three-wheeler imports rose every year. Source: [[customs-foreign-trade-statistics-2080-83]], via ev_adoption_and_charging.csv.</figcaption>
</figure>

## Coverage / Method

- **Industrial anchors:** rows come from FY 2025/26 transmission-project descriptions that name an industrial corridor, SEZ or industrial consumer. District is filled only where the text names it, and province is left `unknown` for the post-integration join. The 10 industrial districts and Bhairahawa SEZ are kept as explicit gap rows, because the Industrial District Management website could not be reached.
- **EV imports:** rows are produced by `scripts/extract_customs_ev_imports.py` from Table 5 of the customs annual workbooks ([[customs-foreign-trade-statistics-2080-83]]).
- **Charging:** rows come from [[nea-annual-report-fy2024-25]] (PDF pp.13, 71, 88) and [[nea-annual-report-fy2025-26]] (PDF p.66).
- **Fossil backbone:** the pipeline comes from [[indian-embassy-motihari-amlekhgunj-pipeline-2019]] (69 km, 10-inch, 2 MMTPA). Storage comes from [[wecs-energy-synopsis-2024]] Table 4.4.

## Caveats

- Customs data cover ASYCUDA offices only (29 offices in FY 2080/81, 24 later), and HS code splits shift between years. Imports are not registrations, sales or vehicles in use.
- The NEA-named "Nepalgunj industrial area" and the gap row "Nepalgunj Industrial District" may describe the same estate; they are not merged without a source.
- Days of fuel stock, depot-level diesel and LPG capacity, Thankot and Sinamangal depot splits, and the Amlekhgunj–Lothar and Siliguri–Jhapa pipeline plans are not verified. The NOC website returned HTTP 403.

### Evidence gaps for AI and data-centre siting

Siting a large, steady compute load needs data that is not public in the sources above:

- **fibre routes and carrier points of presence**, at least at district level
- **substation bay and transformer headroom (MVA)** by grid substation, beyond nameplate capacity
- **hourly feeder and substation load profiles**, to test whether a new 24/7 load fits within dry-season and evening-peak limits
- **outage and reliability statistics by feeder**, since existing notes cover corridor upgrades, not measured reliability

## Linked Data

- [Industrial load anchors (CSV)](../../../data/industrial_load_anchors.csv)
- [EV adoption and charging (CSV)](../../../data/ev_adoption_and_charging.csv)
- [Fossil infrastructure (CSV)](../../../data/fossil_infrastructure.csv)
- [[data-erc-retail-tariffs]] — EV charging and industrial tariff rates

## Sources

- [[nea-annual-report-fy2025-26]]
- [[nea-annual-report-fy2024-25]]
- [[customs-foreign-trade-statistics-2080-83]]
- [[wecs-energy-synopsis-2024]]
- [[indian-embassy-motihari-amlekhgunj-pipeline-2019]]
- [[nepal-energy-institution-websites-2026]]

## Related

[[noc]] · [[data-industrial-electricity-consumers]] · [[data-final-energy-mix]] · [[demand-and-electrification]]
