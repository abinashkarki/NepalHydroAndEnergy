#!/usr/bin/env python3
"""Build the fully-static Search/Seek index for the wiki explorer.

The browser must not load an embedding model. This script does the expensive
offline work and ships only compact lexical postings plus a quantized
page-neighbor graph for broad discovery.
"""
from __future__ import annotations

import json
import math
import re
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
META = ROOT / "wiki" / "explorer" / "shared" / "wiki-page-meta.json"
ALIASES = ROOT / "wiki" / "explorer" / "shared" / "wiki-search-aliases.json"
OUT = ROOT / "wiki" / "explorer" / "shared" / "wiki-search-index.json"

STOPWORDS = set("""
a an the and or but if else for of in on at to from by with as is are was were be been being have has had do does did
not no nor so very can could should would may might must will shall this that these those it its i you he she they we
us them his her him their our your my me one two three some any all most more less than then also too here there when where why how
which what who whom whose into onto over under between within across about against amongst per via while during after before since until
also although still yet only just even ever never really often always sometimes maybe perhaps because however therefore thus hence such
each both either neither many few several other another same different new old high low big small large great good bad first second next last
own out up down off above below near far inside outside through throughout off through s t d m re ve ll
""".split())
TOKEN_RE = re.compile(r"[a-z0-9][a-z0-9\-_/]+")


def tokenize(text: str) -> list[str]:
    return [t for t in TOKEN_RE.findall(text.lower()) if len(t) > 2 and t not in STOPWORDS]


def load_aliases() -> tuple[dict[str, list[str]], list[dict]]:
    if not ALIASES.exists():
        return {}, []
    raw = json.loads(ALIASES.read_text(encoding="utf-8"))
    expanded: dict[str, set[str]] = defaultdict(set)
    phrase_aliases: list[dict] = []
    for key, values in raw.items():
        if key.startswith("_"):
            continue
        key_terms = tokenize(key)
        value_terms: set[str] = set()
        for value in values:
            value_terms.update(tokenize(value))
        phrase_aliases.append({
            "phrase": key.lower(),
            "terms": sorted(set(key_terms)),
            "expand": sorted(value_terms),
            "weight": 0.8,
        })
        if key.lower() == "solar hydro complementarity":
            continue
        for term in key_terms:
            expanded[term].update(value_terms)
    return {k: sorted(v - {k}) for k, v in sorted(expanded.items()) if v}, phrase_aliases


def compact_pages(pages: list[dict]) -> list[dict]:
    return [
        {
            "s": p["slug"],
            "t": p["title"],
            "c": p["category"],
            "y": p.get("type", ""),
            "u": p.get("subcategory", ""),
            "e": p.get("excerpt", ""),
            "i": int(p.get("image_count", 0) or 0),
            "stub": bool(p.get("is_stub", False)),
            "pq": p.get("page_quality", ""),
        }
        for p in pages
    ]


def build_postings(pages: list[dict]) -> tuple[dict[str, list[list[int]]], dict[str, int], list[int]]:
    postings: dict[str, list[list[int]]] = defaultdict(list)
    doc_freq: Counter[str] = Counter()
    doc_len: list[int] = []
    for doc_id, page in enumerate(pages):
        tf = Counter(page.get("token_freq") or {})
        doc_len.append(sum(tf.values()))
        for term, count in sorted(tf.items()):
            if count <= 0:
                continue
            postings[term].append([doc_id, int(count)])
            doc_freq[term] += 1
    return dict(sorted(postings.items())), dict(sorted(doc_freq.items())), doc_len


def weighted_doc_vectors(pages: list[dict], doc_freq: dict[str, int]) -> list[dict[str, float]]:
    total = max(len(pages), 1)
    vectors: list[dict[str, float]] = []
    for page in pages:
        tf = Counter(page.get("token_freq") or {})
        title_terms = set(tokenize(page.get("title", "")))
        tag_terms = set(tokenize(" ".join(page.get("tags") or [])))
        heading_terms = set(tokenize(" ".join(page.get("headings") or [])))
        vec: dict[str, float] = {}
        for term, count in tf.items():
            idf = math.log(1 + (total - doc_freq.get(term, 0) + 0.5) / (doc_freq.get(term, 0) + 0.5))
            boost = 1.0
            if term in title_terms:
                boost += 1.5
            if term in tag_terms:
                boost += 0.8
            if term in heading_terms:
                boost += 0.5
            vec[term] = (1 + math.log(count)) * idf * boost
        norm = math.sqrt(sum(v * v for v in vec.values())) or 1.0
        vectors.append({term: value / norm for term, value in vec.items() if value > 0})
    return vectors


def build_neighbors(vectors: list[dict[str, float]], top_k: int = 8) -> dict[str, list[list[int]]]:
    inverted: dict[str, list[tuple[int, float]]] = defaultdict(list)
    for doc_id, vec in enumerate(vectors):
        for term, weight in vec.items():
            inverted[term].append((doc_id, weight))

    neighbors: dict[str, list[list[int]]] = {}
    for doc_id, vec in enumerate(vectors):
        scores: defaultdict[int, float] = defaultdict(float)
        for term, weight in vec.items():
            for other_id, other_weight in inverted[term]:
                if other_id == doc_id:
                    continue
                scores[other_id] += weight * other_weight
        top = sorted(scores.items(), key=lambda item: item[1], reverse=True)[:top_k]
        if top:
            neighbors[str(doc_id)] = [[other_id, min(1000, max(0, round(score * 1000)))] for other_id, score in top]
    return neighbors


def main() -> None:
    meta = json.loads(META.read_text(encoding="utf-8"))
    pages = meta["pages"]
    postings, doc_freq, doc_len = build_postings(pages)
    vectors = weighted_doc_vectors(pages, doc_freq)
    aliases, alias_phrases = load_aliases()
    out = {
        "version": 1,
        "pages": compact_pages(pages),
        "postings": postings,
        "doc_freq": doc_freq,
        "doc_len": doc_len,
        "avg_doc_len": sum(doc_len) / max(len(doc_len), 1),
        "aliases": aliases,
        "alias_phrases": alias_phrases,
        "neighbors": build_neighbors(vectors),
    }
    OUT.write_text(json.dumps(out, separators=(",", ":"), ensure_ascii=False), encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)} ({len(pages)} pages, {len(postings)} terms)")


if __name__ == "__main__":
    main()
