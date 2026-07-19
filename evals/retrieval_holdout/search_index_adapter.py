#!/usr/bin/env python3
"""Read-only adapter that records the existing Explorer search rankings.

The adapter never changes judgments or indexes. Freeze and review a query set
before running this command. The scorer remains independent of this adapter.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .scorer import EvaluationError, validate_query_set


ROOT = Path(__file__).resolve().parents[2]
EXISTING_EVALUATOR = ROOT / "scripts" / "evaluate_search_benchmark.py"


def _load_existing_search_module() -> Any:
    spec = importlib.util.spec_from_file_location("_nepal_energy_existing_search", EXISTING_EVALUATOR)
    if spec is None or spec.loader is None:
        raise EvaluationError(f"cannot load existing search adapter from {EXISTING_EVALUATOR}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def record_run(
    query_set: dict[str, Any],
    *,
    limit: int = 30,
    run_id: str,
    generated_at: str,
) -> dict[str, Any]:
    """Execute the current read-only index path and return a ranked-run artifact."""
    validate_query_set(query_set)
    if query_set.get("purpose") == "real_holdout" and query_set.get("status") != "frozen":
        raise EvaluationError("a real holdout must be frozen before search execution")
    module = _load_existing_search_module()
    search, facts = module.load_indexes()
    recorded = []
    for query in query_set["queries"]:
        lexical = search.seek(query["query"], limit=limit)
        fact_results = facts.seek(query["query"], limit=8) if facts else []
        merged = module.merge_fact_results(fact_results, lexical)[:limit]
        recorded.append(
            {
                "query_id": query["id"],
                "ranked_results": [
                    {
                        "doc_id": result.slug,
                        "score": round(float(result.score), 8),
                        "title": result.title,
                    }
                    for result in merged
                    if result.slug
                ],
            }
        )
    return {
        "schema_version": "retrieval-run.v1",
        "artifact_type": "ranked_run",
        "query_set_id": query_set["set_id"],
        "run_id": run_id,
        "generated_at": generated_at,
        "system": {
            "name": "existing-explorer-static-search",
            "version": "scripts/evaluate_search_benchmark.py",
            "index_version": search.version,
            "notes": "Read-only adapter; lexical and fact results are merged by the existing evaluator.",
        },
        "results": recorded,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--queries", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--limit", type=int, default=30)
    parser.add_argument(
        "--generated-at",
        default=None,
        help="ISO timestamp; defaults to current UTC time. Pass explicitly for reproducible fixtures.",
    )
    args = parser.parse_args(argv)
    if args.limit <= 0:
        parser.error("--limit must be positive")
    try:
        query_set = json.loads(args.queries.read_text(encoding="utf-8"))
        generated_at = args.generated_at or datetime.now(timezone.utc).isoformat()
        run = record_run(query_set, limit=args.limit, run_id=args.run_id, generated_at=generated_at)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(run, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    except (OSError, json.JSONDecodeError, EvaluationError) as exc:
        parser.error(str(exc))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
