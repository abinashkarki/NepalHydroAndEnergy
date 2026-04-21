from __future__ import annotations

import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import fitz
from pypdf import PdfReader
from shapely.geometry import LineString, MultiLineString, Point, mapping
from shapely.ops import linemerge, unary_union


ROOT = Path("/Users/hi/projects/nepalEnergy")
RAW = ROOT / "data" / "raw" / "corridor_tracing"
PROCESSED = ROOT / "data" / "processed" / "maps"

RPGCL_PDF = RAW / "rpgcl" / "nepal_transmission_network_map_revised1.pdf"
LINEWORK_OUT = PROCESSED / "rpgcl_transmission_official_linework.geojson"
LABELS_OUT = PROCESSED / "rpgcl_transmission_official_labels.geojson"
TRACED_OUT = PROCESSED / "transmission_corridor_traced_segments.geojson"
REPORT_OUT = PROCESSED / "rpgcl_transmission_trace_report.json"

TRANSMISSION_LAYERS = {
    "132 kV HTLS",
    "220 kV HTLS",
    "PROPOSED 400kV",
    "PROPOSED 220kV",
    "PROPOSED 132 kV",
    "EXISTING/UNDERCONSTRUCTION 400 kV",
    "EXISTING/UNDERCONSTRUCTION 220 kV",
    "EXISTING 132 kV",
    "cross_border_line_400kv",
}

MAP_NODE_HINTS: dict[str, tuple[float, float]] = {
    "hetauda": (27.4309935, 85.008401),
    "dhalkebar": (26.930012, 85.95488),
    "inaruwa": (26.6098699, 87.1218153),
    "lapsephedi": (27.7518193, 85.494789),
    "ratmate": (27.8530224, 85.0613809),
    "damauli": (27.9828293, 84.2655773),
    "butwal": (27.7003986, 83.4657667),
    "bharatpur": (27.6811896, 84.4301652),
    "bardaghat": (27.5514632, 83.7993104),
    "udipur": (28.176794, 84.431168),
    "khudi": (28.1964, 84.3339),
    "mirchaiya": (26.8321962, 86.2448435),
    "tingla": (27.41565, 86.607529),
    "dhungesanu": (26.6142, 87.7066),
    "soyak_tap": (26.783, 87.903),
}


@dataclass(frozen=True)
class CorridorSpec:
    corridor_id: str
    name: str
    voltage_kv: str
    status: str
    layer: str
    viewport_name: str
    anchors: tuple[str, ...]
    anchor_terms: tuple[str, ...]
    buffer_deg: float
    min_segment_length_deg: float
    confidence: str
    notes: str
    coverage: str = "full"
    allow_fallback_anchors: bool = True


CORRIDOR_SPECS = [
    CorridorSpec(
        corridor_id="hddi_400",
        name="Hetauda-Dhalkebar-Inaruwa 400 kV backbone",
        voltage_kv="400",
        status="Operational",
        layer="EXISTING/UNDERCONSTRUCTION 400 kV",
        viewport_name="Layers",
        anchors=("hetauda", "dhalkebar", "inaruwa"),
        anchor_terms=("Hetauda", "Dhalkebar", "Inaruwa"),
        buffer_deg=0.28,
        min_segment_length_deg=0.1,
        confidence="high",
        notes="Extracted from the official geospatial RPGCL transmission network map. Inaruwa guide anchor uses the repo place-anchor fallback because the map labels the terminal area differently.",
    ),
    CorridorSpec(
        corridor_id="hetauda_bharatpur_bardaghat_220",
        name="Hetauda-Bharatpur-Bardaghat 220 kV corridor",
        voltage_kv="220",
        status="Operational",
        layer="EXISTING/UNDERCONSTRUCTION 220 kV",
        viewport_name="Layers",
        anchors=("hetauda", "bharatpur", "bardaghat"),
        anchor_terms=("Hetauda", "Bharatpur", "Bardaghat"),
        buffer_deg=0.22,
        min_segment_length_deg=0.08,
        confidence="high",
        notes="Extracted from the official geospatial RPGCL transmission network map using the existing/under-construction 220 kV layer.",
    ),
    CorridorSpec(
        corridor_id="mca_central_400",
        name="Lapsiphedi-Ratmate-Hetauda-Damauli-Butwal 400 kV central corridor",
        voltage_kv="400",
        status="Under construction",
        layer="PROPOSED 400kV",
        viewport_name="Layers",
        anchors=("lapsephedi", "ratmate", "hetauda", "damauli", "butwal"),
        anchor_terms=("Lapsephedi", "Ratmate", "Hetauda", "Damauli", "Butwal"),
        buffer_deg=0.26,
        min_segment_length_deg=0.05,
        confidence="high",
        notes="Official-vector route extraction from the RPGCL geospatial map. This is a route-faithful national-scale trace and should supersede the previous compact spine.",
    ),
    CorridorSpec(
        corridor_id="udipur_damauli_bharatpur_220",
        name="Udipur-Damauli-Bharatpur 220 kV reinforcement",
        voltage_kv="220",
        status="Under construction",
        layer="PROPOSED 220kV",
        viewport_name="Layers",
        anchors=("khudi", "udipur", "damauli", "bharatpur"),
        anchor_terms=("Khudi", "Udipur", "Damauli", "Bharatpur"),
        buffer_deg=0.18,
        min_segment_length_deg=0.02,
        confidence="medium",
        notes="Derived from the official geospatial map and aligned to the Khudi-Udipur / Udipur-Bharatpur naming used in the NEA annual report.",
    ),
    CorridorSpec(
        corridor_id="solu_tingla_mirchaiya_132",
        name="Solu Corridor Tingla-Mirchaiya 132 kV",
        voltage_kv="132",
        status="Operational",
        layer="PROPOSED 132 kV",
        viewport_name="New Data Frame",
        anchors=("tingla", "mirchaiya"),
        anchor_terms=("Tingla", "Mirchaiya"),
        buffer_deg=0.18,
        min_segment_length_deg=0.015,
        confidence="medium",
        notes="The official map still styles this corridor in the proposed-132 layer; the trace follows the mapped route between Tingla and New Mirchaiya.",
        allow_fallback_anchors=False,
    ),
    CorridorSpec(
        corridor_id="kabeli_132",
        name="Kabeli / Soyak-Dhungesanu 132 kV branch",
        voltage_kv="132",
        status="Under construction",
        layer="PROPOSED 132 kV",
        viewport_name="New Data Frame",
        anchors=("mirchaiya", "dhungesanu", "soyak_tap"),
        anchor_terms=("Mirchaiya", "Dhungesanu", "Soyak"),
        buffer_deg=0.22,
        min_segment_length_deg=0.015,
        confidence="low",
        coverage="partial",
        notes="Partial official-vector trace for the mapped Soyak Tap-Dhungesanu branch. The full Godak/Amarpur family still needs the route-grade NEA IEE/RAP packet.",
        allow_fallback_anchors=False,
    ),
]


MANUAL_CORRIDOR_TRACES: list[dict[str, Any]] = [
    {
        "corridor_id": "kabeli_132",
        "corridor_label": "Kabeli 132 kV",
        "name": "Kabeli / Godak-Soyak-Amarpur 132 kV corridor",
        "voltage_kv": "132",
        "status": "Under construction",
        "trace_confidence": "medium",
        "trace_coverage": "full",
        "trace_method": "manual_pdf_trace",
        "geometry_basis": (
            "Manual corridor trace derived from the recovered Kabeli IEE district/VDC map and route "
            "description, cross-checked against the Kabeli single-line schematic and supporting NEA RAP/SMEF packets."
        ),
        "notes": (
            "This manual trace follows the documented bifurcation from the southern trunk up to Soyak, then east "
            "to Godak and northwest toward Phidim/Amarpur. It is materially better than the old substation spine, "
            "but should still be read as corridor geometry rather than parcel-level alignment."
        ),
        "source_id": "nea_kabeli_iee",
        "source_pdf": "nea_kabeli_iee.pdf",
        "page_start": 26,
        "page_end": 27,
        "segments": [
            {
                "segment_suffix": "trunk",
                "segment_name": "Kabeli 132 kV southern trunk (Lakhanpur-Soyak)",
                "anchor_names": ["Lakhanpur", "Chulachuli", "Mahamai area", "Danabari area", "Soyak"],
                "coordinates": [
                    [87.7161407, 26.6564208],
                    [87.6824564, 26.7660322],
                    [87.7900000, 26.7833000],
                    [87.8394400, 26.7819400],
                    [87.8794803, 26.8681639],
                ],
            },
            {
                "segment_suffix": "godak_branch",
                "segment_name": "Kabeli 132 kV Godak branch",
                "anchor_names": ["Soyak", "Godak"],
                "coordinates": [
                    [87.8794803, 26.8681639],
                    [87.9748807, 26.8782363],
                ],
            },
            {
                "segment_suffix": "amarpur_branch",
                "segment_name": "Kabeli 132 kV Phidim-Amarpur branch",
                "anchor_names": ["Soyak", "Chamaita", "Phidim", "Bharapa", "Amarpur"],
                "coordinates": [
                    [87.8794803, 26.8681639],
                    [87.8338425, 27.0083791],
                    [87.7660956, 27.1441345],
                    [87.7556963, 27.1599670],
                    [87.7479409, 27.2587964],
                ],
            },
        ],
    },
    {
        "corridor_id": "marsyangdi_upper_220",
        "corridor_label": "Marsyangdi Upper 220 kV",
        "name": "Marsyangdi Corridor Manang-Khudi-Udipur 220 kV",
        "voltage_kv": "220",
        "status": "Under construction",
        "trace_confidence": "medium",
        "trace_coverage": "full",
        "trace_method": "manual_pdf_trace",
        "geometry_basis": (
            "Manual corridor trace derived from the recovered upper Marsyangdi RAP location, project-area, and "
            "accessibility maps, anchored to mapped Dharapani, Khudi, Besishahar, and Udipur nodes."
        ),
        "notes": (
            "The route follows the upper Marsyangdi valley south from Dharapani to Khudi and then bends southeast "
            "toward Udipur. This is a document-grounded corridor trace, not a tower-by-tower alignment."
        ),
        "source_id": "nea_marsyangdi_rap_upper",
        "source_pdf": "nea_marsyangdi_rap_upper.pdf",
        "page_start": 33,
        "page_end": 36,
        "segments": [
            {
                "segment_suffix": "main",
                "segment_name": "Marsyangdi Upper 220 kV main route",
                "anchor_names": ["Dharapani", "Marsyangdi RM", "Khudi", "Besishahar", "Udipur"],
                "coordinates": [
                    [84.3583825, 28.5189984],
                    [84.3625000, 28.4200000],
                    [84.3582715, 28.2810894],
                    [84.3761440, 28.2313160],
                    [84.4311680, 28.1767940],
                ],
            },
        ],
    },
    {
        "corridor_id": "solu_tingla_mirchaiya_132",
        "corridor_label": "Solu Corridor 132 kV",
        "name": "Solu Corridor Tingla-Mirchaiya 132 kV",
        "voltage_kv": "132",
        "status": "Operational",
        "trace_confidence": "low",
        "trace_coverage": "full",
        "trace_method": "manual_route_trace",
        "geometry_basis": (
            "Manual corridor trace derived from NEA Transmission Annual Book 2077 narrative pages on the Tingla "
            "substation and Solu Corridor transmission line, anchored to the source-stated Mirchaiya and Tingla "
            "terminals plus the Maruwa/Katari reroute location and the municipal corridor through Okhaldhunga."
        ),
        "notes": (
            "This is a corridor-level reconstruction, not an alignment-sheet trace. The FY 2019/20 yearbook "
            "describes the line as a 90 km double-circuit route from Mirchaiya to Tingla and notes a rerouting "
            "dispute at Maruwa, Katari municipality. The FY 2024/25 inventory later lists 180 km, which likely "
            "reflects double-circuit conductor counting rather than a different path."
        ),
        "source_id": "nea_transmission_annual_book_2077",
        "source_pdf": "nea_transmission_annual_book_2077.pdf",
        "page_start": 47,
        "page_end": 52,
        "segments": [
            {
                "segment_suffix": "main",
                "segment_name": "Solu Corridor 132 kV main route",
                "anchor_names": ["Mirchaiya", "Katari / Maruwa", "Manebhanjyang", "Rumjatar", "Pattale", "Tingla"],
                "coordinates": [
                    [86.2448435, 26.8321962],
                    [86.4208900, 27.0219510],
                    [86.4655248, 27.2119455],
                    [86.5460807, 27.3041767],
                    [86.5490677, 27.4025403],
                    [86.6075290, 27.4156500],
                ],
            },
        ],
    },
]


def load_geospatial_viewports(reader: PdfReader) -> dict[str, dict[str, Any]]:
    page = reader.pages[0]
    viewports: dict[str, dict[str, Any]] = {}
    for viewport in page["/VP"]:
        name = str(viewport["/Name"])
        measure = viewport["/Measure"].get_object()
        bbox = [float(v) for v in viewport["/BBox"]]
        gpts = [float(v) for v in measure["/GPTS"]]
        viewports[name] = {
            "bbox": bbox,
            "gpts": gpts,
        }
    return viewports


def clean_text(text: str) -> str:
    return text.replace("\x00", "").strip()


def euclidean_distance(a: tuple[float, float], b: tuple[float, float]) -> float:
    return math.hypot(a[0] - b[0], a[1] - b[1])


def point_to_geo_factory(viewport: dict[str, Any]):
    left, bottom, right, top = viewport["bbox"]
    g = viewport["gpts"]
    # GPTS order follows the LPTS order [0,1, 0,0, 1,0, 1,1].
    top_left = (g[2], g[3])
    top_right = (g[4], g[5])
    bottom_right = (g[6], g[7])
    bottom_left = (g[0], g[1])

    def point_to_geo(x: float, y: float) -> tuple[float, float]:
        u = (x - left) / (right - left)
        v = (y - top) / (bottom - top)
        lat = (
            (1 - u) * (1 - v) * top_left[0]
            + u * (1 - v) * top_right[0]
            + u * v * bottom_right[0]
            + (1 - u) * v * bottom_left[0]
        )
        lon = (
            (1 - u) * (1 - v) * top_left[1]
            + u * (1 - v) * top_right[1]
            + u * v * bottom_right[1]
            + (1 - u) * v * bottom_left[1]
        )
        return lon, lat

    return point_to_geo


def point_in_bbox(x: float, y: float, bbox: list[float]) -> bool:
    left, bottom, right, top = bbox
    return left <= x <= right and top <= y <= bottom


def flatten_line_items(items: list[Any]) -> list[tuple[float, float]]:
    points: list[tuple[float, float]] = []
    for item in items:
        op = item[0]
        if op != "l":
            continue
        p1, p2 = item[1], item[2]
        if not points:
            points.append((p1.x, p1.y))
        points.append((p2.x, p2.y))
    return points


def normalize_lines(geoms: list[LineString | MultiLineString]) -> list[LineString]:
    normalized: list[LineString] = []
    for geom in geoms:
        if geom.is_empty:
            continue
        if isinstance(geom, LineString):
            if len(geom.coords) >= 2 and geom.length > 0:
                normalized.append(geom)
            continue
        for part in geom.geoms:
            if len(part.coords) >= 2 and part.length > 0:
                normalized.append(part)
    return normalized


def extract_labels(
    page: fitz.Page,
    viewport_name: str,
    viewport_bbox: list[float],
    excluded_bbox: list[float] | None,
    point_to_geo: Any,
) -> list[dict[str, Any]]:
    labels: list[dict[str, Any]] = []
    for block in page.get_text("dict")["blocks"]:
        for line in block.get("lines", []):
            for span in line.get("spans", []):
                text = clean_text(span["text"])
                if not text:
                    continue
                x0, y0, x1, y1 = span["bbox"]
                cx = (x0 + x1) / 2
                cy = (y0 + y1) / 2
                if not point_in_bbox(cx, cy, viewport_bbox):
                    continue
                if excluded_bbox and point_in_bbox(cx, cy, excluded_bbox):
                    continue
                lon, lat = point_to_geo(cx, cy)
                labels.append(
                    {
                        "type": "Feature",
                        "geometry": {"type": "Point", "coordinates": [lon, lat]},
                        "properties": {
                            "text": text,
                            "page_x": round(cx, 3),
                            "page_y": round(cy, 3),
                            "viewport_name": viewport_name,
                            "source_pdf": RPGCL_PDF.name,
                        },
                    }
                )
    return labels


def choose_anchor_points(labels: list[dict[str, Any]]) -> dict[str, dict[str, dict[str, Any]]]:
    by_term: dict[str, list[dict[str, Any]]] = {}
    for feature in labels:
        text = feature["properties"]["text"]
        for key in MAP_NODE_HINTS:
            if key.replace("_", " ") in text.lower():
                by_term.setdefault(key, []).append(feature)

    selected: dict[str, dict[str, dict[str, Any]]] = {}
    for key, hint in MAP_NODE_HINTS.items():
        candidates = by_term.get(key, [])
        if candidates:
            best = min(
                candidates,
                key=lambda feature: euclidean_distance(
                    (feature["geometry"]["coordinates"][1], feature["geometry"]["coordinates"][0]),
                    hint,
                ),
            )
            viewport_name = best["properties"]["viewport_name"]
            selected.setdefault(viewport_name, {})[key] = best
        pseudo_feature = {
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": [hint[1], hint[0]]},
            "properties": {
                "text": key.replace("_", " ").title(),
                "viewport_name": "fallback",
                "source_pdf": RPGCL_PDF.name,
                "anchor_basis": "repo_hint",
            },
        }
        selected.setdefault("fallback", {})[key] = pseudo_feature
    return selected


def extract_linework(
    page: fitz.Page,
    viewport_name: str,
    viewport_bbox: list[float],
    excluded_bbox: list[float] | None,
    point_to_geo: Any,
) -> list[dict[str, Any]]:
    features: list[dict[str, Any]] = []
    feature_id = 1
    for drawing_idx, drawing in enumerate(page.get_drawings(), start=1):
        layer = drawing.get("layer")
        if layer not in TRANSMISSION_LAYERS:
            continue
        points = [
            (x, y)
            for x, y in flatten_line_items(drawing["items"])
            if point_in_bbox(x, y, viewport_bbox) and not (excluded_bbox and point_in_bbox(x, y, excluded_bbox))
        ]
        if len(points) < 2:
            continue
        coords = [point_to_geo(x, y) for x, y in points]
        if len(coords) < 2:
            continue
        geom = LineString(coords)
        if geom.length == 0:
            continue
        color = drawing.get("color")
        feature = {
            "type": "Feature",
            "geometry": mapping(geom),
            "properties": {
                "id": f"rpgcl_line_{feature_id:05d}",
                "drawing_index": drawing_idx,
                "layer": layer,
                "viewport_name": viewport_name,
                "width": round(float(drawing.get("width") or 0), 3),
                "color_rgb": [round(float(v), 6) for v in color] if color else [],
                "source_pdf": RPGCL_PDF.name,
                "source_type": "official_geospatial_pdf_vector",
                "page_x_min": round(min(x for x, _ in points), 3),
                "page_y_min": round(min(y for _, y in points), 3),
                "page_x_max": round(max(x for x, _ in points), 3),
                "page_y_max": round(max(y for _, y in points), 3),
            },
        }
        features.append(feature)
        feature_id += 1
    return features


def build_corridor_segments(
    linework: list[dict[str, Any]],
    anchors: dict[str, dict[str, dict[str, Any]]],
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    traced_features: list[dict[str, Any]] = []
    report: dict[str, Any] = {}
    line_geoms = [
        (
            feature,
            LineString(feature["geometry"]["coordinates"]),
        )
        for feature in linework
    ]

    for spec in CORRIDOR_SPECS:
        viewport_anchors = anchors.get(spec.viewport_name, {})
        fallback_anchors = anchors.get("fallback", {}) if spec.allow_fallback_anchors else {}
        anchor_features = [viewport_anchors.get(anchor_key) or fallback_anchors.get(anchor_key) for anchor_key in spec.anchors]
        anchor_features = [feature for feature in anchor_features if feature]
        anchor_coords = [tuple(feature["geometry"]["coordinates"]) for feature in anchor_features]
        if len(anchor_coords) < 2:
            report[spec.corridor_id] = {
                "status": "skipped_missing_anchors",
                "matched_anchors": [feature["properties"]["text"] for feature in anchor_features],
                "expected_anchors": list(spec.anchor_terms),
            }
            continue

        guide = LineString(anchor_coords)
        corridor_buffer = guide.buffer(spec.buffer_deg)
        selected_geoms: list[LineString] = []
        selected_source_ids: list[str] = []
        for feature, geom in line_geoms:
            if feature["properties"]["layer"] != spec.layer:
                continue
            if feature["properties"]["viewport_name"] != spec.viewport_name:
                continue
            if geom.intersects(corridor_buffer):
                selected_geoms.append(geom)
                selected_source_ids.append(feature["properties"]["id"])
        if not selected_geoms:
            report[spec.corridor_id] = {
                "status": "no_linework_selected",
                "matched_anchors": [feature["properties"]["text"] for feature in anchor_features],
                "expected_anchors": list(spec.anchor_terms),
            }
            continue

        merged = unary_union(selected_geoms)
        merged = normalize_lines([merged] if isinstance(merged, LineString) else list(merged.geoms) if isinstance(merged, MultiLineString) else [merged])
        merged = normalize_lines([linemerge(merged)]) if merged else []
        normalized = [geom for geom in merged if geom.length >= spec.min_segment_length_deg]
        if not normalized and merged:
            normalized = [max(merged, key=lambda geom: geom.length)]
        if not normalized:
            report[spec.corridor_id] = {
                "status": "merge_empty",
                "matched_anchors": [feature["properties"]["text"] for feature in anchor_features],
                "expected_anchors": list(spec.anchor_terms),
                "selected_count": len(selected_geoms),
            }
            continue

        for idx, geom in enumerate(normalized, start=1):
            traced_features.append(
                {
                    "type": "Feature",
                    "geometry": mapping(geom),
                    "properties": {
                        "corridor_id": spec.corridor_id,
                        "segment_id": f"{spec.corridor_id}_seg_{idx:02d}",
                        "segment_name": f"{spec.name} segment {idx}",
                        "name": spec.name,
                        "voltage_kv": spec.voltage_kv,
                        "status": spec.status,
                        "source_pdf": RPGCL_PDF.name,
                        "source_layer": spec.layer,
                        "viewport_name": spec.viewport_name,
                        "geometry_basis": "Official vector extraction from geospatial RPGCL transmission network map (2021).",
                        "trace_confidence": spec.confidence,
                        "trace_coverage": spec.coverage,
                        "anchor_chain": " -> ".join(feature["properties"]["text"] for feature in anchor_features),
                        "matched_anchor_count": len(anchor_features),
                        "selected_drawing_count": len(selected_geoms),
                        "selected_source_ids": selected_source_ids,
                        "notes": spec.notes,
                    },
                }
            )

        report[spec.corridor_id] = {
            "status": "ok",
            "matched_anchors": [feature["properties"]["text"] for feature in anchor_features],
            "expected_anchors": list(spec.anchor_terms),
                "selected_count": len(selected_geoms),
                "output_segment_count": len(normalized),
                "layer": spec.layer,
                "viewport_name": spec.viewport_name,
                "coverage": spec.coverage,
                "confidence": spec.confidence,
            }

    return traced_features, report


def build_manual_corridor_segments() -> tuple[list[dict[str, Any]], dict[str, Any]]:
    traced_features: list[dict[str, Any]] = []
    report: dict[str, Any] = {}

    for corridor in MANUAL_CORRIDOR_TRACES:
        segment_count = 0
        for index, segment in enumerate(corridor["segments"], start=1):
            geom = LineString(segment["coordinates"])
            traced_features.append(
                {
                    "type": "Feature",
                    "geometry": mapping(geom),
                    "properties": {
                        "corridor_id": corridor["corridor_id"],
                        "corridor_label": corridor["corridor_label"],
                        "segment_id": f"{corridor['corridor_id']}_{segment['segment_suffix']}",
                        "segment_name": segment["segment_name"],
                        "name": corridor["name"],
                        "voltage_kv": corridor["voltage_kv"],
                        "status": corridor["status"],
                        "source_pdf": corridor["source_pdf"],
                        "source_id": corridor["source_id"],
                        "source_layer": "manual_recovered_pdf_trace",
                        "viewport_name": "manual_pdf_trace",
                        "page_start": corridor["page_start"],
                        "page_end": corridor["page_end"],
                        "geometry_basis": corridor["geometry_basis"],
                        "trace_method": corridor["trace_method"],
                        "trace_confidence": corridor["trace_confidence"],
                        "trace_coverage": corridor["trace_coverage"],
                        "anchor_chain": " -> ".join(segment["anchor_names"]),
                        "matched_anchor_count": len(segment["anchor_names"]),
                        "selected_drawing_count": 1,
                        "selected_source_ids": [corridor["source_id"]],
                        "notes": corridor["notes"],
                    },
                }
            )
            segment_count = index

        report[corridor["corridor_id"]] = {
            "status": "ok_manual_trace",
            "source_id": corridor["source_id"],
            "source_pdf": corridor["source_pdf"],
            "page_start": corridor["page_start"],
            "page_end": corridor["page_end"],
            "output_segment_count": segment_count,
            "coverage": corridor["trace_coverage"],
            "confidence": corridor["trace_confidence"],
            "trace_method": corridor["trace_method"],
        }

    return traced_features, report


def main() -> None:
    PROCESSED.mkdir(parents=True, exist_ok=True)

    reader = PdfReader(str(RPGCL_PDF))
    viewports = load_geospatial_viewports(reader)
    main_view = viewports["Layers"]
    inset_view = viewports["New Data Frame"]
    doc = fitz.open(RPGCL_PDF)
    page = doc[0]
    labels = extract_labels(
        page,
        viewport_name="Layers",
        viewport_bbox=main_view["bbox"],
        excluded_bbox=inset_view["bbox"],
        point_to_geo=point_to_geo_factory(main_view),
    )
    anchors = choose_anchor_points(labels)
    linework = extract_linework(
        page,
        viewport_name="Layers",
        viewport_bbox=main_view["bbox"],
        excluded_bbox=inset_view["bbox"],
        point_to_geo=point_to_geo_factory(main_view),
    )
    traced_segments, corridor_report = build_corridor_segments(linework, anchors)
    manual_segments, manual_report = build_manual_corridor_segments()
    all_traced_segments = traced_segments + manual_segments

    LINEWORK_OUT.write_text(json.dumps({"type": "FeatureCollection", "features": linework}, indent=2))
    LABELS_OUT.write_text(json.dumps({"type": "FeatureCollection", "features": labels}, indent=2))
    TRACED_OUT.write_text(json.dumps({"type": "FeatureCollection", "features": all_traced_segments}, indent=2))
    REPORT_OUT.write_text(
        json.dumps(
            {
                "source_pdf": str(RPGCL_PDF),
                "viewports": viewports,
                "linework_feature_count": len(linework),
                "label_feature_count": len(labels),
                "selected_anchor_keys": sorted(anchors.keys()),
                "corridors": corridor_report,
                "manual_corridors": manual_report,
                "traced_feature_count": len(all_traced_segments),
            },
            indent=2,
        )
    )

    print(f"[ok] official linework -> {LINEWORK_OUT}")
    print(f"[ok] official labels -> {LABELS_OUT}")
    print(f"[ok] traced corridors -> {TRACED_OUT}")
    print(f"[ok] trace report -> {REPORT_OUT}")


if __name__ == "__main__":
    main()
