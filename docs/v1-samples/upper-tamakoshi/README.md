# Upper Tamakoshi, three ways

Three sample pages, written for comparison while we decide what V1 of the wiki is for. All three use the same evidence: the current `wiki/pages/entities/upper-tamakoshi.md`, the UTKHPL 2026 filings, and the UKHLL research compilation. They were written independently of each other.

| | [Learning instrument](learning-instrument.md) | [Public reference](public-reference.md) | [Project registry](project-registry.md) |
|---|---|---|---|
| Reader | You, trying to understand the sector | A journalist, student or citizen | A machine, a map, or anyone comparing projects |
| Opens with | A puzzle: "the plant that ended load-shedding is in trouble. How?" | A four-sentence neutral lead | A record header: slug, aliases, status, capacity |
| Allowed to interpret? | Yes. That's its job | No. It only points to where interpretation lives | No. Minimal prose |
| Unit of content | A line of reasoning | A dated, cited fact | A row: entity, metric, period, value, source, grade |
| Handles conflicting evidence by | Showing how the conflict changes the reasoning | Listing it in a "disputed" table | Keeping both rows and marking which one is preferred |
| Links outward to | Concept pages. The project is a lens on the sector | Syntheses, for the "why it matters" | Nothing argumentative |
| How it ages | Stays valid as a learning trail. Its conclusions need revisiting | Needs a date check each review | Append rows. The page re-renders |
| Cost of "add the latest earnings" | A re-think, but only for cases that are interesting | Edit the key-facts table and the finance section | Append 3–4 rows to `facts.csv` |

## What all three surfaced that the live page hides

- **The latest filing reports a profit.** UTKHPL's FY2082/83 third-quarter statement shows NPR 286.8M net profit, with finance costs at about half of revenue. The live page says the plant "cannot break even even when the river cooperates." None of the three samples could square these two, and all three flagged it.
- **The revenue year is likely wrong.** The primary filing gives NPR 8.679B for FY2080/81. The live page puts about 8.68B in FY2079/80 and a computed "9.3–9.5B" in FY2080/81. That computed ceiling is what the "structurally inevitable default" argument rests on.
- **The default story rests on secondary evidence.** Generation percentages, the ICRA "D" rating, the flood losses and the insurance-exclusion story all come from a deep-research compilation, not from a primary filing in the wiki.
- **Smaller inconsistencies:**
  - Construction took "7 years" or "11 years", depending on the section.
  - Rolwaling adds 216.51 GWh (filing) or 212 GWh (compilation).
  - The wet tariff is NPR 3.74 (registry) or 3.63 ([[ppa-pricing]]).

## Notice

- The **registry** is the only form in which "update every company's earnings" stays cheap. It's also the least interesting to read.
- The **learning instrument** is the only form that teaches you something about the *sector*. It's also the only one that goes stale quietly, because a conclusion can outlive its inputs.
- The **public reference** sits between them. It can be generated largely from the registry, with a thin layer of written prose and links out to the analysis pages.

One way to combine them: the registry holds facts, the reference page renders them, and the learning pages exist only for the handful of cases that actually teach something. Each learning page would cite registry rows rather than restating numbers.

## Files

- `learning-instrument.md`
- `public-reference.md`
- `project-registry.md`
- `registry-data/facts.csv` (60 fact rows)
- `registry-data/events.csv` (11 events)
- `registry-data/open_items.csv` (12 open items)
