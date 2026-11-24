#!/usr/bin/env python3
"""Aggregate electric-vehicle import rows from Nepal Customs annual trade workbooks.

Input: the Department of Customs "Foreign Trade Statistics" annual XLSX files
(Table 5, "Imports by Commodities"), downloaded from customs.gov.np. They are
not committed; pass each as ``FY=path``::

    python scripts/extract_customs_ev_imports.py \
        2080/81=data/raw/customs/FTS_2080_81.xlsx \
        2081/82=data/raw/customs/FTS_Annual_2081_82.xlsx

Output: CSV rows on stdout in the ``ev_imports`` shape used by
``data/ev_adoption_and_charging.csv``. Only the Python standard library is used,
so the workbook is parsed without third-party XLSX code.
"""
from __future__ import annotations

import csv
import re
import sys
import zipfile
import xml.etree.ElementTree as ET

NS = {
    "m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main",
    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
}
TABLE5 = "5_Imports_By_Commodity"

# category -> 8-digit national HS codes (as printed in the workbook)
CATEGORIES: dict[str, tuple[str, ...]] = {
    "Electric car, jeep & van (HS 8703.80)": (
        "87038021", "87038029", "87038059", "87038069", "87038079", "87038089"),
    "Electric three-wheelers (HS 8703.80.1x)": ("87038011", "87038019"),
    "Electric buses, minibuses & microbuses (HS 8702.40.10-30)": (
        "87024010", "87024020", "87024030"),
    "Electric jeep, car & van classed under HS 8702.40.49": ("87024049",),
    "Electric motorcycles, scooters & mopeds (HS 8711.60.2x-9x)": (
        "87116020", "87116031", "87116032", "87116090"),
    "Electric bicycles (HS 8711.60.10)": ("87116010",),
}
COLUMNS = ["period", "category", "hs_codes", "quantity", "quantity_unit", "value_npr_thousand"]


def read_table5(path: str) -> dict[str, tuple[float, float]]:
    """Return {hs_code: (quantity, value_npr_thousand)} from Table 5."""
    z = zipfile.ZipFile(path)
    shared: list[str] = []
    if "xl/sharedStrings.xml" in z.namelist():
        for si in ET.fromstring(z.read("xl/sharedStrings.xml")).findall("m:si", NS):
            shared.append("".join(t.text or "" for t in si.iter(f"{{{NS['m']}}}t")))
    wb = ET.fromstring(z.read("xl/workbook.xml"))
    rels = {r.get("Id"): r.get("Target") for r in ET.fromstring(z.read("xl/_rels/workbook.xml.rels"))}
    target = None
    for sheet in wb.find("m:sheets", NS):
        if sheet.get("name") == TABLE5:
            target = rels[sheet.get(f"{{{NS['r']}}}id")].lstrip("/")
    if target is None:
        raise SystemExit(f"{path}: sheet {TABLE5} not found")
    if not target.startswith("xl/"):
        target = "xl/" + target
    out: dict[str, tuple[float, float]] = {}
    for row in ET.fromstring(z.read(target)).iter(f"{{{NS['m']}}}row"):
        cells: dict[str, str] = {}
        for c in row.findall("m:c", NS):
            v = c.find("m:v", NS)
            col = re.sub(r"\d", "", c.get("r", ""))
            if v is None:
                continue
            cells[col] = shared[int(v.text)] if c.get("t") == "s" else (v.text or "")
        code = cells.get("A", "").strip()
        if re.fullmatch(r"\d{8}", code):
            try:
                out[code] = (float(cells.get("D", "0")), float(cells.get("E", "0")))
            except ValueError:
                continue
    return out


def main(argv: list[str]) -> int:
    if not argv:
        print(__doc__, file=sys.stderr)
        return 2
    writer = csv.writer(sys.stdout)
    writer.writerow(COLUMNS)
    for arg in argv:
        period, path = arg.split("=", 1)
        table = read_table5(path)
        for category, codes in CATEGORIES.items():
            present = [c for c in codes if c in table]
            qty = sum(table[c][0] for c in present)
            value = sum(table[c][1] for c in present)
            writer.writerow([f"FY {period}", category, ";".join(present),
                             int(round(qty)), "PCS", round(value, 1)])
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
