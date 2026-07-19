# Wiki & Map Viewer

A single three-pane viewer that fuses the markdown wiki with the GeoJSON maps:
**nav · wiki page · live map**, with bidirectional sync (open a page → map flies
to it and scopes layers; click a feature on the map → that page loads).

## Run

```bash
cd wiki/explorer
./serve.sh                   # python3 -m http.server on :8765
# then open http://localhost:8765/wiki/explorer/
```

The viewer must be served over HTTP (not `file://`) — every fetch of GeoJSON
and markdown depends on it.

## What's in here

```
explorer/
  index.html                          # the viewer (entry point)
  serve.sh                            # tiny dev server
  shared/
    style.css                         # base stylesheet
    leaflet-init.js                   # makeMap, LayerManager, popupHTML, slug lookup
    source-used-by.js                 # computed backlinks / source Used By renderer
    wiki-loader.js                    # markdown loader, frontmatter split, wikilink rewriter
    wiki-search.js                    # fast lexical + structured search runtime
    wiki-vector-search.js             # on-demand semantic reranking for conceptual queries
    layer-manifest.json               # declarative layer definitions (29 layers)
    presets.json                      # named map lenses (mirrors docs/maps/*.html)
    bindings.json                     # slug ↔ feature(s) mapping (stand-in for frontmatter)
    wiki-page-index.json              # built by scripts/build_wiki_page_index.py
    wiki-page-meta.json               # built by scripts/build_wiki_page_meta.py
    wiki-backlinks.json               # built by scripts/build_backlinks.py
    wiki-fact-index.json              # structured facts for answer-first search
    wiki-search-index.json            # built by scripts/build_wiki_search_index.py
    wiki-vector-index.json            # quantized chunks built by scripts/build_wiki_vector_index.py
    wiki-search-aliases.json          # curated query expansion terms
```

## Data sources (live, not duplicated)

- Wiki markdown: `../pages/{sources,entities,concepts,syntheses,claims,data}/*.md`
- GeoJSON layers: `../../data/processed/maps/*.geojson`

## Interaction philosophy

The explorer is an evidence reader with a spatial companion, not a map dashboard
with articles attached. Its interaction rules are:

1. **Start with the user's question.** Find is the primary discovery surface;
   browse categories stay collapsed until the reader chooses one.
2. **State knowledge depth honestly.** A **Record** is a registry-backed factual
   page, **Analysis** adds substantial narrative and sourcing, and **Map only**
   means no wiki page exists. Visual polish must not blur those distinctions.
3. **Let the page lead and the map explain place.** Opening a page preserves the
   chosen map lens and adds only the context needed for that page.
4. **Claims and counts must come from the matching data path.** Structured search
   may summarize only structured facts. Lexical results may recommend a page but
   must not be presented as a factual project set. The map reports what actually
   resolved to geometry, not what merely has a binding entry.
5. **Prefer progressive disclosure.** Presets answer common questions; individual
   layers, the full wiki index, and long related-result lists are secondary tools.
6. **Every spatial detour is reversible.** Temporary search overlays preserve the
   previous preset, layers, centre and zoom, with an explicit restore action.
7. **Mobile presents one task at a time.** Find, Read and Map are distinct modes;
   a shared search URL reopens in Find, while a page-only link reopens in Read.

When behavior is ambiguous, choose the state that makes provenance, uncertainty
and the user's next reversible action clearest.

## Features

### Map presets (lenses)
A pill bar at the top of the map flips between six named layer sets:

| Preset | What it shows | Mirrors |
|---|---|---|
| **Overview** (default) | national project and system overview | — |
| **Tributaries** | rivers + downstream + operating / under-construction hydro | `nepal_tributary_explorer.html` |
| **Geopolitics** | basin polygons (Nepal + India), comparison rivers, origin/control callouts, downstream impact markers | `nepal_geopolitics_river_influence.html` |
| **Power system** | traced corridors, grid hubs, cross-border gateways, priority watchlist, storage shortlist, project cloud | `nepal_power_system_explorer.html` |
| **Solar system** | solar resources, projects and grid context | — |
| **Wiki minimal** | restrained map context for reading | — |

The current preset is reflected in the URL (`?preset=power_system`). Opening a wiki page **adds** that page's bound layers on top of the active preset rather than replacing it, so you keep your chosen lens. Use the `≡` button to open the per-layer toggle panel.

Deep-link example: `index.html?preset=geopolitics&page=koshi-basin` opens with the geopolitics lens *and* the koshi-basin page in one go.

Presets and layers are declarative: edit `shared/presets.json` to add a new lens or `shared/layer-manifest.json` to register a new GeoJSON layer.

### Resizable panes
Drag the vertical bars between panes. Widths persist in `localStorage`.
**Reset layout** in the app bar clears all viewer preferences (widths,
collapsed groups and map preferences).

### Nav
Collapsible category sections (Entities · Concepts · Claims · Syntheses · Data
· Sources). Entities are sub-grouped into **Basins / Projects / Institutions /
Geopolitics & Trade / Profiles** — subcategory inferred from frontmatter
`tags:` and slug patterns by `scripts/build_wiki_page_meta.py`. Spatial
anchoring is shown via the leading dot: ● = mapped, ○ = no spatial binding.

Categories start collapsed to keep discovery scannable. Click a category header
to expand it; state is persisted.

### Search and decision UX

The unified Find surface handles exact page lookup, normal-language questions,
structured project filters and source seeking. Structured matches produce an
answer-first summary, followed by grouped project, analysis, source and related
results. Queries and active filters are reflected in the URL. Keyboard users can
focus Find with `/` or Cmd/Ctrl+K and navigate results with the arrow keys.

Status, basin, storage and capacity questions are filtered through the fact
index before ranking. Conceptual questions show fast local results first and
load the optional semantic index only when reranking may help. Spatial result
sets can be shown as a temporary map-only overlay and then restored without
discarding the prior preset.

Search artifacts are rebuilt by `scripts/build_wiki_fact_index.py` from local processed map
datasets, by `scripts/build_wiki_search_index.py` from `wiki-page-meta.json`
plus `wiki-search-aliases.json`, and by `scripts/build_wiki_vector_index.py`
from local markdown chunks. The vector index uses
`mixedbread-ai/mxbai-embed-xsmall-v1` and ships normalized int8 vectors so the
hosted profile stays small.

## Adding a spatial page

Append an entry under `pages` in `shared/bindings.json`:

```json
"my-new-page-slug": {
  "type": "entity",
  "category": "project",
  "features": [
    { "layer": "hydropower_points", "match": { "field": "project", "value_contains": "My Project" } }
  ],
  "layers_on": ["country_outline", "basin_polygons", "hydropower_points"]
}
```

If your wiki page already has the slug `my-new-page-slug.md` under
`wiki/pages/entities/`, it'll appear in the nav automatically.

The bindings live centrally for now; same shape works as per-page YAML
frontmatter (`map:` block) when we want to migrate.

## Computed source Used By

Source-page `Used By` sections are not maintained in markdown. The reader loads
`shared/wiki-backlinks.json` and renders exact backlinks as `Used By` for source
pages. If page links change, rebuild wiki metadata before release.

## Regenerating the page indices

Run any time pages are added, removed, or retagged:

```bash
python3 scripts/build_wiki_page_index.py    # nav structure
python3 scripts/build_wiki_page_meta.py     # search corpus + subcategories
python3 scripts/build_wiki_fact_index.py    # factual Seek answers
python3 scripts/build_wiki_search_index.py  # static Search / Seek index
.venv/bin/python scripts/build_wiki_vector_index.py --local-files-only
```
