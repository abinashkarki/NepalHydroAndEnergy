from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from scripts import benchmark_hydromap_coverage as benchmark


def external(
    name: str,
    capacity: str,
    category: str = "construction",
    river: str = "Test River",
    license_no: str = "1",
) -> dict:
    return {
        "name": name,
        "capacity": capacity,
        "category": category,
        "river": river,
        "licenseNo": license_no,
        "lat1": "27.0",
        "lat2": "27.1",
        "lon1": "85.0",
        "lon2": "85.1",
    }


def local(name: str, capacity: float, license_type: str = "Survey", river: str = "Test River") -> dict:
    return {
        "project": name,
        "capacity_mw": capacity,
        "license_type": license_type,
        "river": river,
        "raw_lat": 27.05,
        "raw_lon": 85.05,
    }


class HydroMapBenchmarkTests(unittest.TestCase):
    def test_canonical_name_is_conservative(self) -> None:
        self.assertEqual(
            benchmark.canonical_project_name("Upper Kabeli-2 HEP"),
            "upper kabeli 2",
        )
        self.assertEqual(
            benchmark.canonical_project_name("Upper Kabeli-2 Hydropower Project"),
            "upper kabeli 2",
        )
        self.assertNotEqual(
            benchmark.canonical_project_name("Upper Kabeli-2 HEP"),
            benchmark.canonical_project_name("Upper Kabeli HEP"),
        )
        self.assertIn("cascade", benchmark.canonical_project_name("Kabeli Cascade HEP"))

    def test_energy_type_separates_embedded_non_hydro(self) -> None:
        self.assertEqual(benchmark.classify_energy_type({"name": "Grid Solar PV", "river": ""}), "solar")
        self.assertEqual(benchmark.classify_energy_type({"name": "Mustang Wind Power", "river": ""}), "wind")
        self.assertEqual(benchmark.classify_energy_type({"name": "Upper Arun HEP", "river": "Arun"}), "hydro")

    def test_unique_exact_name_matches_even_when_capacity_conflicts(self) -> None:
        result = benchmark.match_hydropower(
            [local("Phukot Karnali", 426)],
            [external("Phukot Karnali HEP", "480", river="Karnali")],
        )
        self.assertEqual(result["matches"], [(0, 0)])
        self.assertEqual(result["ambiguous"], [])

    def test_duplicate_name_is_disambiguated_only_by_capacity(self) -> None:
        result = benchmark.match_hydropower(
            [local("Seti Khola HPP", 25)],
            [external("Seti Khola HEP", "3.5"), external("Seti Khola HPP", "25")],
        )
        self.assertEqual(result["matches"], [(0, 1)])

    def test_duplicate_name_with_same_capacity_stays_ambiguous(self) -> None:
        result = benchmark.match_hydropower(
            [local("Idi Khola SHP", 0.975)],
            [
                external("Idi Khola SHP", "0.975", category="operation"),
                external("Idi Khola SHP", "0.975", category="construction"),
            ],
        )
        self.assertEqual(result["matches"], [])
        self.assertEqual(result["ambiguous"], [(0, [0, 1])])

    def test_best_suggestion_never_changes_match_state(self) -> None:
        target = external("Kaligandaki Koban", "400", river="Kali Gandaki")
        suggestion = benchmark.best_suggestion(
            target,
            [local("Kali Gandaki-Kowan", 400, river="Kali Gandaki")],
        )
        self.assertIsNotNone(suggestion)
        self.assertGreater(suggestion["combined_similarity"], 0.8)
        result = benchmark.match_hydropower(
            [local("Kali Gandaki-Kowan", 400, river="Kali Gandaki")],
            [target],
        )
        self.assertEqual(result["matches"], [])

    def test_spec_weighting_can_prefer_river_and_capacity_alias(self) -> None:
        target = {"name": "sahas urja", "river": "Solu Khola", "capacity": 86}
        suggestion = benchmark.best_suggestion(
            target,
            [
                local("Sabha A Hydropower Project", 9, river="Sabha Khola"),
                local("Solu Khola (Dudha Koshi)", 86, river="Solu Khola"),
            ],
            weights=(0.45, 0.30, 0.25),
        )
        self.assertEqual(suggestion["local"]["project"], "Solu Khola (Dudha Koshi)")

    def test_build_benchmark_keeps_license_and_delivery_categories_separate(self) -> None:
        payload = {
            "total": 1,
            "last_updated": "2026-07-06T00:00:00Z",
            "last_updated_display": "2026-07-02",
            "projects": [external("Example HEP", "10", category="operation")],
        }
        summary, tables = benchmark.build_benchmark(
            payload,
            [local("Example HPP", 10, license_type="Generation")],
            [],
            [],
            {"fixture": True},
            "2026-07-11T00:00:00+00:00",
        )
        self.assertEqual(summary["matching"]["status_crosswalk"], {"Generation -> operation": 1})
        self.assertEqual(summary["local"]["hydro"]["license_types"]["Generation"]["rows"], 1)
        self.assertEqual(summary["external"]["hydro"]["categories"]["operation"]["rows"], 1)
        self.assertEqual(tables[benchmark.ACTIVE_REVIEW_NAME], [])

    def test_output_paths_cannot_overlap_inputs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "input.json"
            path.write_text("{}", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "Refusing to overwrite"):
                benchmark.validate_output_paths([path], [path])

    def test_percentile_interpolates_even_length_values(self) -> None:
        values = [0.0, 10.0, 20.0, 30.0]
        self.assertEqual(benchmark.percentile(values, 0.5), 15.0)
        self.assertAlmostEqual(benchmark.percentile(values, 0.9), 27.0)
        with self.assertRaisesRegex(ValueError, "between 0 and 1"):
            benchmark.percentile(values, 1.1)


if __name__ == "__main__":
    unittest.main()
