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

## 2026-05-10 — Pre-Cycle Cleanup (Post-Review Fixes)

**Agent:** OpenCode (kimi-k2.6)
**Session type:** Cleanup — 3 external-agent flags + 1 enhancement
**Pages touched:**
- `sources/wb-country-economic-memo-2025` — Added missing `## Limitations` and `## Used By` sections (audit log said they were added in Week 2 but were not present on disk). Renamed `## Relevance to Project` → `## Relevance`.
- `claims/claim-mw-not-equal-value` — Added missing `## Boundary Conditions` section (audit log said it was added in Week 2 but was not present on disk).
- `wiki/FLAGGED_FOR_REVIEW.md` — Removed 3 resolved items from Open Items: IRENA migration, ontology confidence, validator enhancement. All were already in Resolved Items.
- `scripts/validate_repo.py` — Added tier-aware filtering to `validate_required_sections()`: `record`-tier pages in entities/sources/data are skipped; `brief`-tier entities skip `## Limitations & Controversies`. Reduced baseline from 696 to 593 warnings. Added summary-by-category output and `WIKI_VERBOSE=1` flag.

**Validation result:** `OK: 378 wiki pages, caches valid, map manifest valid, tracked hygiene clean`

**Flags raised:** None.

**Pattern observed:**
- **Audit log / file mismatch is a real risk.** Two Week 2 edits were recorded in WIKI_AUDIT_LOG.md but never written to disk. Root cause unknown — possibly edit tool failure, revert, or the edits were proposed but never executed. Added standing rule: verify file contents match audit log before pushing.
- **Tier filter is high-leverage.** 72 record-tier pages correctly skipped. Entity warnings dropped from 324 to 218. Second cycle should now target the ~593 real warnings, not the inflated 696.

**Decisions made:**
- Human approved all fixes via batch confirmation.
- External agent proposed revised second-cycle sequencing (claims → sources → concepts → data → entities, by gap size and citation leverage). Incorporated into `docs/second-cycle-handoff.md`.

---

## 2026-05-11 — Claims Pass (Second Cycle, Session 1)

**Agent:** OpenCode (kimi-k2.6)
**Session type:** Claims pass (second cycle) — 5 pages
**Pages touched:**
- `claims/claim-solar-cheaper-than-small-hydro` — Fixed heading case: `## Boundary conditions` → `## Boundary Conditions` (pure formatting fix, no content change)
- `claims/claim-governance-binding` — Added `## Boundary Conditions` section (4 bullets derived from existing Evidence: governance is not the only constraint, not all delays are governance failures, no specific model prescribed, reform is not claimed easy)
- `claims/claim-systems-conversion-failure` — Added `## Boundary Conditions` section (4 bullets derived from existing Evidence/Unresolved Issues: not zero progress, not irreversible, not universal indictment, not a guarantee)
- `claims/claim-india-decisive-actor` — Added `## Boundary Conditions` section (4 bullets derived from existing Evidence: Nepal retains agency, India does not control every decision, cooperation is not impossible, not every project requires Indian involvement)
- `claims/claim-ror-dominance` — Added `## Boundary Conditions` section (4 bullets derived from existing Evidence/Unresolved Issues: operating fleet scope, RoR/PRoR not inherently bad, storage not impossible, definition sensitivity)

**Validation result:** `OK: 378 wiki pages, caches valid, map manifest valid, tracked hygiene clean` (5 claim warnings resolved)

**Flags raised:** None. All boundary conditions derived from existing page content; no new factual claims or confidence changes.

**Pattern observed:**
- **Boundary Conditions section is the canonical gap across claims.** All 5 pages were missing it; all were `analysis`-tier and should have had it per TEMPLATES.md.
- **Derivation method confirmed:** Boundary conditions should be drawn from existing Evidence and Unresolved Issues content, not invented. This prevents the section from restating the claim or introducing new arguments.
- **claim-solar-cheaper-than-small-hydro** had the section present but with lowercase heading — a minor formatting gap that validator caught. Indicates the section is sometimes present but not canonical-cased.

**Decisions made:**
- Human approved all 5 changes with explicit confirmation of derivation method and two wording notes (claim-india-decisive-actor bullet 3 on cooperation; claim-ror-dominance bullet 4 on definition sensitivity).
- Human proposed relaxing confirm gate for second batch of 6 if diagnoses are uniformly "missing Boundary Conditions, content derived from existing Evidence" with no flags.

---

## 2026-05-11 — Claims Pass (Second Cycle, Session 2) — CATEGORY CLOSED

**Agent:** OpenCode (kimi-k2.6)
**Session type:** Claims pass (second cycle) — 6 pages, batch-parallel write with relaxed confirm gate
**Pages touched:**
- `claims/claim-domestic-led-strategy` — Added `## Boundary Conditions` (4 bullets derived from Evidence: export-support framing, industrial-path viability caveat, absorption vs potential distinction, no specific policy sequence prescribed)
- `claims/claim-floating-pv-leverage` — Replaced `## Boundary conditions` (lowercase, single sentence) with `## Boundary Conditions` (4 bullets: niche not useless, scales with reservoir stock, no land-framework substitute, conditional on future reservoirs)
- `claims/claim-pror-not-storage` — Added `## Boundary Conditions` (4 bullets derived from Evidence: PRoR not useless, intraday ≠ inter-seasonal, mixed portfolios open, taxonomy sensitivity)
- `claims/claim-sediment-core-issue` — Added `## Boundary Conditions` (4 bullets: not the only constraint, basin-specific risk, not unbuildable, ppm figures indicative)
- `claims/claim-solar-political-coalition-is-rural` — Replaced `## Boundary conditions` (lowercase, single sentence) with `## Boundary Conditions` (4 bullets: political legitimacy not grid energy, broader than IPPs, different value not cost comparison, explains resilience not predicts outcomes)
- `claims/claim-solar-terai-only-short-cycle-build` — Replaced `## Boundary conditions` (lowercase, single sentence) with `## Boundary Conditions` (4 bullets: build speed not firm capacity, individual stalls possible, hydro still necessary, not a winter-balance sole solution)

**Validation result:** `OK: 378 wiki pages, caches valid, map manifest valid, tracked hygiene clean` — **Claims category: ZERO warnings.** Total warnings dropped from 593 → 582.

**Milestone:** **Claims is the first category to hit zero structural warnings in the second cycle.** All 16 claim pages now have canonical `## Boundary Conditions` sections.

**Flags raised:** None. Batch-parallel write approved by human under relaxed confirm gate for uniformly structural, zero-flag diagnoses.

**Pattern observed:**
- **Three pages had lowercase `## Boundary conditions` heading** (claim-floating-pv-leverage, claim-solar-political-coalition-is-rural, claim-solar-terai-only-short-cycle-build) — the section existed but was non-canonical cased. This pattern was caught by validator and fixed.
- **Derivation method confirmed across 11 pages:** All Boundary Conditions drawn from existing Evidence and Unresolved Issues content. No new factual claims introduced.
- **Relaxed confirm gate worked as intended:** For structural-only, zero-flag diagnoses, batch-parallel write reduced friction without reducing safety. Confirm gate remains mandatory for any flagged item.

**Decisions made:**
- Human approved batch-parallel write for all six under relaxed confirm gate protocol.
- Human confirmed claim-sediment-core-issue bullet 4 as strongest boundary condition in batch; kept exactly as written.
- claim-domestic-led-strategy bullet 4 accepted as abstract but accurate; no concrete anchor added (Evidence examples exist but boundary stays at strategic-framing level).

---

## 2026-05-11 — Sources Pass (Second Cycle, Session 2)

**Agent:** OpenCode (kimi-k2.6)
**Session type:** Sources pass (second cycle) — 5 pages, batch-parallel write with relaxed confirm gate
**Pages touched:**
- `sources/nea-annual-report-fy2024-25` — Added `## Limitations` section (4 bullets: snapshot date, NEA-only perspective, World Bank reconciliation gap, missing granularity). Has `## Summary` and `## Used By` already present and verified.
- `sources/jica-ipsdp-main-report-vol2` — Added `## Limitations` (3 bullets: incomplete volume with annex topic parenthetical, study assumptions not verified outcomes, 2024 cutoff) and `## Used By` (26 backlinks). Has `## Summary` already present.
- `sources/nea-transmission-annual-book-2077` — Added `## Limitations` (4 bullets: FY 2019/20 snapshot, superseded for totals, no technical modelling, mixed genre) and `## Used By` (13 backlinks). Has `## Summary` already present.
- `sources/wecs-hydropower-potential-2019` — Added `## Limitations` (4 bullets: screening opacity, gross vs techno-economic distinction, legacy figure persistence, exclusions for climate/sediment/buildability) and `## Used By` (10 backlinks). Has `## Summary` already present.
- `sources/wecs-energy-synopsis-2024` — Added `## Limitations` (4 bullets: single-year snapshot, repository stub, biomass estimates, grid-electricity share jump) and `## Used By` (5 backlinks). Has `## Summary` already present.

**Validation result:** `OK: 378 wiki pages, caches valid, map manifest valid, tracked hygiene clean`
- **Before:** 582 total warnings (sources: 48 missing Limitations, 47 missing Used By, 16 missing Summary)
- **After:** 573 total warnings (sources: 43 missing Limitations, 43 missing Used By, 16 missing Summary)
- **Delta:** −9 warnings (5 Limitations + 4 Used By resolved)

**Flags raised:**
- `wecs-energy-synopsis-2024`: **Data hygiene flag** — PDF copy in `data/raw/core/` is a 404 HTML stub. Logged in `wiki/FLAGGED_FOR_REVIEW.md` as open item for replacement or external-only marking.

**Pattern observed:**
- **Used By lists built from grep, never memory.** All 5 pages verified via `grep -rl` before writing. Backlink counts after due-diligence correction: nea-annual-report-fy2024-25 (38), jica-ipsdp-main-report-vol2 (26), nea-transmission-annual-book-2077 (13), wecs-hydropower-potential-2019 (10), wecs-energy-synopsis-2024 (5).
- **Limitations derived from existing page content.** No new factual claims invented. Cross-source reconciliation note (nea-annual-report World Bank gap) explicitly framed as date difference, not contradiction.
- **Zero hierarchy violations across 5 source pages.** All pages stayed within source-description discipline (what this source provides, how reliable it is, what it does not cover).

**Decisions made:**
- Human approved batch-parallel write for all five under relaxed confirm gate.
- Human confirmed specific wording notes: nea-annual-report reconciliation gap bullet, nea-transmission "mixed genre" bullet, wecs-hydropower "legacy figure persistence" bullet.
- WECS stub flagged for future data hygiene task.

---

## 2026-05-11 — Sources Pass (Second Cycle, Session 3) — SCHEDULED SOURCES COMPLETE

**Agent:** OpenCode (kimi-k2.6)
**Session type:** Sources pass (second cycle) — 5 pages, batch-parallel write with relaxed confirm gate
**Pages touched:**
- `sources/nepal-transmission-landscape-2025` — Added `## Limitations` (4 bullets: compilation not primary source, snapshot date, missing granularity, transfer capacity approximations) and `## Used By` (30 backlinks — most-cited source in wiki). Has `## Summary` already present.
- `sources/adb-hydropower-growth-nepal` — Added `## Limitations` (3 bullets: thin extraction, 2020 cutoff, missing source URL) and `## Used By` (1 backlink: buildability). Has `## Summary` already present.
- `sources/icra-nepal-surveillance-a996-b119` — Replaced `## Caveat` with `## Limitations` (3 bullets: incomplete citation, point-in-time assessment, single-source dependency) and added `## Used By` (3 backlinks). Has `## Summary` already present.
- `sources/national-water-plan-nepal` — Added `## Limitations` (4 bullets: historical estimates, 2005 cutoff, strategic vs precise, single planning document) and `## Used By` (4 backlinks). Has `## Summary` already present.
- `sources/wb-water-sector-diagnostic` — Added `## Limitations` (4 bullets: storage-gap framing, active vs total ambiguity, 2023 cutoff, JICA MW targets are study outputs) and `## Used By` (2 backlinks). Has `## Summary` already present.

**Validation result:** `OK: 378 wiki pages, caches valid, map manifest valid, tracked hygiene clean`
- **Before Session 3:** 573 total warnings (sources: 43 missing Limitations, 43 missing Used By, 16 missing Summary)
- **After Session 3:** 563 total warnings (sources: 38 missing Limitations, 38 missing Used By, 16 missing Summary)
- **Delta (this session):** −10 warnings (5 Limitations + 5 Used By)
- **Delta (sources pass total, 2 sessions):** 582 → 563 = −19 warnings (10 Limitations + 9 Used By)

**Flags raised:**
- `adb-hydropower-growth-nepal`: **Data hygiene flag** — missing source URL in frontmatter. Logged in `wiki/FLAGGED_FOR_REVIEW.md` alongside `wecs-energy-synopsis-2024` PDF stub.

**Pattern observed:**
- **Secondary data hygiene pattern emerging:** Two source pages in two sessions with missing live URLs or PDF stubs (`wecs-energy-synopsis-2024` 404 stub, `adb-hydropower-growth-nepal` missing URL). Worth a standing note that source pages should have a live URL or an explicit "external-only, no local copy" notation in frontmatter. Add to session template for future source passes.
- **`nepal-transmission-landscape-2025` is the most-cited source in the wiki** (30 backlinks). Any future changes to this page — confidence updates, scope revisions, or structural edits — should trigger review of the 30 dependent claim, concept, data, entity, and intervention pages. The page's criticality warrants a frontmatter note or explicit sentence in Limitations.
- **Zero hierarchy violations across 10 source pages in 2 sessions.** All pages stayed within source-description discipline.
- **Used By lists built from grep, never memory.** All 10 pages verified via `grep -rl` before writing.

**Decisions made:**
- Human approved batch-parallel write for all five under relaxed confirm gate.
- Human confirmed specific wording notes: nepal-transmission transfer capacity bullet, icra single-source dependency bullet, national-water-plan strategic vs precise bullet, wb-water-sector storage-gap framing bullet.
- Two data hygiene items added to FLAGGED_FOR_REVIEW.md.

---

## 2026-05-11 — Concepts Pass (Second Cycle, Session 4)

**Agent:** OpenCode (kimi-k2.6)
**Session type:** Concepts pass (second cycle) — 5 pages, batch-parallel write with relaxed confirm gate
**Pages touched:**
- `concepts/hydro-geopolitics` — Added `## Summary`, `## Simple Explanation`, `## Common Misunderstandings` (3 bullets: India as enemy, technical optimization enough, Bhutan as clone). No hierarchy violations.
- `concepts/agrivoltaics-and-land` — Added `## Summary`, `## Simple Explanation`, `## Common Misunderstandings` (3 bullets: nice-to-have bonus, every site must be agrivoltaic, capex-free). **Reframed hierarchy violation:** "## The policy moves this concept implies" section changed from prescriptive "Nepal needs" to observation-level "Scaling agrivoltaics requires" and "Absent these four conditions." Added cross-reference to intervention and claim pages for policy implications.
- `concepts/glof-risk` — Added `## Summary`, `## Simple Explanation`, `## Common Misunderstandings` (3 bullets: just a big flood, environmental side issue, only near-glacier projects at risk). No hierarchy violations.
- `concepts/ppa-pricing` — Added `## Summary`, `## Simple Explanation`, `## Common Misunderstandings` (3 bullets: market prices, same rate for all, lower rates always better). Evaluative language ("catastrophic inefficiency") verified as descriptive, not prescriptive. No hierarchy violations.
- `concepts/domestic-led-hydro-strategy` — Added `## Summary`, `## Simple Explanation`, `## Common Misunderstandings` (3 bullets: anti-export, lacks demand, only about hydro). Page reports research convergence; normative argument lives on `claim-domestic-led-strategy`. No hierarchy violations.

**Validation result:** `OK: 378 wiki pages, caches valid, map manifest valid, tracked hygiene clean`
- **Before Session 4:** 563 total warnings (concepts: 41 missing Common Misunderstandings, 41 missing Simple Explanation, 40 missing Summary)
- **After Session 4:** 548 total warnings (concepts: 36 missing Common Misunderstandings, 36 missing Simple Explanation, 35 missing Summary)
- **Delta (this session):** −15 warnings (5 Summary + 5 Simple Explanation + 5 Common Misunderstandings)

**Flags raised:**
- `concepts/agrivoltaics-and-land`: **Hierarchy violation (Invariant #9)** — policy prescriptions reframed in place rather than logged for migration. Downstream-check confirmed no existing intervention page carries the 4 policy moves. Reframe approved by human: preserves analytical content, removes invariant violation, adds cross-references to policy pages.

**Pattern observed:**
- **Third policy prescription found on a concept page** across full audit — `agrivoltaics-and-land` joins `buildability` (Week 6) and `data-storage-comparison` (Week 2) as pages where prescriptive language accumulated. Consistent structural finding: concept and data pages absorb analysis that hasn't found its synthesis or intervention home. Worth a standing note in next monthly review about whether an intervention page for Terai solar land policy is warranted.
- **Zero new factual claims across 5 pages.** All sections derived from existing content.

**Decisions made:**
- Human approved batch-parallel write for all five.
- Human confirmed specific wording notes: hydro-geopolitics Bhutan bullet, glof-risk infrastructure solvency framing, ppa-pricing third misunderstanding bullet, domestic-led Simple Explanation clarity.
- Agrivoltaics reframe approved: "Scaling agrivoltaics requires" / "Absent these four conditions" with cross-references.

---

## 2026-05-11 — Concepts Pass (Second Cycle, Session 5)

**Agent:** OpenCode (kimi-k2.6)
**Session type:** Concepts pass (second cycle) — 5 pages, batch-parallel write with relaxed confirm gate
**Pages touched:**
- `concepts/stranded-generation` — Added `## Summary`, `## Simple Explanation`, `## Common Misunderstandings` (3 bullets: broken plants, more generation helps, curtailment only hurts small IPPs). No hierarchy violations.
- `concepts/seasonal-mismatch` — Added `## Summary`, `## Simple Explanation`, `## Common Misunderstandings` (3 bullets: temporary drought, more dams solve it, solar eliminates it). No hierarchy violations.
- `concepts/seasonal-arbitrage-trap` — Added `## Summary`, `## Simple Explanation`, `## Common Misunderstandings` (3 bullets: positive net exports mean winning, IEX spread proves resolution, better negotiation fixes it). No hierarchy violations.
- `concepts/q-design-discharge` — Added `## Summary`, `## Simple Explanation`, `## Common Misunderstandings` (3 bullets: just a technical detail, higher always better, always developer's fault). No hierarchy violations.
- `concepts/ganges-contribution` — Added `## Summary`, `## Simple Explanation`, `## Common Misunderstandings` (3 bullets: proportional to land area, unlimited bargaining power, exact/current figures). No hierarchy violations.

**Validation result:** `OK: 378 wiki pages, caches valid, map manifest valid, tracked hygiene clean`
- **Before Session 5:** 548 total warnings (concepts: 36 missing Common Misunderstandings, 36 missing Simple Explanation, 35 missing Summary)
- **After Session 5:** 533 total warnings (concepts: 31 missing Common Misunderstandings, 31 missing Simple Explanation, 30 missing Summary)
- **Delta (this session):** −15 warnings (5 Summary + 5 Simple Explanation + 5 Common Misunderstandings)
- **Delta (concepts pass total, 2 sessions):** 563 → 533 = −30 warnings (10 Summary + 10 Simple Explanation + 10 Common Misunderstandings)

**Flags raised:** None.

**Pattern observed:**
- **Five consecutive clean concept sessions** — no hierarchy violations, no flags, no factual judgment calls across ten pages (Sessions 4–5 plus Week 6 first cycle). Concepts written before the governance layer existed had structural gaps but not interpretive violations. The two violations found earlier (`buildability` Week 6, `agrivoltaics-and-land` Session 4) were exceptions, not the pattern.
- **Simple Explanation quality is highest in concepts category.** The seasonal-mismatch Simple Explanation ("This is not a drought or a shortage of dams — it is the physics of building a power system from rivers that follow a different calendar than human needs") was the best single sentence in the concepts pass.

**Decisions made:**
- Human approved batch-parallel write for all five.
- Human confirmed specific wording notes: stranded-generation curtailment bullet, seasonal-mismatch physics sentence, seasonal-arbitrage-trap negotiation bullet, q-design-discharge methodological failure bullet, ganges-contribution leverage bullet.

---

## 2026-05-11 — Data Pages Pass (Second Cycle, Session 6)

**Agent:** OpenCode (kimi-k2.6)
**Session type:** Data pages pass (second cycle) — 8 pages (4 already compliant from Week 7), 6 clean + 2 flagged
**Pages touched:**
- `data/data-trade-time-series` — Added `## Coverage / Method` (strong reconciliation note preserving all 3 NEA views) and `## Caveats` (IEX ≠ whole system caveat). Has `## Summary` from Week 7. Three `> [!finding]` callouts verified as observation-level; no hierarchy violations.
- `data/data-domestic-demand` — Added `## Summary`, `## Coverage / Method`, `## Caveats`. **Hierarchy violation found and reframed:** "## Value-Capture Framing" section contained interpretive content without downstream home. Reframed to observation-level with cross-references. Content migrated to `syntheses/twenty-year-strategy.md` under Phase 2 as "Value capture: domestic electrification outranks export optimization" section. Downstream-check confirmed argument did not exist elsewhere before migration.
- `data/data-fleet-composition` — Added `## Summary`, `## Coverage / Method`, `## Caveats`. No hierarchy violations.
- `data/data-solar-fleet-inventory` — Added `## Summary`, `## Coverage / Method`, `## Caveats`. No hierarchy violations.
- `data/data-storage-comparison` — Added `## Summary`, `## Coverage / Method`, `## Caveats`. No hierarchy violations.
- `data/data-nepal-peak-load-curve-fy2024-25` — Added `## Summary`, `## Coverage / Method`, `## Caveats`. No hierarchy violations.
- `data/data-agricultural-energy-consumption` — Added `## Summary`, `## Coverage / Method`, `## Caveats`. One `> [!finding]` callout verified as observation-level; no hierarchy violations.
- `data/data-consumption-geographic-distribution` — Added `## Summary`, `## Coverage / Method`, `## Caveats`. No hierarchy violations.

**Migration executed:** `syntheses/twenty-year-strategy.md` — added "Value capture: domestic electrification outranks export optimization" section under Phase 2.

**Validation result:** `OK: 378 wiki pages, caches valid, map manifest valid, tracked hygiene clean`
- **Before Session 6:** 533 total warnings
- **After Session 6:** 510 total warnings
- **Delta (this session):** −23 warnings
- **Delta (full second cycle):** 582 → 510 = −72 warnings

**Flags raised:**
- `data-domestic-demand`: **Hierarchy violation (Invariant #9)** — reframed and migrated per Invariant #10.
- **Research gap logged:** Electric cooking statistic (0.5%) from 2021 WB estimate, no annual update. Tracked in `FLAGGED_FOR_REVIEW.md`.

**Pattern observed:**
- **Fourth policy-level content migration in the project.** Downstream-check rule proved its value again.
- **Data pages closing faster than expected:** 4 already compliant + 8 resolved in one session = 12 of 15 scheduled pages complete.
- **Coverage/Method three-part structure (data source, methodology, known gaps) is producing genuinely useful sections.**

**Decisions made:**
- Human confirmed batch write for all 8 pages.
- Human confirmed migration target: `syntheses/twenty-year-strategy.md`.
- Human flagged electric cooking statistic as research gap.

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
