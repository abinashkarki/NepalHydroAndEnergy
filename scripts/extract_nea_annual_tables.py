#!/usr/bin/env python3
"""Extract and verify NEA multi-year system tables into a fiscal-year time series.

Reads the statistics appendices of the NEA "A Year in Review" annual reports
(FY 2025/26 and FY 2024/25) with ``pdftotext -layout``, parses the ten-year
summary rows (energy availability, peaks, sales, consumers, system loss,
statement of profit or loss) plus the installed-capacity summary and grid
coverage sentence, and writes ``data/nea_system_annual_timeseries.csv``.

Rules:
- Values are copied from the report tables; nothing is interpolated.
  Cells a table does not report stay blank.
- The latest report wins for overlapping years (FY 2016/17-FY 2024/25 come
  from the FY 2025/26 report); the FY 2024/25 report supplies FY 2015/16 and
  the FY 2024/25 installed-capacity / grid-coverage snapshot.
- Overlapping years are cross-checked between reports and differences are
  printed (financial restatements are expected).

Usage (from the repo root of a checkout that has the gitignored PDFs):
    python scripts/extract_nea_annual_tables.py            # write CSV
    python scripts/extract_nea_annual_tables.py --check    # compare with committed CSV
    python scripts/extract_nea_annual_tables.py --repo-root /path/to/checkout
"""
from __future__ import annotations

import argparse
import csv
import io
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUTPUT = Path("data/nea_system_annual_timeseries.csv")
MONTHLY_BALANCE = Path("data/processed/tables/nea_energy_balance_monthly_fy2025_26.csv")
VERIFIED_ON = "2026-11-24"

REPORTS = {
    "fy2025-26": {
        "slug": "nea-annual-report-fy2025-26",
        "pdf": Path("data/raw/nea_annual_reports/nea_annual_report_2025_26.pdf"),
        # Column labels in the statistics appendix ("2017" = FY 2016/17 ... "2026*" = FY 2025/26).
        "years": list(range(2017, 2027)),
        "pages": {
            "availability": 169,
            "sales": 170,
            "consumers": 171,
            "loss": 173,
            "pnl": 156,
            "capacity": 185,
            "coverage": 13,
        },
    },
    "fy2024-25": {
        "slug": "nea-annual-report-fy2024-25",
        "pdf": Path("data/raw/projects_storage/nea_annual_report_2024_2025.pdf"),
        "years": list(range(2016, 2026)),
        "pages": {
            "availability": 138,
            "sales": 139,
            "consumers": 140,
            "loss": 142,
            "pnl": 126,
            "capacity": 154,
            "coverage": 12,
        },
    },
}

# (field, page key, row label regex, right_aligned, reversed_years)
TABLE_ROWS = [
    ("energy_nea_gwh", "availability", r"NEA Own Generation", False, False),
    ("energy_nea_subsidiary_gwh", "availability", r"Power Purchase - NEA Sub", False, False),
    ("energy_ipp_gwh", "availability", r"Power Purchase from IPPs", False, False),
    ("energy_import_gwh", "availability", r"Power Purchase from India", False, False),
    ("energy_total_available_gwh", "availability", r"Total Availability \(MU\)", False, False),
    ("peak_demand_national_mw", "availability", r"National Peak Demand \(MW\)", False, False),
    ("peak_demand_system_mw", "availability", r"System Peak Demand Including Export \(MW\)", True, False),
    ("energy_sales_gwh", "sales", r"Total Internal Sales \(MU\)", False, False),
    ("energy_export_gwh", "sales", r"Export Sales \(MU\)", False, False),
    ("consumers_total", "consumers", r"Total Consumers", False, False),
    ("system_loss_pct", "loss", r"System Loss %", False, False),
    ("nea_revenue_npr_m", "pnl", r"Sales Revenue", False, True),
    ("nea_net_profit_npr_m", "pnl", r"Profit [Bb]efore [Ii]ncome [Tt]ax", False, True),
]

CAPACITY_LABELS = {
    "hydro_nea": r"Total\s*Hydro\s*\(\s*NEA\s*\)",
    "hydro_sub": r"Total\s*Hydro\s*\(\s*NEA\s*Subsidiary\s*\)",
    "hydro_ipp": r"Total\s*Hydro\s*\(\s*IPPs\s*\)",
    "thermal_nea": r"Total\s*Thermal\s*\(\s*NEA\s*\)",
    "bagasse_ipp": r"Total\s*Bagasse\s*\(\s*IPPs\s*\)",
    "solar_total": r"Total\s*Solar\s*\(\s*Nepal\s*\)",
    "solar_nea": r"Total\s*Solar\s*\(\s*NEA\s*\)",
    "solar_ipp": r"Total\s*Solar\s*\(\s*IPPs\s*\)",
    "total": r"Total\s*Installed\s*Capacity",
}

COLUMNS = [
    "fiscal_year_bs",
    "fiscal_year_ad",
    "installed_capacity_total_mw",
    "installed_nea_mw",
    "installed_nea_subsidiary_mw",
    "installed_ipp_mw",
    "installed_solar_mw",
    "peak_demand_national_mw",
    "peak_demand_system_mw",
    "energy_nea_gwh",
    "energy_nea_subsidiary_gwh",
    "energy_ipp_gwh",
    "energy_import_gwh",
    "energy_export_gwh",
    "energy_total_available_gwh",
    "energy_sales_gwh",
    "system_loss_pct",
    "consumers_total",
    "electrification_pct",
    "nea_revenue_npr_m",
    "nea_net_profit_npr_m",
    "source_slug",
    "source_locator",
    "verified_on",
]

NUM = re.compile(r"\(?-?[\d][\d,]*\.?\d*\)?%?|-")


def pdftotext_page(pdf: Path, page: int) -> str:
    exe = shutil.which("pdftotext") or "/opt/homebrew/bin/pdftotext"
    out = subprocess.run(
        [exe, "-f", str(page), "-l", str(page), "-layout", str(pdf), "-"],
        check=True,
        capture_output=True,
        text=True,
    )
    return out.stdout


def to_number(token: str) -> float | None:
    token = token.strip()
    if token in {"-", ""}:
        return None
    neg = token.startswith("(") and token.endswith(")")
    token = token.strip("()%").replace(",", "")
    value = float(token)
    return -value if neg else value


def parse_row(text: str, label: str, n: int, right_aligned: bool) -> list[float | None]:
    """Return n values for a table row; pad on the left for right-aligned short rows."""
    pattern = re.compile(r"^[ \t]*" + label + r"[ \t]+([-\d(][\d,.()% \t-]*)$", re.M)
    match = pattern.search(text)
    if not match:
        raise ValueError(f"row not found: {label}")
    tokens = match.group(1).split()
    # pdftotext occasionally splits a number after its first digit ("8 7,155", "9 ,067").
    while len(tokens) > n:
        for i, tok in enumerate(tokens[:-1]):
            nxt = tokens[i + 1]
            if re.fullmatch(r"\(?\d", tok) and re.match(r"[\d,]", nxt):
                tokens[i : i + 2] = [tok + nxt]
                break
        else:
            raise ValueError(f"cannot reconcile {len(tokens)} tokens for {label}: {tokens}")
    values = [to_number(t) for t in tokens]
    if len(values) < n:
        if not right_aligned:
            raise ValueError(f"short row for {label}: {tokens}")
        values = [None] * (n - len(values)) + values
    return values


def parse_capacity(text: str) -> dict[str, float]:
    flat = " ".join(text.split())
    result = {}
    for key, label in CAPACITY_LABELS.items():
        match = re.search(label + r"\s+([\d][\d,]{2,})", flat)
        if not match:
            raise ValueError(f"capacity label not found: {key}")
        result[key] = float(match.group(1).replace(",", "")) / 1000.0  # kW -> MW
    return result


def parse_coverage(text: str) -> float:
    flat = " ".join(text.split())
    match = re.search(r"[Nn]ational grid coverage.{0,80}?reached\s+([\d.]+)\s*(?:%|percent)", flat)
    if not match:
        raise ValueError("grid coverage sentence not found")
    return float(match.group(1))


def year_label(ad_end: int) -> tuple[str, str]:
    bs_start = ad_end + 56
    return f"{bs_start}/{str(bs_start + 1)[-2:]}", f"{ad_end - 1}/{str(ad_end)[-2:]}"


def extract_report(repo: Path, key: str) -> dict:
    cfg = REPORTS[key]
    pdf = repo / cfg["pdf"]
    if not pdf.exists():
        raise SystemExit(f"missing PDF: {pdf} (PDFs are gitignored; pass --repo-root)")
    pages = {name: pdftotext_page(pdf, num) for name, num in cfg["pages"].items()}
    years = cfg["years"]
    table: dict[int, dict[str, float | None]] = {y: {} for y in years}
    for field, page_key, label, right_aligned, reverse in TABLE_ROWS:
        values = parse_row(pages[page_key], label, len(years), right_aligned)
        if reverse:
            values = list(reversed(values))
        for year, value in zip(years, values):
            table[year][field] = value
    capacity = parse_capacity(pages["capacity"])
    nea = capacity["hydro_nea"] + capacity["thermal_nea"] + capacity["solar_nea"]
    ipp = capacity["hydro_ipp"] + capacity["bagasse_ipp"] + capacity["solar_ipp"]
    total_check = nea + capacity["hydro_sub"] + ipp
    if abs(total_check - capacity["total"]) > 0.01:
        raise SystemExit(f"{key}: capacity components {total_check} != total {capacity['total']}")
    snapshot_year = years[-1]
    table[snapshot_year].update(
        {
            "installed_capacity_total_mw": capacity["total"],
            "installed_nea_mw": nea,
            "installed_nea_subsidiary_mw": capacity["hydro_sub"],
            "installed_ipp_mw": ipp,
            "installed_solar_mw": capacity["solar_total"],
            "electrification_pct": parse_coverage(pages["coverage"]),
        }
    )
    return {"cfg": cfg, "table": table}


def fmt(value: float | None, field: str) -> str:
    if value is None:
        return ""
    if field.endswith("_pct"):
        return f"{value:.2f}" if field == "system_loss_pct" else f"{value:g}"
    if field.startswith("installed_"):
        return f"{value:.3f}".rstrip("0").rstrip(".")
    return str(int(round(value)))


def locator(cfg: dict, year: int, snapshot: bool) -> str:
    p = cfg["pages"]
    col = f"{year}*" if year == cfg["years"][-1] else str(year)
    parts = [
        f"statistics appendix column '{col}': energy & peaks PDF p.{p['availability']}",
        f"sales p.{p['sales']}",
        f"consumers p.{p['consumers']}",
        f"system loss p.{p['loss']}",
        f"statement of profit or loss p.{p['pnl']}",
    ]
    if snapshot:
        parts.append(f"installed capacity summary p.{p['capacity']}")
        parts.append(f"grid coverage p.{p['coverage']}")
    return "; ".join(parts)


def build_rows(repo: Path) -> tuple[list[dict], list[str]]:
    latest = extract_report(repo, "fy2025-26")
    prior = extract_report(repo, "fy2024-25")
    notes: list[str] = []
    # Cross-check overlapping years.
    for year in sorted(set(latest["table"]) & set(prior["table"])):
        for field, *_ in TABLE_ROWS:
            a = latest["table"][year].get(field)
            b = prior["table"][year].get(field)
            if a is not None and b is not None and abs(a - b) > 1e-9:
                notes.append(f"FY ending {year} {field}: FY2025/26 report {a:g} vs FY2024/25 report {b:g}")
    rows = []
    years = sorted(set(latest["table"]) | set(prior["table"]))
    for year in years:
        bs, ad = year_label(year)
        values: dict[str, float | None] = {}
        slugs: list[str] = []
        locs: list[str] = []
        if year in latest["table"]:
            values.update(latest["table"][year])
            slugs.append(latest["cfg"]["slug"])
            locs.append(f"{latest['cfg']['slug']}: " + locator(latest["cfg"], year, year == latest["cfg"]["years"][-1]))
        if year in prior["table"]:
            prior_vals = prior["table"][year]
            used = False
            for field, value in prior_vals.items():
                if values.get(field) is None and value is not None:
                    values[field] = value
                    used = True
            if used:
                slugs.append(prior["cfg"]["slug"])
                snapshot = year == prior["cfg"]["years"][-1]
                if year in latest["table"]:
                    p = prior["cfg"]["pages"]
                    locs.append(
                        f"{prior['cfg']['slug']}: installed capacity summary PDF p.{p['capacity']}; grid coverage p.{p['coverage']}"
                    )
                else:
                    locs.append(f"{prior['cfg']['slug']}: " + locator(prior["cfg"], year, snapshot))
        row = {"fiscal_year_bs": bs, "fiscal_year_ad": ad}
        for col in COLUMNS[2:-3]:
            row[col] = fmt(values.get(col), col)
        row["source_slug"] = ";".join(slugs)
        row["source_locator"] = " | ".join(locs)
        row["verified_on"] = VERIFIED_ON
        rows.append(row)
    return rows, notes


def render(rows: list[dict]) -> str:
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=COLUMNS, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return buf.getvalue()


def monthly_crosscheck(repo: Path, rows: list[dict]) -> list[str]:
    path = repo / MONTHLY_BALANCE
    if not path.exists():
        return [f"monthly balance not found: {MONTHLY_BALANCE}"]
    totals = {}
    with path.open(encoding="utf-8") as handle:
        for rec in csv.DictReader(handle):
            totals[rec["metric"]] = float(rec["Total"])
    latest = next(r for r in rows if r["fiscal_year_ad"] == "2025/26")
    nea_monthly = totals["NEA_ROR_PROR"] + totals["STORAGE"] + totals["SOLAR"] + totals["THERMAL"]
    pairs = [
        ("NEA own generation", nea_monthly, latest["energy_nea_gwh"]),
        ("NEA subsidiaries", totals["NEA_SUBSIDIARY"], latest["energy_nea_subsidiary_gwh"]),
        ("IPPs", totals["IPP"], latest["energy_ipp_gwh"]),
        ("Import", totals["IMPORT"], latest["energy_import_gwh"]),
        ("Export", totals["EXPORT"], latest["energy_export_gwh"]),
        ("System energy demand vs total available", totals["MONTHLY_SYSTEM_ENERGY_DEMAND"], latest["energy_total_available_gwh"]),
    ]
    return [f"{name}: monthly balance {m:g} GWh vs annual table {a} GWh (diff {m - float(a):+g})" for name, m, a in pairs]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--repo-root", type=Path, default=ROOT, help="checkout containing data/raw PDFs")
    parser.add_argument("--check", action="store_true", help="fail if committed CSV differs")
    args = parser.parse_args()
    repo = args.repo_root.resolve()
    rows, notes = build_rows(repo)
    text = render(rows)
    out = ROOT / OUTPUT
    print(f"{len(rows)} fiscal years: {rows[0]['fiscal_year_ad']} .. {rows[-1]['fiscal_year_ad']}")
    for note in notes:
        print("overlap difference:", note)
    for note in monthly_crosscheck(ROOT, rows):
        print("monthly cross-check:", note)
    if args.check:
        current = out.read_text(encoding="utf-8") if out.exists() else ""
        if current != text:
            print(f"FAIL: {OUTPUT} is stale; rerun without --check", file=sys.stderr)
            return 1
        print(f"OK: {OUTPUT} matches extraction")
        return 0
    out.write_text(text, encoding="utf-8")
    print(f"wrote {OUTPUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
