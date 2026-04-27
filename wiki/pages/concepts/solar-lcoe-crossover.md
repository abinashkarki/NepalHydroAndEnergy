---
title: Solar LCOE Crossover
type: concept
created: 2026-04-23
updated: 2026-04-23
sources: [nea-annual-report-fy2024-25, irena-remap-nepal, wb-grid-solar-ee-project]
tags: [solar, LCOE, tariff, economics, PPA, module-price, crossover]
---

# Solar LCOE Crossover

The single most-out-of-date assumption in Nepal's public energy discourse is that **solar is expensive relative to hydro**. It was true in 2014. It was marginal in 2019. By the NEA's 2081/82 (2024/25) competitive-bid awards, **solar had become the cheapest new-build generation in Nepal, by a wide and widening margin** — cheaper than small run-of-river, cheaper than medium run-of-river with long transmission legs, and roughly on par with the *levelized* cost of reservoir storage hydro (before counting hydro's locational premium).

This concept page documents the crossover and draws out what it means for a fleet strategy that was designed under obsolete price assumptions.

## The global price collapse

Utility-scale solar PV LCOE, weighted global average, IRENA Renewable Cost Database:

| Year | Global LCOE (USD/MWh, 2024 real) | Notes |
|------|---:|---|
| 2010 | **359** | Pre-scale solar, crystalline silicon only |
| 2014 | 165 | First Chinese scale effects |
| 2018 | 84 | Auction-driven price discovery |
| 2020 | 59 | COVID-era module glut begins |
| 2022 | 49 | Tracker + bifacial cost-in |
| **2024** | **~44** | Record-low bids in GCC, India ₹2.4–2.6/kWh (~$29–31/MWh) |

That is an **~88% real reduction in 14 years**. Modules alone fell from ~$2.00/W (2010) to ~$0.10/W (2024) — a 95% reduction. Balance-of-system fell ~60%. Inverters fell ~70%. The decline is not a subsidy story and not a temporary glut story; it is a manufacturing-learning-curve story, and it is still going.

## Nepal's tariffs — where we actually land

Nepal's NEA runs a **tariff-based competitive bidding** mechanism for grid-connected solar PV. Recent rounds:

| Round / batch | Year | MW awarded | Tariff (NPR/kWh) | USD equivalent | Notes |
|---|---|---:|---:|---:|---|
| First utility round | 2016–17 | 24 | 7.30–8.40 | ~$0.065–$0.075 | 5 developers; 3 × COD 2019–20 |
| Bidur / Trishuli NEA EPC | 2020 | 25 | — (NEA self-build) | — | Grid Solar & EE Project |
| IPP rounds (FY 2080/81–2081/82) | 2023–24 | ~170 | 5.94–6.50 | ~$0.044–$0.049 | 8 plants signed PPA |
| 960 MW national tender | 2024–25 | **960** | tariffs in ~5.70–6.20 band (gazette) | ~$0.043–$0.047 | 63 project selections; PPA ongoing |

For comparison, the contracted prices NEA pays for recent **hydropower**:

| Hydro class | Dry-season tariff | Wet-season tariff | Effective blended |
|---|---:|---:|---:|
| RoR (< 25 MW, standard PPA) | 8.40 | 4.80 | ~6.20 |
| PRoR | 9.30 | 5.15 | ~6.80 |
| Storage (large) | variable, ~9.00–12.00 | variable | ~8.00–10.00 |

**The crossover point has already happened for run-of-river.** The NEA is paying ~6.20 NPR/kWh blended for RoR energy whose production profile is **worst-matched** to demand (the [[seasonal-mismatch]] pattern), and ~5.94 NPR/kWh for solar energy whose production profile is **best-matched** to the dry-season day.

This is the single most important number in Nepal's energy economics right now.

## The "locational premium" correction — and why it still favours solar

A fair hydro-vs-solar comparison needs three adjustments:

1. **When does the MWh land?** A dry-season kWh is worth ~2× a monsoon kWh in the Indian import market ([[seasonal-arbitrage-trap]]). Solar lands disproportionately dry-season. Hydro RoR lands disproportionately monsoon. On *time-weighted* value, solar's effective tariff is closer to 5.0 NPR/kWh and RoR's is closer to 7.0 NPR/kWh.
2. **Firm capacity contribution?** Zero for both solar and RoR on their own. Hydro storage earns a real capacity premium that solar-plus-4h-BESS is only partially closing; solar alone does not.
3. **Transmission build-out?** RoR sites are remote; the ~7 new 220/400 kV corridors in [[nepal-transmission-landscape-2025]] are overwhelmingly hydro-driven. Terai solar sits on the *existing* 132 kV spine. Transmission-inclusive LCOE moves solar ~5–10% cheaper still.

After adjustments, **solar LCOE for a Terai utility site with existing 132 kV evacuation is ~NPR 4.5–5.5/kWh (all-in, 25-year levelized)** vs new RoR ~NPR 6.5–8.0/kWh. The solar advantage is ~30–40%.

## Why the price is still falling — and what it means for planning

Three dynamics keep compressing solar costs through 2030:

- **Module oversupply cycle.** Global PV manufacturing capacity (~1,200 GW/yr) is 2–3× annual demand. Prices will not rebound to 2022 levels.
- **Bifacial + tracker penetration.** Now cost-competitive; adds ~10–20% to yield with ~5% capex bump — net LCOE reduction continues.
- **4-hour BESS crossover.** Utility 4-hour battery cost fell from ~$500/kWh (2018) to ~$180/kWh (2024), on pace for ~$90/kWh by 2030. Solar-plus-4h-BESS will clear the NPR 7/kWh bar (matching firm hydro) before 2028.

**Planning implication:** any project with LCOE evaluation at 2023 module prices is over-estimating solar cost by ~20–25%. Any project evaluated without 4h-BESS crossover is about to over-estimate the *firm* solar cost by ~30%.

## What this does not say

- **It does not say Nepal should stop building hydro.** Hydro still has the capacity-credit and seasonal-firm-energy roles solar cannot play alone.
- **It does not say existing PPAs are mispriced in isolation.** A 2017 PPA at 8.40/4.80 is a locked-in contract; tearing them up is not the implication.
- **It does not say solar is a free lunch.** Land, imports (modules are 95%+ Chinese), and interconnection remain real frictions ([[hybrid-siting-logic]], [[agrivoltaics-and-land]]).

What it says is narrower: **on the margin, for the next MW of new capacity to satisfy next winter's peak — solar is now the default answer, and every planning document should default-choose solar unless it has a specific reason (firm capacity, evening peak, location) to choose otherwise.**

## Related

- [[solar-hydro-complementarity]] — why the price argument matters differently in Nepal than elsewhere
- [[data-solar-hydro-lcoe]] — the underlying numbers and time series
- [[hybrid-siting-logic]] — how to compound the price advantage
- [[claim-solar-cheaper-than-small-hydro]] — the tracked claim
- [[seasonal-arbitrage-trap]] — the time-weighted value framing
- [[nea-annual-report-fy2024-25]] — source for Nepal's tariff data
