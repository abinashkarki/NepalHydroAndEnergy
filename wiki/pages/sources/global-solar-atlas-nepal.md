---
title: Global Solar Atlas (Nepal coverage)
type: source
created: 2026-04-23
updated: 2026-04-23
source_type: dataset
source_author: Solargis / World Bank Group (ESMAP)
source_date: 2024-01-01
source_url: https://globalsolaratlas.info/map?c=28.13,84.18,7
sources: []
tags: [solargis, global-solar-atlas, satellite, GHI, DNI, map-tile, nepal]
---

# Global Solar Atlas (Nepal Coverage)

The **primary satellite-derived solar resource dataset** for Nepal's explorer map layer and the reference cross-check for every GHI / DNI number used elsewhere in the wiki. Provided as a free-to-use web-tile and downloadable-data service by **Solargis** under the **World Bank Group ESMAP** programme.

Cross-validated against the **in-situ** [[wb-esmap-solar-resource-assessment]] pyranometer network (14 stations, 2015–2019), so the derived spatial maps carry ~±5% accuracy at station locations and somewhat wider error bands in untested high-mountain terrain.

## What the source provides

- **Global Horizontal Irradiance (GHI)** — annual and monthly means at ~9 arc-second (~250 m) spatial resolution
- **Direct Normal Irradiance (DNI)** — same spatial detail
- **Diffuse Horizontal Irradiance (DIF)** — for tilted-array optimization
- **Photovoltaic Electricity Output (PVOUT)** — modelled output for a reference PV system at each location
- **Optimal tilt angle** maps
- **Air temperature** 2-m height climatology
- **Tile-ready map service** (XYZ / WMS endpoints for integration into web maps)

## Nepal-specific findings

- **GHI range across Nepal:** ~3.8 to ~6.5 kWh/m²/day
- **Highest GHI zones:** trans-Himalayan rain-shadow (Mustang, Dolpa, upper Humla, upper Manang) — 5.8–6.5 kWh/m²/day
- **Lowest GHI zones:** Kathmandu Valley and east-facing mid-hill slopes — 4.2–4.6 kWh/m²/day
- **Terai plains:** 4.8–5.3 kWh/m²/day — broadly uniform with the north Indian plains
- **PVOUT (specific yield):** 1,500–1,800 kWh/kWp/year in trans-Himalayan, 1,350–1,500 in Terai, 1,150–1,350 in mid-hill — the yield hierarchy that translates GHI into MWh/MWp

## Why this source is the map-layer anchor

The wiki explorer's proposed **`solar_ghi_zones`** layer (see [[data-map-inventory]], [[data-nepal-solar-resource-zones]]) is built from Global Solar Atlas classifications, specifically:

1. Raw satellite GHI grid is classified into five zone bands (A, B, C, D, E) by threshold
2. Zone polygons are intersected with district boundaries for display
3. Map tiles are served directly from the Global Solar Atlas XYZ endpoint as an **overlay basemap** option in the explorer

The attribution required by the Global Solar Atlas licence (CC BY 4.0) is included in the layer legend and the map credits.

## Licence and data access

- **Licence:** Creative Commons Attribution 4.0 (CC BY 4.0)
- **Attribution:** "Solargis, The World Bank Group" in any derived product
- **Tile service:** XYZ / WMS endpoints (see Global Solar Atlas documentation)
- **Data download:** National-level GeoTIFF layers available directly from the Global Solar Atlas download section (annual GHI, DNI, PVOUT)
- **API:** Solargis commercial API for higher-resolution or bespoke time-series (not needed for map display)

## Cross-validation against ESMAP station data

Global Solar Atlas vs measured (from [[wb-esmap-solar-resource-assessment]]):

| Station | GSA GHI | Measured GHI | Bias |
|---|---:|---:|---:|
| Kathmandu | 4.4 | 4.3 | +2% |
| Pokhara | 4.5 | 4.5 | 0% |
| Nepalgunj | 5.2 | 5.1 | +2% |
| Simara | 4.9 | 4.9 | 0% |
| Biratnagar | 5.0 | 4.9 | +2% |
| Dhankuta | 4.5 | 4.4 | +2% |
| Jumla | 5.3 | 5.2 | +2% |
| Surkhet | 4.9 | 4.8 | +2% |
| **Jomsom** | **5.5** | **6.0** | **−8%** |

Trans-Himalayan is the one zone where satellite systematically **under**-estimates GHI (Jomsom 8% bias). This is the most important caveat: for Mustang / Dolpa / upper Manang planning, field measurement should be used where available, and the "Zone A 5.8–6.5" range cited in the wiki is calibrated to measurement rather than to the satellite layer.

## Related

- [[wb-esmap-solar-resource-assessment]] — the calibration source
- [[solar-resource-geography-nepal]] — the concept-page interpretation
- [[data-nepal-solar-resource-zones]] — the classification used in the map layer
- [[data-map-inventory]] — where this appears in the explorer
- [[irena-remap-nepal]] — independent scenario use of the same data
