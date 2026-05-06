#!/usr/bin/env python3
"""MCP server exposing the Nepal Energy Wiki as tools for AI agents.

Trust model: This is a read-only public-data server with no authentication by design.
- All 10 tools are read-only (no write/delete/modify operations).
- Stdio transport only — the server is accessible only to local processes
  with filesystem access to this repo. It is NOT a network service.
- Input slugs are validated through pre-built dictionary lookups (no
  filesystem path traversal possible).
- No secrets, API keys, credentials, or environment variable reads.
- All wiki content served is already public at transparentgov.ai.
- Rate limiting is not implemented (unnecessary for single-process stdio).
- No audit trail or request logging exists.

If you add draft/private wiki pages, gate them behind a "public" field in
the page index to avoid accidental exposure through these tools.
"""

from __future__ import annotations

# ---------------------------------------------------------------------------
# Trust domain: read-only local server, no auth.
# ---------------------------------------------------------------------------
TRUST_DOMAIN = "public-read-only"  # all wiki content is public by design

import json
import math
import re
from pathlib import Path

from mcp.server.fastmcp import FastMCP

# ---------------------------------------------------------------------------
# Paths — repo root is two levels up from this script
# ---------------------------------------------------------------------------
ROOT = Path(__file__).resolve().parents[1]
SHARED = ROOT / "wiki" / "explorer" / "shared"
PAGES = ROOT / "wiki" / "pages"

# ---------------------------------------------------------------------------
# MCP server
# ---------------------------------------------------------------------------
mcp = FastMCP(
    "Nepal Energy Wiki",
    instructions="Search and explore the Nepal hydropower accountability wiki with 319 pages across entities, concepts, claims, data, sources, and syntheses. Use wiki_search() to find pages, wiki_get_page() to read them, and wiki_get_backlinks() to navigate the link graph.",
)

# ---------------------------------------------------------------------------
# Load static indices once at startup
# ---------------------------------------------------------------------------
def _load_json(name: str) -> dict | list:
    path = SHARED / f"{name}.json"
    if not path.exists():
        raise FileNotFoundError(f"Index file not found: {path}")
    return json.loads(path.read_text())


_page_index = _load_json("wiki-page-index")
_page_meta = _load_json("wiki-page-meta")
_search_index = _load_json("wiki-search-index")
_fact_index = _load_json("wiki-fact-index")
_backlinks = _load_json("wiki-backlinks")

# Build fast lookups
_pages_by_slug: dict[str, dict] = {}
for p in _page_meta["pages"]:
    _pages_by_slug[p["slug"]] = p

_all_slugs: set[str] = set(_page_index["slugToCategory"].keys())
_categories = list(_page_index["byCategory"].keys())

# BM25 search structures
_pages_array = _search_index["pages"]  # [{'s': slug, 't': title, ...}, ...]
_doc_len: list[int] = _search_index["doc_len"]  # indexed by page position
_doc_freq: dict[str, int] = _search_index["doc_freq"]
_postings: dict[str, list[list[int]]] = _search_index["postings"]  # {term: [[page_idx, tf], ...]}
_total_docs = len(_pages_array)
_avgdl = sum(_doc_len) / max(_total_docs, 1)

# Map page index → slug
_idx_to_slug: dict[int, str] = {}
_slug_to_idx: dict[str, int] = {}
for i, p in enumerate(_pages_array):
    slug = p["s"]
    _idx_to_slug[i] = slug
    _slug_to_idx[slug] = i


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _tokenize(text: str) -> list[str]:
    return re.findall(r"[a-z0-9\u0900-\u097F]+", text.lower())


def _bm25_search(query: str, top_k: int = 10) -> list[tuple[str, float, str]]:
    """BM25 lexical search. Returns (slug, score, excerpt) tuples."""
    tokens = _tokenize(query)
    if not tokens:
        return []

    k1, b = 1.5, 0.75
    results: dict[int, float] = {}  # page_idx → score

    for term in tokens:
        if term not in _postings:
            continue
        df = _doc_freq.get(term, 0)
        if df == 0:
            continue
        idf = math.log(1 + (_total_docs - df + 0.5) / (df + 0.5))

        for page_idx, tf in _postings[term]:
            dl = _doc_len[page_idx] if page_idx < len(_doc_len) else _avgdl
            score = idf * (tf * (k1 + 1)) / (tf + k1 * (1 - b + b * dl / _avgdl))
            results[page_idx] = results.get(page_idx, 0.0) + score

    ranked = sorted(results.items(), key=lambda x: x[1], reverse=True)[:top_k]
    out = []
    for page_idx, score in ranked:
        slug = _idx_to_slug.get(page_idx)
        if not slug:
            continue
        page = _pages_by_slug.get(slug, {})
        excerpt = page.get("excerpt", "")[:200]
        out.append((slug, round(score, 4), excerpt))
    return out


def _load_page_body(slug: str) -> str | None:
    """Load the raw Markdown body of a page by slug."""
    cat = _page_index["slugToCategory"].get(slug)
    if not cat:
        return None
    path = PAGES / cat / f"{slug}.md"
    if not path.exists():
        return None
    text = path.read_text()
    # Strip YAML frontmatter
    if text.startswith("---"):
        parts = text.split("---", 2)
        if len(parts) >= 3:
            return parts[2].strip()
    return text.strip()


# ---------------------------------------------------------------------------
# Tools — Search
# ---------------------------------------------------------------------------
@mcp.tool()
def wiki_search(query: str, top_k: int = 10) -> str:
    """BM25 lexical search across all 319 wiki pages.

    Args:
        query: Search terms, e.g. "Chilime PPA rate", "AD penalties", "Q-design".
        top_k: Number of results (default 10).

    Returns a ranked list of (slug, score, excerpt) tuples.
    """
    results = _bm25_search(query, top_k)
    if not results:
        return "No results found."

    lines = [f"Search: \"{query}\" — {len(results)} results:"]
    for slug, score, excerpt in results:
        title = _page_index["slugToTitle"].get(slug, slug)
        cat = _page_index["slugToCategory"].get(slug, "?")
        lines.append(f"  [{score}] {title} ({cat}/{slug})")
        if excerpt:
            lines.append(f"    {excerpt}")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Tools — Page retrieval
# ---------------------------------------------------------------------------
@mcp.tool()
def wiki_get_page(slug: str) -> str:
    """Get the full metadata and Markdown body of a wiki page.

    Args:
        slug: Page slug, e.g. "nea-triple-authority", "chilime", "q-design-discharge".

    Returns the page title, category, tags, excerpt, and full body text.
    """
    page = _pages_by_slug.get(slug)
    if not page:
        close = [s for s in _all_slugs if slug.lower() in s.lower()][:5]
        hint = f"  Did you mean: {', '.join(close)}" if close else ""
        return f"Page '{slug}' not found.{hint}"

    body = _load_page_body(slug) or ""
    # Truncate very long pages
    if len(body) > 8000:
        body = body[:8000] + "\n\n[... page truncated at 8000 chars ...]"

    lines = [
        f"# {page['title']}",
        f"Category: {page['category']}",
        f"Type: {page.get('type', '')}",
        f"Tags: {', '.join(page.get('tags', []))}",
    ]
    if page.get("excerpt"):
        lines.append(f"Excerpt: {page['excerpt']}")
    lines.append("")
    lines.append(body)

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Tools — Entity lookups
# ---------------------------------------------------------------------------
@mcp.tool()
def wiki_get_entity(slug: str) -> str:
    """Get an entity (project, institution, basin) page — specs, narrative, and map data.

    Args:
        slug: Entity slug, e.g. "sahas-urja", "upper-tamakoshi", "chameliya-hydropower".
    """
    page = _pages_by_slug.get(slug)
    if not page or page.get("category") != "entities":
        return f"Entity '{slug}' not found."

    body = _load_page_body(slug) or ""
    if len(body) > 8000:
        body = body[:8000] + "\n\n[... truncated at 8000 chars ...]"

    # Extract spec tables
    spec_lines = []
    in_table = False
    for line in body.split("\n"):
        if line.startswith("|") and "|" in line[1:]:
            in_table = True
            spec_lines.append(line)
        elif in_table and not line.startswith("|"):
            break

    lines = [
        f"# {page['title']}",
        f"Tags: {', '.join(page.get('tags', []))}",
    ]
    if spec_lines:
        lines.append("")
        lines.append("## Specifications")
        lines.extend(spec_lines)
    lines.append("")
    lines.append(body)

    return "\n".join(lines)


@mcp.tool()
def wiki_get_concept(slug: str) -> str:
    """Get a concept page — analytical framework, mechanism, or argument.

    Args:
        slug: Concept slug, e.g. "nea-triple-authority", "ppa-pricing", "ad-penalties".
    """
    page = _pages_by_slug.get(slug)
    if not page or page.get("category") != "concepts":
        return f"Concept '{slug}' not found."

    body = _load_page_body(slug) or ""
    if len(body) > 8000:
        body = body[:8000] + "\n\n[... truncated at 8000 chars ...]"

    lines = [
        f"# {page['title']}",
        f"Tags: {', '.join(page.get('tags', []))}",
        f"Excerpt: {page.get('excerpt', '')}",
        "",
        body,
    ]
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Tools — Graph navigation
# ---------------------------------------------------------------------------
@mcp.tool()
def wiki_get_backlinks(slug: str, top_k: int = 20) -> str:
    """Get pages that link to a given page (reverse wikilink graph).

    Args:
        slug: Target page slug.
        top_k: Maximum number of referring pages to show.

    Returns a list of pages, each with the link context.
    """
    bl = _backlinks["backlinks"].get(slug, [])
    if not bl:
        return f"No pages link to '{slug}'."

    lines = [f"Pages linking to '{slug}' ({len(bl)} total, showing {min(len(bl), top_k)}):"]
    for ref in bl[:top_k]:
        title = ref.get("title", ref["slug"])
        cat = ref.get("category", "?")
        ctx = ref.get("context", "")[:120].strip()
        lines.append(f"  - [[{title}]] ({cat}/{ref['slug']})")
        if ctx:
            lines.append(f"    \"...{ctx}...\"")
    return "\n".join(lines)


@mcp.tool()
def wiki_get_wikilinks(slug: str) -> str:
    """Extract all [[wikilinks]] referenced in a page's body.

    Args:
        slug: Page slug.

    Returns categorized list of links — which exist as pages and which are broken.
    """
    body = _load_page_body(slug)
    if body is None:
        return f"Page '{slug}' not found."

    links = re.findall(r"\[\[([^\]|#]+)(?:[|#][^\]]+)?\]\]", body)
    if not links:
        return f"No wikilinks found in '{slug}'."

    existing = []
    broken = []
    for link in sorted(set(links)):
        link = link.strip().lower().replace(" ", "-")
        if link in _all_slugs:
            title = _page_index["slugToTitle"].get(link, link)
            existing.append(f"  - [[{title}]] ({link})")
        else:
            broken.append(f"  - [[{link}]] (not found)")

    lines = [f"Wikilinks in '{slug}':"]
    if existing:
        lines.append(f"  Valid ({len(existing)}):")
        lines.extend(existing)
    if broken:
        lines.append(f"  Broken ({len(broken)}):")
        lines.extend(broken)
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Tools — Structured facts
# ---------------------------------------------------------------------------
@mcp.tool()
def wiki_get_facts(limit: int = 50) -> str:
    """Get structured facts about hydropower projects (capacity, status, basin, etc.).

    Args:
        limit: Maximum number of facts to return.

    Returns a table of project facts extracted from map data.
    """
    facts = _fact_index["facts"][:limit]
    if not facts:
        return "No facts available."

    # Find common keys
    keys = set()
    for f in facts:
        keys.update(k for k in f if k not in ("id", "layer", "source_file"))
    keys = sorted(keys)

    lines = [f"Structured Facts ({len(facts)} of {_fact_index['stats'].get('total', '?')} total):", ""]
    for fact in facts:
        name = fact.get("project", fact.get("name", fact.get("id", "?")))
        capacity = fact.get("capacity_mw", fact.get("capacity", "?"))
        status = fact.get("license_type", fact.get("status", "?"))
        river = fact.get("river", "?")
        lines.append(f"  {name} | {capacity} MW | {status} | {river}")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Tools — Navigation / Discovery
# ---------------------------------------------------------------------------
@mcp.tool()
def wiki_list_pages(category: str | None = None, limit: int = 50) -> str:
    """List wiki pages by category.

    Args:
        category: One of: entities, concepts, claims, data, sources, syntheses.
                  If omitted, lists all categories with page counts.
        limit: Maximum pages to list per category.

    Returns a list of page slugs with titles, or a category overview.
    """
    if category is None:
        lines = ["Wiki categories:"]
        for cat in sorted(_categories):
            slugs = _page_index["byCategory"].get(cat, [])
            lines.append(f"  {cat}: {len(slugs)} pages")
        lines.append(f"  Total: {_page_index['totalPages']} pages")
        return "\n".join(lines)

    cat_slugs = _page_index["byCategory"].get(category)
    if cat_slugs is None:
        return f"Unknown category '{category}'. Valid: {', '.join(_categories)}"

    lines = [f"{category} ({len(cat_slugs)} pages, showing {min(len(cat_slugs), limit)}):"]
    for slug in sorted(cat_slugs)[:limit]:
        title = _page_index["slugToTitle"].get(slug, slug)
        lines.append(f"  - {title} ({slug})")
    return "\n".join(lines)


@mcp.tool()
def wiki_get_all_entities() -> str:
    """List all entity pages with key specifications from structured facts.

    Returns a compact table of all entities with capacity, status, and river data
    where available from the fact index.
    """
    # Build a fact lookup by project name
    fact_map: dict[str, dict] = {}
    for fact in _fact_index["facts"]:
        name = fact.get("project", "")
        if name:
            fact_map[name.lower()] = fact

    entity_slugs = _page_index["byCategory"].get("entities", [])
    lines = [f"Entities ({len(entity_slugs)} total):", ""]

    for slug in sorted(entity_slugs):
        page = _pages_by_slug.get(slug, {})
        title = page.get("title", slug)
        tags = page.get("tags", [])
        tag_str = ", ".join(tags[:3]) if tags else ""

        # Try to match to a fact
        fact_match = None
        for fact_name, fact in fact_map.items():
            if slug.lower() in fact_name or fact_name in slug.lower():
                fact_match = fact
                break

        if fact_match:
            cap = fact_match.get("capacity_mw", "?")
            status = fact_match.get("license_type", "?")
            lines.append(f"  {title} | {cap} MW | {status} | {tag_str}")
        else:
            lines.append(f"  {title} | ? MW | ? | {tag_str}")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    mcp.run()
