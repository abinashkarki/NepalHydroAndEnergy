# Wiki Governance

The Nepal Energy Wiki is a research production pipeline, not a collection of notes. Every edit must preserve traceable reasoning chains from primary evidence to strategic conclusion. Structure and provenance take priority over elegance, brevity, or narrative flow.

## Authority Hierarchy

Interpretive freedom increases upward only. Moving content downward in the hierarchy corrupts epistemic structure.

| Level | Page types | What they do | What they must NOT do |
|---|---|---|---|
| **L1 — Sources** | `sources/*` | Ingest and describe primary materials. Answer: what does this source give you, and how reliable is it? | No interpretation. No synthesis conclusions. No "so what." |
| **L2 — Data / Entities / Claims** | `data/*`, `entities/*`, `claims/*` | Present structured facts, project records, and evidence-backed arguments. | Data pages: no strategic implications. Entity pages: no policy prescriptions. Claim pages: no conclusions that exceed the evidence cited. |
| **L3 — Syntheses** | `syntheses/*` | Connect evidence into coherent arguments. This is the ONLY layer where "so what" belongs. | No invention of new primary facts. No claims without backing L1/L2 pages. |
| **L4 — Master Thesis** | `syntheses/master-thesis.md` | Cross-synthesis narrative layer. The authoritative framing for the entire wiki. | Must be fully grounded in L3 syntheses, which are grounded in L2 claims/data/entities, which are grounded in L1 sources. |

**Hard rule:** A page at level N may reference pages at any level ≤ N. It may NOT push interpretive content downward. If a data page contains a strategic implication, that implication must be moved to a synthesis or claim page, and the data page should link to it.

## Non-Negotiable Invariants

1. **No quantitative claim without source linkage.** Every capacity, cost, date, generation figure, transmission voltage, project status, or policy claim must cite a source page or structured data row.
2. **No interpretation inside source pages.** Source pages describe what the source provides and how reliable it is. Analysis of the source's findings belongs in claim or synthesis pages.
3. **No synthesis conclusions on data pages.** Data pages present numbers with confidence flags and caveats. The interpretive payoff lives in synthesis pages only.
4. **No page renaming without logging.** Any slug rename must be recorded in `wiki/FLAGGED_FOR_REVIEW.md` with the old slug, new slug, and rationale.
5. **No duplicate page creation without flagging.** Before creating a new page, check `wiki/ONTOLOGY.md` for existing canonical terms and `wiki/explorer/shared/wiki-page-index.json` for existing slugs.
6. **No confidence inheritance across claims.** Each claim carries its own confidence flag (`high`, `medium-high`, `medium`, `low`). A page-level confidence does not propagate to individual claims on that page.
7. **No deletion without archival notation.** Deleting a page requires human approval and a note in `wiki/WIKI_AUDIT_LOG.md` with the slug, date, and reason.
8. **Never replace sourced claims with paraphrased summaries.** If a source says something specific, quote or cite it specifically. Do not smooth it into generic prose that loses traceability.
9. **No policy prescriptions on concept or data pages.** Concept pages may describe implications but may not prescribe responses. The line is "this means X" versus "Nepal should do X." Prescriptions belong in syntheses and interventions.
10. **Never remove interpretive content without verifying downstream existence.** Before removing interpretive content from a source or data page, verify via grep that the same argument exists on a claim or synthesis page. If it does not, log the migration target in `wiki/FLAGGED_FOR_REVIEW.md` before removing. This rule proved its value three times in the first cycle; it is permanent infrastructure.

## Agent Philosophy

The wiki prioritizes epistemic clarity over brevity, novelty, or prose quality. The system exists to preserve traceable reasoning chains from source → extraction → synthesis → conclusion. When in doubt, preserve structure and provenance over elegance.

Agents optimize locally. Global optimization guidance:
- Prefer adding a new linked page over expanding an existing page beyond its category discipline.
- Prefer explicit gaps (`unknown`, `unverified`, `gap`) over confident weak claims.
- Prefer boring, predictable headings (`Summary`, `Key Facts`, `Why It Matters`, `Evidence`, `Caveats`, `Sources`) over clever ones.

## Page Quality Tiers

Every non-stub page should declare its ambition honestly. Do not overbuild or underbuild relative to its tier.

| Tier | Meaning | Minimum content |
|---|---|---|
| `record` | Registry-backed factual page. Limited narrative. | Spec table + lead paragraph + sources. Auto-stubs live here. |
| `brief` | Short interpretive page with key context. | 1-3 narrative paragraphs explaining what this is and why it matters for Nepal. |
| `analysis` | Substantial narrative with evidence and sourcing. | Multiple sections with evidence, caveats, internal links, and a clear line of reasoning. |
| `flagship` | Comprehensive core page. Canonical reference for a topic. | Full argument structure, cross-links to related pages, caveats, open questions, and clean source attribution. |

## Data Page Interpretation Policy

Data pages may contain **observation-level findings** but must not contain **strategic implications**.

- **Observation yes, interpretation no.** A data page may note that "the IEX spread flipped positive in 2023-24." It may NOT conclude that "this proves the seasonal arbitrage trap is resolving."
- **Finding yes, implication no.** A data page may flag a pattern in numbers. It may NOT prescribe policy or draw system-level conclusions.
- Every finding in a data page must point to a claim or synthesis page where the interpretive payoff lives.

**Data pages are the highest-risk category for hierarchy violations.** They are the most common place where analysis gets parked when it has not yet found its synthesis home. Watch for phrases like "Nepal should," "the priority is," "this proves," and "therefore." If you see them, reframe to observation-level or move to a synthesis page.

Callout types in data pages:
- `> [!warning]` — data quality issue, reconciliation note, or caveat
- `> [!important]` — structural data point readers should not miss
- `> [!finding]` — observation-level pattern (permitted, but must be bounded)

`> [!finding]` must never contain words like "therefore," "proves," "demonstrates that," "explains why," or policy prescriptions. If you see those, move the content to a claim or synthesis page.

## Category Discipline

Every page belongs to exactly one category. If a page feels like it should be two things, split it.

| Category | Core question | Canonical sections |
|---|---|---|
| `sources` | What does this source provide, and how reliable is it? | Summary, Key Findings, Relevance, Limitations, Used By |
| `entities` | What is this project/institution/actor, and what are its key facts? | Summary, Key Facts, Specifications, Why It Matters, Timeline, Sources |
| `concepts` | What is this idea, and why does it matter in Nepal? | Summary, Simple Explanation, Why It Matters in Nepal, Technical Details, Examples, Related |
| `claims` | What is being argued, what is the evidence, and what are the caveats? | Claim, Evidence, Confidence Rationale, Caveats, Boundary Conditions, Related |
| `data` | What does this dataset show, and what are its limitations? | Summary, What This Shows, Fields/Method, Coverage, Caveats, Linked Data, Sources |
| `syntheses` | What argument connects the evidence, and what follows from it? | Summary, Core Argument, Evidence Trail, Implications, Open Questions, Related |
| `interventions` | What action is proposed, what is the theory of change, and what is the political feasibility? | The Intervention, Theory of Change, Current Status, What This Unlocks, Research Gaps, Political Feasibility, Related |

## Source Attribution

- **Entity pages** (especially `generator: specs-refresh` or `manual` with `tags: [project]`): must have a `sources:` frontmatter list and a `## Sources` section linking to source pages.
- **Claim pages**: must cite source pages in frontmatter and inline.
- **Data pages**: must declare provenance in frontmatter and inline.
- **Synthesis pages**: should link to the claims, data, and entity pages that ground the argument.

## Bounded Session Rules

1. **Scope limit:** 5 pages maximum per session. No exceptions.
2. **Confirm gate:** Wait for human approval before writing the final version of any page.
3. **Flag gate:** Any change touching confidence, facts, sources, or ontology terms must be explicitly flagged.
4. **Stopping conditions:** Stop immediately if you encounter a split/merge decision, unresolved contradiction, category uncertainty, or missing source material.
5. **No broad rewrites:** Do not rewrite whole pages. Show only what changes and why.
6. **Audit trail:** Every session that edits pages must be logged in `wiki/WIKI_AUDIT_LOG.md`.

## Monthly Review Protocol

Once per month, a human must:

1. Read `wiki/FLAGGED_FOR_REVIEW.md` and resolve or re-prioritize open items.
2. Check `wiki/WIKI_AUDIT_LOG.md` for drift patterns (repeated violations, frequent flags, scope creep).
3. Update `wiki/ONTOLOGY.md` with any new canonical terms that have stabilized.
4. Run `make validate` and address any failures.
5. Review the past month's edited pages for hierarchy violations (interpretation bleeding downward, source pages containing analysis, etc.).

## Growth Path

Start strict on the above. As the wiki matures, introduce lightweight navigation layers:
- Reading paths for different audiences (10-minute overview, researcher, policy-focused)
- Curated lens pages that link existing pages in a declared sequence
- These require no restructuring; they are navigation indexes on top of clean base structure.

## Files That Govern This Wiki

| File | What it governs |
|---|---|
| `wiki/GOVERNANCE.md` | This file. Hierarchy, invariants, philosophy, session rules. |
| `wiki/ONTOLOGY.md` | Canonical terms, aliases, parent syntheses. Prevents semantic drift. |
| `wiki/TEMPLATES.md` | Section structure per page category. Derived from exemplars. |
| `wiki/QUALITY_RUBRIC.md` | What stub / usable / analysis / flagship means per category. |
| `wiki/FLAGGED_FOR_REVIEW.md` | Running log of ontology conflicts, split/merge candidates, unresolved flags. |
| `wiki/WIKI_AUDIT_LOG.md` | Session log of agent edits: date, pages touched, changes made, flags raised. |
| `CONTRIBUTING.md` | 50-line human entry point. Links to the above. |
| `docs/session-template.md` | Reusable prompt wrapper for every editing session. |
