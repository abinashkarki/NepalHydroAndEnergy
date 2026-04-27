from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


ROOT = Path("/Users/hi/projects/nepalEnergy")
PROCESSED = ROOT / "data" / "processed" / "maps"
MANIFEST_DIR = ROOT / "data" / "processed" / "corridor_tracing" / "manifests"
DOCS = ROOT / "docs" / "maps"

CORRIDORS_PATH = PROCESSED / "transmission_corridors.geojson"
NETWORK_PATH = PROCESSED / "transmission_corridor_traced_network.geojson"
VALIDATION_PATH = PROCESSED / "transmission_corridor_validation_report.json"
BUILD_REPORT_PATH = PROCESSED / "transmission_network_build_report.json"
CROSS_BORDER_POINTS_PATH = PROCESSED / "cross_border_interconnections.geojson"
CROSS_BORDER_LINES_PATH = PROCESSED / "cross_border_interconnection_lines.geojson"
TRACE_MANIFEST_PATH = MANIFEST_DIR / "corridor_trace_manifest.json"
SOURCE_INVENTORY_PATH = MANIFEST_DIR / "corridor_source_inventory.json"

DOSSIER_JSON_PATH = PROCESSED / "transmission_corridor_dossiers.json"
DOSSIER_CSV_PATH = PROCESSED / "transmission_corridor_dossiers.csv"
CROSS_BORDER_DOSSIER_JSON_PATH = PROCESSED / "cross_border_interconnection_dossiers.json"
CROSS_BORDER_DOSSIER_CSV_PATH = PROCESSED / "cross_border_interconnection_dossiers.csv"
GRID_CONFIDENCE_REPORT_PATH = DOCS / "grid_confidence_report.md"

PRIORITY_CORRIDORS = {
    "mca_central_400": 1,
    "hddi_400": 2,
    "hetauda_bharatpur_bardaghat_220": 3,
    "udipur_damauli_bharatpur_220": 4,
    "marsyangdi_upper_220": 5,
    "kabeli_132": 6,
    "solu_tingla_mirchaiya_132": 7,
    "western_132_backbone": 8,
    "chameliya_attariya_132": 9,
    "kohalpur_surkhet_dailekh_132": 10,
}

SOURCE_CLASS_RANK = {
    "geospatial_vector_map": 100,
    "alignment_atlas": 95,
    "rap": 88,
    "iee": 84,
    "environmental_study": 78,
    "feasibility_summary": 64,
    "annual_report": 58,
    "annual_book": 60,
    "master_plan_summary": 52,
    "master_plan_report": 50,
    "regional_plan": 44,
}

CYCLE_SOURCE_CHECKS = {
    "mcc_nepal_compact": {
        "title": "MCC Nepal Compact",
        "url": "https://assets.mcc.gov/content/uploads/compact-nepal.pdf",
        "applies_to": ["mca_central_400"],
        "use": "Authoritative topology and component-length basis for the five MCA 400 kV transmission segments.",
    },
    "mcc_fy2025_annual_report": {
        "title": "MCC Fiscal Year 2025 Annual Report",
        "url": "https://www.mcc.gov/resources/doc/annual-report-2025/",
        "applies_to": ["mca_central_400", "gorakhpur_new_butwal"],
        "use": "Current implementation status and program-length context.",
    },
    "pib_lok_sabha_2026_04_02": {
        "title": "Government of India PIB Lok Sabha reply, April 2 2026",
        "url": "https://www.pib.gov.in/PressReleseDetailm.aspx?PRID=2248339&lang=1&reg=3",
        "applies_to": ["cross_border_interconnections"],
        "use": "Official current list of Nepal-India cross-border transmission links.",
    },
    "cea_nep_volume_ii": {
        "title": "CEA National Electricity Plan Volume II: Transmission",
        "url": "https://cea.nic.in/wp-content/uploads/notification/2024/10/National_Electricity_Plan_Volume_II_Transmission.pdf",
        "applies_to": ["cross_border_interconnections"],
        "use": "India-side planning context for future and implementation-stage interconnections.",
    },
}

CYCLE_FOCUS = [
    "Hold the default public layer to source-aware geometry, not visual completeness.",
    "Upgrade corridor dossiers before upgrading linework.",
    "Prioritize 400 kV backbone/export links, then 220 kV domestic corridors, then weak 132 kV evacuation corridors.",
    "Keep all inferred connectors visually distinct and leave larger gaps in QA.",
]


def load_json(path: Path) -> Any:
    return json.loads(path.read_text())


def source_quality(row: dict[str, Any], inventory_by_id: dict[str, dict[str, Any]]) -> tuple[int, str]:
    source_id = row.get("source_id")
    inv = inventory_by_id.get(source_id, {})
    doc_class = inv.get("document_class") or ""
    role = row.get("source_role") or inv.get("primary_use") or ""
    score = SOURCE_CLASS_RANK.get(doc_class, 40)
    if role == "trace_grade_candidate":
        score += 5
    elif role == "manual_route_basis":
        score += 8
    elif role == "status_reference":
        score -= 12
    elif role == "reference_only":
        score -= 20
    return max(0, min(100, score)), doc_class or role or "unknown"


def geometry_grade(role_counts: Counter[str], validation: dict[str, Any]) -> str:
    if role_counts.get("source_trace") and validation.get("remaining_gap_count", 0) == 0:
        return "source-grade route"
    if role_counts.get("source_trace"):
        return "source-backed fragments with QA gaps"
    if role_counts.get("manual_trace") and validation.get("remaining_gap_count", 0) == 0:
        return "document-grounded corridor"
    if role_counts.get("manual_trace"):
        return "document-grounded corridor with QA gaps"
    return "conceptual / not traced"


def public_decision(validation: dict[str, Any], grade: str, best_score: int) -> str:
    warnings = validation.get("downgrade_reasons") or ""
    if "route-grade atlas trace" in grade and not warnings and best_score >= 80:
        return "default-visible, high confidence"
    if "route-grade RAP trace" in grade and not warnings and best_score >= 80 and validation.get("confidence") == "high":
        return "default-visible, high confidence"
    if "route-grade RAP trace" in grade and not warnings and best_score >= 80:
        return "default-visible, caveated"
    if "source-grade route" in grade and not warnings and best_score >= 80:
        return "default-visible, high confidence"
    if best_score >= 75 and "length delta" not in warnings:
        return "default-visible, caveated"
    if "conceptual" in grade:
        return "context-only until route-grade source exists"
    return "default-visible with explicit QA warning"


def next_action(corridor_id: str, validation: dict[str, Any], grade: str) -> str:
    if corridor_id == "mca_central_400":
        if not validation.get("downgrade_reasons"):
            return "Resolved in the atlas-trace layer; keep sheet provenance and status under periodic review."
        return "Select exact MCA Annex D-1 sheet ranges and replace any RPGCL-overview sections where the atlas gives better route geometry."
    if corridor_id == "hddi_400":
        if not validation.get("downgrade_reasons"):
            return "Resolved into a RAP-controlled public trace with mixed segment status; keep looking for tower/alignment sheets if a higher-precision route becomes available."
        return "Use the World Bank RAP route map to resolve the large remaining RPGCL extraction gaps and reconcile the 288 route-km basis."
    if corridor_id == "hetauda_bharatpur_bardaghat_220":
        if not validation.get("downgrade_reasons"):
            return "Resolved into two source-controlled public segments; keep searching for a downloadable route map or alignment sheet for future precision."
        return "Find route-grade RAP/EIA or official line map; current official-vector extraction appears longer than the route-km interpretation."
    if corridor_id == "udipur_damauli_bharatpur_220":
        if not validation.get("downgrade_reasons"):
            return "Resolved from the NEA Marsyangdi RAP trace; keep Khudi-Udipur scope separate until separately sourced."
        return "Re-check the NEA Marsyangdi RAP route sketch against any newer project alignment source."
    if corridor_id == "marsyangdi_upper_220":
        return "Keep as document-grounded; validate branch endpoints against upper Marsyangdi RAP and EIB CIA."
    if corridor_id == "kabeli_132":
        return "Digitize branch structure from the Kabeli IEE route figures; keep Godak and Phidim/Amarpur branches explicit."
    if corridor_id == "solu_tingla_mirchaiya_132":
        return "Search for route-grade IEE/RAP/alignment material; keep 90 route-km vs 180 circuit-km caveat until resolved."
    if corridor_id == "western_132_backbone":
        return "Keep as operational 132 kV backbone context; upgrade only if a higher-resolution NEA/utility route packet becomes available."
    if corridor_id == "chameliya_attariya_132":
        return "Keep as operational far-west hydro evacuation context; verify future Chameliya-Jauljibi interface separately from this domestic 132 kV line."
    if corridor_id == "kohalpur_surkhet_dailekh_132":
        return "Track construction status until energised; keep visually distinct from operational western 132 kV backbone."
    if validation.get("remaining_gap_count", 0):
        return "Resolve remaining QA gaps or document why they must stay open."
    if "conceptual" in grade:
        return "Recover a route-grade source before moving into the connected traced network."
    return "Monitor status/source freshness."


def build_corridor_dossiers() -> list[dict[str, Any]]:
    corridors = {f["properties"]["id"]: f["properties"] for f in load_json(CORRIDORS_PATH)["features"]}
    network = load_json(NETWORK_PATH)["features"]
    validation_rows = {row["corridor_id"]: row for row in load_json(VALIDATION_PATH)["corridors"]}
    build_report = load_json(BUILD_REPORT_PATH)
    manifest_rows = load_json(TRACE_MANIFEST_PATH)
    inventory = load_json(SOURCE_INVENTORY_PATH)
    inventory_by_id = {row["source_id"]: row for row in inventory}

    rows_by_corridor: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in manifest_rows:
        rows_by_corridor[row["corridor_id"]].append(row)
    network_by_corridor: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for feature in network:
        network_by_corridor[feature["properties"]["corridor_id"]].append(feature)

    all_ids = sorted(set(corridors) | set(network_by_corridor) | set(validation_rows))
    dossiers: list[dict[str, Any]] = []
    for corridor_id in all_ids:
        props = corridors.get(corridor_id, {})
        features = network_by_corridor.get(corridor_id, [])
        role_counts = Counter(f["properties"].get("geometry_role") for f in features)
        method_counts = Counter(f["properties"].get("trace_method") for f in features)
        validation = validation_rows.get(corridor_id, {})
        sources = rows_by_corridor.get(corridor_id, [])
        scored_sources = []
        for source in sources:
            score, source_class = source_quality(source, inventory_by_id)
            scored_sources.append((score, source_class, source))
        scored_sources.sort(key=lambda item: item[0], reverse=True)
        best_score = scored_sources[0][0] if scored_sources else 0
        best_source = scored_sources[0][2] if scored_sources else {}
        grade = geometry_grade(role_counts, validation)
        if method_counts.get("manual_atlas_trace") and validation.get("remaining_gap_count", 0) == 0:
            grade = "route-grade atlas trace"
        if method_counts.get("manual_rap_trace") and validation.get("remaining_gap_count", 0) == 0:
            grade = "route-grade RAP trace"
        source_ids = sorted({s.get("source_id") for s in sources if s.get("source_id")})
        dossier = {
            "corridor_id": corridor_id,
            "priority_rank": PRIORITY_CORRIDORS.get(corridor_id, 99),
            "name": props.get("name") or (features[0]["properties"].get("name") if features else corridor_id),
            "voltage_kv": props.get("voltage_kv") or (features[0]["properties"].get("voltage_kv") if features else ""),
            "status": props.get("status") or (features[0]["properties"].get("status") if features else "Unknown"),
            "category": props.get("category", ""),
            "anchor_chain": " -> ".join(props.get("anchor_chain", [])),
            "geometry_grade": grade,
            "public_decision": public_decision(validation, grade, best_score),
            "best_source_id": best_source.get("source_id", ""),
            "best_source_class": scored_sources[0][1] if scored_sources else "",
            "best_source_page_or_sheet": best_source.get("figure_or_sheet", ""),
            "source_quality_score": best_score,
            "source_ids": ", ".join(source_ids),
            "network_feature_count": len(features),
            "source_trace_count": role_counts.get("source_trace", 0),
            "manual_trace_count": role_counts.get("manual_trace", 0),
            "inferred_connector_count": role_counts.get("inferred_connector", 0),
            "official_route_km": validation.get("official_route_km"),
            "official_circuit_km": validation.get("official_circuit_km"),
            "comparison_length_km": validation.get("comparison_length_km"),
            "network_length_km": validation.get("network_length_km"),
            "length_delta_pct": validation.get("length_delta_pct"),
            "remaining_gap_count": validation.get("remaining_gap_count", 0),
            "max_remaining_gap_km": validation.get("max_remaining_gap_km", 0.0),
            "downgrade_reasons": validation.get("downgrade_reasons", ""),
            "next_action": next_action(corridor_id, validation, grade),
            "default_layer_ready": public_decision(validation, grade, best_score).startswith("default-visible"),
            "source_coverage_note": build_report.get("corridor_source_coverage", {}).get(corridor_id, {}),
        }
        dossiers.append(dossier)
    return sorted(dossiers, key=lambda row: (row["priority_rank"], row["corridor_id"]))


def build_cross_border_dossiers() -> list[dict[str, Any]]:
    points = {f["properties"]["id"]: f["properties"] for f in load_json(CROSS_BORDER_POINTS_PATH)["features"]}
    lines = load_json(CROSS_BORDER_LINES_PATH)["features"]
    dossiers = []
    for feature in lines:
        props = feature["properties"]
        cid = props["interconnection_id"]
        point = points.get(cid, {})
        endpoint_quality = "defensible endpoint connector" if props.get("connection_scope") == "endpoint_connector" else "gateway stub only"
        if point.get("status") != props.get("status"):
            status_alignment = "status mismatch"
        else:
            status_alignment = "status aligned"
        if props.get("status") == "Operational" and props.get("connection_scope") == "gateway_stub":
            decision = "default-visible, operational point plus conservative stub"
        elif props.get("status") == "Operational":
            decision = "default-visible, operational endpoint connector"
        else:
            decision = "default-visible, non-operational dashed/faint"
        dossiers.append(
            {
                "interconnection_id": cid,
                "name": props.get("name"),
                "voltage_kv": props.get("voltage_kv"),
                "status": props.get("status"),
                "nepal_node": props.get("nepal_node"),
                "india_node": props.get("india_node"),
                "connection_scope": props.get("connection_scope"),
                "endpoint_quality": endpoint_quality,
                "trace_confidence": props.get("trace_confidence"),
                "source_id": props.get("source_id"),
                "source_url": props.get("source_url"),
                "length_km": props.get("length_km"),
                "status_alignment": status_alignment,
                "public_decision": decision,
                "next_action": (
                    "Find source-backed India-side substation coordinates before drawing more than a stub."
                    if props.get("connection_scope") == "gateway_stub"
                    else "Keep endpoint connector; do not draw full India-side route without a route source."
                ),
            }
        )
    return dossiers


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def md_table(rows: list[dict[str, Any]], fields: list[str]) -> str:
    header = "| " + " | ".join(fields) + " |"
    sep = "| " + " | ".join("---" for _ in fields) + " |"
    body = []
    for row in rows:
        values = []
        for field in fields:
            value = row.get(field, "")
            if isinstance(value, float):
                value = f"{value:.1f}"
            values.append(str(value).replace("\n", " ").replace("|", "/"))
        body.append("| " + " | ".join(values) + " |")
    return "\n".join([header, sep, *body])


def build_markdown_report(corridors: list[dict[str, Any]], cross_border: list[dict[str, Any]]) -> str:
    warning_rows = [row for row in corridors if row.get("downgrade_reasons")]
    high_priority = [row for row in corridors if row["priority_rank"] < 99]
    source_counts = Counter(row["geometry_grade"] for row in corridors)
    status_counts = Counter(row["status"] for row in cross_border)
    lines = [
        "# Grid Confidence Report",
        "",
        "Purpose: define the current product-quality state of the public grid map and the next source-quality cycle.",
        "",
        "## Product rule",
        "",
        "The map should optimize for faithful public understanding, not visual completeness. A line can be default-visible only when its status, voltage, endpoints, source basis, and geometry role are auditable. Bigger geometry gaps stay visible in QA instead of being closed with speculative linework.",
        "",
        "## Current state",
        "",
        f"- Corridor dossiers: {len(corridors)}",
        f"- Cross-border dossiers: {len(cross_border)}",
        f"- Corridor geometry grades: {dict(source_counts)}",
        f"- Cross-border status mix: {dict(status_counts)}",
        f"- Corridors with explicit QA warnings: {len(warning_rows)}",
        "",
        "## Next-cycle focus",
        "",
        *[f"- {item}" for item in CYCLE_FOCUS],
        "",
        "## Priority corridor dossiers",
        "",
        md_table(
            high_priority,
            [
                "priority_rank",
                "corridor_id",
                "status",
                "geometry_grade",
                "source_quality_score",
                "length_delta_pct",
                "remaining_gap_count",
                "public_decision",
            ],
        ),
        "",
        "## Cross-border dossiers",
        "",
        md_table(
            cross_border,
            [
                "interconnection_id",
                "status",
                "connection_scope",
                "endpoint_quality",
                "source_id",
                "public_decision",
            ],
        ),
        "",
        "## QA warnings to work down",
        "",
    ]
    if warning_rows:
        lines.append(
            md_table(
                warning_rows,
                ["corridor_id", "downgrade_reasons", "next_action"],
            )
        )
    else:
        lines.append("No corridor-level QA warnings.")
    lines.extend(
        [
            "",
            "## Source checks for this cycle",
            "",
            md_table(
                [
                    {
                        "source_id": key,
                        "title": value["title"],
                        "url": value["url"],
                        "use": value["use"],
                    }
                    for key, value in CYCLE_SOURCE_CHECKS.items()
                ],
                ["source_id", "title", "url", "use"],
            ),
            "",
            "## Stop rule",
            "",
            "This phase is publishable when every default-visible major corridor has an auditable source basis, no planned or implementation-stage line renders as operational, inferred connectors remain visually distinct, and all remaining geometry gaps are documented in the QA layer rather than silently bridged.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    corridors = build_corridor_dossiers()
    cross_border = build_cross_border_dossiers()
    DOSSIER_JSON_PATH.write_text(json.dumps({"corridors": corridors, "source_checks": CYCLE_SOURCE_CHECKS}, indent=2))
    CROSS_BORDER_DOSSIER_JSON_PATH.write_text(json.dumps({"interconnections": cross_border}, indent=2))
    write_csv(DOSSIER_CSV_PATH, corridors)
    write_csv(CROSS_BORDER_DOSSIER_CSV_PATH, cross_border)
    GRID_CONFIDENCE_REPORT_PATH.write_text(build_markdown_report(corridors, cross_border))
    print(f"Wrote {DOSSIER_JSON_PATH.relative_to(ROOT)}")
    print(f"Wrote {CROSS_BORDER_DOSSIER_JSON_PATH.relative_to(ROOT)}")
    print(f"Wrote {GRID_CONFIDENCE_REPORT_PATH.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
