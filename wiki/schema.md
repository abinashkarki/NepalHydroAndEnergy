---
title: Schema
type: overview
created: 2026-04-14
updated: 2026-04-14
---

# Wiki Schema

Public wiki schema for the Nepal Energy & Hydropower knowledge hub. The schema
keeps source notes, entity records, concepts, claims, data pages, and synthesis
pages separate so readers can tell analysis from evidence and registry records.

## Page Types

| Type | Directory | Purpose |
|------|-----------|---------|
| source | pages/sources/ | Summary of one primary source document |
| entity | pages/entities/ | Page about a specific thing (river, project, org, country) |
| concept | pages/concepts/ | Page about an idea, pattern, or analytical distinction |
| synthesis | pages/syntheses/ | Cross-cutting analysis or filed query answer |
| claim | pages/claims/ | Tracked research claim with confidence and provenance |
| data | pages/data/ | Reusable data table or figure specification |
| overview | (root) | Top-level wiki pages (index, schema, log) |

## Filename Convention

Lowercase, hyphens, no spaces. Examples:
- `koshi-basin.md`
- `nea-annual-report-fy2024-25.md`
- `claim-timing-not-volume.md`

## Frontmatter

Every page requires YAML frontmatter:

```yaml
---
title: Human-Readable Title
type: entity | concept | source | synthesis | claim | data | overview
created: YYYY-MM-DD
updated: YYYY-MM-DD
sources: []
tags: []
---
```

Source pages add:
```yaml
source_type: report | paper | dataset | policy | treaty | other
source_author: Organization or Author
source_date: YYYY-MM-DD
source_url: https://...
```

Claim pages add:
```yaml
confidence: high | medium | low
status: stable | needs-update | needs-narrowing | contested
claim_id: C-NNN
```

Data pages add:
```yaml
figure_type: table | chart-spec | map-spec
```

Entity pages may add an **images list**. Images render as a compact filmstrip
at the top of the reader pane (click to enlarge):
```yaml
images:
  - src: upper-tamakoshi/tailrace.jpg
    caption: Tailrace outflow near Gongar, Dolakha.
    credit: NEA Annual Report FY2023–24
    license: gov-permissive
  - src: upper-tamakoshi/headrace-portal.jpg
    caption: Lamabagar intake and headrace tunnel portal.
    credit: Wikimedia Commons / User:X
    license: CC-BY-SA-4.0
```
- `src` is relative to `wiki/assets/images/`.
- `caption` is required and is shown under the thumbnail.
- `credit` + `license` are required for any image not in the public domain.
- Empty list `images: []` is valid for registry-backed pages without public images yet.

Auto-stub entity pages include `generator: auto-stub` in frontmatter so the
stub generator can safely refresh their spec tables without touching prose.

## Linking

- Use `[[page-name]]` wikilinks (no path, no extension)
- Every page should have at least two outbound links
- Cross-reference liberally — links are cheap, orphans are expensive

## Citations

Reference sources inline with callout blocks:
```markdown
> [!cite] source-filename
> Specific claim or quote from the source.
```

## Callouts

| Callout | Purpose |
|---------|---------|
| `> [!note]` | Ambiguity, editorial comment |
| `> [!warning]` | Something may be outdated or uncertain |
| `> [!contradiction]` | Conflict between sources |
| `> [!gap]` | Known missing information worth investigating |
| `> [!cite]` | Inline source citation |

## Evidence Provenance

Where claims or data depend on a specific source family, note the public source
page in `sources:` and use cite callouts in the body. Internal drafting
provenance should stay out of public-facing narrative unless it is necessary to
explain a data conflict.

## Claim Governance

High-impact core claims are governed through `data/claim_registry.yaml` — a
hand-reviewable YAML registry that pins canonical numeric facts and protects
claims from stale or contradictory data drift.

### Registry Fields

**Metrics** define canonical narrative facts and the wiki pages that serve as
their single source of truth:

```yaml
metrics:
  grid_electricity_share_final_energy:
    source_slug: data-final-energy-mix
    canonical_text:
      - "7.23%"
    deprecated_text:
      - "grid ~4.96%"
    note: "FY 2079/80 WECS final-energy denominator."
```

**Claims** declare which claim pages are governed, their tier, and the metrics
they depend on. Dependent metric `canonical_text` entries are required in the
claim page, and dependent metric `deprecated_text` entries are forbidden:

```yaml
claims:
  C-034:
    slug: claim-domestic-led-strategy
    tier: core
    depends_on:
      - grid_electricity_share_final_energy
```

Claim entries may also add `required_text` or `forbidden_text` for extra
claim-specific anchors that do not belong in a reusable metric.

### Governance Tiers

| Tier | Behavior |
|------|----------|
| `core` | Text-anchor and freshness issues **fail** validation. Resolve before merging. |
| `supporting` | Text-anchor and freshness issues **warn** only. Structural integrity (duplicate IDs, missing slugs, unknown metrics) still fails. |

### Validation

Run `make validate` to check all governed claims. The check fails when:

- A claim page has a duplicate `claim_id`
- A `core` registry entry points to a missing claim slug
- A governed claim page's frontmatter `claim_id` does not match the registry key
- A governed claim depends on an unknown metric
- A metric `source_slug` does not exist in the wiki
- A registry metric, claim, tier, or text-anchor field is malformed
- A governed `core` claim is missing any `required_text`
- A governed `core` claim contains any `forbidden_text`
- A governed `core` claim's `updated:` date is older than one of its metric source pages' `updated:` date

Warnings are issued for unregistered claim pages and unused metrics.

### Purpose

The registry is not a full fact-governance system. It exists to preserve
narrative integrity for the public argument by catching stale numeric anchors
before they drift into contradiction with canonical data pages. Long-tail
source notes and ordinary wiki prose remain editorial.
