from __future__ import annotations

import csv
import json
import unittest

from scripts import build_substation_specs_links as links
from scripts import validate_repo


def load_schema() -> dict:
    return json.loads(validate_repo.SUBSTATION_SCHEMA_PATH.read_text(encoding="utf-8"))


def base_row(**overrides: str) -> dict[str, str]:
    row = {name: "" for name in load_schema()["properties"]}
    row.update({
        "slug": "example-substation", "substation_name": "Example", "highest_voltage_kv": "132",
        "voltage_ratios": "132/33;33/11", "installed_mva": "60", "status": "operating",
        "status_as_of": "2026-07-16", "owner": "Nepal Electricity Authority",
        "source_slug": "nea-annual-report-fy2025-26", "source_locator": "Appendix, p.1",
        "confidence": "high", "last_updated": "2026-11-24",
    })
    row.update(overrides)
    return row


WIKI_SLUGS = {"nea-annual-report-fy2025-26", "mca-central-400"}


class SubstationSchemaTests(unittest.TestCase):
    def errors(self, rows: list[dict[str, str]]) -> list[str]:
        schema = load_schema()
        return validate_repo.substation_specs_errors(schema, list(schema["properties"]), rows, WIKI_SLUGS)

    def test_valid_row_passes(self) -> None:
        self.assertEqual(self.errors([base_row()]), [])

    def test_rejects_bad_status_voltage_and_duplicate_slug(self) -> None:
        errs = self.errors([base_row(status="commissioned"), base_row(highest_voltage_kv="33")])
        joined = "\n".join(errs)
        self.assertIn("'status' value 'commissioned' not in schema enum", joined)
        self.assertIn("'highest_voltage_kv' value '33' not in schema enum", joined)
        self.assertIn("duplicate slugs: example-substation", joined)

    def test_rejects_out_of_range_numbers_and_half_coordinates(self) -> None:
        errs = "\n".join(self.errors([
            base_row(installed_mva="-1", latitude="35.0", longitude="", coordinate_precision="approximate-place"),
        ]))
        self.assertIn("'installed_mva'=-1 below minimum", errs)
        self.assertIn("'latitude'=35.0 above maximum", errs)
        self.assertIn("latitude and longitude must both be set", errs)

    def test_rejects_unknown_source_and_corridor_slugs(self) -> None:
        errs = "\n".join(self.errors([base_row(source_slug="missing-source", corridor_slugs="mca-central-400;nope")]))
        self.assertIn("source_slug 'missing-source' not found", errs)
        self.assertIn("corridor slug 'nope' not found", errs)
        self.assertNotIn("'mca-central-400' not found", errs)

    def test_planned_row_cannot_report_installed_capacity(self) -> None:
        errs = "\n".join(self.errors([base_row(status="planned", installed_mva="30")]))
        self.assertIn("planned row must not report installed_mva", errs)

    def test_substation_slug_does_not_need_wiki_page(self) -> None:
        self.assertEqual(self.errors([base_row(slug="unpaged-substation")]), [])

    def test_repository_csv_is_valid(self) -> None:
        with validate_repo.SUBSTATION_SPECS_CSV_PATH.open(newline="", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            rows = list(reader)
            fieldnames = list(reader.fieldnames or [])
        errs = validate_repo.substation_specs_errors(load_schema(), fieldnames, rows, validate_repo.wiki_page_slugs())
        self.assertEqual(errs, [])
        self.assertGreaterEqual(len(rows), 80)


class SolarLinkTests(unittest.TestCase):
    def test_normalize_name_handles_aliases_and_qualifiers(self) -> None:
        self.assertEqual(links.normalize_name("Sunawal"), links.normalize_name("Sunwal"))
        self.assertEqual(links.normalize_name("Paudi"), links.normalize_name("Paudi Amarai"))
        self.assertEqual(links.normalize_name("Amarpur (Kabeli)"), "amarpur")
        self.assertEqual(links.normalize_name("Trishuli 3B HUB"), "trishuli3b")

    def test_compute_links_sums_matches_and_applies_guards(self) -> None:
        subs = [
            {"slug": "sunwal-substation", "substation_name": "Sunwal", "district": "Nawalparasi"},
            {"slug": "lahan-substation", "substation_name": "Lahan", "district": "Siraha"},
            {"slug": "maharajgunj-substation", "substation_name": "Maharajgunj", "district": ""},
        ]
        solar = [
            {"slug": "a", "substation": "Sunawal", "district": "Nawalparasi", "capacity_mw": "50"},
            {"slug": "b", "substation": "Lahan", "district": "Siraha", "capacity_mw": "10"},
            {"slug": "c", "substation": "Lahan", "district": "Siraha", "capacity_mw": "2.5"},
            {"slug": "d", "substation": "Lahan", "district": "Dang", "capacity_mw": "5"},
            {"slug": "e", "substation": "Maharajgunj", "district": "Kapilvastu", "capacity_mw": "5"},
            {"slug": "f", "substation": "Nowhere", "district": "", "capacity_mw": "1"},
            {"slug": "g", "substation": "", "district": "", "capacity_mw": "9"},
        ]
        totals, log = links.compute_links(subs, solar)
        self.assertEqual(totals, {"sunwal-substation": 50.0, "lahan-substation": 12.5})
        reasons = {e["solar_slug"]: e["reason"] for e in log}
        self.assertTrue(reasons["d"].startswith("district mismatch"))
        self.assertTrue(reasons["e"].startswith("excluded"))
        self.assertEqual(reasons["f"], "no substation_specs row with this name")
        self.assertNotIn("g", reasons)

    def test_repository_links_are_current(self) -> None:
        self.assertEqual(links.main(["--check"]), 0)


if __name__ == "__main__":
    unittest.main()
