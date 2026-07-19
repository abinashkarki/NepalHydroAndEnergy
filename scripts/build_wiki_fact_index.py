#!/usr/bin/env python3
"""Build structured facts for factual Seek queries in the wiki explorer."""
from __future__ import annotations

import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
SHARED = ROOT / "wiki" / "explorer" / "shared"
META = SHARED / "wiki-page-meta.json"
OUT = SHARED / "wiki-fact-index.json"
MAPS = ROOT / "data" / "processed" / "maps"
PROJECT_SPECS = ROOT / "data" / "project_specs.csv"
PROJECT_EVENTS = ROOT / "data" / "project_events.csv"
PROJECT_BLOCKERS = ROOT / "data" / "project_blockers.csv"
CORRIDOR_SPECS = ROOT / "data" / "corridor_specs.csv"

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
    "transmission": [
        "claim-transmission-immediate-blocker",
        "intervention-transmission-completion",
        "nepal-transmission-landscape-2025",
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
    text = str(raw or "").lower().strip()
    if text in {"operating", "under-construction", "partially-operational", "licensed", "survey", "pre-construction", "stalled", "cancelled", "conceptual", "planned", "unknown"}:
        return text
    if any(term in text for term in ["pre-construction", "pre construction"]):
        return "pre-construction"
    if "stalled" in text:
        return "stalled"
    if any(term in text for term in ["cancelled", "canceled", "abandoned"]):
        return "cancelled"
    if "conceptual" in text:
        return "conceptual"
    if any(term in text for term in ["survey", "planned", "proposed", "tender", "pre-ppa", "radar"]):
        return "survey"
    # Check for operating first (explicit terms)
    if any(term in text for term in ["operation", "operating"]):
        return "operating"
    if "construction" in text:
        return "under-construction"
    if "generation" in text or "licence" in text or "license" in text:
        return "licensed"
    return "unknown"


def status_display(value: str) -> str:
    labels = {
        "operating": "Operating",
        "under-construction": "Under construction",
        "licensed": "Generation licence",
        "partially-operational": "Partially operational",
        "survey": "Survey",
        "pre-construction": "Pre-construction",
        "stalled": "Stalled",
        "cancelled": "Cancelled",
        "conceptual": "Conceptual",
        "planned": "Planned",
        "unknown": "Unknown",
    }
    return labels.get(str(value or "").strip().lower(), str(value or "").strip())


def status_priority(props: dict) -> int:
    if props.get("status") or props.get("delivery_status"):
        return 3
    if props.get("doed_primary_category") or props.get("doed_delivery_status"):
        return 2
    return 1 if (props.get("license_type") or props.get("category")) else 0


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


SOLAR_SPECS_CSV = ROOT / "data" / "solar_project_specs.csv"


def load_solar_specs_lookup() -> dict[str, dict[str, str]]:
    if not SOLAR_SPECS_CSV.exists():
        return {}
    lookup: dict[str, dict[str, str]] = {}
    with SOLAR_SPECS_CSV.open(newline="", encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            fid = (row.get("feature_id") or "").strip()
            if fid:
                lookup[fid] = row
    return lookup


def load_features(path: Path) -> list[dict]:
    if not path.exists():
        return []
    data = json.loads(path.read_text(encoding="utf-8"))
    return [feature.get("properties", {}) for feature in data.get("features", [])]


def load_csv_rows(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def page_titles_by_slug() -> dict[str, str]:
    meta = json.loads(META.read_text(encoding="utf-8"))
    return {page["slug"]: page.get("title") or page["slug"] for page in meta.get("pages", [])}


def apply_project_specs(facts_by_key: dict[str, dict], titles: dict[str, str]) -> None:
    """Overlay curated specs while retaining map-derived spatial references."""
    numeric_fields = {
        "capacity_mw", "gross_head_m", "dam_height_m", "num_units",
        "unit_capacity_mw", "annual_design_energy_gwh", "dry_season_energy_gwh",
        "dry_share_pct", "total_storage_mcm", "effective_storage_mcm",
        "total_cost_usd_m", "ppa_rate_wet_npr_kwh", "ppa_rate_dry_npr_kwh",
        "plant_load_factor_pct", "cod_year", "completion_pct",
    }
    field_map = {
        "annual_design_energy_gwh": "annual_energy_gwh",
        "dry_season_energy_gwh": "dry_energy_gwh",
    }
    text_fields = {
        "river", "source_note", "last_updated", "dam_type", "turbine_type",
        "project_type", "q_design", "developer", "concession_type",
        "lead_financier", "debt_equity_ratio",
    }
    for row in load_csv_rows(PROJECT_SPECS):
        slug = (row.get("slug") or "").strip()
        if not slug or slug not in titles:
            continue
        key = next(
            (key for key, fact in facts_by_key.items() if fact.get("wiki_slug") == slug or fact.get("registry_slug") == slug),
            norm_name(titles[slug]),
        )
        fact = facts_by_key.get(key)
        if fact is None:
            fact = {
                "id": f"project:{slug}", "domain": "project", "facets": ["hydro", "project-monitoring"],
                "name": titles[slug], "wiki_slug": slug,
                "feature_ref": {"layer": "project_specs", "id": slug, "match_field": "slug", "match_value": slug},
                "sources": [],
            }
            facts_by_key[key] = fact
        fact["wiki_slug"] = slug
        fact["registry_slug"] = slug
        fact["name"] = fact.get("name") or titles[slug]
        fact["source_layer"] = fact.get("source_layer") or "project_specs"
        fact["sources"] = sorted(set(fact.get("sources", [])) | {"project_specs"})
        for csv_field, raw_value in row.items():
            value = (raw_value or "").strip()
            if not value:
                continue
            out_field = field_map.get(csv_field, csv_field)
            if csv_field in numeric_fields:
                parsed = _safe_float(value)
                fact[out_field] = parsed if parsed is not None else value
            elif csv_field in text_fields:
                fact[out_field] = value
        fact["status"] = status_norm(row.get("status") or fact.get("status", ""))
        fact["status_raw"] = row.get("status") or fact.get("status_raw", "")
        fact["status_display"] = status_display(fact["status"])
        fact["capacity_mw"] = _safe_float(row.get("capacity_mw"), fact.get("capacity_mw"))
        fact["installed_mw"] = fact["capacity_mw"]


def apply_monitoring_data(facts_by_key: dict[str, dict]) -> None:
    by_slug = {fact.get("wiki_slug"): fact for fact in facts_by_key.values() if fact.get("wiki_slug")}
    events: dict[str, list[dict]] = {}
    for row in load_csv_rows(PROJECT_EVENTS):
        slug = row["project_slug"].strip()
        events.setdefault(slug, []).append({
            "id": row["event_id"], "date": row["event_date"], "type": row["event_type"],
            "title": row["title"], "status_after": row["status_after"],
            "description": row["description"], "source_url": row["source_url"],
            "source_title": row["source_title"], "confidence": row["confidence"],
            "verified_on": row["verified_on"],
        })
    blockers: dict[str, list[dict]] = {}
    for row in load_csv_rows(PROJECT_BLOCKERS):
        slug = row["project_slug"].strip()
        blockers.setdefault(slug, []).append({
            "id": row["blocker_id"], "category": row["category"], "status": row["status"],
            "owner": row["owner"], "blocked_milestone": row["blocked_milestone"],
            "description": row["description"], "source_url": row["source_url"],
            "source_title": row["source_title"], "confidence": row["confidence"],
            "last_verified_date": row["last_verified_date"],
        })
    for slug in sorted(set(events) | set(blockers)):
        fact = by_slug.get(slug)
        if fact is None:
            continue
        fact_events = sorted(events.get(slug, []), key=lambda item: item["date"], reverse=True)
        fact_blockers = sorted(blockers.get(slug, []), key=lambda item: (item["status"] != "active", item["category"]))
        fact["latest_events"] = fact_events
        fact["blockers"] = fact_blockers
        dates = [item["verified_on"] for item in fact_events] + [item["last_verified_date"] for item in fact_blockers]
        fact["as_of"] = max(dates) if dates else fact.get("last_updated", "")
        fact["status_dimensions"] = {
            "delivery": fact.get("status", "unknown"),
            "finance": "blocked" if any(item["category"] == "finance" and item["status"] == "active" for item in fact_blockers) else "not-recorded",
            "safeguards": "active-review" if any(item["category"] == "safeguards" and item["status"] == "active" for item in fact_blockers) else "not-recorded",
        }
        fact["evidence_urls"] = sorted({item["source_url"] for item in fact_events + fact_blockers if item.get("source_url")})


def add_corridor_facts(facts_by_key: dict[str, dict], titles: dict[str, str]) -> None:
    grouped: dict[str, list[dict[str, str]]] = {}
    for row in load_csv_rows(CORRIDOR_SPECS):
        grouped.setdefault(row["slug"].strip(), []).append(row)
    for slug, rows in grouped.items():
        if slug not in titles:
            continue
        statuses = {row["status"] for row in rows}
        overall_status = next(iter(statuses)) if len(statuses) == 1 else "partially-operational"
        segments = [{
            "id": row["segment_id"], "name": row["segment_name"], "country": row["country"],
            "voltage_kv": _safe_float(row["voltage_kv"]), "status": row["status"],
            "status_as_of": row["status_as_of"], "owner": row["owner"],
            "dependency": row["dependency"], "source_url": row["source_url"],
            "confidence": row["confidence"],
        } for row in rows]
        facts_by_key[f"corridor:{slug}"] = {
            "id": f"transmission:{slug}", "domain": "transmission", "facets": ["transmission"],
            "name": titles[slug], "wiki_slug": slug, "status": status_norm(overall_status),
            "status_raw": overall_status, "status_display": status_display(overall_status),
            "voltage_kv": max(_safe_float(row["voltage_kv"], 0) for row in rows),
            "segments": segments, "as_of": max(row["status_as_of"] for row in rows),
            "source_layer": "corridor_specs", "sources": ["corridor_specs"],
            "evidence_urls": sorted({row["source_url"] for row in rows}),
            "feature_ref": {"layer": "corridor_specs", "id": slug, "match_field": "slug", "match_value": slug},
            "confidence": "high" if all(row["confidence"] == "high" for row in rows) else "medium",
        }


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
    raw_status = (
        props.get("delivery_status")
        or props.get("status")
        or props.get("doed_delivery_status")
        or props.get("doed_primary_category")
        or props.get("license_type")
        or props.get("category")
        or ""
    )
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
            "under-construction": "hydropower_verified_construction",
            "licensed": "hydropower_construction",
            "cancelled": "hydropower_cancelled",
            "survey": "hydropower_survey",
        }.get(status, "hydropower_survey")
    fact_id = f"{domain}:{slugify(name)}"
    wiki_slug = lookup.get(key) or lookup.get(norm_name(name.replace("HPP", "").replace("HEP", ""))) or ""
    if layer == "solar_plants":
        feature_id = str(props.get("id") or props.get("feature_id") or "").strip()
        if feature_id:
            key = f"solar:{feature_id}"
            fact_id = f"solar:{feature_id}"
        wiki_slug = props.get("_wiki_slug_override") or wiki_slug
    return {
        "id": fact_id,
        "key": key,
        "domain": fact_domain,
        "facets": sorted({fact_domain, domain}),
        "name": name,
        "wiki_slug": wiki_slug,
        "capacity_mw": capacity,
        "installed_mw": _safe_float(props.get("installed_mw"), capacity),
        "capacity_mwp": _safe_float(props.get("capacity_mwp"), capacity),
        "status": status,
        "status_raw": str(raw_status) if raw_status else "",
        "status_display": (
            status_display(props.get("delivery_status") or props.get("status"))
            if (props.get("delivery_status") or props.get("status"))
            else ("Operating" if props.get("doed_delivery_status") == "operating" else props.get("doed_status_display") or status_display(status))
        ),
        "status_priority": status_priority(props),
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
        "tariff_npr_kwh": _safe_float(props.get("tariff_npr_kwh")),
        "is_operating": props.get("is_operating"),
        "procurement_stage": props.get("procurement_stage") or "",
        "developer_type": props.get("developer_type") or "",
        "substation": props.get("substation") or "",
        "bidder": props.get("bidder") or "",
        "resource_zone": props.get("resource_zone") or "",
        "siting_archetype": props.get("siting_archetype") or "",
        "precision_label": props.get("precision_label") or "",
        "location_basis": props.get("location_basis") or "",
        "project_group_slug": props.get("project_group_slug") or "",
        "registry_slug": props.get("_csv_slug") or props.get("slug") or "",
        "label_title": props.get("label_title") or "",
    }


def merge_fact(old: dict, new: dict) -> dict:
    merged = dict(old)
    source_score = {
        "top_capacity_project_annotations": 5,
        "priority_project_watchlist": 4,
        "storage_shortlist_annotations": 3,
        "solar_plants": 3,
        "hydropower_project_display_points": 2,
    }
    merged["sources"] = sorted(set(old.get("sources", [])) | set(new.get("sources", [])))
    if source_score.get(new["source_layer"], 0) > source_score.get(old["source_layer"], 0) or better_capacity(new, old):
        for field in [
            "capacity_mw", "capacity_mwp", "installed_mw", "rank", "source_layer",
            "source_note", "confidence", "tariff_npr_kwh", "procurement_stage",
            "developer_type", "substation", "bidder", "resource_zone",
            "siting_archetype", "precision_label", "location_basis",
            "project_group_slug", "registry_slug", "label_title",
        ]:
            if new.get(field) not in (None, ""):
                merged[field] = new[field]
        if new.get("feature_ref"):
            merged["feature_ref"] = new["feature_ref"]
    for field in ["wiki_slug", "river", "basin", "district", "province", "promoter", "status_raw"]:
        if not merged.get(field) and new.get(field):
            merged[field] = new[field]
    old_status_priority = int(merged.get("status_priority") or 0)
    new_status_priority = int(new.get("status_priority") or 0)
    old_source_score = source_score.get(merged.get("source_layer", ""), 0)
    new_source_score = source_score.get(new.get("source_layer", ""), 0)
    if (
        new.get("status") != "unknown"
        and (
            merged.get("status") in {"unknown", ""}
            or new_status_priority > old_status_priority
            or (new_status_priority == old_status_priority and new_source_score > old_source_score)
        )
    ):
        merged["status"] = new["status"]
        merged["status_raw"] = new.get("status_raw", merged.get("status_raw", ""))
        merged["status_display"] = new.get("status_display", merged.get("status_display", ""))
        merged["status_priority"] = new_status_priority
    merged["facets"] = sorted(set(merged.get("facets", [])) | set(new.get("facets", [])))
    return merged


def main() -> None:
    lookup = title_slug_lookup()
    slugs = existing_slugs()
    titles = page_titles_by_slug()
    solar_specs = load_solar_specs_lookup()  # feature_id -> CSV row
    facts_by_key: dict[str, dict] = {}
    for domain, layer, path in SOURCES:
        for props in load_features(path):
            if layer == "solar_plants":
                feature_id = props.get("id") or ""
                csv_row = solar_specs.get(feature_id)
                if csv_row:
                    csv_slug = (csv_row.get("slug") or "").strip()
                    group_slug = (csv_row.get("project_group_slug") or "").strip()
                    props["_csv_slug"] = csv_slug
                    if csv_slug in slugs:
                        props["_wiki_slug_override"] = csv_slug
                    elif group_slug in slugs:
                        props["_wiki_slug_override"] = group_slug
                    for field, val in csv_row.items():
                        if val and field not in ("slug", "feature_id"):
                            props[field] = val
            fact = fact_from_props(domain, layer, props, lookup)
            if not fact:
                continue
            key = fact.pop("key")
            facts_by_key[key] = merge_fact(facts_by_key[key], fact) if key in facts_by_key else fact
    apply_project_specs(facts_by_key, titles)
    add_corridor_facts(facts_by_key, titles)
    apply_monitoring_data(facts_by_key)
    facts = sorted(
        facts_by_key.values(),
        key=lambda f: (f.get("domain", ""), -(f.get("capacity_mw") or 0), f.get("name", "")),
    )
    for fact in facts:
        fact.pop("status_priority", None)
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
