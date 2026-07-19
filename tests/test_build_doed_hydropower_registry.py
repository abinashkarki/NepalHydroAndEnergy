from __future__ import annotations

import unittest

import pandas as pd

from scripts import build_doed_hydropower_registry as registry


class DoEDRegistryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.source = registry.SourceSpec(
            "fixture",
            "fixture",
            "generation_license",
            1,
            license_status="generation_license",
        )

    def test_standard_table_parses_and_preserves_legal_status(self) -> None:
        html = """
        <p>Updated on - July 02, 2026</p>
        <table><thead><tr><th>S No</th><th>Project</th><th>Capacity (MW)</th><th>River</th>
        <th>Lic No</th><th>Isuue Date</th><th>Latitiude N</th><th>Latitiude N</th>
        <th>Longitude E</th><th>Longitude E</th></tr></thead>
        <tbody><tr><td>1</td><td>Upper Example HEP</td><td>42</td><td>Example</td><td>7</td>
        <td>2080-01-01</td><td>27o 00' 00&quot;</td><td>27o 01' 00&quot;</td>
        <td>85o 00' 00&quot;</td><td>85o 01' 00&quot;</td></tr></tbody></table>
        """
        frame = registry.parse_table(html, self.source)
        row = registry.normalize_row(frame.iloc[0], self.source, registry.parse_updated_on(html, self.source))
        self.assertEqual(row["project"], "Upper Example HEP")
        self.assertEqual(row["source_row_number"], "1")
        self.assertEqual(row["capacity_mw"], 42.0)
        self.assertEqual(row["license_status"], "generation_license")
        self.assertEqual(row["delivery_status"], "")
        self.assertEqual(row["source_updated_on"], "2026-07-02")

    def test_cancelled_header_row_is_promoted(self) -> None:
        frame = pd.DataFrame(
            [
                ["S No", "Project", "Capacity (MW)", "River", "Decision Date"],
                ["1", "Cancelled Example (SLC)", "5", "Example", "65000"],
            ]
        )
        flattened = registry.flatten_columns(frame)
        self.assertIn("Project", flattened.columns)
        self.assertEqual(flattened.iloc[0]["Project"], "Cancelled Example (SLC)")

    def test_multiindex_uses_semantic_last_level(self) -> None:
        frame = pd.DataFrame(
            [[1, "Studied Example", 10]],
            columns=pd.MultiIndex.from_tuples([("noise", "S No"), ("noise", "Project"), ("noise", "Capacity (MW)")]),
        )
        flattened = registry.flatten_columns(frame)
        self.assertEqual(list(flattened.columns), ["S No", "Project", "Capacity (MW)"])

    def test_row_floor_detects_truncated_source(self) -> None:
        source = registry.SourceSpec("fixture", "fixture", "survey_license", 2)
        html = """
        <p>Updated on - July 02, 2026</p>
        <table><tr><th>Project</th><th>Capacity (MW)</th></tr><tr><td>Only One</td><td>1</td></tr></table>
        """
        with self.assertRaisesRegex(ValueError, "below safety floor"):
            registry.parse_table(html, source)

    def test_operating_source_is_only_automatic_delivery_status(self) -> None:
        operating = next(source for source in registry.SOURCES if source.page_id == "operating_gt_1mw")
        generation = next(source for source in registry.SOURCES if source.page_id == "generation_license_gt_1mw")
        self.assertEqual(operating.delivery_status, "operating")
        self.assertEqual(generation.delivery_status, "")


if __name__ == "__main__":
    unittest.main()
