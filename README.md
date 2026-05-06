# Nepal Energy Wiki & Explorer

Public wiki, map explorer, and structured data project for understanding Nepal's electricity system: hydropower seasonality, storage scarcity, transmission bottlenecks, India-facing trade, solar complementarity, and project-level technical records.

Live site: [transparentgov.ai/wiki/explorer](https://transparentgov.ai/wiki/explorer/)

## What this repo contains

This repository combines four things:

- a linked public wiki
- a static Leaflet-based map explorer
- a structured hydropower project-specifications database
- Python build scripts that generate the explorer assets and wiki metadata

The repo is meant to be both a public-facing knowledge product and a working research system. Pages, map layers, and structured records are intentionally connected.

## Core architecture

| Component | Path | Purpose |
|---|---|---|
| Wiki pages | `wiki/pages/` | Interlinked markdown pages across entities, concepts, claims, data, syntheses, interventions, and sources |
| Explorer app | `wiki/explorer/` | Static HTML/JS app that combines the map and wiki reader |
| Project specs database | `data/project_specs.csv` | Hand-curated structured project data used across the wiki and map |
| Built map layers | `data/processed/maps/` | GeoJSON outputs for hydropower, transmission, basins, storage, solar, and scenarios |
| Build scripts | `scripts/` | Python tooling for explorer data, wiki caches, search, backlinks, and stubs |

The deployable surfaces are primarily:

- `wiki/`
- `data/processed/maps/`

The rest of the repository is development tooling, source material, documentation, and working research support.

## Project specs pipeline

`data/project_specs.csv` is the single structured source of truth for technical project records.

```text
data/project_specs.csv
       │
       ├─→ scripts/build_tributary_maps.py
       │     → GeoJSON display points and map popups/cards
       ├─→ scripts/gen_wiki_stubs.py
       │     → wiki stub/spec table generation
       ├─→ scripts/build_wiki_fact_index.py
       │     → searchable structured facts
       └─→ scripts/report_spec_completeness.py
             → data-quality reporting
```

Related files:

- Schema: `wiki/specs-schema.json`
- Explorer vocabulary: `wiki/explorer/shared/vocabulary.json`
- Validation: `scripts/validate_repo.py`

## Repo layout

```text
data/
  project_specs.csv
  license_type_overrides.csv
  processed/
    maps/
    tables/
    corridor_tracing/
    text/
  raw/

docs/
  maps/
  research_briefs/

scripts/
  build_tributary_maps.py
  gen_wiki_stubs.py
  report_spec_completeness.py
  validate_repo.py
  build_wiki_*.py

wiki/
  explorer/
    index.html
    shared/
  pages/
  specs-schema.json
```

## Best entry points

- [wiki/index.md](wiki/index.md)
- [wiki/explorer/README.md](wiki/explorer/README.md)
- [docs/maps/README.md](docs/maps/README.md)
- [docs/agent-handoff-may-2026.md](docs/agent-handoff-may-2026.md)

## Local setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Common workflows

Rebuild wiki metadata:

```bash
make wiki-index
```

Preview wiki stub/spec updates:

```bash
python scripts/gen_wiki_stubs.py
```

Apply wiki stub/spec updates:

```bash
python scripts/gen_wiki_stubs.py --write --refresh-specs
```

Rebuild map GeoJSON and explorer-facing layer data:

```bash
python scripts/build_tributary_maps.py
```

Generate the spec completeness report:

```bash
python scripts/report_spec_completeness.py --all
```

Validate the repository:

```bash
make validate
```

Run the explorer locally:

```bash
make serve
```

Then open:

```text
http://localhost:8765/wiki/explorer/
```

## Working on the explorer

The explorer is configured declaratively through:

- `wiki/explorer/shared/layer-manifest.json`
- `wiki/explorer/shared/presets.json`
- `wiki/explorer/shared/bindings.json`

In practice, explorer changes usually touch one or more of:

- `wiki/explorer/index.html`
- `wiki/explorer/shared/*.js`
- `wiki/explorer/shared/*.json`
- `data/processed/maps/*.geojson`
- `scripts/build_tributary_maps.py`

If you change layer data or popup fields, rebuild the map outputs and run `make validate`.

## Wiki page types

Wiki pages are not all maintained the same way. Frontmatter determines how some pages participate in generation pipelines.

- `generator: auto-stub`
  - registry-style page
  - spec table can be refreshed automatically
  - intentionally minimal narrative
- `generator: specs-refresh`
  - hand-curated page with structured sections that can be refreshed
  - prose survives pipeline refreshes
- `generator: manual`
  - fully hand-maintained
  - skipped by the specs refresh pipeline

## Data and quality notes

- This is a public research system, not an engineering-grade plant database.
- Some layers are approximate by design and should be interpreted as analytical map references, not surveyed coordinates.
- Official power-sector documents often disagree internally; the project keeps those tensions visible instead of flattening them away.
- Coverage in `data/project_specs.csv` is intentionally incomplete where sources are weak; `report_spec_completeness.py` exists to make that visible.
- Some raw PDFs, GIS bundles, and extracted artifacts are too large or unstable to track or re-fetch reliably in a simple way.

## Deployment note

The live site deploys from `main`. If work is done on a side branch, merging to `main` is the step that updates the deploy source.

## Related docs

- [wiki/explorer/README.md](wiki/explorer/README.md)
- [docs/maps/README.md](docs/maps/README.md)
- [AGENTS.md](AGENTS.md)
