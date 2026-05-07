#!/usr/bin/env python3
from __future__ import annotations

import io
import sys
import unittest
import textwrap

from scripts.validate_repo import validate_claim_integrity, warn


class ClaimIntegrityTests(unittest.TestCase):

    # ------------------------------------------------------------------
    # helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _make_claim_page(claim_id: str, updated: str, body: str) -> str:
        return textwrap.dedent(f"""\
        ---
        title: Test Claim
        type: claim
        created: 2026-04-14
        updated: {updated}
        claim_id: {claim_id}
        sources: []
        tags: []
        ---

        {body}
        """)

    @staticmethod
    def _make_registry(metrics: dict | None = None, claims: dict | None = None) -> dict:
        return {
            "version": 1,
            "metrics": metrics or {},
            "claims": claims or {},
        }

    @staticmethod
    def _claim_data(slug: str, claim_id: str, updated: str, body: str) -> dict:
        text = ClaimIntegrityTests._make_claim_page(claim_id, updated, body)
        return {"text": text, "claim_id": claim_id, "updated": updated}

    # ------------------------------------------------------------------
    # structural failures (always fail, regardless of tier)
    # ------------------------------------------------------------------

    def test_duplicate_claim_id_fails(self) -> None:
        registry = self._make_registry(claims={
            "C-001": {"slug": "claim-a", "tier": "core", "depends_on": []},
            "C-002": {"slug": "claim-b", "tier": "core", "depends_on": []},
        })
        claim_data = {
            "claim-a": self._claim_data("claim-a", "C-001", "2026-01-01", "body a"),
            "claim-b": self._claim_data("claim-b", "C-001", "2026-01-01", "body b"),
        }
        slugs = {"claim-a", "claim-b"}
        with self.assertRaises(SystemExit):
            validate_claim_integrity(slugs, _registry=registry, _claim_data=claim_data)

    def test_missing_governed_claim_page_fails(self) -> None:
        registry = self._make_registry(claims={
            "C-001": {"slug": "claim-missing", "tier": "core", "depends_on": []},
        })
        with self.assertRaises(SystemExit):
            validate_claim_integrity({"claim-other"}, _registry=registry, _claim_data={})

    def test_mismatched_claim_id_fails(self) -> None:
        registry = self._make_registry(claims={
            "C-001": {"slug": "claim-x", "tier": "core", "depends_on": []},
        })
        claim_data = {
            "claim-x": self._claim_data("claim-x", "C-999", "2026-01-01", "body"),
        }
        with self.assertRaises(SystemExit):
            validate_claim_integrity({"claim-x"}, _registry=registry, _claim_data=claim_data)

    def test_unknown_metric_dependency_fails(self) -> None:
        registry = self._make_registry(claims={
            "C-001": {"slug": "claim-x", "tier": "core", "depends_on": ["no_such_metric"]},
        })
        claim_data = {
            "claim-x": self._claim_data("claim-x", "C-001", "2026-01-01", "body"),
        }
        with self.assertRaises(SystemExit):
            validate_claim_integrity({"claim-x"}, _registry=registry, _claim_data=claim_data)

    def test_metric_source_slug_missing_fails(self) -> None:
        registry = self._make_registry(
            metrics={"m1": {"source_slug": "page-that-does-not-exist"}},
            claims={"C-001": {"slug": "claim-x", "tier": "core", "depends_on": ["m1"]}},
        )
        claim_data = {
            "claim-x": self._claim_data("claim-x", "C-001", "2026-01-01", "body"),
        }
        with self.assertRaises(SystemExit):
            validate_claim_integrity({"claim-x"}, _registry=registry, _claim_data=claim_data)

    def test_metric_without_source_slug_fails(self) -> None:
        registry = self._make_registry(
            metrics={"m1": {}},
            claims={"C-001": {"slug": "claim-x", "tier": "core", "depends_on": ["m1"]}},
        )
        claim_data = {
            "claim-x": self._claim_data("claim-x", "C-001", "2026-01-01", "body"),
        }
        with self.assertRaises(SystemExit):
            validate_claim_integrity({"claim-x"}, _registry=registry, _claim_data=claim_data)

    def test_metric_entry_not_dict_fails_cleanly(self) -> None:
        registry = self._make_registry(
            metrics={"m1": "not-a-mapping"},
            claims={"C-001": {"slug": "claim-x", "tier": "core", "depends_on": ["m1"]}},
        )
        claim_data = {
            "claim-x": self._claim_data("claim-x", "C-001", "2026-01-01", "body"),
        }
        with self.assertRaises(SystemExit):
            validate_claim_integrity({"claim-x"}, _registry=registry, _claim_data=claim_data)

    def test_invalid_tier_fails_structurally(self) -> None:
        registry = self._make_registry(claims={
            "C-001": {"slug": "claim-x", "tier": "cor", "depends_on": []},
        })
        claim_data = {
            "claim-x": self._claim_data("claim-x", "C-001", "2026-01-01", "body"),
        }
        with self.assertRaises(SystemExit):
            validate_claim_integrity({"claim-x"}, _registry=registry, _claim_data=claim_data)

    def test_metric_text_fields_must_be_lists(self) -> None:
        registry = self._make_registry(
            metrics={"m1": {"source_slug": "source-page-1", "canonical_text": "7.23%"}},
            claims={"C-001": {"slug": "claim-x", "tier": "core", "depends_on": ["m1"]}},
        )
        claim_data = {
            "claim-x": self._claim_data("claim-x", "C-001", "2026-01-01", "body"),
        }
        with self.assertRaises(SystemExit):
            validate_claim_integrity({"claim-x", "source-page-1"}, _registry=registry,
                                     _claim_data=claim_data)

    def test_registry_version_not_1_fails(self) -> None:
        registry = {"version": 2, "metrics": {}, "claims": {}}
        with self.assertRaises(SystemExit):
            validate_claim_integrity(set(), _registry=registry, _claim_data={})

    def test_registry_not_dict_fails(self) -> None:
        with self.assertRaises(SystemExit):
            validate_claim_integrity(set(), _registry=[], _claim_data={})  # type: ignore[arg-type]

    def test_claim_entry_not_dict_fails(self) -> None:
        registry = {"version": 1, "metrics": {}, "claims": {"C-001": "not-a-mapping"}}
        with self.assertRaises(SystemExit):
            validate_claim_integrity({"claim-x"}, _registry=registry, _claim_data={})

    # ------------------------------------------------------------------
    # content / freshness failures (core claims fail; non-core warn)
    # ------------------------------------------------------------------

    def test_missing_required_text_core_fails(self) -> None:
        registry = self._make_registry(claims={
            "C-001": {"slug": "claim-x", "tier": "core", "depends_on": [],
                      "required_text": ["MUST HAVE THIS"], "forbidden_text": []},
        })
        claim_data = {
            "claim-x": self._claim_data("claim-x", "C-001", "2026-01-01", "no such text here"),
        }
        with self.assertRaises(SystemExit):
            validate_claim_integrity({"claim-x"}, _registry=registry, _claim_data=claim_data)

    def test_forbidden_text_core_fails(self) -> None:
        registry = self._make_registry(claims={
            "C-001": {"slug": "claim-x", "tier": "core", "depends_on": [],
                      "required_text": [], "forbidden_text": ["BAD OLD NUMBER"]},
        })
        claim_data = {
            "claim-x": self._claim_data("claim-x", "C-001", "2026-01-01",
                                        "Contains BAD OLD NUMBER in prose."),
        }
        with self.assertRaises(SystemExit):
            validate_claim_integrity({"claim-x"}, _registry=registry, _claim_data=claim_data)

    def test_metric_canonical_text_is_required_for_dependents(self) -> None:
        registry = self._make_registry(
            metrics={"m1": {"source_slug": "source-page-1", "canonical_text": ["7.23%"]}},
            claims={"C-001": {"slug": "claim-x", "tier": "core", "depends_on": ["m1"]}},
        )
        claim_data = {
            "claim-x": self._claim_data("claim-x", "C-001", "2026-01-01", "body"),
        }
        with self.assertRaises(SystemExit):
            validate_claim_integrity({"claim-x", "source-page-1"}, _registry=registry,
                                     _claim_data=claim_data)

    def test_metric_deprecated_text_is_forbidden_for_dependents(self) -> None:
        registry = self._make_registry(
            metrics={"m1": {"source_slug": "source-page-1", "deprecated_text": ["4.96%"]}},
            claims={"C-001": {"slug": "claim-x", "tier": "core", "depends_on": ["m1"]}},
        )
        claim_data = {
            "claim-x": self._claim_data("claim-x", "C-001", "2026-01-01",
                                        "Old denominator was 4.96%."),
        }
        with self.assertRaises(SystemExit):
            validate_claim_integrity({"claim-x", "source-page-1"}, _registry=registry,
                                     _claim_data=claim_data)

    def test_freshness_core_fails(self) -> None:
        registry = self._make_registry(
            metrics={"m1": {"source_slug": "source-page-1"}},
            claims={
                "C-001": {"slug": "claim-x", "tier": "core",
                          "depends_on": ["m1"], "required_text": [], "forbidden_text": []},
            },
        )
        claim_data = {
            "claim-x": self._claim_data("claim-x", "C-001", "2026-01-01", "body"),
        }
        # source is newer than claim -> claim is stale
        source_dates = {"source-page-1": "2026-05-01"}
        slugs = {"claim-x", "source-page-1"}
        with self.assertRaises(SystemExit):
            validate_claim_integrity(slugs, _registry=registry, _claim_data=claim_data,
                                     _source_dates=source_dates)

    # ------------------------------------------------------------------
    # non-core claims: warn-only on content/freshness
    # ------------------------------------------------------------------

    def test_missing_required_text_non_core_warns_only(self) -> None:
        registry = self._make_registry(claims={
            "C-001": {"slug": "claim-x", "tier": "supporting", "depends_on": [],
                      "required_text": ["MUST HAVE THIS"], "forbidden_text": []},
        })
        claim_data = {
            "claim-x": self._claim_data("claim-x", "C-001", "2026-01-01", "no such text here"),
        }
        stderr = io.StringIO()
        old_stderr = sys.stderr
        sys.stderr = stderr
        try:
            validate_claim_integrity({"claim-x"}, _registry=registry, _claim_data=claim_data)
        finally:
            sys.stderr = old_stderr
        output = stderr.getvalue()
        self.assertIn("missing required text", output)
        self.assertIn("WARNING", output)

    def test_freshness_non_core_warns_only(self) -> None:
        registry = self._make_registry(
            metrics={"m1": {"source_slug": "source-page-1"}},
            claims={
                "C-001": {"slug": "claim-x", "tier": "supporting",
                          "depends_on": ["m1"], "required_text": [], "forbidden_text": []},
            },
        )
        claim_data = {
            "claim-x": self._claim_data("claim-x", "C-001", "2026-01-01", "body"),
        }
        source_dates = {"source-page-1": "2026-05-01"}
        slugs = {"claim-x", "source-page-1"}
        stderr = io.StringIO()
        old_stderr = sys.stderr
        sys.stderr = stderr
        try:
            validate_claim_integrity(slugs, _registry=registry, _claim_data=claim_data,
                                     _source_dates=source_dates)
        finally:
            sys.stderr = old_stderr
        output = stderr.getvalue()
        self.assertIn("older than", output)
        self.assertIn("WARNING", output)

    # ------------------------------------------------------------------
    # warnings that never fail
    # ------------------------------------------------------------------

    def test_unregistered_claim_page_warns(self) -> None:
        registry = self._make_registry(claims={
            "C-001": {"slug": "claim-a", "tier": "core", "depends_on": []},
        })
        claim_data = {
            "claim-a": self._claim_data("claim-a", "C-001", "2026-01-01", "body a"),
            "claim-unreg": self._claim_data("claim-unreg", "C-002", "2026-01-01", "body u"),
        }
        stderr = io.StringIO()
        old_stderr = sys.stderr
        sys.stderr = stderr
        try:
            validate_claim_integrity({"claim-a", "claim-unreg"}, _registry=registry,
                                     _claim_data=claim_data)
        finally:
            sys.stderr = old_stderr
        output = stderr.getvalue()
        self.assertIn("unregistered claim page: claim-unreg", output)

    def test_unused_metric_warns(self) -> None:
        registry = self._make_registry(
            metrics={"unused_metric": {"source_slug": "some-source"}},
            claims={"C-001": {"slug": "claim-x", "tier": "core", "depends_on": []}},
        )
        claim_data = {
            "claim-x": self._claim_data("claim-x", "C-001", "2026-01-01", "body"),
        }
        stderr = io.StringIO()
        old_stderr = sys.stderr
        sys.stderr = stderr
        try:
            validate_claim_integrity({"claim-x", "some-source"}, _registry=registry,
                                     _claim_data=claim_data)
        finally:
            sys.stderr = old_stderr
        output = stderr.getvalue()
        self.assertIn("unused by any claim", output)

    # ------------------------------------------------------------------
    # dash normalization
    # ------------------------------------------------------------------

    def test_dash_normalization_matches_en_dash(self) -> None:
        registry = self._make_registry(claims={
            "C-001": {"slug": "claim-x", "tier": "core", "depends_on": [],
                      "required_text": ["5.70-6.20"], "forbidden_text": ["4.99-5.55"]},
        })
        # Page body uses en-dash between numbers
        claim_data = {
            "claim-x": self._claim_data("claim-x", "C-001", "2026-01-01",
                                        "Tariff band is 5.70\u20136.20 NPR/kWh. Old was 4.99\u20135.55."),
        }
        # Should pass because dashes are normalized: required text "5.70-6.20" contains
        # hyphen, page has "5.70–6.20" with en-dash, normalize makes them match.
        # But forbidden_text "4.99-5.55" matches too -> should fail!
        with self.assertRaises(SystemExit):
            validate_claim_integrity({"claim-x"}, _registry=registry, _claim_data=claim_data)

    def test_dash_normalization_required_text_passes(self) -> None:
        registry = self._make_registry(claims={
            "C-001": {"slug": "claim-x", "tier": "core", "depends_on": [],
                      "required_text": ["5.70-6.20"], "forbidden_text": []},
        })
        claim_data = {
            "claim-x": self._claim_data("claim-x", "C-001", "2026-01-01",
                                        "Tariff band is 5.70\u20136.20 NPR/kWh."),
        }
        # Should not raise — dash normalization makes both match
        validate_claim_integrity({"claim-x"}, _registry=registry, _claim_data=claim_data)

    # ------------------------------------------------------------------
    # C-013 entry-only: no content checks, just structural
    # ------------------------------------------------------------------

    def test_entry_only_claim_passes_structural(self) -> None:
        registry = self._make_registry(claims={
            "C-013": {"slug": "claim-s", "tier": "core", "depends_on": []},
        })
        claim_data = {
            "claim-s": self._claim_data("claim-s", "C-013", "2026-01-01", "sediment body"),
        }
        # Should not raise
        validate_claim_integrity({"claim-s"}, _registry=registry, _claim_data=claim_data)

    # ------------------------------------------------------------------
    # freshness: claim IS newer than source -> passes
    # ------------------------------------------------------------------

    def test_freshness_passes_when_claim_is_newer(self) -> None:
        registry = self._make_registry(
            metrics={"m1": {"source_slug": "source-page-1"}},
            claims={
                "C-001": {"slug": "claim-x", "tier": "core",
                          "depends_on": ["m1"], "required_text": [], "forbidden_text": []},
            },
        )
        claim_data = {
            "claim-x": self._claim_data("claim-x", "C-001", "2026-06-01", "body"),
        }
        source_dates = {"source-page-1": "2026-05-01"}
        slugs = {"claim-x", "source-page-1"}
        # Claim is newer — should not raise
        validate_claim_integrity(slugs, _registry=registry, _claim_data=claim_data,
                                 _source_dates=source_dates)

    # ------------------------------------------------------------------
    # registered claim with no issues passes cleanly
    # ------------------------------------------------------------------

    def test_clean_registered_claim_passes(self) -> None:
        registry = self._make_registry(
            metrics={"m1": {"source_slug": "source-page-1"}},
            claims={
                "C-001": {"slug": "claim-x", "tier": "core", "depends_on": ["m1"],
                          "required_text": ["7.23%"], "forbidden_text": ["4.96%"]},
            },
        )
        claim_data = {
            "claim-x": self._claim_data("claim-x", "C-001", "2026-06-01",
                                        "Grid electricity is 7.23% of final energy."),
        }
        source_dates = {"source-page-1": "2026-01-01"}
        slugs = {"claim-x", "source-page-1"}
        # All good
        validate_claim_integrity(slugs, _registry=registry, _claim_data=claim_data,
                                 _source_dates=source_dates)


if __name__ == "__main__":
    unittest.main()
