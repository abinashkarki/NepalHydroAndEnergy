#!/usr/bin/env python3
"""Lightweight repository validation for portfolio-facing hygiene."""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WIKI_PAGES = ROOT / "wiki" / "pages"
INDEX = ROOT / "wiki" / "explorer" / "shared" / "wiki-page-index.json"
BACKLINKS = ROOT / "wiki" / "explorer" / "shared" / "wiki-backlinks.json"
MANIFEST = ROOT / "wiki" / "explorer" / "shared" / "layer-manifest.json"

WIKILINK_RE = re.compile(r"\[\[([^\]|]+)(?:\|[^\]]+)?\]\]")
FENCED_RE = re.compile(r"```.*?```", re.DOTALL)
INLINE_CODE_RE = re.compile(r"`[^`\n]+`")
PAGE_CATEGORIES = ["sources", "entities", "concepts", "syntheses", "claims", "data"]
FORBIDDEN_TRACKED_PREFIXES = (
    ".playwright-cli/",
    "output/playwright/",
    "tmp/",
    "wiki/explorer/shots/",
)
FORBIDDEN_TRACKED_SUFFIXES = (
    ".DS_Store",
    ".404-stub.bak",
)


def fail(message: str) -> None:
    print(f"FAIL: {message}", file=sys.stderr)
    raise SystemExit(1)


def load_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001
        fail(f"{path.relative_to(ROOT)} is not valid JSON: {exc}")


def strip_ignored_markdown(text: str) -> str:
    text = FENCED_RE.sub(" ", text)
    return INLINE_CODE_RE.sub(" ", text)


def wiki_page_slugs() -> set[str]:
    slugs: set[str] = set()
    for category in PAGE_CATEGORIES:
        for page in (WIKI_PAGES / category).glob("*.md"):
            slugs.add(page.stem)
    return slugs


def validate_wiki_links(slugs: set[str]) -> None:
    broken: list[str] = []
    for category in PAGE_CATEGORIES:
        for page in sorted((WIKI_PAGES / category).glob("*.md")):
            text = strip_ignored_markdown(page.read_text(encoding="utf-8"))
            for match in WIKILINK_RE.finditer(text):
                target = match.group(1).strip()
                if target not in slugs:
                    broken.append(f"{page.relative_to(ROOT)} -> [[{target}]]")
    if broken:
        fail("broken wikilinks:\n" + "\n".join(broken[:50]))


def validate_caches(slugs: set[str]) -> None:
    index = load_json(INDEX)
    if index.get("totalPages") != len(slugs):
        fail(f"wiki-page-index totalPages={index.get('totalPages')} but found {len(slugs)} pages")

    backlinks = load_json(BACKLINKS).get("backlinks", {})
    broken_refs = [
        f"{target} <- {ref.get('slug')}"
        for target, refs in backlinks.items()
        for ref in refs
        if not ref.get("target_exists", False)
    ]
    if broken_refs:
        fail("cached backlinks contain broken refs:\n" + "\n".join(broken_refs[:50]))


def validate_map_manifest() -> None:
    manifest = load_json(MANIFEST)
    layers = manifest.get("layers", {})
    for layer_id, layer in layers.items():
        rel = layer.get("path")
        if not rel or not rel.startswith("../../../"):
            continue
        target = ROOT / rel.replace("../../../", "")
        if not target.exists():
            fail(f"manifest layer {layer_id} points to missing file {target.relative_to(ROOT)}")
        if target.suffix in {".json", ".geojson"}:
            load_json(target)


def validate_tracked_hygiene() -> None:
    tracked = subprocess.check_output(["git", "ls-files"], cwd=ROOT, text=True).splitlines()
    offenders = [
        path
        for path in tracked
        if path.startswith(FORBIDDEN_TRACKED_PREFIXES) or path.endswith(FORBIDDEN_TRACKED_SUFFIXES)
    ]
    if offenders:
        fail("tracked generated/clutter files:\n" + "\n".join(offenders[:50]))


def main() -> None:
    slugs = wiki_page_slugs()
    validate_wiki_links(slugs)
    validate_caches(slugs)
    validate_map_manifest()
    validate_tracked_hygiene()
    print(f"OK: {len(slugs)} wiki pages, caches valid, map manifest valid, tracked hygiene clean")


if __name__ == "__main__":
    main()
