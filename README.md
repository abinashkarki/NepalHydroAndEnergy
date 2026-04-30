# Nepal Hydro & Energy Public Knowledge Hub

Public wiki, map, and data source for understanding Nepal's electricity transition: hydropower seasonality, storage scarcity, transmission bottlenecks, India-facing trade, and the emerging solar complement to run-of-river hydro.

The project combines source notes, derived datasets, interactive maps, and a 309-page linked wiki that can be searched and explored spatially.

## Highlights

- **309-page public wiki** covering sources, entities, concepts, data tables, tracked claims, and syntheses.
- **Interactive Leaflet explorer** that links wiki pages to map layers, page bindings, backlinks, search metadata, and curated presets.
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
data/raw/             Source PDFs and raw downloaded inputs. Heavy files are mostly ignored.
data/processed/       Derived tables, GeoJSON layers, extracted text, and map metadata.
figures/              Static charts used in reports and briefs.
notes/                Working research notes by topic.
scripts/              Data extraction, map generation, wiki cache, and validation scripts.
wiki/                 Linked research wiki and browser explorer.
```

## Reproducible Commands

Install Python dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Regenerate wiki explorer caches:

```bash
make wiki-index
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

- This is an active public knowledge base. Pages distinguish between narrative analysis, source notes, data tables, and registry-backed project records.
- Some official Nepal electricity tables disagree internally; the wiki keeps those tensions visible instead of smoothing them away.
- Map layers are research visualizations, not hydrological or engineering-grade models.
- Several raw PDFs and large GIS bundles are ignored to keep the repository reviewable; derived artifacts and source notes remain tracked.
- A few external endpoints are unstable or protected, so not every raw download can be re-fetched reliably.
