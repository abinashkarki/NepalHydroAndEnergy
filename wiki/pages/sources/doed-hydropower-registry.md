---
title: "DoED Hydropower Registry Tables (July 2026 Snapshot)"
type: source
created: 2026-11-24
updated: 2026-11-24
reviewed: 2026-11-24
review_due: 2027-02-24
source_type: registry
source_author: Department of Electricity Development
source_date: 2026-07-02
source_url: https://doed.gov.np/pages/powerplantsmorethan1
source_status: public-online
accessed: 2026-07-02
verification_status: primary-source-checked
sources: []
tags: [doed, hydropower, registry, operating, generation-licence, power-plants]
excerpt: The official DoED hydropower tables snapshot behind the repo's regulatory-status registry, including 213 operating hydro records totalling 3,909.7 MW.
caveat: Registry rows record regulatory status, capacity, promoter and licence-envelope coordinates; a generation licence does not by itself establish construction progress, and coordinates are envelope references rather than facility locations.
maturity: verified-core
page_quality: record
---

# DoED Hydropower Registry Tables (July 2026 Snapshot)

## Summary

The Department of Electricity Development publishes separate tables for operating hydropower plants (above and below 1 MW), generation licences, survey licences, licence applications, government-studied projects and each cancellation class. The repo snapshots 15 of these pages into `data/processed/tables/doed_hydropower_registry.csv` with page update dates and SHA-256 hashes recorded in `doed_hydropower_registry_summary.json`. Most pages were updated on 2 July 2026; the government-studied page was updated on 2 June 2026.

## Data Extracted

- Project name, capacity (MW), river and promoter
- Regulatory category (operating record, generation licence, survey licence, application, government study, cancellation)
- Record number, record and validity dates (Bikram Sambat)
- Commercial operation date (BS) for operating records
- Licence-envelope latitude/longitude ranges

## Data-Quality Notes

The snapshot holds 3,995 records: 213 operating hydro records (3,909.7 MW), 288 generation licences, 257 survey licences, 392 active applications, 66 government-study records and 2,779 cancellation records. The crosswalk to the 572 legacy local hydropower points, and the reviewed identity aliases, are documented in `docs/doed-hydropower-registry-crosswalk.md`.

Commercial operation dates are published in Bikram Sambat. Where `data/project_specs.csv` carries a `cod_year` derived from a DoED COD, the AD year is an approximate calendar conversion and is left blank when the BS date falls within a few days of 1 January.

## Limitations

- **Regulatory, not delivery, status:** only the operating table supports an operating status. A generation licence is a regulatory stage and is not evidence that civil works have begun.
- **Snapshot date:** plants commissioned, damaged or retired after 2 July 2026 are not reflected (for example, damage from the 26 August 2026 Bhotekoshi flood).
- **Coordinates:** licence-envelope midpoints are reference points, not surveyed facility locations.
- **Capacity:** registry capacity can differ from PPA capacity in NEA appendices and from legacy local registry values; differences are kept visible rather than reconciled silently.

## Related

- [[data-layer-hydropower-operating]]
- [[data-layer-hydropower-construction]]
- [[nea-annual-report-fy2025-26]]
- [[doed-licensing-directive-2075]]
