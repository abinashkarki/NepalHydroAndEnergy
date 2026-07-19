# V1 migration manifest

Created: 2026-07-19
Source snapshot: `/Users/hi/projects/nepalEnergy` working tree
Source HEAD: `ee6f4aea8ed4e7da935b63f5b4aeed97256a0139`
Standalone destination: `/Users/hi/projects/nepalEnergy-v1`

The source repository is not a Git ancestor of this workspace. The V1 folder was initialized as a new repository so its changes and checkpoints cannot alter the original project.

## Copied

| Path | Reason |
|---|---|
| `wiki/pages/` | Complete 401-page source knowledge graph; V1 adds 17 governed pages for a current total of 418. Retaining all source slugs avoids broken links and preserves evidence context. |
| `wiki/explorer/index.html`, `serve.sh`, `shared/`, `lib/` | Public explorer, reader, search, map controls and local runtime libraries. |
| `wiki/assets/images/`, `wiki/assets/figures/` | Images and maintainable figures referenced by current pages. |
| `wiki/assets/maps/layers/`, `wiki/assets/maps/previews/` | Small legacy layers and previews still referenced by data and basin pages. |
| Wiki governance, ontology, templates, schemas and audit records | Required for governed editing and validation. |
| `data/*.csv`, `data/*.yaml`, and schema JSON at the data root | Curated project, solar, claim, event, blocker, alias and authority inputs. |
| `data/processed/maps/` | Deployable GeoJSON required by the explorer; copied as runtime assets. |
| `data/processed/tables/` | Small derived tables used by pages, QA and completeness reports. |
| `data/winter_deficit_model/` | Transparent, compact inputs for the existing seasonal model. |
| `data/raw/projects_storage/naxa_hydropower_projects.geojson` | Compact upstream project registry input used by map tooling. |
| `data/raw/maps/nepal_provinces.geojson` and `river_network_review_overrides.json` | Compact map inputs not reconstructable from page content. |
| `data/processed/lead1/`, `data/processed/wecs_hydropower_potential_2019.txt` | Small inputs required by retained figure/validation checks. |
| `figures/hydropower_license_map.png` | Single retained legacy figure referenced by the public corpus. Other figure-development material was omitted. |
| Focused scripts and tests | Wiki indexes, search, validation, project/solar completeness, map builds, status overlays and runtime QA. |
| `docs/research_briefs/curtailment_dispatch_data_acquisition.md` | Governs the retired national curtailment estimate and unresolved evidence request. |

## Deliberately omitted

| Source path | Reason / recovery |
|---|---|
| `.git/` | 614 MB of unrelated source history; V1 uses independent history. |
| `.venv/`, `.pytest_cache/`, `__pycache__/` | Local environments and caches; regenerate locally. |
| `documentary/` | Separate 6.1 GB documentary production surface, outside the electricity-wiki V1. |
| `tmp/`, `output/`, `outputs/`, `test-results/`, `.playwright-cli/` | Temporary renders, screenshots, caches and local QA output. |
| `data/raw/core/`, `corridor_tracing/`, `lead1_sources/`, `hydrology/`, most `projects_storage/` | Bulky source PDFs and extraction inputs. Public source URLs and source pages remain; reacquire a primary document only when re-extraction is required. |
| Bulk `data/raw/maps/` HydroRIVERS, HydroBASINS and OSM shapefiles | Roughly 1.6 GB and reproducible or reacquirable. The explorer's deployable GeoJSON is included. `build_tributary_maps.py` can download HydroRIVERS and HydroBASINS; the OSM waterways source must be reacquired for a full river rebuild. |
| `data/processed/text/`, `page_renders/`, `corridor_tracing/`, dashboards | Regenerable extraction, review and internal-dashboard products not required by the public explorer. The standalone generated-asset manifest no longer claims ownership of the omitted dashboard output. |
| `wiki/explorer/screenshots*`, backups, 3D prototypes and debug utilities | QA and prototype artifacts, not public runtime dependencies. |
| `wiki/assets/maps/html/` | 44 MB of superseded standalone map exports; the integrated explorer and runtime GeoJSON are retained. |
| General `docs/`, `notes/`, `figures/`, `internal/`, `public/` | Documentary, portfolio, architecture, internal dashboard or deployment material outside the standalone V1. One referenced figure and the curtailment acquisition brief are explicit exceptions above. |
| PDF/image-atlas and vision-extraction scripts | They require omitted raw corpora and are not part of the routine wiki/index/data workflow. |

## Regeneration and setup

```bash
cd /Users/hi/projects/nepalEnergy-v1
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Optional semantic-vector rebuild
pip install -r requirements-search.txt

make wiki-index
make validate
make test
make serve
```

Open `http://127.0.0.1:8765/wiki/explorer/`.

`make wiki-index` preserves the shipped vector index when `sentence-transformers` is unavailable. Map GeoJSON already ships in `data/processed/maps/`; a full GIS rebuild additionally requires the omitted upstream HydroRIVERS, HydroBASINS and OSM inputs or reacquisition from their documented providers.

The copied source was an intentionally captured **dirty working-tree snapshot**, not a clean checkout. The source repository already had approximately 258 changed/untracked/deleted status entries before migration. All V1 writes and Git history are confined to this sibling folder.
