#!/usr/bin/env python3
"""Build a normalized non-hydro (solar, wind, thermal, biomass, cogeneration)
regulatory registry from official DoED pages.

Mirrors ``build_doed_hydropower_registry.py``. Legal categories are preserved:
a survey or generation licence does not prove construction, and only rows from
DoED's "Power Plants" pages receive ``delivery_status=operating-registry-listed``.
The free-text ``Address`` column is deliberately dropped because DoED fills it
with promoter phone numbers and contact names.

Usage:
  python scripts/build_doed_nonhydro_registry.py                 # live fetch
  python scripts/build_doed_nonhydro_registry.py --cache-dir DIR # save raw HTML too
  python scripts/build_doed_nonhydro_registry.py --from-cache DIR # offline re-parse
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timezone
from io import StringIO
from pathlib import Path
from typing import Any

import pandas as pd
import requests

try:
    from .build_doed_hydropower_registry import clean_cell, first_value, flatten_columns
    from .benchmark_hydromap_coverage import parse_number
except ImportError:  # Direct script execution adds scripts/ rather than the repository root.
    from build_doed_hydropower_registry import clean_cell, first_value, flatten_columns
    from benchmark_hydromap_coverage import parse_number


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_DIR = ROOT / "data" / "processed" / "tables"
REGISTRY_NAME = "doed_nonhydro_registry.csv"
SUMMARY_NAME = "doed_nonhydro_registry_summary.json"
# DoED has published "Ocotober" on at least one page; accept any month-like word.
UPDATED_RE = re.compile(r"Updated\s+on\s*-\s*([A-Za-z]+)\s+(\d{1,2}),?\s+(\d{4})", re.IGNORECASE)
MONTH_TYPOS = {"ocotober": "october"}

OUTPUT_FIELDS = [
    "record_id",
    "source_row_number",
    "project",
    "capacity_mw",
    "technology",
    "regulatory_category",
    "license_status",
    "delivery_status",
    "record_number",
    "record_date_bs",
    "validity_date_bs",
    "cod_date_bs",
    "promoter",
    "location_text",
    "latitude_1_dms",
    "latitude_2_dms",
    "longitude_1_dms",
    "longitude_2_dms",
    "source_page_id",
    "source_url",
    "source_updated_on",
]

TECHNOLOGIES = ("solar", "wind", "thermal", "biomass", "cogeneration")

# (page-path template, regulatory_category, license_status, delivery_status)
CATEGORIES = (
    ("powerplants{t}", "operating", "", "operating-registry-listed"),
    ("cl{t}", "generation_license", "generation_license", ""),
    ("sl{t}", "survey_license", "survey_license", ""),
    ("appcl{t}", "generation_application", "generation_application", ""),
    ("appsl{t}", "survey_application", "survey_application", ""),
)
# DoED page slugs that do not follow the template.
PATH_OVERRIDES = {"clbiomass": "clbiomass-77"}


@dataclass(frozen=True)
class SourceSpec:
    page_id: str
    path: str
    technology: str
    regulatory_category: str
    license_status: str = ""
    delivery_status: str = ""

    @property
    def url(self) -> str:
        return f"https://doed.gov.np/pages/{self.path}/"


def build_sources() -> list[SourceSpec]:
    sources = []
    for template, category, license_status, delivery_status in CATEGORIES:
        for tech in TECHNOLOGIES:
            path = template.format(t=tech)
            path = PATH_OVERRIDES.get(path, path)
            sources.append(SourceSpec(f"{category}_{tech}", path, tech, category, license_status, delivery_status))
    return sources


SOURCES = build_sources()


def parse_updated_on(html: str, source: SourceSpec) -> str:
    match = UPDATED_RE.search(html)
    if not match:
        raise ValueError(f"DoED page has no parseable update date: {source.url}")
    month = MONTH_TYPOS.get(match.group(1).casefold(), match.group(1))
    parsed = datetime.strptime(f"{month} {match.group(2)} {match.group(3)}", "%B %d %Y")
    return parsed.date().isoformat()


def parse_table(html: str, source: SourceSpec) -> pd.DataFrame:
    tables = pd.read_html(StringIO(html))
    if not tables:
        raise ValueError(f"DoED page contains no HTML table: {source.url}")
    frame = flatten_columns(tables[0])
    missing = {"Project", "Capacity (MW)"}.difference(frame.columns)
    if missing:
        raise ValueError(f"DoED table missing columns {sorted(missing)}: {source.url}")
    return frame[frame["Project"].map(clean_cell) != ""].reset_index(drop=True)


def blank_zero_dms(value: str) -> str:
    """DoED writes 00o 00' 00" when it has no coordinate; keep that as blank."""
    return "" if re.fullmatch(r"0+o\s*0+'\s*0+\"?", value.strip()) else value


def clean_integer_text(value: str) -> str:
    """pandas reads integer-like cells as floats; restore the published form."""
    return value[:-2] if re.fullmatch(r"\d+\.0", value) else value


def blank_zero_date(value: str) -> str:
    return "" if value.strip() in {"0000-00-00", "00-00-0000"} else value


def normalize_row(row: pd.Series, source: SourceSpec, updated_on: str) -> dict[str, Any]:
    project = first_value(row, "Project")
    capacity = parse_number(first_value(row, "Capacity (MW)"))
    record_number = clean_integer_text(first_value(row, "Lic No", "Appn No"))
    source_row_number = clean_integer_text(first_value(row, "S No"))
    identity = "|".join(
        [source.page_id, source_row_number, project, str(capacity if capacity is not None else ""), record_number]
    )
    return {
        "record_id": hashlib.sha256(identity.encode("utf-8")).hexdigest()[:20],
        "source_row_number": source_row_number,
        "project": project,
        "capacity_mw": capacity if capacity is not None else "",
        "technology": source.technology,
        "regulatory_category": source.regulatory_category,
        "license_status": source.license_status,
        "delivery_status": source.delivery_status,
        "record_number": record_number,
        "record_date_bs": blank_zero_date(first_value(row, "Isuue Date", "Issue Date", "Appn Date")),
        "validity_date_bs": blank_zero_date(first_value(row, "Validity")),
        "cod_date_bs": blank_zero_date(first_value(row, "C O D", "COD")),
        "promoter": first_value(row, "Promoter"),
        "location_text": first_value(row, "VDC/District"),
        "latitude_1_dms": blank_zero_dms(first_value(row, "Latitiude N", "Latitude N")),
        "latitude_2_dms": blank_zero_dms(first_value(row, "Latitiude N.1", "Latitude N.1")),
        "longitude_1_dms": blank_zero_dms(first_value(row, "Longitude E")),
        "longitude_2_dms": blank_zero_dms(first_value(row, "Longitude E.1")),
        "source_page_id": source.page_id,
        "source_url": source.url,
        "source_updated_on": updated_on,
    }


def parse_source(html: str, source: SourceSpec) -> tuple[list[dict[str, Any]], str]:
    updated_on = parse_updated_on(html, source)
    frame = parse_table(html, source)
    return [normalize_row(row, source, updated_on) for _, row in frame.iterrows()], updated_on


def fetch_html(source: SourceSpec, timeout: float, from_cache: Path | None) -> bytes:
    if from_cache is not None:
        return (from_cache / f"{source.path}.html").read_bytes()
    response = requests.get(source.url, timeout=timeout, headers={"User-Agent": "TransparentGov-DoED-Registry/1.0"})
    response.raise_for_status()
    return response.content


def build_registry(
    timeout: float = 30.0, from_cache: Path | None = None, cache_dir: Path | None = None
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    reports: list[dict[str, Any]] = []
    for source in SOURCES:
        content = fetch_html(source, timeout, from_cache)
        if cache_dir is not None:
            cache_dir.mkdir(parents=True, exist_ok=True)
            (cache_dir / f"{source.path}.html").write_bytes(content)
        source_rows, updated_on = parse_source(content.decode("utf-8", errors="replace"), source)
        rows.extend(source_rows)
        reports.append({
            "page_id": source.page_id,
            "url": source.url,
            "technology": source.technology,
            "regulatory_category": source.regulatory_category,
            "updated_on": updated_on,
            "rows": len(source_rows),
            "sha256": hashlib.sha256(content).hexdigest(),
        })
    ids = [row["record_id"] for row in rows]
    if len(ids) != len(set(ids)):
        raise ValueError("Normalized DoED non-hydro registry contains duplicate record_id values")
    capacity = Counter()
    for row in rows:
        if row["capacity_mw"] != "":
            capacity[f"{row['technology']}|{row['regulatory_category']}"] += float(row["capacity_mw"])
    summary = {
        "schema_version": 1,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source_authority": "Nepal Department of Electricity Development",
        "scope": (
            "Non-hydro regulatory and operating records; licences and applications do not prove physical "
            "construction. Address column omitted (contains personal contact details)."
        ),
        "rows": len(rows),
        "technology_counts": dict(sorted(Counter(r["technology"] for r in rows).items())),
        "category_counts": dict(sorted(Counter(r["regulatory_category"] for r in rows).items())),
        "listed_capacity_mw_by_technology_and_category": {k: round(v, 3) for k, v in sorted(capacity.items())},
        "sources": reports,
    }
    return rows, summary


def write_registry(output_dir: Path, rows: list[dict[str, Any]], summary: dict[str, Any]) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows, columns=OUTPUT_FIELDS).to_csv(output_dir / REGISTRY_NAME, index=False)
    (output_dir / SUMMARY_NAME).write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--timeout", type=float, default=30.0)
    parser.add_argument("--from-cache", type=Path, help="parse <path>.html files from this directory instead of fetching")
    parser.add_argument("--cache-dir", type=Path, help="also save fetched raw HTML here")
    parser.add_argument("--no-write", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    rows, summary = build_registry(args.timeout, args.from_cache, args.cache_dir)
    if args.no_write:
        print(json.dumps(summary, indent=2, ensure_ascii=False))
        return 0
    output_dir = args.output_dir.expanduser().resolve()
    write_registry(output_dir, rows, summary)
    print(f"Wrote {len(rows)} normalized DoED non-hydro records to {output_dir / REGISTRY_NAME}")
    print(json.dumps(summary["category_counts"], sort_keys=True))
    print(json.dumps(summary["technology_counts"], sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
