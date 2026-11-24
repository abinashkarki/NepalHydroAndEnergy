#!/usr/bin/env python3
"""Build lightweight Explorer GeoJSON layers for the energy-infrastructure registries.

Outputs (data/processed/maps/):
  grid_substations.geojson          data/substation_specs.csv rows with coordinates
  industrial_load_anchors.geojson   data/industrial_load_anchors.csv rows with coordinates
  fossil_infrastructure.geojson     NOC depot points + a SCHEMATIC Motihari-Amlekhgunj line
  non_dam_storage.geojson           data/storage_non_dam_specs.csv rows with coordinates
  doed_nonhydro_operating.geojson   DoED operating non-hydro records, plotted at the
                                    midpoint of the DoED licence coordinate envelope
                                    (a reference midpoint, NOT a facility location)

Rows without coordinates are skipped (never estimated). Run with --check to verify
the committed outputs are current.
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from build_doed_missing_operating_projects import envelope_midpoint  # noqa: E402

MAPS = ROOT / "data" / "processed" / "maps"
SUBSTATIONS = ROOT / "data" / "substation_specs.csv"
INDUSTRIAL = ROOT / "data" / "industrial_load_anchors.csv"
FOSSIL = ROOT / "data" / "fossil_infrastructure.csv"
STORAGE = ROOT / "data" / "storage_non_dam_specs.csv"
DOED_NONHYDRO = ROOT / "data" / "processed" / "tables" / "doed_nonhydro_registry.csv"

OUTPUTS = {
    "grid_substations": MAPS / "grid_substations.geojson",
    "industrial_load_anchors": MAPS / "industrial_load_anchors.geojson",
    "fossil_infrastructure": MAPS / "fossil_infrastructure.geojson",
    "non_dam_storage": MAPS / "non_dam_storage.geojson",
    "doed_nonhydro_operating": MAPS / "doed_nonhydro_operating.geojson",
}

PRECISION_LABELS = {
    "official-map-node": "RPGCL official map substation symbol (~1 km)",
    "approximate-place": "Approximate: named town/village, not the asset footprint",
}
DOED_PRECISION = "DoED licence-envelope reference midpoint; not a facility location"

# Indian terminal of the Motihari-Amlekhgunj pipeline. The OSM Nepal extract does not
# cover India; this is the Nominatim result for "Motihari, Bihar, India" (OSM way
# 22826540, place=city), queried 2026-11-25. City-level only.
MOTIHARI = {"lat": 26.6506888, "lon": 84.9114654, "basis": "Nominatim/OSM way 22826540 (Motihari city, place-level)"}

STATUS_DISPLAY = {
    "operating": "Operating",
    "under-construction": "Under construction",
    "planned": "Planned",
    "partially-operational": "Partially operational",
}
DOED_TECH_LABEL = {"solar": "Solar", "wind": "Wind", "thermal": "Thermal", "cogeneration": "Cogeneration",
                   "biomass": "Biomass"}
NEPAL_BBOX = (80.0, 26.0, 88.3, 30.6)


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def num(value: str | None) -> float | None:
    try:
        text = (value or "").strip()
        return float(text) if text else None
    except ValueError:
        return None


def point(row: dict[str, str]) -> list[float] | None:
    lat, lon = num(row.get("latitude")), num(row.get("longitude"))
    if lat is None or lon is None:
        return None
    return [round(lon, 6), round(lat, 6)]


def clean(props: dict[str, Any]) -> dict[str, Any]:
    return {k: v for k, v in props.items() if v not in (None, "")}


def feature(geometry: dict[str, Any], props: dict[str, Any]) -> dict[str, Any]:
    return {"type": "Feature", "geometry": geometry, "properties": clean(props)}


def collection(name: str, features: list[dict[str, Any]], note: str) -> dict[str, Any]:
    return {"type": "FeatureCollection", "name": name, "note": note, "features": features}


def build_substations() -> dict[str, Any]:
    feats = []
    for row in read_rows(SUBSTATIONS):
        coords = point(row)
        if not coords:
            continue
        kv = row["highest_voltage_kv"]
        status = row["status"]
        feats.append(feature({"type": "Point", "coordinates": coords}, {
            "id": row["slug"],
            "name": f"{row['substation_name']} substation",
            "label_title": f"{row['substation_name']} · {kv} kV",
            "highest_voltage_kv": int(kv),
            "voltage_class": f"{kv} kV",
            "voltage_ratios": row.get("voltage_ratios", "").replace(";", ", "),
            "installed_mva": num(row.get("installed_mva")),
            "planned_additional_mva": num(row.get("planned_additional_mva")),
            "status": status,
            "status_display": STATUS_DISPLAY.get(status, status),
            "status_as_of": row.get("status_as_of"),
            "district": row.get("district"),
            "province": row.get("province"),
            "owner": row.get("owner"),
            "linked_solar_award_mw": num(row.get("linked_solar_award_mw")),
            "cross_border_link": row.get("cross_border_link"),
            "coordinate_precision": row.get("coordinate_precision"),
            "precision_label": PRECISION_LABELS.get(row.get("coordinate_precision", ""), ""),
            "source_slug": row.get("source_slug"),
            "source_locator": row.get("source_locator"),
        }))
    return collection("grid_substations", feats,
                      "From data/substation_specs.csv; only rows with recorded coordinates. "
                      "coordinate_precision distinguishes official map symbols from place-level matches.")


def build_industrial() -> dict[str, Any]:
    feats = []
    for row in read_rows(INDUSTRIAL):
        coords = point(row)
        if not coords:
            continue
        feats.append(feature({"type": "Point", "coordinates": coords}, {
            "id": row["anchor_id"],
            "name": row["anchor_name"],
            "label_title": row["anchor_name"],
            "anchor_type": row["anchor_type"].replace("_", " "),
            "district": row.get("district"),
            "province": row.get("province"),
            "nearest_substation_name": row.get("nearest_substation_name"),
            "substation_slug": row.get("substation_slug"),
            "supply_voltage_kv": num(row.get("supply_voltage_kv")),
            "grid_project_reference": row.get("grid_project_reference"),
            "project_status_as_reported": row.get("project_status_as_reported"),
            "evidence_status": row.get("evidence_status"),
            "coordinate_precision": row.get("coordinate_precision"),
            "precision_label": PRECISION_LABELS.get(row.get("coordinate_precision", ""), ""),
            "source_slug": row.get("source_slug"),
            "source_url": row.get("source_url"),
        }))
    return collection("industrial_load_anchors", feats,
                      "From data/industrial_load_anchors.csv; place-level points for named industrial areas.")


def build_fossil() -> dict[str, Any]:
    feats = []
    for row in read_rows(FOSSIL):
        coords = point(row)
        if not coords:
            continue
        if row["asset_id"] == "pipeline-motihari-amlekhgunj":
            feats.append(feature(
                {"type": "LineString", "coordinates": [[round(MOTIHARI["lon"], 6), round(MOTIHARI["lat"], 6)], coords]},
                {
                    "id": row["asset_id"],
                    "name": row["asset_name"],
                    "label_title": f"{row['asset_name']} (schematic)",
                    "geometry_kind": "pipeline",
                    "geometry_note": "SCHEMATIC straight line between the Motihari (India) and Amlekhgunj (Nepal) "
                                     "terminals; not the surveyed pipeline alignment",
                    "asset_type": row["asset_type"],
                    "status": row["status"],
                    "length_km": num(row.get("length_km")),
                    "design_capacity": f"{row['design_capacity']} {row['design_capacity_unit']}".strip(),
                    "endpoint_basis": f"Motihari: {MOTIHARI['basis']}; Amlekhgunj: see data/fossil_infrastructure.csv notes",
                    "source_slug": row.get("source_slug"),
                    "source_url": row.get("source_url"),
                },
            ))
            continue
        if row.get("asset_type", "").startswith("pipeline"):
            continue
        feats.append(feature({"type": "Point", "coordinates": coords}, {
            "id": row["asset_id"],
            "name": row["asset_name"],
            "label_title": row["asset_name"],
            "geometry_kind": "depot",
            "asset_type": row["asset_type"],
            "location": row.get("location"),
            "ms_storage_kl": num(row.get("ms_storage")),
            "sko_storage_kl": num(row.get("sko_storage")),
            "atf_storage_kl": num(row.get("atf_storage")),
            "storage_unit": row.get("storage_unit"),
            "storage_as_of": row.get("storage_as_of"),
            "coordinate_precision": row.get("coordinate_precision"),
            "precision_label": PRECISION_LABELS.get(row.get("coordinate_precision", ""), ""),
            "source_slug": row.get("source_slug"),
            "source_locator": row.get("source_locator"),
        }))
    return collection("fossil_infrastructure", feats,
                      "NOC depots (town-level points from WECS Table 4.4 names) and a schematic "
                      "Motihari-Amlekhgunj pipeline line. Line geometry is not the real alignment.")


def build_storage() -> dict[str, Any]:
    feats = []
    for row in read_rows(STORAGE):
        coords = point(row)
        if not coords:
            continue
        feats.append(feature({"type": "Point", "coordinates": coords}, {
            "id": row["slug"],
            "name": row["project_name"],
            "label_title": row["project_name"],
            "technology": row["technology"],
            "power_mw": num(row.get("power_mw")),
            "energy_mwh": num(row.get("energy_mwh")),
            "status": row["status"],
            "site": row.get("substation_or_site"),
            "province": row.get("province"),
            "developer_or_agency": row.get("developer_or_agency"),
            "coordinate_precision": row.get("coordinate_precision"),
            "precision_label": PRECISION_LABELS.get(row.get("coordinate_precision", ""), ""),
            "source_url": row.get("source_url"),
            "source_locator": row.get("source_locator"),
        }))
    return collection("non_dam_storage", feats,
                      "From data/storage_non_dam_specs.csv; only rows whose source names a single mappable site.")


def build_doed_nonhydro() -> dict[str, Any]:
    feats = []
    for row in read_rows(DOED_NONHYDRO):
        if row.get("regulatory_category") != "operating":
            continue
        mid = envelope_midpoint(row)
        if not mid:
            continue
        lat, lon = mid
        if not (NEPAL_BBOX[0] <= lon <= NEPAL_BBOX[2] and NEPAL_BBOX[1] <= lat <= NEPAL_BBOX[3]):
            continue
        tech = row["technology"]
        feats.append(feature({"type": "Point", "coordinates": [round(lon, 6), round(lat, 6)]}, {
            "id": row["record_id"],
            "project": row["project"],
            "label_title": f"{row['project']} — reference midpoint, not a facility location",
            "technology": DOED_TECH_LABEL.get(tech, tech),
            "capacity_mw": num(row.get("capacity_mw")),
            "delivery_status": "Operating (DoED register)",
            "location_text": row.get("location_text"),
            "promoter": row.get("promoter"),
            "cod_date_bs": row.get("cod_date_bs"),
            "coordinate_precision": DOED_PRECISION,
            "source_authority": "Nepal Department of Electricity Development",
            "source_url": row.get("source_url"),
            "source_updated_on": row.get("source_updated_on"),
        }))
    return collection("doed_nonhydro_operating", feats,
                      "DoED operating non-hydro records. Points are the midpoint of the DoED licence "
                      "coordinate envelope: reference midpoints, not facility locations.")


BUILDERS = {
    "grid_substations": build_substations,
    "industrial_load_anchors": build_industrial,
    "fossil_infrastructure": build_fossil,
    "non_dam_storage": build_storage,
    "doed_nonhydro_operating": build_doed_nonhydro,
}


def render(payload: dict[str, Any]) -> str:
    return json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--check", action="store_true", help="fail if committed outputs are stale")
    args = parser.parse_args(argv)
    stale = []
    for key, builder in BUILDERS.items():
        text = render(builder())
        out = OUTPUTS[key]
        if args.check:
            if not out.exists() or out.read_text(encoding="utf-8") != text:
                stale.append(str(out.relative_to(ROOT)))
            continue
        out.write_text(text, encoding="utf-8")
        print(f"wrote {out.relative_to(ROOT)} ({len(json.loads(text)['features'])} features, {len(text)} bytes)")
    if stale:
        print("stale outputs: " + ", ".join(stale), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
