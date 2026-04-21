#!/usr/bin/env python3
from __future__ import annotations

import argparse
import html
import json
import shutil
import subprocess
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pdfplumber
from PIL import Image

from pdf_atlas_lib import (
    ALIASES_PATH,
    CAPTION_DISTANCE_PT,
    IMAGE_AREA_PCT_MIN,
    IMAGE_WIDTH_PX_MIN,
    LEGACY_SOURCE_ID,
    PX_PER_POINT,
    ROOT,
    SOURCES,
    SECTION_ROWS,
    THUMB_DPI,
    WIKI_INDEX_PATH,
    atlas_html_path_for_source,
    atlas_title_for_source,
    excerpt,
    get_source,
    normalize,
    page_index_path_for_source,
    section_for_page,
    significant_tokens,
    source_abs_path,
)


@dataclass
class CandidateReason:
    term: str
    source: str
    score: float


def slug_to_title_map() -> dict[str, str]:
    data = json.loads(WIKI_INDEX_PATH.read_text(encoding="utf-8"))
    return {slug: title for slug, title in data["slugToTitle"].items()}


def load_page_index(path: Path) -> list[dict[str, Any]]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_slug_aliases() -> dict[str, str]:
    raw = json.loads(ALIASES_PATH.read_text(encoding="utf-8"))
    return {normalize(alias): slug for alias, slug in raw.items()}


def load_slug_tags(all_slugs: list[str]) -> dict[str, list[str]]:
    out: dict[str, list[str]] = {}
    pages_root = ROOT / "wiki" / "pages"
    for slug in all_slugs:
        path = next((p for p in pages_root.glob(f"*/*{slug}.md") if p.name == f"{slug}.md"), None)
        if not path or not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        if not text.startswith("---\n"):
            continue
        frontmatter = text.split("---\n", 2)[1]
        import re

        match = re.search(r"^tags:\s*\[(.*?)\]\s*$", frontmatter, re.M)
        if not match:
            continue
        tags = [normalize(part) for part in match.group(1).split(",") if normalize(part)]
        if tags:
            out[slug] = tags
    return out


def build_slug_match_index() -> dict[str, list[tuple[str, str, float]]]:
    wiki_index = json.loads(WIKI_INDEX_PATH.read_text(encoding="utf-8"))
    aliases = load_slug_aliases()
    tags_by_slug = load_slug_tags(wiki_index["allSlugs"])
    slug_terms: dict[str, list[tuple[str, str, float]]] = defaultdict(list)

    for slug, title in wiki_index["slugToTitle"].items():
        title_norm = normalize(title)
        slug_norm = normalize(slug.replace("-", " "))
        title_space = title_norm.replace("-", " ")
        if title_norm:
            slug_terms[slug].append((title_norm, "title", 12.0))
        if title_space and title_space != title_norm:
            slug_terms[slug].append((title_space, "title", 10.0))
        if slug_norm and slug_norm != title_norm:
            slug_terms[slug].append((slug_norm, "title", 6.0))
        for token in sorted(set(significant_tokens(title_space)), key=len, reverse=True):
            slug_terms[slug].append((token, "title", 2.5))

    for alias, slug in aliases.items():
        alias_space = alias.replace("-", " ")
        alias_tokens = significant_tokens(alias_space)
        alias_is_specific = len(alias_space) >= 8 or len(alias_tokens) >= 2 or any(ch.isdigit() for ch in alias_space)
        if alias and alias_is_specific:
            slug_terms[slug].append((alias, "alias", 10.0))
            if alias_space != alias:
                slug_terms[slug].append((alias_space, "alias", 9.0))

    for slug, tags in tags_by_slug.items():
        for tag in tags:
            if len(tag) >= 5:
                slug_terms[slug].append((tag, "tag", 0.75))

    deduped: dict[str, list[tuple[str, str, float]]] = {}
    for slug, terms in slug_terms.items():
        best: dict[tuple[str, str], float] = {}
        for term, source, weight in terms:
            key = (term, source)
            best[key] = max(best.get(key, 0.0), weight)
        deduped[slug] = [(term, source, weight) for (term, source), weight in best.items()]
    return deduped


def count_term_occurrences(text: str, term: str) -> int:
    import re

    if not term:
        return 0
    pattern = r"(?<![a-z0-9])" + re.escape(term) + r"(?![a-z0-9])"
    return len(re.findall(pattern, text))


def score_candidate_slugs(
    page_text: str,
    slug_terms: dict[str, list[tuple[str, str, float]]],
    slug_titles: dict[str, str],
) -> list[dict[str, Any]]:
    text = normalize(page_text)
    if not text:
        return []
    scored: list[dict[str, Any]] = []
    for slug, terms in slug_terms.items():
        total = 0.0
        reasons: list[CandidateReason] = []
        for term, source, weight in terms:
            hits = count_term_occurrences(text, term)
            if not hits:
                continue
            contribution = weight * min(hits, 3)
            total += contribution
            reasons.append(CandidateReason(term=term, source=source, score=contribution))
        if total <= 0:
            continue
        reasons.sort(key=lambda item: item.score, reverse=True)
        scored.append(
            {
                "slug": slug,
                "title": slug_titles.get(slug, slug),
                "score": round(total, 2),
                "reasons": [f"matched '{reason.term}' via {reason.source}" for reason in reasons[:3]],
            }
        )
    scored.sort(key=lambda item: (-item["score"], item["slug"]))
    return scored[:5]


def ensure_thumbnails(pdf_path: Path, page_count: int, thumb_dir: Path) -> None:
    thumb_dir.mkdir(parents=True, exist_ok=True)
    need_render = any(not (thumb_dir / f"page_{page:03d}.png").exists() for page in range(1, page_count + 1))
    if not need_render:
        return
    temp_prefix = thumb_dir / "page"
    subprocess.run(
        [
            "pdftoppm",
            "-png",
            "-r",
            str(THUMB_DPI),
            "-f",
            "1",
            "-l",
            str(page_count),
            str(pdf_path),
            str(temp_prefix),
        ],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    for page in range(1, page_count + 1):
        src = thumb_dir / f"page-{page:03d}.png"
        dst = thumb_dir / f"page_{page:03d}.png"
        if src.exists():
            shutil.move(str(src), str(dst))


def page_png_path(thumb_dir: Path, page_num: int) -> Path:
    return thumb_dir / f"page_{page_num:03d}.png"


def load_image_size(thumb_dir: Path, page_num: int) -> tuple[int, int]:
    with Image.open(page_png_path(thumb_dir, page_num)) as img:
        return img.size


def group_words_into_lines(words: list[dict[str, Any]]) -> list[dict[str, Any]]:
    if not words:
        return []
    sorted_words = sorted(words, key=lambda item: (round(item["top"], 1), item["x0"]))
    lines: list[dict[str, Any]] = []
    for word in sorted_words:
        if not lines or abs(word["top"] - lines[-1]["top"]) > 3:
            lines.append(
                {
                    "words": [word],
                    "text": word["text"],
                    "x0": word["x0"],
                    "x1": word["x1"],
                    "top": word["top"],
                    "bottom": word["bottom"],
                }
            )
            continue
        line = lines[-1]
        line["words"].append(word)
        line["text"] += " " + word["text"]
        line["x0"] = min(line["x0"], word["x0"])
        line["x1"] = max(line["x1"], word["x1"])
        line["top"] = min(line["top"], word["top"])
        line["bottom"] = max(line["bottom"], word["bottom"])
    return lines


def line_column(line: dict[str, Any], page_width: float) -> str:
    center = (line["x0"] + line["x1"]) / 2
    return "left" if center < page_width / 2 else "right"


def image_column(image: dict[str, Any], page_width: float) -> str:
    center = (image["x0"] + image["x1"]) / 2
    return "left" if center < page_width / 2 else "right"


def find_nearest_caption(image: dict[str, Any], lines: list[dict[str, Any]], page_width: float) -> str:
    column = image_column(image, page_width)
    candidates: list[tuple[float, int, str]] = []
    image_top = image.get("top", 0.0)
    image_bottom = image.get("bottom", 0.0)
    for idx, line in enumerate(lines):
        if line_column(line, page_width) != column:
            continue
        vertical_gap = min(abs(line["top"] - image_bottom), abs(line["bottom"] - image_top))
        if vertical_gap > CAPTION_DISTANCE_PT:
            continue
        text = line["text"].strip()
        if not text:
            continue
        candidates.append((vertical_gap, idx, text))
    if not candidates:
        return ""
    candidates.sort(key=lambda item: (item[0], item[1]))
    _, best_idx, _ = candidates[0]
    merged = [lines[best_idx]["text"].strip()]
    follow_idx = best_idx + 1
    while follow_idx < len(lines):
        next_line = lines[follow_idx]
        if line_column(next_line, page_width) != column:
            break
        if next_line["top"] - lines[follow_idx - 1]["bottom"] > 6:
            break
        if next_line["top"] - image_bottom > CAPTION_DISTANCE_PT:
            break
        merged.append(next_line["text"].strip())
        follow_idx += 1
    return " ".join(part for part in merged if part)


def page_classification(text: str, kept_images: list[dict[str, Any]], tables: list[Any]) -> dict[str, bool]:
    import re

    text_norm = normalize(text)
    has_photo = any(0.4 <= item["aspect_ratio"] <= 2.5 for item in kept_images)
    has_table = bool(tables)
    kv_hits = len(re.findall(r"\b\d+(?:\.\d+)?\s*kv\b|\bkv\b", text_norm))
    mva_hits = len(re.findall(r"\b\d+(?:\.\d+)?\s*mva\b|\bmva\b", text_norm))
    substation_hits = text_norm.count("substation")
    has_map = (" map " in f" {text_norm} ") or (substation_hits >= 2 and kv_hits + mva_hits >= 3)
    return {
        "has_photo": has_photo,
        "has_table": has_table,
        "has_map": has_map,
    }


def section_for_source_page(source_id: str, page_num: int, page_count: int) -> tuple[str, int, int]:
    if source_id == LEGACY_SOURCE_ID:
        return section_for_page(page_num)
    return ("PDF Pages", 1, page_count)


def image_is_real(image: dict[str, Any], page_width: float, page_height: float) -> tuple[bool, float, float]:
    width_pt = float(image["x1"] - image["x0"])
    height_pt = float(image.get("bottom", 0.0) - image.get("top", 0.0))
    area_pt = max(width_pt, 0.0) * max(height_pt, 0.0)
    page_area = page_width * page_height
    area_pct = (area_pt / page_area) * 100 if page_area else 0.0
    width_px = width_pt * PX_PER_POINT
    in_top_right_glyph_box = image["x0"] >= page_width - 100 and image.get("top", 9999) <= 40
    is_real = area_pct >= IMAGE_AREA_PCT_MIN and width_px >= IMAGE_WIDTH_PX_MIN and not in_top_right_glyph_box
    return is_real, round(area_pct, 2), round(width_px, 1)


def html_escape(text: str) -> str:
    return html.escape(text or "")


def render_atlas_html(source_id: str, source: dict[str, str], records: list[dict[str, Any]]) -> Path:
    atlas_dir = source_abs_path(source, "thumb_dir")
    atlas_html_path = atlas_html_path_for_source(source)
    sections: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for record in records:
        sections[record["section"]["title"]].append(record)

    if source_id == LEGACY_SOURCE_ID:
        ordered_titles = ["Front Matter (Unlisted)"] + [title for title, _, _ in SECTION_ROWS] + ["Back Matter (Unlisted)"]
    else:
        ordered_titles = ["PDF Pages"]

    chunks = [
        "<!doctype html>",
        f"<html><head><meta charset='utf-8'><title>{html_escape(atlas_title_for_source(source_id, source))}</title>",
        "<style>",
        "body{font-family:system-ui,sans-serif;margin:0;background:#f7f5ef;color:#1f2937}",
        "header{position:sticky;top:0;background:#0f5b78;color:#fff;padding:12px 18px;z-index:2}",
        "main{padding:18px;max-width:1280px;margin:0 auto}",
        "section{margin:0 0 28px}",
        "section h2{margin:0 0 10px;padding:8px 10px;background:#dbe8ee;border-left:4px solid #0f5b78}",
        ".card{display:grid;grid-template-columns:280px 1fr;gap:16px;background:#fff;border:1px solid #d6d3d1;border-radius:8px;padding:12px;margin:0 0 12px;box-shadow:0 1px 2px rgba(0,0,0,0.05)}",
        ".thumb img{width:100%;height:auto;border:1px solid #d6d3d1;border-radius:4px;background:#fff}",
        ".meta p{margin:4px 0 8px;line-height:1.45}",
        ".pill{display:inline-block;margin:0 6px 6px 0;padding:3px 8px;border-radius:999px;background:#eef2ff;font-size:12px}",
        ".reason{font-family:ui-monospace,SFMono-Regular,monospace;font-size:12px;color:#475569}",
        ".caption{font-weight:600}",
        ".excerpt{color:#475569}",
        "</style></head><body>",
        f"<header><strong>{html_escape(atlas_title_for_source(source_id, source))}</strong></header><main>",
    ]

    for title in ordered_titles:
        rows = sections.get(title, [])
        if not rows:
            continue
        chunks.append(f"<section><h2>{html_escape(title)} <small>({len(rows)} real images)</small></h2>")
        for record in rows:
            rel_png = Path(record["rendered_page_png"]).relative_to(atlas_dir)
            candidates = "".join(
                f"<div class='reason'>{html_escape(item['slug'])} ({item['score']}): {html_escape('; '.join(item['reasons']))}</div>"
                for item in record["candidate_slugs"]
            ) or "<div class='reason'>No candidate slugs above threshold.</div>"
            classification = record["page_classification"]
            pills = [f"page {record['page']}", f"img {record['image_index']}", f"area {record['area_pct']}%"]
            for key, value in classification.items():
                if value:
                    pills.append(key)
            chunks.append(
                "<div class='card'>"
                f"<div class='thumb'><img src='{html_escape(str(rel_png))}' alt='page {record['page']}'></div>"
                "<div class='meta'>"
                + "".join(f"<span class='pill'>{html_escape(pill)}</span>" for pill in pills)
                + f"<p class='caption'>{html_escape(record['nearest_caption'] or '[no nearby caption]')}</p>"
                + f"<p><strong>Section:</strong> {html_escape(record['section']['title'])}</p>"
                + f"<p><strong>Candidate slugs:</strong><br>{candidates}</p>"
                + f"<p class='excerpt'><strong>Excerpt:</strong> {html_escape(record['page_text_excerpt'])}</p>"
                + "</div></div>"
            )
        chunks.append("</section>")
    chunks.append("</main></body></html>")
    atlas_html_path.write_text("\n".join(chunks), encoding="utf-8")
    return atlas_html_path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-id", required=True, choices=sorted(SOURCES.keys()))
    args = parser.parse_args()

    source = get_source(args.source_id)
    pdf_path = source_abs_path(source, "pdf_path")
    page_index_path = page_index_path_for_source(source)
    atlas_json_path = source_abs_path(source, "atlas_json")
    thumb_dir = source_abs_path(source, "thumb_dir")

    page_rows = load_page_index(page_index_path)
    slug_titles = slug_to_title_map()
    slug_terms = build_slug_match_index()

    ensure_thumbnails(pdf_path, len(page_rows), thumb_dir)

    records: list[dict[str, Any]] = []
    section_counts = Counter()
    pages_with_real_images = Counter()

    with pdfplumber.open(pdf_path) as pdf:
        for idx, page in enumerate(pdf.pages, start=1):
            page_row = page_rows[idx - 1]
            text = page_row["text"] or ""
            words = page.extract_words(use_text_flow=True, keep_blank_chars=False)
            lines = group_words_into_lines(words)
            tables = page.find_tables()
            kept_images: list[dict[str, Any]] = []

            for image_index, image in enumerate(page.images):
                is_real, area_pct, _width_px = image_is_real(image, page.width, page.height)
                if not is_real:
                    continue
                width_pt = float(image["x1"] - image["x0"])
                height_pt = float(image.get("bottom", 0.0) - image.get("top", 0.0))
                aspect_ratio = width_pt / height_pt if height_pt else 0.0
                caption = find_nearest_caption(image, lines, page.width)
                kept_images.append(
                    {
                        "page": idx,
                        "image_index": image_index,
                        "bbox": [
                            round(float(image["x0"]), 2),
                            round(float(image.get("top", 0.0)), 2),
                            round(float(image["x1"]), 2),
                            round(float(image.get("bottom", 0.0)), 2),
                        ],
                        "area_pct": area_pct,
                        "nearest_caption": caption,
                        "aspect_ratio": round(aspect_ratio, 3),
                    }
                )

            classification = page_classification(text, kept_images, tables)
            candidates = score_candidate_slugs(text, slug_terms, slug_titles)
            section_title, start_page, end_page = section_for_source_page(args.source_id, idx, len(page_rows))

            for kept in kept_images:
                record = {
                    "page": idx,
                    "image_index": kept["image_index"],
                    "bbox": kept["bbox"],
                    "area_pct": kept["area_pct"],
                    "nearest_caption": kept["nearest_caption"],
                    "rendered_page_png": str(page_png_path(thumb_dir, idx)),
                    "page_classification": classification,
                    "candidate_slugs": candidates,
                    "page_text_excerpt": excerpt(text),
                    "section": {
                        "title": section_title,
                        "page_start": start_page,
                        "page_end": end_page,
                    },
                }
                records.append(record)
                section_counts[section_title] += 1
                pages_with_real_images[idx] += 1

    atlas_json_path.parent.mkdir(parents=True, exist_ok=True)
    atlas_json_path.write_text(json.dumps(records, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    atlas_html_path = render_atlas_html(args.source_id, source, records)

    print(f"pages_total={len(page_rows)}")
    print(f"real_images_total={len(records)}")
    print("per_section_counts=")
    if args.source_id == LEGACY_SOURCE_ID:
        ordered_titles = ["Front Matter (Unlisted)"] + [title for title, _, _ in SECTION_ROWS] + ["Back Matter (Unlisted)"]
    else:
        ordered_titles = ["PDF Pages"]
    for title in ordered_titles:
        if title in section_counts:
            print(f"  {title}: {section_counts[title]}")
    print(f"atlas_html={atlas_html_path}")
    print(f"atlas_json={atlas_json_path}")


if __name__ == "__main__":
    main()
