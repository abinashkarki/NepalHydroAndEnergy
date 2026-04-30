---
title: Unresolved Questions
type: synthesis
created: 2026-04-14
updated: 2026-04-15
sources: []
tags: [synthesis, gaps, verification, follow-up]
---

# Unresolved Questions

Areas where public evidence remains thin, source definitions conflict, or more granular data would materially improve the hub.

## Research Gaps

| # | Gap | Why It Matters | Status |
|---|-----|---------------|--------|
| 1 | DHM long time-series discharge data by tributary | Validate basin-level flow claims at project resolution | **OPEN** — likely locked behind institutional access |
| 2 | Monthly import-export time series | Strengthen [[seasonal-arbitrage-trap]] argument beyond annual aggregates | **FILLED** — month-by-month GWh table for FY 2079/80 (~2022/23), combined with FY 2025/26 NPR monthly revenue data. See [[data-trade-time-series]] |
| 3 | Plant-level curtailment and outage data | Quantify [[stranded-generation]] precisely | **OPEN** — NEA Load Dispatch Center data not public |
| 4 | NEA financial health | Audited accounts, debt burden, PPA liability exposure | **FILLED** — FY 2024/25 financials and May 2025 white paper data in [[nea]] |
| 5 | Project-level sediment and geology assessments | Move [[sediment-as-design-constraint]] from general to specific | **OPEN** — requires individual project EIAs |
| 6 | Demand-side load shape (hourly/daily) | Critical for system design and [[firm-power]] analysis | **PARTIALLY FILLED** — evening peak timing (18:30-19:25), peak import-at-peak magnitude (643 MW in Falgun 2080), and monthly import totals are documented. Full hourly load curve is not public. See [[data-domestic-demand]] |
| 7 | Post-2024 Bangladesh trade route status | Scale-up trajectory for buyer diversification | **FILLED** — full page at [[bangladesh-trade-route]] |
| 8 | Chinese-linked project status | Earlier public summaries left uncertainty unresolved | **FILLED** — West Seti (CTG withdrew 2018, NHPC now), Budhigandaki (Gezhouba blocked, domestic). See [[west-seti]], [[budhigandaki]] |
| 9 | Environmental/social impact data on storage candidates | Displacement, ecological, downstream effects of [[budhigandaki]], [[dudhkoshi-storage]] | **PARTIALLY FILLED** — Budhigandaki resettlement (8,117 households, NPR 42.65B compensation) now documented |
| 10 | Comparison with other mountain hydro systems | Norway, Switzerland, [[bhutan-hydropower-model]], Laos with actual data | **FILLED** — [[data-mountain-hydro-comparison]] created with IHA/StatRanker/Oxford data |

## Data Conflicts Needing Resolution

| Data Point | Conflict | Recommended Handling |
|------------|--------|-------------|
| Installed capacity | NEA annual report, DoED registry, and hydro-only totals answer different questions | Use **3,591.262 MW total / 3,389.912 MW hydro** for NEA FY 2024/25, and **3,791.874 MW** for the DoED Apr 10, 2026 >1 MW registry |
| Hydro MW | Hydro-only totals can be confused with total installed capacity | Use **3,389.912 MW** in data pages that mean hydro-only FY 2024/25 |
| Trade totals FY 2024/25 | NEA narrative, monthly balance, and trade chart totals differ | Keep all three NEA views with labels: **narrative 1,681 / 2,380**, **monthly table 1,712 / 2,380**, **trade chart 1,711.5272 / 2,331.7360** |
| Potential (gross) | Legacy 83,000 MW slogan vs WECS 2019 reassessment | Keep both: 83k legacy slogan + **72,544 MW** WECS 2019 gross reassessment |
| Potential (techno-economic) | Different filters produce different ranges | Use **32,680 MW** from WECS 2019 where the exact reassessment is needed |
| Current storage (MCM) | Active and gross reservoir volume are mixed in public summaries | Keep both: **85 MCM active** / **130-150 MCM total** |
| Cross-border capacity | Rounded older values compete with project-specific approvals | Use **1,141 MW approved**, with older ~1,000 MW references retained only as rounded framing |
| System losses | Source year and accounting frame differ | Keep source-year tags: **13.46%** (NEA FY 2024/25) vs **~12.7%** (2024 report framing) |
| Basin discharge baselines | Gauge points and basin-border models are not interchangeable | Always label **measurement point**: gauge (e.g. Chatara/Chisapani) vs WECS border model |
| Electricity access | Metered households and broader access/service indicators differ | Keep both by scope: **91.41% metered households** vs **~95% broader access/service indicator** |
| Fleet split | Detailed fleet split and shorthand RoR+PRoR share use different classifications | Use **85.7/9.9/3.7%** for the granular split, with **>90% RoR+PRoR** as shorthand |
| Per-capita electricity | Different source years create a range | Use **370-465 kWh** as a range unless a specific source year is named |

## Claims Still Needing Verification

| Claim Area | What's Needed | Status |
|------------|--------------|--------|
| 400/220 kV corridor status | Current status of internal transmission buildout | **FILLED** — corridor table in [[claim-transmission-immediate-blocker]] with 7 segments verified |
| Plant-wise export approvals | Sharpen firm-vs-surplus export argument | **PARTIALLY FILLED** — 941 MW approved from 28 projects; India CEA data confirms project-level approvals |
| Realized export prices | Firm up [[seasonal-arbitrage-trap]] economics | **FILLED** — NPR 7.11/unit export avg, 6.40 US cents Bangladesh, in [[data-trade-time-series]] |
| Pancheshwar status | Refine [[pancheshwar]] treatment | **FILLED** — Feb 2025 ministerial meeting, 50-50 vs 75-25 impasse, JEG-6 deadline; updated in [[pancheshwar]] |
| China-linked projects | Keep [[hydro-geopolitics]] accurate | **FILLED** — CTG withdrew West Seti 2018, Gezhouba blocked from Budhigandaki; updated in [[hydro-geopolitics]], [[west-seti]], [[budhigandaki]] |

## Related

- [[provider-comparison]] — methodology and evidence review notes
- [[master-thesis]] — the argument these gaps could strengthen or challenge
- [[data-pipeline-readme]] — copied scripts and dataset pipeline inventory
