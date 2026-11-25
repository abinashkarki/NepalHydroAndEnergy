---
title: Nepal Energy Institutions Registry
type: data
created: 2026-11-24
updated: 2026-11-25
reviewed: 2026-11-24
review_due: 2027-02-24
sources: [nepal-energy-institution-websites-2026, nea-annual-report-fy2025-26, wecs-energy-synopsis-2024, aepc-renewable-framework]
tags: [institutions, governance, registry, csv]
excerpt: A 15-row registry of Nepal's core energy institutions, recording each one's establishment date, statutory basis, parent body, mandate, website and public datasets, with unknowns left explicit.
caveat: Most rows rest on the institutions' own websites as read on 24 November 2026; where a site did not state a date or act, the field is `unknown` rather than filled from memory.
maturity: working-page
page_quality: record
---

# Nepal Energy Institutions Registry

## Summary

[energy_institutions.csv](../../../data/energy_institutions.csv) lists 15 institutions:

- ministry and departments: [[moewri]], [[doed]], DHM
- planning and promotion bodies: [[wecs]], [[aepc]]
- utility: [[nea]]
- regulators: [[erc]], SEBON
- state-promoted companies: [[rpgcl]], [[hidcl]], VUCL
- NEA subsidiary for fibre and data centres: [[nepal-digital-infrastructure|NDICL]]
- investment board: [[ibn]]
- industry association: [[ippan]]
- petroleum supplier: [[noc]]

Each row carries the source URL, locator and verification date.

## What This Shows

| Field | Rows known | Rows `unknown` |
|---|---:|---:|
| Established | 9 | 6 (MoEWRI, WECS, IBN, NOC, SEBON, DHM) |
| Official website | 14 | 1 (NDICL) |
| Entity page in this wiki | 12 | 3 (VUCL, SEBON, DHM) |

> [!finding]
> Three of the state-promoted energy companies publish their founding as a Government of Nepal decision or establishment date and do not name an enabling act on their homepages: HIDCL (11 July 2011), RPGCL (12 July 2015) and VUCL (20 November 2016).

> [!finding]
> NEA is listed as a promoter shareholder of both RPGCL and VUCL, and HIDCL is listed as a promoter shareholder of VUCL.

## Coverage / Method

- The rows come from the official-website review recorded in [[nepal-energy-institution-websites-2026]].
- NEA's incorporation date and act come from [[nea-annual-report-fy2025-26]] (PDF p.159). NOC's row uses [[wecs-energy-synopsis-2024]], because the NOC site returned HTTP 403.
- NDICL's row comes from Section 19 of [[nea-annual-report-fy2025-26]] (PDF p.138); no official website was located.
- AEPC's 1996 founding year comes from the existing [[aepc]] page.
- The runbook slug `vucil` is recorded as `vucl`, the company's own abbreviation.

## Caveats

- Website statements are not statutes, and ownership percentages are not published by the state-promoted companies.
- The DHM homepage header reads "Nepal Meteorological Department". The registry keeps the DHM slug and does not resolve the naming change.
- New entity pages were created for ERC, DoED, MoEWRI, RPGCL, HIDCL, IBN, IPPAN and NOC. No pages were created for VUCL, SEBON or DHM.

## Linked Data

- [Energy institutions registry (CSV)](../../../data/energy_institutions.csv)
- [[data-major-developers]] — promoter-level capacity registry

## Sources

- [[nepal-energy-institution-websites-2026]]
- [[nea-annual-report-fy2025-26]]
- [[wecs-energy-synopsis-2024]]
- [[aepc-renewable-framework]]

## Related

[[nea]] · [[erc]] · [[doed]] · [[moewri]]
