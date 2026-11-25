from __future__ import annotations

import csv
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CSV = ROOT / "data" / "nepse_hydro_performance.csv"
COLUMNS = [
    "company_slug", "company_name", "nepse_ticker", "project_slug", "installed_mw", "fiscal_year_bs",
    "fiscal_year_ad", "contracted_or_design_gwh", "actual_generation_gwh", "delivery_vs_contract_pct",
    "electricity_revenue_npr_m", "net_profit_npr_m", "total_debt_npr_m", "source_slug", "source_url",
    "source_locator", "confidence", "verified_on", "notes",
]
NUMERIC = ["installed_mw", "contracted_or_design_gwh", "actual_generation_gwh", "delivery_vs_contract_pct",
           "electricity_revenue_npr_m", "net_profit_npr_m", "total_debt_npr_m"]


class NepseHydroPerformanceTests(unittest.TestCase):
    def test_rows_are_sourced_typed_and_consistent(self) -> None:
        with CSV.open(newline="", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            self.assertEqual(reader.fieldnames, COLUMNS)
            rows = list(reader)
        self.assertGreaterEqual(len(rows), 1)
        keys = [(r["company_slug"], r["fiscal_year_bs"]) for r in rows]
        self.assertEqual(len(keys), len(set(keys)))
        source_pages = {p.stem for p in (ROOT / "wiki" / "pages" / "sources").glob("*.md")}
        project_pages = {p.stem for p in (ROOT / "wiki" / "pages").glob("*/*.md")}
        for row in rows:
            label = f"{row['company_slug']} {row['fiscal_year_bs']}"
            self.assertIn(row["source_slug"], source_pages, label)
            self.assertIn(row["project_slug"], project_pages, label)
            self.assertTrue(row["source_url"].startswith("https://"), label)
            self.assertRegex(row["source_locator"], r"PDF p\.\d+", label)
            self.assertRegex(row["fiscal_year_bs"], r"^20\d\d/\d\d$", label)
            self.assertIn(row["confidence"], {"high", "medium", "low"}, label)
            for col in NUMERIC:
                if row[col]:
                    float(row[col])
            if row["contracted_or_design_gwh"] and row["actual_generation_gwh"]:
                expected = float(row["actual_generation_gwh"]) / float(row["contracted_or_design_gwh"]) * 100
                self.assertAlmostEqual(float(row["delivery_vs_contract_pct"]), expected, places=2, msg=label)


if __name__ == "__main__":
    unittest.main()
