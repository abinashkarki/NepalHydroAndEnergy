#!/usr/bin/env python3
"""Build the opt-in hazard overlay from data/glof_dangerous_lakes.csv.

Output: data/processed/maps/glof_dangerous_lakes.geojson. Only lakes whose
coordinates are published by the source (here: encoded in the ICIMOD lake ID)
are mapped; rows with blank coordinates are left out. --check verifies the
committed output is current.
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LAKES = ROOT / "data" / "glof_dangerous_lakes.csv"
OUT = ROOT / "data" / "processed" / "maps" / "glof_dangerous_lakes.geojson"
LAKE_ID = re.compile(r"GL(\d{3})(\d{3})E(\d{2})(\d{3})N")
PRECISION_LABEL = {"lake-id-encoded": "ICIMOD lake-ID coordinates (0.001 deg; lake, not outlet)"}


def lake_id_coords(lake_id: str) -> tuple[float, float] | None:
    m = LAKE_ID.fullmatch(lake_id.strip())
    if not m:
        return None
    return float(f"{m.group(1)}.{m.group(2)}"), float(f"{m.group(3)}.{m.group(4)}")


def build() -> dict:
    features = []
    with LAKES.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            lat, lon = (row.get("latitude") or "").strip(), (row.get("longitude") or "").strip()
            if not lat or not lon:
                continue
            lat_f, lon_f = float(lat), float(lon)
            encoded = lake_id_coords(row["lake_id"])
            if row["coordinate_precision"] == "lake-id-encoded" and encoded != (round(lon_f, 3), round(lat_f, 3)):
                raise SystemExit(f"{row['lake_id']}: coordinates do not match the lake ID")
            name = row["lake_name"] or row["lake_id"]
            features.append({
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [lon_f, lat_f]},
                "properties": {k: v for k, v in {
                    "id": row["lake_id"],
                    "name": name,
                    "label_title": f"{name} · Rank {row['rank']} potentially dangerous glacial lake",
                    "rank": row["rank"],
                    "river_basin": row["river_basin"],
                    "sub_basin": row["sub_basin"],
                    "pdgl_earlier_identified": row["pdgl_earlier_identified"],
                    "precision_label": PRECISION_LABEL.get(row["coordinate_precision"], row["coordinate_precision"]),
                    "source_title": row["source_title"],
                    "source_locator": row["source_locator"],
                    "source_url": row["source_url"],
                }.items() if v},
            })
    return {"type": "FeatureCollection", "name": "glof_dangerous_lakes",
            "note": "ICIMOD & UNDP (2020) potentially dangerous glacial lakes in Nepal; ranks I (highest) to III.",
            "features": features}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    text = json.dumps(build(), ensure_ascii=False, separators=(",", ":")) + "\n"
    if args.check:
        if not OUT.exists() or OUT.read_text(encoding="utf-8") != text:
            print(f"stale: {OUT.relative_to(ROOT)}", file=sys.stderr)
            return 1
        return 0
    OUT.write_text(text, encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)} ({len(json.loads(text)['features'])} lakes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
