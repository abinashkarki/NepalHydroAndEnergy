from __future__ import annotations

import csv
import io
import json
import math
import re
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

from scripts import build_internal_dashboard as dashboard


def csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


class InternalDashboardUnitTests(unittest.TestCase):
    def test_clean_scalar_preserves_zero_but_normalizes_blank_values(self) -> None:
        self.assertIsNone(dashboard.clean_scalar(None))
        self.assertIsNone(dashboard.clean_scalar("  "))
        self.assertEqual(dashboard.clean_scalar("  operating "), "operating")
        self.assertEqual(dashboard.clean_scalar(0), 0)

    def test_spec_completeness_recomputes_sections_and_tier(self) -> None:
        row = {field: "" for fields in dashboard.SPEC_SECTIONS.values() for field in fields}
        row["gross_head_m"] = "100"
        row["developer"] = "Example Developer"

        result = dashboard.spec_completeness(row)

        expected_total = sum(len(fields) for fields in dashboard.SPEC_SECTIONS.values())
        self.assertEqual(result["filled"], 2)
        self.assertEqual(result["total"], expected_total)
        self.assertEqual(result["sections"]["engineering"]["filled"], 1)
        self.assertEqual(result["sections"]["governance"]["filled"], 1)
        self.assertEqual(result["tier"], "thin")

    def test_completeness_tier_boundaries_are_explicit(self) -> None:
        self.assertEqual(dashboard.tier_for(0), "empty")
        self.assertEqual(dashboard.tier_for(0.1), "thin")
        self.assertEqual(dashboard.tier_for(24.9), "thin")
        self.assertEqual(dashboard.tier_for(25), "moderate")
        self.assertEqual(dashboard.tier_for(49.9), "moderate")
        self.assertEqual(dashboard.tier_for(50), "rich")

    def test_normalized_queue_has_stable_ids_and_explicit_nulls(self) -> None:
        rows = [
            {"project": " Alpha ", "review_status": "unreviewed"},
            {"project": "Beta", "review_status": ""},
        ]

        first = dashboard.normalized_queue(rows, "identity")
        second = dashboard.normalized_queue(rows, "identity")

        self.assertEqual(first, second)
        self.assertTrue(all(re.fullmatch(r"identity-[0-9a-f]{12}", row["queue_id"]) for row in first))
        self.assertEqual(first[0]["project"], "Alpha")
        self.assertIsNone(first[1]["review_status"])
        self.assertTrue(all(row["queue_type"] == "identity" for row in first))


class InternalDashboardGeneratedContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.payload = dashboard.build_payload()

    def test_payload_is_deterministic_and_strict_json(self) -> None:
        first = dashboard.render(self.payload)
        second = dashboard.render(dashboard.build_payload())

        self.assertEqual(first, second)
        json.dumps(self.payload, allow_nan=False)

    def test_top_level_contract_and_inputs_are_stable(self) -> None:
        self.assertEqual(self.payload["schema_version"], 1)
        self.assertEqual(
            set(self.payload),
            {
                "schema_version",
                "title",
                "data_as_of",
                "scope",
                "inputs",
                "overview",
                "coverage",
                "monitoring",
                "reconciliation",
                "sources",
                "contracts",
            },
        )
        expected_inputs = [
            {
                "path": path.relative_to(dashboard.ROOT).as_posix(),
                "sha256": dashboard.sha256(path),
            }
            for path in dashboard.REQUIRED_INPUTS
        ]
        self.assertEqual(self.payload["inputs"], expected_inputs)
        self.assertTrue(all((dashboard.ROOT / item["path"]).is_file() for item in self.payload["inputs"]))
        self.assertTrue(all(re.fullmatch(r"[0-9a-f]{64}", item["sha256"]) for item in self.payload["inputs"]))
        self.assertRegex(self.payload["data_as_of"], dashboard.DATE_RE)

    def test_summary_counts_reconcile_to_authoritative_inputs(self) -> None:
        specs = csv_rows(dashboard.SPECS)
        events = csv_rows(dashboard.EVENTS)
        blockers = csv_rows(dashboard.BLOCKERS)
        corridors = csv_rows(dashboard.CORRIDORS)
        doed_review = csv_rows(dashboard.DOED_REVIEW)
        doed_missing_operating = csv_rows(dashboard.DOED_MISSING_OPERATING)
        hydromap_review = csv_rows(dashboard.HYDROMAP_REVIEW)
        capacity_conflicts = csv_rows(dashboard.CAPACITY_CONFLICTS)
        capacity_decisions = csv_rows(dashboard.CAPACITY_DECISIONS)
        resolved_decisions = {"publish_dual_value", "retain_legacy_below_materiality"}
        resolved_names = {
            row["local_project"] for row in capacity_decisions
            if row["decision"] in resolved_decisions
        }
        unresolved_capacity_conflicts = [
            row for row in capacity_conflicts if row["local_name"] not in resolved_names
        ]
        overview = self.payload["overview"]

        self.assertEqual(overview["specifications"]["projects"], len(specs))
        self.assertEqual(overview["monitoring"]["events"], len(events))
        self.assertEqual(overview["monitoring"]["blockers"], len(blockers))
        self.assertEqual(overview["monitoring"]["corridor_segments"], len(corridors))
        self.assertEqual(overview["registry"]["review_rows"], len(doed_review))
        rejected_suggestions = [
            row for row in doed_review
            if row["review_decision"].startswith("rejected_")
        ]
        self.assertEqual(
            overview["registry"]["identity_review_rows"],
            len(doed_review) - len(doed_missing_operating) - len(rejected_suggestions),
        )
        self.assertEqual(
            overview["registry"]["reviewed_rejected_suggestions"],
            len(rejected_suggestions),
        )
        self.assertEqual(overview["registry"]["missing_operating_local_rows"], len(doed_missing_operating))
        self.assertEqual(overview["benchmark"]["active_review_rows"], len(hydromap_review))
        self.assertEqual(overview["benchmark"]["capacity_conflict_rows"], len(unresolved_capacity_conflicts))
        self.assertEqual(overview["benchmark"]["capacity_conflict_rows_total"], len(capacity_conflicts))
        self.assertEqual(
            overview["benchmark"]["capacity_conflict_rows_resolved"],
            len(capacity_conflicts) - len(unresolved_capacity_conflicts),
        )
        self.assertEqual(len(self.payload["coverage"]["projects"]), len(specs))

    def test_project_and_queue_identifiers_are_unique_and_nonblank(self) -> None:
        coverage = self.payload["coverage"]["projects"]
        monitoring = self.payload["monitoring"]["projects"]
        coverage_slugs = [row["slug"] for row in coverage]
        monitoring_slugs = [row["slug"] for row in monitoring]

        self.assertEqual(len(coverage_slugs), len(set(coverage_slugs)))
        self.assertEqual(len(monitoring_slugs), len(set(monitoring_slugs)))
        self.assertTrue(all(coverage_slugs))
        self.assertTrue(all(monitoring_slugs))

        for queue_name in ("doed_review", "doed_missing_operating", "hydromap_active_review", "capacity_conflicts"):
            rows = self.payload["reconciliation"][queue_name]
            queue_ids = [row["queue_id"] for row in rows]
            self.assertEqual(len(queue_ids), len(set(queue_ids)), queue_name)
            self.assertTrue(all(queue_ids), queue_name)

        flags = self.payload["reconciliation"]["open_flags"]
        flag_ids = [row["id"] for row in flags]
        self.assertEqual(len(flag_ids), len(set(flag_ids)))
        self.assertTrue(all(flag_ids))

    def test_monitoring_foreign_keys_and_nested_counts_reconcile(self) -> None:
        pages = json.loads(dashboard.PAGE_META.read_text(encoding="utf-8"))["pages"]
        page_slugs = {row["slug"] for row in pages}
        expected_monitored = {
            row["project_slug"] for row in csv_rows(dashboard.EVENTS)
        } | {
            row["project_slug"] for row in csv_rows(dashboard.BLOCKERS)
        } | {
            row["slug"] for row in csv_rows(dashboard.CORRIDORS)
        }

        projects = self.payload["monitoring"]["projects"]
        self.assertEqual({row["slug"] for row in projects}, expected_monitored)
        self.assertTrue(expected_monitored <= page_slugs)
        for project in projects:
            self.assertEqual(project["active_blocker_count"], sum(
                blocker.get("status") == "active" for blocker in project["blockers"]
            ))
            if project["events"]:
                event_dates = [row["event_date"] for row in project["events"]]
                self.assertEqual(event_dates, sorted(event_dates, reverse=True))
            if project["last_verified"]:
                self.assertRegex(project["last_verified"], dashboard.DATE_RE)

    def test_completeness_summary_is_derived_from_current_specs(self) -> None:
        projects = self.payload["coverage"]["projects"]
        expected_counts: dict[str, int] = {}
        for project in projects:
            tier = project["completeness"]["tier"]
            expected_counts[tier] = expected_counts.get(tier, 0) + 1
            pct = project["completeness"]["pct"]
            self.assertGreaterEqual(pct, 0)
            self.assertLessEqual(pct, 100)
            self.assertTrue(math.isfinite(pct))

        self.assertEqual(self.payload["overview"]["specifications"]["tier_counts"], dict(sorted(expected_counts.items())))
        expected_average = round(sum(row["completeness"]["pct"] for row in projects) / len(projects), 1)
        self.assertEqual(self.payload["overview"]["specifications"]["average_completeness_pct"], expected_average)

    def test_capacity_conflict_differences_reconcile(self) -> None:
        for row in self.payload["reconciliation"]["capacity_conflicts"]:
            local = float(row["local_capacity_mw"])
            external = float(row["external_capacity_mw"])
            difference = float(row["absolute_difference_mw"])
            self.assertAlmostEqual(difference, abs(local - external), places=3)

    def test_source_records_reconcile_and_links_are_safe_shapes(self) -> None:
        records = self.payload["sources"]["records"]
        summary = self.payload["overview"]["corpus"]

        self.assertEqual(len(records), len(list(dashboard.SOURCE_DIR.glob("*.md"))))
        self.assertEqual(summary["source_pages"], len(records))
        self.assertEqual(summary["sources_with_url"], sum(row["has_url"] for row in records))
        self.assertEqual(summary["sources_with_date"], sum(row["has_source_date"] for row in records))
        for row in records:
            self.assertTrue(row["slug"])
            self.assertEqual(row["wiki_url"], f"/wiki/explorer/?page={row['slug']}")
            if row["source_url"]:
                self.assertTrue(
                    row["source_url"].startswith(("https://", "http://"))
                    or row["source_url"].lower().endswith(".pdf"),
                    f"unexpected source_url shape for {row['slug']}: {row['source_url']!r}",
                )

    def test_cli_check_accepts_current_output_and_rejects_missing_or_stale_output(self) -> None:
        with tempfile.TemporaryDirectory(prefix="dashboard-test-", dir=dashboard.ROOT) as temp_dir:
            output = Path(temp_dir) / "control-room.json"

            with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                self.assertEqual(dashboard.main(["--check", "--output", str(output)]), 1)
                self.assertEqual(dashboard.main(["--output", str(output)]), 0)
                self.assertEqual(dashboard.main(["--check", "--output", str(output)]), 0)

            output.write_text(output.read_text(encoding="utf-8") + " ", encoding="utf-8")
            with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                self.assertEqual(dashboard.main(["--check", "--output", str(output)]), 1)


if __name__ == "__main__":
    unittest.main()
