---
title: NEA Standard PPA Rate Schedule
type: data
created: 2026-11-24
updated: 2026-11-24
reviewed: 2026-11-24
review_due: 2027-02-24
sources: [erc-eca-storage-ppa-discussion-paper-2025, nea-solar-loi-2024, nea-annual-report-fy2025-26, erc-reservoir-ppa-directive-2082]
tags: [ppa, tariff, nea, erc, ror, pror, storage, solar, csv]
excerpt: NEA's April 2017 posted power-purchase rates for RoR, PRoR and reservoir hydropower, the 2024 solar competitive-award tariff range, and NEA's FY 2025/26 average purchase rate, with explicit gaps for wind, biomass and a solar ceiling.
caveat: The hydropower rates are the 27 April 2017 NEA Board schedule as reproduced in an ERC-commissioned discussion paper; the paper does not say whether the RoR and PRoR rates remain unchanged today, and it states that the reservoir rates were withdrawn.
maturity: working-page
page_quality: record
---

# NEA Standard PPA Rate Schedule

## Summary

[ppa_standard_rates.csv](../../../data/ppa_standard_rates.csv) has 25 rows: 16 RoR/PRoR rates and 2 withdrawn reservoir rates from the NEA Board schedule effective 2074/01/14 BS (27 April 2017), 3 solar rows summarising the 2024 competitive award, 3 explicit gap rows (solar ceiling, wind, biomass) and 1 context row for NEA's reported average purchase rate.

## What This Shows

| Technology | Dry season (NRs/kWh) | Wet season (NRs/kWh) | Condition (as printed) |
|---|---|---|---|
| RoR, option 1 (6 dry / 6 wet months) | 8.40 | 4.80 | Wet season at most 70% of energy |
| RoR, option 2 (4 dry / 8 wet months) | 8.40 | 4.80 | Dry-season energy under 30% |
| PRoR, 1–2 / 2–3 / 3–4 / 4–6 peak hours | peak 8.50 / 8.80 / 9.40 / 10.55; non-peak 4.80 | 4.80 | Minimum dry-season energy 30% |
| Reservoir (withdrawn) | 12.40 | 7.10 | Minimum dry-season energy 35%; 3% escalation for 8 years |
| Solar, 2024 award (63 rows, 960 MW) | 4.99–5.54, single rate | — | Award / pre-PPA; capacity-weighted mean 5.43 (derived) |
| NEA average purchase rate, FY 2025/26 | 6.07 (all purchases) | — | Reported outcome, not a tariff |

> [!finding]
> In the 2017 schedule, every RoR and PRoR wet-season rate and every PRoR dry-season non-peak rate is NRs 4.80/kWh. The PRoR rates differ only in the dry-season peak rate, which rises from NRs 8.50 (1–2 peak hours) to NRs 10.55 (4–6 hours).

> [!finding]
> The 2024 solar award tariffs (NRs 4.99–5.54/kWh, single rate) are higher than the 2017 hydropower wet-season rate (NRs 4.80) and lower than its dry-season rate (NRs 8.40).

## Coverage / Method

- Hydropower rows come from Table 1 of [[erc-eca-storage-ppa-discussion-paper-2025]] (printed p.9, PDF p.14). The paper cites "NEA Board Decisions on the Power Purchase Rates and Associated Rules for PPA of ROR/PROR/Storage Projects Effective from 2074/01/14". The season definitions are from the same table: wet is 16 Jestha–15 Mangsir and dry is 16 Mangsir–15 Jestha.
- The source has PRoR bands of 1–2, 2–3, 3–4 and 4–6 daily peak hours at rated capacity. The CSV keeps these bands instead of the runbook's planned 1–2 / 2–4 / 4–6 split.
- Solar rows aggregate the 63 award rows of [[nea-solar-loi-2024]], as transcribed in `data/solar_project_specs.csv`. The capacity-weighted mean is computed here.
- The average purchase rate is from the FY 2025/26 key financial indicators table in [[nea-annual-report-fy2025-26]] (PDF p.158). The table marks the figure provisional, subject to audit.

## Caveats

- **Escalation:** the paper states the 3%-for-8-years escalator only for reservoir rates. For RoR and PRoR the CSV records "not stated in source". Project-level escalation terms reported in ratings documents are on [[ppa-pricing]] and are not used here.
- **Tenure and take-or-pay:** these are `unknown` for every row. No official NEA or ERC text on disk states them; the secondary legal analysis in [[nea-standard-ppa-clauses]] is not used as a rate source.
- **Gaps:** no official posted rate was verified for a solar ceiling, wind or biomass. These rows are kept as explicit `unknown` gaps.
- **Reservoir:** the current reservoir framework is [[erc-reservoir-ppa-directive-2082]], which sets a tariff methodology, not a posted rate.
- **Signed PPAs:** individual signed PPAs may differ from the posted schedule.

## Linked Data

- [NEA standard PPA rates (CSV)](../../../data/ppa_standard_rates.csv)
- [[data-erc-retail-tariffs]] — the retail (sales) side

## Sources

- [[erc-eca-storage-ppa-discussion-paper-2025]] — Table 1, 2017 NEA posted rates
- [[nea-solar-loi-2024]] — 2024 solar award tariffs
- [[nea-annual-report-fy2025-26]] — average power purchase rate
- [[erc-reservoir-ppa-directive-2082]] — current reservoir framework

## Related

[[ppa-pricing]] · [[nea-standard-ppa-clauses]] · [[nea-960mw-solar-tender]]
