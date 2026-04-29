---
title: Layer: Future Regulation Scenario
type: data
created: 2026-04-29
updated: 2026-04-29
figure_type: map-layer-label
sources: [data-map-inventory, data-storage-comparison]
tags: [maps, geojson, layers, explorer, legend, geopolitics, storage]
---

# Layer: Future Regulation Scenario

**Explorer label:** Flow regulation  
**Layer group:** Hydropower layers  
**Feature count:** 11

Storage-first scenario markers showing which projects could alter river timing, dry-season support, downstream sensitivity, and cooperation risk.

## What It Represents

This layer reframes the [[data-layer-storage-shortlist]] for the geopolitics preset. The question is not only how many MW each project adds. The question is whether a project can change the timing of water and electricity enough to matter downstream.

The layer includes mapped storage or storage-like candidates from the existing shortlist:

| Scenario role | Meaning |
|---------------|---------|
| `operating_baseline` | Existing storage that anchors the present system. |
| `near_term_storage` | Storage under construction or close enough to matter for near-term planning. |
| `advanced_planned_storage` | Planned storage with strong Nepal-side documentation and quantified dry-season value. |
| `promising_storage_candidate` | JICA/NEA promising-storage candidates with dry-energy or storage figures. |

## How To Read It

Use this layer with Nepal-origin downstream systems, basin polygons, downstream impact markers, and origin/control callouts. A marker should answer five questions:

| Field | How To Use It |
|-------|---------------|
| Timing (`scenario_horizon`) | Separates Already operating, Under construction, Planned, and Long-term candidate projects. |
| Flow impact (`regulation_potential`) | Indicates whether the project has baseline (no storage), low, medium, high, or very-high timing-regulation signal. |
| `downstream_name` | Names the downstream river system affected by the basin. |
| Downstream risk (`downstream_sensitivity`) | Flags whether the linked basin is geopolitically sensitive downstream. |
| Cooperation needed (`cooperation_potential`) | Identifies where regulation could create cooperative surplus rather than only unilateral leverage. |

The deterministic regulation classes are based on dry-season energy, total storage, and effective storage where available. They are scenario labels, not hydrodynamic model results.

## Caveats

This is a strategic interpretation layer. It does not model reservoir operations, treaty entitlements, flood-routing hydraulics, sediment trapping, irrigation withdrawals, or environmental-flow compliance.

Several projects are planning candidates rather than committed assets. Location precision varies by marker; use the Location source (`location_basis`) and `confidence` fields before treating a point as a site-grade location.

[[data-storage-comparison]] includes Chera-1 in the tabular research workspace, but Chera-1 is not exposed here because it does not currently have a reliable map anchor.

## Linked Data

- [future_regulation_scenario.geojson](../../../data/processed/maps/future_regulation_scenario.geojson) - generated scenario layer.
- [storage_shortlist_annotations.geojson](../../../data/processed/maps/storage_shortlist_annotations.geojson) - source annotation layer.
- [nepal_storage_dry_energy_shortlist.csv](../../../data/processed/tables/nepal_storage_dry_energy_shortlist.csv) - storage and dry-energy source table.

## Related

- [[downstream-river-geopolitics]]
- [[ganges-contribution]]
- [[hydro-geopolitics]]
- [[storage-deficit]]
- [[firm-power]]
- [[environmental-flow-policy]]
- [[data-layer-storage-shortlist]]
- [[data-map-layer-labels]]
