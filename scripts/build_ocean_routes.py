#!/usr/bin/env python3
"""Build Nepal-origin downstream route extensions to the Bay of Bengal.

This is intentionally lightweight: it writes only the ocean-route GeoJSON and
QA report, avoiding the heavier Folium/static-map render path in
build_tributary_maps.py.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import shapefile
from shapely.geometry import LineString, Point, shape


ROOT = Path(__file__).resolve().parent.parent
PROCESSED = ROOT / "data" / "processed" / "maps"
HYDRORIVERS_SHP = ROOT / "data" / "raw" / "maps" / "hydrorivers" / "HydroRIVERS_v10_as_shp" / "HydroRIVERS_v10_as.shp"
DOWNSTREAM_PATH = PROCESSED / "nepal_origin_downstream_systems.geojson"
OUT = PROCESSED / "nepal_origin_ocean_routes.geojson"
REPORT = PROCESSED / "downstream_ocean_route_report.json"

OCEAN_ROUTE_BOUNDS = (77.0, 20.5, 92.8, 31.8)
MAX_SNAP_KM = 5.0

ROUTE_META = {
    "koshi_system": {
        "id": "koshi_ocean_route",
        "name": "Koshi route to Bay of Bengal",
        "merge_system": "Kosi-Ganges-Padma-Meghna",
    },
    "gandaki_system": {
        "id": "gandaki_ocean_route",
        "name": "Gandaki route to Bay of Bengal",
        "merge_system": "Gandak-Ganges-Padma-Meghna",
    },
    "karnali_system": {
        "id": "karnali_ocean_route",
        "name": "Karnali route to Bay of Bengal",
        "merge_system": "Ghaghara-Ganges-Padma-Meghna",
    },
    "mahakali_system": {
        "id": "mahakali_ocean_route",
        "name": "Mahakali route to Bay of Bengal",
        "merge_system": "Sharda-Ghaghara-Ganges-Padma-Meghna",
    },
}


def bbox_overlaps(bbox: tuple[float, float, float, float], bounds: tuple[float, float, float, float]) -> bool:
    return not (bbox[2] < bounds[0] or bbox[0] > bounds[2] or bbox[3] < bounds[1] or bbox[1] > bounds[3])


def flatten_coords(coords: Any) -> list[tuple[float, float]]:
    if not coords:
        return []
    if isinstance(coords[0], (int, float)):
        return [(float(coords[0]), float(coords[1]))]
    out: list[tuple[float, float]] = []
    for item in coords:
        out.extend(flatten_coords(item))
    return out


def south_point(feature: dict[str, Any]) -> tuple[float, float]:
    coords = flatten_coords(feature["geometry"]["coordinates"])
    return min(coords, key=lambda c: c[1])


def load_reaches() -> tuple[list[dict[str, Any]], dict[int, dict[str, Any]]]:
    reader = shapefile.Reader(str(HYDRORIVERS_SHP))
    reaches: list[dict[str, Any]] = []
    for sr in reader.iterShapeRecords():
        if not bbox_overlaps(tuple(sr.shape.bbox), OCEAN_ROUTE_BOUNDS):
            continue
        rec = sr.record.as_dict()
        geom = LineString(sr.shape.points)
        if geom.is_empty or len(geom.coords) < 2:
            continue
        reaches.append(
            {
                "id": int(rec["HYRIV_ID"]),
                "next_down": int(rec["NEXT_DOWN"]),
                "length_km": float(rec["LENGTH_KM"]),
                "dist_dn_km": float(rec["DIST_DN_KM"]),
                "geometry": geom,
            }
        )
    return reaches, {row["id"]: row for row in reaches}


def nearest_reach(point: Point, reaches: list[dict[str, Any]]) -> tuple[dict[str, Any], float]:
    best = min(reaches, key=lambda row: row["geometry"].distance(point))
    return best, best["geometry"].distance(point) * 111.0


def trace_downstream(start: dict[str, Any], lookup: dict[int, dict[str, Any]]) -> tuple[list[dict[str, Any]], bool]:
    route: list[dict[str, Any]] = []
    seen: set[int] = set()
    current = start
    reached_terminal = False
    while current and current["id"] not in seen:
        route.append(current)
        seen.add(current["id"])
        next_down = current["next_down"]
        if next_down == 0:
            reached_terminal = True
            break
        current = lookup.get(next_down)
    return route, reached_terminal


def route_confidence(snap_km: float, reached_terminal: bool) -> str:
    if reached_terminal and snap_km <= 1.0:
        return "high"
    if reached_terminal and snap_km <= MAX_SNAP_KM:
        return "medium_high"
    if reached_terminal:
        return "medium"
    return "low"


def build_routes() -> tuple[dict[str, Any], dict[str, Any]]:
    downstream = json.loads(DOWNSTREAM_PATH.read_text())
    reaches, lookup = load_reaches()
    features: list[dict[str, Any]] = []
    report_routes: list[dict[str, Any]] = []
    skipped: list[dict[str, Any]] = []

    for system in downstream["features"]:
        props = system["properties"]
        origin_id = props["id"]
        meta = ROUTE_META.get(origin_id)
        if meta is None:
            continue
        start_lon, start_lat = south_point(system)
        start_reach, snap_km = nearest_reach(Point(start_lon, start_lat), reaches)
        if snap_km > MAX_SNAP_KM:
            skipped.append({"origin_system_id": origin_id, "reason": "snap_distance_too_large", "snap_distance_km": snap_km})
            continue
        route, reached_terminal = trace_downstream(start_reach, lookup)
        if not route:
            skipped.append({"origin_system_id": origin_id, "reason": "empty_route"})
            continue

        route_length_km = sum(row["length_km"] for row in route)
        end_lon, end_lat = list(route[-1]["geometry"].coords)[-1]
        features.append(
            {
                "type": "Feature",
                "properties": {
                    "id": meta["id"],
                    "theme": "nepal_origin_ocean_route",
                    "name": meta["name"],
                    "basin": props["basin"],
                    "origin_system_id": origin_id,
                    "downstream_name": props["downstream_name"],
                    "merge_system": meta["merge_system"],
                    "ocean_endpoint": "Bay of Bengal",
                    "route_stage": "ocean_extension",
                    "route_confidence": route_confidence(snap_km, reached_terminal),
                    "source_method": "HydroRIVERS NEXT_DOWN trace from current downstream-system endpoint",
                    "snap_distance_km": round(snap_km, 2),
                    "route_length_km": round(route_length_km, 1),
                    "reach_count": len(route),
                    "impact_note": (
                        f"Strategic route continuation from {props['name']} through {meta['merge_system']} "
                        "to the Bay of Bengal; use as topology context, not hydrodynamic modeling."
                    ),
                    "terminal_lon": end_lon,
                    "terminal_lat": end_lat,
                },
                "geometry": {
                    "type": "MultiLineString",
                    "coordinates": [[list(coord) for coord in row["geometry"].coords] for row in route],
                },
            }
        )
        report_routes.append(
            {
                "id": meta["id"],
                "origin_system_id": origin_id,
                "start_reach_id": start_reach["id"],
                "snap_distance_km": round(snap_km, 2),
                "reach_count": len(route),
                "route_length_km": round(route_length_km, 1),
                "reached_terminal": reached_terminal,
                "terminal_lon": end_lon,
                "terminal_lat": end_lat,
            }
        )

    return {"type": "FeatureCollection", "features": features}, {
        "route_count": len(features),
        "bounds": OCEAN_ROUTE_BOUNDS,
        "routes": report_routes,
        "skipped": skipped,
    }


def main() -> None:
    routes, report = build_routes()
    OUT.write_text(json.dumps(routes))
    REPORT.write_text(json.dumps(report, indent=2))
    print(f"wrote {OUT} ({len(routes['features'])} features)")
    print(f"wrote {REPORT}")


if __name__ == "__main__":
    main()
