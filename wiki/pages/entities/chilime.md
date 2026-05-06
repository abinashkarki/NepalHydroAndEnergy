---
title: Chilime
type: entity
created: 2026-04-20
updated: 2026-05-06
sources: [nea-transmission-annual-book-2077, nea-annual-report-fy2024-25]
tags: [project, operating, rasuwa]
images:
  - src: chilime/nea2077-p177-img01.png
    caption: "Work in Progress in Surge Shaft"
    credit: "Nepal Electricity Authority, A Year in Review FY 2019/20 (B.S. 2077)"
    license: gov-permissive
    source_url: "../../../data/raw/corridor_tracing/nea/nea_transmission_annual_book_2077.pdf"
  - src: chilime/nea2077-p177-img02.png
    caption: "Work in Progress in Permanent Bridge"
    credit: "Nepal Electricity Authority, A Year in Review FY 2019/20 (B.S. 2077)"
    license: gov-permissive
    source_url: "../../../data/raw/corridor_tracing/nea/nea_transmission_annual_book_2077.pdf"
  - src: chilime/nea2077-p177-img03.png
    caption: "Signing ceremony of Contract Agreement for Lot-2 electro-mechanical works"
    credit: "Nepal Electricity Authority, A Year in Review FY 2019/20 (B.S. 2077)"
    license: gov-permissive
    source_url: "../../../data/raw/corridor_tracing/nea/nea_transmission_annual_book_2077.pdf"
  - src: chilime/nea2077-p177-img05.png
    caption: "Chilime Hydroelectric Plant"
    credit: "Nepal Electricity Authority, A Year in Review FY 2019/20 (B.S. 2077)"
    license: gov-permissive
    source_url: "../../../data/raw/corridor_tracing/nea/nea_transmission_annual_book_2077.pdf"
  - src: chilime/nea2425-p002-img01.png
    caption: "Sanjen and Chilime HEP Site"
    credit: "Nepal Electricity Authority, A Year in Review FY 2024/25"
    license: gov-permissive
    source_url: "../../../data/raw/projects_storage/nea_annual_report_2024_2025.pdf"
generator: specs-refresh
page_quality: analysis
---

# Chilime

<figure class="wiki-inline-figure">
  <img src="../assets/images/chilime/nea2077-p184-img02.png" alt="Under construction powerhouse filled with the water and debris during the flood.">
  <figcaption>Under construction powerhouse filled with the water and debris during the flood.</figcaption>
</figure>

<figure class="wiki-inline-figure">
  <img src="../assets/images/chilime/nea2077-p182-img02.png" alt="HEP Headworks & Powerhouse">
  <figcaption>HEP Headworks & Powerhouse</figcaption>
</figure>

22 MW · operating · on the Chilime · in Rasuwa district.

<!-- generated:specs:start -->

## Specifications

| Parameter | Value |
|-----------|-------|
| Capacity | 22 MW |
| Status | Operating |
| Registry licence | Operation |
| River | Chilime |
| District | Rasuwa |
| Province | Bagmati Pradesh |

### Output

| Parameter | Value |
|-----------|-------|
| Annual design energy | 132.9 GWh |
| Q-design | Q65+ |
| Type | RoR |

### Governance

| Parameter | Value |
|-----------|-------|
| Developer | Chilime Hydropower Company Limited |

### Schedule

| Parameter | Value |
|-----------|-------|
| Commercial operation | 2003 |
| Completion | 100 % |

<!-- generated:specs:end -->

<!-- generated:sources:start -->

## Sources

- [[nea-transmission-annual-book-2077|NEA Transmission Annual Book 2077]]
- [[nea-annual-report-fy2024-25|NEA Annual Report FY 2024/25]]

<!-- generated:sources:end -->

## Notes

> [!note] This is a registry-backed project record. Capacity, location,
> and licence status come from the Ministry of Energy registry
> mirrored in the map data. Narrative context and images are added
> where public sources are strong enough; the specification table is
> maintained from the registry.

## Performance and Historical Context

Chilime is the sector's most cited success case — and its performance metrics justify the reputation. However, the conditions that produced those metrics are not replicable for modern projects.

### Generation overperformance

Chilime consistently generates **above** its contracted energy, a rarity in Nepal's hydro sector:

| Fiscal Year | Contracted (GWh/yr) | Actual (GWh/yr) | % of Contracted |
|---|---|---|---|
| FY 2075/76 (~2018/19) | 132.9 | 153.7 | **115.6%** |
| FY 2076/77 (~2019/20) | 132.9 | 146.3 | **110.1%** |

Source: Chilime Hydropower Company Limited annual reports.

This overperformance places Chilime in stark contrast to modern IPPs, where zero of 100+ projects evaluated in a recent Urja Khabar audit exceeded 80% of contracted energy. See [[q-design-discharge]] for the full generation performance comparison.

### Why Chilime is not a replicable baseline

Despite being routinely invoked to justify mass public equity participation in hydropower, Chilime's success is a product of a different regulatory, financial, and climatic era:

1. **Conservative Q-design:** Chilime was commissioned in 2003 and likely designed on Q65 or higher — a more cautious flow percentile than the Q40–Q45 now permitted under current DoED guidelines. This means its contracted energy was set conservatively low relative to actual hydrology.

2. **Reliable snow-fed basin:** The Chilime River is a snow-fed system with less seasonal volatility than the monsoon-dominated, rain-fed tributaries where most modern IPPs are located.

3. **Pre-climate-shift commissioning:** Chilime entered operation before the acceleration of cryospheric melt and shifting monsoon patterns that now undermine the stationarity assumption in hydrological models.

4. **Lower financial leverage:** Built in an era of lower construction costs and lower debt leverage, Chilime never faced the Debt Service Coverage Ratio pressures that now push post-2015 projects into technical default. See [[q-design-discharge]] for DSCR break-point analysis.

5. **NEA subsidiary status and PPA rate advantage (VERIFIED):** Chilime is an NEA subsidiary (NEA retains 51% controlling stake). Its PPA, signed June 25, 1997, uses a **dual-tier billing architecture categorically different from modern IPPs**:

   | Category | Tariff (NPR/kWh) | FY2078/79 Volume (GWh) | FY2078/79 Revenue (NPR) |
   |---|---|---|---|
   | Regular Energy | 8.17 | 133.24 | 1,088,000,000 |
   | Excess Energy | 4.08 | 22.82 | 93,110,000 |
   | **Total** | **7.57 (blended)** | **156.06** | **1,181,740,179** |

   Source: Chilime Hydropower Company Limited Annual Report FY2078/79. VERIFIED.

   **This billing architecture — not the per-unit rate alone — is the mechanism of the subsidy.** Unlike modern IPPs, which must classify generation by season (wet/dry), Chilime categorizes output as "Regular" vs "Excess." In FY2078/79, **85.4%** of total generation (133.24 of 156.06 GWh) was classified as Regular Energy and billed at the premium NPR 8.17 rate year-round — regardless of season. A comparable private IPP must sell the majority of its monsoon-heavy generation at the depressed NPR 4.80 wet-season rate.

   **Quantified rate differential:**
   - Chilime blended rate: **NPR 7.57/kWh**
   - Private IPP baseline (optimized 20% dry energy mix): (0.20 × 8.40) + (0.80 × 4.80) = **NPR 5.52/kWh**
   - Differential: **NPR 2.05/kWh = 37.1% revenue advantage per unit**
   - For a 50 MW comparable private IPP generating 200 GWh/year, this represents approximately **NPR 410 million in foregone annual revenue**

   **External academic verification:** The Fenner School of Environment and Society (Australian National University), *Nepal State of Knowledge Report — Renewables and PSH*, independently documents this dynamic:

   > "The major complaint of the rising IPPs is that the playing field is not level, that NEA as generator, transmitter and distributor gives preferential terms to its own projects compared to IPPs; and indeed, this is seen in the case of the Chilime hydropower company that is owned by the NEA and its staff."

   Citation: Fenner School of Environment and Society, ANU, *Nepal State of Knowledge Report — Renewables & PSH*, p. 20. URL: https://fennerschool.anu.edu.au/files/Nepal%20State%20of%20Knowledge%20Report%20-%20Renewables%20%26%20PSH.pdf.

   See [[ppa-pricing]] for the full rate comparison table and [[nea-triple-authority]] for the institutional framework.

6. **IPO after profitability, not before:** Chilime's 2010 IPO occurred after **seven years of profitable operations**, enabling the company to distribute a 35% cash dividend within a year of listing. Modern hydro IPOs are routinely floated pre-commissioning or immediately post-COD, when the project is hemorrhaging cash from capitalized interest. See [[ipo-hydropower-bailout]].

Chilime's subsequent role as a holding company — spinning off subsidiaries (Rasuwagadhi, Sanjen, Madhya Bhotekoshi) to bypass the terminal BOOT-model asset handover — further reflects a business environment that no longer exists for new entrants.

## See also

- [[run-of-river-hydropower]]
- [[q-design-discharge]]
- [[nea-triple-authority]]
- [[ppa-pricing]]
- [[ipo-hydropower-bailout]]
