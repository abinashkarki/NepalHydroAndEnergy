---
title: Layer: Downstream Population Anchors
type: data
created: 2026-04-30
updated: 2026-04-30
figure_type: map-layer-label
sources: [data-map-inventory]
tags: [maps, geojson, layers, explorer, geopolitics, population, cities]
page_quality: analysis
---

# Layer: Downstream Population Anchors

**Explorer label:** Downstream population anchors  
**Layer group:** Hydrology and basin layers  
**Feature count:** 10

City and delta anchors that locate the population geography along Nepal-linked downstream routes.

## What It Represents

This layer adds named places to the downstream river story so the route and dependency zones are easier to orient. The anchors include major cities, delta nodes, and river-port style points along the Ganges, Kosi/Gandak/Ghaghara plains, Padma, and lower delta.

All population-anchor popups route here because the project needs context, not a general-purpose city encyclopedia. The points are orientation marks for [[how-to-read-geopolitics-map]] and [[downstream-river-geopolitics]].

## How To Read It

Use the points to locate the human geography around the river system:

| Field | How To Use It |
|-------|---------------|
| `nearby_river_system` | The river system that gives the anchor its map relevance. |
| `related_origin_routes` | Nepal-linked routes associated with the downstream geography. |
| `population_class` | Qualitative city/metro/delta class. |
| `dependency_note` | Plain-language reason the point is included. |
| `floodplain_context` | Caveat against over-attribution. |

## Caveats

These anchors do not imply that a city is supplied only by Nepal-origin rivers. They are context markers for downstream geography, population concentration, floodplain exposure, and route legibility.

Coordinates are city/context anchors, not water-intake points, flood gauge locations, or infrastructure nodes.

## Linked Data

- [downstream_population_anchors.geojson](../../../data/processed/maps/downstream_population_anchors.geojson)
- [downstream_dependency_layers_report.json](../../../data/processed/maps/downstream_dependency_layers_report.json)

## Related

- [[how-to-read-geopolitics-map]]
- [[data-layer-downstream-dependency-zones]]
- [[data-layer-nepal-origin-ocean-routes]]
- [[downstream-river-geopolitics]]
- [[ganges-contribution]]
- [[india-energy-relationship]]
