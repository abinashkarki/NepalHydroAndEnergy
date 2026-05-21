---
title: Figure Index
type: data
created: 2026-05-13
updated: 2026-05-21
figure_type: table
sources: []
tags: [figures, charts, manifest, data]
page_quality: record
generator: figures
---

# Figure Index

## Summary

Registry of published wiki figures generated from `wiki/explorer/shared/wiki-figure-manifest.json`.

## Published Figures

| Figure | Format | Target Pages | Sources | Caveat |
|--------|--------|--------------|---------|--------|
| [monthly_trade_3y](../../../wiki/assets/figures/monthly_trade_3y.svg) | SVG | [[data-trade-time-series]] | [[nea-annual-report-fy2024-25]] | Annual-report comparison chart totals differ slightly from NEA narrative totals. |
| [fleet_capacity_mix](../../../wiki/assets/figures/fleet_capacity_mix.svg) | SVG | [[data-fleet-composition]] | [[nea-annual-report-fy2024-25]], [[wecs-energy-synopsis-2024]] | Fleet taxonomy varies by reporting source; FY 2022/23 seasonal split is single-year. |
| [basin_seasonality_compare](../../../wiki/assets/figures/basin_seasonality_compare.svg) | SVG | [[data-basin-discharge]] | [[wecs-river-basin-plan-2024]], [[national-water-plan-nepal]] | Metrics mix runoff, surface flow, and rainfall depending on available public source. |
| [storage_gap](../../../wiki/assets/figures/storage_gap.svg) | SVG | [[data-storage-comparison]] | [[wb-water-sector-diagnostic]], [[jica-ipsdp-main-report-vol2]] | JICA storage-need estimates are electricity-system planning needs; current storage uses Kulekhani operational capacity. |
| [electricity_trade_shift](../../../wiki/assets/figures/electricity_trade_shift.svg) | SVG | [[data-trade-time-series]] | [[wb-country-economic-memo-2025]], [[nea-annual-report-fy2024-25]] | Annual totals hide the wet-export and dry-import monthly structure shown in monthly_trade_3y. |
| [lead1_fy2081_82_trade_vs_storage](../../../wiki/assets/figures/lead1_fy2081_82_trade_vs_storage.svg) | SVG | [[data-trade-time-series]] | [[nea-annual-report-fy2024-25]] | Compact wiki figure excludes daily-report parsed points; see the lead-1 table for daily subset coverage. |
| [license_type_mix](../../../wiki/assets/figures/license_type_mix.svg) | SVG | [[data-fleet-composition]] | [[doed-licensing-directive-2075]] | Licensing-stage counts are administrative status snapshots, not financing readiness. |
| [top_operational_projects](../../../wiki/assets/figures/top_operational_projects.svg) | SVG | [[data-fleet-composition]] | [[doed-licensing-directive-2075]] | Public-portal operating status and capacity values can lag commissioning updates. |
| [wecs_basin_potential](../../../wiki/assets/figures/wecs_basin_potential.svg) | SVG | [[data-basin-discharge]], [[data-potential-pyramid]] | [[wecs-hydropower-potential-2019]] | Gross potential is not equivalent to economically developable or transmission-ready capacity. |
| [capacity_balance_fy2024_25](../../../wiki/assets/figures/capacity_balance_fy2024_25.svg) | SVG | [[data-domestic-demand]], [[data-fleet-composition]] | [[nea-annual-report-fy2024-25]] | Monthly capacity-balance rows do not replace hourly dispatch or adequacy modeling. |
| [export_revenue_fy2025_26](../../../wiki/assets/figures/export_revenue_fy2025_26.svg) | SVG | [[data-trade-time-series]] | [[nea-annual-report-fy2024-25]] | First five months only; this is not a full-year revenue curve. |
| [potential_pyramid_funnel](../../../wiki/assets/figures/potential_pyramid_funnel.svg) | SVG | [[data-potential-pyramid]] | [[wecs-hydropower-potential-2019]], [[wb-nepal-power-sector-reform-2022]], [[nea-annual-report-fy2024-25]] | Intermediate levels are compiled order-of-magnitude estimates, not definitive ceilings. |
| [hydropower_license_map](../../../wiki/assets/figures/hydropower_license_map.png) | PNG | [[data-potential-pyramid]] | [[doed-licensing-directive-2075]] | Static map is a portfolio snapshot; use the explorer map for current interactive filtering. |

## Regeneration

Run from the workspace root:

```bash
make wiki-figures
```

The generated manifest is the source of truth for figure paths, source files, target pages, caveats, and license metadata.
