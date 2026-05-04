#!/usr/bin/env python3
"""Build a JSON index of wiki pages so the explorer can resolve slugs without a server-side step.

Output: wiki/explorer/shared/wiki-page-index.json
"""
from __future__ import annotations
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WIKI_PAGES = ROOT / "wiki" / "pages"
OUT = ROOT / "wiki" / "explorer" / "shared" / "wiki-page-index.json"

CATEGORIES = ["sources", "entities", "concepts", "syntheses", "claims", "data", "interventions"]

TITLE_RE = re.compile(r"^title:\s*(.+?)\s*$", re.MULTILINE)


def extract_title(md_path: Path) -> str | None:
    text = md_path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return None
    end = text.find("\n---", 4)
    if end == -1:
        return None
    fm = text[4:end]
    m = TITLE_RE.search(fm)
    return m.group(1).strip() if m else None


def main() -> None:
    by_category: dict[str, list[dict]] = {c: [] for c in CATEGORIES}
    all_slugs: list[str] = []
    slug_to_category: dict[str, str] = {}
    slug_to_title: dict[str, str] = {}

    for cat in CATEGORIES:
        d = WIKI_PAGES / cat
        if not d.exists():
            continue
        for md in sorted(d.glob("*.md")):
            slug = md.stem
            title = extract_title(md) or slug
            by_category[cat].append({"slug": slug, "title": title})
            all_slugs.append(slug)
            slug_to_category[slug] = cat
            slug_to_title[slug] = title

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps({
        "byCategory": by_category,
        "allSlugs": all_slugs,
        "slugToCategory": slug_to_category,
        "slugToTitle": slug_to_title,
        "totalPages": len(all_slugs),
    }, indent=2), encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)} ({len(all_slugs)} pages across {sum(1 for v in by_category.values() if v)} categories)")


if __name__ == "__main__":
    main()
