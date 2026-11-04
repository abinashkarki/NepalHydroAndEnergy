# Official DoED hydropower registry crosswalk

This pipeline converts Nepal Department of Electricity Development tables into an auditable regulatory-status registry, then crosswalks it to the 572 hydropower points used by the explorer. It does not infer construction progress from a licence.

## Rebuild

```bash
python scripts/build_doed_hydropower_registry.py
python scripts/build_doed_project_status_overlay.py
python scripts/apply_doed_project_status_overlay.py
python scripts/build_wiki_fact_index.py
```

The registry builder fetches 15 official DoED pages, validates minimum row counts, records each page's update date and SHA-256 hash, and writes:

- `data/processed/tables/doed_hydropower_registry.csv`
- `data/processed/tables/doed_hydropower_registry_summary.json`

The crosswalk writes:

- `data/processed/tables/doed_project_status_overlay.csv`
- `data/processed/tables/doed_project_crosswalk_review.csv`
- `data/processed/tables/doed_project_status_overlay_summary.json`

Reviewed identity variants live in `data/project_identity_aliases.csv`. Similarity scores only prioritize review; they do not create accepted identities.

Reviewed false nearest-neighbour suggestions live separately in
`data/doed_crosswalk_dispositions.csv`. A rejection is keyed to the official
project, regulatory category, record number, and the specific suggested local
project. The generated review CSV retains the official row with a
`rejected_*` decision, while the internal dashboard removes that reviewed
suggestion from its actionable identity queue. This does **not** match the
official record, remove it from the official registry, change a local map
status, or prevent a different future candidate from entering review.

## Current result

The source snapshot contains 3,995 records: 3,994 hydro and one wind record. It includes 213 operating hydro records, 288 generation licences, 257 survey licences, 392 active applications, 66 government study records, and 2,779 cancellation records. DoED pages were mostly updated 2 July 2026; the government-studied page was updated 2 June 2026.

Of 572 local hydropower points:

- 545 (95.3%) match official records;
- 519 are conservative normalized-name matches;
- 26 use reviewed aliases;
- 27 remain unmatched;
- 201 match an official operating record;
- 239 have a generation licence as their primary regulatory category;
- 63 unmatched official operating or generation-licence records remain visible
  in the review artifact;
- 31 false nearest-neighbour suggestions have an explicit reviewed rejection;
- 32 suggestions remain unreviewed, including 16 absent operating records that
  are tracked in the separate missing-operating coverage queue;
- 16 records remain in the dashboard's actionable identity-review queue.

The 13 July identity review added four high-confidence aliases. These were not
accepted from the nearest-neighbour suggestion alone: each was checked against
the current official record and the legacy local registry.

| Local record | Official DoED identity | Evidence basis |
|---|---|---|
| `Sabha Khola A HEP` | `Super Sabha Khola A HPP` | Same A unit, exact 9.55 MW capacity and licence-envelope midpoint, and promoter spelling variant. This also corrects a prior normalized-name collision with the separate 10.4 MW `Sabha Khola A` record held by another promoter. |
| `Upper Pikhuwa HPP` | `Upper Pikhuwa Khola HEP` | Same upper scheme and promoter, exact licence-envelope midpoint, with the 2.0 to 4.9 MW capacity revision retained rather than hidden. |
| `Ghunsa-Tamor HPP` | `Tamor Khola` | Identical 43 MW capacity, promoter, and licence-envelope midpoint. |
| `Sabha Khola C HPP` | `Sabha Khola C HEP (Cascade)` | Same C unit, promoter spelling variant, and a midpoint separation below 0.5 km; the 4.2 to 9.9 MW capacity revision remains explicit. |

No rejected suggestion is an alias. In particular, high name or location
scores do not collapse numbered or directional
schemes such as `Upper Marsyangdi 1` / `Upper Marsyangdi A`, `Budhi Gandaki Ka` /
`Budhi Gandaki Kha`, `Tamor Khola` / `Tamor Khola-5`, or `Tallo Indrawati` /
`Indrawati-III`; their capacities, promoters, unit names, or regulatory histories
show that they must remain separate unless stronger project-specific evidence is
found.

## Interpretation boundary

Three fields must stay separate:

1. **Delivery status** — operating, under construction, stalled, pre-construction, and similar real-world states supported by project-specific evidence.
2. **Regulatory status** — survey licence, generation licence, application, government study, cancellation, or operating-register entry from DoED.
3. **Legacy licence type** — the Survey/Generation/Operation value carried by the original Naxa-linked map dataset.

Only a DoED operating-table record is promoted to official `doed_delivery_status=operating`. A generation licence is displayed as **Generation licence**, never as evidence that civil works have begun. Curated project evidence may separately set `status=under-construction`.

Historical records are preserved. A project can have both active and cancelled records across its lifecycle; the overlay records this as `doed_record_status=mixed` and selects a primary regulatory category using documented precedence rather than treating the cancellation as automatically current.

### Known legacy content debt

The explorer layer taxonomy and structured fact index use the corrected distinction. However, 38 older `auto-stub` entity pages and two `specs-refresh` pages still contain the inherited phrase `under construction (generation licence)`. The generator has been corrected so it will not create that wording again. Existing narrative pages require a separate governed evidence review because some projects may genuinely be under construction while others only hold a licence; they must not be bulk-relabelled without project-specific sources.

## Official sources

The source manifest and hashes are stored in `doed_hydropower_registry_summary.json`. The principal current tables are the DoED [operating plants above 1 MW](https://doed.gov.np/pages/powerplantsmorethan1), [generation licences above 1 MW](https://doed.gov.np/pages/clhydromorethan1), [survey licences above 1 MW](https://doed.gov.np/pages/hydromorethan1), and [generation-licence applications](https://doed.gov.np/pages/appclhydro). Separate pages cover sub-1 MW records, government studies, and each cancellation class.
