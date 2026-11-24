---
title: Major Hydropower Developers Registry
type: data
created: 2026-11-24
updated: 2026-11-24
reviewed: 2026-11-24
review_due: 2027-02-24
sources: [doed-licensing-directive-2075, nepal-energy-institution-websites-2026, sebon-hydropower-offering-records]
tags: [developers, promoters, doed, nepse, registry, csv]
excerpt: The top 30 hydropower promoters by operating plus generation-licensed MW in DoED's registry, derived by a committed script; NEPSE tickers are left blank until verified.
caveat: Promoter names are grouped by a conservative normalisation of DoED's promoter field, so most rows are single-project special-purpose companies rather than corporate groups.
maturity: working-page
page_quality: record
---

# Major Hydropower Developers Registry

## Summary

[major_developers_nepse.csv](../../../data/major_developers_nepse.csv) ranks the top 30 promoters in the DoED hydropower registry (`data/processed/tables/doed_hydropower_registry.csv`) by operating plus generation-licensed capacity. It is built by `scripts/build_major_developers.py`.

## What This Shows

- The top 30 promoters hold 1,316 MW of the 3,910 MW in DoED's operating lists (34%) and 7,294 MW of the 12,364 MW under active generation licences outside those lists (59%).
- [[nea]] is the largest operating promoter, with 571 MW in DoED's operating records, plus 2,372 MW in survey licences.
- The largest single records are generation licences held by Upper Arun Hydro Electric Limited (1,063 MW) and Satluj Jal Vidyut Nigam Limited ([[arun-3]], 900 MW).

> [!finding]
> 24 of the top 30 promoters have no capacity in DoED's operating lists. Their rank comes entirely from generation licences, which are permits rather than delivered capacity.

## Coverage / Method

- **Scope:** active DoED records only. `operating_mw_approx` sums records in DoED's operating power-plant lists. `pipeline_mw_approx` sums generation licences outside those lists. Survey-licence MW is reported separately and excluded from the ranking.
- **Grouping:** promoters are grouped by name after removing case, punctuation and legal suffixes. No promoter is merged into a parent group, because group ownership is not in the DoED data.
- **Flagship slugs:** `flagship_project_slugs` links a record to `data/project_specs.csv` only when the river matches and capacity is within 1 MW. Five promoters have a match.
- **Tickers:** `nepse_ticker` is blank for every row. No NEPSE or SEBON listing record was checked against these promoter names. [[sebon-hydropower-offering-records]] covers selected offerings only.
- **Regenerate:** run `python scripts/build_major_developers.py` from the repository root.

## Caveats

- DoED's promoter field records the licence holder, often a project company, not the ultimate sponsor or group.
- Licence capacity can differ from built capacity.
- Records with a blank promoter (218 of 3,995 registry rows, any status) are excluded.
- `entity_type` is a naming heuristic (state utility or company as listed). It is not a legal classification.

## Linked Data

- [Major developers registry (CSV)](../../../data/major_developers_nepse.csv)
- [[data-energy-institutions]]

## Sources

- DoED licence and power-plant lists, via the processed registry; licensing rules in [[doed-licensing-directive-2075]]
- [[nepal-energy-institution-websites-2026]]
- [[sebon-hydropower-offering-records]]

## Related

[[doed]] · [[ippan]] · [[nea]]
