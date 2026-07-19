#!/usr/bin/env python3
"""Crosswalk local hydropower map records to the normalized official DoED registry."""

from __future__ import annotations

import argparse
import csv
import json
import math
import re
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

try:
    from .benchmark_hydromap_coverage import (
        canonical_project_name,
        capacity_similarity,
        geojson_properties,
        load_csv,
        load_json,
        parse_number,
        similarity,
    )
except ImportError:
    from benchmark_hydromap_coverage import (
        canonical_project_name,
        capacity_similarity,
        geojson_properties,
        load_csv,
        load_json,
        parse_number,
        similarity,
    )


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_LOCAL_POINTS = ROOT / "data" / "processed" / "maps" / "hydropower_project_display_points.geojson"
DEFAULT_DOED_REGISTRY = ROOT / "data" / "processed" / "tables" / "doed_hydropower_registry.csv"
DEFAULT_ALIASES = ROOT / "data" / "project_identity_aliases.csv"
DEFAULT_REVIEW_DISPOSITIONS = ROOT / "data" / "doed_crosswalk_dispositions.csv"
DEFAULT_OUTPUT_DIR = ROOT / "data" / "processed" / "tables"
OVERLAY_NAME = "doed_project_status_overlay.csv"
REVIEW_NAME = "doed_project_crosswalk_review.csv"
SUMMARY_NAME = "doed_project_status_overlay_summary.json"

REGULATORY_SUFFIXES = re.compile(
    r"\b(slc|glc|gac|sac|gon reserved|reserved)\b",
    flags=re.IGNORECASE,
)

CATEGORY_PRECEDENCE = {
    "operating_record": 100,
    "generation_license": 90,
    "survey_license": 80,
    "generation_application": 70,
    "survey_application": 60,
    "gon_under_study": 50,
    "gon_studied": 40,
    "cancelled_generation_license": 30,
    "cancelled_survey_license": 29,
    "cancelled_generation_application": 20,
    "cancelled_survey_application": 19,
}

STATUS_LABELS = {
    "operating_record": "Operating record",
    "generation_license": "Generation licence",
    "survey_license": "Survey licence",
    "generation_application": "Generation-licence application",
    "survey_application": "Survey-licence application",
    "gon_under_study": "Government project under study",
    "gon_studied": "Government-studied project",
    "cancelled_generation_license": "Generation licence cancelled",
    "cancelled_survey_license": "Survey licence cancelled",
    "cancelled_generation_application": "Generation application cancelled",
    "cancelled_survey_application": "Survey application cancelled",
}

OVERLAY_FIELDS = [
    "local_project",
    "local_capacity_mw",
    "local_license_type",
    "local_river",
    "match_status",
    "match_confidence",
    "match_basis",
    "doed_primary_category",
    "doed_status_display",
    "doed_categories",
    "doed_record_status",
    "doed_license_status",
    "doed_study_status",
    "doed_delivery_status",
    "doed_capacity_mw",
    "doed_capacity_difference_mw",
    "doed_project_names",
    "doed_record_numbers",
    "doed_source_urls",
    "doed_source_updated_on",
    "doed_record_ids",
]

REVIEW_FIELDS = [
    "official_project",
    "official_capacity_mw",
    "official_regulatory_category",
    "official_river",
    "official_record_number",
    "official_source_url",
    "suggested_local_project",
    "suggested_local_capacity_mw",
    "suggested_local_license_type",
    "name_similarity",
    "river_similarity",
    "capacity_similarity",
    "coordinate_distance_km",
    "coordinate_similarity",
    "combined_similarity",
    "review_decision",
]


def identity_name(value: Any) -> str:
    text = REGULATORY_SUFFIXES.sub(" ", str(value or ""))
    return canonical_project_name(text)


def dms_to_decimal(value: Any) -> float | None:
    text = str(value or "").strip().replace("°", "o")
    if not text:
        return None
    match = re.search(r"(-?\d+(?:\.\d+)?)\s*[oO]\s*(\d+(?:\.\d+)?)?\s*'?\s*(\d+(?:\.\d+)?)?", text)
    if not match:
        return parse_number(text)
    degrees = float(match.group(1))
    minutes = float(match.group(2) or 0)
    seconds = float(match.group(3) or 0)
    sign = -1 if degrees < 0 else 1
    return sign * (abs(degrees) + minutes / 60 + seconds / 3600)


def official_midpoint(row: dict[str, Any]) -> tuple[float, float] | None:
    lat1 = dms_to_decimal(row.get("latitude_1_dms"))
    lat2 = dms_to_decimal(row.get("latitude_2_dms"))
    lon1 = dms_to_decimal(row.get("longitude_1_dms"))
    lon2 = dms_to_decimal(row.get("longitude_2_dms"))
    if None in {lat1, lat2, lon1, lon2}:
        return None
    assert lat1 is not None and lat2 is not None and lon1 is not None and lon2 is not None
    if abs(lat1) + abs(lat2) + abs(lon1) + abs(lon2) == 0:
        return None
    return ((lat1 + lat2) / 2, (lon1 + lon2) / 2)


def distance_km(local: dict[str, Any], official: dict[str, Any]) -> float | None:
    local_lat = parse_number(local.get("raw_lat"))
    local_lon = parse_number(local.get("raw_lon"))
    midpoint = official_midpoint(official)
    if local_lat is None or local_lon is None or midpoint is None:
        return None
    official_lat, official_lon = midpoint
    delta_lat = (local_lat - official_lat) * 111
    delta_lon = (local_lon - official_lon) * 111 * math.cos(math.radians(official_lat))
    return math.hypot(delta_lat, delta_lon)


def load_aliases(path: Path) -> dict[str, dict[str, str]]:
    if not path.exists():
        return {}
    aliases: dict[str, dict[str, str]] = {}
    for row in load_csv(path):
        local_project = str(row.get("local_project") or "").strip()
        doed_project = str(row.get("doed_project") or "").strip()
        decision = str(row.get("decision") or "approved").strip().casefold()
        if local_project and doed_project and decision == "approved":
            aliases[local_project] = row
    return aliases


def disposition_key(row: dict[str, Any]) -> tuple[str, str, str, str]:
    """Identify one reviewed nearest-neighbour suggestion, not an official identity."""
    return (
        str(row.get("official_project") or "").strip(),
        str(row.get("official_regulatory_category") or "").strip(),
        str(row.get("official_record_number") or "").strip(),
        str(row.get("suggested_local_project") or "").strip(),
    )


def load_review_dispositions(path: Path) -> dict[tuple[str, str, str, str], dict[str, str]]:
    if not path.exists():
        return {}
    dispositions: dict[tuple[str, str, str, str], dict[str, str]] = {}
    for row in load_csv(path):
        decision = str(row.get("decision") or "").strip()
        key = disposition_key(row)
        if all(key) and decision.startswith("rejected_"):
            dispositions[key] = row
    return dispositions


def candidate_is_compatible(local: dict[str, Any], official: dict[str, Any], candidate_count: int) -> bool:
    distance = distance_km(local, official)
    if distance is not None:
        return distance <= 25
    if candidate_count == 1:
        return True
    river_score = similarity(local.get("river"), official.get("river"))
    capacity_score = capacity_similarity(local.get("capacity_mw"), official.get("capacity_mw"))
    return river_score >= 0.8 and capacity_score >= 0.8


def match_local_records(
    local_rows: list[dict[str, Any]],
    official_rows: list[dict[str, Any]],
    aliases: dict[str, dict[str, str]],
) -> tuple[dict[int, list[int]], dict[int, dict[str, str]]]:
    index: dict[str, list[int]] = defaultdict(list)
    for official_index, row in enumerate(official_rows):
        key = identity_name(row.get("project"))
        if key:
            index[key].append(official_index)
    matches: dict[int, list[int]] = {}
    match_meta: dict[int, dict[str, str]] = {}
    for local_index, local in enumerate(local_rows):
        local_project = str(local.get("project") or "")
        alias = aliases.get(local_project)
        key = identity_name(alias["doed_project"] if alias else local_project)
        candidates = index.get(key, [])
        compatible = [
            official_index
            for official_index in candidates
            if candidate_is_compatible(local, official_rows[official_index], len(candidates))
        ]
        if not compatible:
            continue
        matches[local_index] = compatible
        match_meta[local_index] = {
            "status": "alias" if alias else "exact",
            "confidence": str(alias.get("confidence") or "high") if alias else "high",
            "basis": str(alias.get("match_basis") or "approved identity alias")
            if alias
            else "conservative normalized name with spatial/capacity compatibility",
        }
    return matches, match_meta


def primary_record(rows: list[dict[str, Any]]) -> dict[str, Any]:
    return max(
        rows,
        key=lambda row: (
            CATEGORY_PRECEDENCE.get(str(row.get("regulatory_category")), 0),
            str(row.get("source_updated_on") or ""),
        ),
    )


def join_unique(values: Iterable[Any]) -> str:
    return " | ".join(sorted({str(value).strip() for value in values if str(value or "").strip()}))


def overlay_row(
    local: dict[str, Any],
    matched: list[dict[str, Any]],
    meta: dict[str, str] | None,
) -> dict[str, Any]:
    if not matched:
        return {
            "local_project": local.get("project", ""),
            "local_capacity_mw": local.get("capacity_mw", ""),
            "local_license_type": local.get("license_type", ""),
            "local_river": local.get("river", ""),
            "match_status": "unmatched",
            "match_confidence": "",
            "match_basis": "",
            **{field: "" for field in OVERLAY_FIELDS[7:]},
        }
    primary = primary_record(matched)
    statuses = {str(row.get("record_status") or "") for row in matched}
    record_status = "mixed" if {"active", "cancelled"}.issubset(statuses) else next(iter(statuses - {""}), "")
    local_capacity = parse_number(local.get("capacity_mw"))
    official_capacity = parse_number(primary.get("capacity_mw"))
    difference = (
        round(abs(local_capacity - official_capacity), 3)
        if local_capacity is not None and official_capacity is not None
        else ""
    )
    categories = [row.get("regulatory_category") for row in matched]
    operating = any(row.get("delivery_status") == "operating" for row in matched)
    return {
        "local_project": local.get("project", ""),
        "local_capacity_mw": local.get("capacity_mw", ""),
        "local_license_type": local.get("license_type", ""),
        "local_river": local.get("river", ""),
        "match_status": meta.get("status", "exact") if meta else "exact",
        "match_confidence": meta.get("confidence", "high") if meta else "high",
        "match_basis": meta.get("basis", "") if meta else "",
        "doed_primary_category": primary.get("regulatory_category", ""),
        "doed_status_display": STATUS_LABELS.get(str(primary.get("regulatory_category") or ""), ""),
        "doed_categories": join_unique(categories),
        "doed_record_status": record_status,
        "doed_license_status": primary.get("license_status", ""),
        "doed_study_status": primary.get("study_status", ""),
        "doed_delivery_status": "operating" if operating else "",
        "doed_capacity_mw": official_capacity if official_capacity is not None else "",
        "doed_capacity_difference_mw": difference,
        "doed_project_names": join_unique(row.get("project") for row in matched),
        "doed_record_numbers": join_unique(row.get("record_number") for row in matched),
        "doed_source_urls": join_unique(row.get("source_url") for row in matched),
        "doed_source_updated_on": max(str(row.get("source_updated_on") or "") for row in matched),
        "doed_record_ids": join_unique(row.get("record_id") for row in matched),
    }


def review_score(official: dict[str, Any], local: dict[str, Any]) -> dict[str, Any]:
    name_score = similarity(official.get("project"), local.get("project"))
    river_score = similarity(official.get("river"), local.get("river"))
    capacity_score = capacity_similarity(official.get("capacity_mw"), local.get("capacity_mw"))
    distance = distance_km(local, official)
    coordinate_score = max(0.0, 1.0 - distance / 50) if distance is not None else 0.0
    combined = 0.45 * name_score + 0.20 * river_score + 0.15 * capacity_score + 0.20 * coordinate_score
    return {
        "name_similarity": round(name_score, 3),
        "river_similarity": round(river_score, 3),
        "capacity_similarity": round(capacity_score, 3),
        "coordinate_distance_km": round(distance, 3) if distance is not None else "",
        "coordinate_similarity": round(coordinate_score, 3),
        "combined_similarity": round(combined, 3),
    }


def build_review_queue(
    local_rows: list[dict[str, Any]],
    official_rows: list[dict[str, Any]],
    matched_official_indexes: set[int],
    dispositions: dict[tuple[str, str, str, str], dict[str, str]] | None = None,
) -> list[dict[str, Any]]:
    queue: list[dict[str, Any]] = []
    priority_categories = {"operating_record", "generation_license"}
    for official_index, official in enumerate(official_rows):
        if official_index in matched_official_indexes or official.get("regulatory_category") not in priority_categories:
            continue
        ranked = sorted(
            ((review_score(official, local), local) for local in local_rows),
            key=lambda item: item[0]["combined_similarity"],
            reverse=True,
        )
        scores, suggested = ranked[0]
        review_row = {
                "official_project": official.get("project", ""),
                "official_capacity_mw": official.get("capacity_mw", ""),
                "official_regulatory_category": official.get("regulatory_category", ""),
                "official_river": official.get("river", ""),
                "official_record_number": official.get("record_number", ""),
                "official_source_url": official.get("source_url", ""),
                "suggested_local_project": suggested.get("project", ""),
                "suggested_local_capacity_mw": suggested.get("capacity_mw", ""),
                "suggested_local_license_type": suggested.get("license_type", ""),
                **scores,
                "review_decision": "unreviewed_no_auto_accept",
            }
        disposition = (dispositions or {}).get(disposition_key(review_row))
        if disposition:
            review_row["review_decision"] = disposition["decision"]
        queue.append(review_row)
    queue.sort(key=lambda row: (str(row["official_regulatory_category"]), -(parse_number(row["official_capacity_mw"]) or 0)))
    return queue


def build_overlay(
    local_rows: list[dict[str, Any]],
    official_rows: list[dict[str, Any]],
    aliases: dict[str, dict[str, str]],
    dispositions: dict[tuple[str, str, str, str], dict[str, str]] | None = None,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    hydro_official = [row for row in official_rows if row.get("technology") == "hydro"]
    matches, match_meta = match_local_records(local_rows, hydro_official, aliases)
    overlay: list[dict[str, Any]] = []
    for local_index, local in enumerate(local_rows):
        matched = [hydro_official[index] for index in matches.get(local_index, [])]
        overlay.append(overlay_row(local, matched, match_meta.get(local_index)))
    matched_official = {index for indexes in matches.values() for index in indexes}
    review = build_review_queue(local_rows, hydro_official, matched_official, dispositions)
    rejected_review_rows = sum(str(row["review_decision"]).startswith("rejected_") for row in review)
    summary = {
        "schema_version": 1,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "scope": "Local map crosswalk to official DoED records; generation licences are not construction evidence.",
        "local_rows": len(local_rows),
        "official_hydro_rows": len(hydro_official),
        "matched_local_rows": sum(row["match_status"] != "unmatched" for row in overlay),
        "exact_local_rows": sum(row["match_status"] == "exact" for row in overlay),
        "alias_local_rows": sum(row["match_status"] == "alias" for row in overlay),
        "unmatched_local_rows": sum(row["match_status"] == "unmatched" for row in overlay),
        "operating_local_rows": sum(row["doed_delivery_status"] == "operating" for row in overlay),
        "mixed_record_status_rows": sum(row["doed_record_status"] == "mixed" for row in overlay),
        "review_rows": len(review),
        "unreviewed_rows": len(review) - rejected_review_rows,
        "rejected_suggestion_rows": rejected_review_rows,
        "primary_category_counts": dict(
            sorted(Counter(row["doed_primary_category"] or "unmatched" for row in overlay).items())
        ),
    }
    return overlay, review, summary


def write_csv(path: Path, rows: list[dict[str, Any]], fields: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--local-points", type=Path, default=DEFAULT_LOCAL_POINTS)
    parser.add_argument("--doed-registry", type=Path, default=DEFAULT_DOED_REGISTRY)
    parser.add_argument("--aliases", type=Path, default=DEFAULT_ALIASES)
    parser.add_argument("--review-dispositions", type=Path, default=DEFAULT_REVIEW_DISPOSITIONS)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--no-write", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    local_path = args.local_points.expanduser().resolve()
    official_path = args.doed_registry.expanduser().resolve()
    local_rows = geojson_properties(load_json(local_path), str(local_path))
    official_rows = load_csv(official_path)
    aliases = load_aliases(args.aliases.expanduser().resolve())
    dispositions = load_review_dispositions(args.review_dispositions.expanduser().resolve())
    overlay, review, summary = build_overlay(local_rows, official_rows, aliases, dispositions)
    if args.no_write:
        print(json.dumps(summary, indent=2))
    else:
        output_dir = args.output_dir.expanduser().resolve()
        output_dir.mkdir(parents=True, exist_ok=True)
        write_csv(output_dir / OVERLAY_NAME, overlay, OVERLAY_FIELDS)
        write_csv(output_dir / REVIEW_NAME, review, REVIEW_FIELDS)
        (output_dir / SUMMARY_NAME).write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
        print(
            f"Wrote overlay for {len(overlay)} local projects; "
            f"{summary['unreviewed_rows']} of {len(review)} priority official rows need review"
        )
        print(json.dumps(summary, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
