#!/usr/bin/env python3
"""One-shot curator for jica-ipsdp-main-report-vol2 decisions YAML.

Applies three passes in order:

1. BOTTOM-QUARTILE DROP — rows whose atlas top-candidate score is at or
   below Q1 (25th percentile) are flipped to `drop` with note
   `skipped:bottom-quartile-confidence`.
2. CAPTION REHAB — for remaining film/inline/crop rows whose caption is
   boilerplate (page header, bare `Source: X`, empty), try to synthesize
   a better caption by scanning the page text for a `Figure X.Y-Z ...`
   title line. If no replacement is found, continue to step 3.
3. BOILERPLATE DROP — any remaining row whose caption is still
   boilerplate/empty is flipped to `drop` with note
   `skipped:boilerplate-caption`.

The output is the existing decisions YAML rewritten in place. Any row with
an explicit `action: drop` or unrelated action (`new_node`) is left alone
unless it already meets a rule above.
"""
from __future__ import annotations

import json
import re
import statistics
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))

from pdf_atlas_lib import (  # noqa: E402
    dump_decision_rows,
    get_source,
    parse_decisions_text,
    source_abs_path,
)

SOURCE_ID = "jica-ipsdp-main-report-vol2"


BOILERPLATE_PATTERNS = [
    re.compile(r"^\s*$"),
    re.compile(r"^\[no caption\]$", re.IGNORECASE),
    re.compile(r"^\s*Source:\s.*", re.IGNORECASE),
    re.compile(r"^\s*Annex\s+\d+[;:].*", re.IGNORECASE),
    re.compile(r"^\s*Project on Integrated Power System.*"),
    re.compile(r"^\s*Final Report\s*$"),
    re.compile(r"^[^A-Za-z0-9]{0,4}([A-Za-z]\s){5,}.*", re.IGNORECASE),
]

FIGURE_TITLE_RE = re.compile(
    r"(Figure|Table)\s+\d+(?:\.\d+)*-\d+\s+[^\n\r]+",
)


def is_boilerplate(caption: str) -> bool:
    text = (caption or "").strip()
    if not text:
        return True
    for pat in BOILERPLATE_PATTERNS:
        if pat.match(text):
            return True
    if len(text) < 12:
        return True
    return False


def load_atlas_score_map(atlas_path: Path) -> dict[tuple[int, int], tuple[float, str]]:
    atlas = json.loads(atlas_path.read_text(encoding="utf-8"))
    out: dict[tuple[int, int], tuple[float, str]] = {}
    for rec in atlas:
        key = (int(rec["page"]), int(rec["image_index"]))
        cands = rec.get("candidate_slugs") or []
        top_score = float(cands[0]["score"]) if cands else 0.0
        top_slug = cands[0]["slug"] if cands else ""
        out[key] = (top_score, top_slug)
    return out


def load_page_text_map(page_index_path: Path) -> dict[int, str]:
    data = json.loads(page_index_path.read_text(encoding="utf-8"))
    return {int(row["page"]): row.get("text") or "" for row in data}


def best_figure_title_for_page(page_text: str, target_slug: str) -> str:
    if not page_text:
        return ""
    titles: list[str] = [m.group(0).strip() for m in FIGURE_TITLE_RE.finditer(page_text)]
    if not titles:
        return ""

    slug_tokens = {tok.lower() for tok in target_slug.split("-") if len(tok) >= 4}

    def score(title: str) -> tuple[int, int]:
        lower = title.lower()
        slug_hits = sum(1 for tok in slug_tokens if tok in lower)
        return (slug_hits, -len(title))

    titles.sort(key=score, reverse=True)
    best = titles[0]
    return re.sub(r"\s+", " ", best).strip()


def main() -> None:
    source = get_source(SOURCE_ID)
    yaml_path = source_abs_path(source, "decisions_v2_yaml")
    atlas_path = source_abs_path(source, "atlas_json")
    page_index_path = Path("data/processed/corridor_tracing/manifests/jica_ipsdp_main_report_vol2_page_index.json")

    rows = parse_decisions_text(yaml_path.read_text(encoding="utf-8"))
    score_map = load_atlas_score_map(atlas_path)
    text_map = load_page_text_map(page_index_path)

    active = [r for r in rows if r.get("action") in {"filmstrip", "inline_figure", "crop", "new_node"}]
    scores = [score_map.get((int(r["page"]), int(r["image_index"])), (0.0, ""))[0] for r in active]
    q1 = statistics.quantiles(scores, n=4)[0] if len(scores) >= 4 else (min(scores) if scores else 0.0)

    stats = {
        "bottom_quartile_dropped": 0,
        "caption_rehabbed": 0,
        "boilerplate_dropped": 0,
        "kept": 0,
    }

    out_rows: list[dict[str, Any]] = []
    for row in rows:
        page = int(row["page"])
        image_index = int(row["image_index"])
        action = str(row.get("action", ""))
        if action not in {"filmstrip", "inline_figure", "crop", "new_node"}:
            out_rows.append(row)
            continue

        top_score, _top_slug = score_map.get((page, image_index), (0.0, ""))

        if top_score <= q1:
            dropped = dict(row)
            dropped["action"] = "drop"
            dropped["target_slug"] = ""
            dropped["proposed_slug"] = ""
            dropped["paragraph_anchor"] = ""
            dropped["note"] = f"skipped:bottom-quartile-confidence (score={top_score:.2f}, q1={q1:.2f})"
            out_rows.append(dropped)
            stats["bottom_quartile_dropped"] += 1
            continue

        if action in {"filmstrip", "inline_figure", "crop"}:
            caption = str(row.get("caption", ""))
            if is_boilerplate(caption):
                new_caption = best_figure_title_for_page(
                    text_map.get(page, ""), str(row.get("target_slug", ""))
                )
                if new_caption and not is_boilerplate(new_caption):
                    row = dict(row)
                    row["caption"] = new_caption
                    row["note"] = "caption-rehabbed-from-page-text"
                    stats["caption_rehabbed"] += 1
                else:
                    dropped = dict(row)
                    dropped["action"] = "drop"
                    dropped["target_slug"] = ""
                    dropped["proposed_slug"] = ""
                    dropped["paragraph_anchor"] = ""
                    dropped["note"] = "skipped:boilerplate-caption"
                    out_rows.append(dropped)
                    stats["boilerplate_dropped"] += 1
                    continue

        out_rows.append(row)
        stats["kept"] += 1

    yaml_path.write_text(dump_decision_rows(out_rows), encoding="utf-8")
    print(f"wrote={yaml_path}")
    print(f"q1_threshold_score={q1:.2f}")
    print(f"stats={stats}")


if __name__ == "__main__":
    main()
