---
title: Basin Discharge Data
type: data
created: 2026-04-14
updated: 2026-04-15
figure_type: chart-spec
sources: [wecs-river-basin-plan-2024, national-water-plan-nepal]
tags: [hydrology, discharge, seasonal, basins]
---

# Basin Discharge Data

Consolidated discharge data for Nepal's major river basins. Public sources reference these numbers; provenance varies.

## Average Annual Discharge at Nepal-India Border

| Basin | Area in Nepal (km²) | Avg Discharge (m³/s) | Annual Volume (BCM) | Monsoon Share (%) | Peak-to-Dry Ratio | Primary Source |
|-------|---------------------|---------------------|---------------------|-------------------|--------------------|----------------|
| [[koshi-basin]] | 27,818 | 1,827 | ~57.6 | 67–78% | 25–50:1 | [[wecs-river-basin-plan-2024]] |
| [[gandaki-basin]] | 32,148 | 1,952 | ~61.6 | 74–80% | 22–30:1 | [[wecs-river-basin-plan-2024]] |
| [[karnali-basin]] | 43,153 | 1,256 | ~39.6 | 65–72% | 15–20:1 | [[wecs-river-basin-plan-2024]] |
| [[mahakali-basin]] | — | ~600 | — | ~73% | — | [[wecs-river-basin-plan-2024]] |

> [!note]
> Discharge figures are model-derived (MIKE SHE / MIKE Hydro Basin). Public gauge-based summaries provide slightly different ranges based on gauging-station records rather than basin-plan models. The Karnali has the best dry-season stability (lowest peak-to-dry ratio).

## Measurement Scope

These basin numbers need a scope label every time they are reused:

| Measurement frame | Example figure | Meaning |
|-------------------|----------------|---------|
| WECS border model | Koshi **1,827 m3/s** | Basin-scale modeled discharge at/near the Nepal-India border |
| Gauge / older NWP baseline | Koshi **~1,409 m3/s at Chatara** | Station-specific gauged mean at an internal measurement point |

Both can be valid at once. The conflict only appears when the measurement point is omitted.

## National Aggregate

- Total average annual runoff: ~**225 BCM** (National Water Plan estimate)
- Only ~**15 BCM** had been utilized for economic and social purposes in the National Water Plan framing
- **75%+ of river flow** occurs in the wet season (June–September)

## Dry-Season Stability by River Type

| Type | Dry-Season Stability Ratio | Examples |
|------|---------------------------|----------|
| Glacier-fed | 0.30–0.50 of mean flow | Upper Karnali, Arun |
| Mixed | 0.15–0.30 of mean flow | Trishuli, Marsyangdi |
| Rain-fed | 0.05–0.15 of mean flow | Bagmati, Kamala, Rapti |

> [!cite] basin discharge review
> "Glacier-fed rivers have dry-season stability ratios of 0.3–0.5 of mean flow vs. 0.05–0.15 for monsoon-fed rivers."

## Linked Data

- [nepal_basin_seasonality_baseline.csv](../../../data/processed/tables/nepal_basin_seasonality_baseline.csv) — merged 9-basin seasonality table with basin type, seasonal splits, source notes, and caution flags.
- The merged table adds medium-basin comparators that make the seasonality argument harder to flatten:
  - **West Rapti:** **73.5%** of runoff in four monsoon months, yet still a dry-season deficit basin.
  - **Babai:** explicitly rain-fed, with **76%** of runoff concentrated in monsoon months.
  - **Mahakali:** **73%** of surface runoff in Jun-Sep despite its snow-fed border-river character.
- Merged tributary notes also add a useful corrective case from the **Tamakoshi** basin: roughly **62% rain runoff**, **20% baseflow**, **5% snowmelt**, and **13% glacier melt**. That is why "high mountain" should not be used as shorthand for "glacier-dominated."

## Linked Figures

- [wecs_basin_potential.png](../../../figures/wecs_basin_potential.png) — basin-weighted potential graphic; useful as the geographic companion to this discharge table.

## Chart Specification

A useful next visualization would overlay seasonal flow profiles for all four major basins plus one medium-basin comparator on a single 12-month chart, with the monsoon window shaded. This makes [[seasonal-mismatch]] visually obvious and shows why border-basin averages and gauge means should not be mixed carelessly.
