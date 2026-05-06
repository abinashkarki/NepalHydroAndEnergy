---
title: Hydropower Fleet Composition
type: data
created: 2026-04-14
updated: 2026-04-15
figure_type: chart-spec
sources: [nea-annual-report-fy2024-25, wecs-energy-synopsis-2024, wb-country-economic-memo-2025]
tags: [fleet, ror, pror, storage, capacity]
page_quality: analysis
---

# Hydropower Fleet Composition

Nepal's installed hydropower fleet, broken down by technology type. The RoR dominance is the structural cause of [[seasonal-mismatch]] in generation.

## Fleet by Type

| Type | Share of Installed Capacity | Characteristics | Source |
|------|----------------------------|-----------------|--------|
| Run-of-River (RoR) | ~85.7% | No storage; output mirrors river flow | NEA FY 2022/23 review |
| Peaking Run-of-River (PRoR) | ~9.9% | Small daily pondage; 2–6 hrs peaking | NEA FY 2022/23 review |
| Reservoir / Storage | ~3.7% | Seasonal regulation; only [[kulekhani-cascade]] | NEA FY 2022/23 review |

> [!note]
> Public summaries use the broader "**>90% RoR+PRoR**" framing from [[wb-country-economic-memo-2025]]. Both framings are consistent. The granular breakdown is the most granular.

## Installed Capacity Timeline

| Date | Total Installed (MW) | Source |
|------|---------------------|--------|
| FY 2022/23 | ~2,800 | NEA FY 2022/23 |
| End 2024 | ~2,990 | [[wb-country-economic-memo-2025]] |
| FY 2024/25 | 3,591.262 (total) / 3,389.912 (hydro) | [[nea-annual-report-fy2024-25]] |
| Apr 10 2026 | 3,791.874 (>1 MW hydro plants in DoED registry) | DoED registry snapshot used in [[nepal-energy-profile]] |

## Generation Seasonal Split (FY 2022/23)

| Season | Hydro Generation (GWh) | Share |
|--------|----------------------|-------|
| Dry season | 2,437 | ~27% |
| Wet season | 6,533 | ~73% |
| **Wet/dry ratio** | **2.68x** | |

> [!cite] fleet composition review
> "RoR alone delivered only about 24.5% of its annual generation in dry season."

## Ownership Split

- IPPs: **64%** of installed hydropower by 2024
- NEA and subsidiaries: remaining ~36%
- >70% of capacity added since 2018 came from IPPs

## Linked Data

- [nea_monthly_capacity_balance_fy2024_2025.csv](../../../data/processed/tables/nea_monthly_capacity_balance_fy2024_2025.csv) — monthly capacity contribution by IPPs, NEA, imports, and storage.
- [naxa_hydropower_projects.csv](../../../data/processed/naxa_hydropower_projects.csv) — **572** project records with coordinates, license stage, promoter, and river; useful for separating operating hydro from the broader development pipeline.

> [!warning]
> The project CSV is a licensing/pipeline dataset, not a clean "currently installed operational fleet" table. Use it for geography, corridor clustering, and license-stage mix, not as a substitute for NEA installed-capacity accounting.

## Linked Figures

- [nea_capacity_mix.png](../../../figures/nea_capacity_mix.png) — capacity mix visual.
- [license_type_mix.png](../../../figures/license_type_mix.png) — pipeline split by license stage.
- [top_operational_projects.png](../../../figures/top_operational_projects.png) — concentration of operating MW in a small set of plants.

## Chart Specification

Stacked bar chart: RoR / PRoR / Storage shares of installed capacity, with a second bar showing their shares of dry-season generation. The disparity between capacity share and dry-season contribution makes [[firm-power]] vs MW distinction visually clear.
