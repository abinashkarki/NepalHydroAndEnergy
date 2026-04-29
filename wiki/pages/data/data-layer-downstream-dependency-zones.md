---
title: Layer: Downstream Dependency Zones
type: data
created: 2026-04-30
updated: 2026-04-30
figure_type: map-layer-label
sources: [data-map-inventory]
tags: [maps, geojson, layers, explorer, geopolitics, agriculture, floodplains, delta]
---

# Layer: Downstream Dependency Zones

**Explorer label:** Downstream dependency zones  
**Layer group:** Hydrology and basin layers  
**Feature count:** 5

Strategic downstream exposure zones for agriculture, population, floods, dry-season flow, sediment, and delta sensitivity.

## What It Represents

This layer turns the route-to-ocean trace into a downstream stakes map. It marks broad regions where Nepal-linked river routes pass through dense agricultural plains, flood-sensitive corridors, and the Bangladesh delta system.

For the non-technical reading sequence, start with [[how-to-read-geopolitics-map]]. For the main synthesis, use [[downstream-river-geopolitics]].

The five v1 zones are:

| Zone | Main read |
|------|-----------|
| Eastern Uttar Pradesh Ghaghara-Gandak belt | Western and central Nepal-linked routes entering dense agricultural plains. |
| North Bihar Kosi-Gandak floodplain | High exposure to flood timing, sediment, agriculture, and dense settlement. |
| Bihar Ganges trunk zone | Shared Ganges corridor where separate Nepal-linked routes become a common downstream geography. |
| Padma-Meghna delta dependency zone | Bangladesh-scale delta exposure to upstream timing, sediment, and flood pulses. |
| Lower delta and Bay interface | Coastal-delta context for sediment, salinity, storm surge exposure, and delta stability. |

## How To Read It

Use these polygons as strategic context around the river route, not as precise service areas.

Important fields:

| Field | How To Use It |
|-------|---------------|
| `related_origin_routes` | Links each zone to the Nepal-origin route traces that pass into or through it. |
| `population_pressure` | Qualitative pressure class for map interpretation. |
| `agriculture_importance` | Qualitative agriculture relevance. |
| `dry_season_sensitivity` | Whether timing and dry-season support are strategically relevant. |
| `flood_sensitivity` | Whether monsoon flood timing and attenuation matter. |
| `sediment_sensitivity` | Whether sediment behavior should be part of the strategic read. |
| `delta_sensitivity` | Whether the zone is part of lower-delta vulnerability. |
| `strategic_read` | Plain-language interpretation for popups. |

## Caveats

This is not a hydrodynamic model, irrigation command map, population raster, crop-intensity map, or flood hazard model. It does not claim that Nepal controls total water availability in these zones.

The correct reading is: these are downstream exposure zones touched by Nepal-linked river routes where timing, sediment, flood behavior, and dry-season flow can become politically meaningful.

## Linked Data

- [downstream_dependency_zones.geojson](../../../data/processed/maps/downstream_dependency_zones.geojson)
- [downstream_dependency_layers_report.json](../../../data/processed/maps/downstream_dependency_layers_report.json)

## Related

- [[how-to-read-geopolitics-map]]
- [[eastern-up-ghaghara-gandak-belt]]
- [[north-bihar-kosi-gandak-floodplain]]
- [[bihar-ganges-trunk-zone]]
- [[padma-meghna-delta-dependency]]
- [[lower-delta-bay-interface]]
- [[data-layer-nepal-origin-ocean-routes]]
- [[data-layer-nepal-origin-route-callouts]]
- [[data-layer-downstream-population-anchors]]
- [[downstream-river-geopolitics]]
- [[ganges-contribution]]
- [[storage-deficit]]
