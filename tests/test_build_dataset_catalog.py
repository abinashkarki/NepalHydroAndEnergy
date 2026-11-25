from __future__ import annotations

import csv
import json
import unittest
from pathlib import Path

from scripts import build_dataset_catalog as cat

ROOT = Path(__file__).resolve().parent.parent


class DatasetCatalogTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.catalog = cat.build_catalog()
        cls.by_path = {e["path"]: e for e in cls.catalog["datasets"]}

    def test_every_curated_csv_is_cataloged_with_live_counts(self) -> None:
        self.assertEqual(cat.uncataloged_csvs(self.catalog), [])
        for path in sorted((ROOT / "data").glob("*.csv")):
            rel = path.relative_to(ROOT).as_posix()
            with path.open(newline="", encoding="utf-8-sig") as handle:
                reader = csv.reader(handle)
                header = next(reader)
                rows = sum(1 for _ in reader)
            entry = self.by_path[rel]
            self.assertEqual(entry["rows"], rows, rel)
            self.assertEqual(entry["columns"], len(header), rel)

    def test_entries_have_required_fields_and_valid_domains(self) -> None:
        required = {"id", "title", "domain", "path", "format", "rows", "columns", "schema_path",
                    "companion_page_slug", "last_verified", "license", "summary"}
        ids = [e["id"] for e in self.catalog["datasets"]]
        self.assertEqual(len(ids), len(set(ids)))
        for entry in self.catalog["datasets"]:
            self.assertTrue(required <= set(entry), entry["id"])
            self.assertIn(entry["domain"], cat.DOMAINS)
            self.assertIn(entry["format"], {"csv", "geojson"})
            self.assertRegex(entry["last_verified"], r"^\d{4}-\d{2}-\d{2}$", entry["id"])
            if entry["schema_path"]:
                self.assertTrue((ROOT / entry["schema_path"]).exists(), entry["schema_path"])

    def test_geojson_rows_are_feature_counts(self) -> None:
        entry = self.by_path["data/processed/maps/grid_substations.geojson"]
        data = json.loads((ROOT / entry["path"]).read_text(encoding="utf-8"))
        self.assertEqual(entry["rows"], len(data["features"]))

    def test_committed_outputs_are_current(self) -> None:
        self.assertEqual(cat.main(["--check"]), 0)

    def test_splice_requires_markers(self) -> None:
        with self.assertRaises(SystemExit):
            cat.splice_page("no markers here", "x")
        spliced = cat.splice_page(f"a\n{cat.START}\nold\n{cat.END}\nb", f"{cat.START}\nnew\n{cat.END}")
        self.assertIn("new", spliced)
        self.assertNotIn("old", spliced)


if __name__ == "__main__":
    unittest.main()
