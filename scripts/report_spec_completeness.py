#!/usr/bin/env python3
"""Data completeness report for project_specs.csv.

Usage:
    python3 scripts/report_spec_completeness.py          # terminal summary
    python3 scripts/report_spec_completeness.py --csv    # also write CSV
    python3 scripts/report_spec_completeness.py --md     # also write markdown
    python3 scripts/report_spec_completeness.py --all    # write both
"""

import csv
import sys
from collections import OrderedDict
from pathlib import Path

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

SECTIONS: dict[str, list[str]] = {
    "Engineering": [
        "gross_head_m",
        "design_discharge_m3s",
        "headrace_tunnel_km",
        "dam_height_m",
        "dam_type",
        "num_units",
        "unit_capacity_mw",
        "turbine_type",
        "underground_powerhouse",
        "penstock_length_m",
        "penstock_diameter_m",
        "tailrace_length_m",
    ],
    "Storage": [
        "total_storage_mcm",
        "effective_storage_mcm",
        "pumped_storage_mw",
    ],
    "Output": [
        "annual_design_energy_gwh",
        "dry_season_energy_gwh",
        "dry_share_pct",
        "plant_load_factor_pct",
        "q_design",
        "project_type",
        "catchment_area_km2",
        "environmental_release_m3s",
    ],
    "Financial": [
        "total_cost_usd_m",
        "cost_per_mw_usd_m",
        "ppa_rate_wet_npr_kwh",
        "ppa_rate_dry_npr_kwh",
        "debt_equity_ratio",
    ],
    "Governance": [
        "developer",
        "concession_type",
        "lead_financier",
        "concession_years",
    ],
    "Schedule": [
        "construction_start_year",
        "cod_year",
        "completion_pct",
    ],
}

REGISTRY_FIELDS = {
    "slug",
    "capacity_mw",
    "river",
    "status",
    "source_note",
    "last_updated",
}

CSV_PATH = Path("data/project_specs.csv")
CSV_OUT = Path("data/processed/tables/spec_completeness_report.csv")
MD_OUT = Path("data/processed/tables/spec_completeness_report.md")

# ---------------------------------------------------------------------------
# Core logic
# ---------------------------------------------------------------------------


def load_projects(csv_path: Path) -> list[dict]:
    """Read project_specs.csv and return list of row dicts."""
    with open(csv_path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def is_populated(value: str | None) -> bool:
    """Return True if value is non-empty and non-null."""
    if value is None:
        return False
    return value.strip() != ""


def tier_label(pct: float) -> str:
    """Return data-quality tier string for a completeness percentage."""
    if pct >= 50:
        return "rich"
    if pct >= 25:
        return "moderate"
    if pct > 0:
        return "thin"
    return "empty"


def completeness(project: dict) -> dict:
    """Calculate per-section and overall completeness for one project."""
    result: dict = {"slug": project["slug"]}
    filled_total = 0
    possible_total = 0

    for section_name, fields in SECTIONS.items():
        filled = sum(1 for f in fields if is_populated(project.get(f)))
        total = len(fields)
        result[f"{section_name.lower()}_filled"] = filled
        result[f"{section_name.lower()}_total"] = total
        filled_total += filled
        possible_total += total

    result["total_filled"] = filled_total
    result["total_possible"] = possible_total
    result["completeness_pct"] = (
        round(filled_total / possible_total * 100, 1) if possible_total else 0.0
    )
    result["tier"] = tier_label(result["completeness_pct"])
    result["capacity_mw"] = project.get("capacity_mw", "")
    result["status"] = project.get("status", "")
    return result


# ---------------------------------------------------------------------------
# Reporting helpers
# ---------------------------------------------------------------------------


def _section_label(name: str) -> str:
    """Short label for terminal table."""
    return {"Engineering": "Eng", "Storage": "Sto", "Output": "Out",
            "Financial": "Fin", "Governance": "Gov", "Schedule": "Sch"}.get(name, name)


def _bar(filled: int, total: int, width: int = 12) -> str:
    """Draw an ASCII bar of relative completeness."""
    if total == 0:
        return "·" * width
    ratio = filled / total
    blocks = round(ratio * width)
    return "█" * blocks + "░" * (width - blocks)


def _pct_str(filled: int, total: int) -> str:
    if total == 0:
        return "---"
    return f"{filled/total*100:3.0f}%"


def _tier_icon(tier: str) -> str:
    return {"rich": "★", "moderate": "⬖", "thin": "·", "empty": " "}.get(tier, tier)


def print_summary(projects: list[dict]) -> None:
    """Print terminal summary: per-project bars, section breakdown, gaps."""
    results = [completeness(p) for p in projects]

    # --- Section header ---
    sect_names = list(SECTIONS.keys())
    col_order = ["capacity_mw", "status"] + sect_names + ["total", "tier"]
    header_cols = ["Project", "MW", "Status"] + [_section_label(s) for s in sect_names] + ["Total", "Tier"]

    print()

    # Per-project rows
    for r in results:
        slug = r["slug"]
        parts = [f"{slug:<35}", f"{r['capacity_mw']:>5}", f"{r['status']:<22}"]
        for s in sect_names:
            fill = r[f"{s.lower()}_filled"]
            tot = r[f"{s.lower()}_total"]
            parts.append(_bar(fill, tot, 10))
        parts.append(f"{r['completeness_pct']:>5.0f}%")
        parts.append(_tier_icon(r["tier"]))
        print("  ".join(parts))

    # --- Summary counts by tier ---
    counts = {"rich": 0, "moderate": 0, "thin": 0, "empty": 0}
    for r in results:
        counts[r["tier"]] += 1
    total_proj = len(results)

    print(f"\n{'─' * 85}")
    print(f"  Projects: {total_proj}  |  "
          f"★ rich: {counts['rich']}  ⬖ moderate: {counts['moderate']}  "
          f"· thin: {counts['thin']}  empty: {counts['empty']}")

    # --- Coverage gaps: most under-populated fields ---
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
            print(f"    {f:<35} {c}/{total_proj} ({fill_pct:.0f}% filled)")

    print()


def write_csv(results: list[dict], out_path: Path) -> None:
    """Write spec_completeness_report.csv."""
    out_path.parent.mkdir(parents=True, exist_ok=True)
    csv_section_order = ["engineering", "output", "financial", "governance", "schedule", "storage"]
    filled_total_pairs = []
    for k in csv_section_order:
        filled_total_pairs.append(f"{k}_filled")
        filled_total_pairs.append(f"{k}_total")
    fieldnames = (
        ["slug", "capacity_mw", "status"]
        + filled_total_pairs
        + ["total_filled", "total_possible", "completeness_pct", "tier"]
    )
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(results)
    print(f"  CSV written → {out_path}")


def write_markdown(results: list[dict], out_path: Path) -> None:
    """Write spec_completeness_report.md."""
    out_path.parent.mkdir(parents=True, exist_ok=True)

    counts = {"rich": 0, "moderate": 0, "thin": 0, "empty": 0}
    for r in results:
        counts[r["tier"]] += 1

    rich_projects = [r for r in results if r["tier"] == "rich"]

    # Most under-populated fields
    all_spec_fields = [f for fields in SECTIONS.values() for f in fields]
    field_counts: dict[str, int] = {f: 0 for f in all_spec_fields}
    # We need the original projects; compute from results instead
    total_proj = len(results)
    # Re-derive field counts from the per-section filled numbers
    # Actually we need to re-read projects, but let's derive from results
    # results only have aggregated numbers, not per-field counts.
    # We'll pass them in via a separate computation.

    lines: list[str] = []
    lines.append("# Specification completeness report")
    lines.append("")
    lines.append(f"**{total_proj} projects** with spec data &mdash; "
                 f"{counts['rich']} rich, {counts['moderate']} moderate, "
                 f"{counts['thin']} thin, {counts['empty']} empty.")
    lines.append("")

    # Rich projects table
    if rich_projects:
        lines.append("## Rich projects (≥50% complete)")
        lines.append("")
        lines.append("| Project | MW | % Complete |")
        lines.append("|---------|----|-----------|")
        for r in sorted(rich_projects, key=lambda x: x["completeness_pct"], reverse=True):
            lines.append(f"| {r['slug']} | {r['capacity_mw']} | {r['completeness_pct']}% |")
        lines.append("")

    # Most under-populated fields — we recompute from the results' per-section filled totals
    # Actually we need raw project data. Let's accept projects as a second param.
    lines.append("## Most under-populated fields")
    lines.append("")
    lines.append("| Field | Section | Filled | Total |")
    lines.append("|-------|---------|--------|-------|")

    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"  Markdown written → {out_path}")


def write_markdown_full(results: list[dict], projects: list[dict], out_path: Path) -> None:
    """Write complete markdown report with field-level details."""
    out_path.parent.mkdir(parents=True, exist_ok=True)

    counts = {"rich": 0, "moderate": 0, "thin": 0, "empty": 0}
    for r in results:
        counts[r["tier"]] += 1

    rich_projects = [r for r in results if r["tier"] == "rich"]
    total_proj = len(results)

    # Most under-populated fields
    all_spec_fields = [f for fields in SECTIONS.values() for f in fields]
    field_counts: dict[str, int] = {f: 0 for f in all_spec_fields}
    for p in projects:
        for f in all_spec_fields:
            if is_populated(p.get(f)):
                field_counts[f] += 1
    ranked = sorted(field_counts.items(), key=lambda x: x[1])
    missing = [(f, c) for f, c in ranked if c < total_proj]

    # Build field → section map
    field_section: dict[str, str] = {}
    for sec, fields in SECTIONS.items():
        for f in fields:
            field_section[f] = sec

    lines: list[str] = []
    lines.append("# Specification completeness report")
    lines.append("")
    lines.append(f"**{total_proj} projects** with spec data &mdash; "
                 f"{counts['rich']} rich, {counts['moderate']} moderate, "
                 f"{counts['thin']} thin, {counts['empty']} empty.")
    lines.append("")

    if rich_projects:
        lines.append("## Rich projects (≥50% complete)")
        lines.append("")
        lines.append("| Project | MW | % Complete |")
        lines.append("|---------|----|-----------|")
        for r in sorted(rich_projects, key=lambda x: x["completeness_pct"], reverse=True):
            lines.append(f"| {r['slug']} | {r['capacity_mw']} | {r['completeness_pct']}% |")
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

    print(f"  Markdown written → {out_path}")


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
