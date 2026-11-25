#!/usr/bin/env python3
"""Build the clean-industry & compute siting readiness index (observation-only).

Joins existing verified registries only — no scores, weights or estimates:

* data/substation_specs.csv       grid hubs (operating / partially operational /
                                  under-construction 400 kV and 220 kV substations)
* data/industrial_load_anchors.csv  SEZs, industrial districts/areas and corridors that
                                  link to a >=132 kV substation with coordinates
* data/erc_retail_tariffs.csv     ERC industrial 132 kV time-of-day energy rates

Ecological belt (Terai / Mid-Hill / Valley / Mountain) is a Tier B canonical lookup by
district (CBS/NPHC 2021 ecological-belt classification), tagged ``canonical-lookup``.

Outputs:
  data/clean_industry_siting_index.csv
  data/processed/maps/clean_industry_siting.geojson   (rows with coordinates only)

Run with --check to verify the committed outputs are current.
"""
from __future__ import annotations

import argparse
import csv
import io
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from enrich_canonical_geography import DISTRICT_TO_PROVINCE  # noqa: E402

SUBSTATIONS = ROOT / "data" / "substation_specs.csv"
ANCHORS = ROOT / "data" / "industrial_load_anchors.csv"
TARIFFS = ROOT / "data" / "erc_retail_tariffs.csv"
OUT_CSV = ROOT / "data" / "clean_industry_siting_index.csv"
OUT_GEOJSON = ROOT / "data" / "processed" / "maps" / "clean_industry_siting.geojson"

COLUMNS = [
    "hub_id", "hub_name", "hub_type", "substation_slug", "highest_voltage_kv", "installed_mva",
    "planned_additional_mva", "substation_status", "province", "district", "latitude", "longitude",
    "coordinate_precision", "industrial_tod_132kv_wet_offpeak_npr", "industrial_tod_132kv_dry_peak_npr",
    "linked_corridor_slugs", "linked_solar_award_mw", "climate_zone_band", "verified_readiness_notes",
    "missing_siting_data", "source_basis", "last_updated",
]

GRID_STATUSES = {"operating", "partially-operational", "under-construction"}
GRID_VOLTAGES = {"400": "400kv-grid-hub", "220": "220kv-grid-hub"}
ANCHOR_TYPES = {
    "special_economic_zone": "sez",
    "industrial_district": "industrial-estate",
    "industrial_area": "industrial-estate",
    "industrial_corridor": "industrial-corridor",
}
TARIFF_IDS = {"wet_offpeak": "tod-132-industrial-wet-off-peak", "dry_peak": "tod-132-industrial-dry-peak"}

# Tier B canonical lookup: CBS / NPHC 2021 ecological belts (16 Mountain, 21 Terai;
# the remaining 40 districts are Hill). Kathmandu Valley districts are split out as
# "Valley" because their grid, load and climate context differs from the wider hills.
MOUNTAIN = {
    "Taplejung", "Sankhuwasabha", "Solukhumbu", "Dolakha", "Sindhupalchok", "Rasuwa", "Manang", "Mustang",
    "Dolpa", "Jumla", "Kalikot", "Mugu", "Humla", "Bajura", "Bajhang", "Darchula",
}
TERAI = {
    "Jhapa", "Morang", "Sunsari", "Saptari", "Siraha", "Dhanusha", "Mahottari", "Sarlahi", "Rautahat", "Bara",
    "Parsa", "Chitwan", "Nawalparasi East", "Nawalparasi West", "Rupandehi", "Kapilvastu", "Dang", "Banke",
    "Bardiya", "Kailali", "Kanchanpur",
}
VALLEY = {"Kathmandu", "Lalitpur", "Bhaktapur"}

PRECISION_LABELS = {
    "official-map-node": "RPGCL official map substation symbol (~1 km)",
    "approximate-place": "Approximate: named town/village, not the site footprint",
}

MISSING = ("substation bay headroom and firm connection capacity; optical fibre route/topology "
           "(NDICL OPGW/ADSS network not public); feeder-level SAIDI/SAIFI and hourly reliability; "
           "land and cooling-water availability")


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def climate_band(district: str) -> str:
    if not district:
        return ""
    if district not in DISTRICT_TO_PROVINCE:
        raise SystemExit(f"FAIL: district not in canonical lookup: {district}")
    if district in MOUNTAIN:
        return "Mountain"
    if district in TERAI:
        return "Terai"
    if district in VALLEY:
        return "Valley"
    return "Mid-Hill"


def fmt(value: str) -> str:
    return (value or "").strip()


def tariff_rates() -> dict[str, str]:
    rows = {r["tariff_id"]: r for r in read_rows(TARIFFS)}
    out = {}
    for key, tid in TARIFF_IDS.items():
        if tid not in rows or not fmt(rows[tid]["energy_rate_npr_kwh"]):
            raise SystemExit(f"FAIL: ERC tariff row missing: {tid}")
        out[key] = fmt(rows[tid]["energy_rate_npr_kwh"])
        out[key + "_effective"] = fmt(rows[tid]["effective_from"])
    return out


def readiness_notes(sub: dict[str, str]) -> str:
    parts = [f"{sub['status'].replace('-', ' ')} {sub['highest_voltage_kv']} kV substation"]
    if fmt(sub["installed_mva"]):
        parts.append(f"{fmt(sub['installed_mva'])} MVA installed")
    if fmt(sub["planned_additional_mva"]):
        parts.append(f"{fmt(sub['planned_additional_mva'])} MVA planned addition")
    if fmt(sub["voltage_ratios"]):
        parts.append(f"ratios {fmt(sub['voltage_ratios'])}")
    if fmt(sub["cross_border_link"]):
        parts.append(f"cross-border link: {fmt(sub['cross_border_link'])}")
    return "; ".join(parts)


def base_row(sub: dict[str, str], rates: dict[str, str]) -> dict[str, str]:
    district = fmt(sub["district"])
    return {
        "substation_slug": sub["slug"],
        "highest_voltage_kv": fmt(sub["highest_voltage_kv"]),
        "installed_mva": fmt(sub["installed_mva"]),
        "planned_additional_mva": fmt(sub["planned_additional_mva"]),
        "substation_status": fmt(sub["status"]),
        "province": fmt(sub["province"]),
        "district": district,
        "latitude": fmt(sub["latitude"]),
        "longitude": fmt(sub["longitude"]),
        "coordinate_precision": fmt(sub["coordinate_precision"]),
        "industrial_tod_132kv_wet_offpeak_npr": rates["wet_offpeak"],
        "industrial_tod_132kv_dry_peak_npr": rates["dry_peak"],
        "linked_corridor_slugs": fmt(sub["corridor_slugs"]),
        "linked_solar_award_mw": fmt(sub["linked_solar_award_mw"]),
        "climate_zone_band": climate_band(district),
        "missing_siting_data": MISSING,
    }


def source_basis(sub: dict[str, str], extra: str = "") -> str:
    parts = [f"substation_specs.csv:{sub['slug']} ({fmt(sub['source_slug']) or 'source not recorded'})"]
    if extra:
        parts.append(extra)
    parts.append(f"erc_retail_tariffs.csv:{TARIFF_IDS['wet_offpeak']},{TARIFF_IDS['dry_peak']}")
    parts.append("climate_zone_band: canonical-lookup (CBS/NPHC 2021 ecological belt by district)")
    return "; ".join(parts)


def build_rows() -> list[dict[str, str]]:
    subs = read_rows(SUBSTATIONS)
    by_slug = {s["slug"]: s for s in subs}
    rates = tariff_rates()
    rows: list[dict[str, str]] = []

    for sub in subs:
        kv = fmt(sub["highest_voltage_kv"])
        if kv not in GRID_VOLTAGES or fmt(sub["status"]) not in GRID_STATUSES:
            continue
        row = base_row(sub, rates)
        row.update({
            "hub_id": f"grid-{sub['slug']}",
            "hub_name": fmt(sub["substation_name"]),
            "hub_type": GRID_VOLTAGES[kv],
            "verified_readiness_notes": readiness_notes(sub),
            "source_basis": source_basis(sub),
            "last_updated": fmt(sub["last_updated"]),
        })
        rows.append(row)

    for anchor in read_rows(ANCHORS):
        hub_type = ANCHOR_TYPES.get(fmt(anchor["anchor_type"]))
        if not hub_type:
            continue
        linked = None
        for slug in [s.strip() for s in anchor["substation_slug"].split(";") if s.strip()]:
            sub = by_slug.get(slug)
            if sub and fmt(sub["latitude"]) and int(float(fmt(sub["highest_voltage_kv"]) or 0)) >= 132:
                linked = sub
                break
        if not linked:
            continue
        row = base_row(linked, rates)
        # Prefer the anchor's own district/coordinates when the anchor row records them.
        if fmt(anchor["district"]):
            row["district"] = fmt(anchor["district"])
            row["province"] = fmt(anchor["province"]) or row["province"]
            row["climate_zone_band"] = climate_band(row["district"])
        if fmt(anchor["latitude"]) and fmt(anchor["longitude"]):
            row["latitude"], row["longitude"] = fmt(anchor["latitude"]), fmt(anchor["longitude"])
            row["coordinate_precision"] = fmt(anchor["coordinate_precision"])
        else:
            row["coordinate_precision"] = f"linked-substation:{row['coordinate_precision']}"
        notes = f"linked to {readiness_notes(linked)}"
        if fmt(anchor["supply_voltage_kv"]).replace(".", "", 1).isdigit():
            notes = f"reported supply voltage {fmt(anchor['supply_voltage_kv'])} kV; " + notes
        row.update({
            "hub_id": f"{hub_type}-{anchor['anchor_id']}",
            "hub_name": fmt(anchor["anchor_name"]),
            "hub_type": hub_type,
            "verified_readiness_notes": notes,
            "source_basis": source_basis(linked, f"industrial_load_anchors.csv:{anchor['anchor_id']} ({fmt(anchor['source_slug'])})"),
            "last_updated": max(fmt(linked["last_updated"]), fmt(anchor["verified_on"])),
        })
        rows.append(row)

    order = {"400kv-grid-hub": 0, "220kv-grid-hub": 1, "sez": 2, "industrial-estate": 3, "industrial-corridor": 4}
    rows.sort(key=lambda r: (order[r["hub_type"]], r["hub_name"].lower()))
    return rows


def render_csv(rows: list[dict[str, str]]) -> str:
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=COLUMNS, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return buf.getvalue()


def render_geojson(rows: list[dict[str, str]]) -> str:
    features = []
    for row in rows:
        if not (row["latitude"] and row["longitude"]):
            continue
        props = {k: row[k] for k in COLUMNS if k not in ("latitude", "longitude", "missing_siting_data", "source_basis")}
        props["label_title"] = row["hub_name"]
        props["precision_label"] = PRECISION_LABELS.get(row["coordinate_precision"].replace("linked-substation:", ""), row["coordinate_precision"])
        if row["coordinate_precision"].startswith("linked-substation:"):
            props["precision_label"] = "Plotted at the linked substation: " + props["precision_label"]
        props["status"] = row["substation_status"]
        features.append({
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": [round(float(row["longitude"]), 6), round(float(row["latitude"]), 6)]},
            "properties": props,
        })
    return json.dumps({"type": "FeatureCollection", "features": features}, ensure_ascii=False, separators=(",", ":")) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="fail if committed outputs are stale")
    args = parser.parse_args(argv)
    rows = build_rows()
    outputs = {OUT_CSV: render_csv(rows), OUT_GEOJSON: render_geojson(rows)}
    if args.check:
        stale = [p.relative_to(ROOT).as_posix() for p, text in outputs.items() if not p.exists() or p.read_text(encoding="utf-8") != text]
        if stale:
            print("FAIL: siting readiness outputs stale (run scripts/build_siting_readiness.py): " + ", ".join(stale), file=sys.stderr)
            return 1
        print(f"OK: siting readiness index current ({len(rows)} hubs)")
        return 0
    for path, text in outputs.items():
        path.write_text(text, encoding="utf-8")
    mapped = sum(1 for r in rows if r["latitude"])
    print(f"wrote {len(rows)} hubs ({mapped} mapped) to {OUT_CSV.relative_to(ROOT)} and {OUT_GEOJSON.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
