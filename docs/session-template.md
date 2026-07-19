# Wiki Editing Session Template

Use this template at the start of every weekly editing session. Copy it verbatim, fill in the three bracketed variables, and paste it as the first message.

---

## Context

You are editing the Nepal Energy Wiki. Before doing any work, read these documents in order:

1. `wiki/GOVERNANCE.md` — authority hierarchy, invariants, and agent operating rules
2. `wiki/ONTOLOGY.md` — canonical terms, allowed aliases, and disallowed aliases
3. `[EXEMPLAR_PAGE]` — the reference page for this category (copy its structure)

Do not begin editing until you have read all three.

## Scope

- **Category:** [CATEGORY]
- **Pages to work through (in this order):** [PAGE_1], [PAGE_2], [PAGE_3], [PAGE_4], [PAGE_5]

**Hard limit:** 5 pages maximum. Do not edit any other pages. Do not proceed to the next page until the current one is fully diagnosed, proposed, flagged, and confirmed.

## Source-Page Rule

When editing `sources/*` pages: do not write a manual `## Used By` section. Source-page `Used By` is rendered from `wiki/explorer/shared/wiki-backlinks.json`; run `make wiki-index` after link changes so the computed display stays current.

## Rules

For each page, follow this loop exactly — do not skip steps:

1. **DIAGNOSE:** State in one sentence what structural or content issue this page violates most, referencing the relevant rule or template section by name. If the page is already compliant, say so and move to the next page.
2. **PROPOSE:** Write only the specific changes. Do not rewrite the whole page. Show what changes and why, citing the rule by name.
3. **FLAG:** If any change touches a confidence level, a factual claim, a source linkage, or an ontology term, flag it explicitly for human review.
4. **CONFIRM:** Wait for my approval before writing the final version.

## Invariants (never violate)

- No deletion of pages, claims, or sourced data without explicit human approval
- No renaming of slugs or canonical concepts without logging in `wiki/FLAGGED_FOR_REVIEW.md`
- No confidence inheritance across claims — each claim carries its own flag
- No interpretation inside source pages; no synthesis conclusions on data pages
- No introduction of new canonical terms not already in `wiki/ONTOLOGY.md` — flag for review instead
- No replacement of sourced claims with paraphrased summaries
- Before removing any interpretive content, grep for it downstream first

## Stopping conditions

Stop immediately and report if you encounter any of the following:

- A page that needs to be split or merged
- A contradiction with another page that you cannot resolve within the existing hierarchy
- Uncertainty about which category a piece of content belongs to
- A claim that requires new source material not already cited
- Any of the 5 pages is completed and you have human approval to proceed

## Philosophy

The wiki prioritizes epistemic clarity over brevity, novelty, or prose quality. Preserve traceable reasoning chains from source → extraction → synthesis → conclusion. When in doubt, preserve structure and provenance over elegance.

---

## How to fill in the variables

| Variable | What to write |
|---|---|
| `[EXEMPLAR_PAGE]` | File path to the reference page for this category, e.g. `wiki/pages/syntheses/master-thesis.md` |
| `[CATEGORY]` | One of: `syntheses`, `sources`, `claims`, `concepts`, `data`, `entities`, `interventions` |
| `[PAGE_1]` ... `[PAGE_5]` | Slugs of the 5 pages to edit (no file extension), in priority order |
