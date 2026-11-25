from __future__ import annotations

import csv
import json
import unittest
from pathlib import Path

from scripts import build_siting_readiness as sr

ROOT = Path(__file__).resolve().parent.parent


def read(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


class SitingReadinessTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.rows = read(sr.OUT_CSV)
        cls.subs = {r["slug"]: r for r in read(sr.SUBSTATIONS)}
        cls.tariffs = {r["tariff_id"]: r for r in read(sr.TARIFFS)}

    def test_outputs_are_current(self) -> None:
        self.assertEqual(sr.main(["--check"]), 0)

    def test_columns_and_unique_ids(self) -> None:
        with sr.OUT_CSV.open(newline="", encoding="utf-8") as handle:
            self.assertEqual(next(csv.reader(handle)), sr.COLUMNS)
        ids = [r["hub_id"] for r in self.rows]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertGreaterEqual(len(self.rows), 25)

    def test_numbers_are_copied_from_verified_registries(self) -> None:
        wet = self.tariffs["tod-132-industrial-wet-off-peak"]["energy_rate_npr_kwh"]
        dry = self.tariffs["tod-132-industrial-dry-peak"]["energy_rate_npr_kwh"]
        for row in self.rows:
            sub = self.subs[row["substation_slug"]]
            for col in ("highest_voltage_kv", "installed_mva", "planned_additional_mva", "linked_solar_award_mw"):
                self.assertEqual(row[col], sub[col].strip(), (row["hub_id"], col))
            self.assertEqual(row["substation_status"], sub["status"])
            self.assertEqual(row["industrial_tod_132kv_wet_offpeak_npr"], wet)
            self.assertEqual(row["industrial_tod_132kv_dry_peak_npr"], dry)
            self.assertIn("canonical-lookup", row["source_basis"])
            self.assertIn("bay headroom", row["missing_siting_data"])
            for banned in ("score", "rank", "index_value"):
                self.assertNotIn(banned, " ".join(row.keys()))

    def test_selection_rules(self) -> None:
        grid = [r for r in self.rows if r["hub_type"].endswith("grid-hub")]
        expected = {s for s, r in self.subs.items() if r["highest_voltage_kv"] in ("400", "220") and r["status"] in sr.GRID_STATUSES}
        self.assertEqual({r["substation_slug"] for r in grid}, expected)
        for row in self.rows:
            self.assertIn(row["hub_type"], {"400kv-grid-hub", "220kv-grid-hub", "sez", "industrial-estate", "industrial-corridor"})
            self.assertIn(row["climate_zone_band"], {"Terai", "Mid-Hill", "Valley", "Mountain", ""})
            if not row["hub_type"].endswith("grid-hub"):
                self.assertGreaterEqual(int(self.subs[row["substation_slug"]]["highest_voltage_kv"]), 132)

    def test_climate_band_lookup(self) -> None:
        self.assertEqual(sr.climate_band("Kathmandu"), "Valley")
        self.assertEqual(sr.climate_band("Sunsari"), "Terai")
        self.assertEqual(sr.climate_band("Rasuwa"), "Mountain")
        self.assertEqual(sr.climate_band("Tanahun"), "Mid-Hill")
        self.assertEqual(len(sr.MOUNTAIN), 16)
        self.assertEqual(len(sr.TERAI), 21)
        with self.assertRaises(SystemExit):
            sr.climate_band("Atlantis")

    def test_geojson_only_mapped_rows(self) -> None:
        data = json.loads(sr.OUT_GEOJSON.read_text(encoding="utf-8"))
        self.assertEqual(len(data["features"]), sum(1 for r in self.rows if r["latitude"]))


if __name__ == "__main__":
    unittest.main()
