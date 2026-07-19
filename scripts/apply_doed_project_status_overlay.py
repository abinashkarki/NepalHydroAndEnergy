#!/usr/bin/env python3
"""Apply the reviewed DoED status overlay to the public hydropower point layer."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_GEOJSON = ROOT / "data" / "processed" / "maps" / "hydropower_project_display_points.geojson"
DEFAULT_OVERLAY = ROOT / "data" / "processed" / "tables" / "doed_project_status_overlay.csv"

FIELD_MAP = {
    "match_status": "doed_match_status",
    "match_confidence": "doed_match_confidence",
    "match_basis": "doed_match_basis",
}
SKIP_FIELDS = {"local_project", "local_capacity_mw", "local_license_type", "local_river"}
NUMERIC_FIELDS = {"doed_capacity_mw", "doed_capacity_difference_mw"}
DOED_FIELDS = {
    "doed_match_status", "doed_match_confidence", "doed_match_basis",
    "doed_primary_category", "doed_status_display", "doed_categories",
    "doed_record_status", "doed_license_status", "doed_study_status",
    "doed_delivery_status", "doed_capacity_mw", "doed_capacity_difference_mw",
    "doed_project_names", "doed_record_numbers", "doed_source_urls",
    "doed_source_updated_on", "doed_record_ids",
}
PUBLIC_FIELDS = {
    "doed_primary_category", "doed_status_display", "doed_delivery_status",
    "doed_source_updated_on",
}


def load_overlay(path: Path) -> dict[str, dict[str, Any]]:
    with path.open(newline="", encoding="utf-8") as handle:
        rows = csv.DictReader(handle)
        overlay: dict[str, dict[str, Any]] = {}
        for source in rows:
            project = str(source.get("local_project") or "").strip()
            if not project:
                continue
            values: dict[str, Any] = {}
            for key, value in source.items():
                if key in SKIP_FIELDS:
                    continue
                target = FIELD_MAP.get(key, key)
                text = str(value or "").strip()
                if not text:
                    continue
                if target not in PUBLIC_FIELDS:
                    continue
                if target in NUMERIC_FIELDS:
                    try:
                        values[target] = float(text)
                    except ValueError:
                        values[target] = text
                else:
                    values[target] = text
            overlay[project] = values
    return overlay


def apply_overlay(data: dict[str, Any], overlay: dict[str, dict[str, Any]]) -> tuple[int, int]:
    matched = 0
    unmatched = 0
    for feature in data.get("features", []):
        props = feature.setdefault("properties", {})
        for field in DOED_FIELDS:
            props.pop(field, None)
        project = str(props.get("project") or "")
        row = overlay.get(project)
        if row is None:
            unmatched += 1
            continue
        props.update(row)
        matched += 1
    return matched, unmatched


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--geojson", type=Path, default=DEFAULT_GEOJSON)
    parser.add_argument("--overlay", type=Path, default=DEFAULT_OVERLAY)
    args = parser.parse_args()

    data = json.loads(args.geojson.read_text(encoding="utf-8"))
    matched, unmatched = apply_overlay(data, load_overlay(args.overlay))
    args.geojson.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Applied DoED overlay to {matched} features; {unmatched} lacked overlay rows.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
