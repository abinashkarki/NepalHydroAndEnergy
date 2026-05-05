# Nepal Hydro & Energy Public Knowledge Hub

Public wiki, map, and data source for understanding Nepal's electricity transition: hydropower seasonality, storage scarcity, transmission bottlenecks, India-facing trade, the emerging solar complement to run-of-river hydro, and a structured project technical-specifications database comparable across 25+ projects.

The project combines source notes, derived datasets, interactive maps, a 339-page linked wiki, and a curated project-specs pipeline that feeds both the wiki and the map explorer from a single CSV.

## Highlights

- **339-page public wiki** covering sources, entities, concepts, data tables, tracked claims, syntheses, and interventions.
- **Structured project specs database** (`data/project_specs.csv`) — 25 hydropower projects, 41 fields across engineering, output, financial, governance, and schedule dimensions. Feeds wiki spec tables, map popups, and the fact index from a single source of truth.
- **Completeness reporting** — `scripts/report_spec_completeness.py` surfaces data-quality gaps per project and per field, making the research frontier visible.
- **Interactive Leaflet explorer** that links wiki pages to map layers, page bindings, backlinks, search metadata, and curated presets. Map popups now display turbine type, design energy, gross head, and other technical specs from the CSV.
- **Geospatial data pipeline** for Nepal-linked river basins, hydropower projects, transmission corridors, grid hubs, storage candidates, solar zones, and floating-PV candidates.
- **Seasonality and trade analysis** using NEA annual/daily reports to connect wet-season export surplus, dry-season imports, and storage scarcity.
- **Solar subsystem** added as a first-class analytical layer: GHI zones, plant/tender inventory, LCOE crossover, hydro complementarity, rural/off-grid politics, and map layers.

## Best Entry Points

- [Wiki index](wiki/index.md)
- [Master thesis](wiki/pages/syntheses/master-thesis.md)
- [Solar in the master narrative](wiki/pages/syntheses/solar-in-the-master-narrative.md)
- [Narrative report](docs/nepal_energy_hydropower_report.md)
- [Question-wise analysis](docs/nepal_energy_questionwise_analysis.md)
- [Lead 01 seasonality/storage/trade brief](docs/research_briefs/lead_01_seasonality_storage_trade.md)
- [Map explorer README](wiki/explorer/README.md)

## Project Technical Specifications

A structured data pipeline powers per-project technical specs across the wiki and map:

| Component | Path | Purpose |
|---|---|---|
| **Specs CSV** | `data/project_specs.csv` | Single source of truth — 25 projects, 41 columns across six sections |
| **JSON Schema** | `wiki/specs-schema.json` | Schema with controlled enums for dam type, turbine type, Q-design, status |
| **Vocabulary** | `wiki/explorer/shared/vocabulary.json` | Canonical vocabularies shared across schema, CSV, and UI |
| **Completeness report** | `scripts/report_spec_completeness.py` | Per-project and per-field coverage scoring |

**Data flow:**

```text
data/project_specs.csv  ← hand-curated, single source of truth
       │
       ├─→ build_tributary_maps.py   → GeoJSON display points (map popups/cards)
       ├─→ gen_wiki_stubs.py         → wiki spec tables (auto-stubs refreshed)
       ├─→ build_wiki_fact_index.py  → searchable structured facts
       └─→ report_spec_completeness.py → data-quality dashboard
```

**Projects covered (25):** Upper Tamakoshi, Arun-3, Dudhkoshi Storage, Kali Gandaki A, Tanahu, Chameliya, Sahas Urja, Chilime, Mugu Karnali Storage, Upper Karnali, Karnali Chisapani, Budhigandaki, Pancheshwar, Phukot Karnali, West Seti, Kulekhani Cascade, Nalsyau Gad, Lower Badigad, Naumure (W. Rapti), Sun Koshi No.3, Madi, Andhi Khola, Chera-1, Kokhajor-1, Lower Jhimruk.

Sources: JICA IPSDP Vol 2 (11 storage projects), NEA annual reports, UKHLL/SAPDC/CHCL project documents, VUCL feasibility studies, ADB evaluations, ICRA Nepal ratings.

## Interactive Explorer

**Live:** [https://transparentgov.ai/wiki/explorer/](https://transparentgov.ai/wiki/explorer/)

Run the wiki + map explorer locally:

```bash
./wiki/explorer/serve.sh 8765
```

Then open:

```text
http://localhost:8765/wiki/explorer/
```

Useful presets inside the explorer:

- **Tributaries**: river systems plus operating and under-construction hydropower.
- **Geopolitics**: Nepal-linked basins, downstream systems, comparison rivers, and control callouts.
- **Power**: transmission corridors, grid hubs, cross-border interconnections, priority projects, and storage.
- **Solar**: GHI zones, strategic suitability, operating plants, NEA 960 MW tender anchors, and floating-PV candidates.

## Repository Layout

```text
docs/                 Narrative reports, research briefs, and exported map HTML.
data/
  project_specs.csv    Structured project specs — single source of truth (25 projects, 41 fields).
  license_type_overrides.csv  Manual status corrections for 3 operating plants.
  raw/                 Source PDFs and raw downloaded inputs. Heavy files are mostly ignored.
  processed/
    maps/              GeoJSON layers for all map features (hydropower, storage, solar, etc.).
    tables/            Derived CSVs: storage shortlist, basin seasonality, NEA trade data, spec completeness.
    corridor_tracing/  Source inventory, trace targets, corridor confidence dossiers.
    text/              Extracted full-text versions of key source PDFs.
figures/              Static charts used in reports and briefs.
notes/                Working research notes by topic (hydrology, storage, grid economics, geopolitics).
scripts/
  build_tributary_maps.py     Main geo-data builder — rivers, basins, hydropower, annotations, scenarios.
  gen_wiki_stubs.py           Auto-generates wiki entity stubs with CSV-driven spec tables.
  report_spec_completeness.py Data-quality dashboard — per-project and per-field coverage scoring.
  validate_repo.py            Wiki links, cache consistency, map manifest, and specs CSV validation.
  build_wiki_*.py             Page index, metadata, backlinks, search, fact index, vector index.
  *_trade*.py                 NEA daily trade data, monthly balances, cross-border series.
  *_corridor*.py              Transmission corridor source and tracing manifests.
  *_pdf*.py                   PDF image extraction and atlas generation.
  *_solar*.py, *_figures*.py  Research figure builders.
wiki/
  spec-schema.json    JSON Schema for project_specs.csv with controlled enums.
  pages/              339 interlinked markdown pages across 7 categories.
  explorer/           Leaflet-based interactive map and wiki reader (static HTML + JS).
    shared/           Layer manifest, presets, bindings, vocabulary, search indices, page metadata.
```

## Reproducible Commands

Install Python dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Regenerate wiki explorer caches (page index, metadata, backlinks, search, vector index):

```bash
make wiki-index
```

Regenerate wiki stubs and sync map bindings (dry-run first):

```bash
python scripts/gen_wiki_stubs.py                           # preview
python scripts/gen_wiki_stubs.py --write --refresh-specs   # apply
```

Regenerate the map GeoJSON layers including project specs enrichment:

```bash
python scripts/build_tributary_maps.py
```

Generate the project specs completeness report:

```bash
python scripts/report_spec_completeness.py          # terminal summary
python scripts/report_spec_completeness.py --all    # also write CSV + markdown
```

Validate repo structure and generated metadata:

```bash
make validate
```

Serve the explorer:

```bash
make serve
```

Regenerate selected research figures:

```bash
python scripts/build_research_figures.py
```

## Data And Source Caveats

- This is an active public knowledge base. Pages distinguish between narrative analysis, source notes, data tables, auto-generated registry records, and hand-curated project profiles (tagged `generator: auto-stub` or `specs-refresh` in frontmatter).
- **Project specs.** The 25-project CSV is curated from multiple sources (JICA IPSDP, NEA reports, project documents, ICRA ratings). Coverage varies sharply — some projects have 14+ fields populated, most JICA-screened storage candidates have only 6. The completeness report surfaces these gaps explicitly. Spec values should be treated as "best available from cited source," not engineering-grade measurements.
- Some official Nepal electricity tables disagree internally; the wiki keeps those tensions visible instead of smoothing them away.
- Map layers are research visualizations, not hydrological or engineering-grade models. 10 of 25 spec-covered projects are enriched on the map; the remaining 15 either aren't in the DoED registry (conceptual/bilateral projects) or have slug mismatches with registry names.
- Several raw PDFs and large GIS bundles are ignored to keep the repository reviewable; derived artifacts and source notes remain tracked.
- A few external endpoints are unstable or protected, so not every raw download can be re-fetched reliably.
