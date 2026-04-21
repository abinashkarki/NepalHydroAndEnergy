#!/usr/bin/env python3
"""Global pass: drop inline figures whose caption is visual noise.

A caption is "junk" if it matches any of:
  - empty / "[no caption]"
  - starts with boilerplate ("PDF image from page", "NEA annual-book image",
    "Source:", "Annex N;", "Project on Integrated Power System")
  - sentence fragment (starts with a lowercase letter or a bare preposition)
  - trailing punctuation that indicates truncation (ends with ",", "-", ":",
    "(", " at", " in", etc.)
  - very short and non-descriptive (< 20 chars AND no digit/colon)
  - pure parenthesised fragment like "(Dana - Kushma - New Butwal)."

A caption is "good" (kept unconditionally) if:
  - starts with "Figure N.N-N" / "Table N.N-N" (JICA / NEA annual-report figure
    titles)
  - OR is >= 20 chars, starts with a capital letter, and does not match any
    drop pattern

Run with --dry-run first to see the plan; rerun without --dry-run to apply.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))

from pdf_atlas_lib import SOURCES, ASSETS_DIR, ROOT  # noqa: E402
from extract_pdf_images import (  # noqa: E402
    remove_frontmatter_image,
    remove_inline_figure,
    remove_provenance_entry,
    remove_source_slug_if_unused,
)


PREFIX_TO_SOURCE: dict[str, dict[str, str]] = {
    source["asset_prefix"]: {"slug": source["wiki_source_slug"], "prov": source["provenance_filename"]}
    for source in SOURCES.values()
}

INLINE_FIGURE_RE = re.compile(
    r'<figure class="wiki-inline-figure">\s*<img src="\.\./assets/images/([^"]+)" alt="[^"]*">\s*<figcaption>([^<]*)</figcaption>\s*</figure>',
    re.DOTALL,
)

FRONTMATTER_IMAGE_RE = re.compile(
    r"^\s{2}- src:\s*(?P<src>\S+)\s*\n(?:^\s{4}.*\n)*",
    re.MULTILINE,
)

FRONTMATTER_IMAGE_CAPTION_RE = re.compile(
    r"^\s{4}caption:\s*\"?(?P<caption>[^\"\n]+)\"?\s*$",
    re.MULTILINE,
)

FIGURE_TITLE_RE = re.compile(r"^(Figure|Table)\s+\d+(?:\.\d+)*-\d+\b")
BOILERPLATE_PREFIXES = (
    "pdf image from page",
    "nea annual-book image",
    "source:",
    "annex ",
    "project on integrated power system",
    "final report",
)
TRAILING_TRUNCATION_RE = re.compile(r"[,\-:(\s][a-z]{0,3}$")


def is_junk_caption(raw: str) -> tuple[bool, str]:
    caption = (raw or "").strip()
    if not caption:
        return True, "empty"
    if caption.lower() == "[no caption]":
        return True, "no-caption-marker"
    lowered = caption.lower()
    for prefix in BOILERPLATE_PREFIXES:
        if lowered.startswith(prefix):
            return True, f"boilerplate:{prefix.rstrip(':')}"
    if FIGURE_TITLE_RE.match(caption):
        return False, "figure-title"
    first_char = caption[0]
    if not first_char.isupper() and not first_char.isdigit() and first_char not in "([":
        return True, "fragment:lowercase-start"
    if len(caption) < 20 and not any(ch.isdigit() for ch in caption):
        return True, "too-short-non-numeric"
    if re.fullmatch(r"\(.*\)\.?", caption):
        return True, "parenthesised-fragment"
    last_char = caption.rstrip()[-1]
    if last_char in ",-:(" or caption.rstrip().endswith(" of") or caption.rstrip().endswith(" the"):
        return True, "trailing-truncation"
    # Detect captions dominated by single-letter word groups (OCR garble).
    # Only count single-letter ALPHA tokens (digits like "2", "3" are fine).
    words = caption.split()
    alpha_singletons = sum(1 for w in words if len(w) == 1 and w.isalpha())
    if len(words) >= 5 and alpha_singletons / len(words) >= 0.4:
        return True, "ocr-garble"
    if len(caption) < 12:
        return True, "generic-too-short"
    if TRAILING_TRUNCATION_RE.search(caption) and not FIGURE_TITLE_RE.match(caption):
        return True, "mid-sentence-truncation"
    return False, "ok"


def asset_prefix_from_src(src: str) -> str | None:
    name = Path(src).name
    match = re.match(r"([a-z0-9]+)-p\d", name)
    return match.group(1) if match else None


def purge_inline_figure_from_page(page_text: str, src: str, prov_slug: str, asset_prefix: str) -> tuple[str, list[Path]]:
    updated = remove_inline_figure(page_text, src)
    updated = remove_frontmatter_image(updated, src)
    meta = PREFIX_TO_SOURCE.get(asset_prefix)
    asset_paths_to_delete: list[Path] = []
    if meta:
        updated = remove_source_slug_if_unused(updated, meta["slug"], asset_prefix)
        slug_dir = ASSETS_DIR / prov_slug
        prov_path = slug_dir / meta["prov"]
        if prov_path.exists():
            try:
                prov_data = json.loads(prov_path.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                prov_data = None
            updated_prov = remove_provenance_entry(prov_data, src, prov_slug) if prov_data else None
            if updated_prov is None and prov_path.exists():
                asset_paths_to_delete.append(prov_path)
            elif updated_prov is not None:
                prov_path.write_text(json.dumps(updated_prov, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return updated, asset_paths_to_delete


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    pages = sorted(Path("wiki/pages").glob("*/*.md"))
    drop_report: list[dict[str, Any]] = []
    assets_to_delete: list[Path] = []
    pages_touched = 0

    for page_path in pages:
        text = page_path.read_text(encoding="utf-8")
        matches = list(INLINE_FIGURE_RE.finditer(text))
        if not matches:
            continue
        junk_srcs: list[tuple[str, str, str]] = []  # (src, caption, reason)
        for match in matches:
            src = match.group(1)
            caption = match.group(2).strip()
            drop, reason = is_junk_caption(caption)
            if drop:
                junk_srcs.append((src, caption, reason))

        if not junk_srcs:
            continue

        new_text = text
        for src, caption, reason in junk_srcs:
            prov_slug = src.split("/", 1)[0]
            prefix = asset_prefix_from_src(src) or ""
            new_text, extras = purge_inline_figure_from_page(new_text, src, prov_slug, prefix)
            asset_abs = ASSETS_DIR / src
            if asset_abs.exists():
                extras.append(asset_abs)
            assets_to_delete.extend(extras)
            drop_report.append(
                {
                    "page": str(page_path.relative_to("wiki/pages")),
                    "src": src,
                    "caption": caption,
                    "reason": reason,
                }
            )

        if new_text != text:
            pages_touched += 1
            if not args.dry_run:
                page_path.write_text(new_text, encoding="utf-8")

    if not args.dry_run:
        for asset in assets_to_delete:
            try:
                asset.unlink()
            except FileNotFoundError:
                pass
            parent = asset.parent
            if parent.exists() and not any(parent.iterdir()):
                parent.rmdir()

    from collections import Counter

    reason_counts = Counter(item["reason"] for item in drop_report)
    print(f"pages_touched={pages_touched}")
    print(f"inline_figures_dropped={len(drop_report)}")
    print(f"reason_counts={dict(reason_counts)}")
    print(f"assets_queued_for_delete={len(assets_to_delete)}")
    print()
    print("Sample drops:")
    for item in drop_report[:30]:
        cap = item["caption"][:60] + ("…" if len(item["caption"]) > 60 else "")
        print(f"  {item['page']:55}  reason={item['reason']:30}  \"{cap}\"")


if __name__ == "__main__":
    main()
