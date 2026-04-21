#!/usr/bin/env python3

import argparse
import csv
import html
import json
import re
import subprocess
import sys
import time
from pathlib import Path
from urllib.parse import urljoin

import requests


ARCHIVE_URL = "https://td.neasite.dryicesolutions.net/en/category/daily-operational-reports-1"
DETAIL_BASE = "https://td.neasite.dryicesolutions.net"
MONTH_NAMES = {
    1: "Baishakh",
    2: "Jestha",
    3: "Ashadh",
    4: "Shrawan",
    5: "Bhadra",
    6: "Ashwin",
    7: "Kartik",
    8: "Mangsir",
    9: "Poush",
    10: "Magh",
    11: "Falgun",
    12: "Chaitra",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build NEA daily trade manifest and parsed daily/monthly series."
    )
    parser.add_argument(
        "--output-dir",
        default="/Users/hi/projects/nepalEnergy/data/processed/lead1_trade",
        help="Directory for manifest, parsed CSVs, and summary JSON.",
    )
    parser.add_argument(
        "--pdf-cache-dir",
        default="/Users/hi/projects/nepalEnergy/data/raw/lead1_sources/nea_daily_reports",
        help="Cache directory for downloaded daily report PDFs.",
    )
    parser.add_argument(
        "--max-pages",
        type=int,
        default=None,
        help="Optional cap on archive pages to crawl.",
    )
    parser.add_argument(
        "--max-reports",
        type=int,
        default=None,
        help="Optional cap on reports to download and parse after sorting by detail URL.",
    )
    parser.add_argument(
        "--sleep-seconds",
        type=float,
        default=0.2,
        help="Delay between HTTP requests.",
    )
    parser.add_argument(
        "--refresh",
        action="store_true",
        help="Re-download PDFs even when they already exist in cache.",
    )
    return parser.parse_args()


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def session_with_headers() -> requests.Session:
    session = requests.Session()
    session.headers.update(
        {
            "User-Agent": (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0 Safari/537.36"
            )
        }
    )
    return session


def fetch_text(session: requests.Session, url: str, sleep_seconds: float) -> str:
    response = session.get(url, timeout=30)
    response.raise_for_status()
    time.sleep(sleep_seconds)
    return response.text


def fetch_binary(session: requests.Session, url: str, dest: Path, sleep_seconds: float) -> None:
    response = session.get(url, timeout=60)
    response.raise_for_status()
    dest.write_bytes(response.content)
    time.sleep(sleep_seconds)


def extract_max_page(first_page_html: str) -> int:
    pages = [int(m.group(1)) for m in re.finditer(r"page=(\d+)", first_page_html)]
    return max(pages) if pages else 1


def extract_detail_urls(page_html: str) -> list[str]:
    detail_urls = []
    seen = set()
    for match in re.finditer(r'href="([^"]+/detail/[^"]+)"', page_html):
        href = html.unescape(match.group(1))
        if "/detail/nepal-daily-operational-report-" not in href:
            continue
        if href not in seen:
            seen.add(href)
            detail_urls.append(href)
    return detail_urls


def extract_detail_record(detail_html: str, detail_url: str) -> dict:
    title_match = re.search(r"<h5[^>]*>\s*([^<]+)\s*</h5>", detail_html)
    published_match = re.search(r"([A-Za-z]+\s+\d{1,2},\s+\d{4})", detail_html)
    pdf_candidates = []
    seen = set()
    for pattern in [
        r'(?:href|src)="([^"]+/uploads/shares/[^"]+\.pdf)"',
        r"(?:href|src)='([^']+/uploads/shares/[^']+\.pdf)'",
        r'(?:href|src)="(/uploads/shares/[^"]+\.pdf)"',
        r"(?:href|src)='(/uploads/shares/[^']+\.pdf)'",
        r"(/uploads/shares/[^\"'\s>]+\.pdf)",
    ]:
        for match in re.finditer(pattern, detail_html, re.IGNORECASE):
            candidate = html.unescape(match.group(1).strip())
            if candidate not in seen:
                seen.add(candidate)
                pdf_candidates.append(candidate)

    def pdf_priority(candidate: str) -> tuple[int, int, str]:
        candidate_lower = candidate.lower()
        ndor_rank = 0 if "ndor" in candidate_lower else 1
        if "/daily_op_reports/" in candidate_lower:
            path_rank = 0
        elif "/press_release/" in candidate_lower:
            path_rank = 1
        else:
            path_rank = 2
        return (ndor_rank, path_rank, candidate_lower)

    pdf_url = urljoin(DETAIL_BASE, min(pdf_candidates, key=pdf_priority)) if pdf_candidates else ""
    return {
        "detail_url": detail_url,
        "title": html.unescape(title_match.group(1).strip()) if title_match else "",
        "published_gregorian": published_match.group(1).strip() if published_match else "",
        "pdf_url": pdf_url,
    }


def detail_revision(detail_url: str) -> int:
    match = re.search(r"-r(\d+)$", detail_url, re.IGNORECASE)
    return int(match.group(1)) if match else 0


def deduplicate_rows(rows: list[dict]) -> list[dict]:
    best_by_bs_date: dict[str, dict] = {}
    for row in rows:
        key = row["bs_date"]
        current = best_by_bs_date.get(key)
        if current is None:
            best_by_bs_date[key] = row
            continue
        candidate_key = (
            row["detail_revision"],
            row["crawl_index"] * -1,
        )
        current_key = (
            current["detail_revision"],
            current["crawl_index"] * -1,
        )
        if candidate_key > current_key:
            best_by_bs_date[key] = row
    return sorted(best_by_bs_date.values(), key=lambda item: (item["bs_year"], item["bs_month"], item["bs_day"]))


def pdf_filename_from_url(pdf_url: str) -> str:
    return pdf_url.rsplit("/", 1)[-1]


def run_pdftotext(pdf_path: Path) -> str:
    result = subprocess.run(
        ["pdftotext", "-layout", str(pdf_path), "-"],
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout


def parse_bs_date_components(bs_date: str) -> tuple[int, int, int]:
    year, month, day = [int(part) for part in bs_date.split("/")]
    return year, month, day


def bs_fiscal_year_label(bs_year: int, bs_month: int) -> str:
    if bs_month >= 4:
        return f"{bs_year}_{bs_year + 1}"
    return f"{bs_year - 1}_{bs_year}"


def fiscal_month_order(bs_month: int) -> int:
    return bs_month - 3 if bs_month >= 4 else bs_month + 9


def extract_numeric_line(block: str, expected_fields: int, starts_with_time: bool = False) -> list[str]:
    lines = [line.strip() for line in block.splitlines() if line.strip()]
    for line in lines:
        if starts_with_time:
            if not re.match(r"^\d{1,2}:\d{2}\s+", line):
                continue
            parts = re.split(r"\s+", line)
            if len(parts) >= expected_fields:
                return parts[:expected_fields]
        else:
            if not re.match(r"^\d", line):
                continue
            parts = re.split(r"\s+", line)
            if len(parts) >= expected_fields:
                return parts[:expected_fields]
    raise ValueError("Could not find numeric table row in PDF text block")


def parse_daily_pdf_text(text: str) -> dict:
    date_match = re.search(
        r"For Date:\s*(\d{4}/\d{1,2}/\d{1,2})\s*\(\s*(\d{4}/\d{1,2}/\d{1,2})\s*\)",
        text,
    )
    if not date_match:
        raise ValueError("Could not parse report date line from PDF")

    bs_date = date_match.group(1)
    gregorian_date = date_match.group(2)

    energy_block_match = re.search(
        r"Daily Energy Values([\s\S]*?)Peak Time Generation,\s*Demand and Cross Border Exchange",
        text,
        re.DOTALL,
    )
    if not energy_block_match:
        raise ValueError("Could not isolate daily energy table block from PDF")
    energy_row = extract_numeric_line(energy_block_match.group(1), expected_fields=11)

    peak_block_match = re.search(
        r"Peak Time Generation,\s*Demand and Cross Border Exchange([\s\S]+)",
        text,
        re.DOTALL,
    )
    if not peak_block_match:
        raise ValueError("Could not isolate peak exchange table block from PDF")
    peak_row = extract_numeric_line(peak_block_match.group(1), expected_fields=10, starts_with_time=True)

    bs_year, bs_month, bs_day = parse_bs_date_components(bs_date)
    return {
        "bs_date": bs_date,
        "bs_year": bs_year,
        "bs_month": bs_month,
        "bs_day": bs_day,
        "bs_month_name": MONTH_NAMES[bs_month],
        "gregorian_date": gregorian_date,
        "fiscal_year": bs_fiscal_year_label(bs_year, bs_month),
        "fiscal_month_order": fiscal_month_order(bs_month),
        "nea_subsidiary_mwh": int(energy_row[0]),
        "nea_generation_mwh": int(energy_row[1]),
        "ipp_mwh": int(energy_row[2]),
        "import_mwh": int(energy_row[3]),
        "total_energy_available_mwh": int(energy_row[4]),
        "export_mwh": int(energy_row[5]),
        "inps_demand_met_mwh": int(energy_row[6]),
        "energy_interruption_mwh": int(energy_row[7]),
        "generation_deficit_mwh": int(energy_row[8]),
        "energy_requirement_mwh": int(energy_row[9]),
        "net_exchange_india_mwh": int(energy_row[10]),
        "peak_time": peak_row[0],
        "generation_mw": int(peak_row[1]),
        "peak_import_mw": int(peak_row[2]),
        "peak_availability_mw": int(peak_row[3]),
        "peak_export_mw": int(peak_row[4]),
        "demand_met_at_peak_mw": int(peak_row[5]),
        "peak_interruption_mw": int(peak_row[6]),
        "peak_deficit_mw": int(peak_row[7]),
        "peak_requirement_mw": int(peak_row[8]),
        "net_exchange_india_mw": int(peak_row[9]),
    }


def write_csv(path: Path, rows: list[dict], fieldnames: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def aggregate_monthly(rows: list[dict]) -> list[dict]:
    grouped: dict[tuple[str, int], dict] = {}
    for row in rows:
        key = (row["fiscal_year"], row["bs_month"])
        group = grouped.setdefault(
            key,
            {
                "fiscal_year": row["fiscal_year"],
                "bs_month": row["bs_month"],
                "bs_month_name": row["bs_month_name"],
                "fiscal_month_order": row["fiscal_month_order"],
                "days_count": 0,
                "import_mwh": 0,
                "export_mwh": 0,
                "net_exchange_india_mwh": 0,
                "energy_interruption_mwh": 0,
                "generation_deficit_mwh": 0,
                "energy_requirement_mwh": 0,
                "max_daily_peak_import_mw": 0,
                "max_daily_peak_export_mw": 0,
                "max_daily_peak_requirement_mw": 0,
            },
        )
        group["days_count"] += 1
        group["import_mwh"] += row["import_mwh"]
        group["export_mwh"] += row["export_mwh"]
        group["net_exchange_india_mwh"] += row["net_exchange_india_mwh"]
        group["energy_interruption_mwh"] += row["energy_interruption_mwh"]
        group["generation_deficit_mwh"] += row["generation_deficit_mwh"]
        group["energy_requirement_mwh"] += row["energy_requirement_mwh"]
        group["max_daily_peak_import_mw"] = max(group["max_daily_peak_import_mw"], row["peak_import_mw"])
        group["max_daily_peak_export_mw"] = max(group["max_daily_peak_export_mw"], row["peak_export_mw"])
        group["max_daily_peak_requirement_mw"] = max(
            group["max_daily_peak_requirement_mw"], row["peak_requirement_mw"]
        )
    return sorted(grouped.values(), key=lambda item: (item["fiscal_year"], item["fiscal_month_order"]))


def main() -> int:
    args = parse_args()
    output_dir = Path(args.output_dir)
    pdf_cache_dir = Path(args.pdf_cache_dir)
    ensure_dir(output_dir)
    ensure_dir(pdf_cache_dir)

    session = session_with_headers()

    first_page_html = fetch_text(session, ARCHIVE_URL, args.sleep_seconds)
    max_page = extract_max_page(first_page_html)
    if args.max_pages:
        max_page = min(max_page, args.max_pages)

    detail_urls: list[str] = []
    seen_urls = set()
    for page_num in range(1, max_page + 1):
        page_url = ARCHIVE_URL if page_num == 1 else f"{ARCHIVE_URL}?page={page_num}"
        page_html = first_page_html if page_num == 1 else fetch_text(session, page_url, args.sleep_seconds)
        for detail_url in extract_detail_urls(page_html):
            if detail_url not in seen_urls:
                seen_urls.add(detail_url)
                detail_urls.append(detail_url)

    manifest_rows = []
    for detail_url in detail_urls:
        detail_html = fetch_text(session, detail_url, args.sleep_seconds)
        record = extract_detail_record(detail_html, detail_url)
        manifest_rows.append(record)

    manifest_fieldnames = ["detail_url", "title", "published_gregorian", "pdf_url"]
    write_csv(output_dir / "nea_daily_report_manifest.csv", manifest_rows, manifest_fieldnames)

    parsed_rows = []
    parse_failures = []
    manifest_iter = manifest_rows[: args.max_reports] if args.max_reports else manifest_rows
    for record in manifest_iter:
        if not record["pdf_url"]:
            parse_failures.append(
                {"detail_url": record["detail_url"], "reason": "missing_pdf_url"}
            )
            continue

        pdf_name = pdf_filename_from_url(record["pdf_url"])
        pdf_path = pdf_cache_dir / pdf_name
        try:
            if args.refresh or not pdf_path.exists():
                fetch_binary(session, record["pdf_url"], pdf_path, args.sleep_seconds)
            parsed = parse_daily_pdf_text(run_pdftotext(pdf_path))
            parsed.update(
                {
                    "crawl_index": len(parsed_rows) + len(parse_failures),
                    "detail_revision": detail_revision(record["detail_url"]),
                    "detail_url": record["detail_url"],
                    "title": record["title"],
                    "published_gregorian": record["published_gregorian"],
                    "pdf_url": record["pdf_url"],
                    "pdf_filename": pdf_name,
                }
            )
            parsed_rows.append(parsed)
        except Exception as exc:  # noqa: BLE001
            parse_failures.append(
                {
                    "detail_url": record["detail_url"],
                    "pdf_url": record["pdf_url"],
                    "reason": str(exc),
                }
            )

    parsed_rows.sort(key=lambda item: (item["bs_year"], item["bs_month"], item["bs_day"], item["detail_revision"]))
    parsed_fieldnames = [
        "bs_date",
        "gregorian_date",
        "fiscal_year",
        "bs_year",
        "bs_month",
        "bs_month_name",
        "bs_day",
        "fiscal_month_order",
        "nea_subsidiary_mwh",
        "nea_generation_mwh",
        "ipp_mwh",
        "import_mwh",
        "total_energy_available_mwh",
        "export_mwh",
        "inps_demand_met_mwh",
        "energy_interruption_mwh",
        "generation_deficit_mwh",
        "energy_requirement_mwh",
        "net_exchange_india_mwh",
        "peak_time",
        "generation_mw",
        "peak_import_mw",
        "peak_availability_mw",
        "peak_export_mw",
        "demand_met_at_peak_mw",
        "peak_interruption_mw",
        "peak_deficit_mw",
        "peak_requirement_mw",
        "net_exchange_india_mw",
        "crawl_index",
        "detail_revision",
        "detail_url",
        "title",
        "published_gregorian",
        "pdf_url",
        "pdf_filename",
    ]
    write_csv(output_dir / "nea_daily_trade_parsed_raw.csv", parsed_rows, parsed_fieldnames)

    deduped_rows = deduplicate_rows(parsed_rows)
    write_csv(output_dir / "nea_daily_trade_parsed.csv", deduped_rows, parsed_fieldnames)

    monthly_rows = aggregate_monthly(deduped_rows)
    monthly_fieldnames = [
        "fiscal_year",
        "bs_month",
        "bs_month_name",
        "fiscal_month_order",
        "days_count",
        "import_mwh",
        "export_mwh",
        "net_exchange_india_mwh",
        "energy_interruption_mwh",
        "generation_deficit_mwh",
        "energy_requirement_mwh",
        "max_daily_peak_import_mw",
        "max_daily_peak_export_mw",
        "max_daily_peak_requirement_mw",
    ]
    write_csv(output_dir / "nea_daily_trade_monthly_aggregated.csv", monthly_rows, monthly_fieldnames)

    summary = {
        "archive_url": ARCHIVE_URL,
        "page_count_crawled": max_page,
        "detail_count": len(detail_urls),
        "manifest_count": len(manifest_rows),
        "parsed_raw_count": len(parsed_rows),
        "parsed_count": len(deduped_rows),
        "duplicate_date_count": len(parsed_rows) - len(deduped_rows),
        "failure_count": len(parse_failures),
        "earliest_bs_date": deduped_rows[0]["bs_date"] if deduped_rows else None,
        "latest_bs_date": deduped_rows[-1]["bs_date"] if deduped_rows else None,
        "fiscal_years_present": sorted({row["fiscal_year"] for row in deduped_rows}),
        "failures": parse_failures[:50],
    }
    (output_dir / "nea_daily_trade_summary.json").write_text(
        json.dumps(summary, indent=2),
        encoding="utf-8",
    )

    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
