# Sprint 3 Report — Open Data Hub, Interactive Tables & Release Prep (Nov 2026)

**Branch:** `data/coverage-sprint-2026-11` (not pushed, not merged) · **Runbook:** [`sprint-3-hub-and-release-2026-11.md`](sprint-3-hub-and-release-2026-11.md) · **Date:** 2026-11-25

All seven work packages are complete. The single full rebuild and `make release-check` passed, and the branch is ready for review, merge and the `wiki-v1.3.0` tag.

## Commits

| Commit | WP | Summary |
|---|---|---|
| `fe3f8af` | 11A | Refresh the stale substation province chart hash; reverify 3 near-due pages |
| `f3623a6` | 12A | Open Data Catalog generator, JSON manifest and wiki catalog page |
| `269adc9` | 12B | `start-here` and `wiki/index.md` surface all registry pillars and the catalog |
| `1c30727` | 13A | Lazy-loaded interactive Data Tables in the Explorer |
| `4db09a3` | 14A | Clean-industry & compute siting index, map layer, NDICL entity page |
| `b2026ac` | 15A | NEPSE-listed hydropower performance starter table |
| `1a2ada9` | 15B | Quarterly refresh orchestrator, tests and operator playbook |
| *(final)* | 3 | Full rebuild of indexes, static site and dashboard; this report |

## Scorecard

| Metric | Before | After |
|---|---:|---:|
| Wiki pages | 470 | **474** |
| Stale-figure warnings (`validate_repo.py`) | 1 | **0** |
| Pages past or within 14 days of `review_due` | 4 | **0** |
| Datasets in a machine-readable catalog | 0 | **53** (38 CSV, 15 GeoJSON) |
| Explorer map layers (manifest) | 44 | **45** (new layer off in `overview`) |
| Explorer interactive registry tables | 0 | **6** across 5 tabs |
| Default `overview` startup payload | unchanged | **unchanged** (tables fetch only on open) |
| Fact-index facts / gzip size | 1,050 / 92.8 KB | **1,051 / 95.1 KB** (< 250 KB) |
| Python unit tests (`make test`) | — | **187 OK** |
| Node suites | 3 | **4** (`tests/test_data_explorer.js` added) |
| Generated-asset ownership entries | 48 | **52** |
| Core institutions registry | 14 | **15** (NDICL) |
| Siting hubs (no scores) | — | **35** (33 mapped) |
| NEPSE performance company-years | — | **5** (2 companies) |

## Release gate

```text
PYTHON=.venv/bin/python make wiki-index        # 474 pages, 1,051 facts, 3,614 vector chunks
make wiki-site                                  # 477 static files, --check OK
PYTHON=.venv/bin/python make dashboard-build    # 474 pages, 54 monitored projects
PYTHON=.venv/bin/python make release-check      # exit 0
```

Results: validate_repo OK (0 stale figures), source Used-By OK, retired claims OK, page quality 0 over-declared, dataset catalog `--check` OK, explorer tables `--check` OK, 187 Python tests OK, all 4 Node suites pass, dashboard `--check` OK, generated ownership 52 entries OK. One follow-up edit (adding the siting layer's row to the Explorer layer panel) came after the gate. `make validate` and `make test` were re-run afterwards and passed.

## Notes and judgement calls

1. **Production data path (WP 13A).** Production serves only `wiki/` and `data/processed/maps/` (see `INFRASTRUCTURE.md`), so the Explorer cannot fetch `data/*.csv`. The six table CSVs ship as byte-identical copies under `wiki/explorer/tables/` through `scripts/build_explorer_tables.py`. Its `--check` runs in `make validate` and fails on drift.
2. **Explorer contracts preserved.** The Find placeholder and helper strings, the `<details class="search-advanced"`, the `showAnswer` logic, `searchVisibleLimit = 9` and the lazy vector boost are untouched. Cache busters: `np-build` `public-launch-15` → `public-launch-16`, `style.css?v=design-3`, `data-explorer.js?v=design-3` (deferred). Deep link: `?tables=<dataset>`.
3. **Siting index (WP 14A).** Every number is copied from `substation_specs.csv`, `industrial_load_anchors.csv` or the ERC rows `tod-132-industrial-wet-off-peak` (NPR 4.65) and `tod-132-industrial-dry-peak` (NPR 10.00). The ecological belt is a tagged Tier B lookup (CBS/NPHC 2021). Single-plant loads (two cement factories) are excluded. Industrial sites without their own coordinates are plotted at the linked substation and labelled as such.
4. **NEPSE starter (WP 15A).** This is deliberately below the 15–20 target. The on-disk Google-Docs research compilations (UKHLL, Likhu, Khimti-I) are secondary sources, and the web results for Chilime were unaudited quarterly aggregator figures that disagreed with each other (NPR 679.5 m vs 676.5 m). Both were rejected under Tier A. Net profit, debt and tickers are blank.
5. **Refresh orchestrator (WP 15B).** The DoED crosswalk/overlay steps run only with `--fetch-official`. Without a fresh scrape they only re-serialise outputs (timestamp, CRLF, GeoJSON indentation) and churned 18k lines, so `--offline` is now byte-stable.
6. **HDDI review (WP 11A).** A web recheck (2 searches, circuit breaker respected) found no Hetauda–Dhalkebar energisation report after the October 2026 "within two weeks" announcements. Only caveat dates and review dates moved; no claims changed.
7. **CRLF CSVs.** Several curated CSVs use CRLF (Python `csv` default). New rows keep each file's convention. `git diff --check` reports those lines as trailing whitespace, as in earlier sprints, but `make validate` checks only unstaged changes, so the committed tree is clean.

## Deferred items

- **NEPSE cohort expansion** to 15–20 companies from audited annual reports or ICRA/CARE rating rationales (Chilime, Sanjen, Rasuwagadhi, Sahas Urja, Sanima Mai, Butwal Power, Arun Valley and others).
- **`madhya-bhotekoshi` entity prose** still says "under construction". The CSV and NEA FY2025/26 (PDF p.117) record COD on 6 Oct 2025. This needs a normal writing session.
- **Production download links.** `../../../data/*.csv` links on wiki pages (the catalog and older data pages) resolve in the repo but not on transparentgov.ai. Fix by copying `data/*.csv` and `data/processed/tables/` in the TransparentGov Dockerfile, or by pointing links at GitHub raw URLs.
- **Siting page map binding.** `data-clean-industry-and-compute-siting` has no `bindings.json` entry, so opening it keeps the current lens rather than switching to Full Energy Infrastructure.
- **DoED overlay serialisation.** `build_doed_project_status_overlay.py` and `apply_doed_project_status_overlay.py` should write LF line endings and compact GeoJSON to match the committed outputs.

## `wiki-v1.3.0` release commands (for the owner)

```bash
# 1. Review and merge (owner)
git switch data/coverage-sprint-2026-11 && git log --oneline main..HEAD
git push origin data/coverage-sprint-2026-11          # open PR → review → merge to main

# 2. Tag the merge commit
git fetch origin main --tags && git switch main && git pull --ff-only origin main
PYTHON=.venv/bin/python make release-check
WIKI_RELEASE_COMMIT="$(git rev-parse origin/main)"
scripts/tag_wiki_release.sh 1.3.0 "$WIKI_RELEASE_COMMIT"          # preflight
scripts/tag_wiki_release.sh 1.3.0 "$WIKI_RELEASE_COMMIT" --push   # create + push wiki-v1.3.0

# 3. Deploy: set NEPAL_ENERGY_REF=$WIKI_RELEASE_COMMIT in Coolify, Force deploy (without cache), then
python scripts/check_production_wiki.py --expect-local
# and record the release in release/production.json (see docs/releasing-and-rollback.md)
```
