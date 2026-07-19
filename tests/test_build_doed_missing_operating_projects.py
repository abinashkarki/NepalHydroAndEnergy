from __future__ import annotations

import unittest
import json
from pathlib import Path

from scripts.build_doed_missing_operating_projects import build_missing_operating, envelope_midpoint


class DoEDMissingOperatingTests(unittest.TestCase):
    def test_midpoint_is_envelope_reference(self) -> None:
        row = {
            "latitude_1_dms": "27o 00' 00\"",
            "latitude_2_dms": "27o 02' 00\"",
            "longitude_1_dms": "85o 00' 00\"",
            "longitude_2_dms": "85o 04' 00\"",
        }
        self.assertEqual(envelope_midpoint(row), (27.016667, 85.033333))

    def test_builds_separate_official_layer_and_keeps_unmapped_record_in_csv(self) -> None:
        registry = [
            {
                "project": "Mapped HEP", "technology": "hydro", "regulatory_category": "operating_record",
                "capacity_mw": "10", "latitude_1_dms": "27o 00' 00\"", "latitude_2_dms": "27o 02' 00\"",
                "longitude_1_dms": "85o 00' 00\"", "longitude_2_dms": "85o 04' 00\"", "source_url": "https://doed.gov.np/a",
            },
            {
                "project": "Unmapped SHP", "technology": "hydro", "regulatory_category": "operating_record",
                "capacity_mw": "0.5", "latitude_1_dms": "00o 00' 00\"", "latitude_2_dms": "00o 00' 00\"",
                "longitude_1_dms": "00o 00' 00\"", "longitude_2_dms": "00o 00' 00\"", "source_url": "https://doed.gov.np/b",
            },
        ]
        review = [
            {"official_project": "Mapped HEP", "official_regulatory_category": "operating_record"},
            {"official_project": "Unmapped SHP", "official_regulatory_category": "operating_record"},
        ]
        rows, geojson, summary = build_missing_operating(registry, review)
        self.assertEqual(len(rows), 2)
        self.assertEqual(len(geojson["features"]), 1)
        self.assertIn("not a facility location", geojson["metadata"]["coordinate_precision"])
        self.assertIn("reference midpoint", geojson["features"][0]["properties"]["label_title"])
        self.assertIn("not a facility location", geojson["features"][0]["properties"]["location_basis"])
        self.assertIn("separate from legacy Naxa", geojson["features"][0]["properties"]["dataset_role"])
        self.assertEqual(summary["records_without_usable_coordinates"], 1)

    def test_public_layer_is_opt_in_and_exposes_precision_in_tooltip_and_popup(self) -> None:
        root = Path(__file__).resolve().parents[1]
        manifest = json.loads((root / "wiki/explorer/shared/layer-manifest.json").read_text())
        presets = json.loads((root / "wiki/explorer/shared/presets.json").read_text())
        layer = manifest["layers"]["doed_operating_reference_midpoints"]

        self.assertIn("not facility locations", layer["label"])
        self.assertIn("coordinate_precision", layer["tooltip_fields"])
        self.assertTrue(any(
            isinstance(field, dict) and field.get("field") == "coordinate_precision"
            for field in layer["popup_fields"]
        ))
        self.assertTrue(all(
            "doed_operating_reference_midpoints" not in preset.get("layers_on", [])
            for preset in presets["presets"].values()
        ))


if __name__ == "__main__":
    unittest.main()
