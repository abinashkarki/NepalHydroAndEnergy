---
title: Solar–Hydro Complementarity
type: concept
created: 2026-04-23
updated: 2026-04-23
sources: [nea-annual-report-fy2024-25, wecs-river-basin-plan-2024, wecs-energy-synopsis-2024]
tags: [solar, hydro, seasonality, diurnal, complementarity, firm-power, dispatch]
page_quality: analysis
---

# Solar–Hydro Complementarity

Nepal's structural problem is **timing** ([[claim-timing-not-volume]]). The single most under-used lever for fixing timing is the one physical resource whose generation profile is a near-mirror of Nepal's RoR hydrograph: **utility-scale solar PV**.

This page makes the complementarity argument in two dimensions — **seasonal** and **diurnal** — and then draws the honest consequences for fleet design.

## Seasonal complementarity: strong and exploitable

Nepal's hydro fleet is >90% run-of-river ([[claim-ror-dominance]], [[run-of-river-hydropower]]). RoR output is a direct function of discharge, which collapses to **25–35% of monsoon peak** in January–February ([[seasonal-mismatch]], [[data-basin-discharge]]). The hydro fleet is therefore **worst exactly when clear skies are best**: the dry winter months in Nepal have the highest fraction of clear-sky days, the lowest aerosol / cloud cover, and the lowest atmospheric water column.

Put into a single annual curve:

| Season | Hydro output (RoR-weighted) | Solar output (plane-of-array) | Net to system |
|--------|---------|---------|---------|
| Monsoon (Jun–Sep) | **100** (index) | **~65–75** (heavy cloud cover, esp. mid-hills) | Hydro dominant, monsoon surplus |
| Post-monsoon (Oct–Nov) | ~70 | ~100 | Balanced, both contribute |
| Dry winter (Dec–Feb) | **~30–40** | **~85–95** (cool, clear, low aerosol) | **Solar fills hydro's deficit** |
| Pre-monsoon (Mar–May) | ~45–55 | ~100–110 (highest GHI of year) | Solar dominant, rising hydro |

The pairing is close to **anti-correlated at the annual scale**. No other resource available to Nepal in the next decade — not imports, not gas, not wind, not new storage hydro — has this profile combined with sub-18-month deployability.

The monsoon cost is real (monsoon cloud cover knocks ~25–35% off mid-hill GHI, less off Terai, very little off the trans-Himalayan rain-shadow valleys), but that is exactly the season when hydro is already over-producing and exporting cheap. The system does not *need* the monsoon solar; it desperately needs the winter solar.

## Diurnal complementarity: partial, honest about the gap

The seasonal story is clean. The daily story is not — and this is where casual analysis routinely oversells solar:

- **Solar peak:** ~11:00–14:00 (fixed tilt) or broadened ~09:00–16:00 (single-axis tracking). Essentially zero after sunset.
- **RoR hydro:** nearly flat across 24 hours for a given day's inflow.
- **Nepal's system peak demand:** **~18:00–21:00** in winter (lighting, cooking transition, heating loads) — *after sunset*.

So solar closes the **winter-afternoon** gap but leaves the **winter-evening** gap untouched. The evening peak is the domain of:

1. **Reservoir / PRoR peaking hydro** — [[kulekhani-cascade]], [[tanahu-hydropower]], [[budhigandaki]] (the [[storage-deficit]] story).
2. **Battery storage** — grid-scale BESS charging from mid-day solar and discharging into the evening ramp.
3. **Demand-side shifting** — if electrified cooking arrives ([[data-domestic-demand]]), moving part of the evening cook-peak to mid-day is worth 100–300 MW of avoided peaking capacity.

Solar therefore does **not** make storage redundant. It re-ranks the storage question: Nepal no longer needs storage to serve the winter-*day*; it needs storage (water or chemical) to shift the winter-*day's solar* into the winter-*evening's demand*. That is a qualitatively easier engineering problem than building a seasonal reservoir.

## The three fleet-design implications

### 1. Solar is not "renewable padding" — it is a substitute for the dry-season kWh that RoR physically cannot deliver.

The 2,000–3,000 GWh dry-season energy gap that [[storage-deficit]] and [[seasonal-mismatch]] attribute to missing reservoirs can, at current LCOE ([[solar-lcoe-crossover]]), be met partly by **3–5 GW of Terai solar** producing ~4,500–7,500 GWh/year of which ~1,200–2,000 GWh lands in the Dec–Feb window. This does not eliminate the storage case — but it **de-risks the dry-season deficit** while large reservoir projects go through their 8–12 year build cycles.

### 2. Hybrid sites (solar co-located at hydro) are the cheapest MW Nepal can build.

Existing hydropower sites already carry: an access road, an interconnecting substation, spare evacuation headroom (especially in dry-season when hydro is under-producing), and land (often 1–5 ha of reservoir-adjacent or de-watered terrain). Adding 10–50 MWp of PV at these sites shares ~30–40% of balance-of-system cost. See [[hybrid-siting-logic]].

### 3. Curtailment and wet-season surplus become co-managed problems.

Mid-day monsoon solar over-produces into a grid that is already long on monsoon hydro. Without coordination this is a curtailment nightmare. The solution is **sequenced dispatch**: hold upstream hydro pondage through mid-day (let solar serve the load), release in evening. Done well, monsoon solar lets reservoir operators **defer water into the evening peak and the dry season**, even when they only have 4–8 hours of pondage. This is the operational bridge between [[seasonal-arbitrage-trap]] and a fleet that finally earns premium pricing in its own winter.

## What the complementarity claim does *not* say

- It does not say solar replaces hydro. Hydro remains >70% of energy through 2040 on any realistic build-out.
- It does not say Nepal should stop building storage hydro. The evening peak still needs water or batteries.
- It does not say solar is free. Land, interconnection, and panel import costs are real; see [[agrivoltaics-and-land]].
- It does not say the complementarity is perfect. Monsoon days are cloudy; some winter weeks are cloudy too.

It says something narrower and more actionable: **for the specific problem of the dry-season-day deficit in a RoR-dominated system, solar is the cheapest, fastest, and physically best-matched resource Nepal has access to.**

## Related

- [[solar-resource-geography-nepal]] — where the resource is and why altitude beats latitude
- [[solar-lcoe-crossover]] — the price argument
- [[hybrid-siting-logic]] — the physical co-location play
- [[data-solar-hydro-complementarity-profile]] — the hour-by-hour numbers
- [[claim-timing-not-volume]] — the master claim this concept operationalises
- [[seasonal-mismatch]] — the problem statement
- [[storage-deficit]] — the adjacent lever
- [[firm-power]] — what the system actually needs
