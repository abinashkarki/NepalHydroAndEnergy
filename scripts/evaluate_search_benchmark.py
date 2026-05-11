#!/usr/bin/env python3
"""Evaluate Explore-search rankings against a blind benchmark set.

This intentionally mirrors the deterministic "fast Explore" path in
wiki/explorer/shared/wiki-search.js plus fact-result prepending from
wiki/explorer/index.html. It does not run the browser-side meaning boost.
"""
from __future__ import annotations

import argparse
import html
import json
import math
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent.parent
DEFAULT_BENCHMARK = ROOT / "tests" / "search_benchmark.json"
SEARCH_INDEX = ROOT / "wiki" / "explorer" / "shared" / "wiki-search-index.json"
FACT_INDEX = ROOT / "wiki" / "explorer" / "shared" / "wiki-fact-index.json"

STOPWORDS = set(
    """
a an the and or but if else for of in on at to from by with as is are was were be been being have has had do does did
not no nor so very can could should would may might must will shall this that these those it its i you he she they we
us them his her him their our your my me one two three some any all most more less than then also too here there when where why how
which what who whom whose into onto over under between within across about against amongst per via while during after before since until
also although still yet only just even ever never really often always sometimes maybe perhaps because however therefore thus hence such
each both either neither many few several other another same different new old high low big small large great good bad first second next last
own out up down off above below near far inside outside through throughout off through s t d m re ve ll
""".split()
)
TOKEN_RE = re.compile(r"[a-z0-9][a-z0-9\-_/]+")
TOKEN_SPLIT_RE = re.compile(r"[-_/]+")
SOURCE_INTENT_TERMS = {
    "annual",
    "data",
    "feasibility",
    "fy",
    "guideline",
    "guidelines",
    "proposal",
    "record",
    "report",
    "source",
    "status",
    "study",
    "summary",
    "table",
}


def tokenize(text: str) -> list[str]:
    tokens: list[str] = []
    for raw in TOKEN_RE.findall(text.lower()):
        if is_search_token(raw):
            tokens.append(raw)
        for part in TOKEN_SPLIT_RE.split(raw):
            if part != raw and is_search_token(part):
                tokens.append(part)
    return tokens


def is_search_token(token: str) -> bool:
    return token not in STOPWORDS and (len(token) > 2 or token.isdigit())


def normalize_search_text(text: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9]+", " ", text.lower())).strip()


def compact_search_text(text: str) -> str:
    return normalize_search_text(text).replace(" ", "")


@dataclass(frozen=True)
class Result:
    slug: str
    title: str
    category: str
    type: str
    subcategory: str
    score: float
    reason: str
    snippet: str
    kind: str = "wiki"
    chip: str = ""


class StaticSearchIndex:
    def __init__(self, index: dict[str, Any]) -> None:
        self.version = index["version"]
        self.pages = index.get("pages", [])
        self.postings = index.get("postings", {})
        self.doc_freq = index.get("doc_freq", {})
        self.doc_len = index.get("doc_len", [])
        self.avg_doc_len = index.get("avg_doc_len", 1) or 1
        self.aliases = index.get("aliases", {})
        self.alias_phrases = index.get("alias_phrases", [])
        self.neighbors = index.get("neighbors", {})
        self.total_docs = len(self.pages)

    def seek(self, query: str, limit: int = 30) -> list[Result]:
        query_terms = tokenize(query)
        terms = self.expand_terms(query, query_terms)
        if not terms:
            return []
        scores: dict[int, float] = {}
        reasons: dict[int, str] = {}

        for term in terms:
            rows = self.postings.get(term, [])
            df = self.doc_freq.get(term) or len(rows)
            if not df:
                continue
            idf = math.log(1 + (self.total_docs - df + 0.5) / (df + 0.5))
            for doc_id, tf in rows:
                denom = tf + 1.5 * (1 - 0.75 + 0.75 * ((self.doc_len[doc_id] or self.avg_doc_len) / self.avg_doc_len))
                score = idf * ((tf * 2.5) / denom)
                scores[doc_id] = scores.get(doc_id, 0) + score
                reasons.setdefault(doc_id, term)

        seed_ids = sorted(scores.items(), key=lambda item: item[1], reverse=True)[:12]
        for seed_id, seed_score in seed_ids:
            for neighbor_id, q_score in self.neighbors.get(str(seed_id), []):
                boost = seed_score * (q_score / 1000) * 0.35
                if boost <= 0:
                    continue
                if neighbor_id not in scores or scores[neighbor_id] < boost:
                    reasons[neighbor_id] = f"near {self.pages[seed_id].get('t', 'match')}"
                scores[neighbor_id] = scores.get(neighbor_id, 0) + boost

        self.apply_title_boost(query, query_terms, scores, reasons)
        ranked = sorted(scores.items(), key=lambda item: item[1], reverse=True)[:limit]
        return [self.result_for_page(self.pages[doc_id], score, reasons.get(doc_id, "match")) for doc_id, score in ranked]

    def expand_terms(self, query: str, terms: list[str]) -> list[str]:
        expanded = set(terms)
        for term in terms:
            expanded.update(self.aliases.get(term, []))
        q = query.lower()
        for item in self.alias_phrases:
            phrase = item.get("phrase")
            if phrase and phrase in q:
                expanded.update(item.get("expand", []))
        return [term for term in expanded if term in self.postings]

    def apply_title_boost(self, query: str, query_terms: list[str], scores: dict[int, float], reasons: dict[int, str]) -> None:
        q_norm = normalize_search_text(query)
        q_compact = compact_search_text(query)
        q_term_set = set(query_terms)
        if not q_norm or not q_term_set:
            return
        source_intent = any(term in SOURCE_INTENT_TERMS for term in query_terms)

        for doc_id, page in enumerate(self.pages):
            title_norm = normalize_search_text(page.get("t", ""))
            slug_norm = normalize_search_text(page.get("s", ""))
            title_compact = compact_search_text(page.get("t", ""))
            slug_compact = compact_search_text(page.get("s", ""))
            title_terms = set(tokenize(page.get("t", ""))) | set(tokenize(page.get("s", "")))
            covered = len(q_term_set & title_terms)
            compact_contains = len(q_compact) >= 5 and (q_compact in title_compact or q_compact in slug_compact)
            title_in_query = len(title_norm) >= 5 and title_norm in q_norm
            slug_in_query = len(slug_norm) >= 5 and slug_norm in q_norm
            if not covered and q_norm not in title_norm and q_norm not in slug_norm and not compact_contains and not title_in_query and not slug_in_query:
                continue

            boost = 0.0
            if title_norm == q_norm or slug_norm == q_norm or title_compact == q_compact or slug_compact == q_compact:
                boost += 30
            elif q_norm in title_norm or q_norm in slug_norm:
                boost += 18
            if title_in_query or slug_in_query:
                boost += 18
            if compact_contains:
                boost += 14
            if len(q_compact) >= 5 and (title_compact.startswith(q_compact) or slug_compact.startswith(q_compact)):
                boost += 8
            if covered:
                boost += 9 * (covered / len(q_term_set))
            if covered == len(q_term_set):
                boost += 12
            if not source_intent and page.get("c") == "entities" and boost > 0:
                boost += 4
            if source_intent and page.get("c") == "sources" and boost > 0:
                boost += 3
            if not source_intent and page.get("c") == "sources" and boost > 0:
                boost -= 2
            if boost <= 0:
                continue
            scores[doc_id] = scores.get(doc_id, 0) + boost
            if doc_id not in reasons or boost >= 18:
                reasons[doc_id] = "title"

    def result_for_page(self, page: dict[str, Any], score: float, reason: str, snippet: str = "") -> Result:
        return Result(
            slug=page.get("s", ""),
            title=page.get("t", ""),
            category=page.get("c", ""),
            type=page.get("y", ""),
            subcategory=page.get("u", ""),
            score=score,
            reason=reason,
            snippet=html.escape(snippet or page.get("e", "")),
        )


class StaticFactIndex:
    def __init__(self, index: dict[str, Any], search_index: StaticSearchIndex) -> None:
        self.version = index.get("version")
        self.facts = index.get("facts", [])
        self.page_by_slug = {page.get("s", ""): page for page in search_index.pages}

    def seek(self, query: str, limit: int = 8) -> list[Result]:
        intent = self.classify(query)
        if intent["constraints"]["noFacts"]:
            return []
        facts = self.rank_facts(intent)[:limit]
        return [result for i, fact in enumerate(facts) if (result := self.result_for_fact(fact, i))]

    def classify(self, query: str) -> dict[str, Any]:
        q = query.lower()
        terms = tokenize(q)

        def has(*words: str) -> bool:
            return any(word in q for word in words)

        domain = "solar" if has("solar", "pv") else "hydro"
        status = "any"
        if has("operating", "operation", "existing", "generation", "built", "commissioned", "working", "active", "running", "producing"):
            status = "operating"
        if has("construction", "under construction", "buildout", "building"):
            status = "under-construction"
        if has("survey", "planned", "proposed", "pipeline", "licence", "license"):
            status = "survey"
        storage = has("storage", "reservoir", "dry season", "firm", "peaking")
        superlative = has("biggest", "largest", "highest", "top ", "most mw", "second", "third")
        has_domain_term = any(term in {"hydro", "hydropower", "solar", "pv", "ror", "run-of-river", "storage", "projects"} for term in terms)
        factish = superlative or (has("projects") and (has("karnali") or storage or has("hydro"))) or (has_domain_term and superlative)
        return {
            "relevant": factish,
            "constraints": {
                "noFacts": not factish,
                "domains": [domain, "storage"] if storage else [domain],
                "status": status,
                "metric": "capacity_mw",
                "sort": "desc",
                "limit": 5,
            },
        }

    def rank_facts(self, intent: dict[str, Any]) -> list[dict[str, Any]]:
        constraints = intent.get("constraints", intent)
        domains = set(constraints.get("domains", []))
        status = constraints.get("status", "any")

        def matches(fact: dict[str, Any]) -> bool:
            facets = set(fact.get("facets") or [fact.get("domain")])
            if not any(domain in facets or fact.get("domain") == domain for domain in domains):
                return False
            if status != "any" and fact.get("status") != status:
                return False
            return isinstance(fact.get("capacity_mw"), (int, float))

        return sorted((fact for fact in self.facts if matches(fact)), key=lambda fact: float(fact.get("capacity_mw") or 0), reverse=True)

    def result_for_fact(self, fact: dict[str, Any], index: int) -> Result | None:
        slug = fact.get("wiki_slug") or fact.get("slug") or ""
        page = self.page_by_slug.get(slug, {})
        return Result(
            slug=slug,
            title=fact.get("name", ""),
            category=page.get("c", "facts"),
            type=page.get("y", "fact"),
            subcategory=page.get("u", ""),
            score=1 - index * 0.04,
            reason="fact",
            snippet=f"{format_mw(fact.get('capacity_mw'))} · {fact.get('status_raw') or fact.get('status')}",
            chip=fact.get("status", "fact"),
        )


def format_mw(value: Any) -> str:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return ""
    return f"{number:,.0f} MW" if number >= 100 else f"{number:,.2f} MW".rstrip("0").rstrip(".") + " MW"


def merge_fact_results(facts: list[Result], text_results: list[Result]) -> list[Result]:
    seen = {result.slug for result in facts if result.slug}
    out = list(facts)
    for result in text_results:
        if result.slug and result.slug in seen:
            continue
        out.append(result)
    return out


def load_indexes() -> tuple[StaticSearchIndex, StaticFactIndex | None]:
    search = StaticSearchIndex(json.loads(SEARCH_INDEX.read_text(encoding="utf-8")))
    facts = None
    if FACT_INDEX.exists():
        facts = StaticFactIndex(json.loads(FACT_INDEX.read_text(encoding="utf-8")), search)
    return search, facts


def evaluate_case(case: dict[str, Any], search: StaticSearchIndex, facts: StaticFactIndex | None, top_n: int) -> dict[str, Any]:
    query = case["query"]
    lexical = search.seek(query, limit=30)
    fact_results = facts.seek(query, limit=8) if facts else []
    results = merge_fact_results(fact_results, lexical)
    ranks = {result.slug: index + 1 for index, result in enumerate(results) if result.slug}
    checks = []
    passed = True
    for expectation in case.get("expect", []):
        slug = expectation["slug"]
        rank_le = int(expectation["rank_le"])
        actual_rank = ranks.get(slug)
        ok = actual_rank is not None and actual_rank <= rank_le
        checks.append({"slug": slug, "rank_le": rank_le, "actual_rank": actual_rank, "passed": ok})
        passed = passed and ok
    return {
        "id": case["id"],
        "query": query,
        "intent": case.get("intent", ""),
        "passed": passed,
        "checks": checks,
        "top": [
            {
                "rank": i + 1,
                "slug": result.slug,
                "title": result.title,
                "category": result.category,
                "score": round(result.score, 4),
                "reason": result.reason,
                "chip": result.chip,
            }
            for i, result in enumerate(results[:top_n])
        ],
    }


def render_markdown(evaluations: list[dict[str, Any]], top_n: int) -> str:
    passed = sum(1 for item in evaluations if item["passed"])
    total = len(evaluations)
    lines = [
        "# Search Benchmark Report",
        "",
        f"Passed: {passed}/{total}",
        "",
        "## Failures",
        "",
    ]
    failures = [item for item in evaluations if not item["passed"]]
    if not failures:
        lines.append("No failures.")
        lines.append("")
    for item in failures:
        lines.append(f"### {item['id']}")
        lines.append("")
        lines.append(f"Query: `{item['query']}`")
        lines.append("")
        for check in item["checks"]:
            status = "PASS" if check["passed"] else "FAIL"
            actual = check["actual_rank"] if check["actual_rank"] is not None else "missing"
            lines.append(f"- {status}: `{check['slug']}` expected <= {check['rank_le']}, actual {actual}")
        lines.append("")
        lines.append(f"Top {top_n}:")
        for row in item["top"]:
            chip = f" [{row['chip']}]" if row.get("chip") else ""
            lines.append(f"- {row['rank']}. `{row['slug']}`{chip} - {row['title']} ({row['reason']}, {row['score']})")
        lines.append("")

    lines.extend(["## All Cases", ""])
    for item in evaluations:
        status = "PASS" if item["passed"] else "FAIL"
        expected = ", ".join(
            f"`{check['slug']}` <= {check['rank_le']} (actual {check['actual_rank'] if check['actual_rank'] is not None else 'missing'})"
            for check in item["checks"]
        )
        lines.append(f"- {status} `{item['id']}`: {expected}")
    lines.append("")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--benchmark", type=Path, default=DEFAULT_BENCHMARK)
    parser.add_argument("--top-n", type=int, default=10)
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON instead of markdown.")
    parser.add_argument("--report", type=Path, help="Write the report to this path.")
    parser.add_argument("--strict", action="store_true", help="Exit non-zero when any expectation fails.")
    args = parser.parse_args(argv)

    benchmark = json.loads(args.benchmark.read_text(encoding="utf-8"))
    search, facts = load_indexes()
    evaluations = [evaluate_case(case, search, facts, args.top_n) for case in benchmark.get("cases", [])]
    passed = sum(1 for item in evaluations if item["passed"])
    payload = {
        "benchmark": str(args.benchmark.relative_to(ROOT) if args.benchmark.is_relative_to(ROOT) else args.benchmark),
        "passed": passed,
        "total": len(evaluations),
        "evaluations": evaluations,
    }
    output = json.dumps(payload, indent=2, ensure_ascii=False) if args.json else render_markdown(evaluations, args.top_n)
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(output + "\n", encoding="utf-8")
    print(output)
    return 1 if args.strict and passed != len(evaluations) else 0


if __name__ == "__main__":
    raise SystemExit(main())
