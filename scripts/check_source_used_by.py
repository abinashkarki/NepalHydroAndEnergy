#!/usr/bin/env python3
"""Validate source-page Used By sections against exact wiki backlinks."""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
PAGES = ROOT / "wiki" / "pages"
SOURCES = PAGES / "sources"
USED_BY_RE = re.compile(r"^## Used By\n(?P<body>.*?)(?=^## |\Z)", re.S | re.M)
WIKILINK_RE = re.compile(r"\[\[([^\]|#]+)")


def listed_used_by(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8")
    match = USED_BY_RE.search(text)
    if not match:
        return []
    return sorted(set(WIKILINK_RE.findall(match.group("body"))))


def actual_backlinks(path: Path, all_pages: list[Path]) -> list[str]:
    slug = path.stem
    needle = f"[[{slug}"
    backlinks: list[str] = []
    for page in all_pages:
        if page == path:
            continue
        text = page.read_text(encoding="utf-8")
        text = USED_BY_RE.sub("", text)
        if needle in text:
            backlinks.append(page.stem)
    return sorted(set(backlinks))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--sources-dir",
        type=Path,
        default=SOURCES,
        help="Directory containing source markdown pages.",
    )
    args = parser.parse_args(argv)

    source_dir = args.sources_dir if args.sources_dir.is_absolute() else ROOT / args.sources_dir
    all_pages = sorted(PAGES.rglob("*.md"))
    errors: list[tuple[str, list[str], list[str]]] = []

    for path in sorted(source_dir.glob("*.md")):
        listed = listed_used_by(path)
        actual = actual_backlinks(path, all_pages)
        if listed != actual:
            errors.append((path.relative_to(ROOT).as_posix(), listed, actual))

    if not errors:
        print(f"OK: {len(list(source_dir.glob('*.md')))} source Used By sections match exact backlinks")
        return 0

    print(f"ERROR: {len(errors)} source Used By mismatch(es)")
    for rel, listed, actual in errors:
        print(rel)
        print(f"  listed: {listed}")
        print(f"  actual: {actual}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
