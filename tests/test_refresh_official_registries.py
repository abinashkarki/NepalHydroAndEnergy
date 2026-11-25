from __future__ import annotations

import io
import unittest
from contextlib import redirect_stdout
from unittest import mock

from scripts import refresh_official_registries as rr


class RefreshOrchestratorTests(unittest.TestCase):
    def test_canonical_plan_is_valid(self) -> None:
        self.assertEqual(rr.validate_plan(), [])

    def test_canonical_order(self) -> None:
        names = [s.name for s in rr.STEPS]
        expected_order = [
            "doed-hydro-scrape", "doed-nonhydro-scrape", "doed-status-overlay", "enrich-solar-specs",
            "canonical-geography", "substation-links", "energy-infrastructure-layers", "siting-readiness",
            "dataset-catalog", "hydro-completeness-report", "solar-completeness-report",
        ]
        positions = [names.index(n) for n in expected_order]
        self.assertEqual(positions, sorted(positions))

    def test_offline_plan_excludes_network_steps(self) -> None:
        offline = rr.plan(fetch_official=False)
        self.assertFalse(any(s.fetch for s in offline))
        self.assertNotIn("doed-hydro-scrape", [s.name for s in offline])
        full = rr.plan(fetch_official=True)
        self.assertEqual([s.name for s in full], [s.name for s in rr.STEPS])
        for step in full:
            if step.name.endswith("scrape"):
                self.assertIn("--timeout", step.args)
                self.assertEqual(step.args[step.args.index("--timeout") + 1], "30")

    def test_validation_catches_bad_plans(self) -> None:
        a = rr.Step("a", "scripts/build_dataset_catalog.py", after=("b",))
        b = rr.Step("b", "scripts/build_dataset_catalog.py")
        self.assertIn("a: dependency b must run first", rr.validate_plan([a, b]))
        self.assertIn("a: unknown dependency b", rr.validate_plan([a]))
        missing = rr.Step("m", "scripts/does_not_exist.py")
        self.assertIn("m: missing script scripts/does_not_exist.py", rr.validate_plan([missing]))
        self.assertIn("duplicate step names", rr.validate_plan([b, b]))

    def test_dry_run_is_default_and_executes_nothing(self) -> None:
        with mock.patch.object(rr.subprocess, "run") as run, redirect_stdout(io.StringIO()) as out:
            self.assertEqual(rr.main([]), 0)
        run.assert_not_called()
        self.assertIn("Dry run: nothing executed", out.getvalue())

    def test_diff_summary(self) -> None:
        lines = rr.diff_summary({"x.csv": (10, 50.0), "gone.csv": (1, 1.0)}, {"x.csv": (12, 55.0), "new.csv": (3, 9.0)})
        self.assertIn("  ~ x.csv: rows 10 -> 12 (+2), filled 50.0% -> 55.0%", lines)
        self.assertTrue(any(line.startswith("  + new.csv") for line in lines))
        self.assertTrue(any(line.startswith("  - gone.csv") for line in lines))
        self.assertEqual(rr.diff_summary({"x": (1, 1.0)}, {"x": (1, 1.0)}), [])


if __name__ == "__main__":
    unittest.main()
