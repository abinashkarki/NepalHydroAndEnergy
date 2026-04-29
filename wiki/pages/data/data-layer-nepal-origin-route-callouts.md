---
title: Layer: Nepal-Origin Route Callouts
type: data
created: 2026-04-30
updated: 2026-04-30
figure_type: map-layer-label
sources: [data-map-inventory]
tags: [maps, geojson, layers, explorer, geopolitics, ganges, bangladesh]
---

# Layer: Nepal-Origin Route Callouts

**Explorer label:** Route merge / delta callouts  
**Layer group:** Hydrology and basin layers  
**Feature count:** 7

Merge, transition, and delta markers that make the Nepal-origin route-to-ocean traces readable.

## What It Represents

This layer adds strategic reading points to [[data-layer-nepal-origin-ocean-routes]]. It marks where individual Nepal-linked systems enter larger downstream trunks, where the Ganges becomes the Padma system, and where the route reaches the lower delta / Bay of Bengal terminal reach.

The layer is designed for map comprehension. It does not replace surveyed confluence geometry or a delta distributary model.

For the non-technical reading sequence, start with [[how-to-read-geopolitics-map]].

## How To Read It

Use the callouts as handoff markers:

| Callout type | Meaning |
|--------------|---------|
| `origin_handoff` | A Nepal-linked route enters the wider downstream plains system. |
| `major_merge` | A Nepal-origin route joins the Ganges trunk. |
| `system_transition` | The route crosses into a different downstream naming or political geography. |
| `delta_merge` | The shared trunk reaches lower delta logic. |
| `ocean_endpoint` | The generated route terminal reach. |

Important fields:

| Field | How To Use It |
|-------|---------------|
| `related_origin_routes` | Links the marker back to the route traces it helps explain. |
| `river_system` | Names the downstream trunk or transition point. |
| `strategic_note` | Explains why this marker matters to the geopolitics story. |
| `map_read_note` | States the precision caveat for the point. |
| `confidence` | Flags how strongly to read the marker position. |

## Caveats

These are strategic callouts, not engineering-grade confluence points. Coordinates are intentionally approximate and are used to make the route-to-ocean layer legible at explorer scale.

Dense distributaries, tidal channels, barrages, embankments, irrigation withdrawals, and local floodplain storage are out of scope for this v1 layer.

## Linked Data

- [nepal_origin_route_callouts.geojson](../../../data/processed/maps/nepal_origin_route_callouts.geojson)
- [downstream_dependency_layers_report.json](../../../data/processed/maps/downstream_dependency_layers_report.json)

## Related

- [[how-to-read-geopolitics-map]]
- [[mahakali-sharda-handoff]]
- [[ghaghara-ganges-merge]]
- [[gandak-ganges-merge]]
- [[kosi-ganges-merge]]
- [[ganges-padma-transition]]
- [[padma-meghna-delta]]
- [[bay-of-bengal-terminal]]
- [[data-layer-nepal-origin-ocean-routes]]
- [[data-layer-downstream-dependency-zones]]
- [[downstream-river-geopolitics]]
- [[ganges-contribution]]
- [[hydro-geopolitics]]
