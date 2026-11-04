# HydroMap coverage benchmark

`scripts/benchmark_hydromap_coverage.py` compares the current Nepal Energy map registries with HydroMap Nepal's public JSON feed. It is a read-only coverage and quality check, not an ingestion pipeline.

## Run

```bash
python scripts/benchmark_hydromap_coverage.py
```

For a reproducible offline run, pass a previously obtained source snapshot:

```bash
python scripts/benchmark_hydromap_coverage.py --hydromap-source /path/to/hydromap-projects.json
```

Use `--no-write` to print the derived summary without changing generated artifacts.

## Outputs

The command writes five derived files under `data/processed/tables/`:

- `hydromap_coverage_summary.json` — counts, MW totals, category coverage, provenance hashes, quality indicators, status crosswalk, and specification completeness.
- `hydromap_active_review_queue.csv` — external operating or construction rows without a conservative exact match, with one review-only local suggestion. It intentionally excludes survey, application, study, and cancellation categories; those remain counted in the summary's category coverage.
- `hydromap_capacity_conflicts.csv` — exact-name matches whose capacity differs by more than 0.01 MW.
- `hydromap_local_unmatched.csv` — local rows with no exact match or an unresolved duplicate-name match.
- `hydromap_curated_specs_review.csv` — one review-only external candidate for every curated specification row.

Similarity scores never create matches. They only prioritize human review.

## Matching and status rules

Names are normalized with Unicode NFKD, ASCII folding, case folding, punctuation collapse, and removal of generic terms such as `HEP`, `HPP`, and `Hydropower Project`. Positional, numbered, storage, and cascade tokens remain significant. Duplicate normalized names are accepted only when one candidate also matches capacity within 0.01 MW.

The benchmark deliberately preserves both taxonomies:

- Local `license_type`: Survey, Generation, Operation.
- HydroMap `category`: application, survey, construction, operation, study, or cancellation categories.

These are not interchangeable. A licence category is not a delivery forecast, and capacity across applications, studies, cancellations, construction, and operation must not be summed as one project pipeline.

Capacity revisions are also preserved as two values when a reviewed exact DoED
identity match differs from the legacy Naxa snapshot by at least 10 MW. Generated
project data retain `capacity_mw` as the legacy value and add
`legacy_capacity_mw`, `current_official_capacity_mw`, source labels, and the
absolute difference. The current official capacity describes the regulatory
record only; it does not establish physical construction or delivery progress.
Publication is gated by the reviewed decisions in
`data/capacity_authority_decisions.csv`; a numerical threshold or fuzzy match
alone cannot activate the dual-value fields.

Reviewed exact/high single-record conflicts below the 10 MW publication
threshold use the separate `retain_legacy_below_materiality` decision. They are
removed from the reconciliation queue without adding dual-value fields; this
keeps the published map on the legacy snapshot while recording that the small
difference was checked against the current DoED record. The first review tranche
accepted 60 of 87 queue rows at or below 10 MW; 27 remain open because the
official overlay contains multiple records/categories, the benchmark and DoED
capacities disagree, or one normalized external identity maps to two local rows.

The 10–50 MW review tier accepted 26 single-record or single-category authority
matches. Eleven machine-labelled exact matches remain unresolved because their
overlay rows combine multiple DoED records, categories, or project-name variants:
Syar Khola HPP, Mewa khola HPP, Super Budhigandaki, Simbuwa Khola Hydroelectric
Project, Thulo Khola HPP, Upper Sankhuwa Khola HEP, Middle Chameliya HPP, Rauje
Khola HPP, Upper Tamor A HPP, Balephi A, and Ikhuwa Khola HEP. Those rows require
record-level adjudication before any current official capacity is published.

A subsequent record-level pass resolved 19 of the 29 residual capacity rows:
Ikhuwa Khola was approved for dual-value publication because the same promoter
links its cancelled 30 MW survey application to the current 40 MW generation
application; 14 other current active records were separated from unrelated historical
applications; and Kabeli-3, Myagdi Khola B, Molung Cascade, and Sabha Khola A HEP
were separated from HydroMap normalized-name collisions using the official DoED
crosswalk. Ten rows remain open: Thulo Khola HPP, Upper Dudh Khola HPP, Nar Khola
Hydro-Electric Project, Trishuli Khola, Daram Khola HEP, Bhalaudi Khola HEP, Tadi
Khola, Toj Khola HPP, Badigad HPP, and Gamari Gad HEP. Their generic river names,
different promoters, or exact correspondence to historical rather than current
records prevent a defensible lifecycle identity decision from the registry alone.

The official-source follow-up established that HydroMap's 288 hydro rows labelled `construction` exactly equal the 288 records in DoED's two current **generation-licence** tables (265 above 1 MW and 23 below 1 MW). The label therefore describes a regulatory bucket, not verified physical construction. Explorer-facing output now calls this layer **Generation licence** and keeps document-verified construction separate.

Zero matches for studied or cancelled categories therefore describe a difference in registry scope, not necessarily a gap in active-project coverage.

The spatial diagnostic compares each local registry reference point with the midpoint of HydroMap's `lat1`/`lat2`/`lon1`/`lon2` licence envelope. It is not a dam, intake, or powerhouse accuracy measurement.

## Provenance boundary

HydroMap is used as a public comparison benchmark. The generated artifacts contain derived metrics and bounded review fields rather than a mirror of its source dataset. HydroMap's public page states "Copyright. All Rights Reserved." Prefer current Department of Electricity Development records and project-specific evidence for facts published by TransparentGov.

## What the comparison tells us

- **Breadth:** HydroMap exposes 1,587 electricity records: 1,432 hydro, 149 solar, and 6 wind. The local public map has 572 hydro and 88 solar points. HydroMap is broader because it includes applications, government studies, and cancellations; that is not the same as having more delivery-ready projects.
- **Core hydropower identity coverage:** the initial conservative name pass matched 460 local hydro rows. The official DoED crosswalk plus 21 reviewed aliases raises local hydropower identity coverage to 542 of 572 rows (94.8%). Thirty local records remain unmatched.
- **Operating coverage:** 200 local points match an official operating record, compared with 213 hydro rows in DoED's operating tables. The residual is concentrated among small plants and identity/capacity revisions, not a wholesale operating-data gap.
- **Capacity disagreement is material:** 166 of 542 official matches differ by more than 0.01 MW and 129 differ by more than 1 MW. This shows why name identity and capacity reconciliation must be separate decisions; a changed capacity does not automatically mean a different project.
- **Lifecycle history matters:** 145 matched local projects have both active and cancelled official records in their lifecycle. Treating any historical cancellation as the current status would misclassify them; the crosswalk retains all categories and selects an explicit current primary record by precedence.
- **Complementary strengths:** HydroMap is useful for rapid breadth checks and category discovery. TransparentGov is stronger where it links projects to structured technical specifications, documentary claims, source pages, maps, and curated delivery status. DoED remains the production authority for current regulatory and operating status.

See `docs/doed-hydropower-registry-crosswalk.md` for the official-source pipeline and review boundary.
