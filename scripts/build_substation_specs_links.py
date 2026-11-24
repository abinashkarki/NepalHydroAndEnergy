#!/usr/bin/env python3
"""Refresh generated link columns in data/substation_specs.csv.

Currently one generated column:

* ``linked_solar_award_mw`` - sum of ``capacity_mw`` over rows of
  ``data/solar_project_specs.csv`` whose ``substation`` field names the
  substation (NEA 2024 solar LoI award records name the grid substation each
  award connects to).

Names are matched with :func:`normalize_name` plus a small, explicit alias
table. A district guard rejects a name match when both CSVs give a district
and they disagree. Every solar substation name that does not resolve is
reported with a reason, so the unmatched list is reproducible.

Usage::

    python scripts/build_substation_specs_links.py           # rewrite CSV in place
    python scripts/build_substation_specs_links.py --check   # exit 1 if stale
    python scripts/build_substation_specs_links.py --report  # print match table
"""
from __future__ import annotations

import argparse
import csv
import io
import re
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SUBSTATION_CSV = ROOT / "data" / "substation_specs.csv"
SOLAR_CSV = ROOT / "data" / "solar_project_specs.csv"

# Solar-LoI spelling -> normalised substation name. Only spelling variants of
# the same NEA substation belong here.
ALIASES = {
    "sunawal": "sunwal",
    "sandikharka": "sandhikharka",
    "paudi": "paudiamarai",
    "bhurigaun": "bhurigaon",
    "attariya": "attaria",
}

# Names that collide with an inventory row but are a different place.
EXCLUDED = {
    "maharajgunj": "NEA planned Maharajgunj 132/11 kV is a Kathmandu Valley site; the solar LoI Maharajgunj is in Kapilvastu",
}

DISTRICT_EQUIVALENTS = {
    "tanahu": "tanahun",
    "nawalparasiwest": "nawalparasi",
    "nawalparasieast": "nawalparasi",
}


def normalize_name(value: str) -> str:
    """Lower-case, drop bracketed qualifiers and generic words, keep [a-z0-9]."""
    text = (value or "").lower()
    text = re.sub(r"\([^)]*\)", " ", text)
    text = re.sub(r"\b(substation|sub-station|s/s|grid|hub|switching|kv)\b", " ", text)
    text = re.sub(r"[^a-z0-9]+", "", text)
    return ALIASES.get(text, text)


def normalize_district(value: str) -> str:
    text = re.sub(r"[^a-z]+", "", (value or "").lower())
    return DISTRICT_EQUIVALENTS.get(text, text)


def fmt_mw(value: float) -> str:
    value = round(value, 3)
    return str(int(value)) if value == int(value) else f"{value:g}"


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        return list(reader.fieldnames or []), list(reader)


def compute_links(
    substations: list[dict[str, str]], solar_rows: list[dict[str, str]]
) -> tuple[dict[str, float], list[dict[str, str]]]:
    """Return ({substation slug: MW}, match log rows)."""
    index: dict[str, dict[str, str]] = {}
    for row in substations:
        key = normalize_name(row.get("substation_name", ""))
        if key and key not in index:
            index[key] = row
    totals: dict[str, float] = defaultdict(float)
    log: list[dict[str, str]] = []
    for solar in solar_rows:
        raw = (solar.get("substation") or "").strip()
        if not raw:
            continue
        key = normalize_name(raw)
        entry = {"solar_slug": solar.get("slug", ""), "solar_substation": raw,
                 "solar_district": solar.get("district", ""), "substation_slug": "", "reason": ""}
        try:
            mw = float(solar.get("capacity_mw") or "")
        except ValueError:
            entry["reason"] = "no numeric capacity_mw"
            log.append(entry)
            continue
        if key in EXCLUDED:
            entry["reason"] = "excluded: " + EXCLUDED[key]
        elif key not in index:
            entry["reason"] = "no substation_specs row with this name"
        else:
            target = index[key]
            d_sub = normalize_district(target.get("district", ""))
            d_sol = normalize_district(solar.get("district", ""))
            if d_sub and d_sol and d_sub != d_sol:
                entry["reason"] = f"district mismatch ({target.get('district')} vs {solar.get('district')})"
            else:
                entry["substation_slug"] = target["slug"]
                entry["reason"] = "matched"
                totals[target["slug"]] += mw
        log.append(entry)
    return dict(totals), log


def render(fieldnames: list[str], rows: list[dict[str, str]]) -> str:
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=fieldnames, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return buf.getvalue()


def apply_links(rows: list[dict[str, str]], totals: dict[str, float]) -> list[dict[str, str]]:
    out = []
    for row in rows:
        row = dict(row)
        mw = totals.get(row["slug"])
        row["linked_solar_award_mw"] = fmt_mw(mw) if mw else ""
        out.append(row)
    return out


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--check", action="store_true", help="exit 1 if the CSV is not up to date")
    parser.add_argument("--report", action="store_true", help="print the per-solar-row match log")
    args = parser.parse_args(argv)

    fieldnames, rows = read_csv(SUBSTATION_CSV)
    _, solar_rows = read_csv(SOLAR_CSV)
    totals, log = compute_links(rows, solar_rows)
    rendered = render(fieldnames, apply_links(rows, totals))

    matched = [e for e in log if e["reason"] == "matched"]
    unmatched = sorted({(e["solar_substation"], e["reason"]) for e in log if e["reason"] != "matched"})
    if args.report:
        for e in log:
            print(f"{e['solar_slug']}\t{e['solar_substation']}\t{e['solar_district']}\t{e['substation_slug'] or '-'}\t{e['reason']}")
    print(
        f"substation solar links: {len(matched)}/{len(log)} solar rows matched to "
        f"{len(totals)} substations ({fmt_mw(sum(totals.values()))} MW); "
        f"{len(unmatched)} unmatched names",
        file=sys.stderr,
    )
    if args.report:
        for name, reason in unmatched:
            print(f"  unmatched: {name} - {reason}", file=sys.stderr)

    current = SUBSTATION_CSV.read_text(encoding="utf-8")
    if args.check:
        if current != rendered:
            print("data/substation_specs.csv linked_solar_award_mw is stale; run scripts/build_substation_specs_links.py", file=sys.stderr)
            return 1
        return 0
    if current != rendered:
        SUBSTATION_CSV.write_text(rendered, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
