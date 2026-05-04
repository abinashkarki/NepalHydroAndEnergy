from __future__ import annotations

import csv
import json
import math
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any


ROOT = Path(os.environ.get("NEPAL_ENERGY_ROOT", Path(__file__).resolve().parent.parent))
PROCESSED = ROOT / "data" / "processed" / "maps"
MANIFEST_DIR = ROOT / "data" / "processed" / "corridor_tracing" / "manifests"

TRACED_PATH = PROCESSED / "transmission_corridor_traced_segments.geojson"
CURATED_PATH = PROCESSED / "transmission_corridors.geojson"
PLACE_ANCHORS_PATH = PROCESSED / "place_anchor_index.geojson"
CROSS_BORDER_PATH = PROCESSED / "cross_border_interconnections.geojson"
TRACE_MANIFEST_PATH = MANIFEST_DIR / "corridor_trace_manifest.json"

NETWORK_PATH = PROCESSED / "transmission_corridor_traced_network.geojson"
NODES_PATH = PROCESSED / "transmission_network_nodes.geojson"
CROSS_BORDER_LINES_PATH = PROCESSED / "cross_border_interconnection_lines.geojson"
VALIDATION_JSON_PATH = PROCESSED / "transmission_corridor_validation_report.json"
VALIDATION_CSV_PATH = PROCESSED / "transmission_corridor_validation_report.csv"
GAP_REPORT_PATH = PROCESSED / "transmission_trace_gap_report.geojson"
BUILD_REPORT_PATH = PROCESSED / "transmission_network_build_report.json"

EARTH_RADIUS_KM = 6371.0088
NODE_CLUSTER_KM = 0.05
MIN_CONNECTOR_KM = 0.025
SNAP_THRESHOLDS_KM = {
    "high": 2.0,
    "medium": 5.0,
    "low": 0.0,
}
LENGTH_DELTA_LIMITS_PCT = {
    "high": 10.0,
    "medium": 15.0,
    "low": 25.0,
}

ROUTE_LENGTH_OVERRIDES = {
    "hddi_400": {
        "official_route_km": 288.0,
        "official_circuit_km": 576.0,
        "basis": "NEA FY2024/25 describes approximately 288 km of 400 kV double-circuit HDDI line. The existing-line inventory lists Dhalkebar-Inaruwa as 306 circuit-km and the under-construction inventory lists Hetauda-Dhalkebar as 270 circuit-km, consistent with about 153 km and 135 km route-km respectively. The earlier World Bank HDDTL RAP gives 285.2 km for the Hetauda-Dhalkebar-Duhabi alignment.",
        "source_id": "nea_annual_report_2024_2025+world_bank_hddtl_rap",
    },
    "hetauda_bharatpur_bardaghat_220": {
        "official_route_km": 146.5,
        "official_circuit_km": 293.0,
        "basis": "Hetauda-Bharatpur is reported by NEA/current public status references as about 73 route-km; the NEA Bharatpur-Bardaghat SIA gives 73.5 route-km. Older NEA annual-book tables list 148 circuit-km for each double-circuit section, consistent with about 74 route-km per section.",
        "source_id": "nea_transmission_annual_book_2077+nea_bharatpur_bardaghat_sia",
    },
    "dana_kushma_butwal_220": {
        "official_route_km": 127.57,
        "official_circuit_km": 255.6,
        "basis": "NEA Transmission Annual Book 2077 gives 39.57 route-km for Dana-Kushma and 88 route-km for Kushma-New Butwal, totaling 127.57 route-km. NEA FY2024/25 existing-line inventory lists 79.6 and 176 circuit-km respectively, consistent with double-circuit accounting.",
        "source_id": "nea_transmission_annual_book_2077+nea_annual_report_2024_2025",
    },
    "western_132_backbone": {
        "official_route_km": 404.89,
        "official_circuit_km": 809.78,
        "basis": "NEA FY2024/25 existing high-voltage line inventory lists the operational western 132 kV Terai chain as double-circuit Butwal-Shivapur-Lamahi-Kohalpur 430 circuit-km, Kohalpur-Bhurigaun-Lumki 176.66 circuit-km, and Lamki-Pahalwanpur-Attariya-Mahendranagar (Lalpur) 203.12 circuit-km. Route basis divides double-circuit-km by two. Chameliya-Syaule-Attariya is tracked as its own far-west hydro evacuation corridor.",
        "source_id": "nea_annual_report_2024_2025+rpgcl_transmission_network_map_revised1",
    },
    "chameliya_attariya_132": {
        "official_route_km": 131.0,
        "official_circuit_km": 262.0,
        "basis": "NEA FY2024/25 existing high-voltage line inventory lists Chameliya-Syaule-Attariya as a 262 circuit-km double-circuit 132 kV line, equivalent to about 131 route-km.",
        "source_id": "nea_annual_report_2024_2025+rpgcl_transmission_network_map_revised1",
    },
    "kohalpur_surkhet_dailekh_132": {
        "official_route_km": 84.0,
        "official_circuit_km": 168.0,
        "basis": "NEA FY2024/25 project narrative gives 52 km from Kohalpur to Surkhet and 32 km from Surkhet to Dailekh. The under-construction line table lists the double-circuit package as 168 circuit-km.",
        "source_id": "nea_annual_report_2024_2025",
    },
    "mca_central_400": {
        "official_route_km": 308.65,
        "official_circuit_km": 617.3,
        "basis": "MCC Nepal Compact component route lengths: Ratmate-New Damauli 88.23 km, Ratmate-Lapsiphedi 57.83 km, Ratmate-New Hetauda 55.59 km, New Damauli-New Butwal 84 km, and New Butwal-India Border 23 km. The 617.3 km compact indicator is double-circuit/circuit-km accounting.",
        "source_id": "mcc_nepal_compact",
    },
    "udipur_damauli_bharatpur_220": {
        "official_route_km": 64.45,
        "basis": "NEA Marsyangdi RAP text gives 64.45 route-km for Udipur-Markichowk-Bharatpur; the route map labels the same line as 67 km. Khudi-Udipur should be tracked separately when sourced.",
        "source_id": "nea_marsyangdi_rap",
    },
    "kabeli_132": {
        "official_route_km": 83.74,
        "basis": "NEA Kabeli IEE total route length.",
        "source_id": "nea_kabeli_iee",
    },
    "marsyangdi_upper_220": {
        "official_route_km": 46.0,
        "basis": "Upper Marsyangdi RAP route interpretation; NEA table appears to report double-circuit circuit-km.",
        "source_id": "nea_marsyangdi_rap_upper",
    },
    "solu_tingla_mirchaiya_132": {
        "official_route_km": 90.0,
        "basis": "NEA Transmission Annual Book 2077 route-km; NEA FY2024/25 180 km appears to be circuit-km.",
        "source_id": "nea_transmission_annual_book_2077",
    },
}

INDIA_ANCHOR_BY_INTERCONNECTION = {
    "dhalkebar_muzaffarpur": "muzaffarpur",
    "nautanwa_mainahiya": "nautanwa",
    "inaruwa_purnea": "purnea",
    "lamki_bareilly": "bareilly",
    "chameliya_jauljibi": "jauljibi",
}

# Approximate named-place anchors used only for short conservative gateway stubs
# when the processed place-anchor index does not contain an India-side point.
FALLBACK_INDIA_POINTS = {
    "kataiya_kushaha": {"label": "Kataiya", "lon": 86.73, "lat": 26.58},
    "raxaul_parwanipur": {"label": "Raxaul", "lon": 84.85, "lat": 26.98},
    "tanakpur_mahendranagar": {"label": "Tanakpur", "lon": 80.12, "lat": 29.07},
    "nepalgunj_nanpara": {"label": "Nanpara", "lon": 81.50, "lat": 27.86},
    "gorakhpur_new_butwal": {"label": "Gorakhpur", "lon": 83.37, "lat": 26.76},
}

OFFICIAL_SOURCE_URLS = {
    "pib_lok_sabha_2026_04_02": "https://www.pib.gov.in/PressReleseDetailm.aspx?PRID=2248339&lang=1&reg=3",
    "cea_nep_volume_ii": "https://cea.nic.in/wp-content/uploads/notification/2024/10/National_Electricity_Plan_Volume_II_Transmission.pdf",
    "mcc_fy2025_annual_report": "https://www.mcc.gov/resources/doc/annual-report-2025/",
    "mcc_nepal_compact": "https://assets.mcc.gov/content/uploads/compact-nepal.pdf",
}


@dataclass
class Endpoint:
    key: str
    corridor_id: str
    feature: dict[str, Any]
    coord: tuple[float, float]
    end: str
    node_id: str = ""


def read_geojson(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def write_geojson(path: Path, features: list[dict[str, Any]]) -> None:
    path.write_text(json.dumps({"type": "FeatureCollection", "features": features}, indent=2))


def haversine_km(a: tuple[float, float], b: tuple[float, float]) -> float:
    lon1, lat1 = map(math.radians, a)
    lon2, lat2 = map(math.radians, b)
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    h = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    return 2 * EARTH_RADIUS_KM * math.asin(min(1.0, math.sqrt(h)))


def line_length_km(geometry: dict[str, Any]) -> float:
    if not geometry:
        return 0.0
    gtype = geometry.get("type")
    coords = geometry.get("coordinates") or []
    if gtype == "LineString":
        return sum(haversine_km(tuple(a), tuple(b)) for a, b in zip(coords, coords[1:]))
    if gtype == "MultiLineString":
        return sum(line_length_km({"type": "LineString", "coordinates": part}) for part in coords)
    return 0.0


def endpoint_coords(geometry: dict[str, Any]) -> tuple[tuple[float, float], tuple[float, float]]:
    if geometry.get("type") == "LineString":
        coords = geometry["coordinates"]
        return tuple(coords[0]), tuple(coords[-1])
    if geometry.get("type") == "MultiLineString":
        parts = [part for part in geometry["coordinates"] if part]
        return tuple(parts[0][0]), tuple(parts[-1][-1])
    raise ValueError(f"Unsupported transmission geometry type: {geometry.get('type')}")


def normalize_id(value: str) -> str:
    out = "".join(ch.lower() if ch.isalnum() else "_" for ch in str(value)).strip("_")
    while "__" in out:
        out = out.replace("__", "_")
    return out or "unnamed"


def infer_trace_method(props: dict[str, Any]) -> str:
    if props.get("trace_method"):
        return str(props["trace_method"])
    if props.get("source_layer"):
        return "official_vector"
    return "manual_pdf_trace"


def geometry_role_for_trace(props: dict[str, Any]) -> str:
    method = infer_trace_method(props).lower()
    return "manual_trace" if method.startswith("manual") else "source_trace"


def source_page_or_sheet(props: dict[str, Any]) -> str:
    if props.get("figure_or_sheet"):
        return str(props["figure_or_sheet"])
    if props.get("source_page_or_sheet"):
        return str(props["source_page_or_sheet"])
    if props.get("page_start"):
        page = str(props["page_start"])
        if props.get("page_end") and props.get("page_end") != props.get("page_start"):
            page += f"-{props['page_end']}"
        return page
    return str(props.get("viewport_name") or props.get("source_layer") or "")


def source_id_for_trace(props: dict[str, Any]) -> str:
    if props.get("source_id"):
        return str(props["source_id"])
    if props.get("source_pdf"):
        return Path(str(props["source_pdf"])).stem
    return "unknown_source"


def load_manifest_rows() -> list[dict[str, Any]]:
    if not TRACE_MANIFEST_PATH.exists():
        return []
    return json.loads(TRACE_MANIFEST_PATH.read_text())


def manifest_sources_by_corridor(rows: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[row["corridor_id"]].append(row)
    out: dict[str, dict[str, Any]] = {}
    role_rank = {
        "trace_grade_candidate": 0,
        "manual_route_basis": 1,
        "supporting_alignment_context": 2,
        "status_reference": 3,
        "reference_only": 4,
    }
    for corridor_id, items in grouped.items():
        length_candidates = [r for r in items if isinstance(r.get("official_length_km"), (int, float))]
        length_candidates.sort(key=lambda r: role_rank.get(str(r.get("source_role")), 99))
        chosen = length_candidates[0] if length_candidates else {}
        out[corridor_id] = {
            "chosen_length_row": chosen,
            "sources": items,
            "source_ids": sorted({str(r.get("source_id")) for r in items if r.get("source_id")}),
        }
    return out


def make_place_indexes(place_anchors: dict[str, Any]) -> tuple[dict[str, dict[str, Any]], dict[str, str]]:
    by_id: dict[str, dict[str, Any]] = {}
    label_to_id: dict[str, str] = {}
    for feature in place_anchors.get("features", []):
        props = feature["properties"]
        coords = feature["geometry"]["coordinates"]
        anchor = {
            "id": props["id"],
            "label": props.get("label") or props["id"],
            "lon": coords[0],
            "lat": coords[1],
            "basis": props.get("basis", ""),
        }
        by_id[anchor["id"]] = anchor
        label_to_id[normalize_id(anchor["label"])] = anchor["id"]
        label_to_id[normalize_id(anchor["id"])] = anchor["id"]
    return by_id, label_to_id


def make_node(
    node_id: str,
    coord: tuple[float, float],
    label: str,
    node_type: str,
    status: str,
    voltage_kv: str,
    source_basis: str,
    confidence: str,
    place_anchor_id: str = "",
) -> dict[str, Any]:
    return {
        "type": "Feature",
        "properties": {
            "node_id": node_id,
            "label": label,
            "node_type": node_type,
            "status": status,
            "voltage_kv": voltage_kv,
            "source_basis": source_basis,
            "confidence": confidence,
            "place_anchor_id": place_anchor_id,
        },
        "geometry": {"type": "Point", "coordinates": [coord[0], coord[1]]},
    }


def cluster_endpoint_nodes(endpoints: list[Endpoint]) -> tuple[list[dict[str, Any]], dict[str, tuple[float, float]]]:
    nodes: list[dict[str, Any]] = []
    centers: dict[str, tuple[float, float]] = {}
    clusters: list[dict[str, Any]] = []
    for endpoint in endpoints:
        best = None
        best_dist = float("inf")
        for cluster in clusters:
            dist = haversine_km(endpoint.coord, cluster["coord"])
            if dist < best_dist:
                best = cluster
                best_dist = dist
        if best and best_dist <= NODE_CLUSTER_KM:
            endpoint.node_id = best["node_id"]
            best["members"].append(endpoint)
            continue
        props = endpoint.feature["properties"]
        node_id = f"trace_node_{len(clusters) + 1:04d}"
        endpoint.node_id = node_id
        clusters.append(
            {
                "node_id": node_id,
                "coord": endpoint.coord,
                "members": [endpoint],
                "props": props,
            }
        )
    for cluster in clusters:
        props = cluster["props"]
        members = cluster["members"]
        label = props.get("segment_name") or props.get("name") or props.get("corridor_id")
        if len(members) > 1:
            label = f"{props.get('corridor_id')} junction"
        confidence = props.get("trace_confidence", "unknown")
        nodes.append(
            make_node(
                cluster["node_id"],
                cluster["coord"],
                str(label),
                "trace_endpoint" if len(members) == 1 else "inferred_junction",
                props.get("status", "Unknown"),
                str(props.get("voltage_kv", "")),
                "endpoint cluster from traced transmission geometry",
                str(confidence),
            )
        )
        centers[cluster["node_id"]] = cluster["coord"]
    return nodes, centers


def source_feature_props(
    props: dict[str, Any],
    from_node_id: str,
    to_node_id: str,
    length_km: float,
    corridor_delta_pct: float | None,
) -> dict[str, Any]:
    corridor_id = props.get("corridor_id", "")
    return {
        "corridor_id": corridor_id,
        "segment_id": props.get("segment_id") or normalize_id(props.get("segment_name", corridor_id)),
        "segment_name": props.get("segment_name") or props.get("name") or corridor_id,
        "name": props.get("name") or props.get("segment_name") or corridor_id,
        "voltage_kv": str(props.get("voltage_kv", "")),
        "status": props.get("status") or "Unknown",
        "geometry_role": geometry_role_for_trace(props),
        "trace_method": infer_trace_method(props),
        "trace_confidence": props.get("trace_confidence") or "unknown",
        "source_id": source_id_for_trace(props),
        "source_pdf": props.get("source_pdf") or props.get("source_path") or "",
        "source_page_or_sheet": source_page_or_sheet(props),
        "from_node_id": from_node_id,
        "to_node_id": to_node_id,
        "length_km": round(length_km, 3),
        "length_delta_pct": round(corridor_delta_pct, 2) if corridor_delta_pct is not None else None,
        "geometry_basis": props.get("geometry_basis") or "traced transmission corridor segment",
        "notes": props.get("notes") or "",
    }


def connector_confidence(confidence: str) -> str:
    return "medium" if confidence == "high" else "low"


def make_connector_feature(
    corridor_id: str,
    idx: int,
    a: Endpoint,
    b: Endpoint,
    length_delta_pct: float | None,
) -> dict[str, Any]:
    props_a = a.feature["properties"]
    props_b = b.feature["properties"]
    confidence = min(
        [str(props_a.get("trace_confidence", "low")), str(props_b.get("trace_confidence", "low"))],
        key=lambda v: {"high": 0, "medium": 1, "low": 2}.get(v, 3),
    )
    length = haversine_km(a.coord, b.coord)
    return {
        "type": "Feature",
        "properties": {
            "corridor_id": corridor_id,
            "segment_id": f"{corridor_id}_connector_{idx:02d}",
            "segment_name": f"{props_a.get('name', corridor_id)} inferred connector {idx}",
            "name": props_a.get("name") or props_b.get("name") or corridor_id,
            "voltage_kv": str(props_a.get("voltage_kv") or props_b.get("voltage_kv") or ""),
            "status": props_a.get("status") or props_b.get("status") or "Unknown",
            "geometry_role": "inferred_connector",
            "trace_method": "inferred_endpoint_snap",
            "trace_confidence": connector_confidence(confidence),
            "source_id": "derived_topology",
            "source_pdf": "",
            "source_page_or_sheet": "",
            "from_node_id": a.node_id,
            "to_node_id": b.node_id,
            "length_km": round(length, 3),
            "length_delta_pct": round(length_delta_pct, 2) if length_delta_pct is not None else None,
            "geometry_basis": "Straight connector between traced endpoints inside the explicit snap threshold.",
            "notes": f"Endpoint gap {length:.3f} km; connector is inferred and not a source-traced route.",
        },
        "geometry": {"type": "LineString", "coordinates": [list(a.coord), list(b.coord)]},
    }


def choose_threshold(features: list[dict[str, Any]]) -> float:
    confidences = [str(f["properties"].get("trace_confidence", "low")).lower() for f in features]
    if not confidences:
        return 0.0
    if "low" in confidences:
        return 0.0
    if any(infer_trace_method(f["properties"]).lower() == "official_vector" for f in features):
        return SNAP_THRESHOLDS_KM["high"]
    if "medium" in confidences:
        return SNAP_THRESHOLDS_KM["medium"]
    return SNAP_THRESHOLDS_KM["high"]


def canonical_node_edge(a: str, b: str) -> tuple[str, str]:
    return tuple(sorted((a, b)))


def source_node_edges(endpoints: list[Endpoint]) -> set[tuple[str, str]]:
    nodes_by_feature: dict[int, dict[str, str]] = defaultdict(dict)
    for endpoint in endpoints:
        nodes_by_feature[id(endpoint.feature)][endpoint.end] = endpoint.node_id

    edges: set[tuple[str, str]] = set()
    for endpoint_nodes in nodes_by_feature.values():
        from_node = endpoint_nodes.get("from")
        to_node = endpoint_nodes.get("to")
        if from_node and to_node and from_node != to_node:
            edges.add(canonical_node_edge(from_node, to_node))
    return edges


def connected_components(node_ids: set[str], edges: set[tuple[str, str]]) -> dict[str, int]:
    adjacency: dict[str, set[str]] = {node_id: set() for node_id in node_ids}
    for from_node, to_node in edges:
        adjacency.setdefault(from_node, set()).add(to_node)
        adjacency.setdefault(to_node, set()).add(from_node)

    components: dict[str, int] = {}
    component_idx = 0
    for node_id in sorted(adjacency):
        if node_id in components:
            continue
        stack = [node_id]
        while stack:
            current = stack.pop()
            if current in components:
                continue
            components[current] = component_idx
            stack.extend(sorted(adjacency.get(current, set()).difference(components)))
        component_idx += 1
    return components


def build_connectors_and_gaps(
    by_corridor: dict[str, list[dict[str, Any]]],
    endpoints_by_corridor: dict[str, list[Endpoint]],
    deltas: dict[str, float | None],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, dict[str, Any]]]:
    connector_features: list[dict[str, Any]] = []
    gap_features: list[dict[str, Any]] = []
    summaries: dict[str, dict[str, Any]] = {}
    for corridor_id, endpoints in endpoints_by_corridor.items():
        features = by_corridor[corridor_id]
        threshold = choose_threshold(features)
        existing_edges = source_node_edges(endpoints)
        candidate_pairs: list[tuple[float, Endpoint, Endpoint]] = []
        for i, a in enumerate(endpoints):
            for b in endpoints[i + 1 :]:
                if a.feature is b.feature:
                    continue
                if a.node_id == b.node_id:
                    continue
                if canonical_node_edge(a.node_id, b.node_id) in existing_edges:
                    continue
                dist = haversine_km(a.coord, b.coord)
                candidate_pairs.append((dist, a, b))
        candidate_pairs.sort(key=lambda row: row[0])
        used: set[str] = set()
        accepted_edges: set[tuple[str, str]] = set()
        connector_idx = 1
        for dist, a, b in candidate_pairs:
            if a.key in used or b.key in used:
                continue
            edge_key = canonical_node_edge(a.node_id, b.node_id)
            if threshold and MIN_CONNECTOR_KM <= dist <= threshold:
                connector_features.append(make_connector_feature(corridor_id, connector_idx, a, b, deltas.get(corridor_id)))
                connector_idx += 1
                accepted_edges.add(edge_key)
                used.add(a.key)
                used.add(b.key)

        node_ids = {endpoint.node_id for endpoint in endpoints}
        components = connected_components(node_ids, existing_edges | accepted_edges)
        remaining_gaps: list[float] = []
        reported_gap_edges: set[tuple[str, str]] = set()
        for endpoint in endpoints:
            nearest = None
            nearest_dist = float("inf")
            for other in endpoints:
                if endpoint.feature is other.feature or endpoint.key == other.key:
                    continue
                if components.get(endpoint.node_id) == components.get(other.node_id):
                    continue
                dist = haversine_km(endpoint.coord, other.coord)
                if dist < nearest_dist:
                    nearest = other
                    nearest_dist = dist
            if nearest and nearest_dist > max(threshold, MIN_CONNECTOR_KM):
                gap_edge = canonical_node_edge(endpoint.node_id, nearest.node_id)
                if gap_edge in reported_gap_edges:
                    continue
                reported_gap_edges.add(gap_edge)
                remaining_gaps.append(nearest_dist)
                gap_features.append(
                    {
                        "type": "Feature",
                        "properties": {
                            "corridor_id": corridor_id,
                            "from_segment_id": endpoint.feature["properties"].get("segment_id"),
                            "to_segment_id": nearest.feature["properties"].get("segment_id"),
                            "from_node_id": endpoint.node_id,
                            "to_node_id": nearest.node_id,
                            "gap_km": round(nearest_dist, 3),
                            "threshold_km": threshold,
                            "issue": "unconnected_endpoint_gap",
                            "notes": "Nearest traced endpoint is outside the automatic connector threshold.",
                        },
                        "geometry": {"type": "LineString", "coordinates": [list(endpoint.coord), list(nearest.coord)]},
                    }
                )
        summaries[corridor_id] = {
            "snap_threshold_km": threshold,
            "connector_count": connector_idx - 1,
            "remaining_gap_count": len(remaining_gaps),
            "max_remaining_gap_km": round(max(remaining_gaps), 3) if remaining_gaps else 0.0,
        }
    return connector_features, gap_features, summaries


def build_cross_border_lines(
    interconnections: dict[str, Any],
    place_by_id: dict[str, dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[str]]:
    line_features: list[dict[str, Any]] = []
    node_features: list[dict[str, Any]] = []
    warnings: list[str] = []
    for feature in interconnections.get("features", []):
        props = feature["properties"]
        cid = props["id"]
        nepal_coord = tuple(feature["geometry"]["coordinates"])
        india_anchor_id = INDIA_ANCHOR_BY_INTERCONNECTION.get(cid)
        india_anchor = place_by_id.get(india_anchor_id or "")
        connection_scope = "endpoint_connector" if india_anchor else "gateway_stub"
        basis = "Nepal-side point to processed India-side place anchor."
        if india_anchor:
            india_coord = (india_anchor["lon"], india_anchor["lat"])
            india_label = india_anchor["label"]
        else:
            fallback = FALLBACK_INDIA_POINTS.get(cid)
            if not fallback:
                warnings.append(f"{cid}: skipped cross-border line; no India-side endpoint or gateway basis.")
                continue
            india_coord = (fallback["lon"], fallback["lat"])
            india_label = fallback["label"]
            basis = "Conservative gateway stub toward named India-side endpoint; not a route alignment."
        line_length = haversine_km(nepal_coord, india_coord)
        if connection_scope == "gateway_stub" and line_length > 35:
            bearing_stub = point_toward(nepal_coord, india_coord, 18.0)
            india_coord = bearing_stub
            line_length = haversine_km(nepal_coord, india_coord)
        source_id = "pib_lok_sabha_2026_04_02"
        if cid == "gorakhpur_new_butwal":
            source_id = "mcc_fy2025_annual_report"
        elif props.get("status") in {"Implementation setup", "Planned"}:
            source_id = "cea_nep_volume_ii"
        line_features.append(
            {
                "type": "Feature",
                "properties": {
                    "id": f"{cid}_line",
                    "interconnection_id": cid,
                    "name": props.get("name"),
                    "voltage_kv": str(props.get("voltage_kv", "")),
                    "status": props.get("status") or "Unknown",
                    "geometry_role": "gateway_stub" if connection_scope == "gateway_stub" else "inferred_connector",
                    "connection_scope": connection_scope,
                    "trace_confidence": "medium" if connection_scope == "endpoint_connector" else "low",
                    "source_id": source_id,
                    "source_url": OFFICIAL_SOURCE_URLS.get(source_id, ""),
                    "nepal_node": props.get("nepal_node"),
                    "india_node": props.get("india_node") or india_label,
                    "length_km": round(line_length, 3),
                    "geometry_basis": basis,
                    "notes": (
                        "Endpoint connector only; Indian-side route is not drawn."
                        if connection_scope == "endpoint_connector"
                        else "Short gateway stub only; full Indian-side route is intentionally not guessed."
                    ),
                },
                "geometry": {"type": "LineString", "coordinates": [list(nepal_coord), list(india_coord)]},
            }
        )
        node_features.append(
            make_node(
                f"border_gateway_{cid}",
                nepal_coord,
                props.get("name", cid),
                "border_gateway",
                props.get("status", "Unknown"),
                str(props.get("voltage_kv", "")),
                "cross_border_interconnections.geojson Nepal-side point",
                "medium",
            )
        )
    return line_features, node_features, warnings


def point_toward(start: tuple[float, float], end: tuple[float, float], distance_km: float) -> tuple[float, float]:
    total = haversine_km(start, end)
    if total <= distance_km or total == 0:
        return end
    t = distance_km / total
    return (start[0] + (end[0] - start[0]) * t, start[1] + (end[1] - start[1]) * t)


def build_validation_rows(
    by_corridor: dict[str, list[dict[str, Any]]],
    connector_features: list[dict[str, Any]],
    manifest_sources: dict[str, dict[str, Any]],
    connector_summaries: dict[str, dict[str, Any]],
) -> tuple[list[dict[str, Any]], dict[str, float | None]]:
    connectors_by_corridor: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for feature in connector_features:
        connectors_by_corridor[feature["properties"]["corridor_id"]].append(feature)

    rows: list[dict[str, Any]] = []
    deltas: dict[str, float | None] = {}
    for corridor_id, features in sorted(by_corridor.items()):
        traced_length = sum(line_length_km(feature["geometry"]) for feature in features)
        connector_length = sum(line_length_km(feature["geometry"]) for feature in connectors_by_corridor.get(corridor_id, []))
        network_length = traced_length + connector_length
        override = ROUTE_LENGTH_OVERRIDES.get(corridor_id, {})
        official_route_km = override.get("official_route_km")
        official_circuit_km = override.get("official_circuit_km")
        comparison_length_km = override.get("comparison_length_km") or official_route_km
        manifest_row = (manifest_sources.get(corridor_id) or {}).get("chosen_length_row") or {}
        if official_route_km is None:
            official_route_km = manifest_row.get("official_length_km")
            comparison_length_km = official_route_km
        delta = None
        if isinstance(comparison_length_km, (int, float)) and comparison_length_km:
            delta = ((network_length - comparison_length_km) / comparison_length_km) * 100
        deltas[corridor_id] = delta
        confidence = min(
            [str(f["properties"].get("trace_confidence", "low")) for f in features],
            key=lambda v: {"high": 0, "medium": 1, "low": 2}.get(v, 3),
        )
        limit = LENGTH_DELTA_LIMITS_PCT.get(confidence, 25.0)
        warnings: list[str] = []
        if delta is not None and abs(delta) > limit:
            warnings.append(f"length delta {delta:.1f}% exceeds {limit:.0f}% {confidence}-confidence threshold")
        summary = connector_summaries.get(corridor_id, {})
        if summary.get("remaining_gap_count", 0):
            warnings.append(f"{summary['remaining_gap_count']} endpoint gaps remain outside snap threshold")
        if any(not f["properties"].get("status") for f in features):
            warnings.append("one or more source trace segments have missing status")
        if any(not source_id_for_trace(f["properties"]) for f in features):
            warnings.append("one or more source trace segments have missing source provenance")
        rows.append(
            {
                "corridor_id": corridor_id,
                "feature_count": len(features),
                "connector_count": len(connectors_by_corridor.get(corridor_id, [])),
                "official_route_km": round(float(official_route_km), 3) if isinstance(official_route_km, (int, float)) else None,
                "official_circuit_km": (
                    round(float(official_circuit_km), 3) if isinstance(official_circuit_km, (int, float)) else None
                ),
                "comparison_length_km": (
                    round(float(comparison_length_km), 3) if isinstance(comparison_length_km, (int, float)) else None
                ),
                "official_length_basis": override.get("basis") or manifest_row.get("notes") or "",
                "official_length_source_id": override.get("source_id") or manifest_row.get("source_id") or "",
                "traced_length_km": round(traced_length, 3),
                "connector_length_km": round(connector_length, 3),
                "network_length_km": round(network_length, 3),
                "length_delta_pct": round(delta, 2) if delta is not None else None,
                "snap_threshold_km": summary.get("snap_threshold_km", 0.0),
                "remaining_gap_count": summary.get("remaining_gap_count", 0),
                "max_remaining_gap_km": summary.get("max_remaining_gap_km", 0.0),
                "confidence": confidence,
                "downgrade_reasons": "; ".join(warnings),
            }
        )
    return rows, deltas


def rewrite_feature_deltas(network_features: list[dict[str, Any]], deltas: dict[str, float | None]) -> None:
    for feature in network_features:
        corridor_id = feature["properties"].get("corridor_id")
        delta = deltas.get(corridor_id)
        feature["properties"]["length_delta_pct"] = round(delta, 2) if delta is not None else None


def main() -> None:
    PROCESSED.mkdir(parents=True, exist_ok=True)
    traced = read_geojson(TRACED_PATH)
    curated = read_geojson(CURATED_PATH)
    place_anchors = read_geojson(PLACE_ANCHORS_PATH)
    interconnections = read_geojson(CROSS_BORDER_PATH)
    manifest_rows = load_manifest_rows()
    manifest_sources = manifest_sources_by_corridor(manifest_rows)
    place_by_id, label_to_id = make_place_indexes(place_anchors)

    by_corridor: dict[str, list[dict[str, Any]]] = defaultdict(list)
    endpoints: list[Endpoint] = []
    endpoints_by_corridor: dict[str, list[Endpoint]] = defaultdict(list)
    for feature in traced.get("features", []):
        props = feature["properties"]
        corridor_id = props["corridor_id"]
        by_corridor[corridor_id].append(feature)
        start, end = endpoint_coords(feature["geometry"])
        for suffix, coord in (("from", start), ("to", end)):
            endpoint = Endpoint(
                key=f"{props.get('segment_id', corridor_id)}:{suffix}",
                corridor_id=corridor_id,
                feature=feature,
                coord=coord,
                end=suffix,
            )
            endpoints.append(endpoint)
            endpoints_by_corridor[corridor_id].append(endpoint)

    trace_nodes, node_centers = cluster_endpoint_nodes(endpoints)

    anchor_nodes: list[dict[str, Any]] = []
    curated_by_id = {f["properties"]["id"]: f for f in curated.get("features", [])}
    for feature in curated.get("features", []):
        props = feature["properties"]
        for label in props.get("anchor_chain", []):
            anchor_id = label_to_id.get(normalize_id(label))
            if not anchor_id or f"grid_{anchor_id}" in node_centers:
                continue
            anchor = place_by_id[anchor_id]
            node_centers[f"grid_{anchor_id}"] = (anchor["lon"], anchor["lat"])
            anchor_nodes.append(
                make_node(
                    f"grid_{anchor_id}",
                    (anchor["lon"], anchor["lat"]),
                    anchor["label"],
                    "grid_hub",
                    props.get("status", "Unknown"),
                    str(props.get("voltage_kv", "")),
                    "processed place anchor referenced by curated transmission corridor",
                    "medium",
                    anchor_id,
                )
            )

    cross_border_lines, border_nodes, cross_border_warnings = build_cross_border_lines(interconnections, place_by_id)

    empty_deltas = {corridor_id: None for corridor_id in by_corridor}
    connectors, gaps, connector_summaries = build_connectors_and_gaps(by_corridor, endpoints_by_corridor, empty_deltas)
    validation_rows, deltas = build_validation_rows(by_corridor, connectors, manifest_sources, connector_summaries)
    connectors, gaps, connector_summaries = build_connectors_and_gaps(by_corridor, endpoints_by_corridor, deltas)
    validation_rows, deltas = build_validation_rows(by_corridor, connectors, manifest_sources, connector_summaries)

    network_features: list[dict[str, Any]] = []
    endpoint_node_lookup = {endpoint.key: endpoint.node_id for endpoint in endpoints}
    for feature in traced.get("features", []):
        props = feature["properties"]
        start_key = f"{props.get('segment_id', props['corridor_id'])}:from"
        end_key = f"{props.get('segment_id', props['corridor_id'])}:to"
        length = line_length_km(feature["geometry"])
        network_features.append(
            {
                "type": "Feature",
                "properties": source_feature_props(
                    props,
                    endpoint_node_lookup[start_key],
                    endpoint_node_lookup[end_key],
                    length,
                    deltas.get(props["corridor_id"]),
                ),
                "geometry": feature["geometry"],
            }
        )
    network_features.extend(connectors)
    rewrite_feature_deltas(network_features, deltas)

    all_nodes = trace_nodes + anchor_nodes + border_nodes

    write_geojson(NETWORK_PATH, network_features)
    write_geojson(NODES_PATH, all_nodes)
    write_geojson(CROSS_BORDER_LINES_PATH, cross_border_lines)
    write_geojson(GAP_REPORT_PATH, gaps)

    VALIDATION_JSON_PATH.write_text(
        json.dumps(
            {
                "generated_from": {
                    "traced_segments": str(TRACED_PATH),
                    "curated_corridors": str(CURATED_PATH),
                    "manifest": str(TRACE_MANIFEST_PATH),
                },
                "snap_thresholds_km": SNAP_THRESHOLDS_KM,
                "length_delta_limits_pct": LENGTH_DELTA_LIMITS_PCT,
                "corridors": validation_rows,
            },
            indent=2,
        )
    )
    with VALIDATION_CSV_PATH.open("w", newline="", encoding="utf-8") as handle:
        fieldnames = list(validation_rows[0].keys()) if validation_rows else []
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(validation_rows)

    build_warnings: list[str] = []
    for row in validation_rows:
        if row["downgrade_reasons"]:
            build_warnings.append(f"{row['corridor_id']}: {row['downgrade_reasons']}")
    build_warnings.extend(cross_border_warnings)
    BUILD_REPORT_PATH.write_text(
        json.dumps(
            {
                "network_features": len(network_features),
                "source_trace_features": sum(1 for f in network_features if f["properties"]["geometry_role"] == "source_trace"),
                "manual_trace_features": sum(1 for f in network_features if f["properties"]["geometry_role"] == "manual_trace"),
                "inferred_connector_features": sum(
                    1 for f in network_features if f["properties"]["geometry_role"] == "inferred_connector"
                ),
                "network_nodes": len(all_nodes),
                "cross_border_line_features": len(cross_border_lines),
                "trace_gap_features": len(gaps),
                "corridor_source_coverage": {
                    cid: {
                        "manifest_source_ids": manifest_sources.get(cid, {}).get("source_ids", []),
                        "curated_corridor_present": cid in curated_by_id,
                    }
                    for cid in sorted(by_corridor)
                },
                "official_source_urls": OFFICIAL_SOURCE_URLS,
                "warnings": build_warnings,
            },
            indent=2,
        )
    )
    print(f"Wrote {NETWORK_PATH.relative_to(ROOT)} ({len(network_features)} features)")
    print(f"Wrote {NODES_PATH.relative_to(ROOT)} ({len(all_nodes)} nodes)")
    print(f"Wrote {CROSS_BORDER_LINES_PATH.relative_to(ROOT)} ({len(cross_border_lines)} features)")
    print(f"Wrote {VALIDATION_JSON_PATH.relative_to(ROOT)}")
    if build_warnings:
        print(f"Warnings: {len(build_warnings)}")


if __name__ == "__main__":
    main()
