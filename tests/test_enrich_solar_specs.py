from __future__ import annotations

import csv
import json
import unittest
from pathlib import Path

from scripts import enrich_solar_specs as enrich

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = json.loads((ROOT / "wiki" / "solar-specs-schema.json").read_text(encoding="utf-8"))
VALID_PROVINCES = set(enrich.PROVINCE_CODE_NAMES.values())


def load_rows() -> list[dict[str, str]]:
    with (ROOT / enrich.CSV_PATH).open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


class EnrichSolarSpecsTests(unittest.TestCase):
    def test_district_lookup_covers_all_77_districts(self) -> None:
        single = [d for d, p in enrich.DISTRICT_PROVINCES.items() if len(p) == 1]
        self.assertEqual(len(single), 77)
        self.assertTrue(all(set(p) <= VALID_PROVINCES for p in enrich.DISTRICT_PROVINCES.values()))

    def test_split_district_requires_row_evidence(self) -> None:
        row = {"district": "Nawalparasi", "substation": ""}
        self.assertEqual(enrich.derive_province(row, ["Koshi"]), ("", "split-district-unresolved"))
        self.assertEqual(enrich.derive_province(row, ["Gandaki"])[0], "Gandaki")
        row["substation"] = "Parasi"
        self.assertEqual(enrich.derive_province(row, [])[0], "Lumbini")

    def test_district_wins_over_display_point(self) -> None:
        row = {"district": "Kanchanpur", "substation": "Belauri"}
        self.assertEqual(enrich.derive_province(row, ["Koshi"]), ("Sudurpashchim", "district-lookup"))

    def test_unlisted_district_gets_no_zone(self) -> None:
        self.assertEqual(enrich.derive_zone("Nuwakot")[0], "")
        self.assertEqual(enrich.derive_zone("Kapilbastu")[0], "B1")
        self.assertEqual(enrich.derive_zone("Nawalpur")[0], "B1")

    def test_siting_requires_named_substation(self) -> None:
        award = {"record_kind": "procurement-award-record", "procurement_stage": "loi-awarded", "substation": "Lamahi"}
        self.assertEqual(enrich.derive_siting(award)[0], "substation-adjacent")
        award["substation"] = ""
        self.assertEqual(enrich.derive_siting(award)[0], "unknown")
        op = {"record_kind": "operating-registry-record", "label_title": "Solar Power Project, Simara 11 kV S/S"}
        self.assertEqual(enrich.derive_siting(op)[0], "substation-adjacent")
        op["label_title"] = "Bel Chautara Solar Farm Project"
        self.assertEqual(enrich.derive_siting(op)[0], "unknown")

    def test_committed_csv_is_enriched_and_schema_valid(self) -> None:
        rows = load_rows()
        self.assertTrue(rows)
        zone_enum = set(SCHEMA["properties"]["resource_zone"]["enum"])
        siting_enum = set(SCHEMA["properties"]["siting_archetype"]["enum"])
        for row in rows:
            self.assertIn(row["province"], VALID_PROVINCES, row["slug"])
            self.assertIn(row["resource_zone"], zone_enum, row["slug"])
            self.assertIn(row["siting_archetype"], siting_enum - {""}, row["slug"])
            self.assertEqual(row["expected_annual_generation_gwh"], "", row["slug"])
        self.assertEqual(set(rows[0]) - set(SCHEMA["properties"]), set())

    def test_enrichment_is_idempotent(self) -> None:
        rows = load_rows()
        before = [dict(r) for r in rows]
        provinces = enrich.load_polygons(
            ROOT / enrich.PROVINCES_PATH, lambda p: enrich.PROVINCE_CODE_NAMES[int(p["PROVINCE"])]
        )
        ghi = enrich.load_polygons(ROOT / enrich.GHI_ZONES_PATH, lambda p: p["id"])
        enrich.enrich(rows, provinces, ghi)
        self.assertEqual(rows, before)


if __name__ == "__main__":
    unittest.main()
