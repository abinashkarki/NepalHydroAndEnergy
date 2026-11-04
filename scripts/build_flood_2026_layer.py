#!/usr/bin/env python3
"""Build the 26 August 2026 Bhotekoshi-Trishuli flood map layers.

Reads the hand-curated impact register (data/flood_2026_08_impact_register.csv),
the hydropower display-point registry, and HydroRIVERS-derived river linework,
then emits:

  - flood_2026_route.geojson              segmented flood-route reaches
  - flood_2026_impacts_confirmed.geojson  officially/media-confirmed damage points
  - flood_2026_impacts_watch.geojson      market-signal watch points
  - flood_2026_corridor_projects.geojson  registry projects within the corridor buffer
  - flood_2026_secondary_hazards.geojson  barrier lake and Tibet-side hazard markers
  - flood_2026_build_report.json          build stats and unmatched rows

Geometry confidence is explicit: the Tibet-side and border segments are
approximate hand alignment; the Trishuli/Narayani reaches inherit HydroRIVERS
alignment from data/processed/maps/nepal_relevant_tributaries.geojson.
"""
from __future__ import annotations

import csv
import json
from pathlib import Path

from pyproj import Transformer
from shapely.geometry import LineString, Point
from shapely.ops import transform as shp_transform

ROOT = Path(__file__).resolve().parent.parent
MAPS = ROOT / "data" / "processed" / "maps"
REGISTER = ROOT / "data" / "flood_2026_08_impact_register.csv"
POINTS = MAPS / "hydropower_project_display_points.geojson"
TRIBUTARIES = MAPS / "nepal_relevant_tributaries.geojson"

AS_OF = "2026-08-30"
EVENT_ID = "bhotekoshi-trishuli-flood-2026"

ORIGIN = (85.42, 28.35)
GYIRONG = (85.32, 28.32)
RASUWA_BORDER = (85.307, 28.244)
RASUWAGADHI_PLANT = (85.37, 28.251)
RASUWA_BHOTEKOSHI_PLANT = (85.354, 28.205)
TIMURE = (85.30, 28.20)
SYABRUBESI = (85.293, 28.146)
DHUNCHE = (85.30, 28.11)
BETRAWATI = (85.22, 27.99)
DEVIGHAT_BIDUR = (85.15, 27.92)
MUGLING = (84.55, 27.87)
NARAYANGHAT = (84.47, 27.70)
INDIA_BORDER = (83.869, 27.24)

MILESTONES = [
    ("origin-avalanche", ORIGIN, "Langtang Lirung northern slopes - ice-rock avalanche source into the Lhende Khola"),
    ("gyirong-port", GYIRONG, "Gyirong town and Gyirong Port trade hub, Tibet - six hydropower plants and port infrastructure damaged"),
    ("rasuwa-border", RASUWA_BORDER, "Rasuwagadhi border crossing"),
    ("rasuwagadhi-plant", RASUWAGADHI_PLANT, "Rasuwagadhi 111 MW plant - completely washed away (NEA)"),
    ("rasuwa-bhotekoshi-plant", RASUWA_BHOTEKOSHI_PLANT, "Rasuwagadhi Bhotekoshi 120 MW construction site - damaged"),
    ("timure", TIMURE, "Timure - settlements swept away, helipad destroyed"),
    ("syabrubesi-confluence", SYABRUBESI, "Syabrubesi - Bhote Koshi meets the Trishuli; Langtang Khola confluence; town destroyed"),
    ("dhunche", DHUNCHE, "Dhunche, Rasuwa headquarters"),
    ("betrawati", BETRAWATI, "Betrawati"),
    ("devighat-bidur", DEVIGHAT_BIDUR, "Devighat, Trisuli Bazar and Bidur (Nuwakot) - Trishuli, Devighat plants and Bidur solar"),
    ("mugling", MUGLING, "Mugling - Trishuli-Marsyangdi confluence; Prithvi Highway severed at Krishnabhir downstream"),
    ("narayanghat", NARAYANGHAT, "Narayanghat and Devghat, Chitwan"),
    ("india-border", INDIA_BORDER, "Narayani (Gandak) at the India border near the Valmikinagar barrage"),
]

REACH_NOTES = {
    "origin-avalanche->gyirong-port": "Approximate hand alignment. Reuters-cited scientists describe a massive ice-rock avalanche on the northern slopes of Langtang Lirung into the Lhende Khola on the Tibetan side; cause analysis still under way as of 2026-08-30.",
    "gyirong-port->rasuwa-border": "Approximate hand alignment. Chinese state media reported damage at Gyirong Port and to hydropower infrastructure; 261 foreign nationals including 104 Nepalis were reported missing on the Tibetan side.",
    "rasuwa-border->rasuwagadhi-plant": "Approximate hand alignment anchored on confirmed damage. The flood path through the Lende valley passes the Rasuwagadhi plant, which NEA reports as completely washed away.",
    "rasuwagadhi-plant->rasuwa-bhotekoshi-plant": "Approximate hand alignment anchored on confirmed damage at the Rasuwagadhi Bhotekoshi 120 MW construction site.",
    "rasuwa-bhotekoshi-plant->timure": "Approximate hand alignment. Timure settlements were swept away and the rescue helipad was destroyed.",
    "timure->syabrubesi-confluence": "Approximate hand alignment. Timure-Syabrubesi markets and hydropower works destroyed; a new barrier lake formed upstream near the Chhochen Khola-Purepu Tsangpo confluence.",
    "syabrubesi-confluence->dhunche": "HydroRIVERS alignment. Corridor reach containing Chilime (buried) and the Langtang Khola and Sanjen side valleys.",
    "dhunche->betrawati": "HydroRIVERS alignment. Upper Trishuli-1 (216 MW, damaged) and Upper Trishuli 3A (60 MW, workers trapped in underground powerhouse).",
    "betrawati->devighat-bidur": "HydroRIVERS alignment. Upper Trishuli 3B site turned into a riverbed; Trishuli and Devighat plants damaged; Bidur 25 MWp solar substation inundated.",
    "devighat-bidur->mugling": "HydroRIVERS alignment. Prithvi Highway collapsed at Krishnabhir on 30 August, severing the Muglin-Kathmandu section as the Trishuli eroded the road base.",
    "mugling->narayanghat": "HydroRIVERS alignment. Trishuli becomes the Narayani below the Marsyangdi confluence.",
    "narayanghat->india-border": "HydroRIVERS alignment. Highest body-recovery counts downstream (Chitwan 259, Nawalparasi East and West 266) and channel changes reported more than 100 km from the source.",
}

HAND_COORDS = {
    "Bidur / Trishuli 25 MWp Solar Farm": (85.145, 27.918),
}

SECONDARY_HAZARDS = [
    {
        "name": "Barrier lake (Chhochen Khola - Purepu Tsangpo confluence)",
        "hazard": "landslide-dam-barrier-lake",
        "lon": 85.28,
        "lat": 28.27,
        "description": "China MWR via CCTV/Global Times (27 Aug): lake volume about 2 million cubic metres, already overflowing, with another 3 million cubic metres expected within three days and a high breach risk. Location approximate; the same Purepu glacier system produced the 8 July 2025 GLOF.",
        "location_precision": "approximate",
    },
    {
        "name": "Gyirong Port damage cluster, Tibet",
        "hazard": "tibet-side-damage",
        "lon": 85.32,
        "lat": 28.32,
        "description": "Reuters-cited reporting: at least six major hydropower plants and infrastructure at the Gyirong Port trade hub damaged in the multi-stage hazard chain before the flood reached Nepal.",
        "location_precision": "approximate",
    },
]

TIER_LABELS = {
    "on-corridor": "On flood corridor (<= 300 m of mapped route)",
    "corridor-adjacent": "Corridor-adjacent (<= 1500 m of mapped route)",
    "near-corridor": "Near corridor (<= 3000 m of mapped route)",
}

UTM45N = Transformer.from_crs("EPSG:4326", "EPSG:32645", always_xy=True)


def to_utm(lon: float, lat: float):
    return UTM45N.transform(lon, lat)


def load_register():
    with REGISTER.open(encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def feature_by_name():
    gj = json.loads(POINTS.read_text(encoding="utf-8"))
    index = {}
    for feat in gj["features"]:
        name = (feat["properties"].get("project") or "").strip()
        if name:
            index[name] = feat
    return gj, index


def river_lines():
    gj = json.loads(TRIBUTARIES.read_text(encoding="utf-8"))
    lines = {}
    for feat in gj["features"]:
        name = feat["properties"].get("name")
        if name in ("Trishuli River", "Narayani River"):
            lines[name] = [tuple(c) for c in feat["geometry"]["coordinates"]]
    return lines


def nearest_index(line, target, start=0):
    tx, ty = to_utm(*target)
    best_i, best_d = start, None
    for i in range(start, len(line)):
        px, py = to_utm(*line[i])
        d = (px - tx) ** 2 + (py - ty) ** 2
        if best_d is None or d < best_d:
            best_i, best_d = i, d
    return best_i


def dedupe(line, min_m=60.0):
    out = [line[0]]
    for pt in line[1:]:
        px, py = to_utm(*pt)
        qx, qy = to_utm(*out[-1])
        if ((px - qx) ** 2 + (py - qy) ** 2) ** 0.5 >= min_m:
            out.append(pt)
    return out


def build_route(lines):
    hand = [ORIGIN, GYIRONG, RASUWA_BORDER, RASUWAGADHI_PLANT, RASUWA_BHOTEKOSHI_PLANT, TIMURE, SYABRUBESI]
    trishuli = lines["Trishuli River"]
    narayani = lines["Narayani River"]

    t_start = nearest_index(trishuli, SYABRUBESI)
    t_end = nearest_index(trishuli, (narayani[0][0], narayani[0][1]), start=t_start)
    combined = dedupe(hand + trishuli[t_start:t_end] + narayani)

    reach_lines = []
    prev_i = 0
    for name, coord, desc in MILESTONES:
        idx = nearest_index(combined, coord, start=prev_i)
        reach_lines.append((name, idx, desc))
        prev_i = idx
    reach_lines.append(("route-end", len(combined) - 1, "End of mapped Narayani route"))

    features = []
    for (from_ms, from_i, _), (to_ms, to_i, to_desc) in zip(reach_lines, reach_lines[1:]):
        seg = combined[from_i:to_i + 1]
        if len(seg) < 2:
            continue
        key = f"{from_ms}->{to_ms}"
        hand_part = from_i < len(hand)
        features.append({
            "type": "Feature",
            "geometry": {"type": "LineString", "coordinates": [[round(x, 5), round(y, 5)] for x, y in seg]},
            "properties": {
                "reach_id": key,
                "from": from_ms,
                "to": to_ms,
                "event": EVENT_ID,
                "event_date": "2026-08-26",
                "as_of": AS_OF,
                "description": REACH_NOTES.get(key, ""),
                "alignment": "approximate_hand" if from_i < len(hand) else "hydrorivers",
                "confidence": "approximate" if from_i < len(hand) else "high",
            },
        })
    return features


def build_impacts(register, point_index):
    confirmed, watch, unmatched = [], [], []
    for row in register:
        match = (row.get("match_name") or "").strip()
        props = {
            "project": row["project"],
            "capacity_mw": row["capacity_mw"],
            "phase": row["phase"],
            "river": row["river"],
            "district": row["district"],
            "status_tier": row["status_tier"],
            "confidence": row["confidence"],
            "impact_summary": row["impact_summary"],
            "people_note": row["people_note"],
            "sources": row["sources"],
            "event": EVENT_ID,
            "as_of": AS_OF,
        }
        hand = HAND_COORDS.get(row["project"])
        feat = point_index.get(match) if match else None
        if feat is not None:
            props["location_precision"] = feat["properties"].get("precision_label", "registry point")
            props["developer"] = feat["properties"].get("developer", "")
            coords = [feat["properties"].get("raw_lon"), feat["properties"].get("raw_lat")]
        elif hand is not None:
            props["location_precision"] = "approximate hand placement"
            coords = list(hand)
        else:
            unmatched.append(row["project"])
            continue
        target = confirmed if row["confidence"] in ("confirmed_official", "confirmed_media") else watch
        target.append({
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": [round(coords[0], 5), round(coords[1], 5)]},
            "properties": props,
        })
    return confirmed, watch, unmatched


def build_corridor(route_features, point_gj, point_index):
    route_line = LineString(
        [c for f in route_features for c in f["geometry"]["coordinates"]]
    )
    route_utm = shp_transform(lambda x, y, z=None: to_utm(x, y), route_line)
    features = []
    for feat in point_gj["features"]:
        p = feat["properties"]
        lon, lat = p.get("raw_lon"), p.get("raw_lat")
        if lon is None or lat is None:
            continue
        d = route_utm.distance(Point(*to_utm(lon, lat)))
        if d > 3000:
            continue
        tier = "on-corridor" if d <= 300 else ("corridor-adjacent" if d <= 1500 else "near-corridor")
        features.append({
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": [round(lon, 5), round(lat, 5)]},
            "properties": {
                "project": p.get("project", ""),
                "capacity_mw": p.get("capacity_mw", ""),
                "license_type": p.get("license_type", ""),
                "district": p.get("district", ""),
                "river": p.get("river", ""),
                "exposure_tier": tier,
                "exposure_label": TIER_LABELS[tier],
                "distance_to_route_m": int(round(d)),
                "event": EVENT_ID,
                "as_of": AS_OF,
            },
        })
    return features


def build_secondary_hazards():
    return [
        {
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": [h["lon"], h["lat"]]},
            "properties": {
                "name": h["name"],
                "hazard": h["hazard"],
                "description": h["description"],
                "location_precision": h["location_precision"],
                "event": EVENT_ID,
                "as_of": AS_OF,
            },
        }
        for h in SECONDARY_HAZARDS
    ]


def main():
    register = load_register()
    point_gj, point_index = feature_by_name()
    lines = river_lines()

    route = build_route(lines)
    confirmed, watch, unmatched = build_impacts(register, point_index)
    corridor = build_corridor(route, point_gj, point_index)
    hazards = build_secondary_hazards()

    outputs = {
        "flood_2026_route.geojson": {"type": "FeatureCollection", "features": route},
        "flood_2026_impacts_confirmed.geojson": {"type": "FeatureCollection", "features": confirmed},
        "flood_2026_impacts_watch.geojson": {"type": "FeatureCollection", "features": watch},
        "flood_2026_corridor_projects.geojson": {"type": "FeatureCollection", "features": corridor},
        "flood_2026_secondary_hazards.geojson": {"type": "FeatureCollection", "features": hazards},
    }
    for name, gj in outputs.items():
        (MAPS / name).write_text(json.dumps(gj, indent=1, ensure_ascii=False), encoding="utf-8")

    report = {
        "event": EVENT_ID,
        "as_of": AS_OF,
        "route_reaches": len(route),
        "route_alignment_note": "Tibet-side and border reaches are approximate hand alignment; Trishuli/Narayani reaches use HydroRIVERS linework from nepal_relevant_tributaries.geojson",
        "impacts_confirmed": len(confirmed),
        "impacts_watch": len(watch),
        "register_rows": len(register),
        "register_unmatched": unmatched,
        "corridor_projects": len(corridor),
        "corridor_tiers": {
            tier: sum(1 for f in corridor if f["properties"]["exposure_tier"] == tier)
            for tier in TIER_LABELS
        },
        "secondary_hazards": len(hazards),
    }
    (MAPS / "flood_2026_build_report.json").write_text(json.dumps(report, indent=1), encoding="utf-8")
    print(json.dumps(report, indent=1))


if __name__ == "__main__":
    main()
