#!/usr/bin/env python3
"""Score frozen relevance judgments against pre-recorded ranked results.

This module is deliberately search-implementation agnostic. It reads two JSON
artifacts, validates their v1 contract, and computes metrics without executing
or importing a retrieval system.
"""
from __future__ import annotations

import argparse
import json
import math
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable


QUERY_SCHEMA_VERSION = "retrieval-holdout.v1"
RUN_SCHEMA_VERSION = "retrieval-run.v1"
DEFAULT_KS = (1, 3, 5, 10)
ALLOWED_QUERY_TYPES = {
    "exact_entity",
    "attribute_lookup",
    "conceptual",
    "source_seeking",
    "comparative",
    "multi_constraint",
    "other",
}


class EvaluationError(ValueError):
    """Raised when an evaluation artifact violates the frozen v1 contract."""


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise EvaluationError(message)


def _unique_strings(values: Iterable[str], label: str) -> None:
    values = list(values)
    _require(len(values) == len(set(values)), f"{label} must be unique")


def validate_query_set(query_set: dict[str, Any], *, require_frozen: bool = True) -> None:
    _require(query_set.get("schema_version") == QUERY_SCHEMA_VERSION, "unsupported query-set schema_version")
    _require(query_set.get("artifact_type") == "query_set", "query set artifact_type must be 'query_set'")
    _require(isinstance(query_set.get("set_id"), str) and query_set["set_id"], "query set requires set_id")
    _require(query_set.get("purpose") in {"synthetic_example", "real_holdout"}, "invalid query-set purpose")
    _require(query_set.get("status") in {"example", "template", "frozen"}, "invalid query-set status")
    provenance = query_set.get("provenance")
    _require(isinstance(provenance, dict), "query set requires provenance")
    for key in (
        "created_by",
        "created_at",
        "judgments_established_before_system_execution",
        "system_results_inspected_during_judging",
    ):
        _require(key in provenance, f"query-set provenance missing {key}")

    queries = query_set.get("queries")
    _require(isinstance(queries, list), "query set queries must be a list")
    _unique_strings((query.get("id") for query in queries), "query ids")

    if require_frozen:
        _require(query_set.get("status") in {"example", "frozen"}, "template query sets cannot be scored")
        _require(bool(provenance.get("judgments_established_before_system_execution")), "judgments must predate execution")
        _require(not provenance.get("system_results_inspected_during_judging"), "judging must not inspect system results")
        if query_set.get("status") == "frozen":
            _require(bool(provenance.get("frozen_at")), "frozen query sets require provenance.frozen_at")

    for index, query in enumerate(queries):
        prefix = f"queries[{index}]"
        _require(isinstance(query, dict), f"{prefix} must be an object")
        _require(isinstance(query.get("id"), str) and query["id"], f"{prefix}.id is required")
        if require_frozen:
            _require(isinstance(query.get("query"), str) and query["query"].strip(), f"{prefix}.query is required")
            _require(query.get("query_type") in ALLOWED_QUERY_TYPES, f"{prefix}.query_type is invalid")
        judgments = query.get("judgments")
        _require(isinstance(judgments, list), f"{prefix}.judgments must be a list")
        if require_frozen:
            _require(any(j.get("relevance", 0) > 0 for j in judgments), f"{prefix} needs a positive judgment")
        doc_ids: list[str] = []
        for judgment_index, judgment in enumerate(judgments):
            label = f"{prefix}.judgments[{judgment_index}]"
            _require(isinstance(judgment, dict), f"{label} must be an object")
            doc_id = judgment.get("doc_id")
            relevance = judgment.get("relevance")
            _require(isinstance(doc_id, str) and doc_id, f"{label}.doc_id is required")
            _require(type(relevance) is int and 0 <= relevance <= 3, f"{label}.relevance must be an integer 0..3")
            doc_ids.append(doc_id)
        _unique_strings(doc_ids, f"{prefix} judgment doc_ids")


def validate_run(run: dict[str, Any], query_set: dict[str, Any]) -> None:
    _require(run.get("schema_version") == RUN_SCHEMA_VERSION, "unsupported run schema_version")
    _require(run.get("artifact_type") == "ranked_run", "run artifact_type must be 'ranked_run'")
    _require(run.get("query_set_id") == query_set["set_id"], "run query_set_id does not match query set")
    _require(isinstance(run.get("run_id"), str) and run["run_id"], "run requires run_id")
    _require(isinstance(run.get("generated_at"), str) and run["generated_at"], "run requires generated_at")
    _require(isinstance(run.get("system"), dict) and run["system"].get("name"), "run requires system.name")
    results = run.get("results")
    _require(isinstance(results, list), "run results must be a list")
    known_queries = {query["id"] for query in query_set["queries"]}
    query_ids: list[str] = []
    for index, result in enumerate(results):
        prefix = f"results[{index}]"
        _require(isinstance(result, dict), f"{prefix} must be an object")
        query_id = result.get("query_id")
        _require(query_id in known_queries, f"{prefix}.query_id is not in the query set")
        query_ids.append(query_id)
        ranked = result.get("ranked_results")
        _require(isinstance(ranked, list), f"{prefix}.ranked_results must be a list")
        doc_ids: list[str] = []
        for rank, item in enumerate(ranked, start=1):
            _require(isinstance(item, dict), f"{prefix}.ranked_results[{rank - 1}] must be an object")
            doc_id = item.get("doc_id")
            _require(isinstance(doc_id, str) and doc_id, f"{prefix}.ranked_results[{rank - 1}].doc_id is required")
            doc_ids.append(doc_id)
        _unique_strings(doc_ids, f"{prefix} ranked doc_ids")
    _unique_strings(query_ids, "run query_ids")


def _dcg(relevances: list[int], k: int) -> float:
    return sum(((2**relevance) - 1) / math.log2(rank + 1) for rank, relevance in enumerate(relevances[:k], start=1))


def _mean(values: Iterable[float]) -> float:
    values = list(values)
    return sum(values) / len(values) if values else 0.0


def _rounded(value: float) -> float:
    return round(value, 6)


def _score_query(
    query: dict[str, Any],
    ranked_results: list[dict[str, Any]] | None,
    ks: tuple[int, ...],
    primary_k: int,
) -> dict[str, Any]:
    judgments = {item["doc_id"]: item["relevance"] for item in query["judgments"]}
    missing_from_run = ranked_results is None
    ranked_results = ranked_results or []
    ranked_ids = [item["doc_id"] for item in ranked_results]
    relevances = [judgments.get(doc_id, 0) for doc_id in ranked_ids]
    relevant_ranks = [rank for rank, relevance in enumerate(relevances, start=1) if relevance > 0]
    reciprocal_rank = 1 / relevant_ranks[0] if relevant_ranks else 0.0
    ideal_relevances = sorted((value for value in judgments.values() if value > 0), reverse=True)

    metrics: dict[str, float] = {"mrr": _rounded(reciprocal_rank)}
    for k in ks:
        metrics[f"hit@{k}"] = float(any(relevance > 0 for relevance in relevances[:k]))
        ideal = _dcg(ideal_relevances, k)
        metrics[f"ndcg@{k}"] = _rounded(_dcg(relevances, k) / ideal if ideal else 0.0)

    if missing_from_run:
        failure_category = "missing_query_results"
    elif not ranked_ids:
        failure_category = "no_results"
    elif not relevant_ranks:
        failure_category = "no_relevant_retrieved"
    elif relevant_ranks[0] > primary_k:
        failure_category = "relevant_below_primary_k"
    else:
        failure_category = "success"

    return {
        "query_id": query["id"],
        "query": query["query"],
        "query_type": query["query_type"],
        "metrics": metrics,
        "first_relevant_rank": relevant_ranks[0] if relevant_ranks else None,
        "failure_category": failure_category,
        "returned": len(ranked_ids),
        "unjudged_in_primary_k": sum(1 for doc_id in ranked_ids[:primary_k] if doc_id not in judgments),
    }


def _aggregate(rows: list[dict[str, Any]], metric_names: list[str]) -> dict[str, Any]:
    return {
        "queries": len(rows),
        **{
            name: _rounded(_mean(row["metrics"][name] for row in rows))
            for name in metric_names
        },
        "failure_categories": dict(sorted(Counter(row["failure_category"] for row in rows).items())),
    }


def evaluate(
    query_set: dict[str, Any],
    run: dict[str, Any],
    *,
    ks: Iterable[int] = DEFAULT_KS,
    primary_k: int = 10,
) -> dict[str, Any]:
    """Validate and score a pre-recorded run against a frozen query set."""
    ks_tuple = tuple(sorted(set(ks)))
    _require(bool(ks_tuple) and all(type(k) is int and k > 0 for k in ks_tuple), "ks must contain positive integers")
    _require(type(primary_k) is int and primary_k > 0, "primary_k must be a positive integer")
    validate_query_set(query_set)
    validate_run(run, query_set)
    result_by_query = {item["query_id"]: item["ranked_results"] for item in run["results"]}
    rows = [
        _score_query(query, result_by_query.get(query["id"]), ks_tuple, primary_k)
        for query in query_set["queries"]
    ]
    metric_names = ["mrr"] + [name for k in ks_tuple for name in (f"hit@{k}", f"ndcg@{k}")]
    by_type: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        by_type[row["query_type"]].append(row)
    return {
        "schema_version": "retrieval-report.v1",
        "query_set_id": query_set["set_id"],
        "run_id": run["run_id"],
        "primary_k": primary_k,
        "ks": list(ks_tuple),
        "overall": _aggregate(rows, metric_names),
        "by_query_type": {
            query_type: _aggregate(type_rows, metric_names)
            for query_type, type_rows in sorted(by_type.items())
        },
        "failures": [
            {
                "query_id": row["query_id"],
                "query_type": row["query_type"],
                "category": row["failure_category"],
                "first_relevant_rank": row["first_relevant_rank"],
                "returned": row["returned"],
            }
            for row in rows
            if row["failure_category"] != "success"
        ],
        "queries": rows,
    }


def _parse_ks(value: str) -> tuple[int, ...]:
    try:
        return tuple(int(item.strip()) for item in value.split(",") if item.strip())
    except ValueError as exc:
        raise argparse.ArgumentTypeError("ks must be comma-separated integers") from exc


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--queries", type=Path, required=True, help="Frozen query-set JSON.")
    parser.add_argument("--run", type=Path, required=True, help="Pre-recorded ranked-run JSON.")
    parser.add_argument("--ks", type=_parse_ks, default=DEFAULT_KS, help="Cutoffs, default: 1,3,5,10.")
    parser.add_argument("--primary-k", type=int, default=10, help="Cutoff used for failure categorization.")
    parser.add_argument("--output", type=Path, help="Optional report JSON path; stdout is always written.")
    args = parser.parse_args(argv)

    try:
        query_set = json.loads(args.queries.read_text(encoding="utf-8"))
        run = json.loads(args.run.read_text(encoding="utf-8"))
        report = evaluate(query_set, run, ks=args.ks, primary_k=args.primary_k)
    except (OSError, json.JSONDecodeError, EvaluationError) as exc:
        parser.error(str(exc))
    rendered = json.dumps(report, indent=2, ensure_ascii=False, sort_keys=True)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered + "\n", encoding="utf-8")
    print(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
