---
title: Data Pipeline Readme
type: data
created: 2026-04-15
updated: 2026-05-13
figure_type: table
sources: [nea-annual-report-fy2024-25]
tags: [scripts, pipeline, regeneration, data, maps]
page_quality: analysis
---

# Data Pipeline Readme

## Summary

This data page documents the copied data-build scripts, the processed products they generate, what dependencies are present in the merged workspace, and which regeneration paths still require fuller raw inputs.

Reference page for the copied scripts and the data products they generate. The scripts now live in the merged workspace under `scripts/`, but not all raw dependencies were copied over.

## Script Inventory

| Script | Purpose | Main inputs | Main outputs |
|--------|---------|-------------|--------------|
| [build_wiki_figures.py](../../../scripts/build_wiki_figures.py) | Published wiki figures and figure manifest | processed tables, curated legacy figures | `wiki/assets/figures/`, `wiki/explorer/shared/wiki-figure-manifest.json` |
| [build_research_figures.py](../../../scripts/build_research_figures.py) | Legacy static research figures | processed project table, Nepal boundary | files in `figures/` |
| [build_tributary_maps.py](../../../scripts/build_tributary_maps.py) | Tributary/basin HTML maps and GeoJSON layers | raw waterways, HydroBASINS, project geodata | `data/processed/maps/`, `wiki/assets/maps/html/` |
| [build_lead1_trade_outputs.py](../../../scripts/build_lead1_trade_outputs.py) | Lead-1 monthly trade panels | monthly trade and NEA balance CSVs | `data/processed/lead1_trade/`, `figures/lead1_*.png` |
| [build_nea_daily_trade_series.py](../../../scripts/build_nea_daily_trade_series.py) | NEA daily-report crawl and parse pipeline | NEA archive pages + cached PDFs | `data/processed/lead1_trade/` manifest, parsed CSVs, summary JSON |

## What Is Present In This Merged Workspace

- Processed tables and lead-1 outputs under `data/processed/`
- Published wiki figures under `wiki/assets/figures/`
- Legacy research figures under `figures/`
- Interactive HTML maps and preview PNGs under `wiki/assets/maps/`
- The copied scripts themselves under `scripts/`

## Coverage / Method

The inventory is based on the scripts checked into `scripts/`, the processed outputs under `data/processed/`, the figure directory, and the copied map assets under `wiki/assets/maps/`. It distinguishes scripts that are close to runnable from scripts that still depend on raw source libraries or fuller geospatial inputs not present in this workspace.

## Caveats

This page is a regeneration guide for the merged workspace, not a guarantee that every pipeline can be fully rerun from checked-in files alone.

## What Is Not Fully Present

- The original raw PDF source library from the code repo was **not** copied wholesale.
- The full raw geospatial stack used to regenerate the maps was **not** copied wholesale.
- The checked-in NEA daily parsed dataset here is only a **40-report subset**, even though archive coverage has been scanned much deeper.

That means:

- `build_lead1_trade_outputs.py` is the closest to immediately runnable.
- `build_research_figures.py` is partly runnable from merged processed data.
- `build_tributary_maps.py` and `build_nea_daily_trade_series.py` still expect a fuller raw-input environment for full regeneration.

## Regeneration Commands

Run from the workspace root:

```bash
python scripts/build_lead1_trade_outputs.py
python scripts/build_wiki_figures.py
python scripts/build_research_figures.py
python scripts/build_tributary_maps.py
python scripts/build_nea_daily_trade_series.py --max-pages 4 --max-reports 40 --refresh
```

For daily-trade work, the last command should be treated as a pipeline entry point, not as proof of full historical completeness. The archive-depth note in [[data-trade-time-series]] remains the authoritative caveat.

## Related

- [[data-trade-time-series]]
- [[data-map-inventory]]
- [[data-storage-comparison]]
- [[unresolved-questions]]
