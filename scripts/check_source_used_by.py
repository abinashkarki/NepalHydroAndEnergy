#!/usr/bin/env python3
"""Validate that source-page Used By sections are computed, not manual.

Source pages used to carry hand-maintained ``## Used By`` sections. Those
sections drifted because the real authority is the wikilink graph. The explorer
now renders source-page Used By lists from ``wiki-backlinks.json``; markdown
source pages should not carry unmanaged Used By prose.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
PAGES = ROOT / "wiki" / "pages"
SOURCES = PAGES / "sources"
USED_BY_RE = re.compile(r"^## Used By\n(?P<body>.*?)(?=^## |\Z)", re.S | re.M)


def has_manual_used_by(path: Path) -> bool:
    text = path.read_text(encoding="utf-8")
    return USED_BY_RE.search(text) is not None


def main(argv: list[str] | None = None) -> int:
    if argv:
        print("ERROR: this checker no longer accepts arguments", file=sys.stderr)
        return 2

    errors = [path.relative_to(ROOT).as_posix() for path in sorted(SOURCES.glob("*.md")) if has_manual_used_by(path)]

    if not errors:
        print(f"OK: {len(list(SOURCES.glob('*.md')))} source pages have no manual Used By sections")
        return 0

    print(f"ERROR: {len(errors)} source page(s) contain manual ## Used By sections")
    for rel in errors:
        print(f"  {rel}")
    print("Used By is rendered from wiki/explorer/shared/wiki-backlinks.json; remove manual sections.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
