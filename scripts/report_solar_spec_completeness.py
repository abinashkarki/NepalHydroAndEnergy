#!/usr/bin/env python3
"""Data completeness report for solar_project_specs.csv.

Usage:
    python3 scripts/report_solar_spec_completeness.py          # terminal summary
    python3 scripts/report_solar_spec_completeness.py --csv    # also write CSV
    python3 scripts/report_solar_spec_completeness.py --md     # also write markdown
    python3 scripts/report_solar_spec_completeness.py --all    # write both
"""

import csv
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

SECTIONS: dict[str, list[str]] = {
    "Output & Economics": [
        "tariff_npr_kwh",
        "expected_annual_generation_gwh",
    ],
    "Geography & Siting": [
        "district",
        "province",
        "substation",
        "resource_zone",
        "siting_archetype",
    ],
    "Ownership": [
        "owner",
        "bidder",
        "developer_type",
    ],
    "Data Quality": [
        "precision_label",
        "location_basis",
        "confidence",
    ],
}

SECTION_KEYS = {
    "Output & Economics": "output_economics",
    "Geography & Siting": "geography_siting",
    "Ownership": "ownership",
    "Data Quality": "data_quality",
}

REGISTRY_FIELDS = {
    "slug",
    "feature_id",
    "label_title",
    "project_group_slug",
    "status",
    "procurement_stage",
    "is_operating",
    "capacity_mwp",
    "capacity_mw",
    "source_note",
    "source_slug",
    "last_updated",
}

CSV_PATH = Path("data/solar_project_specs.csv")
CSV_OUT = Path("data/processed/tables/solar_spec_completeness_report.csv")
MD_OUT = Path("data/processed/tables/solar_spec_completeness_report.md")

# ---------------------------------------------------------------------------
# Core logic
# ---------------------------------------------------------------------------


def load_projects(csv_path: Path) -> list[dict]:
    with open(csv_path, newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def is_populated(value: str | None) -> bool:
    if value is None:
        return False
    return value.strip() != ""


def tier_label(pct: float) -> str:
    if pct >= 50:
        return "rich"
    if pct >= 25:
        return "moderate"
    if pct > 0:
        return "thin"
    return "empty"


def completeness(project: dict) -> dict:
    result: dict = {"slug": project["slug"]}
    filled_total = 0
    possible_total = 0

    for section_name, fields in SECTIONS.items():
        section_key = SECTION_KEYS[section_name]
        filled = sum(1 for f in fields if is_populated(project.get(f)))
        total = len(fields)
        result[f"{section_key}_filled"] = filled
        result[f"{section_key}_total"] = total
        filled_total += filled
        possible_total += total

    result["total_filled"] = filled_total
    result["total_possible"] = possible_total
    result["completeness_pct"] = (
        round(filled_total / possible_total * 100, 1) if possible_total else 0.0
    )
    result["tier"] = tier_label(result["completeness_pct"])
    result["capacity_mwp"] = project.get("capacity_mwp", "")
    result["status"] = project.get("status", "")
    result["is_operating"] = project.get("is_operating", "")
    return result


# ---------------------------------------------------------------------------
# Reporting helpers
# ---------------------------------------------------------------------------


def _section_label(name: str) -> str:
    return {
        "Output & Economics": "Econ",
        "Geography & Siting": "Geo",
        "Ownership": "Owner",
        "Data Quality": "DQ",
    }.get(name, name)


def _bar(filled: int, total: int, width: int = 10) -> str:
    if total == 0:
        return "·" * width
    ratio = filled / total
    blocks = round(ratio * width)
    return "█" * blocks + "░" * (width - blocks)


def _tier_icon(tier: str) -> str:
    return {"rich": "★", "moderate": "⬖", "thin": "·", "empty": " "}.get(tier, tier)


def print_summary(projects: list[dict]) -> None:
    results = [completeness(p) for p in projects]

    sect_names = list(SECTIONS.keys())

    print()

    # Per-project rows
    for r in results:
        slug = r["slug"]
        parts = [f"{slug:<35}", f"{r['capacity_mwp']:>6}", f"{r['status']:<12}"]
        for s in sect_names:
            section_key = SECTION_KEYS[s]
            fill = r[f"{section_key}_filled"]
            tot = r[f"{section_key}_total"]
            parts.append(_bar(fill, tot, 10))
        parts.append(f"{r['completeness_pct']:>5.0f}%")
        parts.append(_tier_icon(r["tier"]))
        print("  ".join(parts))

    # Summary counts by tier
    counts = {"rich": 0, "moderate": 0, "thin": 0, "empty": 0}
    op_count = sum(1 for p in projects if (p.get("is_operating") or "").strip().upper() == "TRUE")
    for r in results:
        counts[r["tier"]] += 1
    total_proj = len(results)

    print(f"\n{'─' * 85}")
    print(f"  Projects: {total_proj} ({op_count} operating, {total_proj - op_count} tender/pre-PPA)  |  "
          f"★ rich: {counts['rich']}  ⬖ moderate: {counts['moderate']}  "
          f"· thin: {counts['thin']}  empty: {counts['empty']}")

    # Coverage gaps: most under-populated fields
    all_spec_fields = [f for fields in SECTIONS.values() for f in fields]
    field_counts: dict[str, int] = {f: 0 for f in all_spec_fields}
    for p in projects:
        for f in all_spec_fields:
            if is_populated(p.get(f)):
                field_counts[f] += 1

    ranked = sorted(field_counts.items(), key=lambda x: x[1])
    missing = [(f, c) for f, c in ranked if c < total_proj]
    if missing:
        print(f"\n  Most under-populated fields ({total_proj} projects total):")
        for f, c in missing[:10]:
            fill_pct = c / total_proj * 100
            print(f"    {f:<40} {c}/{total_proj} ({fill_pct:.0f}% filled)")

    print()


def write_csv(results: list[dict], out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    csv_section_order = [SECTION_KEYS[s] for s in SECTIONS.keys()]
    filled_total_pairs = []
    for k in csv_section_order:
        filled_total_pairs.append(f"{k}_filled")
        filled_total_pairs.append(f"{k}_total")
    fieldnames = (
        ["slug", "capacity_mwp", "status", "is_operating"]
        + filled_total_pairs
        + ["total_filled", "total_possible", "completeness_pct", "tier"]
    )
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(results)
    print(f"  CSV written -> {out_path}")


def write_markdown_full(results: list[dict], projects: list[dict], out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)

    counts = {"rich": 0, "moderate": 0, "thin": 0, "empty": 0}
    for r in results:
        counts[r["tier"]] += 1

    rich_projects = [r for r in results if r["tier"] == "rich"]
    total_proj = len(results)
    op_count = sum(1 for p in projects if (p.get("is_operating") or "").strip().upper() == "TRUE")

    # Most under-populated fields
    all_spec_fields = [f for fields in SECTIONS.values() for f in fields]
    field_counts: dict[str, int] = {f: 0 for f in all_spec_fields}
    for p in projects:
        for f in all_spec_fields:
            if is_populated(p.get(f)):
                field_counts[f] += 1
    ranked = sorted(field_counts.items(), key=lambda x: x[1])
    missing = [(f, c) for f, c in ranked if c < total_proj]

    # Build field -> section map
    field_section: dict[str, str] = {}
    for sec, fields in SECTIONS.items():
        for f in fields:
            field_section[f] = sec

    lines: list[str] = []
    lines.append("# Solar specification completeness report")
    lines.append("")
    lines.append(f"**{total_proj} projects** ({op_count} operating, {total_proj - op_count} tender/pre-PPA) &mdash; "
                 f"{counts['rich']} rich, {counts['moderate']} moderate, "
                 f"{counts['thin']} thin, {counts['empty']} empty.")
    lines.append("")

    if rich_projects:
        lines.append("## Rich projects (>=50% complete)")
        lines.append("")
        lines.append("| Project | MWp | Status | % Complete |")
        lines.append("|---------|-----|--------|-----------|")
        for r in sorted(rich_projects, key=lambda x: x["completeness_pct"], reverse=True):
            lines.append(f"| {r['slug']} | {r['capacity_mwp']} | {r['status']} | {r['completeness_pct']}% |")
        lines.append("")

    lines.append("## Most under-populated fields")
    lines.append("")
    lines.append("| Field | Section | Filled | Total |")
    lines.append("|-------|---------|--------|-------|")
    for f, c in missing[:15]:
        sec = field_section.get(f, "")
        lines.append(f"| `{f}` | {sec} | {c} | {total_proj} |")
    lines.append("")

    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"  Markdown written -> {out_path}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    args = set(sys.argv[1:])
    do_csv = "--csv" in args or "--all" in args
    do_md = "--md" in args or "--all" in args

    projects = load_projects(CSV_PATH)
    results = [completeness(p) for p in projects]

    print_summary(projects)

    if do_csv:
        write_csv(results, CSV_OUT)

    if do_md:
        write_markdown_full(results, projects, MD_OUT)


if __name__ == "__main__":
    main()
