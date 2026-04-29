---
title: Layer: Storage Shortlist
type: data
created: 2026-04-25
updated: 2026-04-25
figure_type: map-layer-label
sources: [data-map-inventory, data-storage-comparison]
tags: [maps, geojson, layers, explorer, legend]
---

# Layer: Storage Shortlist

**Explorer label:** Storage reservoirs  
**Layer group:** Hydropower layers  
**Feature count:** 11

Storage and storage-like projects highlighted for dry-season energy value, not just installed MW.

## What It Represents

This layer isolates projects that matter for seasonal balancing. Nepal's core hydro problem is not annual water volume alone; it is the mismatch between wet-season abundance and dry-season scarcity. Storage and storage-like projects are therefore treated differently from ordinary run-of-river MW.

The shortlist combines three evidence types:

| Category | Meaning | Projects In Layer |
|----------|---------|-------------------|
| Operating storage | Existing seasonal-storage asset already serving the system | Kulekhani I-III |
| Under-construction storage | Near-term storage addition in the official project stack | Tanahu |
| Advanced / promising planned storage | Projects with dry-energy or storage figures strong enough to matter for the winter deficit argument | Dudhkoshi Storage, Nalsyau Gad, Lower Badigad, Naumure, Sun Koshi No.3, Madi, Andhi Khola, Kokhajor-1, Lower Jhimruk |

The point of the layer is to separate **firm or seasonal value** from nameplate capacity. A project with moderate MW can matter more than a larger wet-season-heavy project if it contributes dependable dry-season energy.

## Included Projects

| Project | Basin | MW | Dry Energy | Dry Share | Priority Read |
|---------|-------|---:|-----------:|----------:|---------------|
| Kulekhani I-III | Bagmati | 106 | n/a | n/a | Only operating seasonal-storage cascade in Nepal; crucial for dry-month balancing and peaking. |
| Tanahu | Gandaki | 140 | n/a | n/a | Most practical near-term new storage addition in the checked official set. |
| Dudhkoshi Storage | Koshi | 670 | 1,252.0 GWh | 37.1% | Largest quantified dry-season block in the checked official Nepal-side sources. |
| Nalsyau Gad | Karnali | 410 | 581.8 GWh | 41.4% | Best dry-energy output in the JICA promising-project set. |
| Lower Badigad | Gandaki | 380.3 | 354.7 GWh | 26.0% | Large Gandaki carryover storage plus strong dry output. |
| Naumure (W. Rapti) | West Rapti | 245 | 309.9 GWh | 26.8% | Very large effective storage for a medium-basin project. |
| Sun Koshi No.3 | Koshi | 536 | 335.9 GWh | 17.8% | Large east-central reservoir block with meaningful dry support. |
| Madi | West Rapti | 199.8 | 170.7 GWh | 27.5% | Moderate MW but useful dry-energy ratio in a water-deficit medium basin. |
| Andhi Khola | Gandaki | 180 | 137.1 GWh | 21.1% | Smaller but still meaningful dry-energy contributor. |
| Kokhajor-1 | Koshi | 111.5 | 94.1 GWh | 33.7% | High dry-energy share for a relatively small plant. |
| Lower Jhimruk | West Rapti | 142.5 | 94.4 GWh | 20.8% | Useful medium-basin storage candidate, though layout conflicts with Naumure in the current design. |

## How To Read It

Use it with basin seasonality, cross-border trade, transmission, and priority-watchlist layers. The main question is not "how many MW?" but "how much controllable dry-season support does this project add, and where does that support land in the grid?"

The key fields are:

| Field | How To Use It |
|-------|---------------|
| `category` | Distinguishes operating, under-construction, advanced planned, and JICA promising-storage records. |
| Installed capacity (`installed_mw`) | Nameplate capacity; useful but secondary to seasonal output. |
| Annual energy (`annual_energy_gwh`) | Total expected generation where available. |
| Dry-season energy (`dry_energy_gwh`) | The most important value field for the storage argument. |
| Dry-season share (`dry_share_pct`) | Dry-season output as a share of annual energy; useful for comparing differently sized projects. |
| `total_storage_mcm` / `effective_storage_mcm` | Reservoir scale where the source provides it. |
| Why it matters (`priority_read`) | Plain-language reason the project was included. |
| `source_note` | Shows whether the record comes from NEA annual reporting, NEA-linked project notes, or the JICA/NEA storage master plan. |

The layer works best as a filter over Nepal's broader hydro portfolio. It keeps the storage question visible while the user inspects large projects, transmission corridors, and seasonal trade behavior.

## Caveats

Storage labels do not settle design, resettlement, environmental, financing, treaty, or procurement questions. Some projects are storage-like or proposed rather than confirmed deliverable storage assets.

Several records are planning candidates from the JICA/NEA storage master-plan material rather than committed projects. Dry-energy values are therefore analytical anchors, not delivery forecasts. Location precision also varies: some markers use project or operating-plant points, while others use river anchors because the public source is stronger on project concept than on map geometry.

The shortlist has 11 map features, while [[data-storage-comparison]] also discusses Chera-1 in the broader 12-project table. Chera-1 is retained in the tabular research workspace but is not currently exposed as a map marker in this layer.

## Linked Data

- [storage_shortlist_annotations.geojson](../../../data/processed/maps/storage_shortlist_annotations.geojson) - 11-feature explorer annotation layer.
- [nepal_storage_dry_energy_shortlist.csv](../../../data/processed/tables/nepal_storage_dry_energy_shortlist.csv) - 12-project dry-energy table, including fields not all shown on the map.
- [[data-storage-comparison]] - wider storage-gap and dry-energy comparison context.

## Related

- [[storage-deficit]]
- [[firm-power]]
- [[seasonal-arbitrage-trap]]
- [[claim-storage-physical-fix]]
- [[claim-mw-not-equal-value]]
- [[data-layer-basin-seasonality]]

- [[data-map-layer-labels]]
- [[data-map-inventory]]
