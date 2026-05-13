# Page Templates

Derived from exemplars. Use these as the canonical section structure for each category. Contributors should copy the shape of the exemplar page linked in each section.

---

## Brief Block (cross-category)

Every operating-project entity, every major claim, every intervention, and every concept that is referenced by a synthesis page should carry a **brief block** at the top of the page. The block is a 200-word, six-number, one-signal summary that serves first-time readers and powers the persona briefing packs at `wiki/explorer/briefing-packs/`.

The brief is **orthogonal to the page_quality tier** — it is a structured summary that lives at the top of pages of any tier. It is built and refreshed from the frontmatter `brief:` object by `scripts/build_briefs.py`.

**Frontmatter shape:**

```yaml
brief:
  headline: "One sentence (≤140 chars). The thing a reader should remember."
  what: "One short paragraph (≤300 chars). What this is and where it sits."
  metrics:
    - { label: "Capacity",          value: "144 MW" }
    - { label: "Design energy",     value: "860 GWh/yr" }
    - { label: "Avg actual",        value: "~592 GWh/yr (−30%)" }
    - { label: "Commissioned",      value: "2002" }
    - { label: "PPA dry",           value: "—" }
    - { label: "Dry-season share",  value: "~22%" }
  signal: amber          # green | amber | red — see semantics below
  signal_note: "Aging assets, sediment, rehab overhang; firm-but-declining."
  why_it_matters: "The reference case for what an NEA-run multilaterally-financed plant looks like at 20+ years."
  audiences: [policymakers, investors, journalists]   # which persona packs include this brief
```

**Visible markdown block** (auto-generated between markers, do not hand-edit):

```markdown
<!-- generated:brief:start -->

## Brief

<p class="wiki-brief-signal" data-signal="amber"><strong>Signal: Amber.</strong> Aging assets, sediment, rehab overhang; firm-but-declining.</p>

**Nepal's largest operating plant; 144 MW since 2002; ~30% under design energy.** Run-of-river-with-pondage at Mirmi, the NEA-owned, ADB+JBIC-funded fleet anchor.

| Capacity | Design energy | Avg actual | Commissioned | PPA dry | Dry-season share |
|---|---|---|---|---|---|
| 144 MW | 860 GWh/yr | ~592 GWh/yr (−30%) | 2002 | — | ~22% |

_Why it matters: The reference case for what an NEA-run multilaterally-financed plant looks like at 20+ years._

<!-- generated:brief:end -->
```

**Signal semantics by page type:**

| Page type | green | amber | red |
|---|---|---|---|
| Operating project (entity) | Performing as designed, no major risk | Aging / under-performing / rehab overhang / financial strain | Stranded / defaulted / in litigation / safety event |
| Claim | High confidence, settled | Medium-high with caveats | Active dispute or contradicting evidence |
| Intervention | High political feasibility | Medium feasibility / contested | Low feasibility / blocked |
| Concept / synthesis | Argument is settled in the wiki | Argument is partially settled | Argument is unresolved or contested |

**Rules:**

- Six metrics is the target. Five is acceptable. Four is the minimum.
- `headline` and `what` together should be ≤200 words.
- `why_it_matters` is one sentence. It is the only place a brief is allowed to gesture at "so what" — and only as context, not policy prescription.
- `audiences` controls which briefing pack the entry appears in. Omit to include in none. Use `[policymakers, investors, journalists]` for system-spine pages.
- Build / refresh: `python3 scripts/build_briefs.py --write --inject --packs`.

---

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
