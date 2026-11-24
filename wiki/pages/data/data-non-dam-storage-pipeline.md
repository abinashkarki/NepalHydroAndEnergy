---
title: Non-Dam Storage Pipeline (BESS and Pumped Hydro)
type: data
created: 2026-11-24
updated: 2026-11-24
reviewed: 2026-11-24
review_due: 2027-02-24
sources: [nea-annual-report-fy2025-26, moewri-ipsdp-exec-summary-2025]
tags: [storage, bess, pumped-storage, flexibility, csv]
excerpt: A source-checked registry of Nepal's battery and pumped-storage projects as reported by NEA in FY 2025/26, from screening candidates to remote PV-plus-battery sites under construction.
caveat: No grid-scale BESS or pumped-storage plant is reported as operating. Capacities are study or target values; battery energy ratings published with implausible units are excluded.
maturity: working-page
page_quality: record
---

# Non-Dam Storage Pipeline (BESS and Pumped Hydro)

## Summary

This registry lists the battery energy storage (BESS) and pumped-storage hydropower (PSH) projects named in NEA's FY 2025/26 annual report, with status and page locators. None of the entries is operating. The most advanced are four small off-grid PV-plus-battery sites in Karnali.

## What This Shows

| Project | Technology | MW | Province | Status |
|---|---|---:|---|---|
| Hulingtar-Dumkim PSH | pumped-hydro | 494.5 | Bagmati | feasibility-study |
| Syarpu Lake PSH | pumped-hydro | 334 | Karnali | survey-licence |
| Kulekhani-Sisneri PSH | pumped-hydro | 100 | Bagmati | survey-licence |
| G-25 Pumped Storage | pumped-hydro | 411 | — | screened |
| Begnas Rupa Pump Storage | pumped-hydro | 150 | — | proposed |
| NEA utility BESS (target) | bess | 100 | — | proposed |
| Karnali Solar Energy Project (Mugu, Dolpa, Jumla, Humla) | bess (PV-coupled) | — | Karnali | under-construction / pre-construction |

> [!finding]
> The three PSH projects in NEA's Project Development Department portfolio sum to 928.5 MW (494.5 + 334 + 100). That matches the department's stated pumped-storage study portfolio of 928.5 MW (NEA FY 2025/26, PDF p.79).

> [!finding]
> NEA and the IPSDP classify Begnas-Rupa differently. NEA's planned-capacity table calls it "Begnas Rupa Pump Storage" (150 MW). The MoEWRI IPSDP executive summary lists "Begnas- Rupa Storage HEP" (150 MW, STO).

> [!finding]
> For the Karnali PV-plus-BESS sites, NEA prints battery sizes of 2,000–3,800 "MWh" for plants of 360–995 kW AC, in both the FY 2024/25 and FY 2025/26 reports. Those sizes are not plausible in MWh, so `energy_mwh` is left blank and the printed values are kept in `notes`.

## Coverage / Method

The machine-readable [storage_non_dam_specs.csv](../../../data/storage_non_dam_specs.csv) has one row per project or site. Each row records source URL, PDF page locator, confidence and `last_updated`. Status values used are `under-construction`, `pre-construction`, `feasibility-study`, `survey-licence`, `screened` and `proposed`. Rows were included only if NEA names them in its report. Wiki narrative pages without a primary locator were not used.

## Caveats

- NEA also reports screening totals: 63 pumped-storage candidates (69,428 MW) ranked from 220 identified over FY 2080/81 to FY 2082/83. Only named projects appear in the registry.
- The 100 MW BESS is a stated aim to be deployed at several substations under a PPP model. No sites, energy rating or award are published.

## Linked Data

- [Non-dam storage registry (CSV)](../../../data/storage_non_dam_specs.csv)

## Sources

- [[nea-annual-report-fy2025-26]]
- [[moewri-ipsdp-exec-summary-2025]]

## Related

[[storage-and-flexibility]] · [[storage-deficit]] · [[karnali-solar-energy-project]] · [[kulekhani-cascade]]
