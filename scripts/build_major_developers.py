#!/usr/bin/env python3
"""Rank hydropower promoters by MW from the DoED registry.

Reads ``data/processed/tables/doed_hydropower_registry.csv`` (active rows
only) and writes ``data/major_developers_nepse.csv`` with the top N promoters
by operating plus generation-licensed capacity.

Definitions (all sums of DoED ``capacity_mw`` over active records):
- operating_mw_approx: records in DoED's operating power-plant lists
  (``delivery_status == operating``).
- pipeline_mw_approx: generation-licence records not in the operating lists.
- survey_license_mw: survey-licence records (reported separately, not pipeline).

Promoter names are grouped by a conservative normalisation (case, punctuation
and legal suffixes such as "Pvt. Ltd."/"Limited" removed). No promoter is merged
with a parent group, and ``nepse_ticker`` is left blank unless a verified ticker
is supplied in ``VERIFIED_TICKERS``.
"""
from __future__ import annotations

import argparse
import csv
import re
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REGISTRY = Path("data/processed/tables/doed_hydropower_registry.csv")
SPECS = Path("data/project_specs.csv")
OUTPUT = Path("data/major_developers_nepse.csv")
LAST_UPDATED = "2026-11-24"

# Only tickers confirmed against NEPSE/SEBON records belong here.
VERIFIED_TICKERS: dict[str, str] = {}

SUFFIXES = (
    "private limited", "pvt limited", "pvt ltd", "p ltd", "pvt", "limited", "ltd",
    "company", "co", "inc",
)

COLUMNS = [
    "rank", "developer_slug", "developer_name", "entity_type", "nepse_ticker",
    "operating_mw_approx", "pipeline_mw_approx", "survey_license_mw",
    "operating_records", "generation_license_records", "survey_license_records",
    "largest_record_project", "largest_record_mw", "flagship_project_slugs",
    "source_basis", "source_url", "last_updated",
]


def normalise(name: str) -> str:
    text = name.casefold().replace("&", " and ")
    text = re.sub(r"[^a-z0-9 ]+", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    changed = True
    while changed:
        changed = False
        for suffix in SUFFIXES:
            if text.endswith(" " + suffix):
                text = text[: -len(suffix) - 1].strip()
                changed = True
    return text


def slugify(text: str) -> str:
    return re.sub(r"-+", "-", re.sub(r"[^a-z0-9]+", "-", text)).strip("-")


def entity_type(name: str) -> str:
    key = name.casefold()
    if "nepal electricity authority" in key:
        return "state utility"
    if re.search(r"[,/;]", key):
        return "multiple promoters (as listed by DoED)"
    return "company (as listed by DoED)"


def to_float(value: str) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def river_key(value: str) -> str:
    value = re.sub(r"\(.*?\)", "", value.casefold())
    return re.sub(r"[^a-z]", "", value.replace("river", "").replace("khola", ""))


def load_specs(root: Path) -> list[dict[str, str]]:
    path = root / SPECS
    if not path.exists():
        return []
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def match_slug(project: dict[str, str], specs: list[dict[str, str]]) -> str:
    """Return a project_specs slug only on same river and capacity within 1 MW."""
    river = river_key(project.get("river", ""))
    cap = to_float(project.get("capacity_mw", ""))
    if not river or not cap:
        return ""
    hits = [
        row["slug"] for row in specs
        if river_key(row.get("river", "")) == river
        and abs(to_float(row.get("capacity_mw", "")) - cap) <= 1.0
    ]
    return hits[0] if len(hits) == 1 else ""


def build(root: Path, top: int) -> list[dict[str, object]]:
    with (root / REGISTRY).open(encoding="utf-8", newline="") as handle:
        rows = [r for r in csv.DictReader(handle) if r.get("record_status") == "active"]
    specs = load_specs(root)

    groups: dict[str, dict] = defaultdict(lambda: {
        "names": defaultdict(int), "op": 0.0, "gl": 0.0, "sl": 0.0,
        "n_op": 0, "n_gl": 0, "n_sl": 0, "projects": [],
    })
    for row in rows:
        promoter = (row.get("promoter") or "").strip()
        key = normalise(promoter)
        if not key:
            continue
        cap = to_float(row.get("capacity_mw", ""))
        group = groups[key]
        group["names"][promoter] += 1
        if row.get("delivery_status") == "operating":
            group["op"] += cap
            group["n_op"] += 1
            group["projects"].append(row)
        elif row.get("regulatory_category") == "generation_license":
            group["gl"] += cap
            group["n_gl"] += 1
            group["projects"].append(row)
        elif row.get("regulatory_category") == "survey_license":
            group["sl"] += cap
            group["n_sl"] += 1

    ranked = sorted(
        (g for g in groups.items() if g[1]["op"] + g[1]["gl"] > 0),
        key=lambda item: (-(item[1]["op"] + item[1]["gl"]), item[0]),
    )[:top]

    out: list[dict[str, object]] = []
    for rank, (key, group) in enumerate(ranked, start=1):
        name = max(group["names"].items(), key=lambda kv: (kv[1], kv[0]))[0]
        largest = max(group["projects"], key=lambda r: to_float(r.get("capacity_mw", "")))
        slugs = sorted({s for s in (match_slug(p, specs) for p in group["projects"]) if s})
        out.append({
            "rank": rank,
            "developer_slug": slugify(key),
            "developer_name": name,
            "entity_type": entity_type(name),
            "nepse_ticker": VERIFIED_TICKERS.get(slugify(key), ""),
            "operating_mw_approx": round(group["op"], 3),
            "pipeline_mw_approx": round(group["gl"], 3),
            "survey_license_mw": round(group["sl"], 3),
            "operating_records": group["n_op"],
            "generation_license_records": group["n_gl"],
            "survey_license_records": group["n_sl"],
            "largest_record_project": largest.get("project", ""),
            "largest_record_mw": to_float(largest.get("capacity_mw", "")),
            "flagship_project_slugs": ";".join(slugs),
            "source_basis": "DoED registry promoter field, active records; operating = DoED operating lists; "
                            "pipeline = generation licences not in operating lists",
            "source_url": "https://doed.gov.np/pages/",
            "last_updated": LAST_UPDATED,
        })
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--repo-root", type=Path, default=ROOT)
    parser.add_argument("--top", type=int, default=30)
    parser.add_argument("--output", type=Path, default=None)
    args = parser.parse_args()
    rows = build(args.repo_root, args.top)
    output = args.output or (args.repo_root / OUTPUT)
    with output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=COLUMNS)
        writer.writeheader()
        writer.writerows(rows)
    print(f"wrote {len(rows)} developers to {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
