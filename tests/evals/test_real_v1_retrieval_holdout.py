from __future__ import annotations

import hashlib
import json
import unittest
from collections import Counter
from datetime import datetime
from pathlib import Path

from evals.retrieval_holdout.scorer import evaluate, validate_query_set


ROOT = Path(__file__).resolve().parents[2]
HOLDOUT = ROOT / "evals" / "retrieval_holdout" / "real_v1"
WIKI_PAGES = ROOT / "wiki" / "pages"


def load_json(name: str) -> dict:
    return json.loads((HOLDOUT / name).read_text(encoding="utf-8"))


class RealV1RetrievalHoldoutTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.query_path = HOLDOUT / "query-set.json"
        cls.queries = load_json("query-set.json")
        cls.ranked_run = load_json("ranked-run.json")
        cls.report = load_json("scored-report.json")

    def test_frozen_query_set_has_exact_persona_balance(self) -> None:
        validate_query_set(self.queries)
        self.assertEqual(self.queries["status"], "frozen")
        self.assertEqual(len(self.queries["queries"]), 30)
        self.assertEqual(len({query["id"] for query in self.queries["queries"]}), 30)
        self.assertEqual(len({query["query"] for query in self.queries["queries"]}), 30)

        personas = Counter(
            query["notes"].split(";", 1)[0].removeprefix("persona=")
            for query in self.queries["queries"]
        )
        self.assertEqual(personas, {f"P{index}": 5 for index in range(1, 7)})

    def test_judgments_resolve_to_real_pages_and_have_rationales(self) -> None:
        for query in self.queries["queries"]:
            self.assertTrue(
                any(judgment["relevance"] >= 2 for judgment in query["judgments"]),
                query["id"],
            )
            for judgment in query["judgments"]:
                matches = list(WIKI_PAGES.glob(f"*/{judgment['doc_id']}.md"))
                self.assertEqual(matches and len(matches), 1, (query["id"], judgment["doc_id"]))
                self.assertTrue(judgment.get("rationale", "").strip(), (query["id"], judgment["doc_id"]))

    def test_frozen_checksum_matches_query_set_bytes(self) -> None:
        checksum_line = (HOLDOUT / "CHECKSUMS.sha256").read_text(encoding="utf-8").splitlines()[0]
        expected, filename = checksum_line.split(maxsplit=1)
        self.assertEqual(filename, "query-set.json")
        actual = hashlib.sha256(self.query_path.read_bytes()).hexdigest()
        self.assertEqual(actual, expected)

    def test_run_postdates_freeze_and_covers_every_query_once(self) -> None:
        frozen_at = datetime.fromisoformat(self.queries["provenance"]["frozen_at"].replace("Z", "+00:00"))
        generated_at = datetime.fromisoformat(self.ranked_run["generated_at"])
        self.assertGreater(generated_at, frozen_at)
        self.assertEqual(self.ranked_run["query_set_id"], self.queries["set_id"])
        result_ids = [result["query_id"] for result in self.ranked_run["results"]]
        self.assertEqual(len(result_ids), 30)
        self.assertEqual(set(result_ids), {query["id"] for query in self.queries["queries"]})

    def test_recorded_report_is_reproducible(self) -> None:
        reproduced = evaluate(self.queries, self.ranked_run, ks=(1, 3, 5, 10), primary_k=10)
        self.assertEqual(reproduced, self.report)
        self.assertEqual(
            self.report["overall"],
            {
                "queries": 30,
                "mrr": 0.740171,
                "hit@1": 0.633333,
                "ndcg@1": 0.538095,
                "hit@3": 0.8,
                "ndcg@3": 0.505938,
                "hit@5": 0.866667,
                "ndcg@5": 0.54555,
                "hit@10": 0.966667,
                "ndcg@10": 0.62371,
                "failure_categories": {"relevant_below_primary_k": 1, "success": 29},
            },
        )
        self.assertEqual(
            self.report["failures"],
            [
                {
                    "query_id": "real-v1-15",
                    "query_type": "multi_constraint",
                    "category": "relevant_below_primary_k",
                    "first_relevant_rank": 26,
                    "returned": 30,
                }
            ],
        )


if __name__ == "__main__":
    unittest.main()
