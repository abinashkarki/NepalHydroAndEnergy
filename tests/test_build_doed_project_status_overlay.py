from __future__ import annotations

import csv
import unittest

from scripts import build_doed_project_status_overlay as overlay


def local(name: str, capacity: float, lat: float = 27.05, lon: float = 85.05) -> dict:
    return {
        "project": name,
        "capacity_mw": capacity,
        "license_type": "Survey",
        "river": "Example",
        "raw_lat": lat,
        "raw_lon": lon,
    }


def official(name: str, capacity: float, category: str, lat: str = "27o 00' 00\"", lon: str = "85o 00' 00\"") -> dict:
    return {
        "record_id": f"{name}-{category}",
        "project": name,
        "capacity_mw": str(capacity),
        "river": "Example",
        "technology": "hydro",
        "regulatory_category": category,
        "record_status": "cancelled" if category.startswith("cancelled") else "active",
        "license_status": category,
        "study_status": "",
        "delivery_status": "operating" if category == "operating_record" else "",
        "record_number": "1",
        "latitude_1_dms": lat,
        "latitude_2_dms": lat,
        "longitude_1_dms": lon,
        "longitude_2_dms": lon,
        "source_url": "https://doed.gov.np/example",
        "source_updated_on": "2026-07-02",
    }


class DoEDOverlayTests(unittest.TestCase):
    def test_identity_name_strips_regulatory_suffix_not_project_number(self) -> None:
        self.assertEqual(overlay.identity_name("Upper Example-2 HEP (SLC)"), "upper example 2")
        self.assertNotEqual(overlay.identity_name("Upper Example-2 HEP"), overlay.identity_name("Upper Example HEP"))

    def test_dms_conversion(self) -> None:
        self.assertAlmostEqual(overlay.dms_to_decimal("27o 30' 00\""), 27.5)
        self.assertIsNone(overlay.dms_to_decimal(""))

    def test_operating_record_wins_and_sets_delivery_status(self) -> None:
        rows = [
            official("Example HEP", 10, "survey_license"),
            official("Example HEP", 10, "generation_license"),
            official("Example HEP", 10, "operating_record"),
        ]
        result, review, summary = overlay.build_overlay([local("Example HPP", 10)], rows, {})
        self.assertEqual(result[0]["doed_primary_category"], "operating_record")
        self.assertEqual(result[0]["doed_delivery_status"], "operating")
        self.assertEqual(summary["operating_local_rows"], 1)
        self.assertEqual(review, [])

    def test_generation_license_does_not_set_delivery_status(self) -> None:
        result, _, _ = overlay.build_overlay(
            [local("Example HPP", 10)],
            [official("Example HEP", 10, "generation_license")],
            {},
        )
        self.assertEqual(result[0]["doed_primary_category"], "generation_license")
        self.assertEqual(result[0]["doed_delivery_status"], "")

    def test_approved_alias_matches_distinct_name(self) -> None:
        aliases = {
            "Developer Name": {
                "local_project": "Developer Name",
                "doed_project": "River Name HEP",
                "confidence": "high",
                "match_basis": "reviewed",
            }
        }
        result, _, summary = overlay.build_overlay(
            [local("Developer Name", 10)],
            [official("River Name HEP", 10, "operating_record")],
            aliases,
        )
        self.assertEqual(result[0]["match_status"], "alias")
        self.assertEqual(summary["alias_local_rows"], 1)

    def test_rejected_suggestion_is_a_disposition_not_an_identity_match(self) -> None:
        official_row = official("Separate Official HEP", 40, "generation_license")
        candidate = local("Nearest Local HEP", 10)
        key = (
            "Separate Official HEP",
            "generation_license",
            "1",
            "Nearest Local HEP",
        )
        result, review, summary = overlay.build_overlay(
            [candidate],
            [official_row],
            {},
            {key: {"decision": "rejected_distinct_project"}},
        )
        self.assertEqual(result[0]["match_status"], "unmatched")
        self.assertEqual(review[0]["review_decision"], "rejected_distinct_project")
        self.assertEqual(summary["review_rows"], 1)
        self.assertEqual(summary["unreviewed_rows"], 0)
        self.assertEqual(summary["rejected_suggestion_rows"], 1)

    def test_reviewed_alias_ledger_contains_evidence_for_wave_four_matches(self) -> None:
        with overlay.DEFAULT_ALIASES.open(newline="", encoding="utf-8") as handle:
            aliases = {row["local_project"]: row for row in csv.DictReader(handle)}
        expected = {
            "Sabha Khola A HEP": "Super Sabha Khola A HPP",
            "Upper Pikhuwa HPP": "Upper Pikhuwa Khola HEP",
            "Ghunsa-Tamor HPP": "Tamor Khola",
            "Sabha Khola C HPP": "Sabha Khola C HEP (Cascade)",
        }
        for local_project, doed_project in expected.items():
            with self.subTest(local_project=local_project):
                row = aliases[local_project]
                self.assertEqual(row["doed_project"], doed_project)
                self.assertEqual(row["decision"], "approved")
                self.assertEqual(row["confidence"], "high")
                self.assertTrue(row["match_basis"])
                self.assertTrue(row["reviewed_on"])
                self.assertIn("Official DoED", row["source_note"])

    def test_rejection_ledger_is_specific_and_auditable(self) -> None:
        with overlay.DEFAULT_REVIEW_DISPOSITIONS.open(newline="", encoding="utf-8") as handle:
            rows = list(csv.DictReader(handle))
        self.assertEqual(len(rows), 31)
        keys = [overlay.disposition_key(row) for row in rows]
        self.assertEqual(len(keys), len(set(keys)))
        for row, key in zip(rows, keys):
            with self.subTest(official_project=row["official_project"]):
                self.assertTrue(all(key))
                self.assertEqual(row["decision"], "rejected_distinct_project")
                self.assertEqual(row["confidence"], "high")
                self.assertTrue(row["rationale"])
                self.assertRegex(row["reviewed_on"], r"^\d{4}-\d{2}-\d{2}$")
                self.assertIn("Official DoED", row["source_note"])


if __name__ == "__main__":
    unittest.main()
