# Data Coverage Sprint Report — November 2026

**Branch:** `data/coverage-sprint-2026-11` (ready for review / PR into `v2/design-system` or `main`)  
**Completion:** **11 / 11 Work Packages (`WP 1A` through `WP 5C`) DONE** + Governance v2 streamline + Full release gate passing.

---

## 1. Before vs. After Coverage Scorecard

| Dimension | Before Sprint | After Sprint | Delta / Key Milestone |
|---|---:|---:|---|
| **Total Wiki Pages** | 429 | **462** | +33 pages (10 operating hydro, 8 core institutions, 11 data pages, 4 sources) |
| **Hydropower `project_specs.csv`** | 25 projects (6 operating / 844 MW / 21.6%) | **87 projects** (**53 operating / 2,828 MW / 72.3%**, 13 UC / 2,419 MW) | +62 projects; **0 → 2 rich**, **8 → 24 moderate** (+127 verified cells in WP 3B) |
| **Grid Substations `substation_specs.csv`** | 0 rows (stale FY 2076/77 markdown table) | **153 substations** (15×400 kV, 22×220 kV, 104×132 kV, 12×66 kV) | 15,541 MVA in service + 18,389 MVA pipeline; **149/153 district & province**; 24 linked to 590 MW solar awards; JSON schema + validator + tests |
| **Transmission `corridor_specs.csv`** | 2 corridors / 4 segments | **23 corridors / 40 segments** | 16 domestic + 6 cross-border + 1 other; 36/40 with verified lengths |
| **Solar `solar_project_specs.csv`** | 88 rows (0% province, 0% resource zone, 0% siting) | **88 rows** (**88/88 province**, **78/88 resource zone**, **67/88 siting archetype**) | 91.1% overall cell fill + deterministic `scripts/enrich_solar_specs.py` |
| **Non-Hydro DoED Registry** | None | **161 rows** (`doed_nonhydro_registry.csv`) | Live scrape of 25 official DoED solar/wind/thermal/biomass/cogen pages |
| **NEA System & Generation Time-Series** | Single-year FY 2024/25 indicators (23 rows) | **11-FY annual time series** (2072/73–2082/83) + **46 indicators** + **44 plant-generation rows** + **116 grid-summary rows** | Replaces 6-year-stale FY 2076/77 grid capacity tables with FY 2025/26 |
| **Tariffs, PPAs & Cross-Border / Non-Dam Storage** | 0 CSVs | **223 ERC retail tariff rows** + **25 NEA PPA rate rows** + **10 CEA export rows** (1,200 MW) + **10 BESS/PSH rows** | Complete structured market & flexibility backbone |
| **Institutions & Developers** | 3 institution pages (`nea`, `wecs`, `aepc`) | **14 institutions** (`energy_institutions.csv` + **8 new pages**: `erc`, `doed`, `moewri`, `rpgcl`, `hidcl`, `ibn`, `ippan`, `noc`) + **30 major developers/NEPSE** | Closes the institutional reference blind spot |
| **Load Anchors, EVs & Fossil Backbone** | 0 CSVs (1 mention of EVs, 1 of NOC) | **20 industrial/SEZ anchors** (100% linked to `substation_slug`) + **24 EV rows** (incl. Customs HS-code imports) + **20 NOC pipeline/depot rows** | First-class demand-side & energy-substitution backbone |
| **Legacy Stub Debt** | 38 auto-stubs with deprecated wording | **0 remaining** | Cleared cleanly |
| **Fact Index / Dashboard** | 666 facts / 25 monitored coverage rows | **692 facts** / **87 coverage rows**, **31 monitored projects**, **93 sources** | Full end-to-end validation green |

---

## 2. Commit Log on `data/coverage-sprint-2026-11`

- `b93d83b` — Add overnight data coverage sprint runbook
- `f87ecad` — WP 1A: 10-year NEA system time-series CSV + FY 2025/26 indicators
- `a1ebdcd` — WP 1B: Plant-level annual generation CSV + FY 2025/26 grid capacity summary
- `f2eb508` — WP 2A: Structured `substation_specs.csv` backbone (153 rows), schema, validator, and tests
- `f2ac057` — WP 2B: Expand `corridor_specs.csv` to 23 corridors / 40 segments
- `2173cfb` — WP 3A: Expand `project_specs.csv` from 25 → 87 real operating & pipeline hydro projects
- `4fb2070` — WP 4A + 4B: Deterministic solar enrichment, live DoED non-hydro registry (161 rows), CEA export & BESS/PSH registries
- `9a38fe9` — WP 5A–5C: ERC retail tariffs, NEA standard PPA rates, 8 missing institutions + developers, industrial/EV/NOC registries
- `1848e57` — Backfill canonical Nepal geography (149/153 substations) & 100% `substation_slug` links in `industrial_load_anchors.csv`
- `e9c9432` — WP 3B: Enrich 29 flagship & JICA storage rows in `project_specs.csv` (+127 cells) and rebuild maps/stubs
- `df64740` — Streamline `wiki/GOVERNANCE.md` with Two-Tier Grounding Rule and Data Sprint Mode
- *(final commit)* — Rebuilt `wiki-index`, `wiki-site`, `control-room.json`, updated vector-index test budget (1.4 → 1.8 MB for 462 pages), and sprint report

---

## 3. Validation & Verification Gate Results

- `scripts/validate_repo.py`: **PASS** (462 wiki pages, 87 hydro specs, 88 solar specs, 153 substations, 0 schema/orphan errors)
- `scripts/check_source_used_by.py`: **PASS** (93 source pages clean)
- `scripts/check_retired_claims.py`: **PASS** (3 rules clear)
- `scripts/assess_page_quality.py --check`: **PASS** (0 over-declared pages)
- `make test`: **PASS** (145 Python unit tests + 3 Node regression suites)
- `make dashboard-check`: **PASS** (13 dashboard unit tests + runtime contract)
- `scripts/check_generated_ownership.py`: **PASS** (38 generated asset entries valid)

---

## 4. Follow-Up Items / Next High-Value Moves

1. **Map & Explorer UI Surfacing:** The new CSVs (`substation_specs.csv`, `industrial_load_anchors.csv`, `fossil_infrastructure.csv`, `ev_adoption_and_charging.csv`, `storage_non_dam_specs.csv`, `erc_retail_tariffs.csv`) are all validated and documented in the wiki; the next high-ROI UI step is wiring `substation_specs.csv` (geocoding the remaining 125/153 substations cleanly) and `industrial_load_anchors.csv` into explorer map layers and `wiki-fact-index.json`.
2. **Per-Plant CEA Cross-Border Export Table:** `data/cross_border_approved_plants.csv` currently holds NEA channel-level FY 2024/25 & FY 2025/26 totals (1,200.01 MW across 37 plants) because CEA's cross-border page and approval-letter PDF returned HTTP 404; ingesting the per-plant CEA approval list when reachable will complete plant-level export tracking.
3. **Temporary Claude Worktrees:** Five `.claude/worktrees/agent-*` directories from the parallel overnight run remain untouched on disk; once you confirm you no longer need them, clean them up with `git worktree remove` + `git branch -D worktree-agent-*`.
4. **Vector Index Budget Note:** `scripts/test_wiki_search_index.py` was bumped from `1_400_000` → `1_800_000` bytes (current compressed size: 1,466,118 bytes at 462 pages).
