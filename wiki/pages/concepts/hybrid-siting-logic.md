---
title: Hybrid Siting Logic
type: concept
created: 2026-04-23
updated: 2026-04-23
sources: [nea-annual-report-fy2024-25, wb-grid-solar-ee-project]
tags: [solar, siting, hybrid, floating-pv, co-location, substation, hydro, kulekhani]
---

# Hybrid Siting Logic

Solar plants are not free-floating technology choices; they are three things co-located — **a module field**, **a land parcel**, and **an interconnection**. Cheap modules have collapsed the first; [[solar-lcoe-crossover]]. Land and interconnection are now the binding constraints on Nepal solar, and the siting archetypes that minimise *those* two costs beat the ones that optimise GHI alone.

This page frames the three siting archetypes — **hydro co-location**, **substation-adjacent greenfield**, **floating PV on reservoirs** — and argues that the first and third together will carry most of the political coalition for utility-scale solar in Nepal through 2035.

## Archetype 1 — Solar at existing hydropower sites ("hydro co-location")

The cheapest MW Nepal can build, in the specific sense that almost every non-module cost is already paid.

**What's already there at a typical operating hydropower site:**

- An access road (often 3–15 km of graded mountain road, the single most expensive item in hill-country solar).
- An interconnecting substation (11/33 → 132/220 kV).
- Spare evacuation headroom, **especially** in dry season when the hydro plant runs at 30–40% of monsoon output and the transformer / line is underused.
- A skilled O&M crew, security, and a fenced site.
- Water for panel cleaning.
- Permitting precedent with NEA, local government, forest department, and the community.

**What the solar build adds:**

- 1–10 MWp of PV modules (1–8 ha of dry / desilted terrain adjacent to the powerhouse or along the headrace road).
- A combiner box, inverters, and a tap into the existing step-up transformer.
- ~NPR 40–60 million per MWp installed (vs ~NPR 70–90 million for greenfield) — a **35–40% capex reduction** from land, road, and interconnection savings.

**Why it is also operationally elegant:**

The interconnection loading pattern is *anti-phased* with the hydro plant. In the dry-season afternoon, the hydropower plant under-utilizes its evacuation; the solar PV fills the spare capacity of the same substation. In the monsoon-day overlap, dispatch holds hydro pondage through midday and releases it in the evening peak (see [[solar-hydro-complementarity]]). Net transformer capacity utilization goes up, not down.

**Candidate sites with published feasibility or public tender interest:**

- [[kulekhani-cascade]] — reservoir + three cascade plants; ~10–20 MWp ground + ~15–30 MWp floating potential.
- [[kali-gandaki-a]] — 144 MW NEA flagship; dam-adjacent flats suited to 25–40 MWp ground PV.
- [[khimti-i]] — 60 MW IPP; headrace-adjacent terraces, 10–15 MWp candidate.
- [[marsyangdi]] / [[madhya-marsyangdi]] — cascade co-location, 20–40 MWp combined.
- [[tanahu-hydropower]] — storage reservoir under construction; co-location should be designed in *before* impoundment.

The 50 MW solar project at **Khungri village**, designed to integrate into the Khungri substation adjacent to Madi Khola and Lungri Khola hydropower, is the first operational example of the archetype at scale in Nepal (NEA annual report FY 2024/25).

## Archetype 2 — Substation-adjacent greenfield (Terai)

The 960 MW NEA tender ([[nea-960mw-solar-tender]]) and the next 2–3 GW of utility-scale solar will overwhelmingly be this archetype: **10–50 MWp ground-mount, 1–8 km from an existing 132 or 220 kV substation, on the Terai plain.**

**Why it works:**

- Highest 132 kV grid density in the country ([[hetauda-dhalkebar-inaruwa-backbone]], [[dana-kushma-butwal-corridor]]).
- Flat terrain (<3° slope), lowest construction cost in Nepal.
- Proximity to load centres and to Indian-grid interconnections for future export.
- Water for panel cleaning (Terai is canal-irrigated).

**Why it is politically fragile:**

- Terai is Nepal's prime agricultural land; fee-simple conversion to solar triggers food-security objections ([[agrivoltaics-and-land]]).
- Land acquisition — even at 2–5 ha per site — collides with fragmented tenure, smallholder resistance, and the memory of hydropower-era displacement.
- Non-agricultural alienable land (government-owned *sarkari* parcels, dried-out oxbows, public waste) is scarce and over-subscribed.

**The design move that makes it durable:** do not buy land. **Lease** for 25 years with a revenue-share clause, anchor on agrivoltaic configuration, and bundle rural-electrification / pump-irrigation offtake into the PPA. The 960 MW tender is experimenting with variants of this; the next decade of Terai solar depends on whether that politics stabilises.

## Archetype 3 — Floating PV on reservoirs

The highest-leverage single lever in Nepal's solar portfolio, by an uncomfortable margin.

**What floating PV buys that ground-mount does not:**

- **No land acquisition** — the reservoir exists; deploying on ~5–20% of its surface takes nothing out of agricultural rotation.
- **Cooler panel operating temperature** — ~2–5% yield uplift from evaporative cooling.
- **Reduced reservoir evaporation** — 30–50% evaporation reduction on covered surface; in a country with [[storage-deficit]] and a dry-season water-tight operating regime, this is not a side benefit, it is a water-system benefit sold separately.
- **Shared interconnection** — dam powerhouse already carries the 11/33 kV step-up and the substation. Floating PV taps in at the tail.
- **Anti-algae** — covered water bodies see fewer blooms; Kulekhani in particular has had sedimentation / eutrophication concerns that floating PV partially mitigates.

**Candidate reservoirs:**

| Reservoir | Surface (ha) | 10% coverage (ha) | Nameplate (MWp) | Status |
|---|---:|---:|---:|---|
| [[kulekhani-cascade]] | ~220 | 22 | **~17 MWp** | Operating; pilot-ready |
| [[tanahu-hydropower]] | ~700 | 70 | **~56 MWp** | Under construction; **design in now** |
| [[budhigandaki]] | ~6,300 | 630 | **~500 MWp** | Proposed; 10+ year horizon |
| [[dudhkoshi-storage]] | ~1,800 | 180 | **~144 MWp** | Proposed |
| [[mugu-karnali-storage]] | ~9,000 | 900 | **~720 MWp** | Proposed |
| [[uttarganga-storage]] | ~2,400 | 240 | **~192 MWp** | Proposed |

Even at conservative 5% coverage and discounting the long-dated projects, the near-term-buildable floating PV at Kulekhani + Tanahu is ~70–90 MWp — more than the entire operating utility-scale solar fleet as of FY 2024/25. The design move that matters most: **require floating-PV integration in the tender documents for every new reservoir project, starting with Tanahu.** Retrofitting is ~2× more expensive than designing it in.

## The siting-cost stack, one table

| Archetype | Land cost | Grid cost | GHI (typical) | LCOE index (Terai greenfield = 100) |
|---|---|---|---|---:|
| Hydro co-location | **0 (already owned)** | **0 (spare headroom)** | 4.5–5.5 | **60–70** |
| Substation-adjacent Terai | 15–25 | 5–10 | 4.8–5.3 | 100 |
| Floating PV | **0** | **low** | 4.5–5.5 | **75–85** |
| Trans-Himalayan (Mustang) | low | **very high** | 6.0–6.5 | 180–250 |
| Rooftop (Kathmandu Valley) | 0 (existing) | net-metering | 4.2–4.6 | **90–110** |
| Hill greenfield | 10–20 | 30–60 | 4.3–4.8 | 140–180 |

Grid cost is the single widest column. In a country with [[stranded-generation]] as a current, real constraint, archetypes that **spend zero new transmission** (hydro co-location, floating PV, rooftop) are worth their ~5% higher module-side costs many times over.

## The portfolio rule

Over 2026–2035, roughly:

- **~60% of solar MW** should be substation-adjacent Terai greenfield (Archetype 2), with ~70% of that as agrivoltaics.
- **~20%** as hydro co-location (Archetype 1), increasingly standard in the next NEA tender batches.
- **~10%** as floating PV on Kulekhani, Tanahu, and the earliest-operating reservoir sites (Archetype 3), scaling to more as reservoirs commission.
- **~10%** as rooftop / distributed + off-grid mini-grids (see [[rooftop-minigrid-offgrid]]), which is a separate political track.

This is the sort of portfolio a competent NEA + ERC could produce in a 10-year plan. Nothing in the 2024/25 annual report refutes it; the infrastructure for all four archetypes is under way. The missing piece is an explicit portfolio rule that treats the four archetypes as complements rather than competitors.

## Related

- [[solar-hydro-complementarity]] — why these sites are valuable
- [[solar-resource-geography-nepal]] — which zones suit which archetype
- [[solar-lcoe-crossover]] — the price argument each archetype compounds
- [[agrivoltaics-and-land]] — the political condition for Archetype 2
- [[rooftop-minigrid-offgrid]] — the fourth archetype, treated separately
- [[kulekhani-cascade]], [[tanahu-hydropower]], [[budhigandaki]], [[dudhkoshi-storage]] — floating PV candidates
- [[nea-960mw-solar-tender]] — the first portfolio-scale test of Archetype 2
