---
title: Domestic Electricity Demand Distribution
type: data
created: 2026-04-14
updated: 2026-04-15
figure_type: chart-spec
sources: [nea-annual-report-fy2024-25, wecs-energy-synopsis-2024]
tags: [demand, consumption, residential, industrial, load-profile, nepal]
---

# Domestic Electricity Demand Distribution

Where Nepal's electricity actually goes — by sector, by time of day, and by how far the country is from its own potential demand. Central evidence for [[domestic-led-hydro-strategy]] and the [[seasonal-arbitrage-trap]] value-capture argument.

## Sectoral Demand Split (FY 2020/21)

Source: NEA Distribution and Consumer Services Directorate (total energy sales ~7,277 GWh).

| Sector | Share of Sales | GWh (approx.) |
|--------|---------------|---------------|
| Domestic (residential) | **43.05%** | ~3,138 |
| Industrial | **38.69%** | ~2,816 |
| Commercial | 7.02% | ~511 |
| Non-commercial | 2.80% | ~204 |
| Others (water supply, irrigation, etc.) | 8.44% | ~614 |

> [!finding] Industry is nearly as large as residential
> Industrial customers are a tiny fraction of total consumer count yet consume ~39% of electricity sold — almost as much as all households combined. This makes industry the highest-leverage demand lever: winning or losing a few large industrial users has an outsized system effect.

## Total System Energy Balance (FY 2020/21)

| Metric | Value |
|--------|-------|
| Total consumption | 7,319 GWh |
| NEA own generation share | 31.66% |
| IPP generation share | 36.51% |
| **Imports from India share** | **31.83%** |
| System loss | **17.18%** (up from 15.27% prior year) |

> [!warning] Imports were one-third of supply in FY 2020/21
> Even in a "hydropower country," Nepal was importing nearly as much as it generated itself. By FY 2024/25, this has shifted substantially (net exporter), but the FY 2020/21 baseline reveals how recent and fragile the net-export status is.

System loss has since improved to ~13.46% (FY 2024/25) — a meaningful gain, but every percentage point of loss still means more purchased or generated energy is required for the same delivered kWh, and imported energy is partially "lost" before reaching paying load.

> [!note]
> The merged workspaces surface two adjacent but different system-loss figures: **~13.46%** in NEA FY 2024/25 reporting and **~12.7%** in a 2024 World Bank / report-style framing. Keep the fiscal year and source attached; they are not interchangeable.

## Load Profile: Evening Peak Dominates

Monthly operational reports show peak demand consistently hitting around **18:30–19:25** — the daily cooking-and-lighting window. This is not a quirk; it is structural:

- Run-of-river hydro generates throughout the day at near-constant output (flow-following)
- Demand spikes in the evening when people return home
- The mismatch is most acute in **dry-season evenings**, when hydro output is at its annual floor and demand is at its daily peak

Specific data points from operational reports:
- **Baisakh 2080**: peak times cluster around **19:00–19:25**
- **Falgun 2080** (mid-Feb to mid-Mar 2024): peak time repeatedly **18:30–18:55**; monthly maximum import-at-peak **643 MW** in a single day

This evening peak pattern is why Nepal needs import approval for hundreds of MW in winter: its fleet cannot shift generation within the day (no pumped storage, limited pondage), so it relies on cross-border imports to cover the evening spike precisely when domestic output is weakest.

## The Electrification Gaps — Where Demand Is Not Yet Created

### Electric cooking: the largest untapped demand

- Electric cooking used by **less than ~1% of households** in Nepal
- Biomass (firewood, dung) and **imported LPG** dominate cooking energy
- This is not a preference story — it is a reliability and appliance-access story

The strategic implication: if Nepal could shift even 20–30% of cooking to electricity, it would create a large, distributed, flexible domestic load that could absorb monsoon surplus, reduce LPG import bills, and provide a new economic case for rural electrification investment.

### Per-capita consumption gap

- Nepal's per-capita electricity use: **370–465 kWh/year**
- Global middle-income average: ~2,000–3,000 kWh/year
- Nepal's hydropower potential per capita: **~29,400 kWh/year** (theoretical)

The ratio between potential and actual is ~277:1. Even the gap between actual use and middle-income norms is ~5–7x. This headroom is not a failure — it is the demand-creation opportunity that makes the [[domestic-led-hydro-strategy]] viable over a 20-year horizon.

## Value-Capture Framing

Electricity "captures value" when:
1. It sells scarce kWh at high value (dry-season firm power, peak hours)
2. It buys deficit kWh at low cost (off-peak imports when available)
3. It uses the bulk of output domestically in **high-productivity activities**

Nepal currently does (1) partially (improving IEX spreads) and (2) inadequately (structurally forced to buy peak-hour winter imports). On (3) — the domestic transformation pathway — the electric cooking statistic captures the scale of the gap: Nepal's biggest potential demand creator is barely tapped.

The deepest value-capture move is not better export contracts. It is **electrifying cooking, industrial heat, and transport** at scale — turning Nepal from a seasonal kWh exporter into a country where electricity is the backbone of economic productivity.

## Linked Data

- [nea_monthly_energy_balance_fy2024_2025.csv](../../../data/processed/tables/nea_monthly_energy_balance_fy2024_2025.csv) — monthly demand, imports, storage generation, and supply composition.
- [nea_monthly_capacity_balance_fy2024_2025.csv](../../../data/processed/tables/nea_monthly_capacity_balance_fy2024_2025.csv) — monthly capacity-side view of imports, storage MW, and peak demand.

## Measurement Notes

- **Household electrification:** the wiki uses **91.41%** when discussing metered household connections from NEA.
- **Broader access indicator:** some report prose rounds electricity access to **~95%**. That is a wider access/service indicator, not the same thing as metered household electrification.

## Chart Specification

Pie chart: sectoral demand split (residential / industrial / commercial / other).
Second panel: bar chart comparing Nepal per-capita consumption (~420 kWh) vs regional peers and global middle-income average, on same axis as theoretical potential — the visual gap is the argument.
Third panel: load profile curve (daily MW demand, showing 18:30–19:25 evening peak vs hydro's flat-ish RoR output) — highlight the mismatch window.

## Related

- [[seasonal-arbitrage-trap]] — the trade cost of not building domestic demand
- [[domestic-led-hydro-strategy]] — the strategic response
- [[stranded-generation]] — monsoon surplus that domestic load could absorb
- [[nea]] — the utility that must enable this demand growth
- [[green-hydrogen-nepal]] — industrial-scale demand creation from surplus
