from __future__ import annotations

import copy
import unittest

from scripts.apply_doed_project_status_overlay import DOED_FIELDS, apply_overlay


class ApplyDoedStatusOverlayTests(unittest.TestCase):
    def test_applies_official_fields_without_changing_geometry_or_curated_status(self) -> None:
        data = {
            "type": "FeatureCollection",
            "features": [{
                "type": "Feature",
                "properties": {
                    "project": "Example HEP",
                    "status": "under-construction",
                    "license_type": "Generation",
                    "doed_status_display": "stale",
                },
                "geometry": {"type": "Point", "coordinates": [84.0, 28.0]},
            }],
        }
        geometry = copy.deepcopy(data["features"][0]["geometry"])
        matched, unmatched = apply_overlay(data, {
            "Example HEP": {
                "doed_status_display": "Generation licence",
                "doed_primary_category": "generation_license",
            }
        })
        props = data["features"][0]["properties"]
        self.assertEqual((matched, unmatched), (1, 0))
        self.assertEqual(data["features"][0]["geometry"], geometry)
        self.assertEqual(props["status"], "under-construction")
        self.assertEqual(props["doed_status_display"], "Generation licence")

    def test_removes_stale_doed_fields_when_feature_has_no_overlay_row(self) -> None:
        data = {
            "features": [{
                "properties": {"project": "Missing", "doed_status_display": "stale"},
                "geometry": None,
            }]
        }
        matched, unmatched = apply_overlay(data, {})
        self.assertEqual((matched, unmatched), (0, 1))
        self.assertTrue(DOED_FIELDS.isdisjoint(data["features"][0]["properties"]))


if __name__ == "__main__":
    unittest.main()
