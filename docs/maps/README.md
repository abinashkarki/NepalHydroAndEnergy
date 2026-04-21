# Nepal Tributary Maps

## Primary entry point — Wiki & Map explorer

The four HTML maps below are now available as **switchable lenses inside the wiki+map explorer**, alongside the wiki content. Open the explorer and use the preset bar at the top of the map to flip between the same four views; each preset is also deep-linkable via `?preset=…&page=…`.

- [`/wiki/explorer/index.html`](/Users/hi/projects/nepalEnergy/wiki/explorer/index.html) — single-page viewer with all four lenses + the wiki

| Folium HTML | Explorer preset | Deep link |
|---|---|---|
| `nepal_tributary_explorer.html` | **Tributary explorer** (default) | `?preset=tributary_explorer` |
| `nepal_tributary_network.html` | **River network** | `?preset=tributary_network` |
| `nepal_geopolitics_river_influence.html` | **Geopolitics** | `?preset=geopolitics` |
| `nepal_power_system_explorer.html` | **Power system** | `?preset=power_system` |

Both the static HTMLs and the explorer presets render the same underlying GeoJSON layers from `data/processed/maps/`. The presets are defined in `wiki/explorer/shared/presets.json` and only differ from each other (and from the static HTMLs) in default-on layers and initial fit-bounds.

## Static interactive maps (still published)

Useful when you want a single self-contained file to share, embed, or open offline. They do not include the wiki side-pane, search, or layer-add behavior.

- [Nepal Tributary Explorer](/Users/hi/projects/nepalEnergy/docs/maps/nepal_tributary_explorer.html)
- [Nepal Tributary Network](/Users/hi/projects/nepalEnergy/docs/maps/nepal_tributary_network.html)
- [Nepal River Geopolitics Explorer](/Users/hi/projects/nepalEnergy/docs/maps/nepal_geopolitics_river_influence.html)
- [Nepal Power System Explorer](/Users/hi/projects/nepalEnergy/docs/maps/nepal_power_system_explorer.html)

## Preview images

- [Cross-border hydrology preview](/Users/hi/projects/nepalEnergy/docs/maps/nepal_cross_border_hydrology.png)
- [Cross-border view with hydropower projects](/Users/hi/projects/nepalEnergy/docs/maps/nepal_cross_border_with_projects.png)
- [Cross-border basin context preview](/Users/hi/projects/nepalEnergy/docs/maps/nepal_cross_border_basin_context.png)
- [Geopolitics map preview](/Users/hi/projects/nepalEnergy/docs/maps/nepal_geopolitics_river_influence.png)

## Source layers

- [Relevant tributaries GeoJSON](/Users/hi/projects/nepalEnergy/data/processed/maps/nepal_relevant_tributaries.geojson)
- [Northern Indian comparison rivers GeoJSON](/Users/hi/projects/nepalEnergy/data/processed/maps/india_reference_rivers.geojson)
- [Nepal-origin downstream systems GeoJSON](/Users/hi/projects/nepalEnergy/data/processed/maps/nepal_origin_downstream_systems.geojson)
- [Nepal-linked basin polygons GeoJSON](/Users/hi/projects/nepalEnergy/data/processed/maps/nepal_linked_basin_polygons.geojson)
- [India-origin comparison basin polygons GeoJSON](/Users/hi/projects/nepalEnergy/data/processed/maps/india_comparison_basin_polygons.geojson)
- [Origin comparison callouts GeoJSON](/Users/hi/projects/nepalEnergy/data/processed/maps/river_influence_callouts.geojson)
- [Downstream impact markers GeoJSON](/Users/hi/projects/nepalEnergy/data/processed/maps/downstream_hydrology_markers.geojson)
- [Nepal country outline GeoJSON](/Users/hi/projects/nepalEnergy/data/processed/maps/nepal_country_outline.geojson)
- [Basin seasonality annotations GeoJSON](/Users/hi/projects/nepalEnergy/data/processed/maps/basin_seasonality_annotations.geojson)
- [Top capacity project annotations GeoJSON](/Users/hi/projects/nepalEnergy/data/processed/maps/top_capacity_project_annotations.geojson)
- [Priority project watchlist GeoJSON](/Users/hi/projects/nepalEnergy/data/processed/maps/priority_project_watchlist.geojson)
- [Storage shortlist annotations GeoJSON](/Users/hi/projects/nepalEnergy/data/processed/maps/storage_shortlist_annotations.geojson)
- [Transmission corridors GeoJSON](/Users/hi/projects/nepalEnergy/data/processed/maps/transmission_corridors.geojson)
- [Official transmission linework from RPGCL geospatial PDF](/Users/hi/projects/nepalEnergy/data/processed/maps/rpgcl_transmission_official_linework.geojson)
- [Official transmission map labels from RPGCL geospatial PDF](/Users/hi/projects/nepalEnergy/data/processed/maps/rpgcl_transmission_official_labels.geojson)
- [Traced transmission corridor segments](/Users/hi/projects/nepalEnergy/data/processed/maps/transmission_corridor_traced_segments.geojson)
- [Transmission tracing report](/Users/hi/projects/nepalEnergy/data/processed/maps/rpgcl_transmission_trace_report.json)
- [India cross-border interconnections GeoJSON](/Users/hi/projects/nepalEnergy/data/processed/maps/cross_border_interconnections.geojson)
- [Place anchor index GeoJSON](/Users/hi/projects/nepalEnergy/data/processed/maps/place_anchor_index.geojson)
- [Annotation build report](/Users/hi/projects/nepalEnergy/data/processed/maps/annotation_build_report.json)
- [Power-system build report](/Users/hi/projects/nepalEnergy/data/processed/maps/power_system_build_report.json)
- [Hydropower display points GeoJSON](/Users/hi/projects/nepalEnergy/data/processed/maps/hydropower_project_display_points.geojson)
- [Hydropower anchor report](/Users/hi/projects/nepalEnergy/data/processed/maps/hydropower_project_anchor_report.json)
- [River network QA report](/Users/hi/projects/nepalEnergy/data/processed/maps/river_network_qa_report.json)
- [Tributary compatibility report](/Users/hi/projects/nepalEnergy/data/processed/maps/tributary_fetch_report.json)
- [India river fetch report](/Users/hi/projects/nepalEnergy/data/processed/maps/india_reference_rivers_report.json)

## Coverage

The explorer now combines:

- 22 reviewed, connected HydroRIVERS-backed Nepal rivers and tributaries currently cleared for publication across the Koshi, Gandaki, Karnali, Mahakali, and medium-basin systems
- 11 northern Gangetic comparison rivers in India
- 4 traced Nepal-origin downstream systems extending beyond Nepal's borders
- 4 HydroBASINS-derived Nepal-linked upstream basin polygons
- 4 HydroBASINS-derived India-origin comparison basin polygons
- origin/control callouts comparing Nepal-linked systems against non-Nepal comparison basins
- decluttered default labeling with separate major and detailed tributary label layers
- seasonal impact overlays for monsoon dominance and dry-season share
- all 572 hydropower projects in Nepal, with detailed popups and an optional dense label layer
- hydropower project display anchors split into 81 higher-confidence site points, 427 river-aligned references, and 64 raw registry references
- a curated 12-project watchlist mixing priority operating/build projects with a few large survey-stage projects kept on the radar
- basin seasonality annotations built from the research CSV
- a top-10 MW project annotation layer built from the Naxa / DoED-linked project dataset
- a storage shortlist annotation layer with dry-energy callouts where a defensible point or river anchor exists
- 7 source-backed transmission corridor spines built from NEA, MCA-Nepal, ADB, and World Bank project references
- 7 traced transmission corridor families combining official RPGCL vector extraction and recovered/manual NEA corridor tracing
- 10 Nepal-India interconnection nodes split by operational, under-construction, implementation-setup, and planned status
- dedicated transmission hub and cross-border gateway node layers for the power-system view

The public river layer now uses HydroRIVERS Asia as the published geometry source and keeps OSM waterway names only as corridor hints, label context, and sanity checks. Rivers that do not pass the automated topology gates or explicit manual review are withheld from the public GeoJSON rather than drawn as fragmented placeholders.

The annotation build currently skips one storage-shortlist project because it does not yet have a defensible map anchor in the current source stack:

- Chera-1

## Notes

The default explorer now keeps the denser India labels, detailed tributary labels, basin polygons, callouts, hydropower project layers, and all transmission/network overlays switched off so the hydrology remains readable. Turn them on from the layer control when you want basin geometry, plains-river detail, project context, or grid context.

The new power-system map flips that emphasis. It keeps the traced transmission layer, grid hubs, cross-border gateways, top-capacity projects, and storage shortlist on first, while river layers stay available but switched off by default.

Hydropower markers now use a precision-aware display model rather than treating every registry point as an exact site. Operating projects stay as higher-confidence site points. Most survey and generation licenses are displayed as river-aligned references when a plausible mapped river can be matched nearby, and only the residual weak matches remain as raw registry references. The matching stack now uses reviewed tributary geometry first, then exact-name OSM waterway fallback for local reaches that the published tributary layer does not carry cleanly, and finally HydroRIVERS reach context. An optional dashed offset layer shows where the displayed reference point differs materially from the raw registry coordinate.

The power-system view now also includes a curated `Priority projects + radar surveys` layer turned on by default. It is intentionally smaller than the full project cloud: six operating/buildout priorities and six large survey-stage projects that are worth tracking even before they have fully defensible site-grade geometry. A small subset of the radar watchlist now uses document-backed anchors instead of plain registry points, including Arun-3 near Num, Upper Karnali near the published powerhouse vicinity by Tallo Balde Khola, and Betan Karnali near Tatalighat.

The geopolitics map switches the basin polygons and origin/control callouts on by default. It is meant to answer a different question from the explorer: where Nepal materially sits inside the upstream geography of Gangetic-plain river systems, and where it does not.

The seasonal overlay is an interpretation layer built from the basin-level monsoon share values used in the research notes. It is useful for relative comparison, not for plant-by-plant dispatch modeling.

The new annotation layers are also interpretation layers. Basin seasonality labels are grounded in the WECS basin-plan table, but storage-shortlist markers mix exact project points, clustered existing project points, and river or basin anchors depending on source availability. The popup for each annotation states the anchor basis explicitly.

The map now contains two transmission geometry tiers. `Transmission corridors` is still the curated fallback spine layer. `Transmission corridors (traced)` is the higher-quality layer built from a mix of official RPGCL vector extraction and recovered NEA PDF tracing. It now covers `hddi_400`, `hetauda_bharatpur_bardaghat_220`, `mca_central_400`, `udipur_damauli_bharatpur_220`, `kabeli_132`, `marsyangdi_upper_220`, and `solu_tingla_mirchaiya_132`. The Solu trace is source-grounded but lower-confidence than the route-atlas corridors because it is reconstructed from narrative pages and anchored place names rather than a published alignment sheet.

Transmission is now styled as a neutral dashed network overlay rather than another colored hydro path. Grid hubs are shown with circle nodes and cross-border gateways with diamond nodes so the power system reads differently from rivers.

Those traced corridors are still national-scale routes, not tower-by-tower engineering alignments. Some come from official vector linework, while `kabeli_132` and `marsyangdi_upper_220` are manual traces from recovered NEA corridor packets. All of them are a major upgrade from the old substation-spine approximation, but they should still be read as corridor geometry rather than final cadastral alignment.

The cross-border interconnection layer uses Nepal-side interconnection nodes or border-gate nodes rather than guessed route geometry inside India. This keeps the map honest while still showing where Nepal's export and import gateways sit.

The eastern 132 kV corridors are still the weakest traced set. `kabeli_132` and `solu_tingla_mirchaiya_132` are now present in traced form from recovered NEA material, but both remain manual/document-grounded traces rather than official vector extraction or full alignment-sheet digitization.

The basin polygons are derived from HydroBASINS Asia level 6, aggregated upstream from selected outlet points on the relevant river trunks. They are hydrologic polygons, not administrative river-basin plan boundaries.

River QA now has an explicit internal review workflow. Review contact sheets are generated under `/Users/hi/projects/nepalEnergy/tmp/river_review/`, manual decisions and river-specific routing overrides live in `/Users/hi/projects/nepalEnergy/data/raw/maps/river_network_review_overrides.json`, and only rivers with both `qa_status=pass` and `review_status=pass` are published in `nepal_relevant_tributaries.geojson`.
