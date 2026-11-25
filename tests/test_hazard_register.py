from __future__ import annotations

import csv
import unittest
from pathlib import Path

from scripts import build_hazard_layers as hz

ROOT = Path(__file__).resolve().parent.parent
EVENTS = ROOT / "data" / "infrastructure_hazard_events.csv"
EVENT_COLUMNS = [
    "event_id", "event_date", "hazard_type", "river_basin", "district", "province", "affected_asset_name",
    "asset_slug", "asset_type", "affected_mw", "outage_days", "estimated_damage_npr_m", "estimated_damage_usd_m",
    "impact_summary", "source_url", "source_title", "confidence", "verified_on",
]


class HazardRegisterTests(unittest.TestCase):
    def test_event_rows_are_sourced_and_typed(self) -> None:
        with EVENTS.open(newline="", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            self.assertEqual(reader.fieldnames[: len(EVENT_COLUMNS)], EVENT_COLUMNS)
            rows = list(reader)
        self.assertGreaterEqual(len(rows), 10)
        self.assertEqual(len({r["event_id"] for r in rows}), len(rows))
        for row in rows:
            self.assertIn(row["hazard_type"], {"flood", "glof", "landslide", "earthquake"}, row["event_id"])
            self.assertIn(row["asset_type"], {"hydro", "substation", "transmission"}, row["event_id"])
            self.assertIn(row["confidence"], {"high", "medium", "low"}, row["event_id"])
            self.assertTrue(row["source_url"].startswith("https://"), row["event_id"])
            for col in ("affected_mw", "outage_days", "estimated_damage_npr_m", "estimated_damage_usd_m"):
                if row[col]:
                    float(row[col])
        # August 2026 detail stays in its own register: exactly one cross-reference row.
        aug = [r for r in rows if r["event_date"].startswith("2026-08")]
        self.assertEqual(len(aug), 1)
        self.assertIn("flood_2026_08_impact_register.csv", aug[0]["affected_asset_name"])

    def test_lakes_match_icimod_ids_and_layer_is_current(self) -> None:
        with hz.LAKES.open(newline="", encoding="utf-8") as handle:
            lakes = list(csv.DictReader(handle))
        self.assertEqual(len(lakes), 21)
        self.assertTrue(all(r["country"] == "Nepal" for r in lakes))
        for row in lakes:
            if row["latitude"]:
                self.assertEqual(hz.lake_id_coords(row["lake_id"]), (float(row["longitude"]), float(row["latitude"])))
        self.assertEqual(hz.main(["--check"]), 0)


if __name__ == "__main__":
    unittest.main()
