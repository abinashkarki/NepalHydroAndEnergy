---
title: Map Inventory
type: data
created: 2026-04-15
updated: 2026-04-25
figure_type: map-spec
sources: [wecs-river-basin-plan-2024, nea-annual-report-fy2024-25]
tags: [maps, geojson, layers, inventory, multimodal]
page_quality: analysis
---

# Map Inventory

Catalog of the merged map stack imported from the code workspace. This page is the bridge between the wiki's analytical pages and the interactive / geospatial asset layer.

For the reader-facing legend and layer-control wording, see [[data-map-layer-labels]].

## Interactive Maps

- [Nepal Tributary Explorer](../../assets/maps/html/nepal_tributary_explorer.html)
- [Nepal Tributary Network](../../assets/maps/html/nepal_tributary_network.html)
- [Nepal River Geopolitics Explorer](../../assets/maps/html/nepal_geopolitics_river_influence.html)
- [Nepal Power System Explorer](../../assets/maps/html/nepal_power_system_explorer.html)

## Preview Images

- [Cross-border hydrology preview](../../assets/maps/previews/nepal_cross_border_hydrology.png)
- [Cross-border basin context preview](../../assets/maps/previews/nepal_cross_border_basin_context.png)
- [Cross-border projects preview](../../assets/maps/previews/nepal_cross_border_with_projects.png)
- [Geopolitics preview](../../assets/maps/previews/nepal_geopolitics_river_influence.png)

## Layer Inventory

| Layer | File | Feature count | Purpose |
|-------|------|--------------:|---------|
| Nepal tributaries | [nepal_relevant_tributaries.geojson](../../assets/maps/layers/nepal_relevant_tributaries.geojson) | 30 | Named hydropower-relevant Nepal rivers and tributaries |
| India comparison rivers | [india_reference_rivers.geojson](../../assets/maps/layers/india_reference_rivers.geojson) | 11 | Northern plains comparison rivers with no Nepal-origin control |
| Nepal-origin downstream systems | [nepal_origin_downstream_systems.geojson](../../assets/maps/layers/nepal_origin_downstream_systems.geojson) | 4 | Koshi, Gandaki, Karnali, Mahakali traced beyond Nepal |
| Nepal-origin routes to ocean | `data/processed/maps/nepal_origin_ocean_routes.geojson` | 4 | HydroRIVERS route extensions from Nepal-linked systems to the Bay of Bengal |
| Route merge / delta callouts | `data/processed/maps/nepal_origin_route_callouts.geojson` | 7 | Strategic merge, transition, and delta markers for route readability |
| Downstream dependency zones | `data/processed/maps/downstream_dependency_zones.geojson` | 5 | Broad downstream exposure zones for agriculture, population, flood, dry-season, sediment, and delta sensitivity |
| Downstream population anchors | `data/processed/maps/downstream_population_anchors.geojson` | 10 | City and delta anchors along Nepal-linked downstream routes |
| Nepal-linked basin polygons | [nepal_linked_basin_polygons.geojson](../../assets/maps/layers/nepal_linked_basin_polygons.geojson) | 4 | Upstream hydrologic polygons for Nepal-linked systems |
| India-origin comparison basins | [india_comparison_basin_polygons.geojson](../../assets/maps/layers/india_comparison_basin_polygons.geojson) | 4 | Comparison basins with zero Nepal-origin control |
| Origin/control callouts | [river_influence_callouts.geojson](../../assets/maps/layers/river_influence_callouts.geojson) | 8 | Basin-level interpretive labels and Nepal-share metadata |
| Downstream hydrology markers | [downstream_hydrology_markers.geojson](../../assets/maps/layers/downstream_hydrology_markers.geojson) | 4 | Discharge / monsoon-share marker points for main downstream systems |
| Nepal outline | [nepal_country_outline.geojson](../../assets/maps/layers/nepal_country_outline.geojson) | 1 | Base national boundary geometry |
| Solar GHI zones | `data/processed/maps/solar_ghi_zones.geojson` | 6 | Coarse resource-zone polygons from ESMAP / Global Solar Atlas interpretation |
| Solar plants and tender nodes | `data/processed/maps/solar_plants.geojson` | curated | Operating DoED plants plus NEA 960 MW LoI tender anchors |
| Solar suitability zones | `data/processed/maps/solar_suitability.geojson` | 6 | Strategic suitability bands, not parcel screening |
| Floating PV candidates | `data/processed/maps/floating_pv_candidates.geojson` | 5+ | Reservoir / future-reservoir candidates with explicit confidence fields |
| Future regulation scenario | `data/processed/maps/future_regulation_scenario.geojson` | 11 | Storage-first scenario layer for timing, downstream sensitivity, and cooperation potential |
| Major transmission network | `data/processed/maps/transmission_corridor_traced_network.geojson` | 22 | Source-controlled corridor geometry for the public grid layer |
| Cross-border links | `data/processed/maps/cross_border_interconnection_lines.geojson` | 10 | Conservative operational/planned interconnection lines and stubs |
| Grid hubs and substations | `data/processed/maps/place_anchor_index.geojson` | 39 | Named grid anchors used to orient the transmission network |

## Coverage Notes

- Hydropower overlay in the explorer uses the merged [naxa_hydropower_projects.csv](../../../data/processed/naxa_hydropower_projects.csv) dataset with **572** project records.
- The geopolitics layer carries the highest-value infographic metadata: upstream basin area, approximate Nepal area share, control class, and monsoon share.
- Current callout examples:
  - **Koshi-Kosi system:** ~63,142 km² upstream basin, ~49.8% Nepal area share, **73%** monsoon share.
  - **Gandaki-Narayani-Gandak:** ~42,541 km², ~75.5% Nepal area share, **74%** monsoon share.
  - **Karnali-Ghaghara:** ~22,732 km², ~86.1% Nepal area share, **72%** monsoon share.

## Known Gaps

- Exact OSM linework was **not** recovered for **West Seti River**, **Chameliya River**, and **West Rapti River**; they are flagged in the fetch report rather than invented.
- Some transmission corridors remain corridor-grade rather than tower-by-tower alignments; the public network exposes status, confidence, and source provenance instead of hiding that uncertainty.
- Cross-border interconnections are now mapped conservatively as gateway lines/stubs, with operational and planned links styled distinctly.
- Solar layers are curated evidence layers, not engineering-grade GIS. Exact-looking points are used only where DoED coordinates exist; tender markers use substation or district anchors with Location source (`location_basis`) and `precision_label`.

## Next Annotation Layers

These are the clearest upgrades if the map stack is pushed further toward infographic use:

- Continue promoting high-value transmission corridors from conceptual context into the major transmission network as route-grade evidence is recovered.
- Tie cross-border interconnection capacity and utilization back to [[data-trade-time-series]].
- **Storage annotations** for [[kulekhani-cascade]], [[tanahu-hydropower]], [[budhigandaki]], and [[dudhkoshi-storage]]
- **Future regulation scenario** is now exposed as [[data-layer-future-regulation-scenario]], using mapped storage candidates as a strategic timing layer.
- **Sediment / GLOF hazard markers** for [[koshi-basin]] and key Gandaki corridors
- **Basin popup sparklines** showing monsoon vs dry share directly inside the map
- **System-scale Ganges contribution arrows** to reinforce [[ganges-contribution]] beyond the new [[data-layer-nepal-origin-ocean-routes]] route traces and [[data-layer-downstream-dependency-zones]].
- **Solar system preset** tying [[data-nepal-solar-resource-zones]], [[data-solar-fleet-inventory]], [[nea-960mw-solar-tender]], and [[claim-floating-pv-leverage]] to the explorer

## Related

- [[koshi-basin]]
- [[gandaki-basin]]
- [[karnali-basin]]
- [[mahakali-basin]]
- [[claim-transmission-immediate-blocker]]
- [[data-nepal-solar-resource-zones]]
- [[data-solar-fleet-inventory]]
- [[claim-floating-pv-leverage]]
- [[data-map-layer-labels]]
