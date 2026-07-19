from __future__ import annotations

import copy
import json
import math
import unittest
from pathlib import Path

from evals.retrieval_holdout.scorer import EvaluationError, evaluate, validate_query_set


ROOT = Path(__file__).resolve().parents[2]
PACKAGE = ROOT / "evals" / "retrieval_holdout"


def load_json(name: str) -> dict:
    return json.loads((PACKAGE / name).read_text(encoding="utf-8"))


class RetrievalHoldoutTests(unittest.TestCase):
    def setUp(self) -> None:
        self.queries = load_json("synthetic_queries.json")
        self.run = load_json("synthetic_run.json")

    def test_synthetic_report_is_deterministic(self) -> None:
        first = evaluate(self.queries, self.run)
        second = evaluate(self.queries, self.run)
        self.assertEqual(first, second)
        self.assertEqual(first["overall"]["queries"], 4)
        self.assertEqual(first["overall"]["mrr"], 0.375)
        self.assertEqual(first["overall"]["hit@1"], 0.25)
        self.assertEqual(first["overall"]["hit@3"], 0.5)
        self.assertEqual(
            first["overall"]["failure_categories"],
            {"missing_query_results": 1, "no_results": 1, "success": 2},
        )
        self.assertEqual(set(first["by_query_type"]), {"comparative", "conceptual", "exact_entity", "source_seeking"})

    def test_ndcg_uses_graded_gain_and_log_discount(self) -> None:
        report = evaluate(self.queries, self.run, ks=(1, 3))
        conceptual = next(row for row in report["queries"] if row["query_id"] == "syn-02")
        actual_dcg = 7 / math.log2(3) + 1 / math.log2(4)
        ideal_dcg = 7 / math.log2(2) + 1 / math.log2(3)
        self.assertEqual(conceptual["metrics"]["hit@1"], 0.0)
        self.assertEqual(conceptual["metrics"]["hit@3"], 1.0)
        self.assertEqual(conceptual["metrics"]["mrr"], 0.5)
        self.assertAlmostEqual(conceptual["metrics"]["ndcg@3"], round(actual_dcg / ideal_dcg, 6))

    def test_failure_categories_are_exclusive_and_bounded_by_primary_k(self) -> None:
        run = copy.deepcopy(self.run)
        syn_02 = next(item for item in run["results"] if item["query_id"] == "syn-02")
        report = evaluate(self.queries, run, primary_k=1)
        by_id = {row["query_id"]: row for row in report["queries"]}
        self.assertEqual(by_id["syn-02"]["failure_category"], "relevant_below_primary_k")

        syn_02["ranked_results"] = [{"doc_id": "synthetic-decoy"}]
        report = evaluate(self.queries, run, primary_k=1)
        by_id = {row["query_id"]: row for row in report["queries"]}
        self.assertEqual(by_id["syn-02"]["failure_category"], "no_relevant_retrieved")

    def test_unjudged_documents_are_zero_gain_and_reported(self) -> None:
        report = evaluate(self.queries, self.run, primary_k=3)
        exact = next(row for row in report["queries"] if row["query_id"] == "syn-01")
        expected = 7 / (7 + 1 / math.log2(3))
        self.assertEqual(exact["unjudged_in_primary_k"], 1)
        self.assertAlmostEqual(exact["metrics"]["ndcg@3"], round(expected, 6))

    def test_template_has_exactly_30_unseen_slots_and_is_not_scoreable(self) -> None:
        template = load_json("holdout_template_30.json")
        self.assertEqual(len(template["queries"]), 30)
        self.assertEqual(len({query["id"] for query in template["queries"]}), 30)
        self.assertTrue(all(query["query"] is None for query in template["queries"]))
        with self.assertRaisesRegex(EvaluationError, "template query sets cannot be scored"):
            validate_query_set(template)

    def test_real_holdout_requires_pre_execution_freeze(self) -> None:
        queries = copy.deepcopy(self.queries)
        queries["purpose"] = "real_holdout"
        queries["status"] = "frozen"
        queries["provenance"]["frozen_at"] = None
        with self.assertRaisesRegex(EvaluationError, "frozen query sets require"):
            validate_query_set(queries)

        queries["provenance"]["frozen_at"] = "2026-06-20T00:00:00Z"
        queries["provenance"]["system_results_inspected_during_judging"] = True
        with self.assertRaisesRegex(EvaluationError, "must not inspect"):
            validate_query_set(queries)

    def test_duplicate_ranked_documents_are_rejected(self) -> None:
        run = copy.deepcopy(self.run)
        run["results"][0]["ranked_results"].append({"doc_id": "synthetic-blue-reservoir"})
        with self.assertRaisesRegex(EvaluationError, "ranked doc_ids must be unique"):
            evaluate(self.queries, run)

    def test_run_must_reference_matching_query_set(self) -> None:
        run = copy.deepcopy(self.run)
        run["query_set_id"] = "wrong-set"
        with self.assertRaisesRegex(EvaluationError, "does not match"):
            evaluate(self.queries, run)


if __name__ == "__main__":
    unittest.main()
