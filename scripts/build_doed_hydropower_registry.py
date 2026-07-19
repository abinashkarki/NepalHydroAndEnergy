#!/usr/bin/env python3
"""Build a normalized hydropower regulatory registry from official DoED pages.

The output preserves legal/regulatory categories and does not infer physical
construction from a generation licence. Only official power-plant rows receive
``delivery_status=operating``.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from io import StringIO
from pathlib import Path
from typing import Any

import pandas as pd
import requests

try:
    from .benchmark_hydromap_coverage import classify_energy_type, parse_number
except ImportError:  # Direct script execution adds scripts/ rather than the repository root.
    from benchmark_hydromap_coverage import classify_energy_type, parse_number


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_DIR = ROOT / "data" / "processed" / "tables"
REGISTRY_NAME = "doed_hydropower_registry.csv"
SUMMARY_NAME = "doed_hydropower_registry_summary.json"
UPDATED_RE = re.compile(r"Updated\s+on\s*-\s*([A-Za-z]+\s+\d{1,2},?\s+\d{4})", re.IGNORECASE)

OUTPUT_FIELDS = [
    "record_id",
    "source_row_number",
    "project",
    "capacity_mw",
    "river",
    "technology",
    "regulatory_category",
    "record_status",
    "license_status",
    "study_status",
    "delivery_status",
    "record_number",
    "record_date_bs",
    "validity_date_bs",
    "cod_date_bs",
    "promoter",
    "address",
    "latitude_1_dms",
    "latitude_2_dms",
    "longitude_1_dms",
    "longitude_2_dms",
    "location_text",
    "source_page_id",
    "source_url",
    "source_updated_on",
]


@dataclass(frozen=True)
class SourceSpec:
    page_id: str
    path: str
    regulatory_category: str
    minimum_rows: int
    record_status: str = "active"
    license_status: str = ""
    study_status: str = ""
    delivery_status: str = ""

    @property
    def url(self) -> str:
        return f"https://doed.gov.np/pages/{self.path}"


SOURCES = [
    SourceSpec("survey_license_gt_1mw", "hydromorethan1", "survey_license", 200, license_status="survey_license"),
    SourceSpec("survey_license_lt_1mw", "hydrolessthan1", "survey_license", 10, license_status="survey_license"),
    SourceSpec(
        "generation_license_gt_1mw",
        "clhydromorethan1",
        "generation_license",
        200,
        license_status="generation_license",
    ),
    SourceSpec(
        "generation_license_lt_1mw",
        "clhydrolessthan1",
        "generation_license",
        10,
        license_status="generation_license",
    ),
    SourceSpec(
        "survey_application_gt_1mw",
        "appslhydromorethan1",
        "survey_application",
        200,
        license_status="survey_application",
    ),
    SourceSpec(
        "survey_application_lt_1mw",
        "appslhydrolessthan1",
        "survey_application",
        1,
        license_status="survey_application",
    ),
    SourceSpec(
        "generation_application",
        "appclhydro",
        "generation_application",
        30,
        license_status="generation_application",
    ),
    SourceSpec(
        "operating_gt_1mw",
        "powerplantsmorethan1",
        "operating_record",
        150,
        license_status="operating_record",
        delivery_status="operating",
    ),
    SourceSpec(
        "operating_lt_1mw",
        "powerplantslessthan1",
        "operating_record",
        10,
        license_status="operating_record",
        delivery_status="operating",
    ),
    SourceSpec(
        "gon_under_study",
        "gonunderstudy",
        "gon_under_study",
        30,
        study_status="under_study",
    ),
    SourceSpec("gon_studied", "gonstudied", "gon_studied", 20, study_status="studied"),
    SourceSpec(
        "cancelled_survey_license",
        "slc",
        "cancelled_survey_license",
        100,
        record_status="cancelled",
        license_status="survey_license_cancelled",
    ),
    SourceSpec(
        "cancelled_generation_license",
        "glc",
        "cancelled_generation_license",
        20,
        record_status="cancelled",
        license_status="generation_license_cancelled",
    ),
    SourceSpec(
        "cancelled_generation_application",
        "generationcanceled",
        "cancelled_generation_application",
        10,
        record_status="cancelled",
        license_status="generation_application_cancelled",
    ),
    SourceSpec(
        "cancelled_survey_application",
        "canceled_hydro/",
        "cancelled_survey_application",
        2000,
        record_status="cancelled",
        license_status="survey_application_cancelled",
    ),
]


def clean_cell(value: Any) -> str:
    if value is None or pd.isna(value):
        return ""
    text = " ".join(str(value).replace("\xa0", " ").split())
    return "" if text.casefold() == "nan" else text


def flatten_columns(frame: pd.DataFrame) -> pd.DataFrame:
    result = frame.copy()
    if isinstance(result.columns, pd.MultiIndex):
        result.columns = [clean_cell(column[-1]) for column in result.columns]
    else:
        result.columns = [clean_cell(column) for column in result.columns]
    if "Project" not in result.columns and not result.empty:
        first_row = [clean_cell(value) for value in result.iloc[0].tolist()]
        if "Project" in first_row:
            result = result.iloc[1:].copy()
            result.columns = first_row
    deduped: list[str] = []
    counts: dict[str, int] = {}
    for column in result.columns:
        base = clean_cell(column)
        count = counts.get(base, 0)
        deduped.append(base if count == 0 else f"{base}.{count}")
        counts[base] = count + 1
    result.columns = deduped
    return result.reset_index(drop=True)


def parse_updated_on(html: str, source: SourceSpec) -> str:
    match = UPDATED_RE.search(html)
    if not match:
        raise ValueError(f"DoED page has no parseable update date: {source.url}")
    raw = match.group(1).replace(",", "")
    parsed = datetime.strptime(raw, "%B %d %Y")
    return parsed.date().isoformat()


def parse_table(html: str, source: SourceSpec) -> pd.DataFrame:
    tables = pd.read_html(StringIO(html))
    if not tables:
        raise ValueError(f"DoED page contains no HTML table: {source.url}")
    frame = flatten_columns(tables[0])
    required = {"Project", "Capacity (MW)"}
    missing = required.difference(frame.columns)
    if missing:
        raise ValueError(f"DoED table missing columns {sorted(missing)}: {source.url}")
    frame = frame[frame["Project"].map(clean_cell) != ""].reset_index(drop=True)
    if len(frame) < source.minimum_rows:
        raise ValueError(
            f"DoED table row count {len(frame)} is below safety floor {source.minimum_rows}: {source.url}"
        )
    return frame


def first_value(row: pd.Series, *columns: str) -> str:
    for column in columns:
        if column in row.index:
            value = clean_cell(row[column])
            if value:
                return value
    return ""


def normalize_row(row: pd.Series, source: SourceSpec, updated_on: str) -> dict[str, Any]:
    project = first_value(row, "Project")
    capacity = parse_number(first_value(row, "Capacity (MW)"))
    river = first_value(row, "River")
    record_number = first_value(row, "Lic No", "Appn No")
    record_date = first_value(row, "Isuue Date", "Issue Date", "Appn Date", "Decision Date")
    source_row_number = first_value(row, "S No")
    identity = "|".join(
        [
            source.page_id,
            source_row_number,
            project,
            str(capacity if capacity is not None else ""),
            record_number,
            source.url,
        ]
    )
    technology = classify_energy_type({"name": project, "river": river})
    return {
        "record_id": hashlib.sha256(identity.encode("utf-8")).hexdigest()[:20],
        "source_row_number": source_row_number,
        "project": project,
        "capacity_mw": capacity if capacity is not None else "",
        "river": river,
        "technology": technology,
        "regulatory_category": source.regulatory_category,
        "record_status": source.record_status,
        "license_status": source.license_status,
        "study_status": source.study_status,
        "delivery_status": source.delivery_status,
        "record_number": record_number,
        "record_date_bs": record_date,
        "validity_date_bs": first_value(row, "Validity"),
        "cod_date_bs": first_value(row, "C O D", "COD"),
        "promoter": first_value(row, "Promoter"),
        "address": first_value(row, "Address"),
        "latitude_1_dms": first_value(row, "Latitiude N", "Latitude N"),
        "latitude_2_dms": first_value(row, "Latitiude N.1", "Latitude N.1"),
        "longitude_1_dms": first_value(row, "Longitude E"),
        "longitude_2_dms": first_value(row, "Longitude E.1"),
        "location_text": first_value(row, "VDC/District"),
        "source_page_id": source.page_id,
        "source_url": source.url,
        "source_updated_on": updated_on,
    }


def fetch_source(source: SourceSpec, timeout: float) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    response = requests.get(
        source.url,
        timeout=timeout,
        headers={"User-Agent": "TransparentGov-DoED-Registry/1.0"},
    )
    response.raise_for_status()
    html = response.text
    updated_on = parse_updated_on(html, source)
    frame = parse_table(html, source)
    rows = [normalize_row(row, source, updated_on) for _, row in frame.iterrows()]
    return rows, {
        "page_id": source.page_id,
        "url": source.url,
        "regulatory_category": source.regulatory_category,
        "updated_on": updated_on,
        "rows": len(rows),
        "sha256": hashlib.sha256(response.content).hexdigest(),
    }


def build_registry(timeout: float = 30.0) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    source_reports: list[dict[str, Any]] = []
    for source in SOURCES:
        source_rows, report = fetch_source(source, timeout)
        rows.extend(source_rows)
        source_reports.append(report)
    ids = [row["record_id"] for row in rows]
    if len(ids) != len(set(ids)):
        raise ValueError("Normalized DoED registry contains duplicate record_id values")
    content_signatures = [
        (
            row["regulatory_category"],
            row["project"],
            row["capacity_mw"],
            row["river"],
            row["record_number"],
        )
        for row in rows
    ]
    duplicate_content_rows = len(content_signatures) - len(set(content_signatures))
    summary = {
        "schema_version": 1,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source_authority": "Nepal Department of Electricity Development",
        "scope": "Regulatory and operating records; generation licences do not prove physical construction.",
        "rows": len(rows),
        "duplicate_content_rows": duplicate_content_rows,
        "technology_counts": dict(sorted(pd.Series([row["technology"] for row in rows]).value_counts().to_dict().items())),
        "category_counts": dict(
            sorted(pd.Series([row["regulatory_category"] for row in rows]).value_counts().to_dict().items())
        ),
        "sources": source_reports,
    }
    return rows, summary


def write_registry(output_dir: Path, rows: list[dict[str, Any]], summary: dict[str, Any]) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    frame = pd.DataFrame(rows, columns=OUTPUT_FIELDS)
    frame.to_csv(output_dir / REGISTRY_NAME, index=False)
    (output_dir / SUMMARY_NAME).write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--timeout", type=float, default=30.0)
    parser.add_argument("--no-write", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    rows, summary = build_registry(timeout=args.timeout)
    if args.no_write:
        print(json.dumps(summary, indent=2, ensure_ascii=False))
    else:
        output_dir = args.output_dir.expanduser().resolve()
        write_registry(output_dir, rows, summary)
        print(f"Wrote {len(rows)} normalized DoED records to {output_dir / REGISTRY_NAME}")
        print(json.dumps(summary["category_counts"], sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
