---
title: Schema
type: overview
created: 2026-04-14
updated: 2026-04-14
---

# Wiki Schema

Project-scoped wiki for the Nepal Energy & Hydropower research. Mirrors the
personal wiki schema at `/Users/hi/projects/mypersonalpedia/wiki/` so pages
can be copied over after video essay work is complete.

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
providers: [hermes, claude, codex, gemini]
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
- Empty list `images: []` is valid (placeholder for auto-stubs).

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

## Provider Provenance

Where claims or data originate from the multi-provider research, note provenance:
- **hermes** — multi-wave research program with source extraction
- **claude** — narrative report + QA document
- **codex** — sourced QA + report with 15 verified URLs
- **gemini** — 22-page PDF with 74 works cited, deepest engineering detail

## Migration to Personal Wiki

After the video essay, durable pages (mostly concepts, entities, syntheses)
copy straight into the personal wiki. Claims and data pages stay here as
project archive.
