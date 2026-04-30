# Nepal Energy 3D Terrain Explorer

Phase 1 is a focused vertical slice for a project-first 3D companion to the wiki explorer.

## Vision

Nepal Energy is not just a map of where energy assets sit. The important question is why those assets matter in that location.

For Nepal, the answer is usually terrain: river drops, valley access, ridge crossings, transmission bottlenecks, dry-season storage value, and the distance between hydropower potential and deliverable power. The 3D Terrain Explorer is intended to make that visible.

The long-term product direction is a curated 3D atlas where a wiki page can open a real terrain scene: the project, river, basin, corridor, and nearby system context are all visible immediately.

## Current Phase

Phase 1 is the Upper Tamakoshi vertical slice.

The goal is not to build the full national 3D atlas yet. The goal is to make one scene feel credible and useful:

- Upper Tamakoshi opens directly from `?page=upper-tamakoshi`
- the camera starts in an oblique terrain view
- the project marker is visible without extra toggles
- the Tama Koshi River is highlighted
- nearby hydropower context can be shown
- the sidebar explains the selected feature
- the user can zoom, rotate, tilt, reset, and toggle scene layers

This keeps the experiment reversible while proving the interaction model.

## How To Run

From the repository root:

```bash
cd wiki/explorer
./serve.sh
```

Open:

```text
http://localhost:8765/wiki/explorer/3d-terrain.html?page=upper-tamakoshi&v=phase1
```

The page must be served over HTTP. Opening the file directly with `file://` will break data loading.

## What Works Now

- CesiumJS runtime loaded from `wiki/explorer/lib/cesium/`
- Esri World Imagery satellite basemap
- ArcGIS WorldElevation3D terrain, with a flat fallback if terrain is unavailable
- Upper Tamakoshi project marker from existing GeoJSON data
- Tama Koshi River highlight from existing tributary data
- secondary hydropower context from existing hydropower project points
- optional transmission and basin context
- clickable Cesium entities with sidebar cards
- grouped scene toggles
- explicit camera controls for zoom, rotation, top-down view, oblique view, and reset
- elevation profile panel with a clear fallback state when terrain sampling fails

## Data Sources

The 3D scene does not duplicate project data. It reads the same source files as the 2D explorer:

- `shared/layer-manifest.json`
- `shared/bindings.json`
- `data/processed/maps/*.geojson`

Upper Tamakoshi is resolved through the existing `upper-tamakoshi` binding, including the historical `hydropower_points` alias used by the split hydropower layers.

## Known Limits

- This is not a full national 3D atlas yet.
- Only Upper Tamakoshi is curated as a first-class scene.
- No GLB or architectural 3D models are included yet.
- Imagery and terrain depend on external Esri/ArcGIS services.
- Terrain sampling may fail in constrained browsers or offline environments; the scene still renders with a fallback profile.
- The 2D explorer remains the primary production UI while this branch matures.

## Future Deliveries

Likely next product increments:

1. Add more curated project scenes: Arun 3, Budhigandaki, West Seti, Kulekhani, Tanahu, and key transmission corridors.
2. Add 2D-to-3D deep links from wiki pages and map popups.
3. Make elevation profiles selectable for any river, headrace, or transmission corridor.
4. Add simple generated 3D structure markers for dams, powerhouses, substations, and towers before investing in detailed GLB models.
5. Add narrative tours that explain one energy system story at a time.
6. Add export paths for Google Earth/KML/KMZ once the in-app scene model is stable.
7. Evolve scene configuration out of the HTML into a declarative manifest when there are enough scenes to justify it.

## Product Evolution Notes

The direction is intentionally product-led, not technology-led. Cesium is useful only if the scene helps users understand Nepal's energy geography faster than the 2D map alone.

Phase 1 should be judged by whether Upper Tamakoshi feels informative, explorable, and grounded in terrain. If the scene works, future work can expand coverage and polish the system. If it feels noisy or unclear, the scene model should be simplified before adding more projects.
