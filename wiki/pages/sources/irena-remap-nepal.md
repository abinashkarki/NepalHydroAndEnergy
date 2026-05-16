---
title: IRENA Renewable Readiness Assessment and REmap Nepal
type: source
created: 2026-04-23
updated: 2026-04-23
source_type: report
source_author: International Renewable Energy Agency (IRENA)
source_date: 2023-01-01
source_url: https://www.irena.org/publications
sources: []
tags: [irena, renewable, solar, nepal, lcoe, cost, policy, remap]
---

# IRENA Renewable Readiness Assessment and REmap Nepal

Primary international source for **solar and renewable cost benchmarking** against Nepal specifics. Two IRENA document streams are relevant:

1. **IRENA Renewable Readiness Assessment (RRA) — Nepal (2017, with subsequent updates).** Country-level diagnostic; identifies barriers and potential across solar, wind, and small hydro.
2. **IRENA REmap Nepal scenario analysis.** Quantitative pathway modelling for higher renewables shares in Nepal's electricity and total energy mix.

Plus the **IRENA Renewable Capacity Statistics** (annual, global) and **Renewable Cost Database** — which provide the global LCOE benchmarks this project uses in [[data-solar-hydro-lcoe]] and [[solar-lcoe-crossover]].

## What these sources cover

- Solar PV technical potential by Nepal resource zone
- Wind potential (limited but non-trivial in Mustang + parts of Koshi)
- Small hydro potential (overlaps with [[wecs-hydropower-potential-2019]])
- Barriers analysis: financing, policy, grid integration, skills
- LCOE benchmarks for Nepal-comparable countries
- Scenario pathways to 2030 / 2050 with renewables share
- Policy recommendations and institutional framework proposals

## Key data points (composite from RRA + REmap + Cost Database)

### Solar (Nepal-specific)

- **Estimated solar PV technical potential:** ~50,000–100,000 MWp (various IRENA framings; caveats on siteability)
- **Mean Nepal GHI:** ~4.7–4.9 kWh/m²/day (matches Global Solar Atlas)
- **Suggested short-term target:** >1 GW by 2030 (REmap Accelerated Case); policy + financing gaps identified as primary blocker, not resource

### Global LCOE benchmarks (IRENA Renewable Cost Database)

- Utility-scale solar PV weighted global LCOE 2010 → 2024: **$0.359 → $0.044 per kWh** (−88% real)
- Module price 2010 → 2024: $2.00/W → ~$0.10/W (−95%)
- Onshore wind LCOE 2010 → 2024: $0.113 → $0.033 per kWh
- BESS (4h utility) LCOE 2020 → 2024: ~$190 → ~$95 per MWh
- Capacity-weighted auction-low solar tariff 2024: ~$0.020–$0.030/kWh (GCC, India)

These are the numbers the [[solar-lcoe-crossover]] argument rides on.

## IRENA's diagnostic frame for Nepal

The RRA identifies five priority barriers:

1. **Policy coherence** — fragmented responsibility across MoEWRI / NEA / AEPC / ERC
2. **Financing access** — limited local-currency long-tenor finance for renewables
3. **Grid integration** — transmission and distribution readiness for variable resources
4. **Institutional capacity** — solar-specific engineering and O&M depth is thin
5. **Land and permits** — no agrivoltaic framework, fragmented land tenure

Most of these overlap with the [[bottleneck-hierarchy]] for hydro, with one addition specific to solar: **absence of land/permitting framework** for utility-scale ground-mount.

## Why this source matters to the project

- Provides the **global LCOE benchmarks** the [[solar-lcoe-crossover]] and [[data-solar-hydro-lcoe]] pages rely on.
- Gives an **externally-credentialed estimate of Nepal solar potential** without the over-promise of some national documents.
- Frames the **barriers analysis** in language compatible with donor programs — useful for mapping AEPC / EIB / WB programme gaps.
- The REmap pathway is a reasonable benchmark against which to judge the NEA/MoEWRI 2024/25 actual trajectory (960 MW tender + 170 MW PPA + 142 MW operating).

## Data-quality and caveats

- IRENA's Nepal "technical potential" estimates vary widely (50,000–100,000+ MWp) depending on whether high-mountain inaccessible land is counted. **Only the Zone A trans-Himalayan + Zone B Terai + Zone C mid-hill deployable fraction (~15,000–25,000 MWp) matters for real planning**; see [[data-solar-fleet-inventory]] potential pyramid.
- IRENA REmap pathways are **normative scenarios, not forecasts.** Use for direction of travel, not for calendar-year predictions.
- Global LCOE benchmarks reflect **weighted averages**; Nepal-specific numbers should always be context-adjusted for grid costs, land costs, and FX.

## Relevance to project

Anchor citation for:

- [[solar-lcoe-crossover]]
- [[data-solar-hydro-lcoe]]
- [[data-solar-fleet-inventory]] (potential pyramid)
- [[solar-resource-geography-nepal]]
- [[claim-solar-cheaper-than-small-hydro]]

## Related

- [[wb-esmap-solar-resource-assessment]] — the measured-resource complement
- [[global-solar-atlas-nepal]] — the satellite-derived complement
- [[wecs-energy-synopsis-2024]] — the domestic energy-balance frame
- [[wb-country-economic-memo-2025]] — macroeconomic context
