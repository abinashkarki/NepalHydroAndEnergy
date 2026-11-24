from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest import mock

from scripts import build_doed_nonhydro_registry as registry

# Hand-made fixture reproducing only the DoED table structure; names are fictitious.
OPERATING_HTML = """
<p>Updated on - Ocotober 15, 2026</p>
<table><thead><tr><th>S No</th><th>Project</th><th>Capacity (MW)</th><th>Lic No</th>
<th>Isuue Date</th><th>Validity</th><th>Promoter</th><th>Address</th><th>Latitiude N</th>
<th>Latitiude N</th><th>Longitude E</th><th>Longitude E</th><th>VDC/District</th><th>C O D</th></tr></thead>
<tbody>
<tr><td>1</td><td>Example Solar Farm</td><td>5.5</td><td>101</td><td>2080-01-01</td><td>0000-00-00</td>
<td>Example Power Ltd.</td><td>Example Road, 98000000</td><td>00o 00' 00&quot;</td><td>00o 00' 00&quot;</td>
<td>85o 00' 00&quot;</td><td>85o 01' 00&quot;</td><td>Example (Exampledistrict)</td><td>2081-02-02</td></tr>
<tr><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td></tr>
</tbody></table>
"""

EMPTY_HTML = """
<p>Updated on - October 15, 2026</p>
<table><thead><tr><th>S No</th><th>Project</th><th>Capacity (MW)</th><th>Appn No</th>
<th>Appn Date</th><th>Promoter</th></tr></thead><tbody></tbody></table>
"""


class DoEDNonHydroRegistryTests(unittest.TestCase):
    def test_sources_cover_five_technologies_and_five_categories(self) -> None:
        self.assertEqual(len(registry.SOURCES), 25)
        paths = {s.path for s in registry.SOURCES}
        self.assertIn("clbiomass-77", paths)
        self.assertIn("powerplantssolar", paths)
        operating = [s for s in registry.SOURCES if s.regulatory_category == "operating"]
        self.assertTrue(all(s.delivery_status == "operating-registry-listed" for s in operating))
        licences = [s for s in registry.SOURCES if s.regulatory_category != "operating"]
        self.assertTrue(all(s.delivery_status == "" for s in licences))

    def test_operating_row_normalization(self) -> None:
        source = registry.SourceSpec("operating_solar", "powerplantssolar", "solar", "operating", "",
                                     "operating-registry-listed")
        rows, updated = registry.parse_source(OPERATING_HTML, source)
        self.assertEqual(updated, "2026-10-15")  # tolerates DoED's month typo
        self.assertEqual(len(rows), 1)
        row = rows[0]
        self.assertEqual(row["project"], "Example Solar Farm")
        self.assertEqual(row["capacity_mw"], 5.5)
        self.assertEqual(row["record_number"], "101")
        self.assertEqual(row["validity_date_bs"], "")
        self.assertEqual(row["cod_date_bs"], "2081-02-02")
        self.assertEqual(row["latitude_1_dms"], "")
        self.assertEqual(row["longitude_2_dms"], "85o 01' 00\"")
        self.assertNotIn("address", row)
        self.assertEqual(set(row), set(registry.OUTPUT_FIELDS))

    def test_empty_table_is_valid(self) -> None:
        source = registry.SourceSpec("survey_application_wind", "appslwind", "wind", "survey_application",
                                     "survey_application")
        rows, updated = registry.parse_source(EMPTY_HTML, source)
        self.assertEqual(rows, [])
        self.assertEqual(updated, "2026-10-15")

    def test_missing_update_date_fails_loudly(self) -> None:
        with self.assertRaises(ValueError):
            registry.parse_source("<table><tr><th>Project</th><th>Capacity (MW)</th></tr></table>",
                                  registry.SOURCES[0])

    def test_offline_build_from_cache(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            cache = Path(tmp)
            for source in registry.SOURCES:
                html = OPERATING_HTML if source.page_id == "operating_solar" else EMPTY_HTML
                (cache / f"{source.path}.html").write_text(html, encoding="utf-8")
            with mock.patch.object(registry.requests, "get", side_effect=AssertionError("network used")):
                rows, summary = registry.build_registry(from_cache=cache)
        self.assertEqual(summary["rows"], 1)
        self.assertEqual(summary["category_counts"], {"operating": 1})
        self.assertEqual(len(summary["sources"]), 25)
        self.assertTrue(all(len(s["sha256"]) == 64 for s in summary["sources"]))


if __name__ == "__main__":
    unittest.main()
