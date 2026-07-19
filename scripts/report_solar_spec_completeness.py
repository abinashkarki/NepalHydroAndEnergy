#!/usr/bin/env python3
"""Report independent V1 evidence coverage axes for solar records.

There is intentionally no overall rich/moderate/thin score: a procurement row
can have excellent provenance while still having no delivery, output or precise
geography evidence.
"""

from __future__ import annotations

import csv
import sys
from pathlib import Path

CSV_PATH = Path("data/solar_project_specs.csv")
CSV_OUT = Path("data/processed/tables/solar_spec_completeness_report.csv")
MD_OUT = Path("data/processed/tables/solar_spec_completeness_report.md")

AXES = {
    "lifecycle": ["record_kind", "delivery_status", "status_as_of", "operating_status", "delivery_verification_note"],
    "output": ["expected_annual_generation_gwh", "expected_generation_basis"],
    "geography": ["latitude", "longitude", "province", "municipality", "geography_verification_status"],
    "provenance": ["source_slug", "source_type", "source_date", "verified_on", "evidence_scope", "verification_status"],
}


def populated(value: str | None) -> bool:
    return bool(value and value.strip())


def covered(axis: str, field: str, value: str | None) -> bool:
    """Count explicit missing markers as honest metadata, not data coverage."""
    if not populated(value):
        return False
    if axis == "output" and value == "not-published-in-source":
        return False
    if axis == "geography" and value == "missing":
        return False
    return True


def load() -> list[dict[str, str]]:
    with CSV_PATH.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def coverage(row: dict[str, str]) -> dict[str, object]:
    result: dict[str, object] = {
        "slug": row["slug"],
        "capacity_mw": row.get("capacity_mw", ""),
        "record_kind": row.get("record_kind", ""),
        "delivery_status": row.get("delivery_status", ""),
    }
    for axis, fields in AXES.items():
        filled = sum(covered(axis, field, row.get(field)) for field in fields)
        result[f"{axis}_filled"] = filled
        result[f"{axis}_total"] = len(fields)
        result[f"{axis}_pct"] = round(100 * filled / len(fields), 1)
    return result


def bar(percent: float, width: int = 10) -> str:
    blocks = round(percent / 100 * width)
    return "█" * blocks + "░" * (width - blocks)


def print_summary(rows: list[dict[str, str]], results: list[dict[str, object]]) -> None:
    print("\nSolar V1 evidence coverage (axes are independent; no overall quality tier)\n")
    print("  slug                                 delivery status                 life        output      geo         provenance")
    for result in results:
        axes = "  ".join(bar(float(result[f"{axis}_pct"])) for axis in AXES)
        print(f"  {str(result['slug']):<36} {str(result['delivery_status']):<31} {axes}")

    print(f"\n  Records: {len(rows)}")
    for status in sorted({row["delivery_status"] for row in rows}):
        selected = [row for row in rows if row["delivery_status"] == status]
        capacity = sum(float(row.get("capacity_mw") or 0) for row in selected)
        print(f"  {status}: {len(selected)} records / {capacity:.2f} MW")

    print("\n  Axis averages:")
    for axis in AXES:
        average = sum(float(result[f"{axis}_pct"]) for result in results) / len(results)
        print(f"    {axis:<12} {average:5.1f}%")

    print("\n  Missing-field coverage:")
    for axis, fields in AXES.items():
        for field in fields:
            count = sum(covered(axis, field, row.get(field)) for row in rows)
            if count < len(rows):
                print(f"    {axis:<12} {field:<38} {count}/{len(rows)}")
    print()


def write_csv(results: list[dict[str, object]]) -> None:
    CSV_OUT.parent.mkdir(parents=True, exist_ok=True)
    fields = ["slug", "capacity_mw", "record_kind", "delivery_status"]
    for axis in AXES:
        fields.extend([f"{axis}_filled", f"{axis}_total", f"{axis}_pct"])
    with CSV_OUT.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(results)
    print(f"  CSV written -> {CSV_OUT}")


def write_markdown(rows: list[dict[str, str]], results: list[dict[str, object]]) -> None:
    MD_OUT.parent.mkdir(parents=True, exist_ok=True)
    operating = [row for row in rows if row["delivery_status"] == "operating-registry-listed"]
    awards = [row for row in rows if row["delivery_status"] == "award-only-delivery-unknown"]
    lines = [
        "# Solar V1 evidence coverage",
        "",
        "Coverage is reported on four independent axes. There is no overall rich/moderate/thin score because complete procurement metadata does not establish project delivery.",
        "",
        f"- **Operating-registry-listed:** {len(operating)} records / {sum(float(r.get('capacity_mw') or 0) for r in operating):.2f} MW",
        f"- **Award-only, delivery unknown:** {len(awards)} records / {sum(float(r.get('capacity_mw') or 0) for r in awards):.2f} MW",
        "",
        "## Axis coverage",
        "",
        "| Axis | Average coverage | Interpretation |",
        "|---|---:|---|",
    ]
    meanings = {
        "lifecycle": "Evidence class, dated delivery status and its limitation",
        "output": "Expected or observed generation and its basis",
        "geography": "Coordinates plus administrative/siting verification",
        "provenance": "Source, date, review and evidence scope",
    }
    for axis in AXES:
        average = sum(float(result[f"{axis}_pct"]) for result in results) / len(results)
        lines.append(f"| {axis.title()} | {average:.1f}% | {meanings[axis]} |")
    lines.extend(["", "## Material gaps", ""])
    for axis, fields in AXES.items():
        for field in fields:
            count = sum(covered(axis, field, row.get(field)) for row in rows)
            if count < len(rows):
                lines.append(f"- **{axis} / `{field}`:** {count} of {len(rows)} records populated")
    lines.append("")
    MD_OUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"  Markdown written -> {MD_OUT}")


def main() -> None:
    args = set(sys.argv[1:])
    rows = load()
    results = [coverage(row) for row in rows]
    print_summary(rows, results)
    if "--csv" in args or "--all" in args:
        write_csv(results)
    if "--md" in args or "--all" in args:
        write_markdown(rows, results)


if __name__ == "__main__":
    main()
