# AGENTS.md — nepalEnergy

Project overview for AI agents and contributors working in this repository.

## What this repo is

A public wiki and interactive map explorer covering Nepal's electricity system — hydropower projects, transmission corridors, storage, solar complementarity, seasonal mismatch, electricity trade, and system-level energy analysis. Now includes a structured project technical-specifications database (25 projects, 41 fields) that feeds both the wiki and map from a single CSV. The live site is at [transparentgov.ai/wiki/explorer](https://transparentgov.ai/wiki/explorer/).

## Architecture

| Component | Description |
|---|---|
| `wiki/pages/` | 339 interlinked markdown pages — entities, concepts, claims, sources, data, syntheses, interventions |
| `wiki/explorer/` | Leaflet-based interactive map + wiki reader, served as static HTML |
| `data/project_specs.csv` | Structured project specs — single source of truth for technical data |
| `data/processed/maps/` | GeoJSON layers (hydropower, transmission, basins, scenarios) |
| `scripts/` | Python build tools — page index, backlinks, search, map data pipelines |

The `wiki/` and `data/processed/maps/` directories are the deployable content surfaced on the live site. `scripts/`, `docs/`, `notes/`, `figures/`, and `data/raw/` are development tooling.

## Project Specs Pipeline

`data/project_specs.csv` is the structured data backbone — hand-curated, single source of truth. Flows to three surfaces:

```text
data/project_specs.csv
       │
       ├─→ build_tributary_maps.py   → GeoJSON display points (map popups/cards)
       ├─→ gen_wiki_stubs.py         → auto-stub wiki spec tables
       ├─→ build_wiki_fact_index.py  → searchable structured facts
       └─→ report_spec_completeness.py → data-quality dashboard
```

**Schema:** `wiki/specs-schema.json` (JSON Schema with controlled enums). **Vocabulary:** `wiki/explorer/shared/vocabulary.json`. **Validation:** `scripts/validate_repo.py` checks CSV column structure and orphaned slugs.

**Generator types in wiki frontmatter:**
- `generator: auto-stub` — pure registry stub, spec table auto-refreshed, "no narrative" badge in UI
- `generator: specs-refresh` — hand-curated page with rich prose, classified as refreshable but markers absent (prose sections survive pipeline)
- `generator: manual` — fully hand-maintained, skipped by spec refresh

## Local Development

```bash
# Install deps
python -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt

# Regenerate wiki metadata (backlinks, search index, page index, presets)
make wiki-index

# Regenerate wiki stubs with CSV-driven specs (dry-run first)
python scripts/gen_wiki_stubs.py
python scripts/gen_wiki_stubs.py --write --refresh-specs

# Regenerate GeoJSON layers with specs enrichment
python scripts/build_tributary_maps.py

# Completeness report
python scripts/report_spec_completeness.py --all

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
| `wiki/explorer/shared/` | Layer manifest, presets, bindings, vocabulary, search index, page metadata |
| `scripts/build_tributary_maps.py` | Main geo-data builder (annotations, corridors, scenario layers, specs merge) |
| `scripts/gen_wiki_stubs.py` | Wiki stub generator — reads CSV, generates sectioned spec tables |
| `scripts/report_spec_completeness.py` | Per-project and per-field data-quality scoring |
| `data/project_specs.csv` | Master structured specs — 25 projects, 41 columns |
| `wiki/specs-schema.json` | JSON Schema with controlled enums |
| `data/processed/maps/` | Built GeoJSON outputs |
| `data/processed/tables/` | Derived CSVs including spec_completeness_report |
| `wiki/pages/` | Wiki content (markdown, interlinked) |
