---
title: Map Layer Labels
type: data
created: 2026-04-25
updated: 2026-04-25
figure_type: map-spec
sources: [data-map-inventory]
tags: [maps, geojson, layers, explorer, legend]
page_quality: analysis
---

# Map Layer Labels

This page is the index for the explorer layer-control labels. Each row below links to an individual wiki page with deeper context, interpretation notes, caveats, and related pages. The hover popups in the map use the same labels and open these pages directly.

The layer stack mixes three kinds of controls: basemaps, evidence layers, and text-label overlays. Evidence layers are usually GeoJSON-backed. Basemaps and text labels change how the map reads, but they are still listed here because they shape interpretation.

## Basemaps

| Label | Features | Short meaning | Page |
|-------|---------:|---------------|------|
| Carto Positron | basemap | Neutral light basemap for reading dense hydrology, project, and transmission overlays without heavy terrain shading. | [[data-layer-carto-positron]] |
| Topographic | basemap | Terrain-oriented basemap useful for checking river corridors, valleys, ridge crossings, and Himalayan project context. | [[data-layer-topographic-basemap]] |
| Satellite | basemap | Imagery basemap for visual checking of settlements, reservoirs, roads, river valleys, and corridor anchors. | [[data-layer-satellite-basemap]] |

## Hydrology and basin layers

| Label | Features | Short meaning | Page |
|-------|---------:|---------------|------|
| Basin areas | 4 | Koshi, Gandaki, Karnali, and Mahakali upstream basin polygons, with Nepal share and monsoon context. | [[data-layer-nepal-linked-basin-polygons]] |
| India basins | 4 | Comparison basins outside Nepal-origin control, included to keep Nepal-origin leverage in proportion. | [[data-layer-india-comparison-basins]] |
| Nepal rivers | 22 | HydroRIVERS-derived Nepal tributaries relevant to the power and basin story, including WECS potential where available. | [[data-layer-nepal-tributaries]] |
| Downstream rivers | 4 | Main Nepal-origin systems traced downstream toward the Ganges plain to show where upstream control becomes regional influence. | [[data-layer-nepal-origin-downstream-systems]] |
| Ocean route | 4 | HydroRIVERS downstream traces continuing Nepal-linked systems through the Ganges/Padma/Meghna route to the Bay of Bengal. | [[data-layer-nepal-origin-ocean-routes]] |
| Route merge / delta callouts | 7 | Merge, transition, and delta markers that make the Nepal-origin route-to-ocean traces readable. | [[data-layer-nepal-origin-route-callouts]] |
| Downstream dependency zones | 5 | Strategic downstream exposure zones for agriculture, population, floods, dry-season flow, sediment, and delta sensitivity. | [[data-layer-downstream-dependency-zones]] |
| Downstream population anchors | 10 | City and delta anchors that locate the population geography along Nepal-linked downstream routes. | [[data-layer-downstream-population-anchors]] |
| India comparison rivers | 11 | Reference rivers outside Nepal-origin control, included so the map does not overstate Nepal's share of northern India hydrology. | [[data-layer-india-comparison-rivers]] |
| Flow measurements | 4 | Point markers carrying discharge, annual runoff, monsoon share, and impact notes for major systems. | [[data-layer-downstream-impact-markers]] |
| River influence | 8 | Interpretive callouts for origin, control class, Nepal share, and downstream identity across the basin stack. | [[data-layer-origin-control-callouts]] |
| Wet/dry season flow | 8 | Basin annotations focused on monsoon concentration, winter weakness, and dry-season implications. | [[data-layer-basin-seasonality]] |

## Hydropower layers

| Label | Features | Short meaning | Page |
|-------|---------:|---------------|------|
| Hydro — operating | 81 | Operating hydropower projects from the project registry. Marker area scales by capacity, and wiki counts show page coverage. | [[data-layer-hydropower-operating]] |
| Hydro — building | 180 | Generation/construction-license projects, useful for seeing near-term capacity pressure on basins and transmission corridors. | [[data-layer-hydropower-construction]] |
| Hydro — planned | 311 | Survey-stage hydropower licenses: early pipeline signals, not built capacity. | [[data-layer-hydropower-survey-study]] |
| Priority projects | 12 | Curated strategically important projects by size, storage value, basin leverage, financing, or transmission dependence. | [[data-layer-priority-watchlist]] |
| Storage reservoirs | 11 | Storage and storage-like projects highlighted for dry-season energy value, not just installed MW. | [[data-layer-storage-shortlist]] |
| Flow regulation | 11 | Storage-first scenario markers showing which projects could alter timing, downstream sensitivity, and cooperation risk. | [[data-layer-future-regulation-scenario]] |
| Top 10 largest | 10 | Largest hydropower projects in the display set, useful for separating headline MW from deliverable system value. | [[data-layer-top-10-capacity-projects]] |

## Transmission and trade layers

| Label | Features | Short meaning | Page |
|-------|---------:|---------------|------|
| Main network | 22 | Public-facing source-controlled transmission corridors, with status and provenance visible in popups. | [[data-layer-transmission-connected-traced-network]] |
| Power hubs & substations | 39 | Named grid hubs and substation/place anchors used to orient the network. | [[data-layer-grid-hubs-place-anchors]] |
| Cross-border lines | 10 | Conservative line/stub geometries for operational, under-construction, implementation-stage, and planned cross-border links. | [[data-layer-cross-border-interconnection-lines]] |
| International gateways | 10 | Nepal-side gateway points for cross-border interconnections with status and timeline context. | [[data-layer-cross-border-interconnections]] |
| Corridor sketch | 7 | Simplified substation sketch for orientation and not-yet-promoted corridor context. | [[data-layer-transmission-corridors-curated]] |

## Solar layers

| Label | Features | Short meaning | Page |
|-------|---------:|---------------|------|
| Solar resource zones | 6 | Coarse solar resource zones. These are strategic zones, not parcel-level siting decisions. | [[data-layer-solar-ghi-zones]] |
| Solar plants | 89 | Operating solar plants plus NEA 960 MW award anchors, with approximate-location flags where needed. | [[data-layer-solar-plants-nea-awards]] |
| Best solar locations | 6 | Strategic suitability bands combining resource value with constraint notes. | [[data-layer-solar-strategic-suitability]] |
| Floating solar | 5 | Reservoir or future-reservoir floating PV candidates with confidence and capacity-band fields. | [[data-layer-floating-pv-candidates]] |

## Text label overlays

| Label | Features | Short meaning | Page |
|-------|---------:|---------------|------|
| River name labels | text overlay | Permanent river and basin text labels. Turn these on when geography matters more than raw features. | [[data-layer-map-text-labels]] |
| Grid line labels | text overlay | Permanent corridor labels for grid overlays, separated from river labels to reduce low-zoom clutter. | [[data-layer-transmission-labels]] |

## Reading The Counts

- A plain feature count is the number of GeoJSON features in that layer after any manifest filter is applied.
- The layer-control count uses `wiki-backed / total` for larger layers. For example, hydropower layers show how many projects currently resolve to a wiki page out of all projects in that license-status group.
- Marker-size legends apply only to layers whose style scales radius by a numeric field, such as capacity.

## Related

- [[data-map-inventory]]
- [[project-roadmap]]
- [[claim-transmission-immediate-blocker]]
- [[storage-deficit]]
- [[ganges-contribution]]
