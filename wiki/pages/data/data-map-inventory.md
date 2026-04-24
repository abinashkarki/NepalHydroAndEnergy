---
title: Map Inventory
type: data
created: 2026-04-15
updated: 2026-04-24
figure_type: map-spec
sources: [wecs-river-basin-plan-2024, nea-annual-report-fy2024-25]
tags: [maps, geojson, layers, inventory, multimodal]
---

# Map Inventory

Catalog of the merged map stack imported from the code workspace. This page is the bridge between the wiki's analytical pages and the interactive / geospatial asset layer.

## Interactive Maps

- [Nepal Tributary Explorer](../../assets/maps/html/nepal_tributary_explorer.html)
- [Nepal Tributary Network](../../assets/maps/html/nepal_tributary_network.html)
- [Nepal River Geopolitics Explorer](../../assets/maps/html/nepal_geopolitics_river_influence.html)

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
| Nepal-linked basin polygons | [nepal_linked_basin_polygons.geojson](../../assets/maps/layers/nepal_linked_basin_polygons.geojson) | 4 | Upstream hydrologic polygons for Nepal-linked systems |
| India-origin comparison basins | [india_comparison_basin_polygons.geojson](../../assets/maps/layers/india_comparison_basin_polygons.geojson) | 4 | Comparison basins with zero Nepal-origin control |
| Origin/control callouts | [river_influence_callouts.geojson](../../assets/maps/layers/river_influence_callouts.geojson) | 8 | Basin-level interpretive labels and Nepal-share metadata |
| Downstream hydrology markers | [downstream_hydrology_markers.geojson](../../assets/maps/layers/downstream_hydrology_markers.geojson) | 4 | Discharge / monsoon-share marker points for main downstream systems |
| Nepal outline | [nepal_country_outline.geojson](../../assets/maps/layers/nepal_country_outline.geojson) | 1 | Base national boundary geometry |
| Solar GHI zones | `data/processed/maps/solar_ghi_zones.geojson` | 6 | Coarse resource-zone polygons from ESMAP / Global Solar Atlas interpretation |
| Solar plants and tender nodes | `data/processed/maps/solar_plants.geojson` | curated | Operating DoED plants plus NEA 960 MW LoI tender anchors |
| Solar suitability zones | `data/processed/maps/solar_suitability.geojson` | 6 | Strategic suitability bands, not parcel screening |
| Floating PV candidates | `data/processed/maps/floating_pv_candidates.geojson` | 5+ | Reservoir / future-reservoir candidates with explicit confidence fields |

## Coverage Notes

- Hydropower overlay in the explorer uses the merged [naxa_hydropower_projects.csv](../../../data/processed/naxa_hydropower_projects.csv) dataset with **572** project records.
- The geopolitics layer carries the highest-value infographic metadata: upstream basin area, approximate Nepal area share, control class, and monsoon share.
- Current callout examples:
  - **Koshi-Kosi system:** ~63,142 km² upstream basin, ~49.8% Nepal area share, **73%** monsoon share.
  - **Gandaki-Narayani-Gandak:** ~42,541 km², ~75.5% Nepal area share, **74%** monsoon share.
  - **Karnali-Ghaghara:** ~22,732 km², ~86.1% Nepal area share, **72%** monsoon share.

## Known Gaps

- Exact OSM linework was **not** recovered for **West Seti River**, **Chameliya River**, and **West Rapti River**; they are flagged in the fetch report rather than invented.
- No transmission-corridor layer exists yet for the seven segments documented in [[claim-transmission-immediate-blocker]].
- No cross-border interconnection-point layer yet exists for Dhalkebar-Muzaffarpur, New Butwal-Gorakhpur, or other trade chokepoints.
- Solar layers are curated evidence layers, not engineering-grade GIS. Exact-looking points are used only where DoED coordinates exist; tender markers use substation or district anchors with `precision_label` and `location_basis`.

## Next Annotation Layers

These are the clearest upgrades if the map stack is pushed further toward infographic use:

- **Transmission corridors** from [[claim-transmission-immediate-blocker]]
- **Cross-border interconnection nodes** tied to [[data-trade-time-series]]
- **Storage annotations** for [[kulekhani-cascade]], [[tanahu-hydropower]], [[budhigandaki]], and [[dudhkoshi-storage]]
- **Sediment / GLOF hazard markers** for [[koshi-basin]] and key Gandaki corridors
- **Basin popup sparklines** showing monsoon vs dry share directly inside the map
- **System-scale Ganges contribution arrows** to reinforce [[ganges-contribution]]
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
