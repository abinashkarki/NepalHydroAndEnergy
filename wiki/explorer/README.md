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
    wiki-bm25.js                      # tiny BM25 index for "Content" search
    wiki-semantic.js                  # transformers.js loader + IndexedDB embedding cache
    layer-manifest.json               # declarative layer definitions (all 16 layers)
    presets.json                      # named map lenses (mirrors docs/maps/*.html)
    bindings.json                     # slug ↔ feature(s) mapping (stand-in for frontmatter)
    wiki-page-index.json              # built by scripts/build_wiki_page_index.py
    wiki-page-meta.json               # built by scripts/build_wiki_page_meta.py
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
- **Filter** — substring match on titles. Instant. Best when you know the title.
- **Content** — BM25 ranking over the full wiki body (with title boost). Instant.
  Snippets show matched terms `<mark>`-highlighted. Powered by `wiki-bm25.js`
  reading `wiki-page-meta.json`.
- **Semantic** — cosine similarity over embeddings produced in-browser by
  [`Xenova/all-MiniLM-L6-v2`](https://huggingface.co/Xenova/all-MiniLM-L6-v2)
  via [transformers.js](https://huggingface.co/docs/transformers.js).
  First activation downloads the model (~25 MB) and embeds all 74 pages
  (≈ 10 s on this corpus). Both the model weights and the embeddings are
  cached in IndexedDB; subsequent loads are instant and fully offline.
  Try queries like *"why is Nepal not exporting more electricity to India?"*
  or *"monsoon flooding and dam safety"* — the right pages surface even when
  the literal words aren't present.

To rebuild semantic embeddings (e.g. after editing pages), open the browser
devtools and run `await window.NepalExplorer.semantic.clearCache()`, then
re-activate Semantic mode.

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
```
