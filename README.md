# Nepal Energy Research Workspace

This repository is a working research workspace for a deep analysis of Nepal's rivers, hydropower system, storage gap, grid constraints, trade pattern, and regional geopolitics.

It is not a polished software package and it is not the final publishing format. Think of it as a research bed: source collection, derived tables, maps, charts, and working reports that can later feed a sharper written piece, deck, or video essay.

## What This Repo Contains

There are three main output layers in the project:

1. Working reports and analysis documents
2. Interactive maps and supporting geospatial layers
3. Derived tables, figures, and scripts that regenerate parts of the analysis

The two main narrative documents are:

- [Question-wise analysis](/Users/hi/projects/nepalEnergy/docs/nepal_energy_questionwise_analysis.md)
- [Narrative report](/Users/hi/projects/nepalEnergy/docs/nepal_energy_hydropower_report.md)

The main mapping entry points are:

- [Nepal Tributary Explorer](/Users/hi/projects/nepalEnergy/docs/maps/nepal_tributary_explorer.html)
- [Nepal Tributary Network](/Users/hi/projects/nepalEnergy/docs/maps/nepal_tributary_network.html)
- [Nepal River Geopolitics Explorer](/Users/hi/projects/nepalEnergy/docs/maps/nepal_geopolitics_river_influence.html)
- [Nepal Power System Explorer](/Users/hi/projects/nepalEnergy/docs/maps/nepal_power_system_explorer.html)
- [Maps README](/Users/hi/projects/nepalEnergy/docs/maps/README.md)

The main lead-1 seasonality/storage/trade brief is:

- [Lead 01 research brief](/Users/hi/projects/nepalEnergy/docs/research_briefs/lead_01_seasonality_storage_trade.md)
- [Lead 01 progress update](/Users/hi/projects/nepalEnergy/docs/research_briefs/lead_01_progress_update.md)

## What Has Been Done

### 1. Core research documents

Two major written outputs already exist:

- [docs/nepal_energy_questionwise_analysis.md](/Users/hi/projects/nepalEnergy/docs/nepal_energy_questionwise_analysis.md): answers the research frame domain by domain
- [docs/nepal_energy_hydropower_report.md](/Users/hi/projects/nepalEnergy/docs/nepal_energy_hydropower_report.md): a cleaner narrative report written from scratch

### 2. Map system for rivers, borders, basins, and hydropower

The repo includes a working interactive map stack covering:

- Nepal tributaries relevant to hydropower
- Nepal-origin downstream systems crossing into India
- northern Gangetic comparison rivers
- Nepal-linked and India-origin comparison basin polygons
- seasonal impact overlays
- hydropower project layers and labels
- first-pass route-faithful traced transmission corridors extracted from an official geospatial power-network PDF

Key derived map layers live in [data/processed/maps](/Users/hi/projects/nepalEnergy/data/processed/maps), and the browser-facing HTML maps live in [docs/maps](/Users/hi/projects/nepalEnergy/docs/maps).

### 3. Lead 1: seasonality, storage, and trade

This lead has moved beyond framing and now includes:

- a basin seasonality baseline table
- a storage-project dry-energy shortlist
- an NEA daily trade scraping/parsing pipeline
- a reshaped monthly trade series from the NEA annual report
- first-pass charts linking wet-season exports, dry-season imports, and weak storage

Important files:

- [Basin seasonality baseline](/Users/hi/projects/nepalEnergy/data/processed/tables/nepal_basin_seasonality_baseline.csv)
- [Storage dry-energy shortlist](/Users/hi/projects/nepalEnergy/data/processed/tables/nepal_storage_dry_energy_shortlist.csv)
- [NEA trade chart monthly series](/Users/hi/projects/nepalEnergy/data/processed/lead1_trade/nea_trade_chart_monthly_long.csv)
- [FY 2081/82 trade vs storage panel table](/Users/hi/projects/nepalEnergy/data/processed/lead1_trade/lead1_monthly_import_export_storage_fy2081_82.csv)
- [Daily archive coverage summary](/Users/hi/projects/nepalEnergy/data/processed/lead1_trade/nea_daily_archive_coverage.json)

Related charts:

- [Three-year monthly trade shape](/Users/hi/projects/nepalEnergy/figures/lead1_monthly_trade_3year.png)
- [FY 2081/82 trade vs storage](/Users/hi/projects/nepalEnergy/figures/lead1_fy2081_82_trade_vs_storage.png)

## Repo Layout

### `docs/`

Human-readable outputs and research writeups.

- [docs/nepal_energy_questionwise_analysis.md](/Users/hi/projects/nepalEnergy/docs/nepal_energy_questionwise_analysis.md)
- [docs/nepal_energy_hydropower_report.md](/Users/hi/projects/nepalEnergy/docs/nepal_energy_hydropower_report.md)
- [docs/maps](/Users/hi/projects/nepalEnergy/docs/maps)
- [docs/research_briefs](/Users/hi/projects/nepalEnergy/docs/research_briefs)

### `data/raw/`

Source documents and downloaded raw inputs.

Main subfolders:

- [data/raw/core](/Users/hi/projects/nepalEnergy/data/raw/core): core reports and base references
- [data/raw/hydrology](/Users/hi/projects/nepalEnergy/data/raw/hydrology): water-plan source material
- [data/raw/projects_storage](/Users/hi/projects/nepalEnergy/data/raw/projects_storage): hydropower and storage project source files
- [data/raw/maps](/Users/hi/projects/nepalEnergy/data/raw/maps): OSM and HydroBASINS geospatial inputs
- [data/raw/lead1_sources](/Users/hi/projects/nepalEnergy/data/raw/lead1_sources): lead-1-specific PDFs and daily report cache

### `data/processed/`

Derived machine-readable outputs.

Main subfolders:

- [data/processed/tables](/Users/hi/projects/nepalEnergy/data/processed/tables): extracted research tables
- [data/processed/maps](/Users/hi/projects/nepalEnergy/data/processed/maps): GeoJSON layers and map-side metadata
- [data/processed/lead1_trade](/Users/hi/projects/nepalEnergy/data/processed/lead1_trade): daily trade outputs, lead-1 monthly series, archive coverage
- [data/processed/text](/Users/hi/projects/nepalEnergy/data/processed/text): PDF-to-text extractions used for inspection

### `figures/`

Static chart outputs used in the reports and briefs.

Examples:

- [storage_gap.png](/Users/hi/projects/nepalEnergy/figures/storage_gap.png)
- [electricity_trade_shift.png](/Users/hi/projects/nepalEnergy/figures/electricity_trade_shift.png)
- [hydropower_license_map.png](/Users/hi/projects/nepalEnergy/figures/hydropower_license_map.png)

### `notes/`

Working research notes organized by topic.

- [01_hydrology_basins.md](/Users/hi/projects/nepalEnergy/notes/01_hydrology_basins.md)
- [02_projects_storage.md](/Users/hi/projects/nepalEnergy/notes/02_projects_storage.md)
- [03_grid_economics.md](/Users/hi/projects/nepalEnergy/notes/03_grid_economics.md)
- [04_geopolitics_climate.md](/Users/hi/projects/nepalEnergy/notes/04_geopolitics_climate.md)
- [05_mcp_mapping_assessment.md](/Users/hi/projects/nepalEnergy/notes/05_mcp_mapping_assessment.md)

### `scripts/`

Regeneration scripts for maps, charts, and trade datasets.

- [build_tributary_maps.py](/Users/hi/projects/nepalEnergy/scripts/build_tributary_maps.py)
- [extract_rpgcl_transmission_vectors.py](/Users/hi/projects/nepalEnergy/scripts/extract_rpgcl_transmission_vectors.py)
- [build_research_figures.py](/Users/hi/projects/nepalEnergy/scripts/build_research_figures.py)
- [build_nea_daily_trade_series.py](/Users/hi/projects/nepalEnergy/scripts/build_nea_daily_trade_series.py)
- [build_lead1_trade_outputs.py](/Users/hi/projects/nepalEnergy/scripts/build_lead1_trade_outputs.py)

## Best Entry Points

If you are opening this repo fresh, start in this order:

1. [README.md](/Users/hi/projects/nepalEnergy/README.md)
2. [docs/nepal_energy_hydropower_report.md](/Users/hi/projects/nepalEnergy/docs/nepal_energy_hydropower_report.md)
3. [docs/nepal_energy_questionwise_analysis.md](/Users/hi/projects/nepalEnergy/docs/nepal_energy_questionwise_analysis.md)
4. [docs/maps/README.md](/Users/hi/projects/nepalEnergy/docs/maps/README.md)
5. [docs/research_briefs/lead_01_progress_update.md](/Users/hi/projects/nepalEnergy/docs/research_briefs/lead_01_progress_update.md)

If you want the data side first, start here:

1. [data/processed/tables](/Users/hi/projects/nepalEnergy/data/processed/tables)
2. [data/processed/lead1_trade](/Users/hi/projects/nepalEnergy/data/processed/lead1_trade)
3. [data/processed/maps](/Users/hi/projects/nepalEnergy/data/processed/maps)

## How To Use The Repo

### Read the research

Open the markdown files in `docs/` and `notes/`.

### Use the maps

Open the HTML files in [docs/maps](/Users/hi/projects/nepalEnergy/docs/maps) in a browser. The explorer maps are interactive and include layer toggles. Use the tributary explorer for hydrology-first reading, the geopolitics explorer for basin/control questions, and the power-system explorer when transmission and interconnections should be the default visual subject.

### Inspect the data

Use the CSV and GeoJSON files under [data/processed](/Users/hi/projects/nepalEnergy/data/processed). These are the most reusable outputs for later analysis, visuals, or scripting.

### Regenerate outputs

Run the scripts from the repo root:

```bash
cd /Users/hi/projects/nepalEnergy
python scripts/build_research_figures.py
python scripts/extract_rpgcl_transmission_vectors.py
python scripts/build_tributary_maps.py
python scripts/build_lead1_trade_outputs.py
python scripts/build_nea_daily_trade_series.py --max-pages 4 --max-reports 40 --refresh
```

For a deeper NEA daily backfill:

```bash
cd /Users/hi/projects/nepalEnergy
python scripts/build_nea_daily_trade_series.py --max-pages 64 --sleep-seconds 0.03
```

That last command is network-heavy and slow. It is useful, but not cheap in time.

## Environment And Dependencies

The workspace currently uses a local virtual environment at [/.venv](/Users/hi/projects/nepalEnergy/.venv).

The scripts rely on standard Python plus a small GIS/plotting stack. From the current code, the important libraries are:

- `requests`
- `matplotlib`
- `folium`
- `shapely`
- `pypdf`
- `pymupdf`
- `pyshp` (`shapefile`)

The NEA daily parser also requires the `pdftotext` command-line tool to be installed and available on the shell path.

## Important Caveats

### 1. This repo is a research workspace, not a production package

There is no packaging, no test suite, and no clean reproducibility contract yet. Outputs are useful, but the repo is still optimized for research momentum.

### 2. Several scripts use absolute paths

Some scripts hardcode:

- `/Users/hi/projects/nepalEnergy`

If the repo moves, those scripts will need to be updated before they run cleanly.

### 3. Some source systems are unstable or blocked

The NEA daily operational archive is usable.

The NEA monthly operational PDFs appear to exist, but direct fetches from this environment have been blocked by the NEA site security layer. Because of that:

- the daily archive currently provides operational coverage from `2080-01-01` to `2081-09-27`
- the older part of FY `2079/80` still relies on the NEA annual report monthly comparison chart rather than a fully parsed monthly operational-report series

### 4. Official NEA totals are not perfectly internally consistent

The project preserves this instead of smoothing it over. For FY `2024/25`, NEA trade totals differ across:

- the annual report narrative
- the monthly energy-balance table
- the trade comparison chart

Use each source for the job it is best at, not as if all three are identical.

### 5. The maps are strong, but not perfect

The map stack is useful for cross-border interpretation and hydropower geography, but some exact named river linework was missing from the OSM extract and is explicitly flagged in the fetch reports rather than invented.

### 6. Some outputs are partial by design

The lead-1 daily trade build is real and working, but the full-archive parse was not completed into a final publication-grade daily series in this workspace yet. Current outputs are enough to support the argument, but not the end-state dataset.

## What Not To Assume

- Do not assume every number in the repo is a single-source “final truth.” Some are extracted from different official tables that disagree.
- Do not assume the interactive maps are authoritative hydrological models. They are research visualizations.
- Do not assume the repo is location-independent. Some scripts are written against this machine and directory layout.
- Do not assume all raw downloads can be re-fetched reliably. A few external endpoints are unstable or protected.
- Do not assume the current reports are publication-ready. They are strong working documents, not final editorial output.

## Suggested Next Steps

The strongest next research paths already identified are:

1. Finish lead 1 by extending the daily trade series and tightening the monthly reconciliation
2. Move to lead 2: hydropower geography versus bottlenecks
3. Move to lead 3: Nepal's geopolitical leverage by basin

If the immediate goal is editorial or video development, the best next step is to convert the current research stack into:

- a tighter thesis memo
- a chapter outline
- a stronger designed visual deck

## Quick Reference

If you only need the most important files:

- [Narrative report](/Users/hi/projects/nepalEnergy/docs/nepal_energy_hydropower_report.md)
- [Question-wise analysis](/Users/hi/projects/nepalEnergy/docs/nepal_energy_questionwise_analysis.md)
- [Map index](/Users/hi/projects/nepalEnergy/docs/maps/README.md)
- [Lead 01 progress update](/Users/hi/projects/nepalEnergy/docs/research_briefs/lead_01_progress_update.md)
- [Processed tables](/Users/hi/projects/nepalEnergy/data/processed/tables)
- [Lead 01 trade outputs](/Users/hi/projects/nepalEnergy/data/processed/lead1_trade)
- [Figures](/Users/hi/projects/nepalEnergy/figures)
