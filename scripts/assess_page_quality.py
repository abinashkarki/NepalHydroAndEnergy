#!/usr/bin/env python3
"""Measure each page against wiki/QUALITY_RUBRIC.md and report the tier it earns.

The rubric's per-category minimums are encoded as required section headings and
a minimum amount of prose. A page "earns" the highest tier whose requirements it
meets. The declared `page_quality` should never exceed the earned tier.

    python scripts/assess_page_quality.py            # report
    python scripts/assess_page_quality.py --apply    # lower over-declared tiers
    python scripts/assess_page_quality.py --check    # exit 1 if any page is over-declared

Core pages (wiki/core-pages.json) are assessed like every other page; core
membership governs freshness and caveats, not the quality label.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PAGES = ROOT / "wiki" / "pages"
CORE = ROOT / "wiki" / "core-pages.json"
TIERS = ["record", "brief", "analysis", "flagship"]

# Per category: tier -> (heading patterns that must all appear, minimum prose words).
# A pattern is a regex alternation matched against lower-cased H2/H3 headings.
RUBRIC: dict[str, dict[str, tuple[list[str], int]]] = {
    "sources": {
        "record": ([], 0),
        "brief": (["summary|overview", "key (findings|data|points)|key data points|findings"], 120),
        "analysis": (["summary|overview", "key (findings|data|points)|findings", "relevance|why it matters|use in", "limitation|caveat"], 250),
        "flagship": (["summary|overview", "key (findings|data|points)|findings", "relevance|why it matters|use in", "limitation|caveat", "method|coverage|scope", "update history|recent updates|changelog"], 500),
    },
    "entities": {
        "record": ([], 0),
        "brief": (["sources?|references"], 150),
        "analysis": (["sources?|references", "status|current status", "significance|context|background|why it matters|history"], 400),
        "flagship": (["sources?|references", "status|current status", "significance|context|background|why it matters|history", "limitation|controvers|caveat"], 800),
    },
    "concepts": {
        "record": ([], 0),
        "brief": ([], 150),
        "analysis": (["summary|overview|definition|what it is", "simple explanation|plain|in brief|explained", "related|see also"], 300),
        "flagship": (["summary|overview|definition|what it is", "simple explanation|plain|in brief|explained", "related|see also", "misunderstand|misconception|myth"], 600),
    },
    "claims": {
        "record": ([], 0),
        "brief": (["claim", "evidence"], 60),
        "analysis": (["claim", "evidence", "confidence", "unresolved|open (issues|questions)", "boundary", "related"], 200),
        "flagship": (["claim", "evidence", "confidence", "unresolved|open (issues|questions)", "boundary", "related", "counter|contrary|challenge", "history"], 400),
    },
    "data": {
        "record": ([], 0),
        "brief": (["summary|overview|what (it|this) shows"], 100),
        "analysis": (["summary|overview|what (it|this) shows", "method|coverage|source", "caveat|limitation"], 250),
        "flagship": (["summary|overview|what (it|this) shows", "method|coverage|source", "caveat|limitation", "reconcil|contradict|conflict", "update history|changelog"], 500),
    },
    "syntheses": {
        "record": ([], 0),
        "brief": ([], 200),
        "analysis": (["evidence|sources|trail", "unknown|open question|unresolved|gap|not yet|what remains|does not know"], 450),
        "flagship": (["evidence|sources|trail", "unknown|open question|unresolved|gap|not yet|what remains|does not know", "reading|read next|where to begin|start", "update history|changelog|what changed"], 1200),
    },
    "interventions": {
        "record": ([], 0),
        "brief": (["question|option|theory of change|proposal|description", "status|evidence|established facts"], 200),
        "analysis": (["question|option|theory of change|proposal|description", "status|evidence|established facts", "unlock|benefit|assessment", "gap|evidence needed|research"], 400),
        "flagship": (["question|option|theory of change|proposal|description", "status|evidence|established facts", "unlock|benefit|assessment", "gap|evidence needed|research", "comparable|case", "institution|stakeholder|feasibility"], 700),
    },
}


def split(text: str) -> tuple[str, str]:
    match = re.match(r"---\n(.*?)\n---\n?", text, re.S)
    return (match.group(1), text[match.end():]) if match else ("", text)


def declared_tier(frontmatter: str) -> str:
    match = re.search(r"^page_quality:\s*(\S+)", frontmatter, re.M)
    return match.group(1).strip("'\"") if match else ""


def prose_words(body: str) -> int:
    kept = []
    for line in body.splitlines():
        stripped = line.strip()
        if stripped.startswith(("|", "#", "<", "<!--", "![")):
            continue
        kept.append(stripped)
    text = re.sub(r"\[\[([^\]|]+)(?:\|([^\]]+))?\]\]", lambda m: m.group(2) or m.group(1), " ".join(kept))
    return len(re.findall(r"[A-Za-z0-9][A-Za-z0-9'’.,%/-]*", text))


def headings(body: str) -> list[str]:
    return [m.group(1).strip().lower() for m in re.finditer(r"^#{2,3}\s+(.+?)\s*$", body, re.M)]


def assess(category: str, body: str) -> tuple[str, dict[str, list[str]]]:
    rules = RUBRIC.get(category)
    if not rules:
        return "record", {}
    found = headings(body)
    words = prose_words(body)
    earned = "record"
    gaps: dict[str, list[str]] = {}
    for tier in TIERS:
        patterns, minimum = rules[tier]
        missing = [p for p in patterns if not any(re.search(p, h) for h in found)]
        if words < minimum:
            missing.append(f"≥{minimum} prose words (has {words})")
        if missing:
            gaps[tier] = missing
            break
        earned = tier
    return earned, gaps


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--apply", action="store_true", help="lower over-declared tiers in place")
    parser.add_argument("--check", action="store_true", help="exit 1 if any page is over-declared")
    parser.add_argument("--json", type=Path, help="write the full assessment to this path")
    args = parser.parse_args()

    core = set(json.loads(CORE.read_text(encoding="utf-8")).get("pages", [])) if CORE.exists() else set()
    rows = []
    for path in sorted(PAGES.rglob("*.md")):
        text = path.read_text(encoding="utf-8")
        frontmatter, body = split(text)
        declared = declared_tier(frontmatter)
        earned, gaps = assess(path.parent.name, body)
        over = declared in TIERS and TIERS.index(declared) > TIERS.index(earned)
        rows.append({
            "slug": path.stem, "category": path.parent.name, "declared": declared, "earned": earned,
            "over_declared": over, "core": path.stem in core, "next_tier_gaps": gaps,
        })
        if args.apply and over:
            new_front = re.sub(r"^page_quality:.*$", f"page_quality: {earned}", frontmatter, count=1, flags=re.M)
            path.write_text(text.replace(frontmatter, new_front, 1), encoding="utf-8")

    declared_mix = Counter(r["declared"] or "(none)" for r in rows)
    earned_mix = Counter(r["earned"] for r in rows)
    over = [r for r in rows if r["over_declared"]]
    core_gaps = [r for r in over if r["core"]]
    print(f"{len(rows)} pages")
    print("declared:", dict(sorted(declared_mix.items())))
    print("earned:  ", dict(sorted(earned_mix.items())))
    print(f"over-declared: {len(over)} ({len(core_gaps)} of them core pages)")
    for r in core_gaps:
        gap = next(iter(r["next_tier_gaps"].values()), [])
        print(f"  core {r['slug']}: declared {r['declared']}, earns {r['earned']}; missing {', '.join(gap)}")
    if args.json:
        args.json.write_text(json.dumps(rows, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    if args.check and over:
        print("FAIL: pages declare a higher page_quality than they earn; run with --apply", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
