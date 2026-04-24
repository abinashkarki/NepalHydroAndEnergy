# Nepal Hydro & Energy Knowledge System

## Project Summary

Built an interactive research system for Nepal's electricity transition, focused on hydropower seasonality, storage scarcity, transmission bottlenecks, India-facing power trade, and solar-hydro complementarity.

The project combines a linked research wiki, derived datasets, curated GeoJSON layers, static figures, and a browser-based Leaflet explorer. It is designed to turn scattered official reports and PDFs into a navigable evidence system.

## What It Demonstrates

- **Research engineering**: converted official reports, PDFs, tables, and source notes into reusable structured outputs.
- **Geospatial analysis**: built map layers for basins, rivers, hydropower projects, storage candidates, transmission corridors, grid hubs, solar zones, and floating-PV candidates.
- **Knowledge-system design**: maintained a 247-page wiki with page types, backlinks, cache metadata, spatial bindings, and full-text search.
- **Energy-system reasoning**: connected Nepal's monsoon hydrograph, dry-season imports, storage deficit, transmission constraints, and solar economics into one strategic frame.
- **Source discipline**: tracked claims separately from concepts and data pages, with confidence, provenance, and caveats.

## Current Outputs

- Interactive wiki/map explorer with presets for hydrology, geopolitics, power system, and solar system views.
- 247 wiki pages across sources, entities, concepts, syntheses, claims, and data.
- Processed GeoJSON map layers under `data/processed/maps/`.
- Research briefs and narrative reports under `docs/`.
- Regeneration scripts for wiki caches, figures, map layers, and selected source extractions.

## Technical Stack

- Python for extraction, transformation, validation, and figure generation.
- GeoJSON + Leaflet for map layers and browser exploration.
- Markdown/YAML for wiki pages and source/provenance metadata.
- Static JSON caches for page index, backlinks, and search metadata.

## Why It Matters

Nepal is often described as a hydropower-rich country. This project reframes that into a system question: can Nepal convert hydrological advantage and cheap solar complementarity into firm, deliverable, financeable power at the right time of year?

That framing is visible in the data model and the interface: pages, maps, claims, and source summaries are linked so a reader can move from a policy claim to the underlying geography, source documents, and system constraints.
