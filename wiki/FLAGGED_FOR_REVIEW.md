# Flagged for Review

Running log of ontology conflicts, split/merge candidates, duplicate concepts, and unresolved agent flags.

Review this file monthly. Resolve items by editing the wiki, merging pages, or updating `wiki/ONTOLOGY.md`.

## Open Items

- **[2026-05-12]** Hierarchy scan: remaining prohibited-term hits in data/source pages
  - Manual scan after the second data batch still finds candidate hierarchy-review hits outside the active batch:
    - `data/data-nepal-peak-load-curve-fy2024-25`: "explains why"
    - `data/data-layer-storage-shortlist`: two uses of "therefore"
    - `data/data-final-energy-mix`: "should" / "therefore" in solar interpretation paragraph
    - `sources/sahas-urja-benchmark-icra-2026`: "demonstrates that" in source summary
    - `data/data-storage-comparison`: "Nepal needs"
    - `data/data-layer-transmission-trace-gaps-qa`: "should improve next" and "explains why"
  - Proposed action: Review each hit for whether it is a true hierarchy violation or acceptable bounded wording; neutralize simple wording drift before adding this scan as an automated validator/test gate.
  - Flagged by: Codex — data cleanup batch 2 QA scan

- **[2026-05-12]** Data hygiene: `doed-licensing-directive-2075` missing source URL
  - No verified public URL is present in frontmatter for the DoED Licensing Directive 2075 source page
  - Proposed action: Locate the DoED directive PDF or official page and add `source_url`
  - Flagged by: Codex — tightly scoped source batch

- **[2026-05-12]** Data hygiene: `himalayan-capital-analysis` incomplete citation
  - Exact article metadata and URL are not yet in frontmatter
  - Proposed action: Locate the Himalayan Capital source URL / publication metadata and update the source page
  - Flagged by: Codex — tightly scoped source batch

- **[2026-05-11]** Data hygiene: `wb-nepal-power-sector-reform-2022` source URL missing
  - A previous `source_url` pointed to the Ganges Strategic Basin Assessment PDF, not the Power Sector Reform Roadmap; the false URL has been cleared
  - Proposed action: Locate the correct live URL for the Power Sector Reform Roadmap and update frontmatter
  - Flagged by: deepseek-v4-pro (hermes) — Sources Pass Batch B

- **[2026-05-11]** Content migration: `data-domestic-demand` value-capture framing
  - Interpretive content ("electrifying cooking, industrial heat, and transport at scale") reframed on data page to observation-level
  - Migrated to `syntheses/twenty-year-strategy.md` under Phase 2 (Store and Industrialize) as "Value capture: domestic electrification outranks export optimization" section
  - Downstream-check confirmed the argument did not exist on any claim/synthesis/intervention page before migration
  - Flagged by: human operator (during Data Pages Pass Session 6)

- **[2026-05-11]** Research gap: Electric cooking statistic (0.5% of households)
  - Figure is from 2021 WB estimate; no annual update series exists
  - AEPC or WB 2025 Economic Memo may have more recent data
  - Proposed action: Replace 0.5% figure if a more recent estimate is found from AEPC or WB 2025 CEM
  - Affects: `data-domestic-demand`, `concepts/domestic-led-hydro-strategy`, `syntheses/twenty-year-strategy`
  - Flagged by: human operator (during Data Pages Pass Session 6)

- **[2026-05-11]** Data hygiene: `adb-hydropower-growth-nepal` missing source URL
  - No live URL in frontmatter; verification path is local extracted text file only
  - Proposed action: Locate live ADB document URL and add to frontmatter, or mark as archive-only source
  - Flagged by: human operator (during Sources Pass Session 3)

- **[2026-05-11]** Data hygiene: `wecs-energy-synopsis-2024` PDF stub in raw/core/
  - `data/raw/core/wecs_energy_sector_synopsis_2024.pdf` is a 404 HTML stub, not the actual report
  - Live document exists only at external `source_url` (giwmscdnone.gov.np)
  - Proposed action: Replace with live document download, or permanently mark as external-only source with no local copy
  - Flagged by: human operator (during Sources Pass Session 2)

- **[2026-05-10]** Content gap: ICIMOD Koshi sediment quantitative figures
  - `sources/icimod-koshi-sediment-threats` lists directional findings only
  - Specific suspended sediment concentration, annual load (Mt/yr), and design-relevant parameters not yet extracted
  - Proposed action: Extract quantitative figures from PDF during a future sediment-focused session, or mark as permanently qualitative if the source does not provide them
  - Flagged by: OpenCode

- **[2026-05-10]** GOVERNANCE.md invariant added: concept/data page prescription boundary
  - Invariant #9 added: "No policy prescriptions on concept or data pages. Concept pages may describe implications but may not prescribe responses. The line is 'this means X' versus 'Nepal should do X.'"
  - Motivated by two hierarchy violations: `data-storage-comparison` (Week 2) and `buildability` (Week 6)
  - Proposed action: No further action needed; invariant is now active. Review at monthly review for enforcement consistency.
  - Flagged by: human operator

- **[2026-05-10]** Exemplar fix: `data-storage-comparison` hierarchy violation still present
  - Week 2 audit log recorded reframing of interpretive language on `data-storage-comparison`, but the language ("The bottleneck is capital, governance, and institutional will, not geology") was still present on disk at Week 7.
  - Root cause: Week 2 edit was not committed or was subsequently reverted.
  - Impact: All data-page edits since Week 2 used a non-compliant exemplar.
  - Proposed action: Fixed during Week 7 pre-task. Verified downstream existence of the interpretive framing on [[master-thesis]] and [[bottleneck-hierarchy]] before reframing.
  - Flagged by: human operator

- **[2026-05-11]** Tier mismatch: `entities/upper-arun` under-built for `analysis` tier
  - Page is short for an `analysis` page and has no quantified parameters (capacity, status, timeline). Declared `analysis` but closer to `brief`.
  - Proposed action: Deep-research session with actual project data (NEA annual report, DoED registry) to bring to `analysis` minimum. Do not attempt structural template fill alone.
  - Affects: `entities/upper-arun`
  - Flagged by: OpenCode (Session 9)

- **[2026-05-10]** GOVERNANCE.md standing note: data pages as highest-risk category for hierarchy violations
  - Data pages have the highest hierarchy violation rate of any category (2 violations in 5 pages in Week 7, including the most severe found across 7 weeks).
  - Pattern: data pages are where analysis gets parked when it hasn't found its synthesis home yet.
  - Proposed action: Add standing note to GOVERNANCE.md calling out data pages as highest-risk category; consider including spot-check of recently edited data pages in monthly drift review.
  - Flagged by: human operator

## Resolved Items

| Date | Item | Resolution |
|---|---|---|
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
