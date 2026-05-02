# Nepal Energy Wiki — MCP Skill

You have access to the Nepal Energy Wiki via MCP. This is a 319-page structured knowledge base about Nepal's hydropower sector — projects, companies, PPA pricing, grid bottlenecks, hydrological risk, AD penalties, insurance, and institutional governance.

The wiki lives at `transparentgov.ai/wiki/explorer/` and is backed by a local MCP server that exposes 10 tools. Every tool returns plain text; there are no images, no API keys, and no network calls.

---

## Setup

Add this to your MCP client config:

```json
{
  "mcpServers": {
    "nepal-energy-wiki": {
      "command": "python3",
      "args": ["scripts/wiki_mcp_server.py"],
      "cwd": "/Users/hi/projects/nepalEnergy"
    }
  }
}
```

Or run directly: `cd /Users/hi/projects/nepalEnergy && make mcp`

**Prerequisite:** `pip install mcp` — the server needs the `mcp` SDK. All wiki data is pre-built static JSON (no external services).

**Important:** The wiki indices must be current. Run `make wiki-index` before starting the MCP server if pages have been added or modified since the last build. The server reads from `wiki/explorer/shared/*.json`.

---

## Page categories

| Category | Count | What's in it |
|---|---|---|
| `entities` | 158 | Projects, companies, institutions, basins, transmission corridors |
| `concepts` | 45 | Analytical frameworks: PPA pricing, Q-design, AD penalties, triple-authority, insurance |
| `claims` | 16 | Investigative claims with evidence assessment |
| `data` | 59 | Structured data pages: layer documentation, demand curves, trade time series |
| `sources` | 31 | Source documents with key data points |
| `syntheses` | 10 | Cross-cutting narrative syntheses |

---

## Tool Reference

### 1. `wiki_search(query, top_k=10)`

BM25 lexical search across all 319 pages. The best starting point for any question.

**Usage:**
```
wiki_search("Chilime PPA rate advantage")
wiki_search("AD penalty formula")
wiki_search("Sahas Urja financial performance")
```

**Returns:** Ranked list of (slug, score, excerpt). Use the slug with `wiki_get_page()` to read the full page.

---

### 2. `wiki_get_page(slug)`

Get full metadata and Markdown body of any wiki page.

**Usage:**
```
wiki_get_page("nea-triple-authority")
wiki_get_page("q-design-discharge")
wiki_get_page("chilime")
```

**Returns:** Title, category, type, tags, excerpt, and full body text (truncated at 8000 chars).

---

### 3. `wiki_get_entity(slug)`

Get an entity page — includes specification tables (capacity, status, river, district) extracted from the body.

**Usage:**
```
wiki_get_entity("sahas-urja")
wiki_get_entity("upper-tamakoshi")
wiki_get_entity("chameliya-hydropower")
wiki_get_entity("barahi-hydropower")
```

---

### 4. `wiki_get_concept(slug)`

Get a concept page — analytical framework, mechanism explanation, or policy argument.

**Usage:**
```
wiki_get_concept("nea-triple-authority")
wiki_get_concept("ppa-pricing")
wiki_get_concept("ad-penalties")
wiki_get_concept("q-design-discharge")
wiki_get_concept("hydro-insurance")
```

---

### 5. `wiki_get_backlinks(slug, top_k=20)`

Reverse wikilink graph — find every page that links to a given page. Essential for understanding how ideas connect.

**Usage:**
```
wiki_get_backlinks("chilime")
wiki_get_backlinks("nea-triple-authority")
```

**Returns:** List of referring pages, each with the surrounding context where the link appears.

---

### 6. `wiki_get_wikilinks(slug)`

Forward wikilink graph — extract all `[[links]]` from a page's body, categorized as valid (existing pages) or broken.

**Usage:**
```
wiki_get_wikilinks("nea-triple-authority")
```

---

### 7. `wiki_list_pages(category=None, limit=50)`

List pages by category, or show category overview with counts if no category specified.

**Usage:**
```
wiki_list_pages()                        # overview
wiki_list_pages("entities", limit=20)    # first 20 entities
wiki_list_pages("concepts")              # all concepts
```

---

### 8. `wiki_get_facts(limit=50)`

Structured facts about hydropower projects from the fact index — capacity, license type, river, province, district. Built from GeoJSON map layers.

**Usage:**
```
wiki_get_facts(limit=30)
```

**Returns:** Table of project facts.

---

### 9. `wiki_get_all_entities()`

Compact table of all 158 entity pages with capacity, status, and tags where available. Faster than calling `wiki_list_pages("entities")` + individual `wiki_get_entity()` calls.

**Usage:**
```
wiki_get_all_entities()
```

---

## Research patterns

### "What does the wiki say about X?"

```
wiki_search("your topic")        → find relevant pages
wiki_get_page("best-match-slug") → read the top result
wiki_get_backlinks("that-slug")  → see what else links to it
```

### "Compare two projects"

```
wiki_get_entity("chilime")
wiki_get_entity("sahas-urja")
```

### "Trace an argument through the wiki"

```
wiki_get_concept("nea-triple-authority")   → start with the framework
wiki_get_backlinks("nea-triple-authority") → see what pages invoke it
wiki_get_wikilinks("nea-triple-authority") → see what it references
```

### "Find all projects on a river"

```
wiki_search("Solu Khola")
wiki_get_entity("sahas-urja")
```

### "What's the evidence for a claim?"

```
wiki_get_page("claim-transmission-immediate-blocker")
wiki_get_page("claim-climate-harder-not-easier")
```

---

## Key pages to know about

### Accountability framework (concepts)

| Slug | What it covers |
|---|---|
| `nea-triple-authority` | NEA as Dispatcher, Single Buyer, and Penalty Administrator — the central governance framework |
| `ppa-pricing` | PPA rate comparison table, Chilime 37.1% differential, NEA internal cost vs commercial rates |
| `q-design-discharge` | Q40/Q45 design parameters, WECS/DHM 1990 method, generation performance table, DSCR break-point |
| `ad-penalties` | Availability Declaration penalty formula, Barahi case study, structural impossibility argument |
| `hydro-insurance` | Project-level premium data, reinsurer withdrawal, market concentration |
| `ipo-hydropower-bailout` | IPO/rights share table, Chilime contrast, triple-authority blindspot |

### Case-study entities

| Slug | What it covers |
|---|---|
| `chilime` | NEA subsidiary, 110%+ overperformance, 1997 PPA with Regular/Excess billing architecture, 37.1% blended rate advantage |
| `sahas-urja` | Private IPP, 86 MW, NPR 172M/MW build cost, standard 4.80/8.40 rate — proves the rate only works at exceptional scale |
| `upper-tamakoshi` | NEA subsidiary, 456 MW, 77% revenue to interest, NPR 3.63/6.96 suppressed PPA rate |
| `chameliya-hydropower` | NEA-owned, $7.5M/MW state capital inefficiency, NPR 3.04/kWh internal cost, decade-long delay |
| `barahi-hydropower` | Sub-10 MW, AD penalty deducted despite ERC exemption — primary audited case |

### Essential data pages

| Slug | What it covers |
|---|---|
| `data-trade-time-series` | Monthly import/export volumes and revenue |
| `data-domestic-demand` | Sectoral electricity consumption breakdown |
| `data-nepal-peak-load-curve-fy2024-25` | System peak load shape |
| `data-solar-hydro-lcoe` | Solar vs hydro levelized cost comparison |
| `data-storage-comparison` | Nepal's storage capacity vs international benchmarks |

### Core syntheses

| Slug | What it covers |
|---|---|
| `seasonal-mismatch` | Why annual water abundance ≠ year-round electricity |
| `stranded-generation` | Curtailment economics, 7 named contingency projects |
| `seasonal-arbitrage-trap` | Sell cheap monsoon, buy expensive dry-season |
| `storage-deficit` | Nepal's ~5 m³/person storage vs China ~664, Norway ~15,100 |
| `peak-water` | Glacio-hydrological window closing ~2040-2070 |

---

## Data quality conventions

The wiki uses standardized citation flags. When you see these in page text, treat them accordingly:

| Flag | Meaning |
|---|---|
| `VERIFIED` | Confirmed from primary source (annual report, regulatory filing, rating agency) |
| `[UNVERIFIED: ...]` | Claim from secondary source or preliminary research — not independently confirmed |
| `[PARTIALLY VERIFIED: ...]` | Partially confirmed — e.g., a range rather than single figure, or a lobbying statement rather than actuarial data |
| `[REQUIRES EXACT CITATION: ...]` | Data is correct but the specific document section/page number needs to be located |
| `[UNDER REVIEW: ...]` | Figure is known to require contextualization — e.g., a seasonal extreme presented as an annual average |
| `[Under research — ...]` | Section is known to the wiki but data is not yet available |

Pages marked `[UNVERIFIED]` or `[UNDER REVIEW]` should not be treated as settled fact. Always trace the source before citing.

---

## When the wiki doesn't have an answer

Common gaps to be aware of:
- **PPA rates for most projects** — only ~9 projects have verified rates in the comparison table
- **NLDC dispatch logs** — not public; no primary source for discrimination claims
- **AD penalty aggregate data** — NEA does not publish total penalties collected
- **IPO use-of-funds** — blocked by SEBON's non-machine-readable PDF filing system
- **Insurance claim settlement data** — no named cases with documented timelines

These gaps are themselves findings — the absence of public data is a structural transparency problem documented across the wiki.
