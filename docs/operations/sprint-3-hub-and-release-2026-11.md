# Sprint 3 Runbook — Release Polish, Open Data Hub & Interactive Discovery (Nov 2026)

**Objective:** Sprints 1–2 built 25+ structured registries, geocoded 102 substations, fixed the 12 km RPGCL map offset, wired 44 Explorer layers + 1,050 searchable facts, and generated 23 SVG charts. **Sprint 3 prepares `wiki-v1.3.0` for launch and transforms TransparentGov's user experience from an essay wiki into an effortless, browsable, downloadable Open Energy Infrastructure Hub:**
1. Clear pre-release polish (1 stale chart + pages nearing `review_due`).
2. Build an **Open Data Catalog** + upgrade the **Front Door (`start-here.md` & `wiki/index.md`)** so every vertical and dataset is 1 click away.
3. Add a **lazy-loaded Interactive Registry Explorer** inside `wiki/explorer/` (filter/sort/download substations, hydro specs, ERC tariffs, non-hydro DoED, and industrial anchors right in the browser!).
4. Launch the **Clean-Power, Industry & AI/Compute Siting Readiness** dataset + `nepal-digital-infrastructure` entity page (combining already-verified grid, tariff, and load-anchor data).
5. Build the **NEPSE Hydropower Performance** starter table and a **Quarterly Refresh Orchestrator** so the hub stays permanently current.

**Audience:** Autonomous Claude session running in `/Users/hi/projects/nepalEnergy` on branch `data/coverage-sprint-2026-11`.

---

## 0. Data Sprint Mode Rules (Follow Strictly!)

1. **Branch & Git Hygiene:** Stay on `data/coverage-sprint-2026-11`. **Never** merge to `main`, push to remote, or force-push — leave the branch spotless and release-ready for the owner to merge & tag `wiki-v1.3.0`.
2. **Environment:** Use `.venv/bin/python` (Python 3.13) and pass `PYTHON=.venv/bin/python` to `make`.
3. **Single Final Rebuild (Quota Saver!):**
   - Do **NOT** run `make wiki-index`, `make wiki-site`, `make dashboard-build`, or `build_wiki_vector_index.py` after every WP.
   - Run fast targeted tests (`validate_repo.py` or specific `unittest`/Node suites) per WP, and run the **single full rebuild + `make release-check` ONCE in Section 3**.
   - Cap parallel sub-agents at **2–3 max**, cherry-pick **only** source/CSV/script/page/test files, and remove any temporary worktrees before finishing.
4. **Two-Tier Grounding (`wiki/GOVERNANCE.md`):**
   - **Tier A (strict primary source):** MW, MVA, GWh, tariffs, revenue, profit, coordinates, delivery status — never guess or fabricate.
   - **Tier B (canonical lookup):** Nepal 77-district ↔ 7-province geography and BS ↔ AD conversions, tagged `canonical-lookup`.
   - Data pages remain observation-only; no manual `## Used By` in `sources/*`.
5. **Explorer & Test Guardrails (CRITICAL — verify before committing UI changes!):**
   - `tests/test_wiki_search_intents.js` asserts exact strings in `wiki/explorer/index.html` (`placeholder="Search this wiki…"`, `Search by project, topic, claim, or source—or browse a section below.`, `<details class="search-advanced"`, `const showAnswer = ...`, and forbids `Track a project|Understand a system problem|Compare options|Verify a claim`). **Do not break those assertions!**
   - `scripts/test_explorer_performance.py` asserts default startup map payload `< 2.2 MB`, `searchVisibleLimit = 9`, lazy vector boost, and stable `np-build` cache buster. **Any new interactive table data MUST be lazy-loaded only when the user opens the Tables view!**
   - Keep `wiki-fact-index.json` `< 250 KB` gzipped and bump `np-build` / asset `?v=` query strings in `wiki/explorer/index.html` when editing Explorer JS/CSS.
   - Register any new committed generated outputs in `docs/generated-assets.json`.
   - External network circuit breaker: max 2 attempts / 30s per URL; never burn quota retrying blocked portals.

---

## 1. Progress Tracker (Update at Wrap-Up)

| WP | Priority | Title | Status | Commit | Key Metric / Result |
|---|---|---|---|---|---|
| **WP 11A** | P0 | Pre-Release Polish: Refresh Stale Substation Chart & Review-Due Check | `DONE` | `fe3f8af` | 0 stale-figure warnings; 3 near-due pages reverified (HDDI energisation still unconfirmed as of 25 Nov web recheck) |
| **WP 12A** | P1 | Open Data Catalog (`scripts/build_dataset_catalog.py` + `data-open-data-catalog.md`) | `DONE` | `f3623a6` | 53 datasets cataloged (38 CSV + 15 GeoJSON incl. later WPs); `--check` in `make validate` |
| **WP 12B** | P1 | Upgrade Hub Front Door (`wiki/pages/syntheses/start-here.md` & `wiki/index.md`) | `DONE` | `269adc9` | 8-pillar registries table on start-here; Open Data & Map Lenses sections in index; 0 broken links |
| **WP 13A** | P2 | Lazy-Loaded Interactive Registry Tables View in Explorer (`wiki/explorer/`) | `DONE` | `1c30727` | 5 tabs / 6 tables, lazy fetch on open, startup payload unchanged; np-build → public-launch-16 |
| **WP 14A** | P3 | Clean-Power, Industry & AI/Compute Siting Readiness Layer + `nepal-digital-infrastructure` | `DONE` | `4db09a3` | 35 hubs (33 mapped), 0 scores; NDICL entity + institutions row 15 |
| **WP 15A** | P4 | NEPSE-Listed Hydropower Performance Starter Table (`data/nepse_hydro_performance.csv`) | `DONE` | `b2026ac` | Starter: 2 companies / 5 company-years (Tier A only); 15–20 target deferred |
| **WP 15B** | P4 | Quarterly Official-Registry Refresh Orchestrator (`scripts/refresh_official_registries.py`) | `DONE` | `1a2ada9` | dry-run/offline/fetch-official; `--offline` byte-stable; 6 unit tests |

---

## 2. Detailed Work Packages (Execute Strictly in Priority Order)

---

### PRIORITY 0 — Pre-Release Polish for `wiki-v1.3.0`

#### WP 11A — Refresh Stale Substation Figure & Clear Near-Due Review Dates
- **Why:** `validate_repo.py` currently emits one warning (`figure substation_province_capacity may be stale: data/substation_specs.csv content changed`) after `New Attariya` moved from Kailali to Kanchanpur, and `start-here.md` (and possibly other pages) has `review_due: 2026-11-29`.
- **Deliverables:**
  1. Run `.venv/bin/python scripts/build_wiki_figures.py` to regenerate `wiki/assets/figures/substation_province_capacity.svg` and update `wiki/explorer/shared/wiki-figure-manifest.json` so **0 stale-figure warnings** remain in `validate_repo.py`.
  2. Scan frontmatter across `wiki/pages/**/*.md` for any pages with `review_due <= 2026-12-15` (excluding `start-here.md`, which WP 12B updates). Verify each against its cited sources; if still accurate, bump `reviewed: 2026-11-25` and `review_due: 2027-02-25` (only after verifying!).
- **Done criteria:** Zero stale-figure warnings in `validate_repo.py`; zero pages past or within 14 days of `review_due`.
- **Suggested commit:** `Refresh stale substation province chart and verify near-due page reviews`

---

### PRIORITY 1 — Open Data Catalog & Hub Front Door *(Highest User-Facing Impact)*

#### WP 12A — Automated Open Data Catalog (`build_dataset_catalog.py` + `data-open-data-catalog.md`)
- **Why:** TransparentGov now maintains **25 structured CSVs** under `data/` plus key derived tables and GeoJSON layers, yet there is no single directory where journalists, researchers, ADB/WB consultants, or builders can browse and download every dataset with row counts, schemas, and freshness dates.
- **Deliverables:**
  1. Write **`scripts/build_dataset_catalog.py`** (with `--check` mode + unit test `tests/test_build_dataset_catalog.py` added to `Makefile` `test` target):
     - Scans curated CSVs in `data/*.csv`, key derived registries in `data/processed/tables/` (`doed_hydropower_registry.csv`, `doed_nonhydro_registry.csv`, `doed_project_status_overlay.csv`, `nea_energy_balance_monthly_fy2025_26.csv`, etc.), and key GeoJSON layers in `data/processed/maps/`.
     - Outputs **`data/processed/tables/dataset_catalog.json`** (register in `docs/generated-assets.json`!) containing for each dataset: `id`, `title`, `domain` (`hydropower`, `solar-nonhydro`, `grid-substations`, `markets-tariffs`, `institutions-finance`, `demand-fossil`, `hazards-climate`, `system-timeseries`), `path`, `format`, `rows`, `columns`, `schema_path`, `companion_page_slug`, `last_verified`, `license`, `summary`.
  2. Create **`wiki/pages/data/data-open-data-catalog.md`** (`page_quality: analysis`, observation-only) presenting clean domain-grouped Markdown tables of all datasets with row counts, freshness dates, companion wiki links, schema links, and direct relative file download links (`../../../data/...`), plus a short reuse/citation & provenance-boundary guide (Tier A vs. Tier B).
- **Done criteria:** `build_dataset_catalog.py --check` passes; every curated CSV in `data/` is cataloged with exact live row/column counts; unit test passes.
- **Suggested commit:** `Add automated Open Data Catalog generator, JSON manifest, and wiki catalog page`

#### WP 12B — Upgrade Hub Front Door (`start-here.md` & `wiki/index.md`)
- **Why:** `start-here.md` still reads primarily as a hydropower essay guide (dated `2026-08-29`, citing `nea-annual-report-fy2024-25`) and mentions none of the new infrastructure verticals, substations, tariffs, institutions, load anchors, hazards, or Open Data Catalog.
- **Deliverables:**
  1. Update **`wiki/pages/syntheses/start-here.md`** (`updated: 2026-11-25`, `reviewed: 2026-11-25`, `review_due: 2027-02-25`, `as_of: 2026-11-25`, add `nea-annual-report-fy2025-26` to `sources`):
     - Keep the clean existing 5-minute system-understanding spine and evidence-model explanation intact!
     - Add a crisp, scannable **"Infrastructure Registries & Open Data"** section right near the top linking all 8 pillars:
       - **Open Data Catalog:** [[data-open-data-catalog]] (25+ downloadable CSVs & GeoJSONs)
       - **Hydropower Fleet:** [[hydropower-system]], [[data-fleet-composition]], [[data-plant-annual-generation]]
       - **Grid, Substations & Corridors:** [[data-substation-inventory]] (153 substations), [[data-nea-grid-infrastructure-fy2025-26]], [[transmission-and-cross-border-trade]]
       - **Solar & Non-Hydro Renewables:** [[solar-system]], [[data-solar-fleet-inventory]], [[data-non-dam-storage-pipeline]]
       - **Tariffs, PPAs & Cross-Border Trade:** [[data-erc-retail-tariffs]], [[data-ppa-standard-rates]], [[data-cross-border-approved-plants]], [[data-nea-system-annual-timeseries]]
       - **Institutions & Developers:** [[data-energy-institutions]], [[data-major-developers]], [[erc]], [[doed]], [[nea]]
       - **Demand, EVs, Industry & Fossil Backbone:** [[data-load-anchors-and-fossil-backbone]], [[data-final-energy-mix]]
       - **Geohazards & Climate Resilience:** [[data-infrastructure-hazard-register]], [[bhotekoshi-trishuli-flood-2026]], [[glof-risk]]
  2. Update **`wiki/index.md`** to add an **Open Data & Infrastructure Registries** section and add the new `Full Energy Infrastructure` and `ICIMOD Dangerous Glacial Lakes` lenses under **Map Lenses**.
- **Done criteria:** Zero broken wikilinks; front-door pages reflect the full energy infrastructure hub while preserving editorial clarity and `assess_page_quality.py --check`.
- **Suggested commit:** `Upgrade start-here and wiki index to surface all energy infrastructure verticals and Open Data Catalog`

---

### PRIORITY 2 — Interactive Filterable Registry Tables Inside the Explorer *(Biggest UX Multiplier)*

#### WP 13A — Lazy-Loaded Interactive Data Tables View in `wiki/explorer/`
- **Why:** Users can search individual facts in Find or click points on the map, but they cannot yet **filter, sort, and compare** all 153 substations by province/voltage, 87 hydro plants by status/type/MW, 223 ERC tariffs by customer category/ToD band, 161 DoED non-hydro plants by technology, or 20 industrial anchors in one interactive table.
- **Architecture (lightweight, zero external dependencies, zero startup cost):**
  1. Create a small, clean standalone JS module **`wiki/explorer/shared/data-explorer.js`** (loaded via `<script src="shared/data-explorer.js?v=design-3" defer></script>` — fetches CSVs **only on demand** when the user opens a table, with in-memory caching!).
  2. Add a clean **"Data"** / **"Tables"** toggle button in the Explorer left-rail header or toolbar (alongside Find / Browse — **without removing or altering any Find placeholder/prompt strings checked by `tests/test_wiki_search_intents.js`!**) that renders an interactive, sortable, filterable table inside the center/reader pane with:
     - **Dataset selector tabs (5 core registries):**
       1. **Substations (153):** Filter by `Province`, `Voltage (400/220/132/66 kV)`, `Status`, text search; sort by `Installed MVA`, `Pipeline MVA`, `Solar Linked MW`; click mapped row to fly to substation on map!
       2. **Hydropower Specs (87):** Filter by `Status`, `Project Type`, text search; sort by `MW`, `Annual GWh`, `Dry Share %`, `Cost/MW`; click row to open wiki entity page!
       3. **ERC Retail Tariffs (223):** Filter by `Customer Category`, `Season`, `Time Band`, text search; sort by `Energy Rate (NPR/kWh)` & `Demand Charge`!
       4. **DoED Non-Hydro (161):** Filter by `Technology` (Solar/Wind/Thermal/Biomass/Cogen), `Regulatory Category`; sort by `MW`!
       5. **Load Anchors & Institutions:** Toggle between `Industrial Load Anchors (20)` (clicking `substation_slug` jumps to substation!) and `Core Institutions (14)` (clicking opens entity page!).
     - **Live summary strip** (filtered row count + total MW / MVA where applicable) + **"Download filtered CSV"** button (client-side Blob download) + **"Download full CSV"** direct link!
     - Respects both **light and dark themes** (`theme.css` CSS variables).
  3. Add a lightweight Node contract test **`tests/test_data_explorer.js`** (and add to `Makefile` `test` target) testing CSV parsing (quoted fields, commas, CRLF!), filtering/sorting logic, and verifying `data-explorer.js` does not eagerly fetch CSVs on initial page load.
  4. Bump `np-build` / cache-buster tokens in `wiki/explorer/index.html`.
- **Done criteria:** `test_explorer_performance.py`, `test_wiki_search_intents.js`, `test_lalupate_stage_one.js`, and new `test_data_explorer.js` ALL pass; zero startup payload increase; clean light/dark theme styling.
- **Suggested commit:** `Add lazy-loaded interactive Data Tables explorer for substations, hydro, tariffs, non-hydro, and load anchors`

---

### PRIORITY 3 — Clean-Power, Industry & AI/Compute Siting Readiness Layer

#### WP 14A — Grounded Clean-Industry & Compute Siting Dataset + `nepal-digital-infrastructure` Entity Page
- **Why:** Positions TransparentGov directly for the emerging wave of productive domestic electrification, industrial decarbonization, and cold-climate renewable AI/compute siting — using **strictly verifiable, already-collected grid, tariff, and institutional facts** (zero hype, zero invented scores!).
- **Deliverables:**
  1. Create entity page **`wiki/pages/entities/nepal-digital-infrastructure.md`** (`page_quality: record` or `brief`) grounded strictly in `data/raw/nea_annual_reports/nea_annual_report_2025_26.pdf` (Section 19, PDF p. 138 — NEA's 100% subsidiary covering Optical Fiber Sector and Data Centers & AI Decision Support) plus `sources/nea-annual-report-fy2025-26.md` — and add it to `data/energy_institutions.csv`.
  2. Write **`scripts/build_siting_readiness.py`** producing **`data/clean_industry_siting_index.csv`** and opt-in GeoJSON **`data/processed/maps/clean_industry_siting.geojson`** (register in `docs/generated-assets.json` + `layer-manifest.json`, OFF in default `overview`, ON in `energy_infrastructure` preset!).
     - Joins **existing verified datasets only** across Nepal's **~25–35 major candidate hubs** (all operating/under-construction **400 kV & 220 kV substations** + all **20 industrial estates/SEZs/corridors** from `industrial_load_anchors.csv` that link to a geocoded ≥132 kV substation):
       - Columns: `hub_id`, `hub_name`, `hub_type` (`400kv-grid-hub`, `220kv-grid-hub`, `sez`, `industrial-estate`, `industrial-corridor`), `substation_slug`, `highest_voltage_kv`, `installed_mva`, `planned_additional_mva`, `substation_status`, `province`, `district`, `latitude`, `longitude`, `coordinate_precision`, `industrial_tod_132kv_wet_offpeak_npr`, `industrial_tod_132kv_dry_peak_npr`, `linked_corridor_slugs`, `linked_solar_award_mw`, `climate_zone_band` (Terai / Mid-Hill / Valley / Mountain — canonical Nepal ecological belt by district), `verified_readiness_notes`, `missing_siting_data` (explicitly noting bay headroom, fiber route, feeder SAIDI/SAIFI), `source_basis`, `last_updated`.
  3. Create observation-only data page **`wiki/pages/data/data-clean-industry-and-compute-siting.md`** summarizing the verified grid/tariff/climate-zone siting baseline and explicitly listing what public data is still missing (optical fiber topology, substation bay headroom, hourly reliability).
- **Done criteria:** 100% of numbers programmatically derived from existing verified CSVs (`substation_specs.csv`, `industrial_load_anchors.csv`, `erc_retail_tariffs.csv`) with zero invented scores; `test_explorer_performance.py` and `validate_repo.py` pass.
- **Suggested commit:** `Add grounded clean-industry & compute siting index, map layer, and Nepal Digital Infrastructure entity page`

---

### PRIORITY 4 — NEPSE Hydropower Performance & Quarterly Refresh Automation

#### WP 15A — NEPSE-Listed Hydropower Actual Performance Starter (`data/nepse_hydro_performance.csv`)
- **Why:** NEA's Annual Report does not itemize actual annual GWh per IPP plant, leaving a major gap between design energy and delivered energy. Public disclosures from NEA subsidiaries and major NEPSE-listed hydropower companies fill this gap with real audited generation and revenue data.
- **Deliverables:**
  1. Create **`data/nepse_hydro_performance.csv`** covering **15–20 major listed/subsidiary hydropower companies** where verified figures exist on disk (`nea_annual_report_2025_26.pdf`, `data/raw/research/` PDFs, existing wiki entity pages like `upper-tamakoshi`, `sahas-urja`, `chilime`, `madhya-bhotekoshi`, `rasuwagadhi`, `sanjen`, `khimti-i`, `likhu-1`, `likhu-4`) and/or verified public financial reports / rating rationales (respecting the 2-attempt / 30s network circuit breaker!):
     - Columns: `company_slug`, `company_name`, `nepse_ticker`, `project_slug`, `installed_mw`, `fiscal_year_bs`, `fiscal_year_ad`, `contracted_or_design_gwh`, `actual_generation_gwh`, `delivery_vs_contract_pct`, `electricity_revenue_npr_m`, `net_profit_npr_m`, `total_debt_npr_m`, `source_slug`, `source_url`, `source_locator`, `confidence`, `verified_on`, `notes`.
  2. Create concise observation-only data page **`wiki/pages/data/data-nepse-hydro-performance.md`** summarizing actual-vs-contracted delivery and financial health across the tracked cohort, explicitly noting sample scope (not a sector-wide census yet).
- **Done criteria:** Every single number sourced with exact locator & fiscal year; zero guessed financial figures; `validate_repo.py` passes.
- **Suggested commit:** `Add verified NEPSE-listed hydropower generation and financial performance starter table`

#### WP 15B — One-Command Quarterly Refresh Orchestrator (`scripts/refresh_official_registries.py`)
- **Why:** Keeping 25+ registries current shouldn't require remembering 12 separate scripts.
- **Deliverables:**
  1. Write **`scripts/refresh_official_registries.py`** with `--dry-run` (default), `--offline` (runs only local deterministic enrichers/builders/reports), and `--fetch-official` (also runs DoED hydro + non-hydro scrapers with 30s timeouts):
     - Runs the canonical dependency order: DoED hydro/non-hydro scrapers (if `--fetch-official`) → DoED crosswalk/overlay → `enrich_solar_specs.py` → `enrich_canonical_geography.py` → `build_substation_specs_links.py` → `build_energy_infrastructure_layers.py` → `build_siting_readiness.py` → `build_dataset_catalog.py` → `report_spec_completeness.py` → `report_solar_spec_completeness.py`.
     - Prints a crisp before/after row-count & completeness diff summary.
  2. Add unit test **`tests/test_refresh_official_registries.py`** testing `--dry-run` plan ordering and step validation (and add to `Makefile` `test` target).
  3. Write concise operator guide **`docs/operations/quarterly-refresh-playbook.md`** documenting the quarterly 10-minute refresh checklist + `wiki-vX.Y.Z` release workflow.
- **Done criteria:** `.venv/bin/python scripts/refresh_official_registries.py --dry-run` and `--offline` succeed cleanly; unit test passes.
- **Suggested commit:** `Add quarterly official-registry refresh orchestrator, tests, and operator playbook`

---

## 3. Single End-of-Run Build, Release Gate & Morning Report (Run ONCE at the End!)

Whenever all WPs finish **or** <15% quota remains:
1. Stop starting new WPs immediately.
2. Update the exact page count in `wiki/index.md` to match `wiki/pages/`.
3. Run the **single** full rebuild and release gate:
   ```bash
   PYTHON=.venv/bin/python make wiki-index
   make wiki-site
   PYTHON=.venv/bin/python make dashboard-build
   PYTHON=.venv/bin/python make release-check
   ```
   Confirm **0 stale-figure warnings**, **0 trailing-whitespace diffs**, **0 over-declared pages**, and **100% passing Python + Node tests**.
4. Update the Progress Tracker table in this runbook, append **one concise sprint-level summary** to `wiki/WIKI_AUDIT_LOG.md`, and write **`docs/operations/sprint-3-report-2026-11.md`** (commits made, before/after scorecard, exact `wiki-v1.3.0` release commands ready for the owner to run, and any deferred items).
5. Commit (`Rebuild wiki indexes, static site, dashboard, and add Sprint 3 completion report`) and verify `git status` is completely clean and no temporary worktrees remain.
