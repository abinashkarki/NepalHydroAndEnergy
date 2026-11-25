---
title: Grid Substation Inventory
type: data
created: 2026-11-24
updated: 2026-11-25
reviewed: 2026-11-24
review_due: 2027-02-24
sources: [nea-annual-report-fy2025-26, nea-annual-report-fy2024-25, nea-transmission-annual-book-2077, nea-solar-loi-2024]
tags: [substations, transmission, grid, csv, nea]
excerpt: "A source-located inventory of 153 grid substations from 66 to 400 kV: 95 in service with 15,541 MVA of transformer capacity, plus the substations NEA lists as under construction or planned."
caveat: Installed MVA counts every transformer NEA lists at a substation, including 33/11 kV and 66/11 kV units. Coordinates are filled only from the RPGCL official map, a repo place anchor or a named OpenStreetMap feature (102/153 rows, precision-tagged); district and province cover 148/153 rows via primary sources and canonical Nepal administrative geography lookup.
maturity: working-page
page_quality: record
---

# Grid Substation Inventory

## Summary

[substation_specs.csv](../../../data/substation_specs.csv) lists **153 grid substations** from 66 kV to 400 kV. Each row records voltage ratios, installed and pipeline MVA, status, location where one is sourced, linked corridors, cross-border role and linked solar awards. There are **95 substations in service** (94 operating, one partially operational) and 58 under construction or planned. The in-service rows add up to **15,540.6 MVA**, which matches NEA's FY 2025/26 total of 15,541 MVA across 318 transformers.

## What This Shows

| Highest voltage | Status | Substations | Installed MVA | Pipeline MVA |
|---|---|---:|---:|---:|
| 400 kV | operating | 2 | 3,445.2 | — |
| 400 kV | partially operational | 1 | 830.0 | — |
| 400 kV | under construction | 4 | — | 982.5 |
| 400 kV | planned | 8 | — | 6,176.0 |
| 220 kV | operating | 13 | 3,429.9 | 1,460.0 |
| 220 kV | under construction | 4 | — | 894.0 |
| 220 kV | planned | 5 | — | 2,189.0 |
| 132 kV | operating | 67 | 7,313.0 | 2,741.0 |
| 132 kV | under construction | 21 | — | 2,028.0 |
| 132 kV | planned | 16 | — | 1,567.5 |
| 66 kV | operating | 12 | 522.5 | 351.0 |
| **Total** | | **153** | **15,540.6** | **18,389.0** |

"Pipeline MVA" (`planned_additional_mva`) is the capacity NEA prints for each substation in its under-construction and planned tables. For operating substations it is expansion capacity. The total splits into 6,260.5 MVA under construction (NEA total: 6,261) and 12,128.5 MVA of itemised planned capacity. NEA's planned total of 16,258 MVA also includes a 4,129 MVA aggregate for the Kathmandu Valley Transmission System Expansion. NEA gives no per-substation breakdown of that aggregate, so the CSV leaves it out.

| Province (sourced + canonical geography) | Substations | Installed MVA |
|---|---:|---:|
| Bagmati | 49 | 5,135.6 |
| Madhesh | 22 | 3,994.5 |
| Koshi | 17 | 2,788.7 |
| Lumbini | 25 | 1,762.2 |
| Gandaki | 23 | 1,298.2 |
| Sudurpashchim | 8 | 489.0 |
| Karnali | 5 | 60.0 |
| Unassigned (multi-district / corridor hub) | 4 | 12.5 |

> [!finding]
> Two substations, Dhalkebar (2,054.2 MVA) and Inaruwa (1,391.0 MVA), hold 22% of in-service transformer capacity. Of the 15 rows at 400 kV, 12 are under construction or planned.

> [!finding]
> All 63 NEA 2024 solar award rows that name a substation were checked against the inventory. 30 rows matched 24 inventory substations, totalling 590 MW. The largest linked totals are Dhalkebar, Kushaha, Motipur and Sunwal at 50 MW each, and Kushaha has 22.5 MVA of listed transformer capacity.

<figure class="wiki-inline-figure">
  <img src="../assets/figures/substation_province_capacity.svg" alt="Horizontal bars of installed and planned additional grid substation MVA for each of Nepal's seven provinces">
  <figcaption>Bagmati holds 5,136 MVA of installed substation capacity against 60 MVA in Karnali; planned additions are spread more evenly. Source: [[nea-annual-report-fy2025-26]] Appendix 8 and project tables, via the CSV on this page.</figcaption>
</figure>

## Coverage / Method

- **Existing substations.** The 95 in-service rows were parsed from NEA FY 2025/26, Appendix 8, "Existing High Voltage Grid Substations" (printed pp.204–211). Every transformer's FY 082-83 MVA is summed. Rows are checked against NEA's summary table (printed p.212): 318 transformers, 15,541 MVA, and matching subtotals for each ratio. The FY 2024/25 table was used only to flag substations that first appear with capacity in that year.
- **Pipeline.** The under-construction table (printed pp.213–214) and the planned/proposed table (printed pp.215–216) were transcribed per substation. Directorate totals were checked against the printed totals: 2,457.5 and 3,803 MVA under construction; 9,267.5 (including the 4,129 MVA aggregate) and 6,990 MVA planned. When a new entry shares a name with an existing substation, it is merged into that row and described in `notes`. Name-only merges of 400 kV sites (Lamahi, Kushma, Burtibang) are marked as site-unconfirmed.
- **MCA-Nepal 400 kV terminals.** Ratmate and New Damauli are not itemised in NEA's appendix. They come from [[mca-central-400]] and carry no MVA.
- **Coordinates.** 102 of 153 rows (67%) have coordinates, from `scripts/geocode_infrastructure_assets.py`: 400 kV 13/15, 220 kV 17/22, 132 kV 65/104, 66 kV 7/12. 64 rows are `official-map-node` (an RPGCL map substation symbol, ~1 km precision; a symbol drawn within 1 km of the row's district border is accepted). 38 are `approximate-place`: a Nominatim or OpenStreetMap match for the named place, not the substation footprint. All RPGCL-derived positions use the corrected GeoPDF georeference in `scripts/rpgcl_georef.py`. An earlier lat/lon-bilinear fit placed them about 6–13 km south of their true position, and rows re-derived on 2026-11-25 keep the replaced value in `notes`. Kushaha's coordinates are withheld because the anchor and the solar award record disagree on its district.
- **District / province.** 148 of 153 rows have a district and province: 39 from primary sources/anchors (`place_anchor_index.geojson`, NEA text, solar LoI list, entity pages) and 109 via deterministic Nepal 77-district canonical geography lookup (`scripts/enrich_canonical_geography.py`, tagged `canonical-geography` in `notes`). Five rows remain unassigned: four multi-district/corridor hubs (`bagmati-substation`, `likhu-hub-substation`, `sunkoshi-hub-substation`, `kavre-ramechhap-substation`) and `ridi-substation`, because Ridi Bazaar straddles the Gulmi/Palpa border. New Attariya was corrected from Kailali to Kanchanpur: the NEA FY 2025/26 map labels it "DAIJI (NEW ATTARIYA)".
- **Commissioning year.** Six rows have a commissioning year, each taken from a dated statement: Dhalkebar 2018, Tingla 2019, Inaruwa 2022, New Hetauda 2024, Surkhet 2026 and Parsauni 2026.
- **Solar links.** `linked_solar_award_mw` is generated by `scripts/build_substation_specs_links.py`. The script normalises names, applies an explicit alias table (for example Sunawal→Sunwal and Paudi→Paudi Amarai), rejects matches where the districts disagree, and excludes Maharajgunj, a Kapilvastu solar site that is not the planned Kathmandu Valley substation of the same name. The script's `--check` mode runs in the test suite.
- **Validation.** The CSV is checked against `wiki/substation-specs-schema.json` by `scripts/validate_repo.py`, which tests enums, numeric ranges, unique slugs, coordinate pairs and the existence of source and corridor slugs.

29 solar substation names do not match an inventory row: Aurahi, Baniyani, Bardibas, Barju, Belauri, Birendrabazzar, Chandrapur, Dhanusha Dham, Dhulabari, Gadhawa, Gorusinge, Gulariya, Haripur, Khungri, Kolabhi, Krishnanagar, Machhagad, Maharajgunj (excluded), Mainapokhar, Manpur, Maulapur, Mukundapur, New Nepalgunj, Palpa/Batasa, Parasi, Rakathum, Sangutar, Simaraungadh and Taulihawa. Most look like 33 kV-level sites outside NEA's grid-substation appendix. Matching them would need a source that ties each name to a grid substation.

## Caveats

- Installed MVA includes distribution-level 33/11 kV and 66/11 kV transformers, as NEA's appendix totals do. It is not the same as grid transformation capacity.
- Status is as of the end of FY 2082/83 (mid-July 2026). New Hetauda is recorded as partially operational: NEA lists its 400/220 kV transformers, but the narrative records 220 kV charging, and the 400 kV Hetauda–Dhalkebar line was still under construction.
- `highest_voltage_kv` is the in-service voltage for operating rows. Planned 400 kV extensions at existing sites, such as New Khimti, Kushma and Lamahi, are recorded in `planned_additional_mva` and `notes`.
- Coordinate gaps (51/153 rows) are deliberate. A place-level match is used only when the named place is unambiguous within the row's district, and it is tagged `approximate-place`. Seven 400/220 kV sites (New Kohalpur, Sunkoshi Hub, Markichowk, Lapang, Dhaubadi, Palpa and Harnaiya) have no RPGCL symbol or unambiguous place match. District/province assignments for the 109 canonical-lookup rows reflect administrative location of the named substation site, not an independent field survey.

## Linked Data

- [Grid substation inventory (CSV)](../../../data/substation_specs.csv)
- [Substation CSV schema](../../substation-specs-schema.json)

## Sources

- [[nea-annual-report-fy2025-26]] — Appendix 8 substation tables (PDF pp.214–226) and project narratives
- [[nea-annual-report-fy2024-25]] — prior-year existing-substation table and New Butwal location
- [[nea-transmission-annual-book-2077]] — Tingla commissioning date and Purbi Chitwan location
- [[nea-solar-loi-2024]] — substation names and districts on the 2024 solar award records

## Related

[[hetauda-dhalkebar-inaruwa-backbone]] · [[mca-central-400]] · [[data-layer-grid-hubs-place-anchors]] · [[data-layer-solar-plants-nea-awards]] · [[tingla-132-33kv-substation]] · [[markichowk-220-132kv-substation]]
