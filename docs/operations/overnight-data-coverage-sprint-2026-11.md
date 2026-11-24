# Overnight Autonomous Data Coverage Sprint — Runbook (Nov 2026)

**Objective:** Shift Nepal Energy Wiki (TransparentGov) from analysis-heavy / thin-data toward a **complete, unified, schema-validated energy infrastructure data hub** — executing strictly in priority order as atomic, validated git commits so the run can stop cleanly at any point when quota expires and leave 100% shippable work.

**Audience:** Autonomous Claude session running overnight in `/Users/hi/projects/nepalEnergy`.

---

## 0. Autonomous Execution Protocol (Read First)

### 0.1 Environment & Git Hygiene
- **Create a dedicated working branch before editing anything:**
  ```bash
  git checkout -b data/coverage-sprint-2026-11
  ```
- **Never** push to remote, force-push, rebase, or touch `main` or `v2/design-system`.
- **Python & tools:** Use `.venv/bin/python` (Python 3.13 with `pypdf`). `pdftotext` is installed at `/opt/homebrew/bin/pdftotext`. Run Make targets with `PYTHON=.venv/bin/python`.
- **Work package loop (strictly one WP at a time):**
  1. Mark the WP `IN_PROGRESS` in the Progress Tracker below.
  2. Build the deliverables (scripts, CSVs, schemas, concise `record`-tier pages).
  3. Run the WP's targeted checks, then run the full gate:
     ```bash
     PYTHON=.venv/bin/python make wiki-index
     make wiki-site
     PYTHON=.venv/bin/python make validate
     PYTHON=.venv/bin/python make test
     ```
  4. Mark the WP `DONE` (with key metric counts) in the Progress Tracker and append a brief entry to `wiki/WIKI_AUDIT_LOG.md`.
  5. Create **one clean atomic commit** for that WP, then immediately move to the next WP without waiting for confirmation.

### 0.2 Pre-Authorized Governance Scope (Overnight Batch Clause)
The repo owner has **pre-authorized** this autonomous data-groundwork sprint on branch `data/coverage-sprint-2026-11`, overriding only the interactive 5-page limit and confirm gate in `wiki/GOVERNANCE.md`. **All epistemic invariants remain strictly binding:**
1. **Zero invented facts.** Every quantitative cell in every CSV must come from a primary source on disk (`data/raw/`, `data/processed/`) or a verified official web source with date + locator. If a value is unknown, leave it blank or `unknown` — never guess.
2. **Explicit provenance on every row.** Include `source_slug` or `source_url`, `source_locator` (page/table/section), and `last_updated` / `verified_on` (`2026-11-24` or `2026-11-25`).
3. **Observation-only data pages.** Data pages may report tables and bounded `> [!finding]` observations, never policy prescriptions or synthesis conclusions.
4. **No manual `## Used By` sections** in `wiki/pages/sources/*` (computed automatically from `wiki-backlinks.json`).
5. **No deleting or renaming existing slugs/pages** without logging in `wiki/FLAGGED_FOR_REVIEW.md`.
6. **Prioritize structured CSVs + scripts + `record`-tier pages over long prose.** Do not burn tokens writing multi-page essays.

### 0.3 Schema & Validator Gotchas (Save Yourself From Failures)
Check `scripts/validate_repo.py` before modifying existing schemas:
- **`data/project_specs.csv`** is validated strictly against `wiki/specs-schema.json` (`additionalProperties: false`).
  - Allowed `status`: `operating`, `under-construction`, `survey`, `pre-construction`, `stalled`, `cancelled`, `conceptual`.
  - Allowed `project_type`: `RoR`, `PROR`, `Peaking RoR`, `RoR With Pondage`, `Storage`, `Pumped-storage`, `Storage / Pumped-storage`, `Storage / Multipurpose`.
  - Allowed `turbine_type`: `Francis`, `Pelton`, `Kaplan`, `Crossflow`, `Francis (Toshiba)`.
  - Allowed `dam_type`: `RCC`, `Earthfill`, `Rockfill`, `Arch`, `Gravity`, `CFRD`, `Concrete-face Rockfill`, `Double-curvature Arch`, `Composite`.
  - Allowed `q_design`: `Q40`, `Q41`, `Q45`, `Q50`, `Q65`, `Q65+`.
  - Allowed `underground_powerhouse`: `yes`, `no`, `partial`.
  - **Orphan slug rule:** Every `slug` in `project_specs.csv` MUST have a matching `wiki/pages/entities/<slug>.md` file.
- **`data/solar_project_specs.csv`** is validated against `wiki/solar-specs-schema.json`.
  - Allowed `siting_archetype`: `substation-adjacent`, `hydro-co-location`, `floating-pv`, `rooftop-distributed`, `off-grid-minigrid`, `unknown`.
- **`data/corridor_specs.csv`** validates `status` against `delivery_values` in `wiki/monitoring-schema.json` / `validate_repo.py` — check exact allowed enum before writing.
- **`docs/generated-assets.json`** is checked by `scripts/check_generated_ownership.py`. If you create a new script that outputs generated files under `data/processed/`, register them in `docs/generated-assets.json`.
- **Internal dashboard check:** At the end of the sprint (or whenever inputs used by `build_internal_dashboard.py` change), run `PYTHON=.venv/bin/python make dashboard-build && PYTHON=.venv/bin/python make release-check`.

### 0.4 External Network Circuit Breaker
- Priorities **1, 2, 3A, and 4A** are **100% offline/local** using PDFs, GeoJSONs, and CSVs already on disk. Complete them first with zero network dependency.
- For tasks that touch external URLs (WP 3B optional verification, WP 4B, WP 5A–5C): cap any single HTTP/web lookup at **2 attempts / 30 seconds**. If a Nepali government portal (`.gov.np`) is down, slow, or gated by a CAPTCHA/anti-bot wall, **stop immediately**, record it under `BLOCKED / DEFERRED` in the tracker, and move to the next task. Never waste quota retrying flaky hosts.

---

## 1. Progress Tracker (Update After Every Commit)

| WP | Priority | Title | Mode | Status | Commit | Key Metric / Result |
|---|---|---|---|---|---|---|
| **WP 1A** | P1 | 10-Year NEA System Time-Series + FY 2025/26 Indicators Refresh | Local PDFs | `DONE` | `f87ecad` | 11 FYs (2072/73–2082/83) in nea_system_annual_timeseries.csv; indicators 23→45 rows incl. 9 provincial-office losses FY 2025/26 |
| **WP 1B** | P1 | Plant-by-Plant Annual Generation CSV + Refresh Stale FY 2076/77 Grid Tables | Local PDFs | `DONE` | `a1ebdcd` | plant_annual_generation.csv 44 rows (22 NEA/UT plants × FY 2024/25, 2025/26; NEA sums exact); IPP generation unallocated (not plant-itemised by NEA); grid summary 116 rows |
| **WP 2A** | P2 | Build `data/substation_specs.csv` + Schema + Data Page (400/220/132 kV) | Local PDFs + GeoJSON | `DONE` | (this commit) | substation_specs.csv 153 rows (400 kV 15, 220 kV 22, 132 kV 104, 66 kV 12; 94 operating / 29 UC / 29 planned / 1 partial); 28 grounded coordinates; 24 with linked solar awards; schema + validator + tests |
| **WP 2B** | P2 | Expand `data/corridor_specs.csv` (2 → 22+ Domestic & Cross-Border Corridors) | Local Dossiers + PDFs | `PENDING` | — | — |
| **WP 3A** | P3 | Expand `data/project_specs.csv` (25 → ~75–85 Real Operating & Pipeline Plants) | Local Repo + DoED + NEA | `PENDING` | — | — |
| **WP 3B** | P3 | Enrich `project_specs.csv` Core Fields + Reconcile 16 Missing Operating Plants + Clean 38 Stubs | Local + Selective Web | `PENDING` | — | — |
| **WP 4A** | P4 | Deterministic Solar V1 Enrichment (`province`, `resource_zone`, `siting_archetype`, est. GWh) | Local Script + GeoJSON | `PENDING` | — | — |
| **WP 4B** | P4 | DoED Non-Hydro Registry Scraper + Cross-Border Export Plants + BESS/PSH Registry | Web + Local | `PENDING` | — | — |
| **WP 5A** | P5 | Structured ERC Retail Tariffs & NEA Standard PPA Rates CSVs + Data Pages | Web + Local | `PENDING` | — | — |
| **WP 5B** | P5 | Core Energy Institutions (8 Missing Entity Pages + CSV) & Top Developers / NEPSE Registry | Local + Web | `PENDING` | — | — |
| **WP 5C** | P5 | Load Anchors & Full-Energy Foundations (EVs, Industrial/SEZ, AI Siting, NOC Fossil) | Web + Local | `PENDING` | — | — |

---

## 2. Detailed Work Packages (Execute Strictly in Order)

---

### PRIORITY 1 — Unlock NEA FY 2025/26 & Multi-Year System Data Already on Disk

> **Why Priority 1:** `nea_annual_report_2025_26.pdf` (9.8 MB) and `nea_annual_report_2024_2025.pdf` (5.6 MB) are already sitting in `data/raw/`, yet `electricity_system_indicators.csv` stops at FY 2024/25, there is no multi-year national electricity time-series CSV, no plant-by-plant annual generation CSV, and the substation/transmission data pages are 6 years stale (FY 2076/77). Note: commit `c68e0e6` already added `sources/nea-annual-report-fy2025-26.md` and updated headline prose in `state-of-the-system.md`; **do not redo that**. Focus strictly on structured CSV extraction and refreshing stale data tables.

#### WP 1A — 10-Year NEA System Time-Series + FY 2025/26 Indicators Refresh
- **Inputs on disk:**
  - `data/raw/nea_annual_reports/nea_annual_report_2025_26.pdf`
  - `data/raw/projects_storage/nea_annual_report_2024_2025.pdf`
  - `data/raw/core/nea_annual_report_2020.pdf`
  - `data/electricity_system_indicators.csv`
  - `data/processed/tables/nea_energy_balance_monthly_fy2025_26.csv`
- **Deliverables:**
  1. Write a reproducible extraction/validation script `scripts/extract_nea_annual_tables.py` (or clean helper) to dump and verify the multi-year summary tables from the NEA Annual Report PDFs.
  2. Create **`data/nea_system_annual_timeseries.csv`** covering at least **10 fiscal years** (e.g., FY 2072/73 through FY 2082/83 — whatever full multi-year span the NEA "At a Glance" / 10-year summary tables provide):
     - Columns: `fiscal_year_bs`, `fiscal_year_ad`, `installed_capacity_total_mw`, `installed_nea_mw`, `installed_ipp_mw`, `installed_solar_mw`, `peak_demand_national_mw`, `peak_demand_system_mw`, `energy_nea_gwh`, `energy_ipp_gwh`, `energy_import_gwh`, `energy_export_gwh`, `energy_total_available_gwh`, `energy_sales_gwh`, `system_loss_pct`, `consumers_total`, `electrification_pct`, `nea_revenue_npr_m`, `nea_net_profit_npr_m`, `source_slug`, `source_locator`, `verified_on`.
  3. Update **`data/electricity_system_indicators.csv`** by adding FY 2025/26 indicator rows alongside FY 2024/25 (preserve FY 2024/25 history; include FY 2025/26 provincial distribution office losses if published in the FY 2025/26 report).
  4. Create concise `data` page **`wiki/pages/data/data-nea-system-annual-timeseries.md`** (`page_quality: record` or `analysis`, observation-only, with summary table, caveats, and linked CSV) and refresh **`wiki/pages/data/data-electricity-system-indicators.md`**.
- **Done criteria:** Zero blank provenance fields; totals cross-checked against `nea_energy_balance_monthly_fy2025_26.csv` and `sources/nea-annual-report-fy2025-26.md`; full `make wiki-index && make wiki-site && make validate && make test` passes.
- **Suggested commit:** `Add 10-year NEA system time-series CSV and refresh FY 2025/26 indicators`

#### WP 1B — Plant-by-Plant Annual Generation CSV + Refresh Stale FY 2076/77 Grid Summary Tables
- **Inputs on disk:**
  - `data/raw/nea_annual_reports/nea_annual_report_2025_26.pdf`
  - `data/raw/projects_storage/nea_annual_report_2024_2025.pdf`
  - `data/raw/research/Urja Khabar “Audit” of IPP Generation vs. Contracted.pdf`
  - `wiki/pages/data/data-nea-substation-capacity-fy2076-77.md`
  - `wiki/pages/data/data-nea-transmission-length-fy2076-77.md`
- **Deliverables:**
  1. Create **`data/plant_annual_generation.csv`** extracting actual annual energy generation (GWh) by plant for **FY 2024/25 and FY 2025/26** from the NEA Annual Report appendices (all NEA-owned plants, NEA subsidiary plants like Upper Tamakoshi / Chilime / Rasuwagadhi / Sanjen / Madhya Bhotekoshi, and major IPP plants listed in the report):
     - Columns: `plant_name`, `project_slug` (blank if no wiki page yet), `ownership_class` (`nea`, `nea-subsidiary`, `ipp`, `solar`, `thermal`), `installed_capacity_mw`, `fiscal_year_ad`, `actual_generation_gwh`, `contracted_or_design_gwh`, `implied_plf_pct`, `source_slug`, `source_locator`, `verified_on`, `notes`.
  2. Create **`data/nea_grid_infrastructure_summary.csv`** with current FY 2024/25 & FY 2025/26 transmission circuit-km by voltage class (400/220/132/66/33 kV) and total substation transformer MVA by voltage ratio (compared against the FY 2076/77 baseline).
  3. Create concise observation-only data pages:
     - `wiki/pages/data/data-plant-annual-generation.md`
     - `wiki/pages/data/data-nea-grid-infrastructure-fy2025-26.md` (and add a clear cross-link note at the top of the historical FY 2076/77 pages pointing readers to the current FY 2025/26 page without deleting the historical records).
- **Done criteria:** Plant generation sums reconciled against NEA aggregate figures (with any unallocated IPP residual explicitly documented); full `make` validation suite passes.
- **Suggested commit:** `Extract plant-level annual generation CSV and FY 2025/26 grid capacity summary`

---

### PRIORITY 2 — Build the Grid Spine (`substation_specs.csv` + Complete `corridor_specs.csv`)

> **Why Priority 2:** Substations and transmission corridors are the physical backbone connecting generation (hydro + solar), domestic distribution, cross-border trade, EV fast-charging, industrial estates, and future AI/compute loads. Right now substations have **0 CSVs** and `corridor_specs.csv` has only **2 corridors (4 rows)** despite 22+ corridors already documented in dossiers and PDFs.

#### WP 2A — Build `data/substation_specs.csv` + Schema + Explorer Integration Check
- **Inputs on disk:**
  - `data/raw/nea_annual_reports/nea_annual_report_2025_26.pdf` (Transmission Directorate / Grid Operation appendices)
  - `data/raw/projects_storage/nea_annual_report_2024_2025.pdf`
  - `data/raw/corridor_tracing/nea/nea_transmission_annual_book_2077.pdf`
  - `data/processed/maps/transmission_network_nodes.geojson` (56 nodes)
  - `data/processed/maps/place_anchor_index.geojson`
  - `data/solar_project_specs.csv` (contains 63 awarded substation names!)
  - Existing substation pages in `wiki/pages/entities/`
- **Deliverables:**
  1. Create **`wiki/substation-specs-schema.json`** (JSON Schema matching repo conventions).
  2. Create **`data/substation_specs.csv`** covering all major **400 kV, 220 kV, and 132 kV** operating, under-construction, and formally planned grid substations in Nepal (target: **80–120+ substations**):
     - Columns: `slug`, `substation_name`, `highest_voltage_kv`, `voltage_ratios`, `installed_mva`, `planned_additional_mva`, `status` (`operating`, `under-construction`, `planned`, `partially-operational`), `status_as_of`, `province`, `district`, `latitude`, `longitude`, `coordinate_precision`, `owner`, `corridor_slugs`, `cross_border_link`, `linked_solar_award_mw`, `commissioned_year`, `source_slug`, `source_locator`, `confidence`, `last_updated`, `notes`.
     - Populate `linked_solar_award_mw` programmatically from `data/solar_project_specs.csv` where substation names match!
  3. Add lightweight schema validation for `data/substation_specs.csv` in `scripts/validate_repo.py` (checking required fields, unique slugs, valid `status` enum, valid numeric ranges) + unit test.
  4. Create **`wiki/pages/data/data-substation-inventory.md`** (`page_quality: record` or `analysis`, observation-only) summarizing substation counts and MVA by voltage class, status, and province.
- **Done criteria:** All 400 kV and 220 kV substations and all major 132 kV substations from NEA FY 2025/26 included; coordinates only populated where grounded in `transmission_network_nodes.geojson` / `place_anchor_index.geojson` / verified source (never fabricated); `make` validation + tests pass.
- **Suggested commit:** `Add structured substation_specs.csv backbone, schema, validator, and inventory page`

#### WP 2B — Expand `data/corridor_specs.csv` (2 → 22+ Domestic & Cross-Border Corridors)
- **Inputs on disk:**
  - `data/corridor_specs.csv` (currently 4 rows / 2 corridors)
  - `data/processed/maps/transmission_corridor_dossiers.csv` (12 domestic corridors)
  - `data/processed/maps/cross_border_interconnection_dossiers.csv` (10 cross-border links)
  - `wiki/pages/entities/` (all 16 `transmission-corridor` + 6 `cross-border` manual pages)
  - `data/raw/nea_annual_reports/nea_annual_report_2025_26.pdf`
  - `data/raw/corridor_tracing/moewri/moewri_ipsdp_exec_summary_2025.pdf`
- **Deliverables:**
  1. Expand **`data/corridor_specs.csv`** from 2 corridors → **all 22+ major domestic corridors & cross-border interconnections** (preserving existing columns so nothing breaks in `validate_repo.py` or `build_wiki_fact_index.py`; check `validate_repo.py` before adding any new column!).
  2. Fill `length_km`, `voltage_kv`, `status`, `status_as_of`, `owner`, `financing`, `dependency`, `source_url`, `source_title`, `confidence` for every corridor segment from the dossiers, entity pages, and NEA FY 2025/26 report.
  3. Ensure every corridor `slug` links cleanly to its corresponding wiki entity page (verify no broken links or invalid `status` enums).
- **Done criteria:** At least **20 distinct corridors / 30+ segments** in `data/corridor_specs.csv`, zero `validate_repo.py` warnings/errors, `wiki-fact-index.json` rebuilt cleanly.
- **Suggested commit:** `Expand corridor_specs.csv to cover all 22+ domestic and cross-border corridors`

---

### PRIORITY 3 — Re-Center & Triple `data/project_specs.csv` on the Real Operating & Active Fleet

> **Why Priority 3:** `data/project_specs.csv` currently has only **25 rows** (only **6 operating = 844 MW / 21.6%** of operating hydro, and **0 rich**), while facts for dozens of real operating & building projects already exist in `wiki/pages/entities/`, `doed_hydropower_registry.csv`, `nea_annual_report_2025_26.pdf`, and `data/raw/research/`.

#### WP 3A — Expand `data/project_specs.csv` from 25 → ~75–85 Real Operating & Active Pipeline Projects
- **Inputs on disk:**
  - `data/project_specs.csv` (25 rows)
  - `data/processed/tables/doed_hydropower_registry.csv` (213 operating, 288 generation licences)
  - `data/processed/tables/doed_project_status_overlay.csv`
  - `data/processed/tables/doed_operating_projects_missing_local.csv` (16 missing operating plants)
  - `wiki/pages/entities/*.md` (all 37 `specs-refresh`, 80 `manual`, 70 `auto-stub` pages — harvest facts already written in prose!)
  - `data/raw/nea_annual_reports/nea_annual_report_2025_26.pdf`
  - `data/raw/research/` PDFs (`Khimti-I`, `Likhu Hydropower Cascade`, `UKHLL`, `Urja Khabar`)
- **Selection rule (deterministic & clear):**
  1. **All operating hydropower plants ≥ 20 MW** in Nepal (~55 plants = ~2,925 MW = **75% of operating hydro**), starting with every one that already has an entity page (Rasuwagadhi 111, Madhya Bhotekoshi 102, Lower Solu 82, Sanjen Khola 78, Likhu-1 77, Middle Tamor 73, Madhya Marsyangdi 70, Marsyangdi 69, Upper Trishuli 3A 60, Khimti-I 60, Likhu-2 55, Super Dordi Kha 54, Likhu-4 52.4, Likhu Khola A 51, Upper Marsyangdi A 50, Mewa Khola 50, Upper Bhotekoshi 45, Super Madi 44, Sanjen 42.5, etc.), **plus** creating clean `record`-tier entity pages for high-capacity operating plants lacking a page (e.g., **Nilgiri Khola-II 71 MW**, **Upper Rahughat 48.5 MW**, **Mathillo Thulo Khola A 22.5 MW**).
  2. **Top ~20–25 active generation-licence / verified under-construction projects ≥ 50 MW** that already have entity pages or are flagship pipeline assets (Upper Arun 1,063, Betan Karnali 439, Upper Tamor 285, Upper Trishuli-1 216, Chainpur Seti 210, Super Tamor 166, Lapche Khola 160, Tamakoshi V, Upper Trishuli 3B, Khimti-II, Rahughat, Jagdulla, etc.).
- **Deliverables:**
  1. Expand **`data/project_specs.csv`** from 25 rows → **75–85 rows**, strictly obeying `wiki/specs-schema.json` enums and ensuring every slug has a matching `wiki/pages/entities/<slug>.md`.
  2. Populate every verifiable field from local sources first (`capacity_mw`, `river`, `status`, `project_type`, `developer`, `cod_year`, `annual_design_energy_gwh`, `dry_season_energy_gwh`, `dry_share_pct`, `gross_head_m`, `design_discharge_m3s`, `num_units`, `unit_capacity_mw`, `turbine_type`, `total_cost_usd_m`, `cost_per_mw_usd_m`, `ppa_rate_wet_npr_kwh`, `ppa_rate_dry_npr_kwh`, `lead_financier`, `concession_type`, `source_note`, `last_updated`).
  3. Run `PYTHON=.venv/bin/python scripts/gen_wiki_stubs.py --write --refresh-specs`, `PYTHON=.venv/bin/python scripts/report_spec_completeness.py --all`, and `PYTHON=.venv/bin/python scripts/build_tributary_maps.py` so map popups and auto-stubs immediately reflect the expanded specs!
- **Done criteria:** `project_specs.csv` has ≥ 70 projects covering ≥ 65% of Nepal's operating hydro MW; `spec_completeness_report.md` regenerated; zero schema/orphan errors in `validate_repo.py`; full `make` validation & test suite passes.
- **Suggested commit:** `Expand project_specs.csv from 25 to 75+ real operating and pipeline hydro projects`

#### WP 3B — Enrich Existing 25 Spec Rows + Clean Legacy Stub & Missing-Operating Debt
- **Deliverables:**
  1. Deepen the original 25 projects in `data/project_specs.csv` (which currently have **0 rich, 8 moderate, 17 thin**) using `data/raw/lead1_sources/jica_storage_master_plan_vol_1.pdf`, `vol_2.pdf`, `wecs_hydropower_potential_2019.pdf`, `nea_annual_report_2025_26.pdf`, and existing flagship entity prose (`upper-tamakoshi.md`, `arun-3.md`, `tanahu-hydropower.md`, `dudhkoshi-storage.md`, `budhigandaki.md`, `kali-gandaki-a.md`, `kulekhani-cascade.md`, etc.) to move at least **10–15 flagship projects into `rich` completeness**.
  2. **Clean up the 38 legacy `auto-stub` entity pages** containing the deprecated phrase `under construction (generation licence)` (see `docs/doed-hydropower-registry-crosswalk.md` line 88):
     - Cross-check each of the 38 against `doed_project_status_overlay.csv`:
       - If DoED shows `operating_record`, update status wording cleanly with DoED COD citation.
       - If DoED shows `generation_license` with no separate document-verified construction source, replace the deprecated phrase with the governed wording `holds a DoED generation licence (physical construction progress not independently verified)`.
       - Do NOT claim verified construction without a project-specific source!
  3. **Review the 16 missing operating DoED projects** (`data/processed/tables/doed_operating_projects_missing_local.csv`): check whether any are aliases of existing local points (if so, add reviewed entries to `data/project_identity_aliases.csv` with explicit evidence note) and ensure the top missing operating plants (≥ 10 MW) are clearly surfaced.
  4. Regenerate `spec_completeness_report.md`, maps, and indexes.
- **Done criteria:** 0 remaining occurrences of deprecated `under construction (generation licence)` in `auto-stub` pages; ≥ 10 projects at `rich` completeness; full `make` validation + tests pass.
- **Suggested commit:** `Deepen flagship hydro specs and clear legacy auto-stub wording debt`

---

### PRIORITY 4 — Close Solar V1 Gaps + Build Non-Hydro, Cross-Border Export & Non-Dam Storage Registries

> **Why Priority 4:** High-leverage automation that turns 0%-filled axes into 100% structured coverage and opens the remaining generation/flexibility registries cleanly.

#### WP 4A — Deterministic Solar V1 Enrichment (`province`, `resource_zone`, `siting_archetype`, Modelled GWh)
- **Inputs on disk:**
  - `data/solar_project_specs.csv` (88 rows, already 100% lat/lon & district!)
  - `data/raw/maps/nepal_provinces.geojson`
  - `data/raw/maps/nepal_districts.geojson`
  - `data/processed/maps/solar_ghi_zones.geojson`
  - `wiki/solar-specs-schema.json`
  - `scripts/report_solar_spec_completeness.py`
- **Deliverables:**
  1. Write **`scripts/enrich_solar_specs.py`** (deterministic, idempotent, zero external API calls):
     - Spatial point-in-polygon join (or verified district → province lookup table checked against `nepal_provinces.geojson`) to populate **`province`** for **88/88 (100%)** rows.
     - Spatial join against `solar_ghi_zones.geojson` to populate **`resource_zone`** for **88/88 (100%)** rows.
     - Set **`siting_archetype`** = `substation-adjacent` for the 63 NEA 960 MW substation-linked tender awards (where `substation` is populated and `procurement_stage` confirms substation-adjacent tender), and populate unambiguous operating plants (`hydro-co-location` / `substation-adjacent` where verified, otherwise `unknown`).
     - Populate **`expected_annual_generation_gwh`** ONLY IF `wiki/solar-specs-schema.json` permits an explicit modelled estimate basis (check `expected_generation_basis` enum in `wiki/solar-specs-schema.json` first! If the schema forbids modelled estimates in `expected_annual_generation_gwh`, do NOT hack the schema — instead document the exact empirical/tariff-bid generation figures where published, or leave `expected_annual_generation_gwh` strictly for reported values and add a separate derived table `data/processed/tables/solar_modeled_yield_estimates.csv`).
  2. Run `PYTHON=.venv/bin/python scripts/report_solar_spec_completeness.py` and rebuild maps/indexes.
  3. Add a unit test verifying `enrich_solar_specs.py` produces 100% valid provinces and schema compliance.
- **Done criteria:** `province` and `resource_zone` jump from **0% → 100%** (88/88); `solar-specs-schema.json` passes 100% strictly; `solar_spec_completeness_report.md` updated.
- **Suggested commit:** `Enrich solar_project_specs.csv with province, resource zone, and siting archetypes`

#### WP 4B — Official Non-Hydro Registry + Cross-Border Approved Export Plants + BESS/Pumped-Hydro Registry
- **Inputs:** Official DoED web pages (with 2-attempt / 30s circuit breaker!), existing wiki sources (`india-energy-relationship`, `bangladesh-trade-route`, `storage-and-flexibility`), `nea_annual_report_2025_26.pdf`.
- **Deliverables:**
  1. **`scripts/build_doed_nonhydro_registry.py`** (mirroring `build_doed_hydropower_registry.py`): fetch DoED's official solar, wind, thermal, and biomass/cogeneration licence & operating plant tables into `data/processed/tables/doed_nonhydro_registry.csv` + summary JSON (with SHA-256 hashes & source timestamps). *If DoED is unreachable, write the parser + unit tests against cached/local HTML fixtures or skip gracefully and log under `BLOCKED`.*
  2. **`data/cross_border_approved_plants.csv`**: structured ledger of all Nepal hydropower plants approved by India's CEA / Designated Authority for cross-border export (IEX / bilateral / Bangladesh trilateral), grounded in `nea_annual_report_2025_26.pdf` and official NEA/CEA records:
     - Columns: `project_name`, `project_slug`, `installed_mw`, `approved_export_mw`, `market_channel` (`iex-dam`, `iex-rtm`, `bilateral-india`, `trilateral-bangladesh`), `approval_status`, `valid_until`, `promoter_country_note`, `source_slug`, `source_locator`, `verified_on`.
  3. **`data/storage_non_dam_specs.csv`**: structured registry of **grid-scale Battery Energy Storage Systems (BESS)** and **Pumped Storage Hydropower (PSH)** projects/studies in Nepal (e.g., NEA/ADB/WB BESS pilots/tenders, Begnas–Rupa PSH, Syarpu, Kulekhani PSH, etc. — strictly verified entries only, with explicit `status` distinguishing `operating`, `tendered`, `feasibility-study`, `proposed`):
     - Columns: `slug`, `project_name`, `technology` (`bess`, `pumped-hydro`), `power_mw`, `energy_mwh`, `duration_hours`, `substation_or_site`, `province`, `status`, `developer_or_agency`, `financier`, `source_url`, `source_title`, `confidence`, `last_updated`, `notes`.
  4. Concise observation-only data pages: `wiki/pages/data/data-cross-border-approved-plants.md` and `wiki/pages/data/data-non-dam-storage-pipeline.md`.
- **Done criteria:** Every row sourced with explicit date and confidence; zero speculative/unverified MW totals; full `make` validation & tests pass.
- **Suggested commit:** `Add non-hydro DoED registry, CEA export-approved plants, and BESS/PSH registries`

---

### PRIORITY 5 — Launch the "Full Energy Infrastructure Hub" Foundations (Market, Institutions & Load Anchors)

> **Why Priority 5:** Only execute after Priorities 1–4 are committed and passing. These three lightweight, schema-first WPs lay the clean foundation for transforming TransparentGov from a hydro/solar wiki into **Nepal's complete energy infrastructure & future-load hub**.

#### WP 5A — Structured Tariffs & PPA Schedules (`erc_retail_tariffs.csv` + `ppa_standard_rates.csv`)
- **Deliverables:**
  1. **`data/erc_retail_tariffs.csv`**: Current official ERC-approved NEA retail electricity tariff schedule (domestic ampere/kWh slabs, industrial 11/33/66/132 kV including Time-of-Day wet/dry peak/normal/off-peak rates, commercial, irrigation, EV charging station rates, water supply):
     - Columns: `tariff_id`, `effective_from`, `customer_category`, `voltage_or_ampere_tier`, `season` (`all`, `wet`, `dry`), `time_band` (`flat`, `peak`, `normal`, `off-peak`), `slab_kwh_range`, `demand_charge_npr_kva`, `energy_rate_npr_kwh`, `minimum_charge_npr`, `source_url`, `source_title`, `verified_on`.
  2. **`data/ppa_standard_rates.csv`**: Official NEA/ERC posted PPA tariff rates & rules by technology (`RoR`, `PRoR-1-2hr`, `PRoR-2-4hr`, `PRoR-4-6hr`, `Storage`, `Solar-ceiling`, `Wind`, `Biomass`), wet/dry NPR/kWh, escalation %, tenure, take-or-pay/take-and-pay status, effective date, source.
  3. Concise observation-only data pages: `wiki/pages/data/data-erc-retail-tariffs.md` and `wiki/pages/data/data-ppa-standard-rates.md`.
- **Done criteria:** Every tariff figure verified against an official ERC tariff order or NEA annual report (do NOT guess outdated slabs); full `make` validation & tests pass.
- **Suggested commit:** `Add structured ERC retail tariff and NEA standard PPA rate tables`

#### WP 5B — Core Energy Institutions (8 Missing Entities) & Top Developers / NEPSE Registry
- **Deliverables:**
  1. **`data/energy_institutions.csv`** covering Nepal's ~12–15 core energy institutions (`nea`, `erc`, `doed`, `moewri`, `wecs`, `aepc`, `rpgcl`, `hidcl`, `vucil`, `ibn`, `ippan`, `noc`, `sebon`, `dhm`), with mandate, statutory act, parent ministry, official website, key public datasets published.
  2. Create concise **`record`/`brief` entity pages** for the **8 missing core institutions** (`erc.md`, `doed.md`, `moewri.md`, `rpgcl.md`, `hidcl.md`, `ibn.md`, `ippan.md`, `noc.md`), following `wiki/GOVERNANCE.md` entity template (`Summary`, `Key Facts`, `Role in Nepal's Energy System`, `Key Datasets & Disclosures`, `Sources`) — keeping them crisp (200–400 words each, factual, zero fluff).
  3. **`data/major_developers_nepse.csv`**: Top 30 hydropower/energy developers & NEPSE-listed hydro companies synthesized from `doed_hydropower_registry.csv` promoter counts + NEA annual report / public disclosures (columns: `developer_slug`, `developer_name`, `entity_type`, `nepse_ticker`, `operating_mw_approx`, `pipeline_mw_approx`, `flagship_project_slugs`, `source_basis`, `last_updated`).
- **Done criteria:** Zero duplicate slugs vs. `wiki-page-index.json`; all links valid; full `make` validation & tests pass.
- **Suggested commit:** `Add core energy institutions registry, 8 missing institution pages, and top developers CSV`

#### WP 5C — Load Anchors & Full-Energy Foundations (EVs, Industrial/SEZ, AI-Compute Siting, NOC Fossil Context)
- **Deliverables (lightweight, high-clarity starter tables — strictly sourced, no speculation):**
  1. **`data/industrial_load_anchors.csv`**: Nepal's major industrial estates (Balaju, Patan, Hetauda, Pokhara, Butwal, Dharan, Nepalgunj, Bhaktapur, Birendranagar, Gajendranarayan), Special Economic Zones (Bhairahawa SEZ, Simara SEZ), and major heavy-industry corridors (Birgunj–Pathlaiya, Sunsari–Morang, Rupandehi–Nawalparasi cement/steel belt) linked to their nearest `substation_slug` (from WP 2A!), province, district, voltage supply, and known power-reliability/feeder notes.
  2. **`data/ev_adoption_and_charging.csv`**: Verified annual EV import statistics (Nepal Department of Customs / economic survey where available) + NEA/major highway DC fast-charging hub inventory (city/highway, district, nearest `substation_slug`, charger count/kW, source).
  3. **`data/fossil_infrastructure.csv`**: Major petroleum & LPG import backbone assets (Motihari–Amlekhgunj pipeline, Amlekhgunj–Lothar & Siliguri–Jhapa planned extensions, major NOC fuel storage depots — Amlekhgunj, Thankot, Biratnagar, Bhairahawa, Pokhara, Nepalgunj, Dhangadhi, Sinamangal ATF — plus capacity in KL & days of stock where officially published).
  4. One concise umbrella data page **`wiki/pages/data/data-load-anchors-and-fossil-backbone.md`** linking the three tables and noting explicit evidence gaps (including what data is needed next for AI/data-center siting: fiber routes, substation bay headroom, and hourly feeder load).
- **Done criteria:** Strictly sourced, explicit `unknown` where official numbers aren't public, zero unverified claims, full `make` validation & tests pass.
- **Suggested commit:** `Add starter registries for industrial load anchors, EV charging, and NOC fossil infrastructure`

---

## 3. End-of-Run Wrap-Up (Run Before Stopping — Even If Quota Runs Low!)

Whenever all WPs finish **or** you estimate <15% quota remains:
1. Stop starting new WPs immediately.
2. Run the full release gate:
   ```bash
   PYTHON=.venv/bin/python make dashboard-build
   PYTHON=.venv/bin/python make release-check
   ```
   Fix any broken links, missing manifest entries in `docs/generated-assets.json`, or test failures.
3. Write a concise morning briefing at **`docs/operations/overnight-sprint-report-2026-11.md`** containing:
   - Exact list of commits made on `data/coverage-sprint-2026-11`
   - Before vs. After scorecard (rows in `project_specs.csv`, `substation_specs.csv`, `corridor_specs.csv`, solar completeness %, new CSVs, new pages)
   - Any items deferred/blocked (with exact reason and next command to resume)
   - Clean `git status` confirmation (`nothing to commit, working tree clean`).
4. Commit the report (`Add overnight data coverage sprint morning report`) and stop cleanly.
