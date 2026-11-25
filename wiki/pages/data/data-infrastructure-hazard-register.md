---
title: Infrastructure Hazard Register (2023-2026) and Dangerous Glacial Lakes
type: data
created: 2026-11-25
updated: 2026-11-25
reviewed: 2026-11-25
review_due: 2027-02-25
sources: [icimod-glacial-lake-inventory-2020, icimod-ndrrma-thame-glof-2024, ndrrma-rasuwa-glacial-flood-sitrep-2025, nea-engineering-annual-report-2081-82, ukhl-financials-generation-fy2079-82, kathmandupost-bhotekoshi-flood-hydropower-damage-2026]
tags: [hazards, flood, GLOF, hydropower, substation, resilience, csv]
excerpt: A dated register of flood and glacial-lake events that damaged Nepal's hydropower and grid assets from 2023 to 2026, plus the 21 potentially dangerous glacial lakes ICIMOD identified in Nepal.
caveat: Damage and outage figures appear only where a source states them. Press tallies of affected projects and MW differ between outlets and are recorded as reported, not reconciled.
maturity: working-page
page_quality: record
---

# Infrastructure Hazard Register (2023-2026) and Dangerous Glacial Lakes

## Summary

Two registries make up this page. [infrastructure_hazard_events.csv](../../../data/infrastructure_hazard_events.csv) records 13 event or asset rows for three flood events and two glacial-lake events between June 2023 and August 2026. Each row gives its date, hazard type, affected asset, and MW, outage and damage figures where a source states them. [glof_dangerous_lakes.csv](../../../data/glof_dangerous_lakes.csv) lists the 21 potentially dangerous glacial lakes in Nepal from the ICIMOD–UNDP 2020 inventory. The lakes are mapped as an opt-in Explorer overlay, "Potentially dangerous glacial lakes (ICIMOD 2020)".

## What This Shows

| Event | Date | Hazard | Recorded asset impacts |
|---|---|---|---|
| Eastern Nepal floods | 17 Jun 2023 | flood | IPPAN tally: 13 projects / 150 MW affected. Upper Hewa Khola (8.5 MW) and Hewa Khola-A (14.9 MW) halted. Super Hewa Khola (5 MW, under construction): Rs 220 million loss (developer estimate). |
| Thame Valley GLOF | 16 Aug 2024 | glof | Khumbu hydropower intake damaged |
| Late-September 2024 floods | 27 Sep 2024 | flood | IPPAN: 15 projects / 1,177 MW halted. Upper Tamakoshi (456 MW) shut for 88 days with NPR 1.79 billion physical damage. Mandu (22 MW) and Solu Dudhkoshi (86 MW) listed as damaged. |
| Rasuwa supraglacial-lake flood | 8 Jul 2025 | glof | Rasuwagadhi (111 MW): 151 days to a first-unit partial return. Trishuli 3B Hub substation: about 80 m channel shift toward the substation. |
| Bhote Koshi–Trishuli flood | 26 Aug 2026 | flood | Cross-reference to [flood_2026_08_impact_register.csv](../../../data/flood_2026_08_impact_register.csv) (18 corridor projects) |

| ICIMOD rank | Nepal lakes | Named examples |
|---|---:|---|
| I | 15 | Tsho Rolpa, Imja Tsho, Lumding, Thulagi, Lower Barun, Hongu 1, Hongu 2 |
| II | 3 | Chamlang, plus two unnamed (Arun, Mugu) |
| III | 3 | three unnamed (Tamor 2, Arun 1) |

> [!finding]
> Nine of the 21 Nepal lakes are in the Dudh Koshi sub-basin. The other Koshi sub-basins hold 9 more: Tamor 4, Arun 4 and Tama Koshi 1. Only three are outside the Koshi: Trishuli, Marsyangdi (Thulagi) and Mugu.

> [!finding]
> The Bhote Koshi–Trishuli corridor shows up in the register twice within 13 months, in July 2025 and August 2026. Rasuwagadhi is a recorded asset in both events.

## Coverage / Method

- An event row appears only when a named primary, official or reputable press source describes it. Every row carries `source_url`, `source_title`, `confidence` and `verified_on`.
- `affected_mw` is the nameplate capacity of the affected asset, or the tally as reported. It does not measure lost output.
- `outage_days` is entered only when a source states the days or gives start and restart dates. The Rasuwagadhi value is computed from NEA Engineering's 8 July and 6 December 2025 dates.
- `estimated_damage_npr_m` is entered only when a source states it. USD values are left blank because no source gives them.
- August 2026 asset-level detail stays in the existing flood register and is not duplicated here.
- Lake coordinates are the values encoded in each ICIMOD lake ID (0.001°), tagged `lake-id-encoded`. Elevation, area and downstream hydropower exposure are blank because the inventory does not tabulate them per lake.
- Province values come from a canonical district-to-province lookup.

## Caveats

- The 2023 and 2024 tallies differ by outlet and counting window. Examples are 13 projects / 150 MW (IPPAN, June 2023) versus 11 projects / 107.54 MW (Republica, 13–22 June 2023), and 15 projects halted versus "at least 20" damaged in September 2024.
- Upper Tamakoshi's outage and damage figures come from a research compilation of company, NEA and ICRA disclosures. They are not a single audited document, and insurance claims of NPR 2.0–3.22 billion were still unsettled.
- The August 2026 event was triggered by an ice-rock avalanche and is recorded as `flood`, not `glof`.
- ICIMOD ranks come from 2015 imagery and remote-sensing screening. They indicate relative concern, not breach probability.
