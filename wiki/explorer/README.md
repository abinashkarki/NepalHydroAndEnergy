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
    wiki-loader.js                    # markdown loader, frontmatter split, wikilink rewriter
    wiki-search.js                    # fast static Search / Seek runtime
    wiki-vector-search.js             # lazy query-vector boost for Seek
    layer-manifest.json               # declarative layer definitions (all 16 layers)
    presets.json                      # named map lenses (mirrors docs/maps/*.html)
    bindings.json                     # slug ↔ feature(s) mapping (stand-in for frontmatter)
    wiki-page-index.json              # built by scripts/build_wiki_page_index.py
    wiki-page-meta.json               # built by scripts/build_wiki_page_meta.py
    wiki-fact-index.json              # structured facts for factual Seek answers
    wiki-search-index.json            # built by scripts/build_wiki_search_index.py
    wiki-vector-index.json            # quantized chunks built by scripts/build_wiki_vector_index.py
    wiki-search-aliases.json          # curated Seek query expansion terms
```

## Data sources (live, not duplicated)

- Wiki markdown: `../pages/{sources,entities,concepts,syntheses,claims,data}/*.md`
- GeoJSON layers: `../../data/processed/maps/*.geojson`

## Features

### Map presets (lenses)
A pill bar at the top of the map flips between five named layer sets:

| Preset | What it shows | Mirrors |
|---|---|---|
| **Tributaries** (default) | rivers + downstream + operating / under-construction hydro | `nepal_tributary_explorer.html` |
| **Geopolitics** | basin polygons (Nepal + India), comparison rivers, origin/control callouts, downstream impact markers | `nepal_geopolitics_river_influence.html` |
| **Power** | traced corridors, grid hubs, cross-border gateways, priority watchlist, storage shortlist, project cloud | `nepal_power_system_explorer.html` |
| **Minimal** | country outline + basin polygons | — |

The current preset is reflected in the URL (`?preset=power_system`). Opening a wiki page **adds** that page's bound layers on top of the active preset rather than replacing it, so you keep your chosen lens. Use the `≡` button to open the per-layer toggle panel.

Deep-link example: `index.html?preset=geopolitics&page=koshi-basin` opens with the geopolitics lens *and* the koshi-basin page in one go.

Presets and layers are declarative: edit `shared/presets.json` to add a new lens or `shared/layer-manifest.json` to register a new GeoJSON layer.

### Resizable panes
Drag the vertical bars between panes. Widths persist in `localStorage`.
**Reset layout** in the app bar clears all viewer preferences (widths,
collapsed groups, search mode).

### Nav
Collapsible category sections (Entities · Concepts · Claims · Syntheses · Data
· Sources). Entities are sub-grouped into **Basins / Projects / Institutions /
Geopolitics & Trade / Profiles** — subcategory inferred from frontmatter
`tags:` and slug patterns by `scripts/build_wiki_page_meta.py`. Spatial
anchoring is shown via the leading dot: ● = mapped, ○ = no spatial binding.

Click a category header to collapse/expand it. State is persisted.

### Search modes
- **Search** — substring match on page titles. Instant. Best when you know the
  page or project name.
- **Seek** — routed discovery. Factual/superlative questions use the structured
  fact index first, then show supporting wiki pages. Facts without narrative
  wiki pages open generated data-record details and fly to the exact map feature,
  keeping the wiki curated without hiding complete map inventory. Conceptual
  questions search page text, tags, headings, phrase-aware aliases, and
  precomputed chunk vectors. It shows fast static results immediately, then may
  lazily load a small browser embedding model to add a meaning-based boost for
  the query. It never embeds the page corpus in the browser. Try queries like
  *"what is the biggest hydro plant"*, *"biggest solar project"*,
  *"winter deficit"*, *"firm power"*, *"India export risk"*, or
  *"storage projects Karnali"*.

Seek is rebuilt by `scripts/build_wiki_fact_index.py` from local processed map
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

## Regenerating the page indices

Run any time pages are added, removed, or retagged:

```bash
python3 scripts/build_wiki_page_index.py    # nav structure
python3 scripts/build_wiki_page_meta.py     # search corpus + subcategories
python3 scripts/build_wiki_fact_index.py    # factual Seek answers
python3 scripts/build_wiki_search_index.py  # static Search / Seek index
.venv/bin/python scripts/build_wiki_vector_index.py --local-files-only
```
