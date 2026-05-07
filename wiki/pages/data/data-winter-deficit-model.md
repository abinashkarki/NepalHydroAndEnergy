---
title: Winter Deficit Model
type: data
created: 2026-05-07
updated: 2026-05-07
sources: [nea-annual-report-fy2024-25, wecs-river-basin-plan-2024]
tags: [winter-deficit, energy-balance, diurnal, evening-peak, dispatch, solar, storage, bess, budhigandaki, model]
page_quality: analysis
---

# Winter Deficit Model

A two-phase reproducible model quantifying Nepal's winter electricity gap at both monthly energy (GWh) and sub-daily capacity (MW) resolution. Phase 1 (`scripts/build_winter_deficit_model.py`) models Dec–Feb monthly energy balances under parameterised 2030/2035 scenarios. Phase 2 (`scripts/build_diurnal_peak_model.py`) models the evening peak hour (18:30) dispatch to answer whether the portfolio that closes the energy gap also delivers evening firm capacity — the 6pm–10pm winter window where solar is zero.

## Phase 1 — Monthly energy balance (all scenarios)

Phase 1 reads NEA FY 2024/25 monthly energy data as baseline, applies scenario assumptions (solar deployment, storage hydro additions, demand growth, BESS, demand-shaping), and outputs monthly Dec–Feb balances. Dec–Feb = Poush + Magh (two BS months, 58 days).

| Scenario | Horizon | Solar MWp | BESS GWh | Demand CAGR | Dec–Feb Demand GWh | Hydro GWh | Solar GWh | BESS GWh | Shaping GWh | Gap GWh | Gap % |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| baseline_fy2025 | 2025 | 142 | 0 | 0% | 2,129 | 1,551 | 28 | 0 | 0 | 551 | 25.9% |
| current_1gw | 2025 | 1,000 | 0 | 0% | 2,129 | 1,551 | 193 | 0 | 0 | 385 | 18.1% |
| current_3gw | 2025 | 3,000 | 0 | 0% | 2,129 | 1,551 | 580 | 0 | 0 | 76 | 3.6% |
| current_5gw | 2025 | 5,000 | 0 | 0% | 2,129 | 1,551 | 966 | 0 | 0 | 0 | 0% |
| current_5gw_bess | 2025 | 5,000 | 2 | 0% | 2,129 | 1,551 | 966 | 1 | 0 | 0 | 0% |
| 2030_baseline | 2030 | 142 | 0 | 8% | 3,128 | 1,926 | 28 | 0 | 0 | 1,175 | 37.6% |
| 2030_17gw | 2030 | 1,700 | 0 | 8% | 3,128 | 1,926 | 329 | 0 | 0 | 874 | 27.9% |
| 2035_full | 2035 | 5,000 | 2 | 7% | 4,188 | 3,247 | 966 | 1 | 400 | 0 | 0% |
| 2035_solar_only | 2035 | 5,000 | 0 | 7% | 4,188 | 2,412 | 966 | 0 | 0 | 810 | 19.3% |
| 2035_no_solar | 2035 | 142 | 0 | 7% | 4,188 | 3,247 | 28 | 0 | 0 | 914 | 21.8% |
| 2035_no_budhigandaki | 2035 | 5,000 | 2 | 7% | 4,188 | 3,247 | 966 | 1 | 400 | 0 | 0% |
| 2035_with_budhigandaki | 2035 | 5,000 | 2 | 7% | 4,188 | 4,187 | 966 | 1 | 400 | 0 | 0% |

**Assumptions:** WECS Low GDP demand CAGRs (8% 2025–30, 7% 2030–35). Terai solar CF 16.5% fixed-tilt. Storage pipeline: Tanahu 140 MW (COD 2026), Dudhkoshi 670 MW (COD 2035, scenario_risk), Budhigandaki 1,200 MW (COD 2036, post-2035). Hydro growth CAGR: 3% (2030), 4% (2035). Dry-season storage energy distributed across four winter months with triangular weights [1,2,2,1] peaking in Poush-Magh. Source: `data/processed/tables/winter_deficit_model/model_parameters.csv`.

## Phase 2 — Diurnal evening-peak dispatch (2035 scenarios)

Phase 2 takes Magh (mid-Jan to mid-Feb, ≈February) as the canonical winter reference month and models the 18:30 evening peak dispatch. The diurnal profile is sourced from [[data-solar-hydro-complementarity-profile]] lines 71–85: February weekday demand shape normalised to peak=100 at 18:30, RoR hydro flat at 30, solar bell curve dropping to zero by 17:30. Interpolation to hourly resolution yields an implied peak-to-average demand ratio of 1.35.

Dispatch logic: RoR hydro flat at average monthly MW. Reservoir hydro dispatched at rated MW in the 17:00–21:00 window (dispatch factor 0.9). Solar = 0 MW at 18:30 (sunset). BESS = 500 MW flat in the 17:30–21:30 window (2 GWh / 4h). Demand shaping = an explicit 400 MW peak reduction at 18:30 for scenarios that include demand-shaping energy.

| Scenario | Peak Demand MW | RoR MW | Reservoir MW | Solar at Peak | BESS MW | Shaping MW | Residual MW | Residual % |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 2035_no_solar | 4,066 | 1,504 | 729 | 0 | 0 | 0 | 1,833 | 45.1% |
| 2035_solar_only | 4,066 | 1,504 | 126 | 0 | 0 | 0 | 2,436 | 59.9% |
| 2035_full | 4,066 | 1,504 | 729 | 0 | 500 | 400 | 933 | 23.0% |
| 2035_no_budhigandaki | 4,066 | 1,504 | 729 | 0 | 500 | 400 | 933 | 23.0% |
| 2035_with_budhigandaki | 4,066 | 1,504 | 1,809 | 0 | 500 | 400 | −147 | −3.6% |

Model parameters: Magh reference month, 29 days, profile-implied peak-to-average ratio 1.348, reservoir dispatch factor 0.9, solar_mw_at_peak always 0.0 at the default 18:30 target hour. Budhigandaki (1,200 MW × 0.9 = 1,080 MW effective) flips the 933 MW deficit to a 147 MW surplus. Source: `scripts/build_diurnal_peak_model.py`, 2035_with_budhigandaki scenario.

## Scenario definitions

Scenario names are inherited from Phase 1 energy-balance design. Note that `2035_solar_only` excludes risky storage (Dudhkoshi) and `2035_no_solar` includes it — the labels describe the *additional* resource being tested, not what is excluded.

| Scenario ID | Solar MWp | Storage hydro active | BESS | Demand shaping | Budhigandaki |
|---|---|---|---|---|---|
| 2035_full | 5,000 | Tanahu + Dudhkoshi (810 MW) | Yes (2 GWh) | Yes (400 GWh Dec–Feb) | No |
| 2035_solar_only | 5,000 | Tanahu only (140 MW) | No | No | No |
| 2035_no_solar | 142 | Tanahu + Dudhkoshi (810 MW) | No | No | No |
| 2035_no_budhigandaki | 5,000 | Tanahu + Dudhkoshi (810 MW) | Yes (2 GWh) | Yes (400 GWh Dec–Feb) | No |
| 2035_with_budhigandaki | 5,000 | Tanahu + Dudhkoshi + Budhi (2,010 MW) | Yes (2 GWh) | Yes (400 GWh Dec–Feb) | Yes (1,200 MW) |

The counterintuitive result — `2035_solar_only` has a worse evening peak (2,436 MW residual) than `2035_no_solar` (1,833 MW) — is correct given these definitions. Both have zero solar at 18:30. The difference is 670 MW of Dudhkoshi reservoir dispatch, excluded from `2035_solar_only` by the Phase 1 design. The 603 MW residual gap between them (2,436 − 1,833) equals Dudhkoshi's dispatch contribution (670 × 0.9 = 603 MW).

## Known limitations

- **Import overcount:** Phase 1 overcounts annual imports by ~282 GWh/year because it does not model shoulder-month simultaneous import/export or NEA curtailment. Winter Dec–Feb figures (Poush-Magh) are more reliable than annual totals. Source: `data/processed/tables/winter_deficit_model/model_parameters.csv` import_accounting_note.
- **BESS sizing:** Phase 1 models BESS as a placeholder ~1 GWh Dec–Feb seasonal contribution (2 GWh distributed evenly across four winter months). Phase 2 diurnal model uses the full 500 MW / 2 GWh BESS power rating for evening dispatch, which is more realistic for the 4-hour evening window. The Phase 1 seasonal GWh understates BESS energy contribution; Phase 2 MW capacity is the correct metric for evening firm capacity analysis.
- **Scenario naming:** `2035_solar_only` excludes scenario_risk storage (Dudhkoshi); `2035_no_solar` includes it. Names reflect Phase 1 energy-balance design and are counterintuitive for Phase 2 capacity-credit comparison. Read the scenario definitions table above when interpreting evening-peak results.
- **Reservoir dispatch:** All reservoir capacity is assumed dispatched at full rated MW in the 17:00–21:00 window at 0.9 availability. This is optimistic — it assumes reservoirs are full and operators choose evening-peak dispatch. Use `--reservoir-dispatch-factor` to test lower availability.
- **BESS state of charge:** No degradation, no state-of-charge constraints within the daily cycle (assumes full charge from mid-day solar). Optimistic.
- **Demand shaping:** Phase 1 models 400 GWh of Dec–Feb energy shifted out of high-stress periods. Phase 2 separately models an explicit 400 MW reduction at the 18:30 target hour for scenarios that include demand shaping; it is a peak-MW assumption, not a GWh-to-MW conversion.
- **Weekday vs weekend:** February weekday profile used as canonical. Weekend industrial load is lower but the evening residential peak still dominates.

## Model parameters

Full parameter table and scenario definitions are in `data/processed/tables/winter_deficit_model/model_parameters.csv`. Key inputs: solar CF profile, storage hydro pipeline, NEA monthly energy balance FY 2024/25. Model source code is in `scripts/build_winter_deficit_model.py` and `scripts/build_diurnal_peak_model.py`.

## Related

- [[solar-role-in-winter-deficit]] — synthesis page for what the model implies for policy
- [[data-solar-hydro-complementarity-profile]] — the diurnal profile the Phase 2 model uses
- [[budhigandaki]] — the 1,200 MW storage project quantified here
- [[dudhkoshi-storage]] — the 670 MW storage project in the 2035 full portfolio
- [[tanahu-hydropower]] — the 140 MW storage project, first to commission
- [[storage-deficit]] — the framing page for Nepal's storage gap
- [[seasonal-mismatch]] — the structural problem this model quantifies
- [[firm-power]] — the capacity-credit frame
