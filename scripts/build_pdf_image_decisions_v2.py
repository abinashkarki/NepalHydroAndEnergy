#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any

from pdf_atlas_lib import (
    DROP_ACTION,
    LEGACY_LOW_SIGNAL_STUBS,
    LEGACY_SOURCE_ID,
    ROOT,
    SOURCES,
    WIKI_INDEX_PATH,
    canonical_candidate_slugs,
    clear_gap,
    drop_row_from,
    dump_decision_rows,
    get_source,
    is_claim_or_data_slug,
    is_source_page_slug,
    normalize,
    slug_shape_rejected,
    source_abs_path,
)


LEGACY_OVERRIDES: dict[tuple[int, int], dict[str, object]] = {
    (2, 0): {
        "action": "filmstrip",
        "target_slug": "kathmandu-valley-underground-cabling",
        "proposed_slug": "",
        "caption": "Inauguration of Underground Cabling in Kathmandu Valley",
        "paragraph_anchor": "",
    },
    (2, 1): {
        "action": "filmstrip",
        "target_slug": "upper-trishuli-3a",
        "proposed_slug": "",
        "caption": "Inauguration of Upper Trisuli 3A Hydroelectric Project",
        "paragraph_anchor": "",
    },
    (25, 1): {
        "action": "filmstrip",
        "target_slug": "andhi-khola",
        "proposed_slug": "",
        "caption": "Repairing of Stay vanes",
        "paragraph_anchor": "",
    },
    (25, 2): {
        "action": "filmstrip",
        "target_slug": "andhi-khola",
        "proposed_slug": "",
        "caption": "Control Room Furnished with SCADA",
        "paragraph_anchor": "",
    },
    (28, 1): {
        "action": "filmstrip",
        "target_slug": "upper-trishuli-3a",
        "proposed_slug": "",
        "caption": "Excitation Floor",
        "paragraph_anchor": "",
    },
    (47, 1): {
        "action": "filmstrip",
        "target_slug": "tingla-132-33kv-substation",
        "proposed_slug": "",
        "caption": "132/33/11 kV Tingla Substation",
        "paragraph_anchor": "",
    },
    (48, 1): {
        "action": "filmstrip",
        "target_slug": "purbi-chitwan-132kv-substation",
        "proposed_slug": "",
        "caption": "Purbi Chitwan 132 kV substation",
        "paragraph_anchor": "",
    },
    (52, 1): {
        "action": "filmstrip",
        "target_slug": "modi-lekhnath-132kv",
        "proposed_slug": "",
        "caption": "Lahachowk substation",
        "paragraph_anchor": "",
    },
    (52, 2): {
        "action": "filmstrip",
        "target_slug": "modi-lekhnath-132kv",
        "proposed_slug": "",
        "caption": "New Modi substation",
        "paragraph_anchor": "",
    },
    (56, 1): {
        "action": "filmstrip",
        "target_slug": "nawalpur-132kv-substation",
        "proposed_slug": "",
        "caption": "Nawalpur 132 kV SS",
        "paragraph_anchor": "",
    },
    (61, 1): {
        "action": "filmstrip",
        "target_slug": "hetauda-dhalkebar-inaruwa-backbone",
        "proposed_slug": "",
        "caption": "Ongoing Stringing work at Dhankuta Section",
        "paragraph_anchor": "",
    },
    (63, 1): {
        "action": "filmstrip",
        "target_slug": "dhungesangu-basantapur-220-132kv",
        "proposed_slug": "",
        "caption": "Foundation of Control Room Building under progress at Dhungesanghu Substation",
        "paragraph_anchor": "",
    },
    (63, 3): {
        "action": "filmstrip",
        "target_slug": "dhungesangu-basantapur-220-132kv",
        "proposed_slug": "",
        "caption": "Tower Erection under progress in Basantapur–Dhungesanghu section",
        "paragraph_anchor": "",
    },
    (67, 1): {
        "action": "filmstrip",
        "target_slug": "ratmate-rasuwagadhi-kerung-400kv",
        "proposed_slug": "",
        "caption": "Joint Technical Group (JTG) meeting between NEA and SGCC at NEA Head office",
        "paragraph_anchor": "",
    },
    (74, 1): {
        "action": "filmstrip",
        "target_slug": "main-load-dispatch-centre",
        "proposed_slug": "",
        "caption": "Emergency Control Center (ECC) Building at Hetauda",
        "paragraph_anchor": "",
    },
    (74, 2): {
        "action": "filmstrip",
        "target_slug": "main-load-dispatch-centre",
        "proposed_slug": "",
        "caption": "During inauguration of main LDC",
        "paragraph_anchor": "",
    },
    (115, 1): {
        "action": "filmstrip",
        "target_slug": "upper-arun",
        "proposed_slug": "",
        "caption": "Honorable Minister for Energy, Water Resources and Irrigation and NEA leadership during the Upper Arun site visit",
        "paragraph_anchor": "",
    },
    (116, 1): {
        "action": "filmstrip",
        "target_slug": "upper-arun",
        "proposed_slug": "",
        "caption": "Project Location",
        "paragraph_anchor": "",
    },
    (117, 1): {
        "action": "filmstrip",
        "target_slug": "upper-arun",
        "proposed_slug": "",
        "caption": "Test Adit at Proposed Headworks Site",
        "paragraph_anchor": "",
    },
    (118, 1): {
        "action": "filmstrip",
        "target_slug": "upper-arun",
        "proposed_slug": "",
        "caption": "Proposed Headworks",
        "paragraph_anchor": "",
    },
    (118, 2): {
        "action": "filmstrip",
        "target_slug": "upper-arun",
        "proposed_slug": "",
        "caption": "Proposed Underground Powerhouse 3D Model",
        "paragraph_anchor": "",
    },
    (152, 1): {
        "action": "filmstrip",
        "target_slug": "kathmandu-valley-underground-cabling",
        "proposed_slug": "",
        "caption": "Cable laying works at Chabahil",
        "paragraph_anchor": "",
    },
    (173, 1): {
        "action": "filmstrip",
        "target_slug": "tanahu-hydropower",
        "proposed_slug": "",
        "caption": "Camp Facilities of Package 2 Contractor",
        "paragraph_anchor": "",
    },
    (173, 2): {
        "action": "filmstrip",
        "target_slug": "tanahu-hydropower",
        "proposed_slug": "",
        "caption": "Tower Testing at the Contractor’s Laboratory",
        "paragraph_anchor": "",
    },
    (173, 3): {
        "action": "filmstrip",
        "target_slug": "tanahu-hydropower",
        "proposed_slug": "",
        "caption": "Portal Area of Cable Tunnel and Main Access",
        "paragraph_anchor": "",
    },
    (176, 1): {
        "action": "filmstrip",
        "target_slug": "tanahu-hydropower",
        "proposed_slug": "",
        "caption": "Site Visit by NEA MD Kulman Ghising on 9th March 2020",
        "paragraph_anchor": "",
    },
    (176, 2): {
        "action": "filmstrip",
        "target_slug": "tanahu-hydropower",
        "proposed_slug": "",
        "caption": "Work in Progress in Power House",
        "paragraph_anchor": "",
    },
    (176, 3): {
        "action": "filmstrip",
        "target_slug": "tanahu-hydropower",
        "proposed_slug": "",
        "caption": "Work in Progress in Adit-3",
        "paragraph_anchor": "",
    },
    (177, 1): {
        "action": "filmstrip",
        "target_slug": "chilime",
        "proposed_slug": "",
        "caption": "Work in Progress in Surge Shaft",
        "paragraph_anchor": "",
    },
    (177, 2): {
        "action": "filmstrip",
        "target_slug": "chilime",
        "proposed_slug": "",
        "caption": "Work in Progress in Permanent Bridge",
        "paragraph_anchor": "",
    },
    (177, 3): {
        "action": "filmstrip",
        "target_slug": "chilime",
        "proposed_slug": "",
        "caption": "Signing ceremony of Contract Agreement for Lot-2 electro-mechanical works",
        "paragraph_anchor": "",
    },
    (177, 5): {
        "action": "filmstrip",
        "target_slug": "chilime",
        "proposed_slug": "",
        "caption": "Chilime Hydroelectric Plant",
        "paragraph_anchor": "",
    },
    (181, 1): {
        "action": "filmstrip",
        "target_slug": "sanjen",
        "proposed_slug": "",
        "caption": "Sanjen (Upper) Hydroelectric Project (SUHEP)",
        "paragraph_anchor": "",
    },
    (181, 2): {
        "action": "filmstrip",
        "target_slug": "sanjen",
        "proposed_slug": "",
        "caption": "SUHEP Headworks and Powerhouse",
        "paragraph_anchor": "",
    },
    (191, 1): {
        "action": "filmstrip",
        "target_slug": "tamakoshi-v",
        "proposed_slug": "",
        "caption": "Interconnection System",
        "paragraph_anchor": "",
    },
    (191, 2): {
        "action": "filmstrip",
        "target_slug": "tamakoshi-v",
        "proposed_slug": "",
        "caption": "Layout of Permanent Camp",
        "paragraph_anchor": "",
    },
    (192, 1): {
        "action": "filmstrip",
        "target_slug": "uttarganga-storage-hydropower-project",
        "proposed_slug": "",
        "caption": "High level visit at the Project Site",
        "paragraph_anchor": "",
    },
    (193, 1): {
        "action": "filmstrip",
        "target_slug": "uttarganga-storage-hydropower-project",
        "proposed_slug": "",
        "caption": "Proposed Reservoir Area",
        "paragraph_anchor": "",
    },
}


def override_row(row: dict[str, object], **updates: object) -> dict[str, object]:
    updated = dict(row)
    updated.update(updates)
    updated.setdefault("target_slug", "")
    updated.setdefault("proposed_slug", "")
    updated.setdefault("caption", "")
    updated.setdefault("paragraph_anchor", "")
    updated.setdefault("source_page", int(updated.get("page", row["page"])))
    updated["page"] = int(updated["page"])
    updated["image_index"] = int(updated["image_index"])
    updated["source_page"] = int(updated["source_page"])
    return updated


def load_atlas_rows(path: Path) -> list[dict[str, Any]]:
    return json.loads(path.read_text(encoding="utf-8"))


def guess_paragraph_anchor(target_slug: str, candidate_terms: list[str]) -> str:
    if not target_slug:
        return ""
    page_path = next((p for p in (ROOT / "wiki" / "pages").glob(f"*/*{target_slug}.md") if p.name == f"{target_slug}.md"), None)
    if not page_path or not page_path.exists():
        return ""
    text = page_path.read_text(encoding="utf-8")
    body = text.split("---\n", 2)[-1]
    paragraphs = [part.strip() for part in re.split(r"\n\s*\n", body) if part.strip()]
    search_terms = [term for term in candidate_terms if len(term) >= 4]
    for paragraph in paragraphs:
        paragraph_norm = normalize(paragraph)
        for term in search_terms:
            if term in paragraph_norm:
                clean = re.sub(r"\s+", " ", paragraph)
                return clean[:120]
    for paragraph in paragraphs:
        if paragraph.startswith("#"):
            continue
        clean = re.sub(r"\s+", " ", paragraph)
        if len(clean) >= 30:
            return clean[:120]
    return ""


def proposed_slug_from_caption(source: dict[str, str], page_text: str, caption: str, page_num: int) -> str:
    raw = caption or page_text
    raw = normalize(raw)
    tokens = [
        tok
        for tok in raw.split()
        if len(tok) >= 3 and tok not in {"nepal", "electricity", "authority", "annual", "review", "fiscal", "year"}
    ]
    if not tokens:
        return f"{source['asset_prefix']}-page-{page_num:03d}"
    return "-".join(tokens[:6])


def legacy_focus_slug(slug: str) -> bool:
    return (
        slug == "nea"
        or slug in {"mai", "rasuwagadhi", "upper-trishuli-3a"}
        or slug in LEGACY_LOW_SIGNAL_STUBS
        or is_claim_or_data_slug(slug)
    )


def base_row_from_record(source: dict[str, str], record: dict[str, Any]) -> dict[str, Any]:
    candidates = record.get("candidate_slugs", [])
    top_slug = candidates[0]["slug"] if candidates else ""
    top_score = candidates[0]["score"] if candidates else 0.0
    next_score = candidates[1]["score"] if len(candidates) > 1 else 0.0
    page_class = record["page_classification"]
    action = DROP_ACTION
    target_slug = ""
    proposed_slug = ""
    paragraph_anchor = ""

    if page_class["has_table"] and not page_class["has_photo"]:
        action = "crop"
        target_slug = top_slug
    elif not candidates or top_score < 6.0:
        action = "new_node"
        proposed_slug = proposed_slug_from_caption(source, record["page_text_excerpt"], record["nearest_caption"], int(record["page"]))
    elif page_class["has_photo"] and clear_gap(top_score, next_score):
        action = "inline_figure"
        target_slug = top_slug
        reason_terms = []
        for reason in candidates[0].get("reasons", []):
            match = re.search(r"matched '([^']+)'", reason)
            if match:
                reason_terms.append(match.group(1))
        paragraph_anchor = guess_paragraph_anchor(top_slug, reason_terms)
    elif page_class["has_photo"]:
        action = "filmstrip"
        target_slug = top_slug
    elif page_class["has_map"]:
        action = "crop"
        target_slug = top_slug

    return {
        "page": int(record["page"]),
        "image_index": int(record["image_index"]),
        "action": action,
        "target_slug": target_slug,
        "proposed_slug": proposed_slug,
        "caption": str(record.get("nearest_caption", "")),
        "paragraph_anchor": paragraph_anchor,
        "source_page": int(record["page"]),
        "note": "",
        "raw_caption": str(record.get("nearest_caption", "")),
        "candidate_slugs": canonical_candidate_slugs(record),
    }


def with_drop_metadata(row: dict[str, Any], record: dict[str, Any], note: str) -> dict[str, Any]:
    return drop_row_from(
        row,
        note=note,
        raw_caption=str(record.get("nearest_caption", "")),
        candidate_slugs=canonical_candidate_slugs(record),
    )


def maybe_apply_guardrails(
    source_id: str,
    source: dict[str, str],
    row: dict[str, Any],
    record: dict[str, Any],
    *,
    is_override: bool,
    counts_by_target: Counter,
) -> dict[str, Any]:
    candidate_slugs = canonical_candidate_slugs(record)
    top_candidate = candidate_slugs[0] if candidate_slugs else ""

    if source_id == LEGACY_SOURCE_ID and not is_override and legacy_focus_slug(top_candidate):
        return with_drop_metadata(row, record, "skipped:auto-routed-to-claim-or-data" if is_claim_or_data_slug(top_candidate) else "skipped:legacy-focus-drop")

    if not is_override and row["action"] in {"filmstrip", "inline_figure", "crop"} and is_claim_or_data_slug(top_candidate):
        return with_drop_metadata(row, record, "skipped:auto-routed-to-claim-or-data")

    target_slug_for_source_check = str(row.get("target_slug", ""))
    own_source_slug = source.get("wiki_source_slug", "")
    if (
        not is_override
        and row["action"] in {"filmstrip", "inline_figure", "crop"}
        and target_slug_for_source_check
        and target_slug_for_source_check != own_source_slug
        and is_source_page_slug(target_slug_for_source_check)
    ):
        return with_drop_metadata(row, record, "skipped:auto-routed-to-source")

    if not is_override and row["action"] == "new_node":
        if slug_shape_rejected(str(row.get("proposed_slug", "")), str(record.get("nearest_caption", "") or record.get("page_text_excerpt", ""))):
            return with_drop_metadata(row, record, "skipped:new-node-shape-rejected")

    target_slug = str(row.get("target_slug", ""))
    if row["action"] in {"filmstrip", "inline_figure"} and target_slug:
        if counts_by_target[target_slug] >= 5 and not is_override:
            return with_drop_metadata(row, record, "skipped:per-target-cap-reached")
        counts_by_target[target_slug] += 1

    return row


def build_rows(source_id: str) -> list[dict[str, Any]]:
    source = get_source(source_id)
    atlas_rows = load_atlas_rows(source_abs_path(source, "atlas_json"))
    overrides = LEGACY_OVERRIDES if source_id == LEGACY_SOURCE_ID else {}
    counts_by_target: Counter = Counter()
    output: list[dict[str, Any]] = []
    for record in atlas_rows:
        key = (int(record["page"]), int(record["image_index"]))
        row = base_row_from_record(source, record)
        is_override = key in overrides
        if is_override:
            row = override_row(row, **overrides[key])
            row["raw_caption"] = str(record.get("nearest_caption", ""))
            row["candidate_slugs"] = canonical_candidate_slugs(record)
            row["note"] = ""
        row = maybe_apply_guardrails(source_id, source, row, record, is_override=is_override, counts_by_target=counts_by_target)
        output.append(row)
    return output


def print_summary(rows: list[dict[str, Any]]) -> None:
    action_counts = Counter(str(row["action"]) for row in rows)
    target_counts = Counter(str(row.get("target_slug", "")) for row in rows if row.get("target_slug"))
    note_counts = Counter(str(row.get("note", "")) for row in rows if row.get("note"))
    print("action_counts=" + json.dumps(dict(sorted(action_counts.items())), ensure_ascii=False))
    if note_counts:
        print("note_counts=" + json.dumps(dict(sorted(note_counts.items())), ensure_ascii=False))
    top_targets = target_counts.most_common(10)
    print("top_target_slugs=" + json.dumps(top_targets, ensure_ascii=False))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-id", required=True, choices=sorted(SOURCES.keys()))
    args = parser.parse_args()

    source = get_source(args.source_id)
    output_path = source_abs_path(source, "decisions_v2_yaml")
    rows = build_rows(args.source_id)
    output_path.write_text(dump_decision_rows(rows), encoding="utf-8")
    print(f"wrote={output_path}")
    print_summary(rows)


if __name__ == "__main__":
    main()
