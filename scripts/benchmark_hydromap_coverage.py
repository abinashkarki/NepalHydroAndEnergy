#!/usr/bin/env python3
"""Benchmark local Nepal Energy registries against HydroMap Nepal.

This command is intentionally comparison-only. It does not copy HydroMap's
source dataset into the repository and never mutates local source registries.
It emits derived metrics and conservative manual-review queues.

Examples:
    python scripts/benchmark_hydromap_coverage.py
    python scripts/benchmark_hydromap_coverage.py --hydromap-source snapshot.json
    python scripts/benchmark_hydromap_coverage.py --no-write
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import re
import unicodedata
from collections import Counter, defaultdict
from datetime import datetime, timezone
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any, Iterable
from urllib.parse import urlparse
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_HYDROMAP_SOURCE = "https://hydromapnepal.com/data/hydropower-projects.json"
DEFAULT_HYDRO_POINTS = ROOT / "data" / "processed" / "maps" / "hydropower_project_display_points.geojson"
DEFAULT_SOLAR_PLANTS = ROOT / "data" / "processed" / "maps" / "solar_plants.geojson"
DEFAULT_PROJECT_SPECS = ROOT / "data" / "project_specs.csv"
DEFAULT_OUTPUT_DIR = ROOT / "data" / "processed" / "tables"

SUMMARY_NAME = "hydromap_coverage_summary.json"
ACTIVE_REVIEW_NAME = "hydromap_active_review_queue.csv"
CONFLICTS_NAME = "hydromap_capacity_conflicts.csv"
UNMATCHED_NAME = "hydromap_local_unmatched.csv"
SPECS_REVIEW_NAME = "hydromap_curated_specs_review.csv"

CAPACITY_TOLERANCE_MW = 0.01
GENERIC_PROJECT_TERMS = re.compile(
    r"\b(hydroelectric|hydro-electric|hydropower|hydro power|project|hpp|hep|hp|shp|power plant|scheme)\b",
    flags=re.IGNORECASE,
)
SOLAR_TERMS = re.compile(r"\b(solar|photovoltaic|pv|saurya)\b", flags=re.IGNORECASE)
WIND_TERMS = re.compile(r"\b(wind|bayu)\b", flags=re.IGNORECASE)

ACTIVE_REVIEW_FIELDS = [
    "external_name",
    "external_capacity_mw",
    "external_category",
    "external_river",
    "external_license_no",
    "suggested_local_name",
    "suggested_local_capacity_mw",
    "suggested_local_license_type",
    "name_similarity",
    "river_similarity",
    "capacity_similarity",
    "combined_similarity",
    "review_status",
]
CONFLICT_FIELDS = [
    "normalized_name",
    "local_name",
    "external_name",
    "local_capacity_mw",
    "external_capacity_mw",
    "absolute_difference_mw",
    "local_license_type",
    "external_category",
    "local_river",
    "external_river",
]
UNMATCHED_FIELDS = [
    "local_name",
    "local_capacity_mw",
    "local_license_type",
    "local_river",
    "reason",
    "candidate_count",
    "candidate_names",
]
SPECS_REVIEW_FIELDS = [
    "local_slug",
    "local_capacity_mw",
    "local_status",
    "local_river",
    "suggested_external_name",
    "suggested_external_capacity_mw",
    "suggested_external_category",
    "suggested_external_river",
    "name_similarity",
    "river_similarity",
    "capacity_similarity",
    "combined_similarity",
    "review_status",
]


def parse_number(value: Any) -> float | None:
    """Parse a numeric value without silently treating malformed data as zero."""
    if value is None or isinstance(value, bool):
        return None
    try:
        return float(str(value).replace(",", "").strip())
    except (TypeError, ValueError):
        return None


def canonical_project_name(value: Any) -> str:
    """Return a conservative ASCII comparison key for a project name."""
    text = unicodedata.normalize("NFKD", str(value or ""))
    text = text.encode("ascii", "ignore").decode("ascii").casefold().replace("&", " and ")
    text = GENERIC_PROJECT_TERMS.sub(" ", text)
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return " ".join(text.split())


def similarity(left: Any, right: Any) -> float:
    """Return a deterministic review-only similarity score."""
    return SequenceMatcher(None, canonical_project_name(left), canonical_project_name(right)).ratio()


def capacity_similarity(left: Any, right: Any) -> float:
    a = parse_number(left)
    b = parse_number(right)
    if a is None or b is None or a <= 0 or b <= 0:
        return 0.0
    return max(0.0, 1.0 - abs(a - b) / max(a, b))


def classify_energy_type(record: dict[str, Any]) -> str:
    """Separate non-hydro technologies embedded in HydroMap's combined feed."""
    name = str(record.get("name") or record.get("label_title") or "")
    river = str(record.get("river") or "")
    if river.strip().casefold() == "solar" or SOLAR_TERMS.search(name):
        return "solar"
    if river.strip().casefold() == "wind" or WIND_TERMS.search(name):
        return "wind"
    return "hydro"


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def is_url(value: str) -> bool:
    return urlparse(value).scheme in {"http", "https"}


def load_hydromap_source(source: str, timeout: float = 30.0) -> tuple[dict[str, Any], dict[str, Any]]:
    """Load a HydroMap payload from a URL or local snapshot with provenance."""
    if is_url(source):
        request = Request(source, headers={"User-Agent": "TransparentGov-HydroMap-Benchmark/1.0"})
        with urlopen(request, timeout=timeout) as response:
            raw = response.read()
            content_type = response.headers.get("Content-Type", "")
        reference = source
        source_kind = "url"
    else:
        path = Path(source).expanduser().resolve()
        raw = path.read_bytes()
        content_type = "application/json"
        reference = str(path)
        source_kind = "local_snapshot"

    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ValueError(f"HydroMap source is not valid JSON: {reference}") from exc
    if not isinstance(payload, dict) or not isinstance(payload.get("projects"), list):
        raise ValueError("HydroMap source must be an object containing a projects list")
    return payload, {
        "kind": source_kind,
        "reference": reference,
        "sha256": sha256_bytes(raw),
        "bytes": len(raw),
        "content_type": content_type,
    }


def load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(payload, dict):
        raise ValueError(f"Expected a JSON object: {path}")
    return payload


def load_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def geojson_properties(payload: dict[str, Any], path_label: str) -> list[dict[str, Any]]:
    features = payload.get("features")
    if not isinstance(features, list):
        raise ValueError(f"Expected a GeoJSON FeatureCollection: {path_label}")
    rows: list[dict[str, Any]] = []
    for feature in features:
        if isinstance(feature, dict) and isinstance(feature.get("properties"), dict):
            rows.append(dict(feature["properties"]))
    return rows


def sum_capacity(rows: Iterable[dict[str, Any]], key: str) -> float:
    return round(sum(parse_number(row.get(key)) or 0.0 for row in rows), 3)


def grouped_counts(rows: list[dict[str, Any]], group_key: str, capacity_key: str) -> dict[str, Any]:
    result: dict[str, Any] = {}
    values = sorted({str(row.get(group_key) or "unknown") for row in rows})
    for value in values:
        group = [row for row in rows if str(row.get(group_key) or "unknown") == value]
        result[value] = {"rows": len(group), "capacity_mw": sum_capacity(group, capacity_key)}
    return result


def duplicate_summary(rows: list[dict[str, Any]], name_key: str) -> dict[str, int]:
    counts = Counter(canonical_project_name(row.get(name_key)) for row in rows)
    counts.pop("", None)
    return {
        "normalized_name_groups": sum(1 for count in counts.values() if count > 1),
        "extra_rows": sum(count - 1 for count in counts.values() if count > 1),
    }


def match_hydropower(
    local_rows: list[dict[str, Any]], external_rows: list[dict[str, Any]]
) -> dict[str, Any]:
    """Conservatively exact-match local rows to external rows."""
    external_index: dict[str, list[int]] = defaultdict(list)
    for external_index_value, row in enumerate(external_rows):
        key = canonical_project_name(row.get("name"))
        if key:
            external_index[key].append(external_index_value)

    matches: list[tuple[int, int]] = []
    ambiguous: list[tuple[int, list[int]]] = []
    unmatched: list[int] = []

    for local_index, local in enumerate(local_rows):
        key = canonical_project_name(local.get("project"))
        candidates = external_index.get(key, [])
        if len(candidates) == 1:
            matches.append((local_index, candidates[0]))
            continue
        if len(candidates) > 1:
            local_capacity = parse_number(local.get("capacity_mw"))
            capacity_matches = [
                candidate
                for candidate in candidates
                if local_capacity is not None
                and parse_number(external_rows[candidate].get("capacity")) is not None
                and abs(local_capacity - float(parse_number(external_rows[candidate]["capacity"])))
                <= CAPACITY_TOLERANCE_MW
            ]
            if len(capacity_matches) == 1:
                matches.append((local_index, capacity_matches[0]))
            else:
                ambiguous.append((local_index, candidates))
            continue
        unmatched.append(local_index)

    return {"matches": matches, "ambiguous": ambiguous, "unmatched": unmatched}


def best_suggestion(
    target: dict[str, Any],
    local_rows: list[dict[str, Any]],
    weights: tuple[float, float, float] = (0.62, 0.23, 0.15),
) -> dict[str, Any] | None:
    """Rank one local candidate for manual review without accepting it."""
    if not local_rows:
        return None
    if not math.isclose(sum(weights), 1.0):
        raise ValueError("Suggestion weights must sum to 1.0")
    name_weight, river_weight, capacity_weight = weights
    best: tuple[float, float, float, float, dict[str, Any]] | None = None
    for local in local_rows:
        name_score = similarity(target.get("name"), local.get("project"))
        river_score = similarity(target.get("river"), local.get("river"))
        capacity_score = capacity_similarity(target.get("capacity"), local.get("capacity_mw"))
        combined = name_weight * name_score + river_weight * river_score + capacity_weight * capacity_score
        candidate = (combined, name_score, river_score, capacity_score, local)
        if best is None or candidate[0] > best[0]:
            best = candidate
    if best is None:
        return None
    combined, name_score, river_score, capacity_score, local = best
    return {
        "local": local,
        "name_similarity": round(name_score, 3),
        "river_similarity": round(river_score, 3),
        "capacity_similarity": round(capacity_score, 3),
        "combined_similarity": round(combined, 3),
    }


def external_type_summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for energy_type in ("hydro", "solar", "wind"):
        selected = [row for row in rows if classify_energy_type(row) == energy_type]
        result[energy_type] = {
            "rows": len(selected),
            "capacity_mw": sum_capacity(selected, "capacity"),
            "categories": grouped_counts(selected, "category", "capacity"),
        }
    result["all"] = {"rows": len(rows), "capacity_mw": sum_capacity(rows, "capacity")}
    return result


def local_solar_summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "rows": len(rows),
        "capacity_mw": sum_capacity(rows, "capacity_mw"),
        "statuses": grouped_counts(rows, "status", "capacity_mw"),
    }


def spec_completeness(rows: list[dict[str, str]]) -> dict[str, Any]:
    if not rows:
        return {"rows": 0, "fields": 0, "overall_cell_completeness_pct": 0.0, "field_nonempty": {}}
    fields = list(rows[0])
    field_nonempty = {field: sum(bool(str(row.get(field) or "").strip()) for row in rows) for field in fields}
    filled = sum(field_nonempty.values())
    total = len(rows) * len(fields)
    return {
        "rows": len(rows),
        "fields": len(fields),
        "overall_cell_completeness_pct": round(100 * filled / total, 1) if total else 0.0,
        "field_nonempty": field_nonempty,
    }


def coordinate_distance_km(local: dict[str, Any], external: dict[str, Any]) -> float | None:
    """Compare a local reference point with the midpoint of an external licence envelope."""
    values = [parse_number(external.get(key)) for key in ("lat1", "lat2", "lon1", "lon2")]
    if any(value is None for value in values) or sum(abs(float(value)) for value in values) == 0:
        return None
    local_lat = parse_number(local.get("raw_lat"))
    local_lon = parse_number(local.get("raw_lon"))
    if local_lat is None or local_lon is None:
        return None
    lat1, lat2, lon1, lon2 = (float(value) for value in values)
    external_lat = (lat1 + lat2) / 2
    external_lon = (lon1 + lon2) / 2
    delta_lat = (local_lat - external_lat) * 111
    delta_lon = (local_lon - external_lon) * 111 * math.cos(math.radians(external_lat))
    return math.hypot(delta_lat, delta_lon)


def percentile(sorted_values: list[float], fraction: float) -> float | None:
    if not sorted_values:
        return None
    if not 0.0 <= fraction <= 1.0:
        raise ValueError("Percentile fraction must be between 0 and 1")
    position = fraction * (len(sorted_values) - 1)
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return sorted_values[lower]
    weight = position - lower
    return sorted_values[lower] * (1.0 - weight) + sorted_values[upper] * weight


def build_benchmark(
    hydromap_payload: dict[str, Any],
    local_hydro: list[dict[str, Any]],
    local_solar: list[dict[str, Any]],
    specs: list[dict[str, str]],
    provenance: dict[str, Any],
    generated_at: str,
) -> tuple[dict[str, Any], dict[str, list[dict[str, Any]]]]:
    external_all = [row for row in hydromap_payload["projects"] if isinstance(row, dict)]
    external_hydro = [row for row in external_all if classify_energy_type(row) == "hydro"]
    match_result = match_hydropower(local_hydro, external_hydro)
    matches: list[tuple[int, int]] = match_result["matches"]
    matched_external = {external_index for _, external_index in matches}

    conflicts: list[dict[str, Any]] = []
    status_crosswalk: Counter[tuple[str, str]] = Counter()
    distances: list[float] = []
    capacity_exact = 0
    for local_index, external_index in matches:
        local = local_hydro[local_index]
        external = external_hydro[external_index]
        status_crosswalk[(str(local.get("license_type") or "unknown"), str(external.get("category") or "unknown"))] += 1
        local_capacity = parse_number(local.get("capacity_mw"))
        external_capacity = parse_number(external.get("capacity"))
        if local_capacity is not None and external_capacity is not None:
            difference = abs(local_capacity - external_capacity)
            if difference <= CAPACITY_TOLERANCE_MW:
                capacity_exact += 1
            else:
                conflicts.append(
                    {
                        "normalized_name": canonical_project_name(local.get("project")),
                        "local_name": local.get("project", ""),
                        "external_name": external.get("name", ""),
                        "local_capacity_mw": local_capacity,
                        "external_capacity_mw": external_capacity,
                        "absolute_difference_mw": round(difference, 3),
                        "local_license_type": local.get("license_type", ""),
                        "external_category": external.get("category", ""),
                        "local_river": local.get("river", ""),
                        "external_river": external.get("river", ""),
                    }
                )
        distance = coordinate_distance_km(local, external)
        if distance is not None:
            distances.append(distance)

    coverage: dict[str, Any] = {}
    categories = sorted({str(row.get("category") or "unknown") for row in external_hydro})
    for category in categories:
        category_rows = [
            (index, row) for index, row in enumerate(external_hydro) if str(row.get("category") or "unknown") == category
        ]
        matched_rows = [(index, row) for index, row in category_rows if index in matched_external]
        total_mw = sum_capacity([row for _, row in category_rows], "capacity")
        matched_mw = sum_capacity([row for _, row in matched_rows], "capacity")
        coverage[category] = {
            "matched_rows": len(matched_rows),
            "total_rows": len(category_rows),
            "row_pct": round(100 * len(matched_rows) / len(category_rows), 1) if category_rows else None,
            "matched_mw": matched_mw,
            "total_mw": total_mw,
            "mw_pct": round(100 * matched_mw / total_mw, 1) if total_mw else None,
        }

    active_review: list[dict[str, Any]] = []
    for external_index, external in enumerate(external_hydro):
        if external_index in matched_external or external.get("category") not in {"operation", "construction"}:
            continue
        suggestion = best_suggestion(external, local_hydro)
        suggested = suggestion["local"] if suggestion else {}
        active_review.append(
            {
                "external_name": external.get("name", ""),
                "external_capacity_mw": parse_number(external.get("capacity")),
                "external_category": external.get("category", ""),
                "external_river": external.get("river", ""),
                "external_license_no": external.get("licenseNo", ""),
                "suggested_local_name": suggested.get("project", ""),
                "suggested_local_capacity_mw": suggested.get("capacity_mw", ""),
                "suggested_local_license_type": suggested.get("license_type", ""),
                "name_similarity": suggestion["name_similarity"] if suggestion else "",
                "river_similarity": suggestion["river_similarity"] if suggestion else "",
                "capacity_similarity": suggestion["capacity_similarity"] if suggestion else "",
                "combined_similarity": suggestion["combined_similarity"] if suggestion else "",
                "review_status": "unreviewed_no_auto_accept",
            }
        )
    active_review.sort(key=lambda row: (-(parse_number(row["external_capacity_mw"]) or 0), str(row["external_name"])))

    unmatched_rows: list[dict[str, Any]] = []
    for local_index in match_result["unmatched"]:
        local = local_hydro[local_index]
        unmatched_rows.append(
            {
                "local_name": local.get("project", ""),
                "local_capacity_mw": local.get("capacity_mw", ""),
                "local_license_type": local.get("license_type", ""),
                "local_river": local.get("river", ""),
                "reason": "no_exact_normalized_name",
                "candidate_count": 0,
                "candidate_names": "",
            }
        )
    for local_index, candidate_indexes in match_result["ambiguous"]:
        local = local_hydro[local_index]
        unmatched_rows.append(
            {
                "local_name": local.get("project", ""),
                "local_capacity_mw": local.get("capacity_mw", ""),
                "local_license_type": local.get("license_type", ""),
                "local_river": local.get("river", ""),
                "reason": "ambiguous_duplicate_normalized_name",
                "candidate_count": len(candidate_indexes),
                "candidate_names": " | ".join(str(external_hydro[index].get("name") or "") for index in candidate_indexes),
            }
        )
    unmatched_rows.sort(key=lambda row: canonical_project_name(row["local_name"]))

    specs_review: list[dict[str, Any]] = []
    for spec in specs:
        target = {
            "name": str(spec.get("slug") or "").replace("-", " "),
            "river": spec.get("river", ""),
            "capacity": spec.get("capacity_mw", ""),
        }
        suggestion = best_suggestion(
            target,
            [
                {
                    "project": row.get("name", ""),
                    "capacity_mw": row.get("capacity", ""),
                    "license_type": row.get("category", ""),
                    "river": row.get("river", ""),
                    "_external": row,
                }
                for row in external_hydro
            ],
            weights=(0.45, 0.30, 0.25),
        )
        suggested = suggestion["local"] if suggestion else {}
        external = suggested.get("_external", {}) if isinstance(suggested, dict) else {}
        specs_review.append(
            {
                "local_slug": spec.get("slug", ""),
                "local_capacity_mw": spec.get("capacity_mw", ""),
                "local_status": spec.get("status", ""),
                "local_river": spec.get("river", ""),
                "suggested_external_name": external.get("name", ""),
                "suggested_external_capacity_mw": external.get("capacity", ""),
                "suggested_external_category": external.get("category", ""),
                "suggested_external_river": external.get("river", ""),
                "name_similarity": suggestion["name_similarity"] if suggestion else "",
                "river_similarity": suggestion["river_similarity"] if suggestion else "",
                "capacity_similarity": suggestion["capacity_similarity"] if suggestion else "",
                "combined_similarity": suggestion["combined_similarity"] if suggestion else "",
                "review_status": "unreviewed_no_auto_accept",
            }
        )

    license_counts = Counter(str(row.get("licenseNo") or "").strip() for row in external_all)
    license_counts.pop("", None)
    zero_coordinate_rows = sum(
        all((parse_number(row.get(key)) or 0.0) == 0 for key in ("lat1", "lat2", "lon1", "lon2"))
        for row in external_all
    )
    distances.sort()
    summary = {
        "schema_version": 1,
        "generated_at": generated_at,
        "scope": {
            "purpose": "comparison benchmark and manual review; not a source-data mirror",
            "production_source_guidance": "Prefer current Department of Electricity Development records for publishable facts.",
            "hydromap_rights_notice": "HydroMap's public page states Copyright. All Rights Reserved.",
        },
        "methodology": {
            "match_rule": "Exact conservative normalized name; duplicate names disambiguated only by capacity within 0.01 MW.",
            "normalization": "Unicode NFKD, ASCII fold, casefold, punctuation collapse, generic HEP/HPP/project terms removed; positional, storage, cascade, and number tokens retained.",
            "suggestions": "Similarity scores are review-only and never auto-accepted.",
            "capacity_warning": "Licence, application, study, cancelled, construction, and operating MW are not interchangeable or additive delivery forecasts.",
            "coverage_interpretation": "Zero matches for studied or cancelled categories indicate different registry scope, not necessarily missing active projects.",
            "coordinate_comparison": "Distances compare local registry reference points with the midpoint of HydroMap lat1/lat2/lon1/lon2 licence envelopes; neither is asserted to be a physical facility coordinate.",
        },
        "provenance": provenance,
        "hydromap_snapshot": {
            "declared_total": hydromap_payload.get("total"),
            "rows_loaded": len(external_all),
            "last_updated": hydromap_payload.get("last_updated"),
            "last_updated_display": hydromap_payload.get("last_updated_display"),
        },
        "external": external_type_summary(external_all),
        "local": {
            "hydro": {
                "rows": len(local_hydro),
                "capacity_mw": sum_capacity(local_hydro, "capacity_mw"),
                "license_types": grouped_counts(local_hydro, "license_type", "capacity_mw"),
            },
            "solar": local_solar_summary(local_solar),
        },
        "matching": {
            "local_exact_rows": len(matches),
            "external_unique_records": len(matched_external),
            "ambiguous_local_rows": len(match_result["ambiguous"]),
            "unmatched_local_rows": len(match_result["unmatched"]),
            "active_review_rows": len(active_review),
            "active_review_scope": {
                "external_categories": ["construction", "operation"],
                "excludes": [
                    "app_const",
                    "app_survey",
                    "basket_cancel",
                    "gon_studied",
                    "gon_under_study",
                    "survey",
                ],
                "reason": "Prioritize current delivery-stage reconciliation; regulatory-universe categories remain visible in category_coverage.",
            },
            "capacity_exact_rows": capacity_exact,
            "capacity_conflict_rows": len(conflicts),
            "category_coverage": coverage,
            "status_crosswalk": {
                f"{local_status} -> {external_status}": count
                for (local_status, external_status), count in sorted(status_crosswalk.items())
            },
            "coordinate_envelope_midpoint_distance_km": {
                "n": len(distances),
                "median": round(percentile(distances, 0.5) or 0.0, 4) if distances else None,
                "p90": round(percentile(distances, 0.9) or 0.0, 4) if distances else None,
                "max": round(max(distances), 4) if distances else None,
            },
        },
        "quality": {
            "external_duplicates": duplicate_summary(external_all, "name"),
            "local_duplicates": duplicate_summary(local_hydro, "project"),
            "external_duplicate_nonempty_license_keys": sum(1 for count in license_counts.values() if count > 1),
            "external_zero_coordinate_rows": zero_coordinate_rows,
        },
        "specs": {
            **spec_completeness(specs),
            "map_rows_enriched_with_curated_status": sum(bool(row.get("status")) for row in local_hydro),
        },
    }
    tables = {
        ACTIVE_REVIEW_NAME: active_review,
        CONFLICTS_NAME: sorted(conflicts, key=lambda row: (-float(row["absolute_difference_mw"]), row["local_name"])),
        UNMATCHED_NAME: unmatched_rows,
        SPECS_REVIEW_NAME: specs_review,
    }
    return summary, tables


def output_paths(output_dir: Path) -> dict[str, Path]:
    return {
        SUMMARY_NAME: output_dir / SUMMARY_NAME,
        ACTIVE_REVIEW_NAME: output_dir / ACTIVE_REVIEW_NAME,
        CONFLICTS_NAME: output_dir / CONFLICTS_NAME,
        UNMATCHED_NAME: output_dir / UNMATCHED_NAME,
        SPECS_REVIEW_NAME: output_dir / SPECS_REVIEW_NAME,
    }


def validate_output_paths(inputs: Iterable[Path], outputs: Iterable[Path]) -> None:
    input_paths = {path.expanduser().resolve() for path in inputs}
    output_list = [path.expanduser().resolve() for path in outputs]
    if len(output_list) != len(set(output_list)):
        raise ValueError("Output paths must be distinct")
    overlap = input_paths.intersection(output_list)
    if overlap:
        raise ValueError(f"Refusing to overwrite input path: {sorted(str(path) for path in overlap)[0]}")


def provenance_path(path: Path) -> str:
    """Prefer stable repository-relative paths in checked-in reports."""
    resolved = path.expanduser().resolve()
    try:
        return str(resolved.relative_to(ROOT))
    except ValueError:
        return str(resolved)


def write_csv_rows(path: Path, rows: list[dict[str, Any]], fields: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def write_outputs(output_dir: Path, summary: dict[str, Any], tables: dict[str, list[dict[str, Any]]]) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    paths = output_paths(output_dir)
    paths[SUMMARY_NAME].write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    write_csv_rows(paths[ACTIVE_REVIEW_NAME], tables[ACTIVE_REVIEW_NAME], ACTIVE_REVIEW_FIELDS)
    write_csv_rows(paths[CONFLICTS_NAME], tables[CONFLICTS_NAME], CONFLICT_FIELDS)
    write_csv_rows(paths[UNMATCHED_NAME], tables[UNMATCHED_NAME], UNMATCHED_FIELDS)
    write_csv_rows(paths[SPECS_REVIEW_NAME], tables[SPECS_REVIEW_NAME], SPECS_REVIEW_FIELDS)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--hydromap-source", default=DEFAULT_HYDROMAP_SOURCE, help="HydroMap JSON URL or local snapshot")
    parser.add_argument("--hydropower-points", type=Path, default=DEFAULT_HYDRO_POINTS)
    parser.add_argument("--solar-plants", type=Path, default=DEFAULT_SOLAR_PLANTS)
    parser.add_argument("--project-specs", type=Path, default=DEFAULT_PROJECT_SPECS)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--timeout", type=float, default=30.0)
    parser.add_argument("--no-write", action="store_true", help="Print the summary JSON without writing artifacts")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    hydro_points = args.hydropower_points.expanduser().resolve()
    solar_plants = args.solar_plants.expanduser().resolve()
    project_specs = args.project_specs.expanduser().resolve()
    output_dir = args.output_dir.expanduser().resolve()
    outputs = output_paths(output_dir)
    local_inputs = [hydro_points, solar_plants, project_specs]
    if not is_url(args.hydromap_source):
        local_inputs.append(Path(args.hydromap_source).expanduser().resolve())
    validate_output_paths(local_inputs, outputs.values())

    hydromap_payload, hydromap_provenance = load_hydromap_source(args.hydromap_source, timeout=args.timeout)
    hydro_payload = load_json(hydro_points)
    solar_payload = load_json(solar_plants)
    specs = load_csv(project_specs)
    provenance = {
        "hydromap": hydromap_provenance,
        "local_hydropower_points": {"path": provenance_path(hydro_points), "sha256": sha256_file(hydro_points)},
        "local_solar_plants": {"path": provenance_path(solar_plants), "sha256": sha256_file(solar_plants)},
        "local_project_specs": {"path": provenance_path(project_specs), "sha256": sha256_file(project_specs)},
    }
    generated_at = datetime.now(timezone.utc).isoformat()
    summary, tables = build_benchmark(
        hydromap_payload,
        geojson_properties(hydro_payload, str(hydro_points)),
        geojson_properties(solar_payload, str(solar_plants)),
        specs,
        provenance,
        generated_at,
    )
    if args.no_write:
        print(json.dumps(summary, indent=2, ensure_ascii=False))
    else:
        write_outputs(output_dir, summary, tables)
        print(f"Wrote {len(outputs)} benchmark artifacts to {output_dir}")
        print(
            "HydroMap hydro rows: "
            f"{summary['external']['hydro']['rows']} | local hydro rows: {summary['local']['hydro']['rows']} | "
            f"exact local matches: {summary['matching']['local_exact_rows']} | "
            f"active review: {summary['matching']['active_review_rows']}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
