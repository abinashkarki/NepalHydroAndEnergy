---
title: Seasonal Mismatch
type: concept
created: 2026-04-14
updated: 2026-11-04
reviewed: 2026-11-04
review_due: 2027-02-04
as_of: 2026-07-16
sources: [wecs-river-basin-plan-2024, wb-water-sector-diagnostic, nea-annual-report-fy2025-26, nea-annual-report-fy2024-25]
tags: [seasonality, monsoon, dry-season, grid, nepal, RoR, demand]
excerpt: Why Nepal can run an electricity surplus in the monsoon and a deficit in the dry season within the same hydro-dominated system, measured month by month.
caveat: Monthly figures are NEA energy-balance totals; plant-level dispatch, hourly load and curtailment series are not publicly consolidated.
maturity: verified-core
page_quality: flagship
---

# Seasonal Mismatch

## Summary

Seasonal mismatch is the gap between when Nepal's rivers deliver water and when its people need electricity. Most of Nepal's power comes from run-of-river hydropower, which generates when water arrives. Water arrives mostly in the monsoon. Demand runs all year. The result is a surplus from roughly Baishakh to Mangshir and a deficit from Poush to Chaitra, every year, regardless of how much capacity is installed. In FY 2025/26, a record net-export year, domestic generation still fell 60% from Bhadra to Falgun and Nepal imported 273 GWh in Falgun ([[nea-annual-report-fy2025-26]], PDF p.176).

## Simple Explanation

Nepal's rivers swell with the monsoon from June to September and shrink through the winter and spring. A run-of-river plant can only use the water passing it, so its output follows the river. Electricity demand changes far less across the year. So the same plants that produce more than Nepal can use in the monsoon produce too little in the dry season. The country exports the surplus and imports the shortfall. This is not a drought and not a shortage of plants. It is two calendars that do not line up.

## The river calendar

Nepal's rivers draw on monsoon rain, snow, glaciers and groundwater, but the annual rhythm is weighted heavily toward the rains. WECS basin modelling places 67–78% of annual runoff in June to September for the Koshi basin, with 11–14% after the monsoon and 5–11% in winter and pre-monsoon ([[wecs-river-basin-plan-2024]], p.20). Other basins differ in detail but share the shape. These are modelled shares, so exact percentages should be quoted by basin, period and method.

Snow and glacier melt lift spring flows in some high basins, which is why generation starts recovering in Baishakh before the monsoon arrives. They do not fill the deepest part of the dry season.

## The electricity calendar

NEA's monthly energy balance shows the river calendar written into the power system.

<figure class="wiki-inline-figure">
  <img src="../assets/figures/energy_balance_fy2025_26.svg" alt="Monthly domestic generation and national demand in FY 2025/26">
  <figcaption>FY 2025/26: domestic generation exceeded national demand from Baishakh to Mangshir and fell short from Poush to Chaitra. Source: [[nea-annual-report-fy2025-26]], PDF p.176.</figcaption>
</figure>

| Month (FY 2025/26) | Domestic generation (GWh) | National demand (GWh) | Export (GWh) | Import (GWh) |
|---|---:|---:|---:|---:|
| Bhadra (Aug–Sep 2025) | 1,991 | 1,405 | 587 | 1 |
| Kartik (Oct–Nov 2025) | 1,716 | 1,056 | 660 | 0 |
| Poush (Dec 2025–Jan 2026) | 1,125 | 1,221 | 40 | 124 |
| Falgun (Feb–Mar 2026) | 801 | 1,067 | 13 | 273 |
| Chaitra (Mar–Apr 2026) | 917 | 1,163 | 21 | 264 |
| Ashadh (Jun–Jul 2026) | 2,161 | 1,608 | 582 | 27 |

Generation fell 60% between Bhadra and Falgun; national demand fell 24%. The same pattern appears in FY 2024/25, when generation was 1,848 GWh in Bhadra and 605 GWh in Falgun ([[nea-annual-report-fy2024-25]], p.134). The mismatch is a property of the system, not of one year's weather.

## Energy, not the annual peak

A common assumption is that the dry season is when demand peaks. The FY 2025/26 data say otherwise. NEA's national peak demand of 2,479 MW occurred on 28 June 2026 and the system peak of 3,226 MW, which includes exports, on 6 July 2026, both at the start of the monsoon ([[nea-annual-report-fy2025-26]], PDF p.13). The dry-season problem is different. It is a shortage of energy across whole months, and of power in the evening hours, when rivers are low.

The hourly shape matters. Evening peak timing (around 18:30–19:25) and peak-hour imports of 643 MW in Falgun 2080 are documented, but a full public hourly load curve is not ([[unresolved-questions]], [[data-domestic-demand]]). Without it, nobody outside NEA can calculate exactly how much dependable capacity the dry season requires.

## Why more run-of-river amplifies both sides

Adding run-of-river capacity is not neutral. It adds energy mostly when the system is already long, and adds little to the dry-season floor. Each new plant enlarges the monsoon surplus that must be exported or spilled, while the winter deficit shrinks only slowly. This is why debates about "potential megawatts" miss the point captured in [[claim-timing-not-volume]] (C-001, high): timing can matter more than volume.

The pattern is visible plant by plant. [[marsyangdi|Marsyangdi]] (69 MW) shows the monsoon-to-dry collapse even in a year at 97% of design generation; [[madhya-marsyangdi|Madhya Marsyangdi]] (70 MW) and [[upper-tamakoshi|Upper Tamakoshi]] (456 MW) show the same shape at different amplitudes. Peaking run-of-river plants can move water within a day, such as Kali Gandaki A's six hours of daily peaking, but not across months ([[claim-pror-not-storage]], C-009, high).

## How the system balances today

Today the dry-season gap is closed mainly by imports from India. Nepal imported 1,155 GWh in FY 2025/26 on the energy-balance table, almost all of it from Poush to Baishakh ([[nea-annual-report-fy2025-26]], PDF p.176). Cross-border transfer limits, set bilaterally, cap how much can flow: up to about 750 MW of imports in FY 2025/26, with a July 2026 agreement raising the combined Dhalkebar corridor limit to 1,400 MW import (PDF p.14). Imports are a reliable tool while India has power to sell at an acceptable price. They are also the most expensive power Nepal buys: about NPR 9.0 per kWh on NEA's summary totals, against about NPR 7.4 earned per kWh exported ([[seasonal-arbitrage-trap]]).

The seasonal-storage contribution is small. The Kulekhani cascade, Nepal's only operating reservoir system, generated 92 GWh across FY 2025/26, most of it in Baishakh and Jestha ([[storage-deficit]]).

## What changes the mismatch

Only a few measures change the mismatch itself rather than moving who bears it:

- **Seasonal storage** that holds monsoon water for the dry months ([[storage-deficit]], [[claim-storage-physical-fix]]). It is the clearest physical answer and the hardest to build ([[buildability]]).
- **Dry-season resources**, mainly daylight generation that is strongest when rivers are weakest; see [[solar-hydro-complementarity]]. It needs pondage, batteries or demand shifting to reach the evening peak.
- **Demand that moves with supply.** Industrial and cooking loads that can shift toward the monsoon or toward daylight reduce the winter evening requirement ([[intervention-electric-cooking-transition]]).
- **Contracts that pay for readiness.** The standard energy-priced tariff rewards energy whenever it arrives. The 2082 reservoir directive distinguishes declared available capacity from contract energy ([[erc-reservoir-ppa-directive-2082]], [[ppa-pricing]]).
- **Imports and trade**, which balance the system but leave it exposed to Indian prices and corridor limits ([[claim-india-decisive-actor]]).

## What it means for planning

The mismatch changes the question planners should ask. "How many megawatts?" has a large, easy answer. "How much electricity can Nepal count on in Falgun, in the evening, at the load centres?" has a smaller and harder one. A useful plan writes down that dry-season requirement first: energy across the dry months, power in the risky hours, how long the power must last, where it must be delivered, and who carries the risk if it fails. Each proposed resource is then judged by what it contributes to that requirement, not by its nameplate.

Under that test, a new run-of-river plant contributes mainly monsoon energy, a reservoir contributes months of shifting, a battery contributes hours, solar contributes dry-season daylight, and an import contract contributes whatever its terms guarantee. None is sufficient alone. The mismatch is why Nepal's electricity strategy needs a portfolio measured in dependable dry-season service, which the [[master-thesis]] develops.

The surplus side has costs too. NEA names minimising generation curtailment as a challenge in its FY 2025/26 report, but no curtailment volume is published, so the energy lost in the monsoon cannot yet be measured ([[stranded-generation]]).

## Common Misunderstandings

- **"Seasonal mismatch is a drought problem."** It recurs every year, including years of record exports.
- **"Annual net exports mean Nepal has enough electricity."** FY 2025/26 had 2,794 GWh of net exports and still imported in every month from Poush to Baishakh.
- **"More dams will solve it."** More run-of-river dams enlarge the monsoon surplus. Only seasonal storage, dry-season resources or flexible demand change the winter floor.
- **"Solar eliminates the mismatch."** Solar helps in daylight. The evening peak still needs another resource.
- **"The dry season is when demand peaks."** In FY 2025/26 the annual peaks came in late June and early July. The dry-season shortfall is about energy across months and power in the evening.

## What would change our mind

- Plant-level data showing the run-of-river fleet's dry-season output rising faster than dry-season demand, so that imports fall without new storage.
- A published hourly load curve showing that the dry-season evening requirement is much smaller than monthly energy totals suggest.
- A sustained shift in basin hydrology that raises winter flows, for example from glacier melt, enough to close the gap. Current evidence points the other way ([[claim-climate-harder-not-easier]]).

## Related

- [[storage-deficit]] — the physical answer and its limits
- [[firm-power]] — what the system can depend on, as distinct from what is installed
- [[run-of-river-hydropower]] — the plant type that follows the river
- [[seasonal-arbitrage-trap]] — the price consequence of selling surplus and buying shortfall
- [[solar-role-in-winter-deficit]] — how a daylight resource changes the dry-season arithmetic
- [[data-trade-time-series]] — multi-year monthly trade
- [[master-thesis]] — the wiki's full argument
- [[film-nepal-has-hydropower]] — the documentary built around this mismatch

## Update history

| Date | Change |
|---|---|
| 2026-11-04 | Rebuilt around measured FY 2025/26 monthly data, with the river calendar sourced to WECS 2024, a chart and month table, the timing of the annual peak, current balancing by imports, and conditions for revision |
| 2026-07-19 | Reviewed for the V1 release |
| 2026-04-14 | Created |
