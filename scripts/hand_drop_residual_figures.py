#!/usr/bin/env python3
"""Final hand-curated pass.

After the rule-based cleanup, a handful of inline-figure captions remain
that are still clearly fragments or body-text leakage. This script drops
them by explicit caption match on each page.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from pdf_atlas_lib import ASSETS_DIR, SOURCES  # noqa: E402
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


HAND_DROPS = [
    ("entities/marsyangdi.md", "Project fiscal year."),
    ("entities/trishuli.md", "2021. stage of manufacturing completion."),
    ("entities/trishuli.md", "Organization at Bardibas, Mahottari."),
    ("entities/trishuli.md", "Participants of Driving Training and House"),
    ("entities/chilime.md", "Structures during the flood in headworks, area."),
    ("entities/chilime.md", "Participants of Five Days Agriculture Training at Rasuwa"),
    ("entities/nea.md", "May 1911 (B.S. 1968, 9th Jestha)."),
    ("entities/dudhkoshi-storage.md", "Hydroelectric Project"),
    ("entities/dudhkoshi-storage.md", "Public Hearing of EIA Report at Rabuwa"),
]


INLINE_FIGURE_RE = re.compile(
    r'<figure class="wiki-inline-figure">\s*<img src="\.\./assets/images/([^"]+)" alt="[^"]*">\s*<figcaption>([^<]*)</figcaption>\s*</figure>',
    re.DOTALL,
)


def asset_prefix_from_src(src: str) -> str | None:
    match = re.match(r"([a-z0-9]+)-p\d", Path(src).name)
    return match.group(1) if match else None


def main() -> None:
    dropped = 0
    assets_removed = 0
    for rel_path, target_caption in HAND_DROPS:
        page_path = Path("wiki/pages") / rel_path
        if not page_path.exists():
            print(f"  skip: {rel_path} not found")
            continue
        text = page_path.read_text(encoding="utf-8")
        src_to_drop: str | None = None
        for match in INLINE_FIGURE_RE.finditer(text):
            if match.group(2).strip() == target_caption:
                src_to_drop = match.group(1)
                break
        if not src_to_drop:
            print(f"  skip: caption not found on {rel_path}: {target_caption!r}")
            continue
        prov_slug = src_to_drop.split("/", 1)[0]
        prefix = asset_prefix_from_src(src_to_drop) or ""
        updated = remove_inline_figure(text, src_to_drop)
        updated = remove_frontmatter_image(updated, src_to_drop)
        meta = PREFIX_TO_SOURCE.get(prefix)
        if meta:
            updated = remove_source_slug_if_unused(updated, meta["slug"], prefix)
            prov_path = ASSETS_DIR / prov_slug / meta["prov"]
            if prov_path.exists():
                try:
                    prov_data = json.loads(prov_path.read_text(encoding="utf-8"))
                except json.JSONDecodeError:
                    prov_data = None
                if prov_data:
                    new_prov = remove_provenance_entry(prov_data, src_to_drop, prov_slug)
                    if new_prov is None:
                        prov_path.unlink()
                    else:
                        prov_path.write_text(json.dumps(new_prov, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        page_path.write_text(updated, encoding="utf-8")
        asset_abs = ASSETS_DIR / src_to_drop
        if asset_abs.exists():
            asset_abs.unlink()
            assets_removed += 1
            parent = asset_abs.parent
            if parent.exists() and not any(parent.iterdir()):
                parent.rmdir()
        dropped += 1
        print(f"  dropped: {rel_path}: {target_caption!r}")

    print()
    print(f"dropped={dropped}, assets_removed={assets_removed}")


if __name__ == "__main__":
    main()
