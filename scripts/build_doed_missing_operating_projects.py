#!/usr/bin/env python3
"""Build a separate DoED layer for operating records absent from the local registry.

Coordinates in this artifact are reference midpoints of the DoED licence envelope.
They are not asserted facility, intake, powerhouse, or dam locations.
"""

from __future__ import annotations

import argparse
import csv
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    from .build_doed_project_status_overlay import dms_to_decimal
except ImportError:
    from build_doed_project_status_overlay import dms_to_decimal


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_REGISTRY = ROOT / "data" / "processed" / "tables" / "doed_hydropower_registry.csv"
DEFAULT_REVIEW = ROOT / "data" / "processed" / "tables" / "doed_project_crosswalk_review.csv"
DEFAULT_CSV = ROOT / "data" / "processed" / "tables" / "doed_operating_projects_missing_local.csv"
DEFAULT_GEOJSON = ROOT / "data" / "processed" / "maps" / "doed_operating_projects_missing_local.geojson"
DEFAULT_SUMMARY = ROOT / "data" / "processed" / "tables" / "doed_operating_projects_missing_local_summary.json"

CSV_FIELDS = [
    "project",
    "capacity_mw",
    "river",
    "record_number",
    "record_id",
    "source_url",
    "source_updated_on",
    "latitude_1_dms",
    "latitude_2_dms",
    "longitude_1_dms",
    "longitude_2_dms",
    "reference_latitude",
    "reference_longitude",
    "coordinate_precision",
    "local_registry_relation",
]

REFERENCE_PRECISION = "DoED licence-envelope reference midpoint; not a facility location"


def envelope_midpoint(row: dict[str, Any]) -> tuple[float, float] | None:
    values = [
        dms_to_decimal(row.get("latitude_1_dms")),
        dms_to_decimal(row.get("latitude_2_dms")),
        dms_to_decimal(row.get("longitude_1_dms")),
        dms_to_decimal(row.get("longitude_2_dms")),
    ]
    if any(value is None for value in values) or not any(values):
        return None
    lat1, lat2, lon1, lon2 = values
    assert lat1 is not None and lat2 is not None and lon1 is not None and lon2 is not None
    return round((lat1 + lat2) / 2, 6), round((lon1 + lon2) / 2, 6)


def build_missing_operating(
    registry: list[dict[str, Any]], review: list[dict[str, Any]]
) -> tuple[list[dict[str, Any]], dict[str, Any], dict[str, Any]]:
    missing_names = {
        row["official_project"]
        for row in review
        if row.get("official_regulatory_category") == "operating_record"
    }
    selected = [
        row
        for row in registry
        if row.get("technology") == "hydro"
        and row.get("regulatory_category") == "operating_record"
        and row.get("project") in missing_names
    ]
    selected.sort(key=lambda row: (-(float(row.get("capacity_mw") or 0)), str(row.get("project") or "")))

    rows: list[dict[str, Any]] = []
    features: list[dict[str, Any]] = []
    for source in selected:
        midpoint = envelope_midpoint(source)
        row = {field: source.get(field, "") for field in CSV_FIELDS}
        row.update({
            "reference_latitude": midpoint[0] if midpoint else "",
            "reference_longitude": midpoint[1] if midpoint else "",
            "coordinate_precision": REFERENCE_PRECISION if midpoint else "DoED record has no usable coordinate envelope; not mapped",
            "local_registry_relation": "official operating record unmatched to legacy Naxa/local registry",
        })
        rows.append(row)
        if midpoint:
            features.append({
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [midpoint[1], midpoint[0]]},
                "properties": {
                    **row,
                    "label_title": f"{row['project']} — reference midpoint, not a facility location",
                    "location_basis": REFERENCE_PRECISION,
                    "dataset_role": "official DoED addition; separate from legacy Naxa registry",
                    "regulatory_category": "operating_record",
                    "delivery_status": "operating",
                    "source_authority": "Department of Electricity Development (DoED), Nepal",
                },
            })

    geojson = {
        "type": "FeatureCollection",
        "name": "DoED operating projects missing from legacy local registry",
        "metadata": {
            "scope": "Official DoED operating records unmatched to the legacy Naxa/local registry.",
            "coordinate_precision": f"{REFERENCE_PRECISION}.",
            "separation": "This is an official-additions layer and must not be merged into the Naxa-derived registry without identity review.",
        },
        "features": features,
    }
    summary = {
        "schema_version": 1,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "missing_operating_records": len(rows),
        "mapped_reference_midpoints": len(features),
        "records_without_usable_coordinates": len(rows) - len(features),
        "scope": "Official DoED operating records unmatched to the legacy Naxa/local registry.",
        "coordinate_precision": f"{REFERENCE_PRECISION}.",
    }
    return rows, geojson, summary


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=CSV_FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--registry", type=Path, default=DEFAULT_REGISTRY)
    parser.add_argument("--review", type=Path, default=DEFAULT_REVIEW)
    parser.add_argument("--csv", type=Path, default=DEFAULT_CSV)
    parser.add_argument("--geojson", type=Path, default=DEFAULT_GEOJSON)
    parser.add_argument("--summary", type=Path, default=DEFAULT_SUMMARY)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    with args.registry.open(encoding="utf-8-sig", newline="") as handle:
        registry = list(csv.DictReader(handle))
    with args.review.open(encoding="utf-8-sig", newline="") as handle:
        review = list(csv.DictReader(handle))
    rows, geojson, summary = build_missing_operating(registry, review)
    write_csv(args.csv, rows)
    args.geojson.parent.mkdir(parents=True, exist_ok=True)
    args.geojson.write_text(json.dumps(geojson, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    args.summary.parent.mkdir(parents=True, exist_ok=True)
    args.summary.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
