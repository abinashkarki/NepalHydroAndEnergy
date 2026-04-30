---
title: Nepal Solar Resource Zones
type: data
created: 2026-04-23
updated: 2026-04-23
figure_type: map-spec
sources: [wb-esmap-solar-resource-assessment, global-solar-atlas-nepal, aepc-renewable-framework]
tags: [solar, GHI, DNI, resource, zones, district, elevation, map-spec]
---

# Nepal Solar Resource Zones

The quantitative companion to [[solar-resource-geography-nepal]]. Table-first; map-spec at the end.

## Country-weighted headline

| Metric | Value | Comparison |
|---|---|---|
| Mean GHI (country, 10-yr) | **4.7–5.0 kWh/m²/day** | ≈ northern India (4.8), southern Spain (4.9), US Georgia (5.0) |
| GHI range (min–max, deployable zones) | **4.2–6.5 kWh/m²/day** | 55% spread across country |
| Mean DNI (trans-Himalayan) | **5.8–6.8 kWh/m²/day** | ≈ Rajasthan (6.3), northern Chile (7.0) |
| Clear-sky days / year (trans-Him.) | **~260–290** | ≈ Leh, Atacama |
| Clear-sky days / year (Terai) | **~200–230** | ≈ Gangetic plain |
| Clear-sky days / year (mid-hill) | **~150–180** | ≈ coastal Kerala; worst in Nepal |
| Monsoon GHI penalty (Terai) | −25% vs April peak | Jun–Sep |
| Monsoon GHI penalty (mid-hill) | −35 to −45% vs April peak | Worst in country |
| Monsoon GHI penalty (trans-Him.) | −5 to −15% vs April peak | Rain-shadow intact |
| Winter GHI (Dec–Feb, Terai) | **4.0–4.5 kWh/m²/day** | Still above 50% of US-California-Central-Valley annual mean |
| Latitude span | 26.35° N – 30.43° N | ±4° band → peak-sun angle varies ±10% between solstices |

The winter-GHI row is the single most important number for the [[solar-hydro-complementarity]] argument: Terai dry-season GHI is still ~85% of its April peak, at exactly the time the RoR hydro fleet drops to 30–40% of its monsoon peak.

## District-level table (operating zone summary)

Values are 10-year means from World Bank ESMAP pyranometer deployment (2015–2019) cross-referenced with Global Solar Atlas (Solargis) satellite-derived estimates. Districts aggregated into representative zone rows for readability; full by-district tables live in the `data/raw/geopolitics_climate/` source material once the WB ESMAP dataset is fully imported (see **Coverage gaps** below).

| Zone | Representative districts | Mean elevation (m) | GHI (kWh/m²/day) | Clear-sky days | Best use |
|---|---|---:|---:|---:|---|
| **A. Trans-Himalayan rain-shadow** | Mustang, Dolpa, Upper Humla, Upper Manang, Upper Mugu, Jumla (upper) | 2,800–4,200 | **5.8–6.5** | 260–290 | Research / mini-grid / long-dated export |
| **B1. Central Terai** | Rautahat, Bara, Parsa, Chitwan (south), Nawalparasi, Rupandehi, Kapilvastu | 80–200 | **4.9–5.2** | 210–230 | Utility greenfield + agrivoltaics |
| **B2. Eastern Terai** | Jhapa, Morang, Sunsari, Saptari, Siraha, Dhanusha, Mahottari, Sarlahi | 60–180 | **4.8–5.1** | 200–220 | Utility greenfield + agrivoltaics |
| **B3. Western Terai** | Banke, Bardiya, Kailali, Kanchanpur | 100–250 | **5.0–5.3** | 220–240 | Utility greenfield; early grid reach |
| **C1. Kathmandu Valley** | Kathmandu, Lalitpur, Bhaktapur | 1,300 | **4.2–4.6** | 150–175 | Rooftop only (pollution haze penalty) |
| **C2. Pokhara / Gandaki hills** | Kaski, Syangja, Tanahu, Gorkha, Lamjung | 800–1,800 | **4.4–4.8** | 165–185 | Rooftop + hydro co-location |
| **C3. Eastern mid-hills** | Dhankuta, Bhojpur, Khotang, Okhaldhunga, Udayapur, Ramechhap, Dolakha | 1,000–2,200 | **4.3–4.7** | 160–180 | Rooftop + mini-grid; hydro co-location |
| **C4. Western mid-hills** | Palpa, Arghakhanchi, Gulmi, Baglung, Parbat, Myagdi, Pyuthan, Rolpa, Salyan, Surkhet, Dailekh | 900–2,100 | **4.4–4.8** | 170–190 | Rooftop + mini-grid; hydro co-location |
| **D. High Himalaya (non-siteable)** | Upper slopes of Taplejung, Sankhuwasabha, Solukhumbu, Rasuwa, northern Gorkha | 3,500–5,500 | 4.5–5.5 | varies | Non-deployable (slope, conservation, snow load) |
| **E. Remote Karnali** | Humla (lower), Mugu (lower), Dolpa (lower), Bajura, Bajhang | 1,500–3,200 | **5.0–5.8** | 200–240 | Off-grid mini-grid (track 3) |

## Zone characterisation for planning use

| Zone | Optimal configuration | Typical LCOE (NPR/kWh) | Grid proximity | Notes |
|---|---|---:|---|---|
| A | Small utility + mini-grid | 7.5–9.0 (grid-inclusive) | Poor (>100 km) | Off-grid LCOE ~NPR 18–25; diesel-displacement |
| B1/B2/B3 | Utility greenfield + agrivoltaics | **4.5–5.5** | Excellent (<10 km) | Workhorse of next 5 GW |
| C1 | Rooftop | 6.0–7.5 (retail displacement) | Distribution | Net-metered |
| C2/C3/C4 | Rooftop + hydro co-location | 5.0–6.5 (co-loc); 6.5–8 (rooftop) | Mixed | Hydro-site archetype |
| D | Not deployable | — | — | Excluded from planning |
| E | Off-grid + BESS | 12–18 (grant-supported) | None | Diesel-displacement valuation |

## The single most under-argued number

Winter-month GHI in the Terai is **4.0–4.5 kWh/m²/day**. A fixed-tilt ground-mount 1 MWp system at Zone B with 17% system PR produces **~4.0 MWh/day in December**. 1 GW = 4 GWh/day = 120 GWh/month.

The Nepal system's January dry-month hydropower shortfall is ~250–400 GWh/month (back-calculated from NEA monthly generation records FY 2024/25). **~3 GW of Terai solar closes the January shortfall by 100% on a monthly-energy basis** (not on a 6 pm peak basis — that's the BESS / reservoir-peaking problem per [[solar-hydro-complementarity]]).

This is the single number that should lead any national solar targeting document.

## Coverage gaps / data we'd like

| Dataset | Source | Status |
|---|---|---|
| WB ESMAP pyranometer hourly series (14 stations, 2015–19) | World Bank / AEPC | Publicly released; **not yet ingested into this project** |
| Global Solar Atlas high-resolution tiles (WMS) | Solargis / WBG | Available as XYZ; **to wire into explorer** — see map-spec |
| AEPC yearbook district-level SHS counts | AEPC | Partial (to 2021); later years patchy |
| NREL NSRDB Nepal subset | NREL | Available; not yet ingested |
| Nepal GHI monthly ERA5 reanalysis | Copernicus | Available; not ingested |
| District shapefile with solar-resource join | derived | **To create** for map integration |

## Map Specification

The wiki explorer is intended to carry **four solar map layers**, indexed in [[data-map-inventory]]:

1. **`solar_ghi_zones`** — polygon layer, Zone A/B/C/D/E as classed polygons colored by mean GHI. Country-scale infographic.
2. **`solar_plants`** — point layer of operating + PPA-signed + tendered utility plants (status-coded symbology). See [[data-solar-fleet-inventory]].
3. **`solar_suitability`** — derived polygon combining Zone B + slope < 3° + <10 km to 132+ kV substation. The "where to build the next 5 GW" overlay.
4. **`floating_pv_candidates`** — point/polygon for [[kulekhani-cascade]], [[tanahu-hydropower]], [[budhigandaki]], [[dudhkoshi-storage]], [[mugu-karnali-storage-hep]], [[uttarganga-storage-hydropower-project]].

### Zone polygons — classification scheme for `solar_ghi_zones`

```
class_A: GHI >= 5.7, elevation >= 2500, trans-Himalayan rain-shadow mask
class_B: GHI 4.7-5.3, slope < 3%, Terai district mask
class_C: GHI 4.2-4.8, mid-hill district mask, elevation 800-2200
class_D: GHI >= 4.5, slope > 15% OR in conservation area OR elevation > 3500
class_E: GHI 4.8-5.8, elevation 1500-3200, remote Karnali/Sudurpaschim districts
```

Legend palette:
- A: **#ef4444** (red — high resource, high friction)
- B: **#10b981** (green — workhorse zone)
- C: **#f59e0b** (amber — rooftop / distributed)
- D: **#9ca3af** (gray — non-deployable)
- E: **#8b5cf6** (purple — off-grid only)

## Chart / infographic call-outs

Three public-facing figures that should anchor the zone story:

1. **Nepal GHI map with overlay of 132 kV grid.** Shows the Terai zone's coincidence with grid density.
2. **Monthly GHI + hydro output stacked bars.** The cleanest visual of [[solar-hydro-complementarity]].
3. **Zone × LCOE bar chart** with hydro small-RoR reference line. Shows the crossover per-zone, making clear that Zone B Terai is already below hydro.

## Related

- [[solar-resource-geography-nepal]] — the narrative companion
- [[solar-hydro-complementarity]] — what the monthly / winter numbers mean for the fleet
- [[data-solar-hydro-complementarity-profile]] — hour-by-hour and month-by-month
- [[wb-esmap-solar-resource-assessment]] — the underlying measured data
- [[global-solar-atlas-nepal]] — the satellite-derived cross-reference
- [[data-map-inventory]] — where this plugs into the explorer
