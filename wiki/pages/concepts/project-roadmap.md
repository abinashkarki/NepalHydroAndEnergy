---
title: Project Roadmap
type: concept
created: 2026-04-20
updated: 2026-04-20
sources: []
tags: [meta, roadmap, planning]
---

# Project Roadmap

Live checklist for the Nepal Energy wiki-map explorer. Updated as each
item lands. Persists across agent sessions so either of us can pick up
where the other stopped.

Status legend: `[x]` done · `[~]` in progress · `[ ]` open · `[→]` deferred.

## Priority 1–3 · Content depth

### Step 1. Narrate top 10 anchor projects

Raise the `Narrated`-tier marker count from 2 to 10+ so the tier filter
is useful and the reader has real prose, not just spec tables.

- [x] Upper Tamakoshi — already narrated (reference template)
- [x] Budhi Gandaki — narrated, cites WB CEM 2025
- [x] Arun-3 — narrated + `arun-3-project-status-2025` source page
- [x] Kali Gandaki A — narrated + `kali-gandaki-a-adb-evaluation` source
- [x] Tanahu — extended + `tanahu-adb-status-2025` source
- [x] Dudhkoshi Storage — extended + `dudhkoshi-nea-proposal-2024` source
- [x] Upper Karnali — narrated + `upper-karnali-pda-record` source
- [x] Mugu Karnali — narrated + `mugu-karnali-feasibility-2025` source
- [ ] West Seti (Bajhang/Doti, 750 MW, storage; recent Indian re-entry) — reserved for user
- [ ] Pancheshwar (Darchula/Uttarakhand, 6720 MW, bi-national treaty) — reserved for user

Template: bold 1-sentence opener · Specifications table · Significance
section · Limitations/Controversies · 2+ primary sources · 3+ inline
`[[wikilinks]]`.

### Step 2. Wikimedia Commons image fetcher

- [x] `scripts/fetch_commons_images.py` — Commons search + CC-license
      filter + download to `wiki/assets/images/<slug>/` + idempotent
      frontmatter patching. Near-duplicate collapse and minimum-width
      filter. Per-slug `_commons.json` manifest captures attribution.
- [x] Batch mode with curated query map for 15 slugs; 50 images pulled
      on first sweep (Kali Gandaki A, Kulekhani cascade, all four
      basins all got real in-subject photos; survey-stage projects
      fell back to district scenery).
- [x] `--sync` mode prunes frontmatter entries when images are
      deleted from disk — user curation workflow confirmed.

### Step 3. Sources & citations discipline

- [ ] `## Sources` convention on all entity pages
- [ ] `scripts/check_sources.py` — flags pages with claims but no cites
- [ ] Require at least one primary source for the top-10 narrated

## Priority 4–6 · Graph structure

### Step 4. Backlinks & related pages

- [x] `scripts/build_backlinks.py` — scans `[[slug]]` refs, writes
      `wiki/explorer/shared/wiki-backlinks.json` (570+ refs, 71 targets)
- [x] wiki-loader renders grouped "Referenced by" footer with context
      snippets
- [x] Chained into `gen_wiki_stubs.py --write` regeneration pipeline
- [x] Code-span-aware scanner (skips wikilink-like examples in templates)

### Step 5. Transmission corridor ↔ wiki bindings ✅

- [x] 10 corridor / cross-border pages written:
      - Corridors: [[hetauda-dhalkebar-inaruwa-backbone]], [[mca-central-400]],
        [[khimti-dhalkebar-corridor]], [[hetauda-bharatpur-bardaghat-corridor]],
        [[dana-kushma-butwal-corridor]]
      - Cross-border: [[dhalkebar-muzaffarpur]], [[gorakhpur-butwal-interconnection]],
        [[inaruwa-purnea-interconnection]], [[kataiya-kushaha-interconnection]],
        [[chameliya-jauljibi-interconnection]]
- [x] Source compilation page [[nepal-transmission-landscape-2025]]
- [x] Bindings in `bindings.json` for all ten features
- [x] Alias `transmission_corridors` added to `transmission_traced_network` so
      clicks on major-network segments resolve to the parent corridor page
- [x] Cross-links from `claim-transmission-immediate-blocker`, `arun-3`,
      `khimti-i` and `bangladesh-trade-route` to the new corridor pages
- [x] Makes the "Power" preset actually narrate

### Step 6. Preset narrative landing pages

- [ ] `narrative_slug` field per preset in `presets.json`
- [ ] Six short landing pages (tributary / koshi / power / geopolitics /
      rivers / minimal)
- [ ] Auto-open on preset switch

## Priority 7–8 · Reproducibility & authoring

### Step 7. `make regenerate` & deterministic build-id

- [ ] `Makefile` with targets: `stubs`, `indexes`, `validate`, `all`
- [ ] `wiki/explorer/shared/build-id.txt` bumped by build, read via
      `<meta name="np-build">` for deterministic cache-busting

### Step 8. `validate_wiki.py` integrity checker

- [ ] Every binding points to an existing slug
- [ ] Every `layers_on` key resolves in the manifest
- [ ] Every `features[].layer` resolves
- [ ] Every `[[wikilink]]` resolves (or is flagged)
- [ ] No orphan entity `.md` without bindings
- [ ] Runs as `make validate`

## Priority 9–10 · Polish & shareability

### Step 9. Shareable deep-links

- [ ] Hash fragment encoding of `{ preset, layers[], slug, tier,
      basemap }`
- [ ] Copy-link button in the toolbar

### Step 10. Mobile/small-screen fallback

- [ ] `@media (max-width: 900px)` — three-pane collapses to tabbed
      layout (Nav · Wiki · Map)

## Completed milestones (archive)

- Explorer foundation: three-pane layout, Leaflet init, layer manifest
- 83 auto-generated project stubs (`hydropower_operating/construction ≥ 20 MW`)
- Three-tier marker system + segmented filter
- Image filmstrip + lightbox from frontmatter
- Cache-busting for JSON indexes and markdown fetches
- Curated-layer exemption from tier filter
- Tier-state banner
- Popup handshake fixes ("Showing in reader", optimistic currentSlug)
- "buildReverseIndex" exact-match binding fix

## See also

- [[hydropower-potential-categories]]
- [[run-of-river-hydropower]]
- [[firm-power]]
