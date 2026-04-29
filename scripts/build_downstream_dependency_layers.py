#!/usr/bin/env python3
"""Build strategic downstream route callout and dependency layers.

These layers are intentionally interpretive. They are designed to make the
Nepal-origin route-to-ocean layer readable and to show downstream exposure
zones without claiming hydrodynamic precision.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent.parent
PROCESSED = ROOT / "data" / "processed" / "maps"

ROUTE_CALLOUTS_OUT = PROCESSED / "nepal_origin_route_callouts.geojson"
DEPENDENCY_ZONES_OUT = PROCESSED / "downstream_dependency_zones.geojson"
POPULATION_ANCHORS_OUT = PROCESSED / "downstream_population_anchors.geojson"
REPORT_OUT = PROCESSED / "downstream_dependency_layers_report.json"


def point_feature(lon: float, lat: float, props: dict[str, Any]) -> dict[str, Any]:
    return {
        "type": "Feature",
        "properties": props,
        "geometry": {"type": "Point", "coordinates": [lon, lat]},
    }


def polygon_feature(coords: list[tuple[float, float]], props: dict[str, Any]) -> dict[str, Any]:
    closed = coords if coords[0] == coords[-1] else [*coords, coords[0]]
    return {
        "type": "Feature",
        "properties": props,
        "geometry": {"type": "Polygon", "coordinates": [[[lon, lat] for lon, lat in closed]]},
    }


def feature_collection(features: list[dict[str, Any]]) -> dict[str, Any]:
    return {"type": "FeatureCollection", "features": features}


ROUTE_CALLOUTS = [
    {
        "id": "mahakali_sharda_handoff",
        "name": "Mahakali/Sharda downstream handoff",
        "label_title": "Mahakali/Sharda joins the western Ganges logic",
        "label_subtitle": "Western Nepal-origin route enters the Sharda-Ghaghara-Ganges path",
        "callout_type": "origin_handoff",
        "related_origin_routes": ["mahakali_ocean_route"],
        "river_system": "Sharda-Ghaghara-Ganges",
        "country": "India",
        "lon": 81.55,
        "lat": 27.65,
        "strategic_note": "Shows where the western Nepal-origin route becomes part of the wider downstream plains system.",
        "map_read_note": "Use as an approximate reading marker for route continuity, not as a surveyed confluence point.",
        "confidence": "medium",
        "source_method": "Curated strategic marker aligned to the generated HydroRIVERS downstream route.",
    },
    {
        "id": "ghaghara_ganges_merge",
        "name": "Ghaghara-Ganges merge",
        "label_title": "Karnali/Ghaghara enters the Ganges trunk",
        "label_subtitle": "Karnali's downstream route becomes a major Ganges tributary path",
        "callout_type": "major_merge",
        "related_origin_routes": ["karnali_ocean_route", "mahakali_ocean_route"],
        "river_system": "Ghaghara-Ganges",
        "country": "India",
        "lon": 84.75,
        "lat": 25.72,
        "strategic_note": "Marks the western and far-western Nepal-linked routes joining the main Ganges downstream story.",
        "map_read_note": "Approximate confluence callout used for narrative legibility.",
        "confidence": "medium_high",
        "source_method": "Curated strategic marker aligned to the generated HydroRIVERS downstream route.",
    },
    {
        "id": "gandak_ganges_merge",
        "name": "Gandak-Ganges merge",
        "label_title": "Gandaki/Gandak enters the Ganges trunk",
        "label_subtitle": "Central Nepal-origin flow path meets the lower Ganges corridor",
        "callout_type": "major_merge",
        "related_origin_routes": ["gandaki_ocean_route"],
        "river_system": "Gandak-Ganges",
        "country": "India",
        "lon": 85.18,
        "lat": 25.67,
        "strategic_note": "Connects the Gandaki-Narayani-Gandak system to the dense Bihar/Ganges corridor.",
        "map_read_note": "Approximate confluence callout used for narrative legibility.",
        "confidence": "medium_high",
        "source_method": "Curated strategic marker aligned to the generated HydroRIVERS downstream route.",
    },
    {
        "id": "kosi_ganges_merge",
        "name": "Kosi-Ganges merge",
        "label_title": "Koshi/Kosi enters the Ganges trunk",
        "label_subtitle": "Eastern Nepal-origin route reaches the lower Ganges corridor",
        "callout_type": "major_merge",
        "related_origin_routes": ["koshi_ocean_route"],
        "river_system": "Kosi-Ganges",
        "country": "India",
        "lon": 87.25,
        "lat": 25.42,
        "strategic_note": "Frames the Kosi as the eastern Nepal-origin system entering the shared Ganges path.",
        "map_read_note": "Approximate confluence callout used for narrative legibility.",
        "confidence": "medium_high",
        "source_method": "Curated strategic marker aligned to the generated HydroRIVERS downstream route.",
    },
    {
        "id": "ganges_padma_transition",
        "name": "Ganges-Padma transition",
        "label_title": "Ganges becomes Padma",
        "label_subtitle": "The shared downstream trunk enters Bangladesh naming and delta logic",
        "callout_type": "system_transition",
        "related_origin_routes": ["koshi_ocean_route", "gandaki_ocean_route", "karnali_ocean_route", "mahakali_ocean_route"],
        "river_system": "Ganges-Padma",
        "country": "India/Bangladesh",
        "lon": 88.05,
        "lat": 24.75,
        "strategic_note": "Shows the transition from northern India river politics into Bangladesh delta dependence.",
        "map_read_note": "Approximate transition marker for reading the route across the border.",
        "confidence": "medium",
        "source_method": "Curated strategic marker aligned to the generated HydroRIVERS downstream route.",
    },
    {
        "id": "padma_meghna_delta_merge",
        "name": "Padma-Meghna delta merge",
        "label_title": "Padma and Meghna converge in the delta",
        "label_subtitle": "The Nepal-linked routes are now part of the lower delta system",
        "callout_type": "delta_merge",
        "related_origin_routes": ["koshi_ocean_route", "gandaki_ocean_route", "karnali_ocean_route", "mahakali_ocean_route"],
        "river_system": "Padma-Meghna",
        "country": "Bangladesh",
        "lon": 90.64,
        "lat": 23.25,
        "strategic_note": "Marks the delta convergence where upstream timing, sediment, flood, and dry-season stories accumulate.",
        "map_read_note": "Approximate delta merge marker; v1 does not map dense distributaries.",
        "confidence": "medium",
        "source_method": "Curated strategic marker aligned to the generated HydroRIVERS downstream terminal reach.",
    },
    {
        "id": "bay_of_bengal_terminal",
        "name": "Bay of Bengal terminal reach",
        "label_title": "Bay of Bengal outlet",
        "label_subtitle": "HydroRIVERS terminal reach for the strategic route trace",
        "callout_type": "ocean_endpoint",
        "related_origin_routes": ["koshi_ocean_route", "gandaki_ocean_route", "karnali_ocean_route", "mahakali_ocean_route"],
        "river_system": "Lower Padma-Meghna-Bay of Bengal",
        "country": "Bangladesh",
        "lon": 90.63125,
        "lat": 23.22292,
        "strategic_note": "Final mapped terminal for the route-to-ocean layer.",
        "map_read_note": "Represents the generated terminal reach, not detailed tidal or distributary geography.",
        "confidence": "medium_high",
        "source_method": "HydroRIVERS terminal coordinate from nepal_origin_ocean_routes.geojson.",
    },
]


DEPENDENCY_ZONES = [
    {
        "id": "eastern_up_ghaghara_gandak_belt",
        "name": "Eastern Uttar Pradesh Ghaghara-Gandak belt",
        "country": "India",
        "coords": [(80.3, 28.2), (84.7, 27.65), (84.9, 25.55), (82.3, 25.05), (80.0, 26.0)],
        "dependency_type": "agriculture_population_floodplain",
        "related_origin_routes": ["karnali_ocean_route", "mahakali_ocean_route", "gandaki_ocean_route"],
        "river_systems": ["Ghaghara", "Gandak", "Ganges"],
        "population_pressure": "high",
        "agriculture_importance": "high",
        "dry_season_sensitivity": "medium",
        "flood_sensitivity": "high",
        "sediment_sensitivity": "medium",
        "delta_sensitivity": "low",
        "strategic_read": "Dense agricultural plains tied to the western and central Nepal-linked downstream routes.",
        "confidence": "medium",
        "geometry_basis": "Curated broad dependency polygon around major downstream river corridors.",
    },
    {
        "id": "north_bihar_kosi_gandak_floodplain",
        "name": "North Bihar Kosi-Gandak floodplain",
        "country": "India",
        "coords": [(84.1, 26.85), (88.75, 26.65), (88.8, 25.05), (86.7, 24.75), (84.25, 25.15), (83.75, 26.1)],
        "dependency_type": "floodplain_agriculture_population",
        "related_origin_routes": ["koshi_ocean_route", "gandaki_ocean_route"],
        "river_systems": ["Kosi", "Gandak", "Ganges"],
        "population_pressure": "very_high",
        "agriculture_importance": "very_high",
        "dry_season_sensitivity": "medium_high",
        "flood_sensitivity": "very_high",
        "sediment_sensitivity": "high",
        "delta_sensitivity": "low",
        "strategic_read": "One of the clearest downstream exposure zones for Nepal-origin river timing, floods, sediment, and dry-season support.",
        "confidence": "medium",
        "geometry_basis": "Curated broad dependency polygon around Kosi-Gandak floodplain geography.",
    },
    {
        "id": "bihar_ganges_trunk_zone",
        "name": "Bihar Ganges trunk zone",
        "country": "India",
        "coords": [(83.8, 25.85), (88.35, 25.55), (88.55, 24.45), (85.7, 24.1), (83.7, 24.65)],
        "dependency_type": "shared_trunk_population_agriculture",
        "related_origin_routes": ["koshi_ocean_route", "gandaki_ocean_route", "karnali_ocean_route", "mahakali_ocean_route"],
        "river_systems": ["Ganges", "Kosi", "Gandak", "Ghaghara"],
        "population_pressure": "very_high",
        "agriculture_importance": "high",
        "dry_season_sensitivity": "high",
        "flood_sensitivity": "high",
        "sediment_sensitivity": "medium_high",
        "delta_sensitivity": "low",
        "strategic_read": "Shared Ganges corridor where separate Nepal-linked routes become a common downstream political geography.",
        "confidence": "medium",
        "geometry_basis": "Curated broad dependency polygon around the lower Bihar Ganges corridor.",
    },
    {
        "id": "padma_meghna_delta_dependency",
        "name": "Padma-Meghna delta dependency zone",
        "country": "Bangladesh",
        "coords": [(88.05, 24.85), (92.15, 24.55), (92.15, 22.2), (90.85, 21.75), (88.65, 22.0), (87.95, 23.3)],
        "dependency_type": "delta_population_agriculture_floodplain",
        "related_origin_routes": ["koshi_ocean_route", "gandaki_ocean_route", "karnali_ocean_route", "mahakali_ocean_route"],
        "river_systems": ["Padma", "Meghna", "Lower Ganges"],
        "population_pressure": "very_high",
        "agriculture_importance": "very_high",
        "dry_season_sensitivity": "high",
        "flood_sensitivity": "very_high",
        "sediment_sensitivity": "high",
        "delta_sensitivity": "very_high",
        "strategic_read": "Lower delta zone where upstream timing, flood pulses, sediment, and dry-season availability become Bangladesh-scale concerns.",
        "confidence": "medium",
        "geometry_basis": "Curated broad dependency polygon around Padma-Meghna delta geography.",
    },
    {
        "id": "lower_delta_bay_interface",
        "name": "Lower delta and Bay interface",
        "country": "Bangladesh/India",
        "coords": [(88.35, 22.75), (91.9, 22.55), (91.6, 20.8), (89.2, 20.7), (88.35, 21.6)],
        "dependency_type": "coastal_delta_sediment_salinity",
        "related_origin_routes": ["koshi_ocean_route", "gandaki_ocean_route", "karnali_ocean_route", "mahakali_ocean_route"],
        "river_systems": ["Lower Padma-Meghna", "Bay of Bengal"],
        "population_pressure": "high",
        "agriculture_importance": "high",
        "dry_season_sensitivity": "high",
        "flood_sensitivity": "high",
        "sediment_sensitivity": "very_high",
        "delta_sensitivity": "very_high",
        "strategic_read": "Coastal interface where river timing, sediment, salinity, storm surge exposure, and delta stability meet.",
        "confidence": "low_medium",
        "geometry_basis": "Curated broad coastal-delta context polygon; not a distributary or salinity model.",
    },
]


POPULATION_ANCHORS = [
    ("varanasi", "Varanasi", 82.9739, 25.3176, "India", "city", "Ganges", ["karnali_ocean_route", "mahakali_ocean_route"], "major_city", "Ganges trunk anchor upstream of the Bihar convergence zone."),
    ("gorakhpur", "Gorakhpur", 83.3732, 26.7606, "India", "city", "Rapti-Ghaghara", ["karnali_ocean_route", "mahakali_ocean_route"], "major_city", "Eastern Uttar Pradesh anchor near the Ghaghara/Rapti plains."),
    ("patna", "Patna", 85.1376, 25.5941, "India", "city", "Ganges-Gandak", ["gandaki_ocean_route", "karnali_ocean_route", "mahakali_ocean_route"], "metro_region", "Bihar Ganges anchor near Gandak and downstream trunk convergence."),
    ("muzaffarpur", "Muzaffarpur", 85.3910, 26.1209, "India", "city", "Gandak-Bagmati-Kosi plains", ["gandaki_ocean_route", "koshi_ocean_route"], "major_city", "North Bihar floodplain anchor between Gandak and Kosi influence zones."),
    ("purnia", "Purnia", 87.4753, 25.7771, "India", "city", "Kosi-Mahananda plains", ["koshi_ocean_route"], "major_city", "Eastern Bihar anchor near the Kosi downstream corridor."),
    ("bhagalpur", "Bhagalpur", 86.9842, 25.2425, "India", "city", "Ganges-Kosi trunk", ["koshi_ocean_route", "gandaki_ocean_route", "karnali_ocean_route", "mahakali_ocean_route"], "major_city", "Lower Bihar Ganges anchor downstream of the main Nepal-linked merges."),
    ("rajshahi", "Rajshahi", 88.6042, 24.3745, "Bangladesh", "city", "Padma", ["koshi_ocean_route", "gandaki_ocean_route", "karnali_ocean_route", "mahakali_ocean_route"], "major_city", "Bangladesh Padma anchor after the Ganges-Padma transition."),
    ("dhaka", "Dhaka", 90.4125, 23.8103, "Bangladesh", "metro", "Padma-Meghna delta", ["koshi_ocean_route", "gandaki_ocean_route", "karnali_ocean_route", "mahakali_ocean_route"], "megacity", "Delta megacity context for downstream flood and dry-season sensitivity."),
    ("khulna", "Khulna", 89.5403, 22.8456, "Bangladesh", "city", "Lower delta", ["koshi_ocean_route", "gandaki_ocean_route", "karnali_ocean_route", "mahakali_ocean_route"], "major_city", "Lower delta anchor near coastal sediment and salinity concerns."),
    ("chandpur", "Chandpur", 90.6450, 23.2330, "Bangladesh", "river_port", "Padma-Meghna", ["koshi_ocean_route", "gandaki_ocean_route", "karnali_ocean_route", "mahakali_ocean_route"], "delta_anchor", "Delta merge anchor near the generated ocean-route terminal reach."),
]


def build_route_callouts() -> list[dict[str, Any]]:
    features = []
    for item in ROUTE_CALLOUTS:
        props = {k: v for k, v in item.items() if k not in {"lon", "lat"}}
        props["theme"] = "nepal_origin_route_callout"
        features.append(point_feature(item["lon"], item["lat"], props))
    return features


def build_dependency_zones() -> list[dict[str, Any]]:
    features = []
    for item in DEPENDENCY_ZONES:
        props = {k: v for k, v in item.items() if k != "coords"}
        props["theme"] = "downstream_dependency_zone"
        props["source_note"] = "Strategic v1 dependency zone curated from route geography; not a hydrodynamic, demographic, or allocation model."
        features.append(polygon_feature(item["coords"], props))
    return features


def build_population_anchors() -> list[dict[str, Any]]:
    features = []
    for anchor_id, name, lon, lat, country, anchor_type, river, routes, pop_class, note in POPULATION_ANCHORS:
        features.append(
            point_feature(
                lon,
                lat,
                {
                    "id": anchor_id,
                    "theme": "downstream_population_anchor",
                    "name": name,
                    "country": country,
                    "anchor_type": anchor_type,
                    "nearby_river_system": river,
                    "related_origin_routes": routes,
                    "population_class": pop_class,
                    "dependency_note": note,
                    "floodplain_context": "Strategic downstream context marker; city point does not imply direct attribution of total water supply to Nepal-origin rivers.",
                    "confidence": "medium",
                    "source_note": "Curated city/river-context anchor for explorer readability.",
                },
            )
        )
    return features


def main() -> None:
    route_callouts = build_route_callouts()
    dependency_zones = build_dependency_zones()
    population_anchors = build_population_anchors()

    ROUTE_CALLOUTS_OUT.write_text(json.dumps(feature_collection(route_callouts), indent=2))
    DEPENDENCY_ZONES_OUT.write_text(json.dumps(feature_collection(dependency_zones), indent=2))
    POPULATION_ANCHORS_OUT.write_text(json.dumps(feature_collection(population_anchors), indent=2))
    REPORT_OUT.write_text(
        json.dumps(
            {
                "route_callout_count": len(route_callouts),
                "dependency_zone_count": len(dependency_zones),
                "population_anchor_count": len(population_anchors),
                "scope": "strategic_dependency_context",
                "precision_note": "Curated v1 overlays for route legibility and downstream exposure; not hydrodynamic modeling.",
                "outputs": [
                    str(ROUTE_CALLOUTS_OUT.relative_to(ROOT)),
                    str(DEPENDENCY_ZONES_OUT.relative_to(ROOT)),
                    str(POPULATION_ANCHORS_OUT.relative_to(ROOT)),
                ],
            },
            indent=2,
        )
    )
    print(f"wrote {ROUTE_CALLOUTS_OUT} ({len(route_callouts)} features)")
    print(f"wrote {DEPENDENCY_ZONES_OUT} ({len(dependency_zones)} features)")
    print(f"wrote {POPULATION_ANCHORS_OUT} ({len(population_anchors)} features)")
    print(f"wrote {REPORT_OUT}")


if __name__ == "__main__":
    main()
