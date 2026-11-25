#!/usr/bin/env python3
"""Extract plant-level annual generation and grid-infrastructure summary tables from NEA annual reports.

Outputs:
- data/plant_annual_generation.csv: annual generation of each NEA-owned plant
  (Generation Directorate monthly-generation tables) and of NEA-subsidiary plants
  where the report states it (Upper Tamakoshi), for FY 2024/25 and FY 2025/26.
- data/nea_grid_infrastructure_summary.csv: transmission circuit-km by voltage
  class and grid-substation transformer MVA by voltage ratio, FY 2024/25 and
  FY 2025/26, plus the ten-year comparison series and the FY 2076/77 baseline.

Table values are parsed from ``pdftotext -layout`` page text. Values the report
states only in narrative or plant fact-sheets are kept as constants in this file,
and each one is checked against the text of its cited page. A value that cannot
be found there aborts the run. The script then reconciles plant sums against
the NEA aggregate supply figures in data/nea_system_annual_timeseries.csv and
prints the residuals.

Usage (repo root of a checkout that has the gitignored PDFs):
    python scripts/extract_nea_plant_and_grid_tables.py [--check] [--repo-root PATH]
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
PLANT_OUT = Path("data/plant_annual_generation.csv")
GRID_OUT = Path("data/nea_grid_infrastructure_summary.csv")
TIMESERIES = Path("data/nea_system_annual_timeseries.csv")
VERIFIED_ON = "2026-11-24"
HOURS = 8760  # implied PLF uses a 365-day year

PDFS = {
    "nea-annual-report-fy2025-26": Path("data/raw/nea_annual_reports/nea_annual_report_2025_26.pdf"),
    "nea-annual-report-fy2024-25": Path("data/raw/projects_storage/nea_annual_report_2024_2025.pdf"),
    "nea-transmission-annual-book-2077": Path("data/raw/corridor_tracing/nea/nea_transmission_annual_book_2077.pdf"),
}
R26 = "nea-annual-report-fy2025-26"
R25 = "nea-annual-report-fy2024-25"
BOOK = "nea-transmission-annual-book-2077"

# fiscal_year_ad -> (report slug, monthly-generation page, capacity-list page)
GEN_YEARS = {
    "2025/26": (R26, 186, 185),
    "2024/25": (R25, 155, 154),
}

# NEA-owned plants:
# (plant_name, generation-table row regex, capacity-list regex, project_slug, design GWh, design page)
# Design generation comes from the FY 2025/26 Generation Directorate plant fact-sheets.
NEA_PLANTS = [
    ("Kaligandaki A", r"Kaligandaki\s*.A.", r"Kaligandaki A", "kali-gandaki-a", "842", 25),
    ("Middle Marsyangdi", r"Mid-?Marsyangdi", r"Middle Marsyandi", "madhya-marsyangdi", "398", 25),
    ("Marsyangdi", r"Marsyandi", r"(?<!Middle )Marsyandi", "marsyangdi", "462.5", 26),
    ("Upper Trishuli 3A", r"Upper Trishuli 3A", r"Upper Trishuli 3A(?: HEP)?", "upper-trishuli-3a", "489.76", 26),
    ("Chameliya", r"Chameliya", r"Chameliya", "chameliya-hydropower", "184.2", 28),
    ("Trishuli", r"Trishuli", r"(?<!Upper )Trishuli(?! 3)", "trishuli", "163", 28),
    ("Devighat", r"Devighat", r"Devighat", "", "114", 29),
    ("Gandak", r"Gandak", r"Gandak", "", "106.38", 29),
    ("Modi Khola", r"Modi", r"Modi Khola", "", "91", 30),
    ("Sunkoshi", r"Sunkoshi", r"Sunkoshi", "", "70", 31),
    ("Puwa Khola", r"Puwa", r"Puwa Khola", "", "48", 31),
    ("Chatara", r"Chatara", r"Chatara", "", "6", 32),
    ("Panauti", r"Panauti", r"Panauti", "", "6.97", 32),
    ("Seti (Pokhara)", r"Seti", r"Seti \(Pokhara\)", "", "9.8", 33),
    ("Fewa", r"Fewa", r"Fewa", "", "6.5", 33),
    ("Sundarijal", r"Sundarijal", r"Sundarijal", "", "7.18", 34),
    ("Kulekhani I", r"Kulekhani I(?!I)", r"Kulekhani I(?!I)", "kulekhani-i", "211", 27),
    ("Kulekhani II", r"Kulekhani II(?!I)", r"Kulekhani II(?!I)", "kulekhani-ii", "104.6", 27),
    ("Kulekhani III", r"Kulekhani III", r"Kulekhani III(?: HEP)?", "kulekhani-iii", "40.85", 30),
    ("Duhabi Multifuel", r"Multifuel", r"Duhabi Multifuel", "", "", None),
    ("Hetauda Diesel", r"Hetauda Diesel", r"Hetauda Diesel", "", "", None),
]
THERMAL = {"Duhabi Multifuel", "Hetauda Diesel"}

# Subsidiary plant generation stated in the Business Development Directorate narrative.
# (plant, slug, fiscal_year_ad, GWh text, slug, page, capacity kW text, capacity page, design text, design page, note)
SUBSIDIARY_ROWS = [
    ("Upper Tamakoshi", "upper-tamakoshi", "2025/26", "2,388.02", R26, 111, "456000", 188, "2,281", 110,
     "Energy generated and delivered to NEA in FY 2082/83 (Business Development Directorate narrative)"),
    ("Upper Tamakoshi", "upper-tamakoshi", "2024/25", "1,529.07", R25, 92, "456000", 157, "", None,
     "FY 2024/25 report states 1,529.07 GWh generated; the FY 2025/26 report (PDF p.111) gives 1,527.77 GWh delivered for FY 2081/82"),
]

PLANT_COLUMNS = [
    "plant_name", "project_slug", "ownership_class", "installed_capacity_mw", "fiscal_year_ad",
    "actual_generation_gwh", "contracted_or_design_gwh", "implied_plf_pct", "source_slug",
    "source_locator", "verified_on", "notes",
]
GRID_COLUMNS = [
    "metric", "voltage_class", "fiscal_year_bs", "fiscal_year_ad", "value", "unit", "count",
    "source_slug", "source_locator", "verified_on", "notes",
]

_cache: dict[tuple[str, int], str] = {}


def page_text(repo: Path, slug: str, page: int) -> str:
    key = (slug, page)
    if key not in _cache:
        pdf = repo / PDFS[slug]
        if not pdf.exists():
            raise SystemExit(f"missing PDF: {pdf} (PDFs are gitignored; pass --repo-root)")
        exe = shutil.which("pdftotext") or "/opt/homebrew/bin/pdftotext"
        out = subprocess.run([exe, "-f", str(page), "-l", str(page), "-layout", str(pdf), "-"],
                             check=True, capture_output=True, text=True)
        _cache[key] = out.stdout
    return _cache[key]


def flat(text: str) -> str:
    return " ".join(text.split())


def require(repo: Path, slug: str, page: int, needle: str) -> None:
    if needle not in flat(page_text(repo, slug, page)):
        raise SystemExit(f"verification failed: '{needle}' not found on {slug} PDF p.{page}")


def num(token: str) -> float:
    return float(token.replace(",", ""))


def first_value(text: str, label: str) -> float:
    match = re.search(r"^[ \t]*" + label + r"[ \t]+(-|[\d,]+(?:\.\d+)?)(?=\s)", text, re.M)
    if not match:
        raise SystemExit(f"generation row not found: {label}")
    return 0.0 if match.group(1) == "-" else num(match.group(1))


def capacity_kw(text: str, label: str) -> float:
    match = re.search(label + r"\s*\**\s+([\d,]{3,})", flat(text))
    if not match:
        raise SystemExit(f"capacity not found: {label}")
    return num(match.group(1))


def fmt(value: float | None, places: int = 2) -> str:
    if value is None:
        return ""
    return f"{value:.{places}f}".rstrip("0").rstrip(".")


def plf(gwh: float, mw: float) -> str:
    return fmt(gwh * 1000 / (mw * HOURS) * 100, 1) if mw else ""


def build_plants(repo: Path) -> tuple[list[dict], dict]:
    rows: list[dict] = []
    totals: dict = {}
    for fy, (slug, gen_page, cap_page) in GEN_YEARS.items():
        gen_text = page_text(repo, slug, gen_page)
        cap_text = page_text(repo, slug, cap_page)
        grand_total = first_value(gen_text, r"Grand Total") / 1000.0
        plant_sum = 0.0
        for name, gen_label, cap_label, pslug, design, design_page in NEA_PLANTS:
            gwh = first_value(gen_text, gen_label) / 1000.0
            plant_sum += gwh
            mw = capacity_kw(cap_text, cap_label) / 1000.0
            notes = []
            loc = f"PDF p.{gen_page} Generation Directorate monthly energy generation table (Total Actual, MWh); capacity p.{cap_page}"
            design_val = ""
            if design and fy == "2025/26":
                needle = "Total Annual Design Generation 211" if name == "Kulekhani I" else f"{design} GWh"
                require(repo, R26, design_page, needle)
                design_val = design
                loc += f"; design generation plant fact-sheet p.{design_page}"
            if gwh == 0:
                notes.append("table prints '-' (no generation) for every month")
            if name in THERMAL:
                notes.append("thermal plant not in normal operation")
            if name == "Gandak" and design_val:
                notes.append("p.187 summary table prints 71.0 GWh design generation")
            if name == "Sunkoshi" and design_val:
                notes.append("p.187 summary table prints 62.7 GWh design generation")
            if name == "Kulekhani I" and design_val:
                notes.append("design is primary + secondary energy")
            rows.append({
                "plant_name": name,
                "project_slug": pslug,
                "ownership_class": "thermal" if name in THERMAL else "nea",
                "installed_capacity_mw": fmt(mw, 3),
                "fiscal_year_ad": fy,
                "actual_generation_gwh": fmt(gwh, 2),
                "contracted_or_design_gwh": design_val.replace(",", ""),
                "implied_plf_pct": plf(gwh, mw),
                "source_slug": slug,
                "source_locator": loc,
                "verified_on": VERIFIED_ON,
                "notes": "; ".join(notes),
            })
        if abs(plant_sum - grand_total) > 0.01:
            raise SystemExit(f"{fy}: plant sum {plant_sum:.2f} != Grand Total {grand_total:.2f}")
        totals[fy] = {"nea_plants": plant_sum, "subsidiary_plants": 0.0, "ipp_plants": 0.0}
    for name, pslug, fy, gwh_text, slug, page, cap_text, cap_page, design, design_page, note in SUBSIDIARY_ROWS:
        require(repo, slug, page, f"{gwh_text} GWh")
        require(repo, slug, cap_page, cap_text)
        loc = f"PDF p.{page} Business Development Directorate narrative; capacity p.{cap_page} (Appendix 7)"
        if design:
            require(repo, slug, design_page, f"{design} GWh")
            loc += f"; design energy p.{design_page}"
        gwh = num(gwh_text)
        mw = num(cap_text) / 1000.0
        totals[fy]["subsidiary_plants"] += gwh
        rows.append({
            "plant_name": name,
            "project_slug": pslug,
            "ownership_class": "nea-subsidiary",
            "installed_capacity_mw": fmt(mw, 3),
            "fiscal_year_ad": fy,
            "actual_generation_gwh": fmt(gwh, 2),
            "contracted_or_design_gwh": design.replace(",", ""),
            "implied_plf_pct": plf(gwh, mw),
            "source_slug": slug,
            "source_locator": loc,
            "verified_on": VERIFIED_ON,
            "notes": note,
        })
    for row in rows:
        if row["project_slug"] and not (ROOT / "wiki/pages/entities" / f"{row['project_slug']}.md").exists():
            raise SystemExit(f"project_slug has no entity page: {row['project_slug']}")
    rows.sort(key=lambda r: (r["fiscal_year_ad"], r["ownership_class"], r["plant_name"]))
    return rows, totals


def reconcile(totals: dict) -> list[str]:
    path = ROOT / TIMESERIES
    agg = {r["fiscal_year_ad"]: r for r in csv.DictReader(path.open(encoding="utf-8"))}
    lines = []
    for fy, t in sorted(totals.items()):
        a = agg[fy]
        for label, plant_key, agg_key in [
            ("NEA own generation", "nea_plants", "energy_nea_gwh"),
            ("NEA subsidiary purchase", "subsidiary_plants", "energy_nea_subsidiary_gwh"),
            ("IPP purchase", "ipp_plants", "energy_ipp_gwh"),
        ]:
            aggregate = float(a[agg_key])
            lines.append(f"{fy} {label}: plants {t[plant_key]:.2f} GWh vs aggregate {aggregate:g} GWh; "
                         f"unallocated {aggregate - t[plant_key]:.2f} GWh")
    return lines


# ---------------------------------------------------------------- grid summary
def bs_to_ad(bs: str) -> str:
    start = int(bs.split("/")[0]) - 57
    return f"{start}/{str(start + 1)[-2:]}"


def norm_bs(token: str) -> str:
    a, b = token.split("/")
    return f"{a}/{b[-2:]}"


def grid_row(metric, vclass, bs, value, unit, slug, loc, count="", notes=""):
    return {
        "metric": metric, "voltage_class": vclass, "fiscal_year_bs": bs, "fiscal_year_ad": bs_to_ad(bs),
        "value": value, "unit": unit, "count": count, "source_slug": slug, "source_locator": loc,
        "verified_on": VERIFIED_ON, "notes": notes,
    }


def ten_year_tables(repo: Path, slug: str, page: int, only: set[str] | None) -> list[dict]:
    text = page_text(repo, slug, page)
    out = []
    loc_line = f"PDF p.{page} Comparison of Transmission Line Length in the last Ten Fiscal Years"
    loc_sub = f"PDF p.{page} Comparison of Substation Capacity in the Last Ten Fiscal Years"
    for m in re.finditer(r"^\s*\d+\s+(20\d\d/0?\d\d)\s+([\d\s.]+?)\s*$", text, re.M):
        bs = norm_bs(m.group(1))
        if only is not None and bs not in only:
            continue
        vals = m.group(2).split()
        if len(vals) >= 5:  # line-length table: 66,132,220,400,total[,increment]
            v66, v132, v220, v400, total = vals[:5]
            for vc, v in [("66kV", v66), ("132kV", v132), ("220kV", v220), ("400kV", v400), ("total", total)]:
                out.append(grid_row("transmission_circuit_km", vc, bs, v, "circuit-km", slug, loc_line))
        elif len(vals) == 3 and bs == "2072/73":  # FY 2072/73 row has no 220/400 kV entries
            v66, v132, total = vals
            for vc, v in [("66kV", v66), ("132kV", v132), ("total", total)]:
                out.append(grid_row("transmission_circuit_km", vc, bs, v, "circuit-km", slug, loc_line,
                                    notes="220 kV and 400 kV cells blank in source"))
        elif len(vals) in (1, 2):  # substation table: total[, increment]
            out.append(grid_row("substation_capacity_total_mva", "all-hv", bs, vals[0], "MVA", slug, loc_sub))
    return out


def ratio_summary(repo: Path, slug: str, page: int, prev_bs: str, cur_bs: str) -> list[dict]:
    text = page_text(repo, slug, page)
    out = []
    loc = f"PDF p.{page} summary of existing high voltage grid substations by voltage rating"
    for m in re.finditer(r"^\s*\d\s+(\d{2,3}/\d{2,3})\s+(\d+)\s+([\d.]+)\s+([\d.]+)\s+(-?[\d.]+)\s*$", text, re.M):
        ratio, count, prev, cur, _inc = m.groups()
        out.append(grid_row("substation_transformer_mva", ratio, cur_bs, cur, "MVA", slug, loc, count=count))
        if prev_bs:
            out.append(grid_row("substation_transformer_mva", ratio, prev_bs, prev, "MVA", slug, loc,
                                notes="prior-year column of the same table; transformer count not given for this year"))
    total = re.search(r"^\s*Total\s+(\d+)\s+([\d.]+)\s+([\d.]+)\s+(-?[\d.]+)\s*$", text, re.M)
    if not total:
        raise SystemExit(f"ratio summary total not found on {slug} p.{page}")
    count, prev, cur, _ = total.groups()
    out.append(grid_row("substation_transformer_mva", "total", cur_bs, cur, "MVA", slug, loc, count=count))
    if prev_bs:
        out.append(grid_row("substation_transformer_mva", "total", prev_bs, prev, "MVA", slug, loc,
                            notes="prior-year column of the same table"))
    ratio_sum = sum(float(r["value"]) for r in out if r["fiscal_year_bs"] == cur_bs and r["voltage_class"] != "total")
    if abs(ratio_sum - float(cur)) > 1.0:
        raise SystemExit(f"{slug} p.{page}: ratio rows sum {ratio_sum} != total {cur}")
    return out


def line_inventory(repo: Path, slug: str, pages: list[int], bs: str) -> list[dict]:
    out = []
    for page in pages:
        for m in re.finditer(r"Total \((\d+) kV\)\s+([\d.]+)", flat(page_text(repo, slug, page))):
            out.append(grid_row("existing_line_inventory_circuit_km", f"{m.group(1)}kV", bs, m.group(2), "circuit-km",
                                slug, f"PDF p.{page} Existing High Voltage Transmission Lines inventory subtotal",
                                notes="sum of the line-by-line inventory; differs from the ten-year comparison table"))
    return out


def build_grid(repo: Path) -> list[dict]:
    rows: list[dict] = []
    rows += ten_year_tables(repo, R26, 205, None)
    rows += ten_year_tables(repo, R25, 170, {"2072/73"})
    rows += ratio_summary(repo, R26, 222, "", "2082/83")
    rows += ratio_summary(repo, R25, 184, "2080/81", "2081/82")
    rows += line_inventory(repo, R26, [208, 209], "2082/83")
    rows += line_inventory(repo, R25, [173, 174], "2081/82")
    # FY 2076/77 baseline: transmission annual book ratio summary.
    text = page_text(repo, BOOK, 251)
    loc = "PDF p.251 annexure summary of existing substations by voltage rating (FY 76-77 column)"
    for m in re.finditer(r"^\s*\d\s+(\d{2,3}/\d{2,3})\s+(\d+)\s+(?:[\d.]+\s+)?([\d.]+)\s+([\d.]+)\s+([\d.]+)\s*$", text, re.M):
        ratio, count, _p, cur, _inc = m.groups()
        rows.append(grid_row("substation_transformer_mva", ratio, "2076/77", cur, "MVA", BOOK, loc, count=count))
    tot = re.search(r"^\s*Total\s+(\d+)\s+[\d.]+\s+[\d.]+\s+([\d.]+)\s+[\d.]+\s*$", text, re.M)
    rows.append(grid_row("substation_transformer_mva", "total", "2076/77", tot.group(2), "MVA", BOOK, loc, count=tot.group(1)))
    # Distribution network statements (DCSD narrative), verified against page text.
    for bs, slug, page, items in [
        ("2082/83", R26, 61, [("distribution_line_circuit_km", "33kV", "8,388", "circuit-km", "8,388 ckt-km of 33 kV"),
                               ("distribution_line_circuit_km", "11kV", "54,296", "circuit-km", "54,296 ckt-km of 11 kV"),
                               ("distribution_substation_mva", "33/11", "3,048", "MVA", "3,048 MVA")]),
        ("2081/82", R25, 49, [("distribution_line_circuit_km", "33kV", "8,145", "circuit-km", "8,145 ckt-km of 33"),
                               ("distribution_line_circuit_km", "11kV", "53,131", "circuit-km", "53,131 ckt-km of 11 kV"),
                               ("distribution_substation_mva", "33/11", "2,997", "MVA", "2,997 MVA")]),
    ]:
        for metric, vc, value, unit, needle in items:
            require(repo, slug, page, needle)
            count = ""
            notes = "DCSD distribution network (not Transmission Directorate grid substations)"
            if metric == "distribution_substation_mva":
                count = "221" if bs == "2082/83" else "210"
                require(repo, slug, page, f"{count} numbers")
            rows.append(grid_row(metric, vc, bs, value.replace(",", ""), unit, slug,
                                 f"PDF p.{page} Distribution and Consumer Services Directorate narrative", count=count, notes=notes))
    order = {"transmission_circuit_km": 0, "existing_line_inventory_circuit_km": 1, "substation_capacity_total_mva": 2,
             "substation_transformer_mva": 3, "distribution_line_circuit_km": 4, "distribution_substation_mva": 5}
    rows.sort(key=lambda r: (order[r["metric"]], r["fiscal_year_bs"], r["voltage_class"]))
    return rows


def render(rows: list[dict], columns: list[str]) -> str:
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=columns, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return buf.getvalue()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--repo-root", type=Path, default=ROOT, help="checkout containing data/raw PDFs")
    parser.add_argument("--check", action="store_true", help="fail if committed CSVs differ")
    args = parser.parse_args()
    repo = args.repo_root.resolve()
    plants, totals = build_plants(repo)
    grid = build_grid(repo)
    print(f"plant rows: {len(plants)}; grid rows: {len(grid)}")
    for line in reconcile(totals):
        print("reconcile:", line)
    outputs = {PLANT_OUT: render(plants, PLANT_COLUMNS), GRID_OUT: render(grid, GRID_COLUMNS)}
    status = 0
    for path, text in outputs.items():
        target = ROOT / path
        if args.check:
            if not target.exists() or target.read_text(encoding="utf-8") != text:
                print(f"FAIL: {path} is stale; rerun without --check", file=sys.stderr)
                status = 1
            else:
                print(f"OK: {path} matches extraction")
        else:
            target.write_text(text, encoding="utf-8")
            print(f"wrote {path}")
    return status


if __name__ == "__main__":
    raise SystemExit(main())
