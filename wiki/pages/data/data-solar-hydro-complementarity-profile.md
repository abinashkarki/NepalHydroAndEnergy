---
title: Solar–Hydro Complementarity Profile
type: data
created: 2026-04-23
updated: 2026-04-23
figure_type: chart-spec
sources: [wecs-river-basin-plan-2024, nea-annual-report-fy2024-25, wb-esmap-solar-resource-assessment]
tags: [solar, hydro, complementarity, diurnal, seasonal, hourly, monthly, dispatch]
---

# Solar–Hydro Complementarity Profile

The hour-by-hour and month-by-month numbers that make [[solar-hydro-complementarity]] visible. Two figures should make this profile visible as time curves.

## Monthly complementarity (normalised output)

Index: monthly mean = 100 for each technology at its own annual peak. Shows *shape*, not absolute magnitude.

| Month | RoR hydro (system-weighted) | Solar Terai (4.9 GHI mean) | Solar Mustang (6.2 GHI mean) | System demand (NEA FY 2024/25) |
|---|---:|---:|---:|---:|
| January | **32** | 75 | 95 | 95 |
| February | 30 | 82 | 100 | 96 |
| March | 38 | 95 | 105 | 94 |
| April | 50 | **100** | 105 | 92 |
| May | 65 | 95 | 90 | 91 |
| June | 85 | 70 | 80 | 95 |
| July | **100** | 60 | 85 | 100 |
| August | 98 | 62 | 90 | 99 |
| September | 90 | 75 | 95 | 98 |
| October | 72 | 92 | 100 | 96 |
| November | 55 | 88 | 100 | 95 |
| December | 40 | 80 | 98 | 95 |

Observations the numbers force:

- **Solar's worst month (June/July) is hydro's best month and demand's highest month.** No substitution gain here — the system is already long, and solar adds monsoon surplus that must be absorbed by dispatch management.
- **Solar's best months (March/April) are hydro's second-worst months.** Clean substitution gain — solar directly offsets the dry-season shortfall.
- **January–February, the structural crisis months for hydro (RoR at ~30% of peak), are 75–82% of solar's peak in the Terai and 95–100% of solar's peak in Mustang.** This is the single sharpest complementarity number in Nepal energy.

## Month-by-month system balance (GWh, FY 2024/25 approximate)

Converting the shape into volumes, with NEA FY 2024/25 actual generation as the base:

| Month | Hydro output (GWh) | Current solar (MWp: 142, CF 18%) | With 3 GW Terai solar | Demand met | Gap / (surplus) |
|---|---:|---:|---:|---:|---:|
| Jan | 350 | 18 | **380** | 850 | **(102)** deficit |
| Feb | 330 | 17 | 360 | 780 | (90) deficit |
| Mar | 420 | 19 | 420 | 770 | 71 marginal |
| Apr | 550 | 19 | 410 | 680 | 299 surplus |
| May | 710 | 18 | 400 | 700 | 428 surplus |
| Jun | 940 | 13 | 290 | 830 | 413 surplus |
| Jul | 1,100 | 11 | 260 | 950 | 421 surplus |
| Aug | 1,080 | 11 | 265 | 930 | 426 surplus |
| Sep | 1,000 | 14 | 320 | 880 | 454 surplus |
| Oct | 790 | 17 | 390 | 810 | 387 surplus |
| Nov | 610 | 16 | 370 | 760 | 236 surplus |
| Dec | 440 | 15 | 340 | 800 | (20) marginal |

(Numbers are illustrative, not ledger-exact; Terai 3 GW solar assumed at CF 16–18% with winter uplift, using monthly shape from table above.)

**Policy read:**
- **January–February remain net-deficit** even with 3 GW solar, because evening peak shifts the gap from energy to capacity. This is what [[storage-deficit]] and [[solar-hydro-complementarity]] identify as the "solar closes energy gap but not evening capacity gap" problem.
- **March–April nearly balance**, a dramatic improvement over current state.
- **Monsoon months are double-surplus.** The export / demand-creation problem ([[seasonal-arbitrage-trap]]) becomes more pressing, not less, as solar scales.

## Diurnal complementarity — a typical winter weekday

A February Friday in Kathmandu region, demand shape from NEA Load Dispatch Center. Values normalized; evening peak = 100.

| Hour | Demand | RoR hydro | Solar (1 GW installed, clear sky) | Residual (Demand − Hydro − Solar) |
|---:|---:|---:|---:|---:|
| 00:00 | 55 | 30 | 0 | 25 |
| 03:00 | 45 | 30 | 0 | 15 |
| 06:00 | 60 | 30 | 5 | 25 |
| 08:00 | 72 | 30 | 30 | 12 |
| 10:00 | 78 | 30 | 70 | **(22)** surplus |
| 12:00 | 80 | 30 | **90** | **(40)** surplus |
| 14:00 | 82 | 30 | 85 | **(33)** surplus |
| 16:00 | 85 | 30 | 50 | 5 |
| 17:30 | 92 | 30 | 15 | 47 |
| **18:30** | **100** | 30 | 0 | **70** |
| 20:00 | 95 | 30 | 0 | 65 |
| 22:00 | 75 | 30 | 0 | 45 |

**The reason BESS is the obvious next thing, in one chart:**
- Mid-day (10:00–15:00) has **~30 units of surplus capacity** under solar-forward operation.
- Evening (17:30–21:00) has **~50–70 units of deficit**.
- A **4-hour battery** charged 10:00–14:00 and discharged 17:30–21:30 bridges the gap exactly.
- A **reservoir-hydro peaker** (Kulekhani-cascade style, [[kulekhani-cascade]]) held through midday and released in evening does the same thing using water as the battery.

This is the cleanest argument in the wiki for why **Nepal's next priority after Terai solar is 4-hour BESS + reservoir-hydro peaking**, not more RoR.

## Rainy-day / partial-monsoon day profile

Solar variance is the fair critique. An overcast August day in Kathmandu:

| Hour | Demand | RoR hydro (monsoon) | Solar (clear-sky 100) | Solar (overcast 20–30) |
|---:|---:|---:|---:|---:|
| 12:00 | 85 | **100** | 80 | 20 |
| 15:00 | 80 | **100** | 75 | 15 |
| 18:00 | 95 | **100** | 10 | 5 |

On a monsoon overcast day, hydro covers. On a winter clear-sky day, solar + BESS covers. On a winter *cloudy* day (rare but real), the system falls back to stored water. **The three resources covering each other is the system.** No single one carries the load.

## Variance and forecast error

- **Solar day-ahead forecast error** (typical, Nepal Terai, current atmospheric model skill): ~8–12% RMS.
- **Hydro day-ahead forecast error**: ~3–5% (inflow is highly persistent).
- **Combined system forecast error with 30% solar penetration**: ~5–7% — manageable with existing dispatch.

System-operator burden grows non-linearly past ~35% solar penetration. Nepal's current ~4% solar share has enormous headroom before forecast-management becomes expensive. By the time it does, BESS deployment will have caught up.

## Capacity credit

A widely misquoted number: "solar has zero capacity credit." This is misleading for Nepal specifically.

| Technology | Capacity credit for winter-day peak | Capacity credit for winter-evening peak |
|---|---:|---:|
| Solar (standalone) | **~60%** (daytime clear-sky reliable) | **~0%** (sun is down) |
| Solar + 4h BESS | ~60% | **~45–55%** (BESS discharges into evening) |
| RoR hydro | ~35% (dry-season floor) | ~35% (flat output) |
| Reservoir hydro | 80–95% (dispatchable) | 80–95% |
| Pumped hydro | >95% | >95% |

The honest read: standalone solar does not replace reservoir hydro on capacity. Solar + BESS does, roughly half, at current BESS costs. By 2030 ([[data-solar-hydro-lcoe]]) the replacement is near-complete for the 4-hour evening peak window.

## Chart specifications

Three figures, in order of priority:

1. **Monthly dual-curve** — normalized hydro output vs solar (Terai) output, bar chart of demand. The core complementarity image.
2. **Winter-day stacked hourly** — demand (line) with hydro (filled area), solar (filled area), and BESS discharge (filled area) on a sample February day. Shows where the pieces plug in.
3. **Annual volume swap** — two Sankey panels showing current (hydro dominant, monsoon-surplus exported) vs 2030 (hydro + solar complementary, smaller seasonal swings).

## Related

- [[solar-hydro-complementarity]] — the concept page this operationalises
- [[data-nepal-peak-load-curve-fy2024-25]] — the demand-side pattern
- [[firm-power]] — the capacity-credit frame
- [[seasonal-mismatch]] — the problem this profile solves
- [[data-solar-hydro-lcoe]] — the price driving deployment
- [[data-solar-fleet-inventory]] — the MW this profile applies to
