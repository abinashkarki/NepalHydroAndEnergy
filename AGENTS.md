# AGENTS.md — nepalEnergy

Project overview for AI agents and contributors working in this repository.

## What this repo is

A public wiki and interactive map explorer covering Nepal's electricity system — hydropower projects, transmission corridors, storage, solar complementarity, seasonal mismatch, electricity trade, and system-level energy analysis. The live site is at [transparentgov.ai/wiki/explorer](https://transparentgov.ai/wiki/explorer/).

## Architecture

| Component | Description |
|---|---|
| `wiki/pages/` | ~340 interlinked markdown pages — entities, concepts, claims, sources, data |
| `wiki/explorer/` | Leaflet-based interactive map + wiki reader, served as static HTML |
| `data/processed/maps/` | GeoJSON layers (hydropower, transmission, basins, scenarios) |
| `scripts/` | Python build tools — page index, backlinks, search, map data pipelines |

The `wiki/` and `data/processed/maps/` directories are the deployable content surfaced on the live site. `scripts/`, `docs/`, `notes/`, `figures/`, and `data/raw/` are development tooling.

## Local Development

```bash
# Install deps
python -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt

# Regenerate wiki metadata (backlinks, search index, page index, presets)
make wiki-index

# Validate generated files
make validate

# Serve explorer locally
make serve     # or: ./wiki/explorer/serve.sh 8765
# Then open: http://localhost:8765/wiki/explorer/
```

## Key Paths

| Path | What |
|---|---|
| `wiki/explorer/index.html` | Main explorer app (Leaflet map + wiki browser) |
| `wiki/explorer/shared/` | Layer manifest, presets, bindings, tour, search index, page metadata |
| `scripts/build_tributary_maps.py` | Main geo-data builder (annotations, corridors, scenario layers) |
| `data/processed/maps/` | Built GeoJSON outputs |
| `wiki/pages/` | Wiki content (markdown, interlinked) |
