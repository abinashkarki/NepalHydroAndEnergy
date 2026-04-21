# `data/raw/` — primary sources (not tracked in git)

This directory holds the primary source material the wiki is built on:
government and donor PDFs, national-scale shapefiles, and a few raw HTML
captures. Most of it is **deliberately excluded from git** (see
`.gitignore` at the repository root) to keep the repo lean — every file
excluded here is freely re-downloadable from its public source.

## What is ignored

| Path | Why excluded |
|------|--------------|
| `data/raw/**/*.pdf` | 77 official PDFs (~200 MB). Re-downloadable. |
| `data/raw/maps/hydrorivers/` | HydroSHEDS / HydroRIVERS v1.0 Asia shapefile bundle. |
| `data/raw/maps/hydrobasins/` | HydroBASINS shapefile bundle. |
| `data/raw/maps/nepal_osm_waterways/` | OSM waterways extract. |
| `data/raw/maps/*.zip` | Raw shapefile / OSM zip archives. |
| `data/raw/**/*.html` | Raw HTML captures (regenerate via scripts). |

## What is tracked

Small, non-regenerable artefacts that the pipelines depend on:

- `data/raw/core/nepal_boundary.geojson`
- `data/raw/maps/nepal_districts.geojson`
- `data/raw/maps/nepal_provinces.geojson`
- `data/raw/maps/river_network_review_overrides.json`
- `data/raw/projects_storage/naxa_hydropower_projects.geojson`
- `data/raw/projects_storage/hydro_naxa_datasets.csv`

## Inventories with source URLs

The authoritative list of ignored sources (with canonical URLs,
page counts, provenance notes and local paths) is kept under `data/processed/`:

- `data/processed/corridor_tracing/corridor_source_inventory.csv` — 77-row
  registry of every corridor-tracing PDF with its public URL.
- `wiki/pages/sources/*.md` — one wiki page per source, each carrying the
  public URL, author, date, and a SHA-256 of the locally-held copy.

## Rehydrating a fresh checkout

```
# PDFs (example)
mkdir -p data/raw/corridor_tracing/jica
curl -L -o data/raw/corridor_tracing/jica/jica_ipsdp_main_report_vol2.pdf \
  "<url from inventory>"

# Shapefiles: HydroSHEDS download page
#   https://www.hydrosheds.org/products/hydrorivers
#   https://www.hydrosheds.org/products/hydrobasins
```

Scripts that operate on these raw files will simply skip sources whose
local copy is missing, so a partial rehydration works fine.
