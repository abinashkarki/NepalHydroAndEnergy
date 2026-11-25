# Quarterly Official-Registry Refresh Playbook

A 10-minute checklist for keeping the wiki's registries current, followed by the
`wiki-vX.Y.Z` release workflow. Run it once a quarter, or after NEA publishes a new
annual report, ERC issues a tariff order, or DoED updates its licence registers.

## 0. Before you start

```bash
cd /Users/hi/projects/nepalEnergy
git switch main && git pull --ff-only origin main
git switch -c data/quarterly-refresh-$(date +%Y-%m)
source .venv/bin/activate        # Python 3.13; pip install -r requirements.txt
```

## 1. Preview the plan (dry run, no side effects)

```bash
python scripts/refresh_official_registries.py            # same as --dry-run
```

The plan runs in canonical dependency order:

| # | Step | Script | Mode |
|---:|---|---|---|
| 1 | DoED hydropower register scrape | `build_doed_hydropower_registry.py --timeout 30` | `--fetch-official` |
| 2 | DoED non-hydro register scrape | `build_doed_nonhydro_registry.py --timeout 30` | `--fetch-official` |
| 3 | DoED crosswalk / status overlay | `build_doed_project_status_overlay.py` | `--fetch-official` |
| 4 | Apply overlay to map points | `apply_doed_project_status_overlay.py` | `--fetch-official` |
| 5 | Solar spec enrichment | `enrich_solar_specs.py` | offline |
| 6 | Canonical district/province geography | `enrich_canonical_geography.py` | offline |
| 7 | Substation ↔ corridor/solar links | `build_substation_specs_links.py` | offline |
| 8 | Energy-infrastructure map layers | `build_energy_infrastructure_layers.py` | offline |
| 9 | Clean-industry siting index | `build_siting_readiness.py` | offline |
| 10 | Explorer Data Tables copies | `build_explorer_tables.py` | offline |
| 11 | Open Data Catalog | `build_dataset_catalog.py` | offline |
| 12 | Hydro spec completeness report | `report_spec_completeness.py --all` | offline |
| 13 | Solar spec completeness report | `report_solar_spec_completeness.py --all` | offline |

The DoED crosswalk steps run only with `--fetch-official`. Without a fresh scrape they would only re-serialise their outputs (new timestamp, line endings and indentation) and produce no new information.

## 2. Hand-curated updates (the part a script cannot do)

Check each primary source for a new edition. Update only rows whose figures you have read in that source, and record `source_slug`, `source_locator` (PDF page) and `verified_on` on each one.

- [ ] **NEA Annual Report** (August): `nea_system_annual_timeseries.csv`, `nea_grid_infrastructure_summary.csv`, `plant_annual_generation.csv`, `substation_specs.csv` (MVA, status), `cross_border_approved_plants.csv`, `nepse_hydro_performance.csv` (subsidiary sections)
- [ ] **ERC tariff orders**: `erc_retail_tariffs.csv`
- [ ] **NEA PPA rate notices**: `ppa_standard_rates.csv`
- [ ] **Company filings and rating rationales** (audited annual figures only, no unaudited quarterly aggregator numbers): `nepse_hydro_performance.csv`
- [ ] **Hazard events** since the last refresh: `infrastructure_hazard_events.csv`
- [ ] **Pages near `review_due`**: `grep -rn "^review_due:" wiki/pages | sort -t: -k3` — move a page's `reviewed` date only after reopening its sources.

Network etiquette: two attempts at most and a 30-second timeout per URL. Do not retry portals that block automated requests.

## 3. Run the refresh

```bash
python scripts/refresh_official_registries.py --offline          # local rebuild only
python scripts/refresh_official_registries.py --fetch-official   # also re-scrape DoED
```

The run stops at the first failing step. At the end it prints a before/after summary of row counts and cell fill rates for every registry. Review the result:

```bash
git status --short && git diff --stat
python scripts/validate_repo.py
```

## 4. Single full rebuild and release gate (once)

```bash
PYTHON=.venv/bin/python make wiki-index
make wiki-site
PYTHON=.venv/bin/python make dashboard-build
PYTHON=.venv/bin/python make release-check
```

Expect zero stale-figure warnings (run `make wiki-figures` first if a chart's source CSV changed) and all Python and Node tests green. Update the page count in `wiki/index.md` if pages were added, then commit.

## 5. Release `wiki-vX.Y.Z`

See [`docs/releasing-and-rollback.md`](../releasing-and-rollback.md) for the full procedure. In short:

```bash
# after the PR is reviewed and merged to main
git fetch origin main --tags && git switch main && git pull --ff-only origin main
PYTHON=.venv/bin/python make release-check
WIKI_RELEASE_COMMIT="$(git rev-parse origin/main)"
scripts/tag_wiki_release.sh X.Y.Z "$WIKI_RELEASE_COMMIT"          # preflight
scripts/tag_wiki_release.sh X.Y.Z "$WIKI_RELEASE_COMMIT" --push   # create + push tag
```

Then set `NEPAL_ENERGY_REF=$WIKI_RELEASE_COMMIT` in Coolify, run **Force deploy (without cache)**, run the production probe, and record the release in `release/production.json`.
