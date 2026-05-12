# Flagged for Review

Running log of ontology conflicts, split/merge candidates, duplicate concepts, and unresolved agent flags.

Review this file monthly. Resolve items by editing the wiki, merging pages, or updating `wiki/ONTOLOGY.md`.

## Open Items

- **[2026-05-11]** Data hygiene: `wb-nepal-power-sector-reform-2022` source URL missing
  - A previous `source_url` pointed to the Ganges Strategic Basin Assessment PDF, not the Power Sector Reform Roadmap; the false URL has been cleared
  - Proposed action: Locate the correct live URL for the Power Sector Reform Roadmap and update frontmatter
  - 2026-05-12 follow-up: searched World Bank documents and public web for exact standalone "Nepal Power Sector Reform Roadmap" / "Power Sector Reform Roadmap 2022" hits. Found related World Bank PSRSHD project and restructuring documents, but not a verified standalone roadmap matching this source page. Leave open rather than attach a non-equivalent URL.
  - Flagged by: deepseek-v4-pro (hermes) — Sources Pass Batch B

## Resolved Items

| Date | Item | Resolution |
|---|---|---|
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

*Last reviewed: 2026-05-11*
*Next review: 2026-06-10*
