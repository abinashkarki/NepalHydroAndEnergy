# Agent Handoff — Nepal Energy Wiki: May 2026 State

## Current State (as of commit `0ad238c`)

**345 wiki pages.** Zero `[UNVERIFIED]` and zero `[REQUIRES EXACT CITATION]` flags
remaining. 5 `[Under research]` flags on peripheral pages (hydro-insurance,
ipo-bailout) that need inaccessible legal documents.

### What was just completed

The wiki's evidence structure has been substantially strengthened across three
recent sessions. Here's the trajectory:

**Round 1 — Entity page narratives (7 pages, auto-stub → Tier A):**
- Marsyangdi (69 MW, 36-year-old fleet anchor at 97% of design)
- Kulekhani I (60 MW, Nepal's only reservoir, 45m drawdown)
- Kulekhani II (32 MW, cascade link, 39 years old)
- Kulekhani III (14 MW, cascade tail-end, 117% target / 79% design) — NEW page
- Madhya Marsyangdi (70 MW, 107.6% of design — highest in NEA fleet)
- Upper Trishuli 3A (60 MW, flood-damaged, 72.7% of design)
- Trishuli (24 MW, oldest plant, 1967, 60% of design, rehab in progress)
- Upper Marsyangdi A (50 MW, cascade anchor, learning curve framing)

All rewritten with primary-source data from NEA FY 2081/82 annual report.
Generator tags changed from auto-stub to specs-refresh (removes "no narrative"
badge in explorer UI). Status tags corrected (UT3A and others: under-construction
→ operating).

**Round 2 — Kulekhani sedimentation + citation fixes:**
- Extracted sedimentation data from JICA Storage Master Plan Vol 1 (PDF in repo):
  85.3 MCM original, 25.3 MCM sediment by 2010 = ~30% loss, commissioning Dec 1982
- Updated to ~40% loss from post-2010 DGPS bathymetry (2021 study): 20.4M m³ total
  lost, 14M m³ active live storage lost. Declining rate (13.3→6.6→4.8 t/ha/yr)
- Applied to kulekhani-i, sediment-as-design-constraint, storage-deficit
- Fenner School citation page numbers fixed (p. 20) across 3 pages
- Chilime PPA rate verified (NPR 7.57/kWh blended, 37.1% revenue advantage)

**Round 3 — New research from external deep research agent:**
- Upper Tamakoshi: corrected generation from ~59% to 85-90% (UKHLL audited accounts)
  with FY2080/81 (90.2%) and FY2081/82 (67.0% — 88-day flood shutdown). Added
  ICRA D default, 88:12 D/E at COD, Rolwaling diversion (212 GWh).
- Khimti-I: rewritten from 46-line stub. 1996 USD PPA, 103% generation, Statkraft/
  Eviny exit to BPC (Sept 2025), Khimti-Dhalkebar corridor.
- Likhu-2: rewritten from 40-line stub. Stranded generation (60→91% after NEA
  transformer upgrade), MV Dugar + UAE FDI, Likhu-4 120→52 MW redesign story.
- ad-penalties: Article 10.2 confirmed (no curtailment exemption). Article 10.1(Ka)
  10% reserve margin with zero compensation. 16% figure confirmed NOT statutory.
- q-design-discharge: Upper Tamakoshi rows corrected, Likhu-2 framed as
  transmission-constrained, Urja Khabar source chain clarified.

**Round 4 — Research gap resolution + concept page cross-links:**
- ERC reservoir directive (2026) fully cited in ppa-pricing
- Electricity Act 2049 Sec.11 royalty/tax provisions cited
- DoED Licensing Directive 2075 Nepali title, Q45 mandate, Q80 exception
- WECS/DHM 1990 official title, data "to 1985", DHM 2016 update
- ~25 entity cross-links added to 7 concept pages (buildability,
  stranded-generation, storage-deficit, q-design-discharge, seasonal-mismatch,
  ppa-pricing, nea-triple-authority)

**Round 5 — Likhu cascade completion:**
- Likhu-1 (77 MW, cascade leader, 80% take-or-pay, MV Dugar FDI model)
- Likhu-4 (52.4 MW, 120→52 MW export redesign after India wheeling dispute,
  desanding basin collapse)

## Highest-Leverage Remaining Tasks

### Tier 1 — Do immediately (low effort, high impact)

**1. Write Likhu Khola A page (29 MW)**
Completes the Likhu cascade at 4/4. Data is in the same research PDF at
`data/raw/research/Likhu Hydropower Cascade Data Request - Google Docs.pdf`.
The page already exists as an auto-stub at `wiki/pages/entities/likhu-khola-a.md`.
Narrative: smallest cascade plant, MD Dugar + UAE FDI, CARE-NP BB+ rating,
same New Khimti corridor dependency. COD Feb 2022.

**2. Create 6 missing source pages for q-design-discharge**
These slugs are referenced in `q-design-discharge.md` frontmatter but have no
source pages:
- `doed-licensing-directive-2075` (directive now cited, just needs a page)
- `wecs-dhm-1990-methodology` (methodology now cited, just needs a page)
- `urja-khabar-generation-audit` (already have a page at
  `sources/urja-khabar-ipp-generation-audit.md` — just need to align the slug)
- `chilime-annual-report-fy2078-79`
- `care-ratings-sanima-mai`
- `ukhl-annual-report`

**3. Write Middle Tamor page (60 MW)**
One of the largest remaining Tier C operating/under-construction stubs.
Likely has data in NEA annual report if NEA-owned.

### Tier 2 — Medium effort

**4. Khimti-II page (49 MW)**
Connected to Khimti-I (same corridor, BPC post-2025). Under construction.
Would strengthen the Khimti-Dhalkebar corridor congestion argument.

**5. Tamakoshi-V page (98 MW)**
Largest remaining Tier C stub in the Tamakoshi basin. Same developer ecosystem
as Upper Tamakoshi.

**6. Trishuli-Galchhi (60 MW) + Upper Lapche Khola (52 MW)**
Large under-construction private IPPs with no narrative.

### Tier 3 — Deep research (needs external documents)

**7. UKHLL audited accounts** — confirmed to exist at utkhpl.org.np. Would add
primary-source citations to Upper Tamakoshi financial tables.

**8. Urja Khabar January 2026 article** — confirmed as PDF at urjakhabar.com.
Would provide the exact source text for the Q-design performance claims.

**9. ADB Kulekhani PCR** — Hydro-Lab/NTNU has conducted multiple bathymetric
surveys. The data probably exists but wasn't found in the deep research pass.

**10. PPA template text** — the central unresolved legal question. No source
found yet.

## Key File Paths for Quick Reference

| What | Where |
|---|---|
| Entity pages (project narratives) | `wiki/pages/entities/` |
| Concept pages (thesis arguments) | `wiki/pages/concepts/` |
| Source pages (research metadata) | `wiki/pages/sources/` |
| NEA annual report PDF | `data/raw/projects_storage/nea_annual_report_2024_2025.pdf` |
| JICA IPSDP Vol 2 | `data/raw/corridor_tracing/jica/jica_ipsdp_main_report_vol2.pdf` |
| JICA Storage Master Plan Vol 1 | `data/raw/lead1_sources/jica_storage_master_plan_vol_1.pdf` |
| Research compilations (UKHLL, Likhu, etc.) | `data/raw/research/` |
| Project specs CSV | `data/project_specs.csv` |
| Explorer app | `wiki/explorer/index.html` |
| Build scripts | `scripts/` |
| Metadata (search index, backlinks) | `wiki/explorer/shared/wiki-*.json` |

## Build Commands

```bash
make wiki-index    # Regenerate metadata (backlinks, search, page index)
make validate      # Check for broken links, orphaned pages
make serve         # Local preview at localhost:8765/wiki/explorer/
```

Never commit without running `make validate` first. The validator catches broken
wikilinks (case-sensitive slugs) and backlink inconsistencies.

## Convention Reminders

- Generator types: `specs-refresh` for pages with narrative (spec block
  auto-refreshes, prose survives), `auto-stub` only for truly bare stubs
- `<!-- generated:specs:start -->` / `<!-- generated:specs:end -->` markers
  enclose auto-generated spec content. All narrative goes BELOW the end marker.
- Wikilinks are case-sensitive — `[[likhu-2]]` not `[[Likhu-2]]`
- `[UNVERIFIED]` and `[REQUIRES EXACT CITATION]` flags should be zero
- Status tags in frontmatter determine explorer layer placement
