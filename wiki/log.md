---
title: Log
type: overview
created: 2026-04-14
updated: 2026-04-15
---

# Wiki Log

## 2026-04-14

- Wiki created with project extensions for claim and data page types.
- Directory structure: sources, entities, concepts, syntheses, claims, data.
- Building from source extraction, narrative drafts, and data verification passes.
- Created 15 source pages (NEA, WECS, WB, ADB, ICIMOD, GGGI, India CBTE).
- Created 5 data pages (basin discharge, fleet composition, trade series, storage comparison, potential pyramid).
- Created 16 entity pages (4 basins, 7 projects, 2 orgs, 3 country profiles).
- Created 15 concept pages (analytical vocabulary for the research domains).
- Created 12 claim pages for tracked assertions.
- Created 5 synthesis pages for the master thesis, bottleneck hierarchy, methodology notes, 20-year strategy, and open questions.
- Populated index.md with all 68 pages.
- Cross-link pass: verified all pages have 2+ outbound wikilinks.

### Gap-filling round 1 (2026-04-14, evening)

Researched 7 of 10 identified gaps + 5 of 5 claims needing verification. Sources: NEA annual reports, Rising Nepal Daily, Kathmandu Post, Reuters, Diplomat Nepal, myRepublica, IHA country profiles, India CEA, Oxford Clean Energy journal, Global Energy Monitor.

**New pages created (3):**
- [[bangladesh-trade-route]] — full trilateral trade entity page
- [[west-seti]] — West Seti project with Chinese withdrawal history
- [[data-mountain-hydro-comparison]] — Norway/Bhutan/Laos/Nepal benchmark table

**Major updates to existing pages (8):**
- [[data-trade-time-series]] — added FY 2025/26 monthly revenue, Bangladesh detail, system peak data
- [[seasonal-arbitrage-trap]] — added FY 2024/25 headline improvement + monthly collapse ratio
- [[pancheshwar]] — detailed Feb 2025 ministerial meeting, 50-50 vs 75-25 impasse, 30-year timeline
- [[budhigandaki]] — upgraded to Apr 2026 status: bids open, land 90% acquired, 2028 target, no Chinese role
- [[nea]] — full financial health section (FY 2024/25 profit −37%, liabilities NPR 385B, May 2025 white paper)
- [[claim-transmission-immediate-blocker]] — added 7-segment corridor status table, upgraded confidence
- [[nepal-energy-profile]] — updated system peak, export approvals, Supreme Court protected-area halt
- [[hydro-geopolitics]] — rewrote China section based on West Seti/Budhigandaki evidence
- [[data-storage-comparison]] — added 50 TWh off-river pumped hydro potential finding

**Gap resolution summary:** 5 of 10 gaps fully filled, 2 partially filled, 3 remain open (DHM discharge, plant-level curtailment, hourly load shape — all likely institutional/non-public data). All 5 claims verification items resolved.

Index updated: 71 pages across 6 categories.

### Additional research integration — all 7 parts (2026-04-14, later)

All 7 parts of the extended research corpus integrated. Parts 1, 2, 3, 6 assessed earlier. Parts 4, 5, 7 were then received and checked. Quality verdict: Part 7 (economics/trade) was strongest; Part 5 (technology) was useful but thinner; Part 4 (seasonal/climate) was summary-grade and mainly confirmed existing claims.

**New pages created (1):**
- [[data-domestic-demand]] — sectoral demand split, load profile (18:30–19:25 peak), electric cooking gap (<1% households), FY 2020/21 supply mix (imports 31.83% of supply)

**Major updates (7 pages):**
- [[data-trade-time-series]] — Added full month-by-month GWh table (FY 2079/80/~2022/23): Baisakh 395.7 GWh imported / zero exported; IEX price evolution 2021-24 (spread flipped positive in 2023-24); Falgun 2080 406.3 GWh single-month import; 654 MW winter import approval Jan-Mar 2026
- [[seasonal-arbitrage-trap]] — Rewrote with IEX two-layer analysis (positive exchange spread vs negative system-wide average), monthly table proof, evening peak context
- [[domestic-led-hydro-strategy]] — Added electric cooking <1%, sectoral demand data, and winter-scarcity framing
- [[sediment-as-design-constraint]] — Added Kali Gandaki A field test data (IEC 60041, best-point 90-92%, overhaul degradation), Khimti multi-stage system (0.13mm threshold), 80% of forced outages from turbine/generator/excitation, Pelton erosion case
- [[peak-water]] — Added quantitative climate table (0.02-0.16°C/yr, -0.3 to -0.8 m w.e./yr glacier balance, glacial lake +0.83%/yr), Karnali decomposition (glacier ice melt = 0.8% of annual flow, snowmelt = 24%)
- [[nepal-energy-profile]] — Updated installed capacity to DoED Apr 10, 2026 figure: 3,791.874 MW / 189 plants
- [[master-thesis]] — Added "winter scarcity tax" framing line

**Gaps update:**
- Gap #2 (monthly GWh trade): now **FILLED** — month-by-month resolution added from the extended trade evidence
- Gap #6 (load shape): upgraded to **PARTIALLY FILLED** — evening peak timing and magnitude documented
- Data conflict: installed capacity updated to 3,791.874 MW (DoED Apr 2026)

Index updated: 72 pages across 6 categories.

## 2026-04-15

### Code-workspace merge

Merged structured outputs from `/Users/hi/projects/nepalEnergy` into this workspace as the canonical research home.

**Assets copied:**
- `data/processed/` tables, lead-1 outputs, map layers, and text extractions
- `figures/` static charts (9 PNGs)
- `wiki/assets/maps/` interactive HTML maps, preview PNGs, and GeoJSON layer copies
- `scripts/` regeneration scripts

**New pages created (2):**
- [[data-map-inventory]] — layer counts, map entry points, missing geometries, next annotation layers
- [[data-pipeline-readme]] — script inventory, inputs/outputs, regeneration caveats

**Major updates (12+ pages):**
- All major `[[data-*]]` pages now point to linked CSVs and figure assets.
- [[data-trade-time-series]] now preserves the NEA three-way mismatch (narrative vs monthly table vs trade chart) instead of flattening it.
- [[data-mountain-hydro-comparison]] aligned Nepal hydro MW with [[data-fleet-composition]] at **3,389.912 MW**.
- [[nepal-energy-profile]] corrected the DoED-vs-NEA installed-capacity labeling and added load-shedding / flood-damage context.
- [[koshi-basin]], [[karnali-basin]], and [[ganges-contribution]] absorbed net-new merged numbers.
- Basin and storage-project entity pages now link to the imported map assets.

**Conflict-resolution notes added to wiki:**
- Installed capacity now split by **NEA FY 2024/25 cut-off** vs **DoED Apr 10, 2026 registry**.
- Losses now carry source-year scope (**13.46%** vs **~12.7%**).
- Electricity access now distinguishes **91.41% metered households** vs broader **~95% access** framing.
- Basin discharge now explicitly distinguishes **gauge means** from **WECS border-model means**.

Index updated: 74 pages across 6 categories.
