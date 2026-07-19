#!/usr/bin/env python3
"""Add the V1 evidence model to the canonical solar CSV.

The migration is deterministic and deliberately does not infer delivery from an
NEA letter of intent. Coordinates are copied from the existing display GeoJSON
and retain the display-anchor caveat.
"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

CSV_PATH = Path("data/solar_project_specs.csv")
MAP_PATH = Path("data/processed/maps/solar_plants.geojson")

V1_FIELDS = [
    "record_kind",
    "record_scope",
    "delivery_status",
    "regulatory_stage",
    "status_as_of",
    "operating_status",
    "capacity_basis",
    "expected_generation_basis",
    "latitude",
    "longitude",
    "municipality",
    "coordinate_precision",
    "geography_verification_status",
    "source_type",
    "source_date",
    "verified_on",
    "evidence_scope",
    "verification_status",
    "delivery_verification_note",
]


def enrich(row: dict[str, str], coordinates: dict[str, tuple[object, object]]) -> dict[str, str]:
    is_operating = row.get("is_operating", "").upper() == "TRUE"
    lon, lat = coordinates.get(row.get("feature_id", ""), ("", ""))
    row.update(
        {
            "record_kind": "operating-registry-record" if is_operating else "procurement-award-record",
            "record_scope": "grid-connected-project-or-award-row",
            "delivery_status": "operating-registry-listed" if is_operating else "award-only-delivery-unknown",
            "regulatory_stage": "operation-registry" if is_operating else "letter-of-intent-award",
            "status_as_of": "2026-01-09" if is_operating else "2024-11-12",
            "operating_status": "official-registry-listed-operating" if is_operating else "not-established-by-source",
            "capacity_basis": "source-reported-mw-ac-dc-unspecified",
            "expected_generation_basis": "not-published-in-source",
            "latitude": str(lat),
            "longitude": str(lon),
            "municipality": "",
            "coordinate_precision": row.get("precision_label", ""),
            "geography_verification_status": "display-anchor-only" if lat != "" else "missing",
            "source_type": "official-registry" if is_operating else "official-procurement-notice",
            "source_date": "2026-01-09" if is_operating else "2024-11-12",
            "verified_on": "2026-07-19",
            "evidence_scope": "operating-registry-listing" if is_operating else "award-event-only",
            "verification_status": "primary-registry-checked" if is_operating else "primary-procurement-record-checked",
            "delivery_verification_note": (
                "Listed as operating in the DoED source snapshot; no plant-output series is included."
                if is_operating
                else "NEA LoI establishes an award only; PPA, financing, construction and operation are not established."
            ),
        }
    )
    return row


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true", help="replace the canonical CSV")
    args = parser.parse_args()

    features = json.loads(MAP_PATH.read_text(encoding="utf-8"))["features"]
    coordinates = {
        feature["properties"]["id"]: tuple(feature["geometry"]["coordinates"])
        for feature in features
        if feature.get("geometry", {}).get("type") == "Point"
    }
    with CSV_PATH.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        original_fields = list(reader.fieldnames or [])
        rows = [enrich(dict(row), coordinates) for row in reader]

    fields = original_fields + [field for field in V1_FIELDS if field not in original_fields]
    print(f"Solar V1 migration: {len(rows)} records, {len(coordinates)} coordinate anchors")
    print("Delivery classes:")
    for status in sorted({row["delivery_status"] for row in rows}):
        count = sum(row["delivery_status"] == status for row in rows)
        capacity = sum(float(row["capacity_mw"] or 0) for row in rows if row["delivery_status"] == status)
        print(f"  {status}: {count} records / {capacity:.2f} MW")

    if not args.write:
        print("Dry run only; pass --write to update data/solar_project_specs.csv")
        return

    temporary = CSV_PATH.with_suffix(".csv.tmp")
    with temporary.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    temporary.replace(CSV_PATH)
    print(f"Wrote {CSV_PATH}")


if __name__ == "__main__":
    main()
