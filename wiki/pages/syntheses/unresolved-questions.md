---
title: Unresolved Questions
type: synthesis
created: 2026-04-14
updated: 2026-04-15
sources: []
tags: [synthesis, gaps, verification, follow-up]
---

# Unresolved Questions

Areas that remain thin across all five providers and data conflicts that need resolution before the master document or video essay can be finalized.

## Research Gaps (Thin Across All Providers)

| # | Gap | Why It Matters | Status |
|---|-----|---------------|--------|
| 1 | DHM long time-series discharge data by tributary | Validate basin-level flow claims at project resolution | **OPEN** — likely locked behind institutional access |
| 2 | Monthly import-export time series | Strengthen [[seasonal-arbitrage-trap]] argument beyond annual aggregates | **FILLED** — DeepResearch Part 7 provides full month-by-month GWh table for FY 2079/80 (~2022/23). Combined with FY 2025/26 NPR monthly revenue data, both dimensions now covered. See [[data-trade-time-series]] |
| 3 | Plant-level curtailment and outage data | Quantify [[stranded-generation]] precisely | **OPEN** — NEA Load Dispatch Center data not public |
| 4 | NEA financial health | Audited accounts, debt burden, PPA liability exposure | **FILLED** — FY 2024/25 financials and May 2025 white paper data in [[nea]] |
| 5 | Project-level sediment and geology assessments | Move [[sediment-as-design-constraint]] from general to specific | **OPEN** — requires individual project EIAs |
| 6 | Demand-side load shape (hourly/daily) | Critical for system design and [[firm-power]] analysis | **PARTIALLY FILLED** — DeepResearch Part 7 provides evening peak timing (18:30–19:25), peak import-at-peak magnitude (643 MW in Falgun 2080), and monthly import totals. Full hourly load curve not public but structural pattern now documented. See [[data-domestic-demand]] |
| 7 | Post-2024 Bangladesh trade route status | Scale-up trajectory for buyer diversification | **FILLED** — full page at [[bangladesh-trade-route]] |
| 8 | Chinese-linked project status | All providers flag uncertainty, none resolves | **FILLED** — West Seti (CTG withdrew 2018, NHPC now), Budhigandaki (Gezhouba blocked, domestic). See [[west-seti]], [[budhigandaki]] |
| 9 | Environmental/social impact data on storage candidates | Displacement, ecological, downstream effects of [[budhigandaki]], [[dudhkoshi-storage]] | **PARTIALLY FILLED** — Budhigandaki resettlement (8,117 households, NPR 42.65B compensation) now documented |
| 10 | Comparison with other mountain hydro systems | Norway, Switzerland, [[bhutan-hydropower-model]], Laos with actual data | **FILLED** — [[data-mountain-hydro-comparison]] created with IHA/StatRanker/Oxford data |

## Data Conflicts Needing Resolution

| Data Point | Hermes | Claude | Codex | Gemini | Recommended |
|------------|--------|--------|-------|--------|-------------|
| Installed capacity | 3,349 MW | ~2,800–3,000 | 3,591 MW | 3,591 MW | Use **two labels**: **3,591.262 MW total / 3,389.912 MW hydro** for NEA FY 2024/25, and **3,791.874 MW** for the DoED Apr 10, 2026 >1 MW registry |
| Hydro MW (wiki-internal) | — | — | 3,389.912 | 3,339 | **3,389.912 MW** in data pages that mean hydro-only FY 2024/25 |
| Trade totals FY 2024/25 | — | — | 1,681 / 2,380 | — | Keep all three NEA views: **narrative 1,681 / 2,380**, **monthly table 1,712 / 2,380**, **trade chart 1,711.5272 / 2,331.7360** |
| Potential (gross) | 83,000 | 83,000 | 72,544 | 83,000 | **Both**: 83k legacy slogan + **72,544 MW** WECS 2019 gross reassessment |
| Potential (techno-economic) | 42–46k | 25–35k | 32,680 | — | **32,680 MW** (WECS 2019) |
| Current storage (MCM) | — | 130–150 | — | 85 active | **Both**: **85 MCM active** / **130–150 MCM total** |
| Cross-border capacity | — | 300–600 utilized | ~1,000 | 1,141 approved | **1,141 MW approved**, with older ~1,000 MW references retained only as rounded framing |
| System losses | — | — | ~12.7% | 13.46% | Keep source-year tags: **13.46%** (NEA FY 2024/25) vs **~12.7%** (2024 report framing) |
| Basin discharge baselines | Gauge-heavy | Gauge-heavy | Border-model-heavy | Mixed | Always label **measurement point**: gauge (e.g. Chatara/Chisapani) vs WECS border model |
| Electricity access | — | — | 91.41% household electrification | ~95% access | Keep both by scope: **91.41% metered households** vs **~95% broader access/service indicator** |
| Fleet split | 85.7/9.9/3.7% | 70/20/10% | >90% RoR+PRoR | >90% RoR+PRoR | **85.7/9.9/3.7%** (Hermes, most granular), with >90% RoR+PRoR as shorthand |
| Per-capita electricity | — | — | 370–400 kWh | 380–465 kWh | **370–465 kWh** (range) |

## Claims Still Needing Verification

From Hermes claim ledger:

| Claim Area | What's Needed | Status |
|------------|--------------|--------|
| 400/220 kV corridor status | Current status of internal transmission buildout | **FILLED** — corridor table in [[claim-transmission-immediate-blocker]] with 7 segments verified |
| Plant-wise export approvals | Sharpen firm-vs-surplus export argument | **PARTIALLY FILLED** — 941 MW approved from 28 projects; India CEA data confirms project-level approvals |
| Realized export prices | Firm up [[seasonal-arbitrage-trap]] economics | **FILLED** — NPR 7.11/unit export avg, 6.40 US cents Bangladesh, in [[data-trade-time-series]] |
| Pancheshwar status | Refine [[pancheshwar]] treatment | **FILLED** — Feb 2025 ministerial meeting, 50-50 vs 75-25 impasse, JEG-6 deadline; updated in [[pancheshwar]] |
| China-linked projects | Keep [[hydro-geopolitics]] accurate | **FILLED** — CTG withdrew West Seti 2018, Gezhouba blocked from Budhigandaki; updated in [[hydro-geopolitics]], [[west-seti]], [[budhigandaki]] |

## Related

- [[provider-comparison]] — what each provider covered well
- [[master-thesis]] — the argument these gaps could strengthen or challenge
- [[data-pipeline-readme]] — copied scripts and dataset pipeline inventory
