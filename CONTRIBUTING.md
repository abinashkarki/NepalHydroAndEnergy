# Contributing to the Nepal Energy Wiki

This wiki is a public research system about Nepal's electricity system. Every contribution must preserve traceable reasoning from source → extraction → synthesis → conclusion.

## Quick Start

1. Read `wiki/GOVERNANCE.md` — the hierarchy, invariants, and session rules.
2. Read `wiki/ONTOLOGY.md` — canonical terms and disallowed aliases.
3. Find the exemplar page for your category in `wiki/TEMPLATES.md`.
4. Copy its shape. Fill in your content.
5. Run `make validate` before submitting.

## The Authority Hierarchy

Interpretive freedom increases upward only:

- **Sources** (`sources/`) — ingest only. No interpretation.
- **Data / Entities / Claims** (`data/`, `entities/`, `claims/`) — facts and evidence. No strategic implications on data pages.
- **Syntheses** (`syntheses/`) — arguments and connections. The only layer where "so what" belongs.
- **Master Thesis** (`syntheses/master-thesis.md`) — the cross-synthesis narrative.

## The Most Important Rules

1. **Every page must explain itself in the first 2-4 sentences.** No slow openings.
2. **Every meaningful page must say why it matters for Nepal's electricity system.** Definition alone is not enough.
3. **Separate plain explanation from technical analysis.** Use `Simple Explanation` and `Technical Details` sections.
4. **Important numbers need evidence.** Every capacity, cost, date, or generation figure must be sourced or marked unknown.
5. **Distinguish fact, estimate, interpretation, and uncertainty.** Use confidence flags at claim level.
6. **One page = one job.** If a project page becomes an essay about national strategy, split or link out.
7. **Use predictable headings.** Boring headings are good: `Summary`, `Key Facts`, `Why It Matters`, `Evidence`, `Caveats`, `Sources`.
8. **Use internal links intentionally.** Links should help readers navigate the system.
9. **Do not manually duplicate structured project data.** If the CSV owns the fact, prose should explain its meaning.
10. **Unknown is acceptable; unsupported certainty is not.** A visible gap is better than a confident weak claim.

## Data Page Rule

Observation yes, interpretation no. Finding yes, implication no. Data pages present numbers; synthesis pages draw conclusions.

## Getting Help

- `wiki/TEMPLATES.md` — section structure per page type
- `wiki/QUALITY_RUBRIC.md` — what stub / brief / analysis / flagship means
- `docs/session-template.md` — prompt template for agent editing sessions
- `wiki/FLAGGED_FOR_REVIEW.md` — open questions and ontology conflicts

## Validation

Run before any commit:

```bash
make validate
```

This checks broken links, cache consistency, public language, map manifest, and spec CSV hygiene.

---

*For detailed governance, see `wiki/GOVERNANCE.md`.*
*For ontology and canonical terms, see `wiki/ONTOLOGY.md`.*
