# Flagged for Review

Running log of ontology conflicts, split/merge candidates, duplicate concepts, and unresolved agent flags.

Review this file monthly. Resolve items by editing the wiki, merging pages, or updating `wiki/ONTOLOGY.md`.

## Open Items

- **[2026-07-10]** Capital-markets evidence: IPO and rights-share claims need issuer-level primary-document reconciliation
  - Approved-prospectus use-of-proceeds extraction is complete for the bounded four-issuer cohort: Ankhu Khola, Joshi Hydropower, People's Power and Terhathum Power. Every issuer assigns some rights proceeds to financing liabilities, but the expansion, repair, promoter-advance and bank-repayment mixes differ materially.
  - Post-offer evidence now shows audited rights issuance and debt reduction for Ankhu Khola, issuer-reported capital completion and long-term debt falling to zero for People's Power, and an issuer statement that Terhathum completed its rights issue and used proceeds to repay long-term bank borrowing. People's Power and Terhathum evidence remains unaudited at the current reporting cutoff.
  - Proposed action: obtain Joshi's final allotment and post-offer balance sheet, trace Ankhu Khola's full planned NPR 800 million Ankhu Khola-2 investment, obtain audited FY 2082/83 confirmation for People's Power and Terhathum, and declare a broader sampling rule before making any sector-wide "bailout rate" finding.
  - Flagged by: Codex — capital-markets evidence pass

## Resolved Items

| Date | Item | Resolution |
|---|---|---|
| 2026-07-19 | Retired national curtailment estimate and Hetauda–Dhalkebar status conflict | Removed the unsupported national daily curtailment band and stale remaining-tower counts from public claim, entity, journalist and decision-dossier surfaces. The canonical claim now states a material delivery constraint without ranking or quantifying national curtailment. Official July 2026 NEA notices establish ongoing conductor stringing, not completion or energisation. Added `data/retired_claims.json` and `scripts/check_retired_claims.py` to prevent reintroduction. |
| 2026-07-13 | Upper Tamakoshi: Rolwaling delivery-status contradiction | Closed by retiring the unsupported complete-halt and blockade claims. UTKHPL's FY 2080/81 annual statements establish construction/EPC/PPA activity at their reporting cutoff, while the May 2026 filing establishes NPR 2.103 billion of capital work in progress but no current package percentage, stop/restart date or commissioning schedule. Current delivery status remains explicitly unverified rather than contradictory. |
| 2026-07-13 | Data hygiene: `wb-nepal-power-sector-reform-2022` source identity and URL | Closed by correcting the legacy-slug page into a two-document World Bank evidence record. The 2025 Country Economic Memorandum now supports the 42,000 MW figure; the 2018 Energy Development Policy Credit programme document supports the dated reform-study context and identifies a 2016 power-market roadmap study. No unsupported standalone 2022 report is asserted. |
| 2026-07-13 | Stage 1 project-monitoring reconciliation: second priority batch | Closed after verifying that Arun-3, Budhigandaki, Pancheshwar, Mugu Karnali and Gorakhpur–Butwal now have governed primary-source records, dated status boundaries and explicit monitoring gaps. Missing DPR, financing, package-progress and synchronized-commissioning evidence remains visible on the entity pages rather than being inferred. |
| 2026-07-13 | Stage 1 project-monitoring reconciliation: three lighthouse dossiers | Closed after verifying that Dudhkoshi's unsupported 200 MW pumped-storage component was removed, Upper Karnali distinguishes partner participation from financial close, and April–May 2026 UTKHPL filings were ingested. The Rolwaling delivery-status contradiction was tracked separately and was closed later on 2026-07-13 by retiring unsupported status claims. |
| 2026-05-12 | Hierarchy scan: remaining prohibited-term hits in data/source pages | Neutralized wording in `data-nepal-peak-load-curve-fy2024-25`, `data-layer-storage-shortlist`, `data-final-energy-mix`, `sources/sahas-urja-benchmark-icra-2026`, `data-storage-comparison`, and `data-layer-transmission-trace-gaps-qa`. Closed after local scan. |
| 2026-05-12 | Data hygiene: `doed-licensing-directive-2075` missing source URL | Added verified DoED public URL for the fifth-amendment version and corrected page language that had implied no amendments since issuance. Closed. |
| 2026-05-12 | Data hygiene: `himalayan-capital-analysis` incomplete citation | Added Himalayan Capital *The Pulse* Shrawan 2081 PDF URL and source date; clarified it is a monthly market report section. Closed. |
| 2026-05-12 | Content migration: `data-domestic-demand` value-capture framing | Verified migrated synthesis home in `twenty-year-strategy` under "Value capture: domestic electrification outranks export optimization"; data page now points to synthesis for interpretation. Closed. |
| 2026-05-12 | Research gap: Electric cooking statistic (0.5% of households) | Added `wb-household-electric-cooking-nepal-2025` source page. The 2025 source corroborates sub-1% adoption but does not provide a newer annual share, so the 2021 0.5% baseline remains with an explicit caveat. Closed. |
| 2026-05-12 | Data hygiene: `adb-hydropower-growth-nepal` missing source URL | Added verified ADB PDF URL for *Hydropower Development and Economic Growth in Nepal*. Closed. |
| 2026-05-12 | Data hygiene: `wecs-energy-synopsis-2024` PDF stub in raw/core/ | Verified `data/raw/core/wecs_energy_sector_synopsis_2024.pdf` is now a real 167-page PDF and updated the source page's local-PDF status. Closed. |
| 2026-05-12 | Content gap: ICIMOD Koshi sediment quantitative figures | Downloaded current ICIMOD record PDF, extracted text, and added sediment-load / soil-loss / station-load figures to `sources/icimod-koshi-sediment-threats`; corrected source date and URL. Closed. |
| 2026-05-12 | GOVERNANCE.md invariant added: concept/data page prescription boundary | Verified invariant #9 is present in `wiki/GOVERNANCE.md`. Closed. |
| 2026-05-12 | Exemplar fix: `data-storage-comparison` hierarchy violation still present | Verified the old "bottleneck is capital..." language is absent; also neutralized remaining `Nepal needs` wording in the storage-need section. Closed. |
| 2026-05-12 | Tier mismatch: `entities/upper-arun` under-built for `analysis` tier | Added official UAHEL source page and updated `upper-arun` with capacity, energy, peaking, evacuation, schedule, and revised limitations. Closed. |
| 2026-05-12 | GOVERNANCE.md standing note: data pages as highest-risk category for hierarchy violations | Verified `wiki/GOVERNANCE.md` includes the data-page high-risk note and interpretation policy. Closed. |
| 2026-05-10 | Content migration: IRENA REmap Nepal strategic framing | Migrated to `syntheses/solar-role-in-winter-deficit` — added "## Benchmarking context" section. Updated `sources/irena-remap-nepal` with cross-reference. Closed. |
| 2026-05-10 | Ontology confidence classification: `claim-climate-harder-not-easier` | Updated `wiki/ONTOLOGY.md` canonical claims table from `medium-high` to `high`. Page qualifier (IPCC HKH convergence) preserved. Closed. |
| 2026-05-10 | Validator enhancement (HIGH PRIORITY): required section headings by page type | Built into `scripts/validate_repo.py` as `validate_required_sections()`. Warns (not hard-fail) on missing canonical headings per TEMPLATES.md. Closed. |

## Monitored External Dependencies

- **[2026-07-11]** Operational curtailment dataset response — monitoring
  - The plant-level availability, dispatch-event, accepted-energy and reason-code records required for a national curtailment measure are not exposed by the reviewed public NEA portals.
  - A data request was sent on 11 July 2026 and is awaiting response. A 13 July recheck found the Generation Directorate operational-report page still displaying `Coming soon` and the monthly-generation area displaying `No Record Found`.
  - Monitoring action: preserve any acknowledgement or response with provenance, coverage and redaction metadata; do not derive a national curtailment estimate from capacity, annual generation or aggregate system reports.
  - Monitoring record: `docs/research_briefs/curtailment_dispatch_data_acquisition.md`

## How to add an item

```
- **[DATE]** Term/concept: description of conflict or uncertainty
  - Proposed action: merge, split, rename, add to ontology
  - Flagged by: agent or human name
```

## Categories of items to flag

- New term that may overlap with an existing canonical term
- Page that feels like it belongs to two categories
- Claim that contradicts another claim without explicit cross-reference
- Source page that has become mini-analysis
- Data page with interpretive language that should be in a synthesis
- Entity page with no generator field or missing source attribution
- Duplicate or near-duplicate slugs

---

*Last reviewed: 2026-07-19*
*Next review: 2026-10-19*
