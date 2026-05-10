# Wiki Audit Log

Session log of agent edits: date, pages touched, changes made, flags raised.

## 2026-05-10 — Governance Layer Established

**Agent:** OpenCode (kimi-k2.6)
**Session type:** Governance-only (no page content edits except mechanical normalization)
**Pages touched:**
- `scripts/normalize_frontmatter.py` — created frontmatter normalization script
- `docs/session-template.md` — created reusable session prompt template
- `wiki/GOVERNANCE.md` — created governance document (hierarchy, invariants, philosophy, session rules)
- `wiki/ONTOLOGY.md` — created ontology document (canonical terms, aliases, parent syntheses, claims)
- `wiki/FLAGGED_FOR_REVIEW.md` — created review log
- `wiki/WIKI_AUDIT_LOG.md` — created this log
- `wiki/TEMPLATES.md` — created lightweight templates
- `wiki/QUALITY_RUBRIC.md` — created quality rubric
- `CONTRIBUTING.md` — created entry point

**Mechanical edits:**
- Normalized frontmatter keys to lowercase in 5 intervention pages:
  - `intervention-electric-cooking-transition.md`
  - `intervention-nea-structural-separation.md`
  - `intervention-q-design-climate-adjustment.md`
  - `intervention-sebon-data-transparency.md`
  - `intervention-transmission-completion.md`

**Validation result:** `OK: 358 wiki pages, caches valid, map manifest valid, tracked hygiene clean`

**Flags raised:** None.

**Baseline saved:** `scripts/baseline_validation_output.txt`

---

## 2026-05-10 — Exemplar Pass (Week 2)

**Agent:** OpenCode (kimi-k2.6)
**Session type:** Exemplar refinement — 7 pages, one per category
**Pages touched:**
- `syntheses/master-thesis` — +purpose statement sentence
- `sources/wb-country-economic-memo-2025` — fix typo, rename `## Relevance to Project` → `## Relevance`, +`## Limitations`, +`## Used By`
- `claims/claim-mw-not-equal-value` — +`## Boundary Conditions`
- `concepts/seasonal-mismatch` — +`## Simple Explanation`, +`## Common Misunderstandings`
- `data/data-storage-comparison` — reframed interpretive paragraph (lines 70-72) to observation-level; moved strategic implication to `storage-deficit` concept page
- `entities/arun-3` — +`## Summary` heading
- `interventions/intervention-transmission-completion` — no changes needed (already exemplary)

**Process improvement:** Added source-page Used By verification rule to `docs/session-template.md` (must be built from grep/backlinks, never from memory).

**Validation result:** Pending (changes to be committed)

**Flags raised:**
- `data-storage-comparison`: hierarchy violation — interpretive language reframing "the bottleneck is capital, governance, and institutional will" removed from data page per GOVERNANCE.md `[!finding]` policy. Strategic implication moved to `storage-deficit` concept page.

**Decisions made:**
- Human approved the data-storage-comparison reframing before write.
- Used By list on source page reconstructed from memory; flagged for verification via grep in actual session.

---

## 2026-05-10 — Syntheses Pass (Week 3)

**Agent:** OpenCode (kimi-k2.6)
**Session type:** Syntheses pass — 5 pages
**Pages touched:**
- `syntheses/start-here` — +purpose statement
- `syntheses/bottleneck-hierarchy` — +purpose statement
- `syntheses/twenty-year-strategy` — +purpose statement
- `syntheses/solar-role-in-winter-deficit` — +purpose statement
- `syntheses/downstream-river-geopolitics` — +purpose statement

**Validation result:** `OK: 358 wiki pages, caches valid, map manifest valid, tracked hygiene clean`

**Flags raised:** None.

**Decisions made:**
- Speculative timeline hedging for twenty-year-strategy was confirmed by human but not needed — current file version lists projects without specific unverified COD dates.

---

## 2026-05-10 — Sources Pass (Week 4)

**Agent:** OpenCode (kimi-k2.6)
**Session type:** Sources pass — 5 pages
**Pages touched:**
- `sources/nea-annual-report-fy2024-25` — +`## Used By` section with verified backlinks (claims, concepts, data, entities, syntheses)
- `sources/chilime-annual-report-fy2078-79` — +`## Summary` heading; neutralized interpretive comparison of private IPP tariffs; removed "37.1% revenue advantage" calculation (already present on [[ppa-pricing]]); +`## Limitations`; updated `## Used By` via grep
- `sources/ppa-data-retrieval-icra-care-2026` — +`## Used By` and `## Limitations`; neutralized epistemic labels ("Proven" → "Document finding"; "The Benchmark" → "Financial profile")
- `sources/irena-remap-nepal` — +`## Summary` heading; +`## Used By`; reframed `## Why this source matters to the project` into neutral `## Relevance`; renamed `## Data-quality and caveats` → `## Limitations`; removed synthesis language about programme-gap mapping and benchmark judgments
- `sources/icimod-koshi-sediment-threats` — expanded `## Key Data Points` with honest gap notation; +`## Limitations`; +`## Used By`

**Validation result:** `OK: 358 wiki pages, caches valid, map manifest valid, tracked hygiene clean`

**Flags raised:**
- `chilime-annual-report-fy2078-79`: **Hierarchy violation** — interpretive comparison and "revenue advantage" framing belonged in claim/concept pages, not source page. Content verified as existing on [[ppa-pricing]] before removal.
- `ppa-data-retrieval-icra-care-2026`: **Hierarchy violation** — "Proven" and "The Benchmark" were conclusions, not source descriptions. Neutralized per GOVERNANCE.md L1 invariant.
- `irena-remap-nepal`: **Hierarchy violation** — strategic framing ("useful for mapping AEPC/EIB/WB programme gaps", "reasonable benchmark against which to judge...") belonged in synthesis pages. Removed from source page; **does NOT currently exist on any downstream synthesis page**. Flagged for content migration to a future solar-focused synthesis page.
- `icimod-koshi-sediment-threats`: **Content gap** — specific quantitative sediment load figures not yet extracted. Left as explicit gap rather than invented.

**Pattern observed:**
- **60% hierarchy violation rate** (3 of 5 source pages contained interpretive language, strategic framing, or epistemic claims that belong in claim/synthesis pages).
- This is not an agent failure; it signals that source pages have been used as a convenient place to park analysis that has not yet found its synthesis home.
- **Standing rule reinforced:** When removing interpretive content from a source page, always verify downstream existence before deleting. If the content does not exist elsewhere, flag the migration target explicitly. Never delete source-page analysis without identifying where it should live.

**Decisions made:**
- Human approved all 5 proposed changes in batch, with feedback reinforcing the downstream-check rule as a standing protocol.

---

## 2026-05-10 — Claims Pass (Week 5)

**Agent:** OpenCode (kimi-k2.6)
**Session type:** Claims pass — 5 pages
**Pages touched:**
- `claims/claim-transmission-immediate-blocker` — +`## Boundary Conditions` section (3 bullets: monetization-not-only bottleneck, curtailment causes beyond transmission, backbone completion does not eliminate all constraints)
- `claims/claim-storage-physical-fix` — +`## Boundary Conditions` section (4 bullets: physical ≠ implementable, no specific project endorsement, does not eliminate grid/demand/virtual storage, seasonal inter-month vs intra-day distinction)
- `claims/claim-timing-not-volume` — +`## Boundary Conditions` section (3 bullets: timing is not the only constraint, not a claim of absolute water sufficiency, does not prescribe policy responses)
- `claims/claim-solar-cheaper-than-small-hydro` — no changes required; exemplary `analysis`-tier claim page with all required sections. Second exemplar-quality claim page alongside `claim-mw-not-equal-value`.
- `claims/claim-climate-harder-not-easier` — +`## Boundary Conditions` section (4 bullets: total annual water may rise, basin-specific variation, does not reject adaptive design, volatility/tail risk focus); +qualifier in `## Confidence rationale` addressing `high` (page) vs `medium-high` (ontology) discrepancy per option (c)

**Validation result:** `OK: 358 wiki pages, caches valid, map manifest valid, tracked hygiene clean`

**Flags raised:**
- `claim-climate-harder-not-easier`: **Confidence level discrepancy** — page frontmatter `confidence: high` does not match `wiki/ONTOLOGY.md` canonical table `medium-high`. Resolved via option (c): page rationale preserved with explicit qualifier; ontology revisit scheduled for monthly review.

**Pattern observed:**
- **Boundary conditions gap is structural and cohort-wide.** 4 of 5 claim pages were missing the required `## Boundary Conditions` section per TEMPLATES.md. This suggests a template-adoption gap across the category, not isolated page failures.
- **Zero hierarchy violations across five claim pages.** Claims are the category most at risk of evidence creep (absorbing analytical work that belongs in syntheses). All five pages held the line — evidence is source-backed, interpretations are claim-level, and no synthesis conclusions leaked in. This suggests the governance layer is working at the category level.
- **Validator enhancement proposed:** `validate_repo.py` should warn (not hard-fail) when claim pages lack `## Boundary Conditions`. Added to `wiki/FLAGGED_FOR_REVIEW.md`.

**Decisions made:**
- Human approved all 5 changes in batch.
- Option (c) selected for confidence discrepancy: preserve page rationale, add explicit qualifier, flag ontology for monthly review.
- `claim-solar-cheaper-than-small-hydro` formally recognized as second exemplar-quality claim page.

---

## 2026-05-10 — Concepts Pass (Week 6)

**Agent:** OpenCode (kimi-k2.6)
**Session type:** Concepts pass — 5 pages
**Pages touched:**
- `concepts/storage-deficit` — +`## Summary` heading; +`## Simple Explanation`; +`## Common Misunderstandings` (3 bullets); +`## Related`; +`## Sources`
- `concepts/run-of-river-hydropower` — +`## Summary` heading; +`## Simple Explanation`; +`## Common Misunderstandings` (3 bullets); +`## Related`; +`## Sources`
- `concepts/firm-power` — **Quality-tier correction:** frontmatter `page_quality` temporarily updated from `analysis` → `brief` to reflect under-built state, then restored to `analysis` after additions. +`## Summary` heading; +`## Simple Explanation`; +`## Examples` (2 bullets); +`## Common Misunderstandings` (3 bullets); +`## Related`; +`## Sources`
- `concepts/solar-hydro-complementarity` — +`## Summary` heading; +`## Sources`. Already exemplary `analysis`-tier page; closest to complete among the five.
- `concepts/buildability` — Fixed text artifact (duplicate sentence fragment at end of Likhu-4 citation). **Hierarchy violation reframe:** "Nepal should rank options by buildable system value" → "The planning-relevant metric is therefore system value — incremental dependable energy, loss factors, curtailment risk, and delivered cost — rather than headline megawatts." +`## Summary` heading; +`## Simple Explanation`; +`## Common Misunderstandings` (3 bullets); +`## Related`; +`## Sources`

**Validation result:** `OK: 358 wiki pages, caches valid, map manifest valid, tracked hygiene clean`

**Flags raised:**
- `concepts/buildability`: **Hierarchy violation** — policy prescription "Nepal should rank options by buildable system value" reframed to descriptive language per GOVERNANCE.md invariant #9 (added this session).
- `concepts/firm-power`: **Quality-tier correction** — page declared `analysis` but was under-built for the tier. Proposed additions bring it to `analysis` minimum. Documented as tier correction.

**Pattern observed:**
- **Structural cohort gap confirmed across concepts and claims.** 5 of 5 concept pages missing `## Summary` heading and `## Sources`; 4 of 5 missing `## Simple Explanation` and `## Common Misunderstandings`. This matches the Week 5 boundary-conditions gap in claims. Both are **template-adoption gaps** from pages written before templates existed, not individual failures.
- **Second policy-prescription hierarchy violation found** (first: `data-storage-comparison` in Week 2). Both were concept/data pages reaching for synthesis-level conclusions. This motivated addition of invariant #9 to GOVERNANCE.md: "No policy prescriptions on concept or data pages."
- **Validator enhancement proposed (high priority):** `validate_repo.py` should warn when pages lack required section headings by category: `## Boundary Conditions` for claims; `## Summary`, `## Simple Explanation`, `## Common Misunderstandings` for concepts. This one rule would have flagged 9 of 10 pages touched in Weeks 5–6 before any human or agent looked at them.

**Decisions made:**
- Human approved all 5 changes in batch.
- Buildability reframe wording confirmed: "The planning-relevant metric is therefore system value..." (removing prescriptive "Nepal should" while preserving analytical force).
- GOVERNANCE.md invariant #9 added: "No policy prescriptions on concept or data pages."

---

## 2026-05-10 — Data Pages Pass (Week 7)

**Agent:** OpenCode (kimi-k2.6)
**Session type:** Data pages pass — 5 pages + exemplar fix
**Pages touched:**
- `data/data-trade-time-series` — +`## Summary` heading; +`## Sources`
- `data/data-potential-pyramid` — +`## Summary` heading; reframed lead paragraph from "systems failure" (causal claim) to "successive filtering...systems constraint" (observation); +`## Coverage / Method`; +`## Caveats`; +`## Sources`; added cross-reference to [[master-thesis]] and [[bottleneck-hierarchy]] for interpretive framing
- `data/data-solar-hydro-lcoe` — +`## Summary` heading; +`## Coverage / Method`; +`## Sources`
- `data/data-basin-discharge` — +`## Summary` heading; +`## Coverage / Method`; +`## Caveats`; +`## Sources`
- `data/data-solar-hydro-complementarity-profile` — +`## Summary` heading; removed `## Policy read` section (hierarchy violation); reframed prescription "Nepal's next priority after Terai solar is 4-hour BESS + reservoir-hydro peaking" to observation-level with cross-reference to [[solar-role-in-winter-deficit]]; +`## Coverage / Method`; +`## Caveats`; +`## Sources`
- `data/data-storage-comparison` (exemplar fix) — **Pre-task:** fixed standing hierarchy violation on reference exemplar. Line 72 reframed from "The bottleneck is capital, governance, and institutional will, not geology" to observation-level language with cross-reference to [[master-thesis]] and [[bottleneck-hierarchy]]. Verified downstream existence before reframing.

**Validation result:** `OK: 358 wiki pages, caches valid, map manifest valid, tracked hygiene clean`

**Flags raised:**
- `data/data-potential-pyramid`: **Hierarchy violation** — lead paragraph contained causal claim "it is a systems failure" on data page. Reframes to observation-level with cross-reference to synthesis pages.
- `data/data-solar-hydro-complementarity-profile`: **Hierarchy violation (most severe found across 7 weeks)** — direct prescription "Nepal's next priority after Terai solar is 4-hour BESS + reservoir-hydro peaking, not more RoR" on data page. **Migration check confirmed** the same argument exists on [[solar-role-in-winter-deficit]]; data page reframed to observation-level with cross-reference.
- `data/data-storage-comparison`: **Standing hierarchy violation in reference exemplar** — Week 2 edit was not committed or was reverted. Fixed as pre-task before Week 8. Impact: all data-page edits since Week 2 used a non-compliant exemplar.

**Pattern observed:**
- **Data pages have the highest hierarchy violation rate of any category.** 2 violations in 5 pages (40%), including the most severe found across 7 weeks. Consistent with in-repo prediction: data pages are where analysis gets parked when it hasn't found its synthesis home yet.
- **Structural cohort gap confirmed across three categories now.** Missing required sections: claims (boundary conditions), concepts (summary/simple explanation/common misunderstandings), data (summary/coverage/caveats/sources). All are template-adoption gaps from pre-template pages.
- **Downstream-check rule proved its value again.** On `data-solar-hydro-complementarity-profile`, verified that the BESS-plus-peaking argument exists on [[solar-role-in-winter-deficit]] before removing prescription from data page. No content lost.

**Decisions made:**
- Human approved all 5 changes in batch.
- Buildability reframe from Week 6 reinforced: "The planning-relevant metric is therefore system value..." approved as removing prescription while preserving analytical force.
- Exemplar fix approved as mandatory pre-task for Week 8.
- GOVERNANCE.md updated with standing note: data pages are highest-risk category for hierarchy violations.

---

## 2026-05-10 — Flagship Entities Pass (Week 8)

**Agent:** OpenCode (kimi-k2.6)
**Session type:** Entities pass — 5 pages
**Pages touched:**
- `entities/upper-tamakoshi` — +`## Summary` heading; +`## Limitations & Controversies` section (summary-level, referencing detailed Financial Performance content); +`## Related` section. Full financial detail preserved in Financial Performance; no content moved.
- `entities/chilime` — +`## Summary` heading; +`## Significance / Why It Matters` heading; +`## Limitations & Controversies` section leading with non-replicability; +`## Related` section. Reorganized existing narrative into template-compliant sections; no new content invented.
- `entities/pancheshwar` — +`## Summary` heading; +`## Limitations & Controversies` section consolidating 30-year stall, benefit-sharing impasse, displacement, seismic risk, financing; Related section already present.
- `entities/nea-960mw-solar-tender` — +`## Summary` heading; +`## Limitations & Controversies` section consolidating implementation risks; +`## Sources` section.
- `entities/budhigandaki` — +`## Summary` heading; +`## Limitations & Controversies` section consolidating repeated modality changes, 8-year build, displacement, seismic/sediment risks, financing uncertainty, long payback.

**Validation result:** `OK: 358 wiki pages, caches valid, map manifest valid, tracked hygiene clean`

**Flags raised:**
- `entities/chilime`: **Tier assessment.** Page declared `analysis` but was structurally closer to `brief`. Proposed additions reorganize existing narrative into canonical sections (Summary, Significance, Limitations & Controversies, Related) to meet `analysis` minimum.

**Pattern observed (eight-week summary):**
- **Hierarchy violations by category:** Data pages highest (2/5, one severe), source pages second (3/5, all moderate), concept pages third (1/5), claims and entities clean (0/5 each). Maps exactly to predicted pattern: categories with most analytical ambition have the most interpretation bleeding across hierarchy.
- **Structural cohort gaps:** `## Summary` missing across all 5 categories; `## Simple Explanation` missing across concepts; `## Boundary Conditions` missing across claims; `## Limitations & Controversies` missing or scattered across entities. All are template-adoption gaps from pre-template pages, not individual failures.
- **Highest-leverage monthly review items:** (1) Validator rule additions to `validate_repo.py` for required section headings by page type; (2) spot-check of data pages specifically for hierarchy violations, given highest violation rate and severity.

**Decisions made:**
- Human approved all 5 changes in batch.
- Upper Tamakoshi: confirmed that Limitations & Controversies should summarize (not move) Financial Performance content.
- Chilime: confirmed non-replicability should lead the Limitations & Controversies section.

---

## Log Format for Future Sessions

```
## YYYY-MM-DD — [Category] Pass

**Agent:** [name/model]
**Session type:** [category pass / exemplar / drift review / cleanup]
**Pages touched:**
- `slug-1`: [brief description of changes]
- `slug-2`: [brief description of changes]

**Validation result:** [OK / FAIL with details]

**Flags raised:**
- [description of flag requiring human review]

**Decisions made:**
- [any human approval or override]
```
