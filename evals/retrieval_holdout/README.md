# Retrieval holdout evaluation

This package evaluates **pre-recorded ranked results**. The scorer does not
execute search, read the wiki, or inspect an index. That separation keeps
relevance judgments independent from the system being measured.

No real holdout queries are included here. `synthetic_queries.json` and
`synthetic_run.json` use fictional identifiers and exist only to demonstrate
the format and metrics. `holdout_template_30.json` contains 30 deliberately
unfilled slots.

## Why the existing 50-query suite is a development benchmark

`tests/search_benchmark.json` is valuable for regression testing, but it is not
an unbiased held-out evaluation. Its 50 queries and expected rank thresholds
are exercised by `scripts/evaluate_search_benchmark.py`, which mirrors the
current Explorer ranking implementation. The suite has therefore been visible
during search design and can influence aliases, boosts, fact routing, and other
tuning decisions.

Report results from that suite as **development benchmark** results. Do not use
them as evidence of generalization to unseen information needs. A real
holdout must be written and judged before the candidate system is run.

## Frozen v1 artifacts

`schema-v1.json` defines two artifact types:

- `retrieval-holdout.v1` query sets, with query type and graded relevance
  judgments from 0 (not relevant) through 3 (direct/highly relevant).
- `retrieval-run.v1` runs, containing ranked document IDs recorded by a named
  system.

The executable validator in `scorer.py` is dependency-free and enforces the
same invariants needed for scoring: unique IDs, relevance grades 0–3, at least
one positive judgment per scored query, matching query-set IDs, and no
duplicate document IDs within a ranking.

Allowed query types are:

- `exact_entity`
- `attribute_lookup`
- `conceptual`
- `source_seeking`
- `comparative`
- `multi_constraint`
- `other`

## Creating the real 30-query holdout

1. Copy `holdout_template_30.json` to a controlled location.
2. Have judges write all query text from plausible user needs without running
   or inspecting the candidate retrieval system.
3. Establish a judgment pool independently (for example from corpus browsing,
   known source/entity inventories, and assessor research). Record explicit
   relevance grades and short rationales.
4. Review query-type coverage and resolve judgment disagreements.
5. Set a stable `set_id`, timestamps, and judge identity. Set
   `status` to `frozen`, fill `frozen_at`, and set
   `judgments_established_before_system_execution` to `true`.
6. Store a hash or immutable copy of the frozen file before any system run.
7. Only then record ranked results. Never add or alter judgments after looking
   at those results; discovered gaps belong in a future holdout version.

The scorer rejects the unfilled template and any real holdout that is not
marked frozen.

## Scoring

From the repository root:

```bash
python -m evals.retrieval_holdout.scorer \
  --queries evals/retrieval_holdout/synthetic_queries.json \
  --run evals/retrieval_holdout/synthetic_run.json \
  --ks 1,3,5,10 \
  --primary-k 10
```

The report contains:

- `hit@k`: fraction of queries with any grade 1–3 result in the first `k`.
- `mrr`: reciprocal rank of the first grade 1–3 result over the complete
  recorded ranking.
- `ndcg@k`: graded nDCG using gain `2^relevance - 1`; unjudged documents are
  treated as relevance 0.
- overall and query-type aggregates.
- one exclusive failure category per query at `primary_k`.

Failure categories are `missing_query_results`, `no_results`,
`no_relevant_retrieved`, `relevant_below_primary_k`, and `success`.
`unjudged_in_primary_k` is also reported as a diagnostic; it is not silently
treated as a new relevance judgment.

## Optional read-only recording adapter

After a query set is frozen, the adapter can record the existing static
Explorer search path without modifying the index:

```bash
python -m evals.retrieval_holdout.search_index_adapter \
  --queries /controlled/path/holdout-v1.json \
  --output /controlled/path/run-v1.json \
  --run-id explorer-static-v1
```

The adapter reads the current generated search/fact indexes through the
existing evaluator. It does not create judgments, mutate wiki content, or
populate the real holdout.

## Focused tests

```bash
python -m unittest discover -s tests/evals -p 'test_*.py'
```
