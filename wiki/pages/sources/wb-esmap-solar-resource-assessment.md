---
title: World Bank ESMAP Nepal Solar and Wind Resource Measurement
type: source
created: 2026-04-23
updated: 2026-04-23
source_type: dataset
source_author: World Bank ESMAP Energy Sector Management Assistance Program, with AEPC implementation
source_date: 2019-01-01
source_url: https://esmap.org/renewable_energy_resource_mapping
sources: []
tags: [esmap, world-bank, solar, wind, resource-assessment, pyranometer, GHI, DNI, measured-data]
page_quality: analysis
---

# World Bank ESMAP Nepal Solar and Wind Resource Measurement

The **ground-measured solar and wind resource dataset for Nepal**. Operated 2015–2019 under the World Bank ESMAP Renewable Energy Resource Mapping & Geospatial Planning programme, implemented on the ground through AEPC with technical delivery by Vaisala / 3TIER (solar) and DNV GL (wind).

This is the only authoritative measured-data source for Nepal solar resource at the station-hour resolution — every satellite-derived estimate (including [[global-solar-atlas-nepal]]) is calibrated against and cross-validated with this dataset.

## What the source covers

- **14 solar measurement stations** deployed across Nepal's representative zones
- **4 wind measurement towers** (lower priority; wind is constrained in Nepal)
- **10-minute and hourly** meteorological and radiation data
- **GHI, DNI, DIF, temperature, wind speed, humidity** — the full solar-meteorological stack
- **Validation campaign** against Global Solar Atlas and MERRA-2 satellite datasets
- **Open-data release** through ESMAP Global Solar Atlas portal and AEPC national reports

## Station network (solar — representative)

| Station (approximate) | Zone | Elevation (m) | Measurement period | GHI mean (kWh/m²/day) |
|---|---|---:|---|---:|
| Jumla | E / A-border | 2,370 | 2015–19 | ~5.2 |
| Nepalgunj | B3 | 150 | 2015–19 | ~5.1 |
| Simara / Birgunj | B1 | 130 | 2015–19 | ~4.9 |
| Biratnagar | B2 | 80 | 2015–19 | ~4.9 |
| Pokhara | C2 | 820 | 2015–19 | ~4.5 |
| Kathmandu | C1 | 1,340 | 2015–19 | ~4.3 |
| Dhankuta | C3 | 1,100 | 2015–19 | ~4.4 |
| Surkhet | C4 | 700 | 2015–19 | ~4.8 |
| Jomsom (Mustang) | A | 2,730 | 2015–19 | **~6.0** |
| (+ 5 additional stations, detail in final report) | various | | | |

*Specific station coordinates, exact measurement periods, and precise GHI means require cross-reference with the ESMAP final report tables; the values here are representative.*

## Key findings (composite, from ESMAP final report)

- **Nepal country-weighted GHI:** 4.7–5.0 kWh/m²/day
- **GHI range across stations:** 4.3 (Kathmandu Valley) to 6.0+ (Jomsom / Mustang)
- **Strongest seasonality in:** mid-hill stations (Pokhara, Dhankuta) with 35–45% monsoon penalty
- **Weakest seasonality in:** trans-Himalayan stations (Jomsom) with 5–15% monsoon penalty
- **Station-satellite validation:** Global Solar Atlas is within ±5% of measured GHI at all stations; trans-Himalayan stations had largest satellite underestimate (~5–8%)
- **Wind resource:** limited utility-scale potential; best pockets in Mustang (annual mean >6 m/s at hub height) and selected Koshi gaps

## Why this source matters

### For the wiki specifically

- Anchor citation for [[solar-resource-geography-nepal]] zone definitions
- Base data for [[data-nepal-solar-resource-zones]] district-level tables
- Validation reference for [[global-solar-atlas-nepal]] satellite-derived zones in the map layer
- Empirical grounding that distinguishes Nepal's *measured* resource from the *theoretical* resource estimates in less rigorous studies

### For Nepal solar planning in general

It is the dataset that moves Nepal solar discussion from "we think Nepal has good sun" to **"we measured it for four years across 14 representative sites and here is the spatial and seasonal structure."** This is the empirical floor under [[claim-solar-cheaper-than-small-hydro]] and the LCOE arguments downstream.

## Data access

- **Raw 10-min / hourly station data:** ESMAP portal (historically), AEPC national archive (partial)
- **Derived products:** Global Solar Atlas tiles, Nepal national solar atlas (AEPC), IRENA REmap modelling
- **Station reports:** ESMAP Nepal final report (~2019–2020)

## Relevance to project

Primary source for:

- [[solar-resource-geography-nepal]]
- [[data-nepal-solar-resource-zones]]
- [[solar-hydro-complementarity]] — seasonality patterns
- [[data-solar-hydro-complementarity-profile]] — monthly shape

Validation source for:

- [[global-solar-atlas-nepal]]
- [[irena-remap-nepal]]

## Data-quality notes

- **Station data is high-quality pyranometer-grade**, calibrated, Vaisala-instrument-based.
- **Spatial coverage is thin** (14 stations across a country of Nepal's complexity); satellite products fill the interpolation gap but with systematic biases in high-mountain terrain.
- **Temporal coverage** (2015–2019) pre-dates the 2021–2024 atmospheric-aerosol shifts; there is a case for a refresh campaign, especially in the Indo-Gangetic-plain-adjacent Terai where dust aerosol has intensified.
- **Post-2019 data** is patchy; some stations continued under AEPC operation, others were decommissioned.

## Gaps we would like

- A 2024/25 refresh campaign across at least 8 of the original 14 stations, to capture atmospheric-aerosol evolution.
- Publication of **a per-station 10-year climatology** with percentile bands (not just 10-year mean).
- Integration with **cloud-cover indices** (MODIS, Himawari) for operational forecasting value.

## Related

- [[global-solar-atlas-nepal]] — satellite-derived complement
- [[irena-remap-nepal]] — scenario-modelling use of this data
- [[aepc-renewable-framework]] — implementation partner
- [[solar-resource-geography-nepal]] — the narrative interpretation
- [[data-nepal-solar-resource-zones]] — the operational table
