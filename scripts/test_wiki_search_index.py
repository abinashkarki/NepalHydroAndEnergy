#!/usr/bin/env python3
from __future__ import annotations

import gzip
import json
import re
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
INDEX = ROOT / "wiki" / "explorer" / "shared" / "wiki-search-index.json"
FACT_INDEX = ROOT / "wiki" / "explorer" / "shared" / "wiki-fact-index.json"
VECTOR_INDEX = ROOT / "wiki" / "explorer" / "shared" / "wiki-vector-index.json"
HTML = ROOT / "wiki" / "explorer" / "index.html"
SEMANTIC_JS = ROOT / "wiki" / "explorer" / "shared" / "wiki-semantic.js"


class WikiSearchIndexTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        subprocess.run(
            [sys.executable, "scripts/build_wiki_search_index.py"],
            cwd=ROOT,
            check=True,
        )
        subprocess.run(
            [sys.executable, "scripts/build_wiki_fact_index.py"],
            cwd=ROOT,
            check=True,
        )
        cls.index = json.loads(INDEX.read_text(encoding="utf-8"))
        cls.fact_index = json.loads(FACT_INDEX.read_text(encoding="utf-8"))
        cls.vector_index = json.loads(VECTOR_INDEX.read_text(encoding="utf-8")) if VECTOR_INDEX.exists() else None

    def test_static_search_index_schema_and_profile(self) -> None:
        self.assertEqual(self.index["version"], 1)
        self.assertGreater(len(self.index["pages"]), 200)
        self.assertIn("postings", self.index)
        self.assertIn("neighbors", self.index)
        self.assertIn("aliases", self.index)
        self.assertLess(len(gzip.compress(INDEX.read_bytes(), compresslevel=9)), 1_000_000)

    def test_neighbor_scores_are_quantized(self) -> None:
        some_neighbors = [pair for rows in self.index["neighbors"].values() for pair in rows]
        self.assertTrue(some_neighbors)
        for target_id, score in some_neighbors[:100]:
            self.assertIsInstance(target_id, int)
            self.assertIsInstance(score, int)
            self.assertGreaterEqual(score, 0)
            self.assertLessEqual(score, 1000)

    def test_aliases_cover_expected_discovery_language(self) -> None:
        aliases = self.index["aliases"]
        for key in ["firm", "winter", "deficit", "india", "export", "risk", "storage", "karnali"]:
            self.assertIn(key, aliases)
        self.assertNotIn("solar", aliases.get("hydro", []), "bare hydro must not expand into solar concepts")
        self.assertNotIn("hybrid", aliases.get("hydro", []), "bare hydro must not expand into hybrid siting")

    def test_runtime_has_no_browser_corpus_embedding_path(self) -> None:
        html = HTML.read_text(encoding="utf-8")
        self.assertNotIn("wiki-semantic.js", html)
        self.assertNotIn("Semantic", html)
        self.assertNotIn("sem-status", html)
        self.assertIn("Find", html)
        self.assertIn("Explore", html)
        self.assertIn("wiki-vector-search.js", html)
        self.assertIn("wiki-fact-index.json", html)

    def test_legacy_semantic_module_is_not_kept_active(self) -> None:
        self.assertFalse(SEMANTIC_JS.exists(), "remove inactive browser-side model loader")

    def test_vector_index_schema_and_quantization(self) -> None:
        self.assertIsNotNone(self.vector_index, "run scripts/build_wiki_vector_index.py")
        vector = self.vector_index
        self.assertEqual(vector["version"], 1)
        self.assertEqual(vector["model"]["dtype"], "int8_unit")
        self.assertGreaterEqual(vector["model"]["dim"], 128)
        self.assertIn("mixedbread-ai/mxbai-embed-xsmall-v1", vector["model"]["id"])
        self.assertGreater(vector["stats"]["chunks"], vector["stats"]["pages"])
        self.assertLess(len(gzip.compress(VECTOR_INDEX.read_bytes(), compresslevel=9)), 1_150_000)
        sample = vector["chunks"][0]
        self.assertEqual({"p", "h", "s", "v"}, set(sample))

    def test_fact_index_schema_and_profile(self) -> None:
        facts = self.fact_index["facts"]
        self.assertEqual(self.fact_index["version"], 1)
        self.assertGreater(len(facts), 500)
        self.assertLess(len(gzip.compress(FACT_INDEX.read_bytes(), compresslevel=9)), 250_000)
        sample = facts[0]
        for key in ["id", "domain", "facets", "name", "capacity_mw", "status", "source_layer", "sources", "feature_ref", "related_slugs"]:
            self.assertIn(key, sample)
        self.assertIn("layer", sample["feature_ref"])

    def test_fact_index_answers_biggest_hydro_queries(self) -> None:
        hydro = [f for f in self.fact_index["facts"] if f["domain"] == "hydro" and f.get("capacity_mw")]
        any_status = sorted(hydro, key=lambda f: f["capacity_mw"], reverse=True)
        operating = sorted([f for f in hydro if f["status"] == "operating"], key=lambda f: f["capacity_mw"], reverse=True)
        self.assertEqual(any_status[0]["name"], "Mugu Karnali Storage HEP")
        self.assertEqual(any_status[0]["capacity_mw"], 1902.0)
        self.assertEqual(operating[0]["name"], "Upper Tamakoshi HPP")
        self.assertEqual(operating[0]["capacity_mw"], 456.0)

    def test_fact_index_answers_biggest_solar_without_wiki_page(self) -> None:
        solar = [f for f in self.fact_index["facts"] if f["domain"] == "solar" and f.get("capacity_mw")]
        any_status = sorted(solar, key=lambda f: f["capacity_mw"], reverse=True)
        operating = sorted([f for f in solar if f["status"] == "operating"], key=lambda f: f["capacity_mw"], reverse=True)
        self.assertEqual(any_status[0]["name"], "Khungri solar award")
        self.assertEqual(any_status[0]["capacity_mw"], 50.0)
        self.assertEqual(any_status[0].get("wiki_slug", ""), "")
        self.assertEqual(any_status[0]["feature_ref"]["layer"], "solar_plants")
        self.assertTrue(any_status[0]["related_slugs"])
        self.assertEqual(operating[0]["name"], "Dharamnagar Solar Farm Project - II Kapilbastu")
        self.assertEqual(operating[0]["capacity_mw"], 15.0)

    def test_golden_query_terms_are_retrievable_from_static_index(self) -> None:
        postings = self.index["postings"]
        aliases = self.index["aliases"]

        def expanded_terms(query: str) -> set[str]:
            terms = set(re.findall(r"[a-z0-9][a-z0-9\\-_/]+", query.lower()))
            expanded = set(terms)
            for term in terms:
                expanded.update(aliases.get(term, []))
            return {term for term in expanded if term in postings}

        checks = {
            "winter deficit": {"winter", "deficit", "dry-season", "storage", "seasonal"},
            "firm power": {"firm", "storage", "dry-season", "peaking"},
            "india export risk": {"india", "export", "trade", "cross-border"},
            "storage projects Karnali": {"storage", "project", "karnali"},
        }
        for query, expected_any in checks.items():
            found = expanded_terms(query)
            self.assertTrue(
                found & expected_any,
                f"{query!r} did not expand into useful index terms: {sorted(found)[:20]}",
            )

    def test_golden_seek_ranking_does_not_poison_hydro_with_solar(self) -> None:
        postings = self.index["postings"]
        aliases = self.index["aliases"]

        def expanded_terms(query: str) -> set[str]:
            terms = set(re.findall(r"[a-z0-9][a-z0-9\\-_/]+", query.lower()))
            expanded = set(terms)
            for term in terms:
                expanded.update(aliases.get(term, []))
            return {term for term in expanded if term in postings}

        biggest_hydro_terms = expanded_terms("what is the biggest hydro plant")
        self.assertIn("hydro", biggest_hydro_terms)
        self.assertNotIn("solar", biggest_hydro_terms)
        self.assertNotIn("hybrid", biggest_hydro_terms)


if __name__ == "__main__":
    unittest.main()
