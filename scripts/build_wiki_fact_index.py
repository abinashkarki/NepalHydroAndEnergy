#!/usr/bin/env python3
"""Build structured facts for factual Seek queries in the wiki explorer."""
from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
SHARED = ROOT / "wiki" / "explorer" / "shared"
META = SHARED / "wiki-page-meta.json"
OUT = SHARED / "wiki-fact-index.json"
MAPS = ROOT / "data" / "processed" / "maps"

SOURCES = [
    ("hydro", "top_capacity_project_annotations", MAPS / "top_capacity_project_annotations.geojson"),
    ("hydro", "hydropower_project_display_points", MAPS / "hydropower_project_display_points.geojson"),
    ("storage", "storage_shortlist_annotations", MAPS / "storage_shortlist_annotations.geojson"),
    ("solar", "solar_plants", MAPS / "solar_plants.geojson"),
    ("hydro", "priority_project_watchlist", MAPS / "priority_project_watchlist.geojson"),
]

RELATED_BY_DOMAIN = {
    "solar": [
        "nea-960mw-solar-tender",
        "data-layer-solar-plants-nea-awards",
        "solar-hydro-complementarity",
        "solar-role-in-winter-deficit",
        "claim-solar-cheaper-than-small-hydro",
    ],
    "hydro": [
        "data-layer-top-10-capacity-projects",
        "data-layer-hydropower-operating",
        "data-layer-hydropower-construction",
        "claim-mw-not-equal-value",
        "storage-deficit",
    ],
    "storage": [
        "data-layer-storage-shortlist",
        "storage-deficit",
        "firm-power",
        "seasonal-mismatch",
    ],
}


def norm_name(value: str) -> str:
    text = re.sub(r"[^a-z0-9]+", " ", str(value or "").lower()).strip()
    text = re.sub(r"\b(hydropower|project|storage|hep|hpp|hp)\b", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def slugify(value: str) -> str:
    return re.sub(r"(^-|-$)", "", re.sub(r"[^a-z0-9]+", "-", str(value or "").lower()))


def _safe_float(value, default=None):
    try:
        return float(value) if value is not None else default
    except (TypeError, ValueError):
        return default


def status_norm(raw: str) -> str:
    text = str(raw or "").lower()
    if any(term in text for term in ["generation", "operation", "operating"]):
        return "operating"
    if "construction" in text:
        return "construction"
    if any(term in text for term in ["survey", "planned", "proposed", "tender", "pre-ppa", "radar"]):
        return "survey"
    return "unknown"


def title_slug_lookup() -> dict[str, str]:
    meta = json.loads(META.read_text(encoding="utf-8"))
    lookup: dict[str, str] = {}
    for page in meta.get("pages", []):
        slug = page["slug"]
        title = page.get("title") or slug
        lookup[norm_name(title)] = slug
        lookup[norm_name(slug.replace("-", " "))] = slug
    # High-confidence project-source aliases where the project is documented by a source page.
    lookup.setdefault(norm_name("Mugu Karnali Storage HEP"), "mugu-karnali-feasibility-2025")
    return lookup


def existing_slugs() -> set[str]:
    meta = json.loads(META.read_text(encoding="utf-8"))
    return {page["slug"] for page in meta.get("pages", [])}


def load_features(path: Path) -> list[dict]:
    if not path.exists():
        return []
    data = json.loads(path.read_text(encoding="utf-8"))
    return [feature.get("properties", {}) for feature in data.get("features", [])]


def better_capacity(new: dict, old: dict) -> bool:
    return float(new.get("capacity_mw") or new.get("installed_mw") or 0) > float(old.get("capacity_mw") or old.get("installed_mw") or 0)


def confidence_for(layer: str, props: dict) -> str:
    if layer in {"top_capacity_project_annotations", "priority_project_watchlist"}:
        return "high"
    if props.get("confidence"):
        return str(props["confidence"]).lower()
    if props.get("precision_tier") == "river_reference":
        return "medium"
    return "medium"


def project_name(props: dict) -> str:
    return str(props.get("project") or props.get("name") or props.get("label_title") or "").strip()


def fact_from_props(domain: str, layer: str, props: dict, lookup: dict[str, str]) -> dict | None:
    name = project_name(props)
    if not name:
        return None
    capacity = props.get("capacity_mw", props.get("installed_mw"))
    try:
        capacity = float(capacity) if capacity is not None else None
    except (TypeError, ValueError):
        capacity = None
    raw_status = props.get("license_type") or props.get("status") or props.get("category") or ""
    status = status_norm(raw_status)
    key = norm_name(name)
    fact_domain = "hydro" if domain == "storage" else domain
    layer_key = layer
    if layer == "top_capacity_project_annotations":
        layer_key = "top_capacity"
    elif layer == "priority_project_watchlist":
        layer_key = "priority_watchlist"
    elif layer == "storage_shortlist_annotations":
        layer_key = "storage_shortlist"
    if layer == "hydropower_project_display_points":
        layer_key = {
            "operating": "hydropower_operating",
            "construction": "hydropower_construction",
            "survey": "hydropower_survey",
        }.get(status, "hydropower_survey")
    return {
        "id": f"{domain}:{slugify(name)}",
        "key": key,
        "domain": fact_domain,
        "facets": sorted({fact_domain, domain}),
        "name": name,
        "wiki_slug": lookup.get(key) or lookup.get(norm_name(name.replace("HPP", "").replace("HEP", ""))) or "",
        "capacity_mw": capacity,
        "installed_mw": _safe_float(props.get("installed_mw"), capacity),
        "status": status,
        "status_raw": str(raw_status) if raw_status else "",
        "river": props.get("river") or "",
        "basin": props.get("basin") or props.get("river") or "",
        "district": str(props.get("district") or "").replace("_", " ").title(),
        "province": props.get("province") or "",
        "promoter": props.get("promoter") or props.get("owner") or props.get("bidder") or "",
        "source_layer": layer,
        "feature_ref": {
            "layer": layer_key,
            "id": props.get("id") or props.get("project") or props.get("name") or props.get("label_title") or name,
            "match_field": "project" if props.get("project") else ("name" if props.get("name") else "label_title"),
            "match_value": props.get("project") or props.get("name") or props.get("label_title") or name,
        },
        "sources": [layer],
        "source_note": props.get("source_note") or "",
        "rank": props.get("rank"),
        "annual_energy_gwh": props.get("annual_energy_gwh") or props.get("annual_design_energy_gwh"),
        "dry_energy_gwh": props.get("dry_energy_gwh") or props.get("dry_season_energy_gwh"),
        "dry_share_pct": props.get("dry_share_pct"),
        "confidence": confidence_for(layer, props),
        "gross_head_m": _safe_float(props.get("gross_head_m")),
        "dam_height_m": _safe_float(props.get("dam_height_m")),
        "dam_type": props.get("dam_type") or "",
        "num_units": props.get("num_units"),
        "unit_capacity_mw": _safe_float(props.get("unit_capacity_mw")),
        "turbine_type": props.get("turbine_type") or "",
        "project_type": props.get("project_type") or "",
        "q_design": props.get("q_design") or "",
        "total_storage_mcm": _safe_float(props.get("total_storage_mcm")),
        "effective_storage_mcm": _safe_float(props.get("effective_storage_mcm")),
        "total_cost_usd_m": _safe_float(props.get("total_cost_usd_m")),
        "ppa_rate_wet_npr_kwh": _safe_float(props.get("ppa_rate_wet_npr_kwh")),
        "ppa_rate_dry_npr_kwh": _safe_float(props.get("ppa_rate_dry_npr_kwh")),
        "developer": props.get("developer") or "",
        "cod_year": props.get("cod_year"),
        "plant_load_factor_pct": _safe_float(props.get("plant_load_factor_pct")),
    }


def merge_fact(old: dict, new: dict) -> dict:
    merged = dict(old)
    merged["sources"] = sorted(set(old.get("sources", [])) | set(new.get("sources", [])))
    source_score = {
        "top_capacity_project_annotations": 5,
        "priority_project_watchlist": 4,
        "storage_shortlist_annotations": 3,
        "solar_plants": 3,
        "hydropower_project_display_points": 2,
    }
    if source_score.get(new["source_layer"], 0) > source_score.get(old["source_layer"], 0) or better_capacity(new, old):
        for field in ["capacity_mw", "installed_mw", "rank", "source_layer", "source_note", "confidence"]:
            if new.get(field) not in (None, ""):
                merged[field] = new[field]
        if new.get("feature_ref"):
            merged["feature_ref"] = new["feature_ref"]
    for field in ["wiki_slug", "river", "basin", "district", "province", "promoter", "status_raw"]:
        if not merged.get(field) and new.get(field):
            merged[field] = new[field]
    if merged.get("status") in {"unknown", ""} and new.get("status") != "unknown":
        merged["status"] = new["status"]
    merged["facets"] = sorted(set(merged.get("facets", [])) | set(new.get("facets", [])))
    return merged


def main() -> None:
    lookup = title_slug_lookup()
    slugs = existing_slugs()
    facts_by_key: dict[str, dict] = {}
    for domain, layer, path in SOURCES:
        for props in load_features(path):
            fact = fact_from_props(domain, layer, props, lookup)
            if not fact:
                continue
            key = fact.pop("key")
            facts_by_key[key] = merge_fact(facts_by_key[key], fact) if key in facts_by_key else fact
    facts = sorted(
        facts_by_key.values(),
        key=lambda f: (f.get("domain", ""), -(f.get("capacity_mw") or 0), f.get("name", "")),
    )
    for fact in facts:
        domains = [d for d in fact.get("facets", []) if d in RELATED_BY_DOMAIN]
        if fact.get("domain") in RELATED_BY_DOMAIN and fact["domain"] not in domains:
            domains.insert(0, fact["domain"])
        related: list[str] = []
        for domain in domains:
            for slug in RELATED_BY_DOMAIN[domain]:
                if slug in slugs and slug != fact.get("wiki_slug") and slug not in related:
                    related.append(slug)
        fact["related_slugs"] = related[:5]
        fact["slug"] = fact.get("wiki_slug", "")
    out = {
        "version": 1,
        "facts": facts,
        "stats": {
            "facts": len(facts),
            "sources": [layer for _, layer, _ in SOURCES],
        },
    }
    OUT.write_text(json.dumps(out, separators=(",", ":"), ensure_ascii=False), encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)} ({len(facts)} facts)")


if __name__ == "__main__":
    main()
