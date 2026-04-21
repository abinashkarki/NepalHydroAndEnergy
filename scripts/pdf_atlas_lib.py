#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent.parent
MANIFESTS_DIR = ROOT / "data" / "processed" / "corridor_tracing" / "manifests"
WIKI_PAGES = ROOT / "wiki" / "pages"
ASSETS_DIR = ROOT / "wiki" / "assets" / "images"
WIKI_INDEX_PATH = ROOT / "wiki" / "explorer" / "shared" / "wiki-page-index.json"
ALIASES_PATH = ROOT / "wiki" / "explorer" / "shared" / "hydropower-slug-aliases.json"

LEGACY_SOURCE_ID = "nea-transmission-annual-book-2077"
THUMB_DPI = 120
PX_PER_POINT = THUMB_DPI / 72.0
IMAGE_AREA_PCT_MIN = 3.0
IMAGE_WIDTH_PX_MIN = 150
CAPTION_DISTANCE_PT = 30.0
GENERIC_TAGS = {
    "project",
    "projects",
    "source",
    "sources",
    "entity",
    "entities",
    "concept",
    "concepts",
    "claim",
    "claims",
    "data",
    "official",
    "grid",
    "generation",
    "transmission",
    "hydro",
    "hydropower",
    "storage",
    "river",
    "basin",
    "watchlist",
    "top",
    "capacity",
    "under",
    "construction",
    "study",
    "survey",
}
SECTION_ROWS = [
    ("Message from the Minister", 2, 3),
    ("Message from the Secretary", 4, 4),
    ("Board of Directorates", 5, 5),
    ("Organisation Structure", 6, 6),
    ("Deputy Managing Directors", 7, 7),
    ("Managing Director's Report", 8, 20),
    ("Generation Directorate", 21, 42),
    ("Transmission Directorate", 43, 75),
    ("Distribution and Consumer Services Directorate", 76, 102),
    ("Planning, Monitoring and Information Technology Directorate", 103, 109),
    ("Engineering Services Directorate", 110, 140),
    ("Project Management Directorate", 141, 158),
    ("NEA's Subsidiary & Associate Companies", 159, 191),
    ("Central Activities", 192, 198),
    ("Administrative Directorate", 199, 203),
    ("Finance Directorate", 204, 219),
    ("Statistic & Schematics", 220, 231),
    ("Electricity Tariff", 232, 238),
    ("Appendix", 239, 263),
    ("Map", 264, 265),
]
LEGACY_LOW_SIGNAL_STUBS = {
    "2019-2020-3nepal",
    "2019-2020-5nepal",
    "nea2077-page-001",
    "nea2077-page-267",
    "inauguration-underground-cabling-kathmandu-valley-dhalkebar",
    "inauguration-upper-trisuli-hydroelectric-project-bardaghat",
}
DROP_ACTION = "drop"

SOURCES = {
    "nea-transmission-annual-book-2077": {
        "pdf_path": "data/raw/corridor_tracing/nea/nea_transmission_annual_book_2077.pdf",
        "asset_prefix": "nea2077",
        "credit": "Nepal Electricity Authority, A Year in Review FY 2019/20 (B.S. 2077)",
        "license": "gov-permissive",
        "wiki_source_slug": "nea-transmission-annual-book-2077",
        "thumb_dir": "tmp/pdf_render/nea_transmission_annual_book_2077",
        "atlas_json": "data/processed/corridor_tracing/manifests/nea_transmission_annual_book_2077_image_atlas.json",
        "decisions_v2_yaml": "data/processed/corridor_tracing/nea_annual_2077_image_decisions_v2.yaml",
        "provenance_filename": "_nea2077.json",
    },
    "nea-annual-report-fy2024-25": {
        "pdf_path": "data/raw/projects_storage/nea_annual_report_2024_2025.pdf",
        "asset_prefix": "nea2425",
        "credit": "Nepal Electricity Authority, A Year in Review FY 2024/25",
        "license": "gov-permissive",
        "wiki_source_slug": "nea-annual-report-fy2024-25",
        "thumb_dir": "tmp/pdf_render/nea_annual_report_2024_2025",
        "atlas_json": "data/processed/corridor_tracing/manifests/nea_annual_report_2024_2025_image_atlas.json",
        "decisions_v2_yaml": "data/processed/corridor_tracing/nea_annual_2425_image_decisions_v2.yaml",
        "provenance_filename": "_nea2425.json",
    },
    "moewri-ipsdp-exec-summary-2025": {
        "pdf_path": "data/raw/corridor_tracing/moewri/moewri_ipsdp_exec_summary_2025.pdf",
        "asset_prefix": "ipsdp2025",
        "credit": "Ministry of Energy, Water Resources and Irrigation (MoEWRI) / JICA — Project on Integrated Power System Development Plan in Nepal, Executive Summary (2025)",
        "license": "gov-permissive",
        "wiki_source_slug": "moewri-ipsdp-exec-summary-2025",
        "thumb_dir": "tmp/pdf_render/moewri_ipsdp_exec_summary_2025",
        "atlas_json": "data/processed/corridor_tracing/manifests/moewri_ipsdp_exec_summary_2025_image_atlas.json",
        "decisions_v2_yaml": "data/processed/corridor_tracing/moewri_ipsdp_2025_image_decisions_v2.yaml",
        "provenance_filename": "_ipsdp2025.json",
    },
    "jica-ipsdp-main-report-vol2": {
        "pdf_path": "data/raw/corridor_tracing/jica/jica_ipsdp_main_report_vol2.pdf",
        "asset_prefix": "ipsdpv2",
        "credit": "JICA Study Team — Project on Integrated Power System Development Plan in Nepal, Final Report, Annexes (Vol. 2) (December 2024)",
        "license": "gov-permissive",
        "wiki_source_slug": "jica-ipsdp-main-report-vol2",
        "thumb_dir": "tmp/pdf_render/jica_ipsdp_main_report_vol2",
        "atlas_json": "data/processed/corridor_tracing/manifests/jica_ipsdp_main_report_vol2_image_atlas.json",
        "decisions_v2_yaml": "data/processed/corridor_tracing/jica_ipsdp_vol2_image_decisions_v2.yaml",
        "provenance_filename": "_ipsdpv2.json",
    },
}


def get_source(source_id: str) -> dict[str, str]:
    try:
        return SOURCES[source_id]
    except KeyError as exc:
        raise KeyError(f"unknown source-id: {source_id}") from exc


def source_abs_path(source: dict[str, str], key: str) -> Path:
    return ROOT / source[key]


def page_index_path_for_source(source: dict[str, str]) -> Path:
    pdf_name = Path(source["pdf_path"]).stem
    return MANIFESTS_DIR / f"{pdf_name}_page_index.json"


def atlas_html_path_for_source(source: dict[str, str]) -> Path:
    return source_abs_path(source, "thumb_dir") / "atlas.html"


def source_page_url_for_assets(source: dict[str, str]) -> str:
    return "../../../" + source["pdf_path"]


def atlas_title_for_source(source_id: str, source: dict[str, str]) -> str:
    if source_id == LEGACY_SOURCE_ID:
        return "NEA Transmission Annual Book 2077 Image Atlas"
    return f"{source['credit']} Image Atlas"


def parse_scalar(value: str) -> Any:
    value = value.strip()
    if value == "":
        return ""
    if value.startswith('"') or value.startswith("[") or value.startswith("{"):
        return json.loads(value)
    if value.isdigit():
        return int(value)
    return value


def parse_decisions_text(raw: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    current: dict[str, Any] | None = None
    for line in raw.splitlines():
        if not line.strip():
            continue
        if line.startswith("- page: "):
            if current:
                rows.append(current)
            current = {"page": int(line.split(": ", 1)[1])}
            continue
        if current is None:
            continue
        if line.startswith("  ") and ": " in line:
            key, value = line.strip().split(": ", 1)
            current[key] = parse_scalar(value)
    if current:
        rows.append(current)
    return rows


def yaml_quote(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False)


def dump_decision_rows(rows: list[dict[str, Any]]) -> str:
    ordered_keys = [
        "page",
        "image_index",
        "action",
        "target_slug",
        "proposed_slug",
        "caption",
        "paragraph_anchor",
        "source_page",
        "note",
        "raw_caption",
        "candidate_slugs",
    ]
    lines: list[str] = []
    for row in rows:
        lines.append(f"- page: {int(row['page'])}")
        for key in ordered_keys[1:]:
            if key not in row:
                continue
            value = row[key]
            if isinstance(value, int):
                rendered = str(value)
            elif isinstance(value, str) and value in {"drop", "filmstrip", "inline_figure", "crop", "new_node", "page_render"}:
                rendered = value
            else:
                rendered = yaml_quote(value)
            lines.append(f"  {key}: {rendered}")
    return "\n".join(lines) + "\n"


def normalize(text: str) -> str:
    text = text.lower()
    text = text.replace("–", "-").replace("—", "-").replace("/", " ")
    text = re.sub(r"[^a-z0-9+\-.\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def significant_tokens(text: str) -> list[str]:
    tokens = []
    for token in re.split(r"[\s\-]+", text):
        token = token.strip()
        if len(token) >= 5 and token not in GENERIC_TAGS:
            tokens.append(token)
    return tokens


def count_term_occurrences(text: str, term: str) -> int:
    if not term:
        return 0
    pattern = r"(?<![a-z0-9])" + re.escape(term) + r"(?![a-z0-9])"
    return len(re.findall(pattern, text))


def excerpt(text: str, limit: int = 240) -> str:
    compact = re.sub(r"\s+", " ", text).strip()
    if len(compact) <= limit:
        return compact
    return compact[: limit - 1].rstrip() + "…"


def section_for_page(page_num: int) -> tuple[str, int, int]:
    if page_num < SECTION_ROWS[0][1]:
        return ("Front Matter (Unlisted)", 1, SECTION_ROWS[0][1] - 1)
    for title, start, end in SECTION_ROWS:
        if start <= page_num <= end:
            return (title, start, end)
    return ("Back Matter (Unlisted)", SECTION_ROWS[-1][2] + 1, 267)


def clear_gap(top_score: float, next_score: float) -> bool:
    return top_score >= 10.0 and (top_score - next_score) >= 4.0


def clamp_bbox_to_page(bbox: list[float], page_width: float, page_height: float) -> list[float] | None:
    x0, top, x1, bottom = bbox
    x0 = max(0.0, min(float(x0), page_width))
    top = max(0.0, min(float(top), page_height))
    x1 = max(x0, min(float(x1), page_width))
    bottom = max(top, min(float(bottom), page_height))
    if x1 <= x0 or bottom <= top:
        return None
    return [round(x0, 2), round(top, 2), round(x1, 2), round(bottom, 2)]


def asset_filename_for(source: dict[str, str], entry: dict[str, Any]) -> str:
    prefix = source["asset_prefix"]
    if entry["action"] == "page_render":
        return f"{prefix}-p{int(entry['page']):03d}.png"
    return f"{prefix}-p{int(entry['page']):03d}-img{int(entry['image_index']):02d}.png"


def title_from_slug(slug: str) -> str:
    return " ".join(part.upper() if part.isdigit() else part.capitalize() for part in slug.split("-"))


def decision_slug(entry: dict[str, Any]) -> str:
    return str(entry.get("target_slug") or entry.get("proposed_slug") or "")


def decision_signature(entry: dict[str, Any]) -> tuple[Any, ...]:
    return (
        int(entry["page"]),
        int(entry["image_index"]),
        entry.get("action", ""),
        decision_slug(entry),
        entry.get("caption", ""),
        entry.get("paragraph_anchor", ""),
        entry.get("note", ""),
    )


def drop_row_from(
    row: dict[str, Any],
    *,
    note: str = "",
    raw_caption: str = "",
    candidate_slugs: list[str] | None = None,
) -> dict[str, Any]:
    return {
        "page": int(row["page"]),
        "image_index": int(row["image_index"]),
        "action": DROP_ACTION,
        "target_slug": "",
        "proposed_slug": "",
        "caption": str(row.get("caption", "")),
        "paragraph_anchor": "",
        "source_page": int(row.get("source_page", row["page"])),
        "note": note,
        "raw_caption": raw_caption,
        "candidate_slugs": list(candidate_slugs or []),
    }


def canonical_candidate_slugs(record: dict[str, Any], limit: int = 3) -> list[str]:
    return [str(item.get("slug", "")) for item in record.get("candidate_slugs", []) if item.get("slug")][:limit]


def split_sentences(text: str) -> list[str]:
    cleaned = re.sub(r"\s+", " ", text).strip()
    if not cleaned:
        return []
    parts = re.split(r"(?<=[.!?])\s+|(?<=:)\s+(?=[A-Z0-9])|(?<=;)\s+", cleaned)
    return [part.strip() for part in parts if part.strip()]


def tokenize_slug(slug: str) -> list[str]:
    return [token for token in slug.split("-") if token]


def is_claim_or_data_slug(slug: str) -> bool:
    return slug.startswith("claim-") or slug.startswith("data-")


def is_source_page_slug(slug: str) -> bool:
    if not slug:
        return False
    return (ROOT / "wiki" / "pages" / "sources" / f"{slug}.md").exists()


def slug_shape_rejected(proposed_slug: str, raw_caption: str) -> bool:
    if not proposed_slug:
        return True
    if proposed_slug[0].isdigit():
        return True
    if "page-" in proposed_slug:
        return True
    if len(tokenize_slug(proposed_slug)) < 3:
        return True
    if slug_spans_multiple_sentence_boundaries(proposed_slug, raw_caption):
        return True
    return False


def slug_spans_multiple_sentence_boundaries(proposed_slug: str, raw_caption: str) -> bool:
    sentences = split_sentences(raw_caption)
    if len(sentences) <= 1:
        return False
    slug_tokens = set(tokenize_slug(proposed_slug))
    if not slug_tokens:
        return False
    matched_sentence_indexes: set[int] = set()
    for index, sentence in enumerate(sentences):
        sentence_tokens = set(normalize(sentence).split())
        if slug_tokens & sentence_tokens:
            matched_sentence_indexes.add(index)
    return len(matched_sentence_indexes) > 1


def low_signal_stub_slugs_for_source(source_id: str) -> set[str]:
    if source_id == LEGACY_SOURCE_ID:
        return set(LEGACY_LOW_SIGNAL_STUBS)
    return set()
