# Overnight Sprint 2 — Activation, Geocoding, Deepening & Visuals Runbook (Nov 2026)

**Objective:** Sprint 1 (`WP 1A–5C`, landed on `data/coverage-sprint-2026-11`) built 13 new structured registries and expanded hydro specs from 25 → 87 projects. **Sprint 2 makes that entire backbone visible, searchable, visual, and deep:**
1. Wire the new infrastructure registries into the **live Explorer map, structured Find (`wiki-fact-index.json`), and a new Grid & Full-Energy preset** (including geocoding high-voltage substations).
2. Deepen the **54 thin operating & under-construction hydro plants** in `data/project_specs.csv` (using ICRA/CARE credit ratings, company disclosures, and NEA/research PDFs).
3. Close every **"Still Open" gap from Sprint 1** (per-plant India CEA export approvals, ERC tariff `effective_from` dates, last 10 solar `resource_zone` rows, spot-check canonical geography).
4. Generate **publication-grade charts (`build_wiki_figures.py`)** from Sprint 1's new datasets.
5. Expand **multi-year geohazard tracking** and **live project events/blockers**.

**Audience:** Autonomous Claude session running overnight in `/Users/hi/projects/nepalEnergy`.

---

## 0. Modern-Model Data Sprint Protocol (Read First — Follow Strictly!)

This sprint operates under the new **Data Sprint Mode** and **Two-Tier Grounding Rule** now codified in `wiki/GOVERNANCE.md`:

### 0.1 Branch, Parallelism & Quota Efficiency
- **Working branch:** Continue directly on `data/coverage-sprint-2026-11` (or branch `data/coverage-sprint-2-2026-11` off it — never touch `main` or `v2/design-system`, never push to remote).
- **Python & tools:** Use `.venv/bin/python` (Python 3.13, `pypdf`) and `/opt/homebrew/bin/pdftotext`. Always pass `PYTHON=.venv/bin/python` to `make`.
- **CRITICAL — Quota & Merge-Conflict Saver (DO NOT IGNORE!):**
  - **Do NOT run `make wiki-index`, `make wiki-site`, `make dashboard-build`, or `build_wiki_vector_index.py` after every WP!** Running 10 full rebuilds across parallel worktrees was the #1 token sink in Sprint 1.
  - Instead, run **fast targeted checks** after each WP (`scripts/validate_repo.py` or specific `unittest` modules) and run the full `make wiki-index && make wiki-site && make dashboard-build && make release-check` **EXACTLY ONCE at the end of the sprint (Section 3)**.
  - **Cap parallel sub-agents at 2–3 max** (not 5 simultaneously), and keep dependent tasks sequential (e.g., WP 6A substation geocoding MUST finish before WP 6B map-layer/fact-index wiring!).
  - If using sub-agent worktrees, cherry-pick **only** source/CSV/script/page/test/GeoJSON files — **never** merge generated `wiki/site/`, `wiki/explorer/shared/*`, or `wiki/WIKI_AUDIT_LOG.md` blobs.
  - **External network circuit breaker:** Max 2 attempts / 30s per external URL. If a portal returns 403/404/timeout or CAPTCHA, log it and immediately try an alternate public source (e.g., ICRA Nepal / CARE Nepal / NEA press release / verified news) or move on.

### 0.2 Two-Tier Grounding Rules (Strict on Numbers, Practical on Geography)
- **Tier A — Measured, Financial & Delivery Facts (strict primary source required):** MW, MVA, GWh, costs, tariffs, PPA rates, CODs, construction progress, physical coordinates, and regulatory-vs-delivery distinctions (`generation_license` ≠ `under-construction`). Never invent or guess.
- **Tier B — Canonical Reference Lookups (deterministic lookup permitted):** Unambiguous Nepal administrative geography (77 districts ↔ 7 provinces) and standard BS ↔ AD fiscal year conversions — tagged `canonical-geography` / `canonical-lookup` in `notes`.
- **Observation-only data pages:** No policy prescriptions or synthesis conclusions on `data/*` pages. No manual `## Used By` sections on `sources/*` pages.

### 0.3 Key Contract & Test Gotchas (Save Yourself From Failures)
- **Explorer startup payload budget (`scripts/test_explorer_performance.py`):** Default preset (`overview`) startup GeoJSON total MUST stay `< 2,200,000` bytes! Keep all new Sprint 2 map layers **off** in the default `overview` preset and turn them **on** in the new `energy_infrastructure` (or `power_system`) preset.
- **Fact index schema & budget (`scripts/test_wiki_search_index.py`):**
  - Compressed `wiki-fact-index.json` MUST stay `< 250,000` bytes (gzip level 9).
  - Every fact dict MUST include all 10 required keys: `id`, `domain`, `facets`, `name`, `capacity_mw`, `status`, `source_layer`, `sources`, `feature_ref` (must contain `"layer"`), `related_slugs`.
  - Keep `test_fact_index_answers_biggest_hydro_queries` passing (`Mugu Karnali Storage HEP` = 1902.0 MW; `Upper Tamakoshi HPP` operating).
- **`layer-manifest.json`:** Every layer entry requires `path`, `kind`, `label`, `style`, `interactive`, `roleByPreset`.
- **`docs/generated-assets.json`:** Register any new committed generated GeoJSONs, tables, or figure assets so `scripts/check_generated_ownership.py` passes.
- **`wiki/specs-schema.json`:** Strict `additionalProperties: false` and strict enums (`status`, `project_type`, `turbine_type`, `dam_type`, `q_design`, `underground_powerhouse`).

---

## 1. Step 0 — Preflight Hygiene (Run First, 2 Minutes, 1 Commit)

Before starting Priority 1:
1. **Clean up the 5 leftover Sprint 1 Claude worktrees and temporary branches** (all their work is already landed on `data/coverage-sprint-2026-11`):
   ```bash
   for wt in /Users/hi/projects/nepalEnergy/.claude/worktrees/agent-*; do
     git worktree remove --force "$wt"
   done
   git branch -D worktree-agent-a03eccff4fa647122 worktree-agent-a53cd1a80048833a3 worktree-agent-a595498963451aa54 worktree-agent-ac3f2c8865bccf880 worktree-agent-af903dead25b46e16
   ```
2. **Fix the 1-line CEA error description in `docs/operations/overnight-sprint-report-2026-11.md`** (change `"timed out"` → `"returned HTTP 404"`).
3. **Spot-check `scripts/enrich_canonical_geography.py`** (specifically smaller substations like `saruattha`, `harnaiya`, `bodebarsain`, `salimpur`, `pangtang`, `dadakhet`, `madichaur`, `ghartigaun`, `ridi`, `keraun`, `hakui`, `bakaspur`) against NEA FY 2025/26 text and fix any misassigned district if found.
4. Commit (`Preflight: clean Sprint 1 worktrees, fix CEA 404 note, verify substation geography`).

---

## 2. Progress Tracker (Update Once Per Priority or at Wrap-Up)

| WP | Priority | Title | Status | Commit | Key Metric / Result |
|---|---|---|---|---|---|
| **Step 0** | Hygiene | Remove 5 Sprint 1 worktrees, fix CEA 404 note, spot-check substation geography | `DONE` | `94b9f38` | 5 worktrees + branches removed; CEA note → HTTP 404; 12 substations spot-checked: Harnaiya Parsa→Bara, Ridi geography withheld (Gulmi/Palpa border) |
| **WP 6A** | P1 | Geocode High-Voltage Substations (400/220/132 kV) & Industrial/Fossil/BESS Assets | `PARTIAL` | `197d0d4` | substations geocoded 28→98/153 (target ≥85 met); 400 kV 12/15, 220 kV 14/22 (targets not met); 11 legacy RPGCL coords corrected (7–14 km south bias); anchors 14/20, fossil 12/20, storage 1/10 |
| **WP 6B** | P1 | Build Explorer GeoJSON Layers, New Preset & Wire All Registries into `wiki-fact-index.json` | `DONE` | `7d292fb` | 5 GeoJSONs / 6 manifest layers, all off in overview; new energy_infrastructure preset; fact index 692→1,050 facts, 92.8 KB gzip; +substation/nonhydro/demand/storage/institution domains |
| **WP 7A** | P2 | Deepen Top 25 Thin Operating Hydro Plants (`project_specs.csv`) via Credit Ratings / Disclosures | `DONE` | `79876cb` | 20/25 operating targets thin→moderate/rich (21/25 incl. Marsyangdi); Likhu-1/Likhu-2 field swap corrected |
| **WP 7B** | P2 | Deepen Top 15 Thin Under-Construction Hydro Plants (`project_specs.csv`) + Refresh Maps & Stubs | `PARTIAL` | `8d6d39e` | dataset tiers 2 rich/24 moderate → 9 rich/41 moderate (target 15/50 not met); 8 flagship rows still thin for lack of primary specs |
| **WP 8A** | P3 | Close Sprint 1 Open Gaps: Per-Plant CEA Export List, ERC Tariff Dates, Last 10 Solar Zones | `PARTIAL` | `48e0a56` | ERC tariff effective_from verified 223/223 (2021-11-17); 28 press-sourced plant-approval rows (16/37 FY 2025/26 plants named); solar resource_zone 78→86/88; DoED vs specs solar reconciliation noted |
| **WP 9A** | P4 | Build 5 Publication-Grade Charts (`build_wiki_figures.py`) & Embed in New Data Pages | `DONE` | `649419e` | 5 new deterministic SVG charts embedded; figure manifest + ownership registered (23 SVGs total) |
| **WP 10A** | P5 | Multi-Year Geohazard Ledger (`infrastructure_hazard_events.csv`) + ICIMOD GLOF Lake Layer | `DONE` | `1766a7e` | infrastructure_hazard_events.csv 13 events (2023–2026); 21 ICIMOD 2020 dangerous lakes + opt-in GLOF layer |
| **WP 10B** | P5 | Expand Live `project_events.csv` (14→50+) & `project_blockers.csv` (16→40+) Across Top 25 Projects | `DONE` | `9eefeab` | project_events 14→57, project_blockers 16→40, 35 unique slugs |

---

## 3. Detailed Work Packages (Execute Strictly in Priority Order)

---

### PRIORITY 1 — Surface Sprint 1's New Infrastructure Backbone in the Live Explorer *(Highest ROI)*

> **Why Priority 1:** Right now, **0 of 153 substations**, **0 of 161 DoED non-hydro projects**, **0 of 20 industrial/SEZ load anchors**, **0 of 10 BESS/PSH assets**, **0 of 20 NOC fossil assets**, and **0 of 14 institutions** are visible on the Explorer map or searchable in structured Find (`wiki-fact-index.json`). Making them live transforms TransparentGov overnight from a hydro/solar map into Nepal's full energy-infrastructure hub.

#### WP 6A — Geocode High-Voltage Substations & New Spatial Registries
- **Inputs on disk:**
  - `data/substation_specs.csv` (currently 28/153 have coords; missing **9×400 kV**, **16×220 kV**, **88×132 kV**, **12×66 kV**)
  - `data/processed/maps/rpgcl_transmission_official_labels.geojson` (official RPGCL substation labels with coordinates!)
  - `data/processed/maps/transmission_network_nodes.geojson` (56 nodes)
  - `data/processed/maps/place_anchor_index.geojson`
  - `data/raw/maps/nepal-osm-free.shp.zip` (OpenStreetMap Nepal places & power features already on disk!)
  - `data/industrial_load_anchors.csv` (20 rows), `data/fossil_infrastructure.csv` (20 rows), `data/storage_non_dam_specs.csv` (10 rows)
- **Deliverables:**
  1. Write **`scripts/geocode_infrastructure_assets.py`** to match missing coordinates deterministically from local spatial assets first (`rpgcl_transmission_official_labels.geojson`, `transmission_network_nodes.geojson`, `nepal-osm-free.shp.zip`, `place_anchor_index.geojson`) and selective OSM/Nominatim verification for high-priority nodes:
     - **Target for `data/substation_specs.csv`:** Achieve **15/15 (100%) on 400 kV**, **≥ 20/22 (90%+) on 220 kV**, and **≥ 85/153 total** substations geocoded — strictly tagged with `coordinate_precision` (`official-map-node` for RPGCL/OSM substation match vs. `approximate-place` for town/municipality match; check `wiki/substation-specs-schema.json` enum!). Never fabricate coordinates.
     - Add `latitude`, `longitude`, `coordinate_precision` to `data/industrial_load_anchors.csv` (all 20 industrial districts/SEZs/corridors are well-known named places — target ≥ 18/20), `data/fossil_infrastructure.csv` (Motihari–Amlekhgunj endpoints + NOC depots — target ≥ 15/20), and `data/storage_non_dam_specs.csv` (target ≥ 8/10).
  2. Run `.venv/bin/python -m unittest tests.test_substation_specs`.
- **Done criteria:** 100% of 400 kV and ≥ 90% of 220 kV substations geocoded with verified precision tags; `test_substation_specs` passes cleanly.
- **Suggested commit:** `Geocode 400/220/132 kV substations, industrial load anchors, fossil depots, and BESS/PSH sites`

#### WP 6B — Build Explorer GeoJSON Layers, New Preset & Wire All Registries into `wiki-fact-index.json`
- **Deliverables:**
  1. Write **`scripts/build_energy_infrastructure_layers.py`** generating clean, lightweight GeoJSON layers under `data/processed/maps/` (and register them in `docs/generated-assets.json`):
     - `data/processed/maps/grid_substations.geojson` (from `substation_specs.csv`, with MVA, highest_voltage_kv, status, province, district, linked_solar_award_mw, coordinate_precision)
     - `data/processed/maps/industrial_load_anchors.geojson` (from `industrial_load_anchors.csv`, linked to `substation_slug`)
     - `data/processed/maps/fossil_infrastructure.geojson` (from `fossil_infrastructure.csv`, including a schematic LineString for Motihari–Amlekhgunj pipeline + Point features for NOC depots)
     - `data/processed/maps/non_dam_storage.geojson` (from `storage_non_dam_specs.csv`: BESS & pumped hydro)
     - `data/processed/maps/doed_nonhydro_operating.geojson` (operating wind/solar/thermal/biomass/cogen points with valid coordinate envelopes from `doed_nonhydro_registry.csv`, explicitly labelled as DoED licence-envelope reference midpoints!)
  2. Register these 5 layers in **`wiki/explorer/shared/layer-manifest.json`** (all `off` in default `overview` preset so `test_default_startup_map_payload_budget` stays green!) and add a crisp new preset **`energy_infrastructure`** (`"Full Energy Infrastructure"`) in **`wiki/explorer/shared/presets.json`** showing substations + major transmission + operating hydro + solar + industrial load anchors + fossil backbone + non-dam storage!
  3. Create minimal `record`-tier `data-layer-*` companion pages only if `validate_repo.py` requires one per manifest layer (check `validate_repo.py` first!).
  4. Extend **`scripts/build_wiki_fact_index.py`** to index structured facts from:
     - `data/substation_specs.csv` (`domain: "substation"`, `capacity_mw` = `None` or MVA stored in `facets`/dedicated field — verify `test_wiki_search_index.py` & `wiki-search.js` handling!)
     - `data/storage_non_dam_specs.csv` (`domain: "storage"`)
     - `data/industrial_load_anchors.csv` (`domain: "demand"`)
     - `data/doed_nonhydro_registry.csv` (operating/licensed wind, biomass, thermal — `domain: "nonhydro"` or `"wind"`/`"thermal"`/`"biomass"`)
     - `data/energy_institutions.csv` (`domain: "institution"`)
     - Keep compressed `wiki-fact-index.json` well below the `250,000` byte gzip cap!
  5. Add unit tests verifying the new layers, preset payload budget, and new fact-index domains (`scripts/test_explorer_performance.py`, `scripts/test_wiki_search_index.py`, `node tests/test_wiki_search_intents.js`).
- **Done criteria:** All 5 GeoJSON layers built and registered; new `energy_infrastructure` preset live; `wiki-fact-index.json` indexes substations, non-dam storage, industrial anchors, non-hydro RE, and institutions (< 250 KB gzipped); `test_explorer_performance` & `test_wiki_search_index` pass.
- **Suggested commit:** `Wire substations, industrial anchors, fossil, BESS/PSH & non-hydro layers into Explorer and fact index`

---

### PRIORITY 2 — Deepen the 54 Thin Real Operating & Under-Construction Hydro Plants (`project_specs.csv`)

> **Why Priority 2:** Sprint 1 tripled `project_specs.csv` from 25 → 87 projects, but **54 of the operating/under-construction plants are still `thin`** (many with just 1–3 fields filled!). Filling real engineering, output, cost, and PPA specs for Nepal's top 40 actual plants turns `project_specs.csv` into an unmatched public dataset.

#### WP 7A — Deepen Top 25 Thin Operating Hydro Plants (`project_specs.csv`)
- **Targets (all operating ≥ 30 MW currently `thin`):**
  `kulekhani-cascade` (106 MW, 2 filled!), `madhya-bhotekoshi` (102 MW, 6), `lower-solu` (82 MW, 3), `sanjen-khola` (78 MW, 3), `likhu-1` (77 MW, 7), `middle-tamor` (73 MW, 3), `nilgiri-khola-ii` (71 MW, 3), `madhya-marsyangdi` (70 MW, 8), `marsyangdi` (69 MW), `khimti-i` (60 MW, 8), `likhu-2` (55 MW, 7), `super-dordi-kha-hydropower-project` (54 MW, 3), `likhu-4` (52.4 MW, 4), `likhu-khola-a` (51 MW, 6), `upper-marsyangdi-a` (50 MW), `mewa-khola-hydropower-project` (50 MW), `upper-rahughat` (48.5 MW), `upper-bhotekoshi` (45 MW), `super-madi` (44 MW), `sanjen` (42.5 MW), `mistri-khola`/`mristi-khola` (42 MW), `kabeli-b-1` (25 MW), `upper-dordi-a` (25 MW), `solu` (23.5 MW), `chilime` (22 MW).
- **Best Primary Sources (Local first, then fast web):**
  1. Local PDFs: `data/raw/research/Khimti-I...pdf`, `Likhu Hydropower Cascade...pdf`, `UKHLL...pdf`, `Urja Khabar...pdf`, `nea_annual_report_2025_26.pdf`, `nea_annual_report_2024_2025.pdf`.
  2. Public credit-rating rationales from **ICRA Nepal (`icranepal.com`)** and **CARE Ratings Nepal (`careratingsnepal.com`)**, plus developer websites / ADB / IFC / FMO project disclosures (these publish exact gross head, design discharge, headrace tunnel km, turbine units, annual & dry GWh, PLF, Q-design, total cost, debt/equity, PPA rates, and COD!).
- **Target fields:** Prioritize the high-value core specs (`gross_head_m`, `design_discharge_m3s`, `headrace_tunnel_km`, `num_units`, `unit_capacity_mw`, `turbine_type`, `underground_powerhouse`, `annual_design_energy_gwh`, `dry_season_energy_gwh`, `dry_share_pct`, `plant_load_factor_pct`, `q_design`, `total_cost_usd_m`, `cost_per_mw_usd_m`, `ppa_rate_wet_npr_kwh`, `ppa_rate_dry_npr_kwh`, `debt_equity_ratio`, `lead_financier`, `cod_year`, `completion_pct`). Cite exact source in `source_note`.
- **Done criteria:** At least **20 of these 25 operating plants** lifted from `thin` → `moderate` or `rich` (≥ 25% / ≥ 50% completeness); strict `wiki/specs-schema.json` validation passes.
- **Suggested commit:** `Deepen technical, output, and financial specs for top 25 operating hydro plants`

#### WP 7B — Deepen Top 15 Thin Under-Construction & Flagship Pipeline Hydro Plants + Refresh Maps/Stubs
- **Targets:**
  `upper-tamor` (285 MW, 1 filled!), `upper-trishuli-1` (216 MW, 1 — IFC/ADB/AIIB/CDC disclosures are super rich!), `super-tamor` (166 MW, 1), `lapche-khola` (160 MW, 1), `rasuwa-bhotekoshi` (120 MW, 1), `jagdulla` (106 MW, 1), `super-trishuli` (100 MW, 1), `upper-trishuli-3b` (37 MW), `betan-karnali` (439 MW), `phukot-karnali` (426 MW), `chainpur-seti` (210 MW), `budhigandaki` (1,200 MW), `west-seti` (750 MW), `arun-3` (900 MW), `mugu-karnali-storage` (1,902 MW — currently 49%, 1 verified field from `rich`!), `dudhkoshi-storage` (670 MW — currently 46%, 2 fields from `rich`!).
- **Deliverables:**
  1. Populate verified specs for all 15+ projects from IFC/ADB/AIIB/VUCL/NEA/ICRA/CARE disclosures.
  2. Run `PYTHON=.venv/bin/python scripts/report_spec_completeness.py --all`, `scripts/gen_wiki_stubs.py --write --refresh-specs`, and `scripts/build_tributary_maps.py` so updated specs flow to map popups & auto-stubs!
- **Done criteria:** `project_specs.csv` reaches **≥ 15 `rich`** and **≥ 50 `moderate`** projects (up from 2 rich / 24 moderate); zero schema errors.
- **Suggested commit:** `Deepen specs for top 15 under-construction & flagship hydro projects and refresh map popups`

---

### PRIORITY 3 — Close Every "Still Open" Loose End from Sprint 1

#### WP 8A — Per-Plant CEA Export List, ERC Tariff Dates, Last 10 Solar Zones & Non-Hydro Crosswalk
- **Deliverables:**
  1. **`data/cross_border_approved_plants.csv`:** Expand from 10 channel-summary rows to include the **individual approved hydro plants (~28–37 plants totaling 1,200.01 MW)** using NEA press releases, NEA FY 2024/25 & 2025/26 reports, India Ministry of Power / PIB press releases, and verified energy-press disclosures (keep channel totals as a separate summary table or `record_scope = channel_summary` vs. `plant_approval` so sums are never double-counted!). Link each plant to its `project_slug` where one exists.
  2. **`data/erc_retail_tariffs.csv`:** Verify the official ERC retail tariff determination effective date(s) (e.g., ERC Decision effective Mangsir 2078 / Nov 2021 for main retail slabs + any subsequent EV charging / industrial revisions) and replace `effective_from = unknown` across all 223 rows with exact verified dates + source citations.
  3. **`data/solar_project_specs.csv` (last 10/88 `resource_zone` rows):** Resolve the 4 missing districts (`Nuwakot`, `Dang`, `Dadeldhura`, `Sankhuwasabha`) in `scripts/enrich_solar_specs.py` (using spatial intersection against `solar_ghi_zones.geojson` or nearest-zone/elevation-verified GHI zone classification, documented in `solar_enrichment_audit.csv`) so `resource_zone` reaches **88/88 (100%)**, and regenerate `solar_spec_completeness_report.md`.
  4. **Cross-check `data/processed/tables/doed_nonhydro_registry.csv` vs. `data/solar_project_specs.csv`:** Add a short reconciliation note in `wiki/pages/data/data-solar-fleet-inventory.md` documenting any operating DoED solar plants not yet in `solar_project_specs.csv`.
- **Done criteria:** All 4 Sprint 1 open items resolved or explicitly narrowed with verified sources; `test_enrich_solar_specs` and `validate_repo.py` pass.
- **Suggested commit:** `Close Sprint 1 open gaps: per-plant export approvals, ERC tariff dates, and 100% solar resource zones`

---

### PRIORITY 4 — Publication-Grade Figures for the New Datasets (`build_wiki_figures.py`)

#### WP 9A — Build & Embed 5 New Charts from Sprint 1 CSVs
- **Inputs:** `scripts/build_wiki_figures.py`, `scripts/chart_style.py`, `wiki/explorer/shared/wiki-figure-manifest.json`, and the Sprint 1 CSVs (`nea_system_annual_timeseries.csv`, `substation_specs.csv`, `plant_annual_generation.csv`, `erc_retail_tariffs.csv`, `ppa_standard_rates.csv`, `ev_adoption_and_charging.csv`).
- **Deliverables:**
  Add 5 clean, high-clarity figures (matching existing repo `chart_style.py` typography/palette and registered in `wiki-figure-manifest.json` + `docs/generated-assets.json`), and embed each in its corresponding data page:
  1. **11-Year Nepal Power System Trajectory** (`data-nea-system-annual-timeseries.md`): Stacked bar/line chart showing NEA + IPP generation, imports vs. exports (GWh), and T&D system loss falling from 25.78% → 12.2% (FY 2015/16–2025/26).
  2. **Provincial Grid Substation Capacity Imbalance** (`data-substation-inventory.md`): Horizontal bar chart comparing installed MVA vs. pipeline MVA across Nepal's 7 provinces (highlighting Bagmati 5,136 MVA vs. Karnali 60 MVA).
  3. **NEA Plant Actual vs. Design Generation Performance** (`data-plant-annual-generation.md`): Comparison bar chart for major NEA/UT plants (FY 2024/25 vs. FY 2025/26 vs. design GWh, highlighting Kulekhani's drop and Upper Tamakoshi's rebound).
  4. **Nepal Electricity Tariff & PPA Ladder** (`data-erc-retail-tariffs.md` & `data-ppa-standard-rates.md`): Clean comparison of domestic slabs, industrial 132/33 kV ToD (wet/dry peak/off-peak), EV charging rates, and NEA standard RoR/PRoR/Storage/Solar PPA rates (NPR/kWh).
  5. **Nepal EV Import Surge by Vehicle Class** (`data-load-anchors-and-fossil-backbone.md`): Customs HS-code annual import volume & value (FY 2080/81–2082/83) across electric cars, 3-wheelers, and buses.
- **Done criteria:** `PYTHON=.venv/bin/python scripts/build_wiki_figures.py` regenerates all 5 charts deterministically; manifest & ownership checks pass; figures render cleanly in the corresponding markdown pages.
- **Suggested commit:** `Add 5 data-driven charts for NEA 11-yr series, provincial substations, plant GWh, tariffs, and EV imports`

---

### PRIORITY 5 — Multi-Year Geohazard Resilience Layer & Expanded Live Project Tracking

> **Why Priority 5:** Run after Priorities 1–4 are committed. These complete the "living national infrastructure intelligence hub" layer.

#### WP 10A — Multi-Year Infrastructure Geohazard Register + ICIMOD GLOF Spatial Layer
- **Deliverables:**
  1. Create **`data/infrastructure_hazard_events.csv`** generalizing `data/flood_2026_08_impact_register.csv` into a multi-year disaster ledger covering major Himalayan hydro/grid shock events:
     - **June 2023 Eastern Nepal / Sankhuwasabha / Hewa Khola floods** (Super Hewa, Hewa Khola, Upper Hewa, Sabha Khola, etc.)
     - **September 2024 Central Nepal / Roshi / Bagmati / Tamakoshi / Kulekhani extreme floods** (Upper Tamakoshi 88-day shutdown / NPR 3.2B damage, Mandu/Bagmati Small, Kulekhani spillway/inflow, etc.)
     - **July 2025 Rasuwa / Bhotekoshi glacial flood** (Rasuwagadhi 111 MW headworks damage, Chilime/Trishuli corridor impacts)
     - **August 2026 Bhotekoshi / Trishuli flood** (summarized/cross-referenced to `flood_2026_08_impact_register.csv`)
     - Columns: `event_id`, `event_date`, `hazard_type` (`flood`, `glof`, `landslide`, `earthquake`), `river_basin`, `district`, `province`, `affected_asset_name`, `asset_slug`, `asset_type` (`hydro`, `substation`, `transmission`), `affected_mw`, `outage_days`, `estimated_damage_npr_m`, `estimated_damage_usd_m`, `impact_summary`, `source_url`, `source_title`, `confidence`, `verified_on`.
  2. Create **`data/glof_dangerous_lakes.csv`** + **`data/processed/maps/glof_dangerous_lakes.geojson`** documenting Nepal's **21 high-priority potentially dangerous glacial lakes** (ICIMOD 2020 inventory: Imja, Tsho Rolpa, Thulagi, Lower Barun, Lumding, Chamlang, Hongu, Dig Tsho, etc. — name, river basin, elevation, area, downstream hydro cascade exposure, verified coordinates from ICIMOD/public literature), and register as an opt-in hazard overlay in `layer-manifest.json`!
  3. Create concise observation-only data page **`wiki/pages/data/data-infrastructure-hazard-register.md`**.
- **Done criteria:** Every event & glacial lake entry verified from primary/ICIMOD/NDRRMA/NEA/reputable press sources; zero fabricated damage figures; registered in `docs/generated-assets.json`.
- **Suggested commit:** `Add multi-year infrastructure hazard register and ICIMOD dangerous glacial lakes map layer`

#### WP 10B — Expand `project_events.csv` (14→50+) & `project_blockers.csv` (16→40+) Across Top 25 Projects
- **Inputs:** `data/project_events.csv`, `data/project_blockers.csv`, `wiki/monitoring-schema.json`, `nea_annual_report_2025_26.pdf`, ADB/World Bank/AIIB/MCA-Nepal disclosures.
- **Deliverables:**
  1. Expand **`data/project_events.csv`** from 14 → **50+ dated milestone rows** and **`data/project_blockers.csv`** from 16 → **40+ active/resolved blocker rows** covering Nepal's top ~25 strategic generation & transmission projects (adding Tamakoshi V, Upper Arun, Upper Trishuli-1, Upper Trishuli-3B, Rahughat, Chainpur Seti, Betan Karnali, Rasuwagadhi post-flood, MCA Central 400 kV, Hetauda–Dhalkebar–Inaruwa, Gorakhpur–Butwal, Inaruwa–Purnea, Marsyangdi Corridor 220 kV, Koshi Corridor 220 kV, Kabeli Corridor, etc.).
  2. Verify strict compliance with `wiki/monitoring-schema.json` and `scripts/validate_repo.py`.
- **Done criteria:** ≥ 50 events and ≥ 40 blockers covering ≥ 22 unique project/corridor slugs; `validate_repo.py` passes cleanly.
- **Suggested commit:** `Expand project_events.csv (50+) and project_blockers.csv (40+) across top 25 strategic projects`

---

## 4. End-of-Run Single Final Build & Release Gate (Run ONCE Before Stopping!)

Whenever all WPs finish **or** you estimate <15% quota remains:
1. Stop starting new WPs immediately.
2. Update the page count in `wiki/index.md` to match the actual count in `wiki/pages/`.
3. Run the **single** full rebuild and release gate:
   ```bash
   PYTHON=.venv/bin/python make wiki-index
   make wiki-site
   PYTHON=.venv/bin/python make dashboard-build
   PYTHON=.venv/bin/python make release-check
   ```
   Fix any broken links, ownership manifest omissions, or test failures.
4. Update the Progress Tracker table in this runbook, append **one concise sprint-level entry** to `wiki/WIKI_AUDIT_LOG.md`, and write a clean morning briefing at **`docs/operations/overnight-sprint-2-report-2026-11.md`** (commits made, before/after scorecard across Explorer layers, fact-index domains, `project_specs.csv` completeness tiers, figures, and any deferred items).
5. Commit (`Rebuild wiki indexes, static site, dashboard, and add Sprint 2 completion report`) and verify `git status` is completely clean.
