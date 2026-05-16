---
title: Solar Resource Geography of Nepal
type: concept
created: 2026-04-23
updated: 2026-04-23
sources: [wb-esmap-solar-resource-assessment, global-solar-atlas-nepal, aepc-renewable-framework]
tags: [solar, GHI, DNI, resource, geography, terai, himalaya, mustang, elevation]
---

# Solar Resource Geography of Nepal

Three sentences to lead with, because they invert most people's priors:

1. **Latitude is not the interesting variable in Nepal.** The country spans ~26.3°N to ~30.4°N, a near-equatorial band whose peak solar angle varies only ±10% between solstices. This is a good solar latitude everywhere — so it explains nothing about where inside Nepal you should build.
2. **Nepal is in the global top quartile for solar resource, not the middle.** Country-weighted Global Horizontal Irradiance (GHI) is **~4.7–5.0 kWh/m²/day**, comparable to northern India and southern Spain. The trans-Himalayan rain-shadow districts (Mustang, Dolpa, Humla, upper Manang) reach **6.0–6.5 kWh/m²/day** — among the best GHI anywhere on Earth outside the Atacama and Tibetan Plateau.
3. **The resource variation across Nepal is driven by altitude, aspect, and monsoon cloud cover — not latitude.** Kathmandu Valley is the *worst* solar region in the country, because of a combination of monsoon cloud cover, mid-hill fog, aerosol pollution, and topographic shading. Terai is middling. Mustang is world-class.

This page maps that variation and draws the siting consequences.

## The four resource zones

Classed by 10-year mean GHI (kWh/m²/day). Values are taken from the World Bank ESMAP pyranometer network, cross-referenced with Global Solar Atlas (Solargis) satellite estimates.

### Zone A — Trans-Himalayan rain-shadow (GHI 5.8–6.5)

**Districts:** Mustang, Dolpa, upper Mugu, upper Manang, upper Humla, Jumla, Darchula (trans-Himalayan pockets).

**Why it wins:** Three compounding effects. (1) **Altitude** — 2,800–4,200 m mean site elevation gives thinner atmosphere, less scattering, cooler panel operating temperatures. (2) **Rain-shadow** — monsoon fronts unload on the southern slopes; these valleys stay clear through June–September. (3) **Low aerosol / zero haze** — no industrial air, no brick-kiln plume, no valley inversions.

**Why it loses anyway:** Distance to grid is the killer. The nearest 132 kV node is often 100–200 km away; terrain multiplies the per-km transmission cost 3–5×. Load is sparse (Mustang has ~14,000 people, no grid-scale demand). **Utility-scale GW-class solar here is a 15-year proposition, not a 3-year one.** In the near term Zone A is for: (a) off-grid mini-grid anchor sites, (b) research / demonstration, and (c) the eventual trans-border export play through [[ratmate-rasuwagadhi-kerung-400kv]].

### Zone B — Terai plains (GHI 4.8–5.3)

**Districts:** Jhapa, Morang, Sunsari, Saptari, Dhanusha, Sarlahi, Mahottari, Bara, Parsa, Rautahat, Nawalparasi, Rupandehi, Kapilvastu, Banke, Bardiya, Kailali, Kanchanpur.

**Why it wins:** This is the Nepal solar story. **Flat terrain** (slope < 3° across most of the belt), **densest 132 / 220 kV grid in the country** ([[hetauda-dhalkebar-inaruwa-backbone]]; [[dana-kushma-butwal-corridor]]), **highest population and industrial demand**, **proximity to the Indian grid** for eventual export via [[dhalkebar-muzaffarpur]], [[gorakhpur-butwal-interconnection]], [[inaruwa-purnea-interconnection]].

**Why it hurts:** (1) **Highest monsoon cloud burden** of the three main zones (25–35% GHI penalty Jun–Sep). (2) **Alienable land is agricultural** — Terai is Nepal's breadbasket; most parcels are rice/wheat rotation, politically and socially committed. (3) **Dust aerosol from India's Indo-Gangetic plain** drops dry-season GHI by another 5–10% through fine particulate deposition on panels.

**Verdict:** Zone B is where the 5–10 GW that matters to the national grid gets built — but almost exclusively through **agrivoltaic** dual-use configurations ([[agrivoltaics-and-land]]) or **substation-adjacent** greenfield pockets, not open fee-simple land purchase at scale.

### Zone C — Mid-hills (GHI 4.3–4.9)

**Districts:** Most of Bagmati, Gandaki, Lumbini, Karnali, and Sudurpaschim hill districts — Kathmandu Valley, Pokhara Valley, Palpa, Syangja, Tanahu, Gorkha, Lamjung, Dhading, Nuwakot, Sindhupalchok, Ramechhap, Okhaldhunga, Khotang, Bhojpur, Dhankuta, Surkhet, Salyan, Rolpa, Pyuthan, Dailekh.

**Why it's middling:** Solid latitude, good clear-sky days October–May — but monsoon cloud cover is punishing (GHI drops to 2.5–3.5 kWh/m²/day through July–August), aerosol is high in the larger valleys, and terrain fragments parcels into the <0.5 ha size that kills utility economics.

**Best use:** **Rooftop** (especially the 200,000+ commercial / institutional rooftops in valley towns), **small distributed generation** at the 33 kV level, and **hybrid solar-at-hydropower-site** where grid and land are already solved ([[hybrid-siting-logic]]). Zone C is where the *third* solar story lives: not utility, not off-grid, but **behind-the-meter and distribution-level** — the [[rooftop-minigrid-offgrid]] track.

### Zone D — High Himalaya (GHI 4.5–5.5 but non-siteable)

**Districts:** High-mountain portions of Taplejung, Sankhuwasabha, Solukhumbu, Dolakha, Rasuwa, northern Gorkha, northern Manang, northern Mustang, Dolpa-Upper, Mugu-North.

Good resource; non-siteable due to slope, land tenure (conservation areas, national parks), inaccessibility, and snow load. Included here only to head off the common error of reading "high altitude = more solar = build there." Almost all high-altitude *deployable* solar in Nepal is in **Zone A** (the trans-Himalayan valleys), not **Zone D** (the mountain faces above them).

## The five siting variables, ranked by signal strength

Ranked by how much each variable moves project economics, tested against 200+ Nepal-context solar assessments:

| Rank | Variable | Effect on LCOE | Notes |
|---|---|---|---|
| 1 | **Distance to 33+ kV substation** | ×2–5 if > 10 km | Dominates utility economics. Beyond 10 km you're building transmission, not solar. |
| 2 | **GHI** | ×0.80–1.10 across zones | 4.5 → 6.5 kWh/m²/day = ~40% more energy per installed MWp → ~25% lower LCOE |
| 3 | **Slope + land-use constraint** | ×1.0–1.8 | Terai flats = 1×; hill terracing + slope correction = 1.5–1.8× |
| 4 | **Monsoon cloud penalty** | ×1.05–1.25 | Correlated with Zone B/C but not identical — trans-Himalayan rain-shadow breaks it |
| 5 | **Latitude (tilt optimization)** | ×0.98–1.02 | Practically invisible across Nepal's 4° span |

Siting decisions that rank latitude above transmission distance are making a ~200× ordering error.

## The one-sentence siting conclusion

**For the next 10 GW of Nepal solar: build on the Terai flats within 10 km of the 132 kV spine, with a secondary tier at hydropower co-location sites, a rooftop track in Kathmandu Valley / Pokhara, and a long-dated Zone A option held in reserve for when the trans-Himalayan interconnection exists.**

That sentence should be the base layer of every Nepal solar strategy document. Almost none of them write it this explicitly because "solar" is treated as a single technology rather than four distinct deployment stories stapled together.

## Related

- [[solar-hydro-complementarity]] — what the seasonal profile does for the hydro fleet
- [[hybrid-siting-logic]] — why hydropower co-location is Zone-B-adjacent gold
- [[agrivoltaics-and-land]] — the only way Terai scales
- [[rooftop-minigrid-offgrid]] — where Zone C and Zone A actually make sense
- [[data-nepal-solar-resource-zones]] — the numbers by district
- [[wb-esmap-solar-resource-assessment]] — the underlying pyranometer data
- [[global-solar-atlas-nepal]] — satellite-derived cross-reference
