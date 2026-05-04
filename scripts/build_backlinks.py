#!/usr/bin/env python3
"""Build a reverse index of wikilink references.

Scans every ``.md`` file under ``wiki/pages/`` for ``[[slug]]`` and
``[[slug|label]]`` patterns, inverts the graph, and writes
``wiki/explorer/shared/wiki-backlinks.json``:

    {
      "koshi-basin": [
        {
          "slug": "upper-tamakoshi",
          "title": "Upper Tamakoshi",
          "category": "entities",
          "context": "...on the Tama Koshi River in eastern [[koshi-basin]]..."
        },
        ...
      ],
      ...
    }

``context`` is a ~120-character window around the link, with the link
itself stripped of brackets, so the reader can show a readable snippet.

Run order:  ``build_wiki_page_index.py`` (needed for slug→title) →
``build_backlinks.py``.
"""
from __future__ import annotations
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WIKI_PAGES = ROOT / "wiki" / "pages"
INDEX_PATH = ROOT / "wiki" / "explorer" / "shared" / "wiki-page-index.json"
OUT = ROOT / "wiki" / "explorer" / "shared" / "wiki-backlinks.json"

CATEGORIES = ["sources", "entities", "concepts", "syntheses", "claims", "data", "interventions"]

WIKILINK_RE = re.compile(r"\[\[([^\]|]+)(?:\|([^\]]+))?\]\]")
CONTEXT_WINDOW = 60  # chars on each side

# Strip fenced code blocks and inline code spans before scanning so
# wikilink-like syntax inside code samples (e.g. ``[[slug]]`` in the
# roadmap page) doesn't pollute the graph.
FENCED_RE = re.compile(r"```.*?```", re.DOTALL)
INLINE_CODE_RE = re.compile(r"`[^`\n]+`")


def strip_code(text: str) -> str:
    """Replace code regions with spaces of equal length so offsets are
    preserved. Preserving offsets isn't strictly required for backlink
    aggregation, but it makes context snippets line up correctly with
    the surrounding prose."""
    def blank(m: re.Match[str]) -> str:
        return " " * (m.end() - m.start())

    text = FENCED_RE.sub(blank, text)
    text = INLINE_CODE_RE.sub(blank, text)
    return text


def load_index() -> dict:
    if not INDEX_PATH.exists():
        raise SystemExit(
            f"missing {INDEX_PATH}; run build_wiki_page_index.py first"
        )
    return json.loads(INDEX_PATH.read_text(encoding="utf-8"))


def strip_frontmatter(text: str) -> str:
    if not text.startswith("---"):
        return text
    end = text.find("\n---", 4)
    if end == -1:
        return text
    return text[end + 4 :]


def make_context(body: str, match: re.Match[str]) -> str:
    """Return a short readable snippet around ``match``, with the
    wikilink's brackets replaced by its display label so the snippet
    reads like sentence text, not markup."""
    start, end = match.span()
    display = (match.group(2) or match.group(1)).strip()
    left = max(0, start - CONTEXT_WINDOW)
    right = min(len(body), end + CONTEXT_WINDOW)
    snippet = body[left:start] + display + body[end:right]
    snippet = re.sub(r"\s+", " ", snippet).strip()
    if left > 0:
        snippet = "\u2026" + snippet
    if right < len(body):
        snippet = snippet + "\u2026"
    return snippet


def main() -> None:
    idx = load_index()
    slug_to_cat = idx.get("slugToCategory", {})
    slug_to_title = idx.get("slugToTitle", {})
    # backlinks[target_slug] -> list of {slug, title, category, context}
    backlinks: dict[str, list[dict]] = {}

    for cat in CATEGORIES:
        d = WIKI_PAGES / cat
        if not d.exists():
            continue
        for md in sorted(d.glob("*.md")):
            src_slug = md.stem
            src_title = slug_to_title.get(src_slug, src_slug)
            raw = md.read_text(encoding="utf-8")
            body = strip_code(strip_frontmatter(raw))
            seen_in_this_page: set[str] = set()
            for m in WIKILINK_RE.finditer(body):
                target = m.group(1).strip()
                if target == src_slug:
                    continue
                # Only record the first occurrence per (source, target)
                # pair so a page that references X three times doesn't
                # flood X's backlinks list.
                if target in seen_in_this_page:
                    continue
                seen_in_this_page.add(target)
                backlinks.setdefault(target, []).append(
                    {
                        "slug": src_slug,
                        "title": src_title,
                        "category": cat,
                        "context": make_context(body, m),
                        "target_exists": target in slug_to_cat,
                    }
                )

    # Sort each list: category order (entities before concepts, etc.),
    # then title alphabetical, for stable rendering.
    cat_rank = {c: i for i, c in enumerate(CATEGORIES)}
    for target, refs in backlinks.items():
        refs.sort(
            key=lambda r: (cat_rank.get(r["category"], 99), r["title"].lower())
        )

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(
        json.dumps(
            {
                "generated": "auto",
                "total_targets": len(backlinks),
                "total_refs": sum(len(v) for v in backlinks.values()),
                "backlinks": backlinks,
            },
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    # Friendly summary for humans
    total_refs = sum(len(v) for v in backlinks.values())
    broken_refs = sum(
        1 for refs in backlinks.values() for r in refs if not r["target_exists"]
    )
    print(
        f"wrote {OUT.relative_to(ROOT)} — "
        f"{len(backlinks)} target pages, {total_refs} references"
        + (f" ({broken_refs} to non-existent slugs)" if broken_refs else "")
    )

    # Top-10 most-referenced slugs (as a readable signal).
    top = sorted(backlinks.items(), key=lambda kv: -len(kv[1]))[:10]
    if top:
        print("most referenced:")
        for slug, refs in top:
            marker = "" if slug in slug_to_cat else "  [no page]"
            print(f"  {len(refs):3d}  {slug}{marker}")


if __name__ == "__main__":
    main()
