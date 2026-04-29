---
title: Layer: Nepal-Origin Routes To Ocean
type: data
created: 2026-04-29
updated: 2026-04-29
figure_type: map-layer-label
sources: [data-map-inventory]
tags: [maps, geojson, layers, explorer, legend, geopolitics, ganges, bangladesh]
---

# Layer: Nepal-Origin Routes To Ocean

**Explorer label:** Nepal-origin routes to ocean  
**Layer group:** Hydrology and basin layers  
**Feature count:** 4

HydroRIVERS downstream traces continuing Nepal-linked systems through the Ganges/Padma/Meghna route to the Bay of Bengal.

## What It Represents

This layer extends the existing [[data-layer-nepal-origin-downstream-systems]] beyond the northern plains. It lets the reader follow each Nepal-linked system through the larger Ganges network toward the Bay of Bengal.

The four route features are:

| Route | Origin system | Merge system |
|-------|---------------|--------------|
| Koshi route to Bay of Bengal | Koshi-Kosi | Kosi-Ganges-Padma-Meghna |
| Gandaki route to Bay of Bengal | Gandaki-Narayani-Gandak | Gandak-Ganges-Padma-Meghna |
| Karnali route to Bay of Bengal | Karnali-Ghaghara | Ghaghara-Ganges-Padma-Meghna |
| Mahakali route to Bay of Bengal | Mahakali-Sharda | Sharda-Ghaghara-Ganges-Padma-Meghna |

## How To Read It

Use this as a strategic continuity layer. The existing downstream-system lines show Nepal-to-plains routing; this layer shows how those systems enter the shared lower Ganges route and ultimately reach the Bay of Bengal.

Important fields:

| Field | How To Use It |
|-------|---------------|
| `merge_system` | Names the downstream trunk each Nepal-linked route joins. |
| `route_confidence` | Indicates how confidently the current downstream endpoint snapped to HydroRIVERS. |
| `snap_distance_km` | Shows the distance between the existing mapped endpoint and the HydroRIVERS route start. |
| `route_length_km` | Approximate downstream route length in the generated trace. |
| `source_method` | Records the HydroRIVERS `NEXT_DOWN` tracing method. |

## Caveats

This is a topology and communication layer, not a hydrodynamic model. It does not represent reservoir operations, flow volumes after withdrawals, distributary splits, tidal dynamics, embankments, barrages, irrigation diversions, or floodplain storage.

Dense delta distributaries are intentionally out of scope for v1. The layer preserves one strategic trunk per Nepal-linked system so the reader can follow the basin story without turning the map into a complete delta-network inventory.

## Linked Data

- [nepal_origin_ocean_routes.geojson](../../../data/processed/maps/nepal_origin_ocean_routes.geojson) - generated route layer.
- [downstream_ocean_route_report.json](../../../data/processed/maps/downstream_ocean_route_report.json) - route QA report.

## Related

- [[downstream-river-geopolitics]]
- [[ganges-contribution]]
- [[hydro-geopolitics]]
- [[data-layer-nepal-origin-downstream-systems]]
- [[data-layer-downstream-impact-markers]]
