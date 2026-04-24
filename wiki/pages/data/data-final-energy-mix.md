---
title: Nepal Final Energy Mix
type: data
created: 2026-04-23
updated: 2026-04-24
figure_type: chart-spec
sources: [wecs-energy-synopsis-2024]
tags: [energy-balance, final-energy, biomass, petroleum, coal, electricity, sectoral, nepal]
---

# Nepal Final Energy Mix

The full fuel × sector matrix of Nepal's final energy consumption, straight from the WECS Energy Sector Synopsis 2024 (FY 2079/80). This is the page that answers "how much of Nepal's total energy is actually hydro?" with a number other than the one everyone quotes. It is the denominator for every serious claim in [[master-thesis]] and [[domestic-led-hydro-strategy]].

## Headline numbers (FY 2079/80 / ~2022–23)

| Metric | Value |
|--------|-------|
| Total final energy consumption | **532.42 PJ** (532,420 TJ) |
| Year-on-year change | **−16.81%** vs FY 2078/79 (640 PJ) |
| Traditional biomass share | **63.87%** (340.04 PJ) |
| Commercial fuel share (excl. electricity) | **25.80%** (137.38 PJ) |
| Grid electricity share | **7.23%** (38.49 PJ) |
| Modern renewable share | **3.10%** (16.50 PJ) |
| **Hydro share of total final energy** | **~6.8%** (electricity × 94.4% hydro) |

> [!note] Correction to older wiki pages
> Earlier pages ([[nepal-energy-profile]], [[data-domestic-demand]], [[domestic-led-hydro-strategy]]) cite grid electricity as **4.96%** of final energy. That figure was carried over from the earlier 2020/21 balance quoted in explanatory prose. The official FY 2079/80 figure is **7.23%**. Both are internally consistent with their respective years; the jump reflects genuine electrification (+21.18% electricity consumption YoY) combined with a drop in coal (−41.5%) and petroleum (−16.1%).

## Axis 1 — Consumption by source

| Source | TJ | Share | Category |
|--------|------:|------:|----------|
| Fuelwood | 304,625 | **57.22%** | Traditional biomass |
| Diesel | 49,728 | 9.34% | Petroleum |
| Grid electricity | 38,490 | **7.23%** | Commercial |
| Coal | 34,016 | 6.39% | Commercial |
| Agricultural residue (incl. bagasse) | 25,623 | 4.81% | Traditional biomass |
| LPG | 23,677 | 4.45% | Petroleum (imported) |
| Petrol | 21,932 | 4.12% | Petroleum |
| Biogas | 10,722 | 2.01% | Modern renewable |
| Animal dung | 9,791 | 1.84% | Traditional biomass |
| ATF (jet fuel) | 6,191 | 1.16% | Petroleum |
| Other petroleum (furnace oil, kerosene) | ~1,840 | 0.35% | Petroleum |
| Modern renewable non-biogas (solar, micro-hydro, wind) | ~5,800 | 1.09% | Modern renewable |
| **Total** | **532,420** | **100%** | |

## Axis 2 — Consumption by sector × fuel (TJ)

Decoded from WECS 2024 Table 4 / Chapter 4.2.2 cross-tab. All rows sum to within rounding of the published sector totals.

| Sector | Fuelwood | Ag res | Dung | Petrol | Diesel | Kero | LPG | ATF | Coal | Electricity | Biogas | Solar/µhydro/wind | **Total** | Share |
|--------|------:|------:|------:|------:|------:|------:|------:|------:|------:|------:|------:|------:|------:|------:|
| Residential | 257,226 | 8,909 | 9,486 | 0 | 111 | 0 | 18,174 | 0 | 35 | 16,139 | 10,714 | 2,669 | **323,463** | **60.75%** |
| Industrial | 31,894 | 16,337 | 0 | 2,502 | 11,646 | 296 | 765 | 0 | **33,622** | 12,874 | 0 | 0 | **111,306** | **20.91%** |
| Transportation | 0 | 0 | 0 | 18,862 | 30,473 | 2 | 2 | **6,191** | 0 | 25 | 0 | 0 | **55,553** | **10.43%** |
| Commercial | 15,414 | 377 | 305 | 175 | 0 | 47 | 4,413 | 0 | 359 | 2,653 | 9 | 3,082 | **26,835** | 5.04% |
| Construction/Mining | 91 | 0 | 0 | 331 | 3,789 | 18 | 322 | 0 | 0 | 5,670 | 0 | 0 | **10,222** | 1.92% |
| Agriculture | 0 | 0 | 0 | 61 | 3,819 | 0 | 0 | 0 | 0 | 1,134 | 0 | 26 | **5,040** | 0.95% |
| **Total** | **304,625** | **25,623** | **9,791** | **21,932** | **49,728** | **363** | **23,676** | **6,191** | **34,016** | **38,495** | **10,723** | **5,777** | **532,420** | **100%** |

("Other petroleum" — furnace oil (1,369 TJ in industry) and kerosene totals — is folded into the petroleum columns above; small residual rounding is in the totals row.)

## The five structural facts in this table

### 1. Fuelwood in household cooking is the single biggest energy flow in the country

**257,226 TJ** of fuelwood burned in residential use is **48.3% of all final energy consumed in Nepal**. Not industry, not transport. Kitchens. See [[data-domestic-demand]] for the companion "<1% of households cook with electricity" fact — together these two numbers are the central feature of Nepal's energy system, not a footnote.

### 2. Industry is 21%, but it's not factories — it's bricks, cement, and steel rerolling

Inside the 111.3 PJ industrial sector:
- **Coal 33.6 PJ (30.2%)** — this is **~99% of all coal consumed in Nepal**, almost entirely brick kilns (fixed-chimney Bull's-trench type, ~1,500+ operating), cement clinker, and iron/steel rerolling.
- **Biomass 48.2 PJ (43.3%)** — fuelwood + bagasse. Long tail of small plants: tea dryers, sugar mills, cardamom dryers, food processing, textiles.
- **Petroleum 16.6 PJ (14.9%)** — diesel gensets (captive power), process heat. A direct reliability cost of the grid, linked to [[stranded-generation]].
- **Electricity 12.9 PJ (11.6%)** — the grid touches only ~12% of industrial energy. Electrification of industry is largely still ahead of Nepal.

Industry is bigger than a casual reader expects precisely because Nepal's energy statistics classify brick kilns and a long tail of small biomass-fed plants as "industrial." Few of them are large factories in the modern sense.

### 3. Transport is 10.4%, and it is essentially 100% imported fossil

**55,528 TJ petroleum vs 25 TJ electricity** in transport. Split inside petroleum:
- Diesel 54.9% (trucks, buses, tractors)
- Petrol 34.0% (motorcycles, cars)
- ATF 11.1% (aviation — all of Nepal's aviation fuel, 6,191 TJ)
- Electricity 0.05% (trolley bus + statistical noise of early EVs)

Transport is **~10% of energy volume** but close to **40–50% of the foreign-exchange cost** of Nepal's energy system, because every drop is imported from India via the Motihari–Amlekhgunj pipeline (operational 2019) plus road tankers.

### 4. Electricity is where Nepal's sector-mix hides a surprise

Electricity shares within each sector:

| Sector | Electricity as % of sector energy |
|--------|------:|
| Construction/Mining | **55.5%** — stone crushers, quarries, cement grinding |
| Agriculture | 22.5% — tubewells, some pumping |
| Industrial | 11.6% |
| Commercial | 9.9% |
| Residential | 5.0% |
| Transportation | 0.05% |

Construction/mining is the only sector in Nepal that is *already* majority-electric. Residential (the biggest sector) is only 5% electric because wood still does the cooking and heating. See [[energy-substitution-pathway]] for the implications.

### 5. The "hydro share" of Nepal's total energy

Hydro is **94.4%** of installed electricity capacity (see [[nepal-energy-profile]], [[data-fleet-composition]]). Electricity is **7.23%** of final energy. So:

**Hydro ≈ 6.8% of Nepal's final energy.** Solar PV (~0.6%), biogas (2.0%), and micro-hydro (~0.4%) add ~3% more. The other ~90% of Nepal's final energy is still biomass + fossil.

This number collapses the "Nepal is a hydropower country" frame into something more honest: Nepal has a hydropower *electricity* system. Its total energy system is still a biomass-and-petroleum system with an electric overlay that is growing fast but starts from ~7%.

The solar section should be read against this denominator. Today's solar fleet is too small to move final-energy shares by itself, but its marginal value is high because it lands in the binding season and can be built faster than large hydro. [[solar-in-the-master-narrative]] is therefore not a claim that solar dominates Nepal's energy balance; it is a claim that solar changes the next marginal investment decision.

## Historical trajectory

| Year | Total (PJ) | Fuelwood share | Electricity share | Source |
|------|------:|------:|------:|--------|
| 2008/09 | 401 | 77.7% | <2% (elec+coal=4%) | WECS 2010 synopsis |
| 2019 | 589 | 62.0% | 3.9% | WECS historical series |
| 2020 | 566 | 64.9% | 4.1% | WECS |
| 2021 | 626 | 60.4% | ~4.2% | WECS |
| 2021/22 | 640 | ~60% | 4.96% | WECS (quoted on earlier wiki pages) |
| **2022/23 (FY 2079/80)** | **532** | **57.22%** | **7.23%** | [[wecs-energy-synopsis-2024]] |

The 16.81% drop in total consumption in FY 2079/80 vs FY 2078/79 is striking. WECS attributes it primarily to sharp declines in coal (−41.5%) and petroleum (−16.1%) imports, partially offset by electricity growth (+21.2%). Whether this reflects genuine substitution or one-off import-compression from 2022's FX crisis is a forward-research question — the FY 2080/81 balance will tell us.

## Chart Specification

Three panels, built for the video essay:

1. **Sankey** — sources → sectors, widths in TJ. The single fattest stream is "Fuelwood → Residential" (257 PJ). "Coal → Industrial" (33.6 PJ) and "Diesel → Transportation" (30.5 PJ) are the next two fattest. Hydro/electricity threads are visually thin across the whole diagram. This is the single most powerful image for the essay's pivot from "hydro story" to "energy story."
2. **Stacked 100% bar per sector** — show that residential is dominated by biomass, industrial by coal+biomass, transport by petroleum, while only construction/mining and (to a lesser extent) agriculture are electricity-majority.
3. **Time-series** — total PJ and electricity share, 2009 → 2023, showing the ~5x slow rise of electricity share against nearly flat fuelwood share.

## Linked Source

- [[wecs-energy-synopsis-2024]] — full report; cross-tab is in Chapter 4.2.2 and Appendix Table 4.

## Related

- [[energy-substitution-pathway]] — the "three sinks to displace" strategic read of this table
- [[nepal-energy-profile]] — country-level snapshot of the electricity system
- [[data-domestic-demand]] — sectoral electricity sales and the electric-cooking gap
- [[data-fleet-composition]] — what's inside that 7.23% electricity slice
- [[domestic-led-hydro-strategy]] — the strategic implication: displace biomass + fossil with hydro-electric loads
- [[green-hydrogen-nepal]] — one of the few paths to displace industrial coal (brick kilns, cement)
- [[solar-in-the-master-narrative]] — why a small current share can still matter at the margin
- [[master-thesis]] — the denominator this table provides
