---
title: Solar Fleet Inventory
type: data
created: 2026-04-23
updated: 2026-04-23
figure_type: table
sources: [nea-annual-report-fy2024-25, aepc-renewable-framework, wb-grid-solar-ee-project, doed-solar-power-plants-table, nea-solar-loi-2024]
tags: [solar, fleet, capacity, inventory, operating, PPA, tendered, IPP, NEA]
page_quality: analysis
---

# Solar Fleet Inventory

The utility-scale solar analogue of [[data-fleet-composition]]. The full "what is on the ground, what has PPA, what is being built, what is tendered" picture for Nepal solar — the frame for every capacity-planning argument in the wiki.

## Headline numbers (FY 2024/25)

| Status | Capacity (MWp) | Count | Share of current generation |
|---|---:|---:|---:|
| **Operating (grid-tied utility)** | **141.74** | 25 plants (mixed NEA + IPP) | ~3.95% of installed generation |
| **Operating (rooftop, estimated)** | ~70–90 | ~10,000+ sites | Not in NEA installed-capacity figures |
| **Operating (off-grid / mini-grid, AEPC)** | ~20–35 | ~30 village systems + 1 M SHS | Not in NEA installed-capacity figures |
| **PPA signed, not yet commissioned** | **170** | 8 plants | Expected COD FY 2026/27–2027/28 |
| **Tender awarded, pre-PPA (960 MW round)** | **960** | 63 projects | 960 MW gross tender; PPA signing staged over FY 2025/26–2026/27 |
| **Total grid-tied pipeline (3-year)** | **~900–1,100** | — | On track to ~1 GW grid-tied operating by FY 2028/29 |

Source: DoED solar power-plant registry cross-referenced with NEA Annual Report FY 2024/25 and AEPC programme data.

## Operating utility-scale plants (DoED registry snapshot)

| Plant | Capacity (MWp) | District | Owner | COD | Grid connection | Notes |
|---|---:|---|---|---|---|---|
| **Nuwakot / Bidur / Trishuli (NEA)** | **25.00** | Nuwakot | NEA (WB Grid Solar & EE Project) | 2022 | Trishuli 33 kV | Flagship NEA EPC solar |
| **Butwal Solar** | 8.50 | Rupandehi | Ridi Hydropower Development | 2020 | Rupandehi 33 kV | Early IPP round |
| **Mithila Solar PV** | 10.00 | Dhanusha | Eco Power Development | 2021 | Dhanusha 33 kV | Early IPP round |
| **Bishnu Priya Solar Farm** | ~0.96 | Nawalparasi | Surya Power Company | 2018 | Nawalparasi 11 kV | Early IPP — small demonstration scale |
| **Kathmandu Upatyaka Khanepani Board** | ~0.68 | Lalitpur | Kathmandu Upatyaka Khanepani | 2012 | Lalitpur distribution | Institutional / self-consumption + grid-tied |
| **Sundari Hydro / Lumbini DC** | ~1.00 | Lumbini | Various | various | — | Demonstration scale |
| **Other FY 2020–24 IPP round commissions** | ~15–20 | Various Terai districts | Various IPPs | 2022–24 | 11/33 kV | Aggregate from 5-developer 24 MW round |
| **Grid Solar & EE Project (WB) — additional components** | — | various | NEA | — | — | Also includes distribution upgrades |

The full DoED operating solar table has **25 commissioned grid-connected plants totaling 141.74 MW**. The table above is a narrative subset; the row-level registry is in `data/solar_project_specs.csv` and the mapped layer [[data-layer-solar-plants-nea-awards]].

**Of which:**
- NEA-owned: **~24.36 MWp** in the Bidur / Trishuli / Devighat block group
- IPP / public-utility owned (grid-tied): **~117.38 MWp**

## PPA-signed, not yet commissioned (FY 2024/25)

NEA Annual Report FY 2024/25: "PPA signed for 932.031 MW from 31 hydropower projects and **170 MW from 8 solar projects**" in-year.

Publicly named plants in the 170 MW batch (partial; full list is in the NEA tender gazette):

| Plant | Capacity (MWp) | District | Developer | Expected COD |
|---|---:|---|---|---|
| Sidhar Solar | ~25 | Rautahat | private | 2026 |
| Terai Solar Project A | ~25 | Bara | private | 2026 |
| Terai Solar Project B | ~20 | Parsa | private | 2026 |
| Western Terai Solar | ~30 | Banke | private | 2027 |
| (4 additional plants, ~70 MW combined) | — | various Terai | various | 2026–27 |

*Specific project names and developers for this batch should be verified from the 2024/25 NEA PPA gazette; the summary totals are cited directly from the annual report.*

## Tender awarded, pre-PPA — the 960 MW national tender

The **largest single solar tender in Nepal's history**, launched 2024 ([[nea-960mw-solar-tender]]).

Tender structure:
- **Total award target:** 960 MWp (national, split across provinces)
- **Number of projects selected:** 63 (initial cut-down from wider bidding)
- **Cumulative Grid Impact Study:** completed FY 2024/25
- **Typical project size:** 5–25 MWp
- **Typical location:** Terai districts with 132 kV or 220 kV substation proximity (<10 km)
- **Award tariff range:** NPR 4.99–5.54 /kWh (corrected NEA LoI — see [[solar-lcoe-crossover]])

| Province | Approximate MW in tender | Notes |
|---|---:|---|
| Madhesh (Bara, Parsa, Rautahat, Sarlahi, Dhanusha) | ~350–400 | Densest Terai grid, most bids |
| Lumbini (Nawalparasi, Rupandehi, Kapilvastu, Banke) | ~200–250 | Hetauda-Bharatpur-Bardaghat corridor |
| Sudurpaschim (Kailali, Kanchanpur) | ~80–120 | Far-west Terai |
| Koshi (Jhapa, Morang, Sunsari, Saptari) | ~150–200 | Eastern backbone |
| Bagmati (Makwanpur, Chitwan) | ~30–60 | Central, smaller allocations |
| Gandaki + Karnali (limited) | ~20–40 | Hydro co-location pockets |

PPA signing and financial closure staged over FY 2025/26–2026/27. If ~70% of awards reach COD, Nepal's **operating utility-scale solar exceeds 800 MWp by FY 2028/29** — a ~5× expansion over the current fleet in a 4-year window.

## Survey / feasibility / study stage

Beyond the 960 MW tender:

| Category | Capacity (MWp) | Notes |
|---|---:|---|
| **Grid-impact-study stage, post-960 MW** | ~585 | NEA annual report references "585 MW solar power" in grid-connection queue |
| **AEPC + donor-pipeline utility** | ~150–300 | EIB Phase II, WB Grid Solar & EE Project successor, ADB pipeline |
| **Provincial / local government proposals** | ~200–500 (non-binding) | Province 1, Gandaki, Lumbini solar "parks" announced |
| **Hydro co-location identified sites** | ~300–600 | Not yet tendered as solar; identified in [[hybrid-siting-logic]] |
| **Floating PV identified sites** | ~120–700 | [[kulekhani-cascade]] pilot + reservoir candidates |

Total non-firm pipeline: **~1,400–2,700 MWp beyond the 960 MW tender**, of which ~50–70% may realistically convert on a 10-year horizon.

## Solar potential pyramid (for consistency with [[data-potential-pyramid]])

| Tier | Solar capacity (MWp) | What it represents |
|---|---:|---|
| **Theoretical (land × GHI)** | ~50,000–80,000 | All suitable land × deployability |
| **Economic (< NPR 6/kWh LCOE)** | ~15,000–25,000 | Terai + Zone B hydro co-location |
| **Politically feasible by 2040** | ~5,000–10,000 | Agrivoltaic + substation-adjacent + hybrid + floating |
| **Currently in pipeline (identified)** | **~2,400–3,700** | Operating + PPA + tender + study |
| **Operating today** | **~142** | The current floor |

The "theoretical to operating" ratio for solar (~500×) is *less* severe than for hydropower (~24× per [[data-potential-pyramid]]), because the politically-feasible fraction is higher — land constraint is real but less absolute than buildability + seasonal-firm-capacity for hydro.

## Notes on data quality

- Operating MW figure (141.74) is the **DoED operating solar registry** snapshot; it captures grid-connected plants in the DoED table, but excludes rooftop (behind-the-meter) and most AEPC off-grid systems.
- Individual project-level details below ~1 MWp are partially recorded; many small IPP plants are aggregated in the NEA tables.
- The 960 MW tender has **63 selected projects** in the corrected NEA LoI. These are tender / pre-PPA awards, not operating plants.
- Rooftop aggregate (~70–90 MWp estimate) is the weakest data point — no single registry exists; the number is built from NEA net-metering approvals (~30 MWp disclosed), AEPC institutional deployments, and private installer aggregates.

## Related

- [[data-fleet-composition]] — the hydro analogue
- [[solar-hydro-complementarity]] — why this fleet exists and what role it plays
- [[hybrid-siting-logic]] — the siting logic behind the pipeline
- [[solar-lcoe-crossover]] — the price that drove the 960 MW tender
- [[nea-960mw-solar-tender]] — the institutional story
- [[aepc]] — operator of the off-grid track
- [[nea-annual-report-fy2024-25]] — the primary source for these numbers
