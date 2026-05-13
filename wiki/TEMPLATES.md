# Page Templates

Derived from exemplars. Use these as the canonical section structure for each category. Contributors should copy the shape of the exemplar page linked in each section.

## Source Pages (`sources/`)

**Exemplar:** `wiki/pages/sources/wb-country-economic-memo-2025.md`

```markdown
## Summary
One paragraph: what this source is, who produced it, when, and what kind of document.

## Key Findings
Bulleted data points relevant to Nepal's energy system. Use tables where appropriate.

## Relevance
Which wiki pages cite this source and for what claims. Use wikilinks.

## Limitations
Known biases, gaps, outdated elements, or methodological caveats.

## Used By
List of pages that reference this source.
```

**Rule:** No interpretation. No "so what." No strategic implications.

---

## Entity Pages (`entities/`)

**Exemplar:** `wiki/pages/entities/arun-3.md` or `wiki/pages/entities/chilime.md`

```markdown
## Summary
Bold 1-sentence opener + 1-2 paragraphs of context.

## Specifications
Registry-backed spec table (auto-generated for stubs).

### Engineering
Key technical parameters.

### Output
Design energy, PLF, seasonal profile.

### Financial
Cost, PPA rates, financing structure.

### Governance
Developer, concession, lead financier.

### Schedule
Construction status, COD target, completion %.

## Significance / Why It Matters
What this project/actor means for the Nepal electricity system.

## Limitations & Controversies
Known risks, delays, disputes, or caveats.

## See also / Related
Wikilinks to related pages.

## Sources
Links to source pages.
```

**Rule:** One page = one project or actor. No policy prescriptions. Auto-stubs keep it lighter.

---

## Concept Pages (`concepts/`)

**Exemplar:** `wiki/pages/concepts/storage-deficit.md` or `wiki/pages/concepts/seasonal-mismatch.md`

```markdown
## Summary
One paragraph: what this concept is.

## Simple Explanation
Plain-language explanation for non-experts.

## Why It Matters in Nepal
Nepal-specific relevance — this is mandatory.

## Technical Explanation
Detailed mechanics, numbers, or system dynamics.

## Examples
Concrete examples from the Nepal system.

## Common Misunderstandings
What this concept is NOT.

## Related
Wikilinks.

## Sources
Links to source pages.
```

**Rule:** Three-paragraph minimum. If it can't sustain what-it-is + why-it-matters-in-Nepal + what-it-connects-to, it's a definition, not a concept page.

---

## Claim Pages (`claims/`)

**Exemplar:** `wiki/pages/claims/claim-mw-not-equal-value.md`

```markdown
## Claim
One bold sentence stating the argument.

## Evidence
Bullet points or paragraphs with source-backed facts.

## Confidence Rationale
Why the confidence level is what it is.

## Unresolved Issues
Gaps, needed verification, or open questions.

## Boundary Conditions
What this claim does NOT say.

## Related
Wikilinks.
```

**Rule:** Confidence flags must appear at claim level, not page level. Each claim carries its own flag.

---

## Data Pages (`data/`)

**Exemplar:** `wiki/pages/data/data-storage-comparison.md`

```markdown
## Summary
One paragraph: what this dataset or layer shows.

## What This Shows
Tables, figures, or descriptions of the data.

## Coverage / Method
How the data was produced, what it covers, and what it excludes.

## Caveats
Known limitations, reconciliation notes, contradictions.

## Linked Data
Links to CSVs, GeoJSON, or other machine-readable outputs.

## Chart Specification
If applicable: what chart should be built from this data.

## Sources
Provenance.
```

**Rule:** Observation yes, interpretation no. Finding yes, implication no. Every `[!finding]` callout must be bounded — no "therefore," "proves," or policy prescriptions.

---

## Synthesis Pages (`syntheses/`)

**Exemplar:** `wiki/pages/syntheses/master-thesis.md`

```markdown
## Summary
One paragraph: the core argument.

## Core Argument
The connected reasoning, with links to evidence.

## Evidence Trail
Which claims, data, and entities support this.

## Implications
What follows if this argument is correct.

## Open Questions
What remains unresolved.

## Related
Wikilinks.
```

**Rule:** This is the ONLY layer where "so what" belongs. Every implication must trace back to L2 evidence.

---

## Intervention Pages (`interventions/`)

**Exemplar:** `wiki/pages/interventions/intervention-transmission-completion.md`

```markdown
## The Intervention
What action is proposed, with specificity.

## Theory of Change
Why this intervention would work — the causal logic.

## Current Status
What is known, verified, and pending.

## What This Unlocks
Quantified or specific benefits if implemented.

## Research Gaps
What is still unknown or unverified.

## Political Feasibility
Who benefits, who resists, realistic path.

## Related
Wikilinks.
```

**Rule:** Each intervention must have a theory of change, current status assessment, and honest research gaps.

---

*These templates are living documents. Update them as exemplars improve.*
