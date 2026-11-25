---
title: Clean-Industry and Compute Siting Baseline
type: data
created: 2026-11-25
updated: 2026-11-25
reviewed: 2026-11-25
review_due: 2027-02-25
sources: [nea-annual-report-fy2025-26, nea-annual-report-fy2024-25]
tags: [siting, industry, data-centers, compute, substations, tariffs, electrification, csv, geojson]
excerpt: "35 candidate hubs for electricity-intensive industry and compute: 24 operating or under-construction 220/400 kV substations and 11 industrial estates, corridors and SEZs, joined to verified grid, ERC tariff and ecological-belt facts. No scores."
caveat: This is a join of existing registries, not a suitability ranking. The data that decides real siting (bay headroom, firm connection capacity, fibre routes and feeder reliability) is not public, and the table says so for every row.
maturity: working-page
page_quality: analysis
---

# Clean-Industry and Compute Siting Baseline

## Summary

[clean_industry_siting_index.csv](../../../data/clean_industry_siting_index.csv) lists **35 candidate hubs** where electricity-intensive industry or data centres could connect to Nepal's high-voltage grid:

- **7 400 kV hubs** (2 operating, 1 partially operational, 4 under construction)
- **17 220 kV hubs** (13 operating, 4 under construction)
- **11 industrial sites** that link to a substation of 132 kV or more with mapped coordinates: 1 SEZ, 7 industrial districts and 3 industrial corridors

`scripts/build_siting_readiness.py` derives every value from three existing registries: [[data-substation-inventory]], [[data-load-anchors-and-fossil-backbone]] and [[data-erc-retail-tariffs]]. It adds no scores, weights or estimates. A map layer, *Clean-industry & compute siting hubs*, is in the Explorer's Full Energy Infrastructure lens.

## What This Shows

| Hub type | Hubs | Installed MVA (rows reporting) | Planned addition MVA (rows reporting) |
|---|---:|---:|---:|
| 400 kV grid hub | 7 | 4,275.21 (3) | 982.5 (2) |
| 220 kV grid hub | 17 | 3,429.9 (13) | 2,354 (6) |

Installed MVA counts every transformer NEA lists at the substation, as in the substation inventory. Under-construction hubs mostly have no installed figure yet.

| Ecological belt | 400 kV | 220 kV | Industrial sites |
|---|---:|---:|---:|
| Terai | 2 | 2 | 7 |
| Mid-Hill | 3 | 10 | 3 |
| Valley (Kathmandu, Lalitpur, Bhaktapur) | 1 | 1 | 1 |
| Mountain | 1 | 4 | 0 |

> [!finding]
> Most 220 kV hubs (14 of 17) sit in the Mid-Hill and Mountain belts, close to hydropower. The industrial estates and corridors sit mainly in the Terai, where the 132 kV network serves them.

**Tariff context.** ERC's industrial time-of-day energy charge for 132 kV supply is the same everywhere in Nepal: **NPR 4.65/kWh** at wet-season off-peak (23:00–05:00) and **NPR 10.00/kWh** at peak, effective 17 November 2021 (tariff rows `tod-132-industrial-wet-off-peak` and `tod-132-industrial-dry-peak`). The table repeats these values on every row so that each row stands alone. Location does not change the energy price. Connection voltage and timing of use do.

**Other joined fields.** 20 hubs list linked transmission corridors. Six list linked NEA solar awards: Dhalkebar 50 MW, Bhairahawa SEZ 40 MW (through its Mainahiya substation), Kushma 20 MW, Markichowk 20 MW, New Butwal 15 MW and Sitalpati 10 MW.

## Method and Coverage

- **Grid hubs:** every row in `substation_specs.csv` with a highest voltage of 400 or 220 kV and a status of operating, partially operational or under construction. Planned substations are excluded.
- **Industrial sites:** every SEZ, industrial district, industrial area and industrial corridor in `industrial_load_anchors.csv` whose linked substation is 132 kV or higher and has coordinates. Single-plant loads (cement factories) are excluded. The site uses its own coordinates where the anchor row records them; otherwise it is plotted at the linked substation and labelled so.
- **Ecological belt:** a Tier B canonical lookup by district (CBS / NPHC 2021 classification: 16 Mountain, 21 Terai, 40 Hill districts), with the three Kathmandu Valley districts shown as *Valley*. Tagged `canonical-lookup` in the `source_basis` column.
- **Coordinates:** 33 of 35 hubs are mapped. Lapang and Markichowk have no sourced coordinates and are not estimated.

## What Public Data Is Still Missing

Every row's `missing_siting_data` column records the same gaps:

- **Substation bay headroom and firm connection capacity.** Installed MVA is not spare capacity.
- **Optical fibre routes.** NEA's new subsidiary [[nepal-digital-infrastructure]] (NDICL) is building fibre on NEA's grid, but it has not published route length or topology.
- **Feeder-level reliability.** SAIDI/SAIFI and hourly outage data per feeder are not public.
- **Land and cooling-water availability.**

Until these are published, the table describes where high-voltage grid capacity and industrial land already meet. It does not show where a large load can actually connect.

## Limitations

- Installed and planned MVA come from NEA reporting and carry the substation inventory's caveats.
- The eastern industrial corridor shares the Inaruwa substation with a 400 kV grid-hub row, so Inaruwa's MVA appears twice. Do not sum MVA across hub types.
- Dharan Industrial District links to a *planned* 220 kV substation.
- Ecological belt is an administrative proxy for climate, not a site temperature or cooling measurement.

## Related

- [[data-substation-inventory]]
- [[data-load-anchors-and-fossil-backbone]]
- [[data-erc-retail-tariffs]]
- [[nepal-digital-infrastructure]]
- [[data-open-data-catalog]]
