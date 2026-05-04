# Nepal Tributary Maps

## Primary entry point — Wiki & Map explorer

The four HTML maps below are now available as **switchable lenses inside the wiki+map explorer**, alongside the wiki content. Open the explorer and use the preset bar at the top of the map to flip between the same four views; each preset is also deep-linkable via `?preset=…&page=…`.

- [`/wiki/explorer/index.html`](./wiki/explorer/index.html) — single-page viewer with all four lenses + the wiki

| Folium HTML | Explorer preset | Deep link |
|---|---|---|
| `nepal_tributary_explorer.html` | **Tributary explorer** (default) | `?preset=tributary_explorer` |
| `nepal_tributary_network.html` | **River network** | `?preset=tributary_network` |
| `nepal_geopolitics_river_influence.html` | **Geopolitics** | `?preset=geopolitics` |
| `nepal_power_system_explorer.html` | **Power system** | `?preset=power_system` |

Both the static HTMLs and the explorer presets render the same underlying GeoJSON layers from `data/processed/maps/`. The presets are defined in `wiki/explorer/shared/presets.json` and only differ from each other (and from the static HTMLs) in default-on layers and initial fit-bounds.

## Static interactive maps (still published)

Useful when you want a single self-contained file to share, embed, or open offline. They do not include the wiki side-pane, search, or layer-add behavior.

- [Nepal Tributary Explorer](./docs/maps/nepal_tributary_explorer.html)
- [Nepal Tributary Network](./docs/maps/nepal_tributary_network.html)
- [Nepal River Geopolitics Explorer](./docs/maps/nepal_geopolitics_river_influence.html)
- [Nepal Power System Explorer](./docs/maps/nepal_power_system_explorer.html)

## Preview images

- [Cross-border hydrology preview](./docs/maps/nepal_cross_border_hydrology.png)
- [Cross-border view with hydropower projects](./docs/maps/nepal_cross_border_with_projects.png)
- [Cross-border basin context preview](./docs/maps/nepal_cross_border_basin_context.png)
- [Geopolitics map preview](./docs/maps/nepal_geopolitics_river_influence.png)

## Source layers

- [Relevant tributaries GeoJSON](./data/processed/maps/nepal_relevant_tributaries.geojson)
- [Northern Indian comparison rivers GeoJSON](./data/processed/maps/india_reference_rivers.geojson)
- [Nepal-origin downstream systems GeoJSON](./data/processed/maps/nepal_origin_downstream_systems.geojson)
- [Nepal-linked basin polygons GeoJSON](./data/processed/maps/nepal_linked_basin_polygons.geojson)
- [India-origin comparison basin polygons GeoJSON](./data/processed/maps/india_comparison_basin_polygons.geojson)
- [Origin comparison callouts GeoJSON](./data/processed/maps/river_influence_callouts.geojson)
- [Downstream impact markers GeoJSON](./data/processed/maps/downstream_hydrology_markers.geojson)
- [Nepal country outline GeoJSON](./data/processed/maps/nepal_country_outline.geojson)
- [Basin seasonality annotations GeoJSON](./data/processed/maps/basin_seasonality_annotations.geojson)
- [Top capacity project annotations GeoJSON](./data/processed/maps/top_capacity_project_annotations.geojson)
- [Priority project watchlist GeoJSON](./data/processed/maps/priority_project_watchlist.geojson)
- [Storage shortlist annotations GeoJSON](./data/processed/maps/storage_shortlist_annotations.geojson)
- [Transmission corridors GeoJSON](./data/processed/maps/transmission_corridors.geojson)
- [Official transmission linework from RPGCL geospatial PDF](./data/processed/maps/rpgcl_transmission_official_linework.geojson)
- [Official transmission map labels from RPGCL geospatial PDF](./data/processed/maps/rpgcl_transmission_official_labels.geojson)
- [Traced transmission corridor segments](./data/processed/maps/transmission_corridor_traced_segments.geojson)
- [Connected traced transmission network](./data/processed/maps/transmission_corridor_traced_network.geojson)
- [Internal topology nodes](./data/processed/maps/transmission_network_nodes.geojson)
- [Internal transmission trace gap report GeoJSON](./data/processed/maps/transmission_trace_gap_report.geojson)
- [Transmission corridor validation report](./data/processed/maps/transmission_corridor_validation_report.json)
- [Transmission network build report](./data/processed/maps/transmission_network_build_report.json)
- [Transmission corridor dossiers](./data/processed/maps/transmission_corridor_dossiers.json)
- [Cross-border interconnection dossiers](./data/processed/maps/cross_border_interconnection_dossiers.json)
- [Grid confidence report](./docs/maps/grid_confidence_report.md)
- [Transmission warning burn-down](./docs/maps/transmission_warning_burndown.md)
- [MCA Annex D-1 atlas index](./data/processed/corridor_tracing/mca_annex_d1/mca_annex_d1_atlas_index.json)
- [MCA Central atlas trace](./data/raw/corridor_tracing/mca/mca_central_400_atlas_trace.geojson)
- [Hetauda-Dhalkebar-Inaruwa RAP trace](./data/raw/corridor_tracing/world_bank/hddi_400_rap_trace.geojson)
- [Hetauda-Bharatpur-Bardaghat source trace](./data/raw/corridor_tracing/nea/hetauda_bharatpur_bardaghat_220_source_trace.geojson)
- [Udipur-Markichowk-Bharatpur RAP trace](./data/raw/corridor_tracing/nea/udipur_damauli_bharatpur_220_rap_trace.geojson)
- [Transmission tracing report](./data/processed/maps/rpgcl_transmission_trace_report.json)
- [India cross-border interconnections GeoJSON](./data/processed/maps/cross_border_interconnections.geojson)
- [India cross-border interconnection lines](./data/processed/maps/cross_border_interconnection_lines.geojson)
- [Place anchor index GeoJSON](./data/processed/maps/place_anchor_index.geojson)
- [Annotation build report](./data/processed/maps/annotation_build_report.json)
- [Power-system build report](./data/processed/maps/power_system_build_report.json)
- [Hydropower display points GeoJSON](./data/processed/maps/hydropower_project_display_points.geojson)
- [Hydropower anchor report](./data/processed/maps/hydropower_project_anchor_report.json)
- [River network QA report](./data/processed/maps/river_network_qa_report.json)
- [Tributary compatibility report](./data/processed/maps/tributary_fetch_report.json)
- [India river fetch report](./data/processed/maps/india_reference_rivers_report.json)

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
- a connected traced-network layer that preserves raw source/manual traces, adds explicit threshold-bounded inferred connectors, and emits gap diagnostics where the evidence is still too weak
- 10 Nepal-India interconnection nodes split by operational, under-construction, implementation-setup, and planned status
- 10 conservative cross-border connector/stub lines, with non-operational links styled as dashed/fainter features
- dedicated transmission hub and cross-border gateway node layers for the power-system view

The public river layer now uses HydroRIVERS Asia as the published geometry source and keeps OSM waterway names only as corridor hints, label context, and sanity checks. Rivers that do not pass the automated topology gates or explicit manual review are withheld from the public GeoJSON rather than drawn as fragmented placeholders.

The annotation build currently skips one storage-shortlist project because it does not yet have a defensible map anchor in the current source stack:

- Chera-1

## Notes

The default explorer now keeps the denser India labels, detailed tributary labels, basin polygons, callouts, hydropower project layers, and all transmission/network overlays switched off so the hydrology remains readable. Turn them on from the layer control when you want basin geometry, plains-river detail, project context, or grid context.

The new power-system map flips that emphasis. It keeps the major transmission network, grid hubs and substations, cross-border gateways and conservative cross-border links, priority watchlist, hydropower build/operating cloud, and storage shortlist on first, while river layers stay available but switched off by default.

Hydropower markers now use a precision-aware display model rather than treating every registry point as an exact site. Operating projects stay as higher-confidence site points. Most survey and generation licenses are displayed as river-aligned references when a plausible mapped river can be matched nearby, and only the residual weak matches remain as raw registry references. The matching stack now uses reviewed tributary geometry first, then exact-name OSM waterway fallback for local reaches that the published tributary layer does not carry cleanly, and finally HydroRIVERS reach context. An optional dashed offset layer shows where the displayed reference point differs materially from the raw registry coordinate.

The power-system view now also includes a curated `Priority projects + radar surveys` layer turned on by default. It is intentionally smaller than the full project cloud: six operating/buildout priorities and six large survey-stage projects that are worth tracking even before they have fully defensible site-grade geometry. A small subset of the radar watchlist now uses document-backed anchors instead of plain registry points, including Arun-3 near Num, Upper Karnali near the published powerhouse vicinity by Tallo Balde Khola, and Betan Karnali near Tatalighat.

The geopolitics map switches the basin polygons and origin/control callouts on by default. It is meant to answer a different question from the explorer: where Nepal materially sits inside the upstream geography of Gangetic-plain river systems, and where it does not.

The seasonal overlay is an interpretation layer built from the basin-level monsoon share values used in the research notes. It is useful for relative comparison, not for plant-by-plant dispatch modeling.

The new annotation layers are also interpretation layers. Basin seasonality labels are grounded in the WECS basin-plan table, but storage-shortlist markers mix exact project points, clustered existing project points, and river or basin anchors depending on source availability. The popup for each annotation states the anchor basis explicitly.

The map now contains one public transmission layer and a small set of context/support layers:

- `Major transmission network` is the public-facing default. It carries source/manual traces plus explicitly marked `inferred_connector` segments where traced endpoints fall inside conservative snap thresholds. Any bigger break stays in the internal validation reports rather than being hidden by a guessed line.
- `Context · corridor sketch` is a simplified substation-to-substation sketch. It is useful for orientation and for corridors that do not have route-grade public geometry, but it is off by default. If it shows a connection missing from the major network, that is a promotion candidate, not confirmed route geometry.
- Internal topology nodes and trace gaps are still generated for checking joins, endpoints, and evidence gaps, but they are not exposed as public map layers.

The major transmission network covers `hddi_400`, `hetauda_bharatpur_bardaghat_220`, `dana_kushma_butwal_220`, `mca_central_400`, `udipur_damauli_bharatpur_220`, `western_132_backbone`, `chameliya_attariya_132`, `kohalpur_surkhet_dailekh_132`, `kabeli_132`, `marsyangdi_upper_220`, and `solu_tingla_mirchaiya_132`. HDDI is split into mixed-status sections so Hetauda-Dhalkebar remains under construction while Dhalkebar-Inaruwa is operational. The western 132 kV additions explain the operational grid reach beyond Butwal without pretending those lines are 220/400 kV transfer assets.

Transmission is now styled as a neutral dashed network overlay rather than another colored hydro path. Grid hubs are shown with circle nodes and cross-border gateways with diamond nodes so the power system reads differently from rivers.

Those traced corridors are still national-scale routes, not tower-by-tower engineering alignments. Some come from official vector linework, while `hddi_400`, `kabeli_132`, and `marsyangdi_upper_220` are manual/document-grounded traces from recovered corridor packets. All of them are a major upgrade from the old substation-spine approximation, but they should still be read as corridor geometry rather than final cadastral alignment.

The cross-border interconnection point layer uses Nepal-side interconnection nodes or border-gate nodes. The new line layer connects to a defensible India-side place anchor where one is present; otherwise it draws only a short gateway stub. It does not guess full Indian-side routes, and planned / implementation-stage links are dashed and fainter than operational links.

The 132 kV corridors should be read as grid-reach and evacuation context, not bulk-transfer equivalents to 220/400 kV. Western operational 132 kV lines now use RPGCL official vector linework controlled by NEA FY2024/25 inventory lengths. The eastern `kabeli_132` and `solu_tingla_mirchaiya_132` traces remain weaker because they are reconstructed from recovered NEA documents rather than official vector extraction or full alignment-sheet digitization.

The basin polygons are derived from HydroBASINS Asia level 6, aggregated upstream from selected outlet points on the relevant river trunks. They are hydrologic polygons, not administrative river-basin plan boundaries.

River QA now has an explicit internal review workflow. Review contact sheets are generated under `./tmp/river_review/`, manual decisions and river-specific routing overrides live in `./data/raw/maps/river_network_review_overrides.json`, and only rivers with both `qa_status=pass` and `review_status=pass` are published in `nepal_relevant_tributaries.geojson`.
