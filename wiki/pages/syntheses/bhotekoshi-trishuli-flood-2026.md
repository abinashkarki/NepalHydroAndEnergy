---
title: Bhotekoshi–Trishuli Flood 2026
type: synthesis
created: 2026-08-30
updated: 2026-08-30
sources: [kathmandupost-bhotekoshi-flood-hydropower-damage-2026, kathmandupost-bhotekoshi-flood-tunnel-rescues-2026, kathmandupost-bhotekoshi-flood-barrier-lake-2026, kathmandupost-bhotekoshi-flood-sitrep-ndrrma-2026, reuters-bhotekoshi-flood-climate-attribution-2026]
tags: [bhotekoshi, trishuli, rasuwa, nuwakot, dhading, chitwan, flood-2026, hazards, GLOF, transboundary, corridor, developing-event]
page_quality: brief
---

# Bhotekoshi–Trishuli Flood 2026

**Status: developing event.** This page records the 26 August 2026 flood while rescue operations and damage assessment are still under way. Every figure carries an as-of date of **30 August 2026** unless stated otherwise, and every damage classification carries an explicit confidence tier. Preliminary numbers here *will* be revised by official assessments; the register behind the map layers (`data/flood_2026_08_impact_register.csv`) is the artifact that gets updated, and this page tracks it.

## The Event

On the morning of **26 August 2026**, a massive ice-rock avalanche from the northern slopes of **Langtang Lirung** entered the Lhende Khola on the Tibetan side, initiating a multi-stage hazard chain that crossed the border into Nepal as the **Bhote Koshi (Rasuwa)** and ran the full **Trishuli–Narayani** system to the Indian border. Expert attribution at the one-week mark is probabilistic — climate-driven destabilisation of high-mountain rock and ice is a risk conditioner, not a proven sole trigger; heavy snow melt coupled with seismic activity is cited as a probable trigger combination. See [[reuters-bhotekoshi-flood-climate-attribution-2026]].

The human toll as of 30 August (NDRRMA update): **734 dead, 2,498 missing** — including 933 people linked to hydropower projects — with 8,186 rescued. See [[kathmandupost-bhotekoshi-flood-sitrep-ndrrma-2026]].

## Flood Route

The route below is reconstructed from reported locations, NDRRMA district-level body-recovery geography, confirmed damage points, and HydroRIVERS linework. Tibet-side and border reaches are approximate hand alignment; the Rasuwa valley alignment is anchored on confirmed damage points; downstream reaches follow the Trishuli and Narayani lines in the map data. The explorer preset **Flood 2026** renders each reach with its own alignment confidence.

```text
Langtang Lirung avalanche → Lhende Khola (Tibet) → Gyirong Port → Rasuwagadhi border
  → Rasuwagadhi plant (destroyed) → Rasuwa Bhotekoshi site → Timure → Syabrubesi
  → Trishuli: Dhunche → Betrawati → Upper Trishuli-1 / 3A / 3B → Devighat–Bidur
  → Mugling (Marsyangdi confluence) → Narayani → Narayanghat → Chitwan → Nawalparasi → India border
```

Downstream evidence: bodies recovered in Chitwan (259), Nawalparasi East (184) and West (82) — roughly 250 km from the source — and expert-cited channel changes more than 100 km downstream. This is a full-trunk flood, not a valley-localised flash event.

## Hydropower Impact — Confidence-Tiered

Roughly **430 MW** was knocked out across 14–15 corridor projects per NEA's acting managing director — over 12 percent of national installed capacity. The register distinguishes what is *confirmed*, what is *watched*, and what is *geometrically exposed but unconfirmed*:

### Tier 1 — Confirmed (official or named-source)

| Project | Capacity | Status | Source tier |
|---|---|---|---|
| Rasuwagadhi | 111 MW | Completely washed away | NEA spokesperson; KOEN reports 90% facility loss |
| Chilime | 22 MW | Buried; tunnel mud-filled, powerhouse damaged | NEA + company executive director |
| Upper Trishuli 3A | 60 MW | Workers trapped in underground powerhouse; cable tunnel entrance buried | Ministry of Energy + NEA |
| Upper Trishuli 3B | 37 MW | Site completely buried, "effectively turned into a riverbed" | Developer statement |
| Upper Trishuli-1 | 216 MW | Damaged; 254 rescued from site | Army rescue + NEA list |
| Trishuli (NEA) | 24 MW | Damaged | NEA/IPPAN list |
| Devighat | 14.1 MW | Damaged | NEA/IPPAN list |
| Mailung Khola | 5 MW | Damaged | NEA/IPPAN list |
| Upper Mailung Khola | 14.3 MW | Damaged | NEA/IPPAN list |
| Upper Mailung A | 6.42 MW | Damaged (under construction) | NEA/IPPAN list |
| Langtang Khola | 20 MW (testing) | Damaged; helicopter-only access | Company + Army |
| Rasuwagadhi Bhotekoshi | 120 MW | Damaged (under construction) | NEA/IPPAN list |
| Bidur / Trishuli solar | 25 MWp | Substation inundated | Ministry of Energy imagery |
| Middle Trishuli Ganga | 15.6 MW | Damaged (under construction) | NEA/IPPAN list; no registry geometry |

### Tier 2 — Watch (indirect signals, no project statement)

Sanjen (42.5 MW), Upper Sanjen (14.8 MW), Sanjen Khola (78 MW) and Trishuli Galchhi (75 MW) — corridor location plus NEPSE share declines of 9–13 percent in their operators' stocks. Market signals are exposure evidence, not damage evidence.

### Tier 3 — Corridor exposure (geometric, unconfirmed)

21 registry projects fall within 3 km of the reconstructed route, including downstream Narayani plants (Rigdi Khola in Chitwan, Gandak in Nawalparasi West, Kalika Kaligandaki in Nawalparasi East) that the named-project lists never mention — the map layer classifies them so that verification can be targeted rather than anecdotal.

### Critical disambiguation

Two different rivers in Nepal are called Bhote Koshi. The flooded one is the Rasuwa Bhote Koshi (Lende), upper tributary of the Trishuli in the **Gandaki** system. The **Sindhupalchok** Bhote Koshi (Chaku, Upper Bhotekoshi 45 MW, Madhya Bhotekoshi 102 MW) is a separate **Koshi**-system river roughly 60 km east and was **not** flooded. Registry points tagged "Bhotekoshi" in Sindhupalchok are correctly excluded from the flood layers. This distinction matters: some of our own registry records carry the same ambiguity — see the Rasuwagadhi river-basin correction noted below.

## Secondary Hazard — The Barrier Lake

A landslide-dam **barrier lake** formed near the Chhochen Khola–Purepu Tsangpo confluence upstream of the border crossing: ~2 million cubic metres on 27 August, already overflowing, with another 3 million cubic metres forecast and a high breach risk per China's Ministry of Water Resources. A breach would re-flood the exact corridor documented above. The Purepu system is the same glacier area that produced the **8 July 2025** supraglacial-lake flood recorded in [[ndrrma-rasuwa-glacial-flood-sitrep-2025]] — and the corridor also took heavy damage in the September 2024 floods. See [[kathmandupost-bhotekoshi-flood-barrier-lake-2026]].

## The Corridor Pattern

Three events in 26 months on one corridor: **September 2024** monsoon floods (11 projects, 600+ MW damaged nationally), **July 2025** Purepu GLOF (three plants, Rasuwagadhi heavily hit and only partially restored by December 2025), and **August 2026** Langtang Lirung avalanche flood (Rasuwagadhi destroyed outright). The 2026 event did not just damage assets; it destroyed the recovery of the *previous* event. This is the strongest evidence yet for the corridor-concentration argument on [[trishuli-cascade]] and the exposure analysis on [[glof-risk]]: Himalayan run-of-river corridors concentrate settlements, roads, intakes, powerhouses and transmission in a single narrow hazard path, and the hazard recurrence interval is shorter than the reconstruction interval.

## Financial and Systemic Impact

- NEA preliminary: "hundreds of billions of rupees"; IPPAN: Rs 25–30 billion (25–30 percent of project cost); government assessment of reconstruction needs up to **US$5 billion**. See [[kathmandupost-bhotekoshi-flood-hydropower-damage-2026]].
- Insurance: private projects generally insured through Nepali non-life insurers; NEA-owned infrastructure may not be comprehensively covered — a systemic gap with sector-wide claim capacity implications.
- NEPSE hydropower and non-life insurance indices fell sharply; construction-sector stocks rose on reconstruction expectations.
- Nepal sought advance power imports from India against the lost 430 MW; no immediate shortage was expected because domestic generation exceeds demand.
- Rescue physics as buildability evidence: underground powerhouses and tunnels both trapped workers (19 tunnels in Army search operations) and offered survival space — the same double-edged design logic documented on [[buildability]].

## What Would Change This Page

- NDRRMA/NEA consolidated damage assessments (project-level engineering damage, final loss figures).
- Independent satellite reconstructions of flood extent (Sentinel-1/2) — would convert Tier 3 geometric exposure into evidence for or against.
- Barrier-lake outcome — breach or stable drainage rewrites the downstream reaches.
- A published causal investigation of the Langtang Lirung initiating mechanism.

## Data Artifacts

- `data/flood_2026_08_impact_register.csv` — hand-curated register (18 rows, confidence-tiered, as-of stamped)
- `data/processed/maps/flood_2026_*.geojson` — route, impact, corridor and hazard layers (build report: `flood_2026_build_report.json`)
- Explorer preset **Flood 2026** — all layers with per-reach alignment confidence

## See Also

- [[glof-risk]] — hazard mechanism family and causal-discipline rules
- [[trishuli-cascade]] — corridor concentration and cascade risk
- [[rasuwagadhi]] — the destroyed project, with its 2025 damage-recovery history
- [[chilime]] — the buried plant within the Chilime group structure
- [[upper-trishuli-3a]] — the underground-powerhouse rescue case
- [[buildability]] — what tunnel-and-powerhouse design means for flood survival
- [[sediment-as-design-constraint]] — debris loads and channel change
- [[kathmandupost-bhotekoshi-flood-hydropower-damage-2026]]
- [[kathmandupost-bhotekoshi-flood-tunnel-rescues-2026]]
- [[kathmandupost-bhotekoshi-flood-barrier-lake-2026]]
- [[kathmandupost-bhotekoshi-flood-sitrep-ndrrma-2026]]
- [[reuters-bhotekoshi-flood-climate-attribution-2026]]
- [[ndrrma-rasuwa-glacial-flood-sitrep-2025]] — the July 2025 predecessor event

## Sources

- [[kathmandupost-bhotekoshi-flood-hydropower-damage-2026]]
- [[kathmandupost-bhotekoshi-flood-tunnel-rescues-2026]]
- [[kathmandupost-bhotekoshi-flood-barrier-lake-2026]]
- [[kathmandupost-bhotekoshi-flood-sitrep-ndrrma-2026]]
- [[reuters-bhotekoshi-flood-climate-attribution-2026]]
