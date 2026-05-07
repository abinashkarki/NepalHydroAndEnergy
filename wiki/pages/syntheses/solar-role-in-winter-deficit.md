---
title: Solar's Role in the Winter Deficit
type: synthesis
created: 2026-04-23
updated: 2026-05-07
sources: [nea-annual-report-fy2024-25, wecs-river-basin-plan-2024, irena-remap-nepal]
tags: [solar, hydro, winter, deficit, seasonal, complementarity, strategy, storage, BESS, synthesis]
page_quality: analysis
---

# Solar's Role in the Winter Deficit

The wiki's existing framing treats Nepal's winter deficit as a **storage problem** ([[storage-deficit]], [[seasonal-mismatch]]). The honest 2026 framing is: **part-storage, part-solar, part-demand-shaping**. This synthesis is an argument for the updated framing, with quantified contribution shares for each lever.

## The problem, tightened

Nepal's **Dec–Feb dry-season energy gap** is approximately:

| Component | Magnitude (GWh / season, 3 months) | Source |
|---|---:|---|
| Current domestic demand | ~2,130 | NEA FY 2024/25, baseline_fy2025 scenario |
| Current hydro output | ~1,551 | Same |
| Current gap (covered by imports) | **~550** | Same |
| Projected demand 2030 (at 8%/yr growth) | ~3,128 | 2030_baseline scenario, build_winter_deficit_model.py |
| Projected demand 2035 (at 7%/yr growth) | ~4,188 | 2035_full scenario, build_winter_deficit_model.py |

The 2030 gap more than doubles from today’s ~550 GWh baseline; by 2035, demand growth at 7% CAGR adds roughly 2,000 GWh to the problem if supply does not keep pace. The lever-ranking below addresses the 2030 and 2035 gaps, not the 2024 gap.

## The four levers

### Lever 1: Storage hydropower (reservoir + PRoR)

**Mechanism:** Shift monsoon water into dry-season generation. The [[claim-storage-physical-fix]] answer.

**Realistic 2035 contribution:** [[tanahu-hydropower]] (140 MW, COD 2026 — under construction, 67% complete as of mid-2025) + [[dudhkoshi-storage]] (670 MW, COD ambitious ~2035). ([[budhigandaki]] 1,200 MW excluded from pre-2036 scenarios — main EPC contract not expected until January 2028, implying earliest COD 2036.) Aggregate new storage dry-season generation ~800–900 GWh/winter-season above the RoR baseline. (Model: 2035_full hydro ~3,246 GWh vs. 2035_solar_only hydro ~2,412 GWh = net storage addition of ~834 GWh.)

**Physical advantage:** Dispatchable; provides capacity credit for evening peak; non-intermittent.

**Strategic weakness:** Build timelines. Beyond Tanahu (2026), none of the remaining storage projects has COD before 2035; [[buildability]] concerns are severe ([[budhigandaki]] has been at "planning" stage for 20+ years). If storage is the only lever, the **2027–2034 window has no new dispatchable storage — Dudhkoshi is the next meaningful addition, with an ambitious COD of ~2035.**

### Lever 2: Utility-scale Terai solar

**Mechanism:** Exploit the ~55% dry-season-share of solar generation (Terai, [[data-solar-hydro-lcoe]]) to fill the daytime energy component of the winter gap.

**Realistic 2035 contribution:** Current ~142 MWp + 170 MWp PPA-signed + 960 MW tender + ~500 MW additional pipeline = **~1,700 MWp by 2028** → **~3,500 MWp by 2032** → **~5,000 MWp by 2035** (at moderate growth).

At 5 GW of Terai solar with CF 16.5% (empirical GIZ/AEPC measurement for Terai fixed-tilt), Dec–Feb dry-season generation ~**966 GWh** (2035_full model output at 16.5% CF); the full dry-season (Nov–Mar) contribution is higher. Source: build_winter_deficit_model.py, 2035_full scenario.

**Physical advantage:** 2–3 year build cycle. The only lever that operates on the 2026–2030 window. Cheaper per-kWh than any new hydropower ([[solar-lcoe-crossover]]).

**Strategic weakness:** Zero contribution to 6 pm evening peak. Requires land (see [[agrivoltaics-and-land]]). Requires BESS or hydro peaking for firm capacity.

### Lever 3: Demand-shaping (electrification + time-of-use)

**Mechanism:** Shift the winter-evening peak (the hardest MW to cover) into mid-day (when solar + flat hydro are available) through electrified cooking + time-of-use tariffs + large industrial demand scheduling.

**Realistic 2035 contribution:**
- Electric cooking penetration: 1% → 20% by 2035 moves ~200–400 MW of winter-evening peak to mid-day if combined with ToU pricing.
- Industrial process scheduling (rolling mills, cement, crushers): ~150–300 MW shiftable to mid-day.
- Net peak-reduction effect: ~300–700 MW, equivalent to ~500–1,200 GWh/winter-season of "virtual storage."

**Physical advantage:** Cheapest lever per kWh shifted. No new physical plant.

**Strategic weakness:** Requires coordinated tariff reform (ERC + NEA), consumer behavior change (slow), and electrification of cooking (slow — [[data-domestic-demand]] shows <1% of households cook electric today).

### Lever 4: Battery energy storage (BESS)

**Mechanism:** Charge from mid-day solar and discharge into the winter-evening peak. The [[data-solar-hydro-complementarity-profile]] diurnal profile case.

**Realistic 2035 contribution:** At 2 GWh of 4h-BESS deployed (plausible 2030–2035 rollout if tender-integrated with solar), covers **~500 MW** of evening peak for 4 hours (2 GWh / 4h). If cycled once daily through the core Dec–Feb winter window, that is roughly **116 GWh** of dispatchable evening energy; Phase 1 keeps BESS as a placeholder energy term, while Phase 2 uses the 500 MW capacity value for evening-peak analysis.

**Physical advantage:** Pairs with solar to provide firm capacity. 4-hour BESS at 2030 prices (~NPR 10/kWh LCOE per [[data-solar-hydro-lcoe]]) competes with reservoir hydropower on firm-capacity cost.

**Strategic weakness:** Capex; cycle life; thermal management in Terai heat. Not yet routinely included in Nepal PPA structures.

## The combined portfolio — 2035 dry-season energy balance

Assuming all four levers work at realistic-ambition (not best-case) levels:

| Lever | Dec–Feb GWh (model) | Firm-capacity note |
|---|---:|---|
| New storage hydro (Tanahu + Dudhkoshi above RoR baseline) | ~834 | Dispatchable; evening capacity credit |
| Utility solar 5 GW Terai (16.5% CF) | ~966 | Daytime only; zero evening without BESS |
| BESS 2 GWh | ~1 (Phase 1 placeholder; about ~116 GWh if cycled once daily across core Dec–Feb) | ~500 MW evening firm capacity |
| Demand-shaping | ~400 | Shifts ~400 MW of evening peak |
| Existing RoR + rooftop baseline | ~2,412 | Continues at current trajectory |
| **Total supply** | **~4,613** | |
| 2035 Dec–Feb demand | ~4,188 | |
| **Net position** | **+425 GWh surplus** | **Gap closed; surplus is headroom** |

Source: `scripts/build_winter_deficit_model.py`, 2035_full scenario. Demand CAGR 7% (2030–35), solar CF 16.5% Terai fixed-tilt, storage pipeline excludes Budhigandaki.

## The Budhigandaki distinction

The model clarifies a distinction the narrative math obscured: Budhigandaki is not necessary to close the 2035 energy gap, but it is the decisive asset for evening firm capacity. At 8%/7% CAGR, the four-lever portfolio closes the Dec–Feb energy balance without Budhigandaki — the 2035_full and 2035_no_budhigandaki scenarios are identical at 0 GWh deficit. But the Phase 2 diurnal model shows a 933 MW residual evening-peak gap at 18:30 in the 2035_full scenario (23% of peak demand) — covered today by imports, and in 2035 still requiring either Budhigandaki or a combination of additional BESS, explicit peak demand-shaping, and cross-border capacity. Budhigandaki's 1,200 MW at 0.9 dispatch factor contributes 1,080 MW to the evening peak, flipping the 933 MW gap to a 147 MW surplus. It is not an energy asset for 2035 — it is a capacity asset, and the most important one in the pipeline. Source: `scripts/build_diurnal_peak_model.py`, 2035_with_budhigandaki scenario.

The combined portfolio **closes the 2035 winter deficit if all four levers execute.** No single lever closes it alone.

## The re-ranking this argues for

The existing [[bottleneck-hierarchy]] ranks:

1. Storage deficit
2. Transmission readiness
3. Buildability
4. Market design / demand
5. Climate / hazard
6. Governance
7. Geopolitics

The updated ranking, if this synthesis holds:

| Rank | Bottleneck | Change |
|---:|---|---|
| 1 | **Transmission + delivery (including solar interconnection)** | Promoted, because 5 GW solar needs grid headroom |
| 2 | **Land + agrivoltaic framework for Terai solar** | **New** |
| 3 | **Storage build-out (hydro + BESS)** | Re-framed: combined, not hydro-alone |
| 4 | Demand-shaping + electrification | Promoted |
| 5 | Buildability | Unchanged |
| 6 | Market / PPA / tariff design | Unchanged |
| 7 | Geopolitics | Unchanged |

The biggest change: **storage** is no longer a pure reservoir-hydro question, and **solar-land-politics** becomes a top-tier national constraint it was not before.

## Three policy moves this synthesis implies

### 1. Tender integration — mandate solar-plus-BESS in the next round.

The 960 MW Phase IV tender ([[nea-960mw-solar-tender]]) does not include BESS mandates. The Phase V tender, for ~1,500–2,000 MW, should. This alone captures ~500 MW of evening-peak firm capacity at marginal capex.

### 2. Agrivoltaic framework — deliver the four institutional fixes from [[agrivoltaics-and-land]].

Lease-template law, agrivoltaic tariff adder, technical standards, VGF channel. Without these, the Terai solar build-out stalls at ~2 GW.

### 3. ERC-led time-of-use tariff reform.

Creates the demand-side incentive for lever 3. Also structures the right price signals for BESS investment.

## Relationship to the master thesis

[[master-thesis]] argues: Nepal is failing to convert hydrological advantage into firm, deliverable, resilient power.

This synthesis adds: **The fleet that delivers firm winter power in 2035 is not predominantly hydro. It is a hydro + solar + BESS + demand-shaping portfolio. The mastery Nepal needs is not in hydrological conversion alone; it is in sequencing a four-lever portfolio, and in the institutional capacity to deliver all four on overlapping timelines.**

That is a more complex master strategy than "build reservoirs." But it is also a more achievable one — the four levers are partial substitutes, so slippage in any one does not collapse the whole.

## Related

- [[master-thesis]] — the master frame
- [[solar-in-the-master-narrative]] — the parallel synthesis
- [[solar-hydro-complementarity]] — the physical basis
- [[storage-deficit]], [[seasonal-mismatch]] — the problems
- [[data-solar-hydro-complementarity-profile]] — the hour-by-hour numbers
- [[bottleneck-hierarchy]] — the ranking to patch
- [[data-winter-deficit-model]] — the reproducible monthly energy-balance model backing this synthesis
- [[claim-timing-not-volume]], [[claim-storage-physical-fix]] — the claims this synthesis extends
