#!/usr/bin/env python3
"""Build the internal Nepal Energy evidence-and-coverage dashboard dataset.

The dashboard is a development-only control room. It summarizes governed wiki
metadata, project monitoring records, specification completeness, registry
crosswalks, and research queues without changing any public source data.

Usage:
    python scripts/build_internal_dashboard.py
    python scripts/build_internal_dashboard.py --check
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable


ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "processed" / "dashboard" / "control-room.json"

PAGE_META = ROOT / "wiki" / "explorer" / "shared" / "wiki-page-meta.json"
BACKLINKS = ROOT / "wiki" / "explorer" / "shared" / "wiki-backlinks.json"
FACT_INDEX = ROOT / "wiki" / "explorer" / "shared" / "wiki-fact-index.json"
SPECS = ROOT / "data" / "project_specs.csv"
EVENTS = ROOT / "data" / "project_events.csv"
BLOCKERS = ROOT / "data" / "project_blockers.csv"
CORRIDORS = ROOT / "data" / "corridor_specs.csv"
DOED_SUMMARY = ROOT / "data" / "processed" / "tables" / "doed_project_status_overlay_summary.json"
DOED_REVIEW = ROOT / "data" / "processed" / "tables" / "doed_project_crosswalk_review.csv"
DOED_REVIEW_DISPOSITIONS = ROOT / "data" / "doed_crosswalk_dispositions.csv"
DOED_MISSING_OPERATING = ROOT / "data" / "processed" / "tables" / "doed_operating_projects_missing_local.csv"
HYDROMAP_SUMMARY = ROOT / "data" / "processed" / "tables" / "hydromap_coverage_summary.json"
HYDROMAP_REVIEW = ROOT / "data" / "processed" / "tables" / "hydromap_active_review_queue.csv"
CAPACITY_CONFLICTS = ROOT / "data" / "processed" / "tables" / "hydromap_capacity_conflicts.csv"
CAPACITY_DECISIONS = ROOT / "data" / "capacity_authority_decisions.csv"
FLAGS = ROOT / "wiki" / "FLAGGED_FOR_REVIEW.md"
SOURCE_DIR = ROOT / "wiki" / "pages" / "sources"

REQUIRED_INPUTS = (
    PAGE_META,
    BACKLINKS,
    FACT_INDEX,
    SPECS,
    EVENTS,
    BLOCKERS,
    CORRIDORS,
    DOED_SUMMARY,
    DOED_REVIEW,
    DOED_REVIEW_DISPOSITIONS,
    DOED_MISSING_OPERATING,
    HYDROMAP_SUMMARY,
    HYDROMAP_REVIEW,
    CAPACITY_CONFLICTS,
    CAPACITY_DECISIONS,
    FLAGS,
)

SPEC_SECTIONS: dict[str, list[str]] = {
    "engineering": [
        "gross_head_m", "design_discharge_m3s", "headrace_tunnel_km",
        "dam_height_m", "dam_type", "num_units", "unit_capacity_mw",
        "turbine_type", "underground_powerhouse", "penstock_length_m",
        "penstock_diameter_m", "tailrace_length_m",
    ],
    "storage": ["total_storage_mcm", "effective_storage_mcm", "pumped_storage_mw"],
    "output": [
        "annual_design_energy_gwh", "dry_season_energy_gwh", "dry_share_pct",
        "plant_load_factor_pct", "q_design", "project_type",
        "catchment_area_km2", "environmental_release_m3s",
    ],
    "financial": [
        "total_cost_usd_m", "cost_per_mw_usd_m", "ppa_rate_wet_npr_kwh",
        "ppa_rate_dry_npr_kwh", "debt_equity_ratio",
    ],
    "governance": ["developer", "concession_type", "lead_financier", "concession_years"],
    "schedule": ["construction_start_year", "cod_year", "completion_pct"],
}

DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
FLAG_RE = re.compile(r"^- \*\*\[(?P<date>\d{4}-\d{2}-\d{2})\]\*\*\s*(?P<title>.+)$", re.M)


def fail(message: str) -> None:
    raise SystemExit(f"ERROR: {message}")


def read_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001
        fail(f"cannot read {path.relative_to(ROOT)}: {exc}")


def read_csv(path: Path) -> list[dict[str, str]]:
    try:
        with path.open(newline="", encoding="utf-8") as handle:
            return list(csv.DictReader(handle))
    except Exception as exc:  # noqa: BLE001
        fail(f"cannot read {path.relative_to(ROOT)}: {exc}")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def clean_scalar(value: Any) -> Any:
    if value is None:
        return None
    if isinstance(value, str):
        value = value.strip()
        return value if value else None
    return value


def number(value: Any) -> float | None:
    value = clean_scalar(value)
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def split_frontmatter(text: str) -> str:
    if not text.startswith("---"):
        return ""
    end = text.find("\n---", 4)
    return "" if end == -1 else text[4:end]


def frontmatter_scalar(frontmatter: str, key: str) -> str | None:
    # Horizontal whitespace only: ``\s`` would cross a newline and could turn a
    # blank ``source_url:`` into the following YAML key/value pair.
    match = re.search(rf"^{re.escape(key)}:[ \t]*([^\r\n]*)$", frontmatter, re.M)
    if not match:
        return None
    value = match.group(1).strip().strip('"').strip("'")
    if not value or value.lower() in {"null", "none", "[]"}:
        return None
    return value


def local_source_href(value: str | None) -> str | None:
    """Resolve repository-relative source paths from the dashboard root."""
    if not value or value.startswith(("https://", "http://", "/")):
        return value
    normalized = value.replace("\\", "/")
    for marker in ("data/", "wiki/"):
        position = normalized.find(marker)
        if position >= 0:
            return "/" + normalized[position:]
    return normalized


def tier_for(pct: float) -> str:
    if pct >= 50:
        return "rich"
    if pct >= 25:
        return "moderate"
    if pct > 0:
        return "thin"
    return "empty"


def spec_completeness(row: dict[str, str]) -> dict[str, Any]:
    sections: dict[str, dict[str, Any]] = {}
    total_filled = 0
    total_possible = 0
    for section, fields in SPEC_SECTIONS.items():
        filled = sum(1 for field in fields if clean_scalar(row.get(field)) is not None)
        total = len(fields)
        pct = round(filled / total * 100, 1) if total else 0
        sections[section] = {"filled": filled, "total": total, "pct": pct}
        total_filled += filled
        total_possible += total
    pct = round(total_filled / total_possible * 100, 1) if total_possible else 0
    return {
        "filled": total_filled,
        "total": total_possible,
        "pct": pct,
        "tier": tier_for(pct),
        "sections": sections,
    }


def collect_dates(values: Iterable[Any]) -> list[str]:
    dates: list[str] = []
    for value in values:
        value = clean_scalar(value)
        if isinstance(value, str) and DATE_RE.match(value):
            dates.append(value)
    return dates


def page_and_source_records(page_meta: dict[str, Any], backlinks: dict[str, Any]) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    pages = page_meta.get("pages", [])
    if not isinstance(pages, list):
        fail("wiki-page-meta.json pages must be a list")

    type_counts = Counter(str(page.get("type") or page.get("category") or "unknown") for page in pages)
    quality_counts = Counter(str(page.get("page_quality") or "unclassified") for page in pages)
    generator_counts = Counter(str(page.get("generator") or "none") for page in pages)
    backlink_map = backlinks.get("backlinks", {})

    sources: list[dict[str, Any]] = []
    for path in sorted(SOURCE_DIR.glob("*.md")):
        fm = split_frontmatter(path.read_text(encoding="utf-8"))
        slug = path.stem
        url = frontmatter_scalar(fm, "source_url")
        source_date = frontmatter_scalar(fm, "source_date")
        last_checked = frontmatter_scalar(fm, "last_checked")
        updated = frontmatter_scalar(fm, "updated")
        title = frontmatter_scalar(fm, "title") or slug.replace("-", " ").title()
        used_by = backlink_map.get(slug, [])
        sources.append({
            "slug": slug,
            "title": title,
            "source_url": url,
            "source_href": local_source_href(url),
            "source_date": source_date,
            "last_checked": last_checked,
            "updated": updated,
            "used_by_count": len(used_by) if isinstance(used_by, list) else 0,
            "has_url": bool(url),
            "has_source_date": bool(source_date),
            "has_last_checked": bool(last_checked),
            "wiki_url": f"/wiki/explorer/?page={slug}",
        })

    summary = {
        "total_pages": len(pages),
        "type_counts": dict(sorted(type_counts.items())),
        "quality_counts": dict(sorted(quality_counts.items())),
        "generator_counts": dict(sorted(generator_counts.items())),
        "source_pages": len(sources),
        "sources_with_url": sum(1 for item in sources if item["has_url"]),
        "sources_with_date": sum(1 for item in sources if item["has_source_date"]),
        "sources_missing_url": sum(1 for item in sources if not item["has_url"]),
        "sources_missing_date": sum(1 for item in sources if not item["has_source_date"]),
        "sources_with_last_checked": sum(1 for item in sources if item["has_last_checked"]),
        "sources_without_backlinks": sum(1 for item in sources if item["used_by_count"] == 0),
    }
    return summary, sources


def parse_open_flags(path: Path) -> list[dict[str, Any]]:
    text = path.read_text(encoding="utf-8")
    start = text.find("## Open Items")
    end = text.find("## Resolved Items")
    section = text[start:end] if start >= 0 and end > start else ""
    matches = list(FLAG_RE.finditer(section))
    flags: list[dict[str, Any]] = []
    for index, match in enumerate(matches):
        body_end = matches[index + 1].start() if index + 1 < len(matches) else len(section)
        detail = section[match.end():body_end].strip()
        title = match.group("title").strip()
        lowered = f"{title} {detail}".lower()
        severity = "high" if any(word in lowered for word in ("contradiction", "curtailment", "financial close", "primary-source gaps")) else "medium"
        flags.append({
            "id": f"flag-{index + 1}",
            "date": match.group("date"),
            "title": title,
            "detail": re.sub(r"\s+", " ", detail),
            "severity": severity,
            "source_path": "wiki/FLAGGED_FOR_REVIEW.md",
        })
    return flags


def normalized_queue(rows: list[dict[str, str]], queue_type: str) -> list[dict[str, Any]]:
    normalized: list[dict[str, Any]] = []
    for index, raw in enumerate(rows):
        row = {key: clean_scalar(value) for key, value in raw.items()}
        identity = json.dumps(row, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        row["queue_id"] = f"{queue_type}-{hashlib.sha256(identity.encode('utf-8')).hexdigest()[:12]}"
        row["queue_type"] = queue_type
        normalized.append(row)
    return normalized


def monitoring_projects(
    specs: list[dict[str, str]],
    events: list[dict[str, str]],
    blockers: list[dict[str, str]],
    corridors: list[dict[str, str]],
    facts: dict[str, Any],
    page_meta: dict[str, Any],
) -> list[dict[str, Any]]:
    events_by_slug: dict[str, list[dict[str, Any]]] = defaultdict(list)
    blockers_by_slug: dict[str, list[dict[str, Any]]] = defaultdict(list)
    corridors_by_slug: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in events:
        events_by_slug[row["project_slug"]].append({key: clean_scalar(value) for key, value in row.items()})
    for row in blockers:
        blockers_by_slug[row["project_slug"]].append({key: clean_scalar(value) for key, value in row.items()})
    for row in corridors:
        corridors_by_slug[row["slug"]].append({key: clean_scalar(value) for key, value in row.items()})
    for rows in events_by_slug.values():
        rows.sort(key=lambda row: row.get("event_date") or "", reverse=True)
    for rows in blockers_by_slug.values():
        rows.sort(key=lambda row: (row.get("status") != "active", row.get("category") or ""))

    spec_by_slug = {row["slug"]: row for row in specs}
    meta_by_slug = {row["slug"]: row for row in page_meta.get("pages", [])}
    fact_rows = facts.get("facts", [])
    fact_by_slug: dict[str, dict[str, Any]] = {}
    for fact in fact_rows:
        slug = fact.get("slug") or fact.get("wiki_slug")
        if not slug:
            continue
        current = fact_by_slug.get(slug)
        if current is None or len(fact.get("latest_events") or []) > len(current.get("latest_events") or []):
            fact_by_slug[slug] = fact

    slugs = sorted(set(events_by_slug) | set(blockers_by_slug) | set(corridors_by_slug))
    projects: list[dict[str, Any]] = []
    for slug in slugs:
        spec = spec_by_slug.get(slug, {})
        fact = fact_by_slug.get(slug, {})
        meta = meta_by_slug.get(slug, {})
        project_events = events_by_slug.get(slug, [])
        project_blockers = blockers_by_slug.get(slug, [])
        project_corridors = corridors_by_slug.get(slug, [])
        verified_dates = collect_dates(
            [row.get("verified_on") for row in project_events]
            + [row.get("last_verified_date") for row in project_blockers]
            + [row.get("status_as_of") for row in project_corridors]
            + [spec.get("last_updated"), fact.get("as_of"), fact.get("last_updated")]
        )
        completeness = spec_completeness(spec) if spec else None
        title = meta.get("title") or fact.get("label_title") or fact.get("name") or slug.replace("-", " ").title()
        status = clean_scalar(spec.get("status")) or clean_scalar(fact.get("status")) or "unknown"
        projects.append({
            "slug": slug,
            "title": title,
            "status": status,
            "capacity_mw": number(spec.get("capacity_mw")) or number(fact.get("capacity_mw")),
            "river": clean_scalar(spec.get("river")) or clean_scalar(fact.get("river")),
            "last_verified": max(verified_dates) if verified_dates else None,
            "latest_event": project_events[0] if project_events else None,
            "events": project_events,
            "blockers": project_blockers,
            "active_blocker_count": sum(1 for row in project_blockers if row.get("status") == "active"),
            "corridor_segments": project_corridors,
            "spec_completeness": completeness,
            "status_dimensions": fact.get("status_dimensions") or {"delivery": status},
            "evidence_urls": sorted(set(fact.get("evidence_urls") or [])),
            "wiki_url": f"/wiki/explorer/?page={slug}",
        })
    return projects


def coverage_projects(
    specs: list[dict[str, str]],
    monitors: list[dict[str, Any]],
    facts: dict[str, Any],
    page_meta: dict[str, Any],
) -> list[dict[str, Any]]:
    monitored = {row["slug"]: row for row in monitors}
    meta_by_slug = {row["slug"]: row for row in page_meta.get("pages", [])}
    fact_slugs = {row.get("slug") or row.get("wiki_slug") for row in facts.get("facts", [])}
    rows: list[dict[str, Any]] = []
    for spec in specs:
        slug = spec["slug"]
        completeness = spec_completeness(spec)
        monitor = monitored.get(slug)
        meta = meta_by_slug.get(slug, {})
        rows.append({
            "slug": slug,
            "title": meta.get("title") or slug.replace("-", " ").title(),
            "capacity_mw": number(spec.get("capacity_mw")),
            "status": clean_scalar(spec.get("status")) or "unknown",
            "last_updated": clean_scalar(spec.get("last_updated")),
            "identity_state": "linked" if slug in fact_slugs else "missing-fact-link",
            "monitoring_state": "monitored" if monitor else "registry-only",
            "active_blocker_count": monitor["active_blocker_count"] if monitor else 0,
            "event_count": len(monitor["events"]) if monitor else 0,
            "completeness": completeness,
            "wiki_url": f"/wiki/explorer/?page={slug}",
        })
    return sorted(rows, key=lambda row: (row["completeness"]["pct"], row["slug"]))


def build_payload() -> dict[str, Any]:
    missing = [path.relative_to(ROOT).as_posix() for path in REQUIRED_INPUTS if not path.exists()]
    if missing:
        fail("missing required input(s): " + ", ".join(missing))

    page_meta = read_json(PAGE_META)
    backlinks = read_json(BACKLINKS)
    facts = read_json(FACT_INDEX)
    specs = read_csv(SPECS)
    events = read_csv(EVENTS)
    blockers = read_csv(BLOCKERS)
    corridors = read_csv(CORRIDORS)
    doed_summary = read_json(DOED_SUMMARY)
    hydromap_summary = read_json(HYDROMAP_SUMMARY)
    missing_operating_rows = read_csv(DOED_MISSING_OPERATING)
    handled_operating_record_numbers = {
        str(row.get("record_number") or "").strip() for row in missing_operating_rows
    }
    raw_doed_review = read_csv(DOED_REVIEW)
    reviewed_rejections = [
        row for row in raw_doed_review
        if str(row.get("review_decision") or "").strip().startswith("rejected_")
    ]
    doed_review = normalized_queue(
        [
            row for row in raw_doed_review
            if not str(row.get("review_decision") or "").strip().startswith("rejected_")
            and not (
                str(row.get("official_regulatory_category") or "").strip() == "operating_record"
                and str(row.get("official_record_number") or "").strip() in handled_operating_record_numbers
            )
        ],
        "doed-crosswalk",
    )
    doed_missing_operating = normalized_queue(missing_operating_rows, "doed-missing-operating")
    hydromap_review = normalized_queue(read_csv(HYDROMAP_REVIEW), "hydromap-active")
    all_capacity_conflicts = read_csv(CAPACITY_CONFLICTS)
    capacity_decisions = read_csv(CAPACITY_DECISIONS)
    resolved_capacity_decisions = {"publish_dual_value", "retain_legacy_below_materiality"}
    resolved_capacity_names = {
        str(row.get("local_project") or "").strip()
        for row in capacity_decisions
        if str(row.get("decision") or "").strip() in resolved_capacity_decisions
    }
    unresolved_capacity_conflicts = [
        row for row in all_capacity_conflicts
        if str(row.get("local_name") or "").strip() not in resolved_capacity_names
    ]
    capacity_conflicts = normalized_queue(unresolved_capacity_conflicts, "capacity-conflict")
    flags = parse_open_flags(FLAGS)

    corpus_summary, sources = page_and_source_records(page_meta, backlinks)
    corpus_summary["structured_facts"] = len(facts.get("facts", []))
    monitors = monitoring_projects(specs, events, blockers, corridors, facts, page_meta)
    coverage = coverage_projects(specs, monitors, facts, page_meta)

    all_dates = collect_dates(
        [page.get("updated") for page in page_meta.get("pages", [])]
        + [row.get("last_updated") for row in specs]
        + [row.get("verified_on") for row in events]
        + [row.get("last_verified_date") for row in blockers]
        + [row.get("status_as_of") for row in corridors]
        + [row.get("source_date") for row in sources]
        + [flag.get("date") for flag in flags]
    )
    data_as_of = max(all_dates) if all_dates else None

    tier_counts = Counter(row["completeness"]["tier"] for row in coverage)
    blocker_status_counts = Counter(row.get("status") or "unknown" for row in blockers)
    attention = [
        {
            "id": "doed-unmatched",
            "severity": "high",
            "title": "Local hydro identities unmatched to DoED",
            "count": doed_summary.get("unmatched_local_rows", 0),
            "view": "reconciliation",
        },
        {
            "id": "doed-review",
            "severity": "high",
            "title": "Official crosswalk records awaiting review",
            "count": len(doed_review),
            "view": "reconciliation",
        },
        {
            "id": "capacity-conflicts",
            "severity": "medium",
            "title": "Material capacity comparisons to adjudicate",
            "count": len(capacity_conflicts),
            "view": "reconciliation",
        },
        {
            "id": "doed-missing-operating",
            "severity": "high",
            "title": "Official operating records absent from local registry",
            "count": len(doed_missing_operating),
            "view": "reconciliation",
        },
        {
            "id": "open-flags",
            "severity": "high",
            "title": "Open evidence and ontology review groups",
            "count": len(flags),
            "view": "reconciliation",
        },
        {
            "id": "source-dates",
            "severity": "medium",
            "title": "Source pages without publication dates",
            "count": corpus_summary["sources_missing_date"],
            "view": "sources",
        },
        {
            "id": "thin-specs",
            "severity": "medium",
            "title": "Curated specifications below moderate depth",
            "count": tier_counts.get("thin", 0) + tier_counts.get("empty", 0),
            "view": "coverage",
        },
    ]

    return {
        "schema_version": 1,
        "title": "Nepal Energy Evidence & Coverage Control Room",
        "data_as_of": data_as_of,
        "scope": "Internal research operations; not a public project-status publication.",
        "inputs": [
            {
                "path": path.relative_to(ROOT).as_posix(),
                "sha256": sha256(path),
            }
            for path in REQUIRED_INPUTS
        ],
        "overview": {
            "corpus": corpus_summary,
            "registry": {
                "local_hydro_rows": doed_summary.get("local_rows"),
                "official_hydro_rows": doed_summary.get("official_hydro_rows"),
                "matched_local_rows": doed_summary.get("matched_local_rows"),
                "unmatched_local_rows": doed_summary.get("unmatched_local_rows"),
                "operating_local_rows": doed_summary.get("operating_local_rows"),
                "mixed_record_status_rows": doed_summary.get("mixed_record_status_rows"),
                "review_rows": doed_summary.get("review_rows"),
                "identity_review_rows": len(doed_review),
                "reviewed_rejected_suggestions": len(reviewed_rejections),
                "missing_operating_local_rows": len(doed_missing_operating),
                "match_pct": round((doed_summary.get("matched_local_rows", 0) / max(doed_summary.get("local_rows", 1), 1)) * 100, 1),
            },
            "specifications": {
                "projects": len(specs),
                "tier_counts": dict(sorted(tier_counts.items())),
                "average_completeness_pct": round(sum(row["completeness"]["pct"] for row in coverage) / max(len(coverage), 1), 1),
            },
            "monitoring": {
                "projects": len(monitors),
                "events": len(events),
                "blockers": len(blockers),
                "blocker_status_counts": dict(sorted(blocker_status_counts.items())),
                "corridor_segments": len(corridors),
            },
            "benchmark": {
                "external_hydro_rows": hydromap_summary.get("external", {}).get("hydro", {}).get("rows"),
                "local_solar_rows": hydromap_summary.get("local", {}).get("solar", {}).get("rows"),
                "external_solar_rows": hydromap_summary.get("external", {}).get("solar", {}).get("rows"),
                "active_review_rows": len(hydromap_review),
                "capacity_conflict_rows": len(capacity_conflicts),
                "capacity_conflict_rows_total": len(all_capacity_conflicts),
                "capacity_conflict_rows_resolved": len(all_capacity_conflicts) - len(capacity_conflicts),
            },
            "attention": attention,
        },
        "coverage": {"projects": coverage},
        "monitoring": {"projects": monitors},
        "reconciliation": {
            "doed_review": doed_review,
            "doed_missing_operating": doed_missing_operating,
            "hydromap_active_review": hydromap_review,
            "capacity_conflicts": capacity_conflicts,
            "open_flags": flags,
        },
        "sources": {"records": sources},
        "contracts": {
            "items": [
                {
                    "id": "canonical-project-identities",
                    "label": "Canonical project identities",
                    "status": "partial",
                    "detail": "Curated projects have stable wiki slugs; unresolved registry records remain name-keyed and are not assigned synthetic identities.",
                },
                {
                    "id": "status-dimensions",
                    "label": "Regulatory and delivery status separation",
                    "status": "partial",
                    "detail": "The DoED overlay preserves regulatory history and monitored projects expose delivery status, but the separation is not yet universal across all public layers.",
                },
                {
                    "id": "field-provenance",
                    "label": "Per-field evidence and applicability",
                    "status": "missing",
                    "detail": "Project specifications currently provide row-level source notes, not per-field evidence or unknown-versus-not-applicable states.",
                },
                {
                    "id": "source-freshness",
                    "label": "Source retrieval and freshness registry",
                    "status": "missing",
                    "detail": "Publication and page-update dates exist, but source pages do not yet record a consistent last_checked value.",
                },
                {
                    "id": "milestones-packages",
                    "label": "Milestone and package tracking",
                    "status": "partial",
                    "detail": "Dated project events exist for the priority set; reusable milestone-stage and construction-package records are not yet normalized.",
                },
                {
                    "id": "queue-lifecycle",
                    "label": "Research queue ownership and decisions",
                    "status": "missing",
                    "detail": "Current queues preserve evidence and review state but do not consistently record assignee, due date, disposition, or decision history.",
                },
                {
                    "id": "frontmatter-health",
                    "label": "Strict frontmatter contract",
                    "status": "warning",
                    "detail": "The dashboard consumes generated regex-tolerant page metadata because the existing corpus is not uniformly strict-YAML parseable.",
                },
            ]
        },
    }


def render(payload: dict[str, Any]) -> str:
    return json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="fail if the generated output is missing or stale")
    parser.add_argument("--output", type=Path, default=OUT, help="override output path")
    args = parser.parse_args(argv)

    output = args.output if args.output.is_absolute() else ROOT / args.output
    generated = render(build_payload())
    if args.check:
        if not output.exists():
            print(f"STALE: {output.relative_to(ROOT)} is missing", file=sys.stderr)
            return 1
        if output.read_text(encoding="utf-8") != generated:
            print(f"STALE: {output.relative_to(ROOT)} does not match current inputs", file=sys.stderr)
            return 1
        print(f"OK: {output.relative_to(ROOT)} matches current dashboard inputs")
        return 0

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(generated, encoding="utf-8")
    payload = json.loads(generated)
    print(
        f"Wrote {output.relative_to(ROOT)}: "
        f"{payload['overview']['corpus']['total_pages']} pages, "
        f"{len(payload['monitoring']['projects'])} monitored projects, "
        f"{sum(len(value) for value in payload['reconciliation'].values())} queue records"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
