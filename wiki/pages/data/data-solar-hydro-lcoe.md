---
title: Solar and Hydro LCOE
type: data
created: 2026-04-23
updated: 2026-04-23
figure_type: chart-spec
sources: [nea-annual-report-fy2024-25, irena-remap-nepal, wb-grid-solar-ee-project]
tags: [solar, hydro, LCOE, tariff, PPA, price, economics, crossover]
---

# Solar and Hydro LCOE

The numerical table behind [[solar-lcoe-crossover]]. Three time series — global solar LCOE, Nepal solar auction tariff, Nepal hydro PPA — plus a value-weighted adjustment.

## Global utility-scale solar LCOE (IRENA Renewable Cost Database)

Weighted global average, levelized, 2024 US dollars.

| Year | Global LCOE ($/MWh) | Module price ($/W) | Capacity factor (weighted) | Notes |
|---:|---:|---:|---:|---|
| 2010 | 359 | ~2.00 | 15% | Crystalline Si, pre-scale |
| 2012 | 240 | 1.20 | 16% | |
| 2014 | 165 | 0.76 | 17% | First Chinese scale |
| 2016 | 110 | 0.55 | 17% | |
| 2018 | 84 | 0.37 | 18% | Auction-discovery era |
| 2020 | 59 | 0.22 | 18% | COVID module glut |
| 2022 | 49 | 0.25 | 19% | Tracker + bifacial standard |
| 2024 | **~44** | **~0.10** | 19–20% | Record-low GCC & India auctions |
| 2025 (est.) | ~40 | ~0.09 | 20% | Continuing oversupply |
| 2030 (projected) | ~30–35 | ~0.08 | 20–21% | IRENA midpoint scenario |

**Module price decline 2010 → 2024: −95%.**
**System LCOE decline 2010 → 2024: −88%.**

## Nepal utility-scale solar auction tariffs

| Auction round | Year | MW awarded | Tariff band (NPR/kWh) | USD equivalent (at period FX) | Notes |
|---|---|---:|---|---:|---|
| First utility round | 2016–17 | 24 | 7.30–8.40 | $0.065–0.075 | 5 developers; 3 × COD 2019–20 (Butwal, Mithila, Bishnu Priya, etc.) |
| NEA Grid Solar & EE Project EPC | 2019–20 | 25 | NEA self-build (capex-based) | — | Bidur / Trishuli 25 MWp |
| IPP rounds FY 2080/81 | 2023 | 45 | 6.40–6.50 | $0.048–$0.049 | — |
| IPP rounds FY 2081/82 | 2024 | ~170 (8 plants) | **5.94–6.50** | **$0.044–$0.049** | PPA signed, COD 2026–27 |
| **960 MW national tender** | 2024–25 | 960 (64 project selections) | **4.99–5.55** | **$0.038–$0.042** | NEA LoI weighted average ~5.43 NPR/kWh |

Nepal's price discovery is following the global auction curve with a ~3–5 year lag; the 960 MW tender tariff is ~40% higher than Gulf-region 2024 lows ($0.030–$0.035) and ~20% above India 2024 lows (₹2.4–2.6/kWh ≈ $0.029–$0.031).

## Nepal hydropower PPA tariffs

NEA-standard PPA structure for IPPs (all figures NPR/kWh; effective since 2016 structure, with periodic revisions):

| Project class | Dry-season (Dec–May) | Wet-season (Jun–Nov) | Blended | Escalation |
|---|---:|---:|---:|---|
| **Small RoR (≤ 25 MW)** | **8.40** | **4.80** | ~6.20 | 3%/yr for first 8 yrs |
| Small RoR (>25 MW to 100 MW) | ~7.90–8.10 | 4.55–4.75 | ~5.90–6.05 | Case-by-case |
| PRoR (peaking run-of-river) | 9.30 | 5.15 | ~6.80 | 3%/yr |
| Large hydro (cost-plus) | 7.50–9.50 | 4.25–5.40 | ~5.80–7.20 | Case-by-case |
| Reservoir storage (new) | 9.50–12.00 | 5.50–7.00 | 7.50–9.50 | Case-by-case |
| Arun-3 / Upper Karnali (export) | export-priced, ~USD 0.043–0.055 | same | same | in USD terms |

## The crossover table

| Technology × year | LCOE / PPA (NPR/kWh) | USD equivalent | Notes |
|---|---:|---:|---|
| Small RoR hydro PPA (blended, current) | **6.20** | $0.047 | Time-un-weighted |
| PRoR hydro PPA (blended, current) | 6.80 | $0.052 | |
| Solar 2024/25 NEA tender (blended) | **~5.43** | ~$0.041 | 960 MW LoI weighted average |
| Solar 2018 NEA auction (blended) | 7.80 | $0.070 | First round |
| Solar 2030 projected (Nepal) | **~4.50–5.20** | $0.034–$0.039 | With 4h BESS: ~6.50–7.50 |
| Global solar LCOE 2024 | 3.8 (NPR eq) | $0.044 | IRENA weighted |
| Gulf 2024 record-low | 2.6 | $0.020 | AEDNRM, UAE |

The Nepal hydro-solar crossover happened between the **2018 (7.80)** and **2023 (6.40)** solar auction rounds. By the 2024 NEA LoI round, **solar is roughly 12% cheaper than small RoR on a blended tariff basis and materially cheaper on a time-weighted-value basis** (see next section).

## Time-weighted value adjustment

A kWh does not have a single price. Dry-season kWh value in the Indian cross-border market is ~2× a monsoon kWh ([[seasonal-arbitrage-trap]]). Adjusted for when each technology delivers:

| Technology | Annual kWh | % in dry-season (Dec–May) | % in wet-season (Jun–Nov) | Value-weighted price ($/MWh) |
|---|---|---:|---:|---:|
| Small RoR hydro | 1,000 | **~30%** | **~70%** | ~51 |
| Solar (Terai) | 1,000 | **~55%** | **~45%** | **~40** |
| Storage hydro (Kulekhani-style) | 1,000 | ~60% | ~40% | ~68 |
| Coal import (proxy benchmark) | 1,000 | 100% dispatchable | — | ~85 |

Solar's ~55% dry-season share (resulting from clear-sky season + low monsoon penalty in Terai) pushes its value-weighted price ~20% below its nominal tariff; RoR's ~30% dry-season share pushes its value-weighted price ~20% above. The two effects compound: **value-weighted, solar is ~22% cheaper than RoR, not 4%.**

This is the single most important economic re-framing for the [[claim-solar-cheaper-than-small-hydro]] claim.

## Solar + BESS crossover trajectory

Utility-scale 4-hour battery system LCOE (Wood Mackenzie / BloombergNEF data):

| Year | BESS LCOE ($/MWh, 4h) | Combined solar+4h-BESS ($/MWh) | Matches reservoir-hydro at (NPR/kWh) |
|---:|---:|---:|---|
| 2020 | 190 | 240 | — (out of range) |
| 2022 | 140 | 185 | — |
| 2024 | **95** | **135–150** | — |
| 2026 (proj.) | 75 | 115 | ~NPR 15 (not yet) |
| 2028 (proj.) | 55 | 95 | ~NPR 12 (matches high-end storage hydro) |
| **2030 (proj.)** | **40** | **~80** | **~NPR 10 (matches mid-range storage hydro)** |

Solar + 4h-BESS reaches **NPR 10/kWh equivalence with new reservoir-hydro around 2030**, at current price-decline trajectories. This is the point at which the **firm capacity** argument for new large reservoir hydro (vs solar + BESS) becomes unclear on pure economics.

## Chart specifications

Three charts for the video essay:

1. **Time-series line chart** — global solar LCOE 2010–2030 (solid), Nepal solar auction tariffs 2017–2025 (dashed with points), Nepal small-RoR PPA (horizontal band). Crossover point annotated.
2. **Stacked-bar per-technology** — current LCOE bars for RoR, PRoR, new storage hydro, solar (auction), solar (LCOE), solar+4h BESS. With time-weighted-value adjustment as a second panel.
3. **Projection fan** — solar LCOE + solar+BESS 2025–2035, with hydro-storage benchmark horizontal. The crossover year for firm-capacity equivalence is the climax.

## Caveats and data hygiene

- Nepal tariffs are **NPR-denominated and escalate 3%/yr for first 8 yrs** in standard PPA; USD conversions use period FX and are approximate.
- Gulf-region solar auction lows ($20–25/MWh) reflect different capital costs, grid conditions, land prices, and tax structures — they are not directly apples-to-apples with Nepal.
- Reservoir-hydro LCOE has wide error bars because sediment / GLOF / cost-overrun risk is case-by-case.
- Solar + BESS capacity-credit comparison assumes 4 hours of storage; longer-duration storage (8h+) is not yet cost-competitive.
- PR (performance ratio) assumed 17–19% for fixed-tilt Terai; could rise to 20–21% with tracker + bifacial.

## Related

- [[solar-lcoe-crossover]] — the concept page
- [[claim-solar-cheaper-than-small-hydro]] — the tracked claim
- [[seasonal-arbitrage-trap]] — the time-weighted valuation frame
- [[data-solar-fleet-inventory]] — the MW this pricing is being applied to
- [[data-solar-hydro-complementarity-profile]] — the profile that drives the time-weighting
- [[irena-remap-nepal]] — IRENA's Nepal-specific cost assessment
