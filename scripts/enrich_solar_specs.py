#!/usr/bin/env python3
"""Deterministically enrich data/solar_project_specs.csv geography/siting fields.

Fills three columns that were blank in solar V1, using only on-disk inputs and
the row's own fields. No network calls; re-running produces identical output.

* ``province`` — from the row's ``district`` via the official 77-district →
  7-province allocation (Constitution of Nepal 2015, Schedule 4; current
  province names). The display coordinate is cross-checked by point-in-polygon
  against ``data/raw/maps/nepal_provinces.geojson``; disagreements are
  recorded in the audit table, never used to override the district. The
  pre-2015 district name "Nawalparasi" spans two provinces, so it is resolved
  only when the point falls in one of the two candidates or the row's own
  substation names the Parasi (Nawalparasi West) headquarters; otherwise blank.
* ``resource_zone`` — from the district listing in the zone table of
  ``wiki/pages/data/data-nepal-solar-resource-zones.md`` (the framework that
  defines the schema enum). Districts not listed there stay blank. The
  ``solar_ghi_zones.geojson`` polygon(s) containing the point are recorded in
  the audit table as a cross-check only (those polygons do not carry sub-zone
  codes).
* ``siting_archetype`` — ``substation-adjacent`` only when the row itself
  names its interconnection substation (NEA 960 MW LoI awards with a populated
  ``substation`` field, or an operating-registry title naming a "S/S"
  substation). Everything else is ``unknown``.

``expected_annual_generation_gwh`` is deliberately untouched: no source row
publishes a figure, and a modelled value would need a capacity AC/DC basis the
sources do not give.

Outputs:
  data/solar_project_specs.csv (in place, only the three columns above)
  data/processed/tables/solar_enrichment_audit.csv
"""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path

from shapely.geometry import Point, shape

ROOT = Path(__file__).resolve().parents[1]
CSV_PATH = Path("data/solar_project_specs.csv")
PROVINCES_PATH = Path("data/raw/maps/nepal_provinces.geojson")
GHI_ZONES_PATH = Path("data/processed/maps/solar_ghi_zones.geojson")
AUDIT_PATH = Path("data/processed/tables/solar_enrichment_audit.csv")

# nepal_provinces.geojson PROVINCE code -> current official province name.
PROVINCE_CODE_NAMES = {
    1: "Koshi",
    2: "Madhesh",
    3: "Bagmati",
    4: "Gandaki",
    5: "Lumbini",
    6: "Karnali",
    7: "Sudurpashchim",
}

# Constitution of Nepal (2015), Schedule 4 district allocation. Pre-split
# district names are mapped to every province they now span.
DISTRICT_PROVINCES: dict[str, tuple[str, ...]] = {
    # Koshi
    **{d: ("Koshi",) for d in [
        "Bhojpur", "Dhankuta", "Ilam", "Jhapa", "Khotang", "Morang", "Okhaldhunga",
        "Panchthar", "Sankhuwasabha", "Solukhumbu", "Sunsari", "Taplejung",
        "Terhathum", "Udayapur"]},
    # Madhesh
    **{d: ("Madhesh",) for d in [
        "Bara", "Dhanusha", "Mahottari", "Parsa", "Rautahat", "Saptari", "Sarlahi",
        "Siraha"]},
    # Bagmati
    **{d: ("Bagmati",) for d in [
        "Bhaktapur", "Chitwan", "Dhading", "Dolakha", "Kathmandu", "Kavrepalanchok",
        "Lalitpur", "Makwanpur", "Nuwakot", "Ramechhap", "Rasuwa", "Sindhuli",
        "Sindhupalchok"]},
    # Gandaki
    **{d: ("Gandaki",) for d in [
        "Baglung", "Gorkha", "Kaski", "Lamjung", "Manang", "Mustang", "Myagdi",
        "Nawalpur", "Parbat", "Syangja", "Tanahu"]},
    # Lumbini
    **{d: ("Lumbini",) for d in [
        "Arghakhanchi", "Banke", "Bardiya", "Dang", "Gulmi", "Kapilvastu", "Parasi",
        "Palpa", "Pyuthan", "Rolpa", "Rukum East", "Rupandehi"]},
    # Karnali
    **{d: ("Karnali",) for d in [
        "Dailekh", "Dolpa", "Humla", "Jajarkot", "Jumla", "Kalikot", "Mugu",
        "Rukum West", "Salyan", "Surkhet"]},
    # Sudurpashchim
    **{d: ("Sudurpashchim",) for d in [
        "Achham", "Baitadi", "Bajhang", "Bajura", "Dadeldhura", "Darchula", "Doti",
        "Kailali", "Kanchanpur"]},
    # Pre-2015 name split into Nawalpur (Gandaki) and Parasi (Lumbini).
    "Nawalparasi": ("Lumbini", "Gandaki"),
}

DISTRICT_ALIASES = {"Kapilbastu": "Kapilvastu", "Dhanusa": "Dhanusha", "Tanahun": "Tanahu"}

# Row-field disambiguation for split districts: (district, substation) -> province.
# Parasi is the headquarters of Parasi district (Nawalparasi West), Lumbini.
SPLIT_DISTRICT_SUBSTATION_HINTS = {("Nawalparasi", "Parasi"): "Lumbini"}

# Representative-district listing from data-nepal-solar-resource-zones.md.
# Zone D lists only "upper slopes" of its districts and so is never assigned
# from a district name alone; upper/lower partial listings are likewise skipped.
ZONE_DISTRICTS: dict[str, tuple[str, ...]] = {
    "B1": ("Rautahat", "Bara", "Parsa", "Nawalparasi", "Rupandehi", "Kapilvastu"),
    "B2": ("Jhapa", "Morang", "Sunsari", "Saptari", "Siraha", "Dhanusha", "Mahottari", "Sarlahi"),
    "B3": ("Banke", "Bardiya", "Kailali", "Kanchanpur"),
    "C1": ("Kathmandu", "Lalitpur", "Bhaktapur"),
    "C2": ("Kaski", "Syangja", "Tanahu", "Gorkha", "Lamjung"),
    "C3": ("Dhankuta", "Bhojpur", "Khotang", "Okhaldhunga", "Udayapur", "Ramechhap", "Dolakha"),
    "C4": ("Palpa", "Arghakhanchi", "Gulmi", "Baglung", "Parbat", "Myagdi", "Pyuthan", "Rolpa",
           "Salyan", "Surkhet", "Dailekh"),
    "A": ("Mustang",),  # Dolpa is split between A (upper) and E (lower)
    "E": ("Bajura", "Bajhang"),
}
# The zone table lists the pre-split "Nawalparasi"; both successor districts inherit it.
ZONE_DISTRICT_ALIASES = {"Nawalpur": "Nawalparasi", "Parasi": "Nawalparasi"}

SUBSTATION_TITLE_RE = re.compile(r"\b\d+\s*kV\s+S/S\b", re.IGNORECASE)

AUDIT_FIELDS = [
    "slug",
    "district",
    "district_normalized",
    "province",
    "province_basis",
    "point_province",
    "point_province_agrees",
    "resource_zone",
    "resource_zone_basis",
    "ghi_polygon_ids",
    "siting_archetype",
    "siting_basis",
]


def load_polygons(path: Path, key) -> list[tuple[str, object]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    return [(key(f["properties"]), shape(f["geometry"])) for f in data["features"]]


def normalize_district(district: str) -> str:
    d = district.strip()
    return DISTRICT_ALIASES.get(d, d)


def derive_province(row: dict[str, str], point_provinces: list[str]) -> tuple[str, str]:
    district = normalize_district(row.get("district", ""))
    candidates = DISTRICT_PROVINCES.get(district)
    if not candidates:
        return "", "district-not-in-lookup"
    if len(candidates) == 1:
        return candidates[0], "district-lookup"
    hint = SPLIT_DISTRICT_SUBSTATION_HINTS.get((district, row.get("substation", "").strip()))
    if hint:
        return hint, "split-district-substation-hint"
    in_candidates = [p for p in point_provinces if p in candidates]
    if len(in_candidates) == 1:
        return in_candidates[0], "split-district-point-in-polygon"
    return "", "split-district-unresolved"


def derive_zone(district: str) -> tuple[str, str]:
    d = normalize_district(district)
    d = ZONE_DISTRICT_ALIASES.get(d, d)
    matches = [zone for zone, districts in ZONE_DISTRICTS.items() if d in districts]
    if len(matches) == 1:
        return matches[0], "zone-table-district-listing"
    if not matches:
        return "", "district-not-listed-in-zone-table"
    return "", "district-listed-in-multiple-zones"


def derive_siting(row: dict[str, str]) -> tuple[str, str]:
    if (
        row.get("record_kind") == "procurement-award-record"
        and row.get("procurement_stage") == "loi-awarded"
        and row.get("substation", "").strip()
    ):
        return "substation-adjacent", "loi-award-names-substation"
    if row.get("record_kind") == "operating-registry-record" and SUBSTATION_TITLE_RE.search(
        row.get("label_title", "")
    ):
        return "substation-adjacent", "registry-title-names-substation"
    return "unknown", "no-siting-evidence-in-row"


def enrich(rows: list[dict[str, str]], provinces, ghi_zones) -> list[dict[str, str]]:
    audit: list[dict[str, str]] = []
    for row in rows:
        try:
            pt = Point(float(row["longitude"]), float(row["latitude"]))
        except (KeyError, TypeError, ValueError):
            pt = None
        point_provinces = [name for name, geom in provinces if pt is not None and geom.covers(pt)]
        ghi_ids = [name for name, geom in ghi_zones if pt is not None and geom.covers(pt)]

        province, province_basis = derive_province(row, point_provinces)
        zone, zone_basis = derive_zone(row.get("district", ""))
        siting, siting_basis = derive_siting(row)
        row["province"] = province
        row["resource_zone"] = zone
        row["siting_archetype"] = siting

        audit.append({
            "slug": row["slug"],
            "district": row.get("district", ""),
            "district_normalized": normalize_district(row.get("district", "")),
            "province": province,
            "province_basis": province_basis,
            "point_province": ";".join(point_provinces),
            "point_province_agrees": "TRUE" if province and province in point_provinces else "FALSE",
            "resource_zone": zone,
            "resource_zone_basis": zone_basis,
            "ghi_polygon_ids": ";".join(ghi_ids),
            "siting_archetype": siting,
            "siting_basis": siting_basis,
        })
    return audit


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--repo-root", type=Path, default=ROOT)
    parser.add_argument("--check", action="store_true", help="exit 1 if the CSV is not already enriched")
    args = parser.parse_args()
    root = args.repo_root

    csv_path = root / CSV_PATH
    with csv_path.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        fieldnames = list(reader.fieldnames or [])
        rows = list(reader)
    before = [dict(r) for r in rows]

    provinces = load_polygons(root / PROVINCES_PATH, lambda p: PROVINCE_CODE_NAMES[int(p["PROVINCE"])])
    ghi_zones = load_polygons(root / GHI_ZONES_PATH, lambda p: p["id"])
    audit = enrich(rows, provinces, ghi_zones)

    if args.check:
        changed = sum(1 for a, b in zip(before, rows) if a != b)
        print(f"{changed} rows would change")
        return 1 if changed else 0

    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    audit_path = root / AUDIT_PATH
    audit_path.parent.mkdir(parents=True, exist_ok=True)
    with audit_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=AUDIT_FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(audit)

    n = len(rows)
    for field in ("province", "resource_zone", "siting_archetype"):
        filled = sum(1 for r in rows if r[field] and r[field] != "unknown")
        print(f"{field}: {filled}/{n} assigned")
    print(f"point/province disagreements: {sum(1 for a in audit if a['province'] and a['point_province_agrees'] == 'FALSE')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
