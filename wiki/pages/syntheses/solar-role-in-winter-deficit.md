---
title: Solar's Role in the Winter Deficit
type: synthesis
created: 2026-04-23
updated: 2026-04-23
sources: [nea-annual-report-fy2024-25, wecs-river-basin-plan-2024, irena-remap-nepal]
tags: [solar, hydro, winter, deficit, seasonal, complementarity, strategy, storage, BESS, synthesis]
---

# Solar's Role in the Winter Deficit

The wiki's existing framing treats Nepal's winter deficit as a **storage problem** ([[storage-deficit]], [[seasonal-mismatch]]). The honest 2026 framing is: **part-storage, part-solar, part-demand-shaping**. This synthesis is an argument for the updated framing, with quantified contribution shares for each lever.

## The problem, tightened

Nepal's **Dec–Feb dry-season energy gap** is approximately:

| Component | Magnitude (GWh / season, 3 months) | Source |
|---|---:|---|
| Current domestic demand | ~2,400–2,700 | NEA FY 2024/25 monthly balance |
| Current hydro output | ~1,100–1,300 | RoR-dominated fleet at dry-season floor |
| Current gap (covered by imports) | **~1,100–1,400** | NEA monthly trade statistics |
| Projected demand 2030 (at ~8%/yr growth) | ~3,800–4,300 | IPSDP projections |
| Projected demand 2035 (at ~7%/yr growth) | ~5,300–6,000 | Long-range extrapolation |

On any realistic load-growth scenario, the **dry-season gap triples by 2035 if nothing changes**. The lever-ranking below addresses the 2030 and 2035 gaps, not the 2024 gap.

## The four levers

### Lever 1: Storage hydropower (reservoir + PRoR)

**Mechanism:** Shift monsoon water into dry-season generation. The [[claim-storage-physical-fix]] answer.

**Realistic 2035 contribution:** [[tanahu-hydropower]] (140 MW, COD ~2027–28) + [[budhigandaki]] (1,200 MW, COD speculative ~2032–35) + [[dudhkoshi-storage]] (~635 MW, COD speculative ~2033+) + [[uttarganga-storage]] + [[mugu-karnali-storage]]. Aggregate new dry-season generation ~2,000–3,500 GWh/winter-season if schedule holds.

**Physical advantage:** Dispatchable; provides capacity credit for evening peak; non-intermittent.

**Strategic weakness:** Build timelines. None of the named projects is COD before 2027; [[buildability]] concerns are severe ([[budhigandaki]] has been at "planning" stage for 20+ years). If storage is the only lever, the **2027–2032 window is physically uncovered.**

### Lever 2: Utility-scale Terai solar

**Mechanism:** Exploit the ~55% dry-season-share of solar generation (Terai, [[data-solar-hydro-lcoe]]) to fill the daytime energy component of the winter gap.

**Realistic 2035 contribution:** Current ~142 MWp + 170 MWp PPA-signed + 960 MW tender + ~500 MW additional pipeline = **~1,700 MWp by 2028** → **~3,500 MWp by 2032** → **~5,000 MWp by 2035** (at moderate growth).

At 5 GW of Terai solar with CF 18% and winter uplift, dry-season generation ~**1,800–2,200 GWh/winter-season**.

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

**Realistic 2035 contribution:** At 2 GWh of 4h-BESS deployed (plausible 2030–2035 rollout if tender-integrated with solar), covers ~2 GW of evening-peak for 4 hours = **~720 GWh/winter-season of dispatchable evening-peak energy**.

**Physical advantage:** Pairs with solar to provide firm capacity. 4-hour BESS at 2030 prices (~NPR 10/kWh LCOE per [[data-solar-hydro-lcoe]]) competes with reservoir hydropower on firm-capacity cost.

**Strategic weakness:** Capex; cycle life; thermal management in Terai heat. Not yet routinely included in Nepal PPA structures.

## The combined portfolio — 2035 dry-season energy balance

Assuming all four levers work at realistic-ambition (not best-case) levels:

| Lever | Dry-season GWh contribution (3 months) | Firm-capacity contribution (MW at 6 pm) |
|---|---:|---:|
| Storage hydro new build | **~2,500** | ~800–1,500 |
| Utility solar (5 GW Terai) | **~2,000** | ~0 (without BESS) |
| BESS (2 GWh) | ~720 | ~500 |
| Demand-shaping | ~800 | ~400 |
| Rooftop + off-grid solar | ~300 | ~50 |
| **Total new dry-season energy** | **~6,320 GWh** | ~1,750–2,450 MW firm |
| 2035 dry-season gap (projected) | ~5,300–6,000 | ~1,800–2,200 |
| Net position | **~balanced** | **~balanced** |

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
- [[claim-timing-not-volume]], [[claim-storage-physical-fix]] — the claims this synthesis extends
