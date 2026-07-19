"""Regression tests for the JavaScript search runtime and generated corpus.

This deliberately executes the browser implementation in Node's built-in
``vm`` module.  It complements Python index-shape tests by proving that the
shipped ``wiki-search.js`` classifies and filters the generated indexes as the
explorer expects.
"""

from __future__ import annotations

import json
from pathlib import Path
import shutil
import subprocess
import textwrap
import unittest


ROOT = Path(__file__).resolve().parents[1]
SEARCH_JS = ROOT / "wiki" / "explorer" / "shared" / "wiki-search.js"
SEARCH_INDEX = ROOT / "wiki" / "explorer" / "shared" / "wiki-search-index.json"
FACT_INDEX = ROOT / "wiki" / "explorer" / "shared" / "wiki-fact-index.json"


NODE_PROBE = textwrap.dedent(
    r"""
    "use strict";

    const fs = require("node:fs");
    const vm = require("node:vm");

    const [searchSourcePath, searchIndexPath, factIndexPath] = process.argv.slice(1);
    const source = fs.readFileSync(searchSourcePath, "utf8");
    const searchData = JSON.parse(fs.readFileSync(searchIndexPath, "utf8"));
    const factData = JSON.parse(fs.readFileSync(factIndexPath, "utf8"));
    const window = {};

    vm.runInNewContext(source, { window, console, Intl }, { filename: searchSourcePath });

    const { StaticSearchIndex, StaticFactIndex } = window.NepalExplorer || {};
    if (typeof StaticSearchIndex !== "function" || typeof StaticFactIndex !== "function") {
      throw new Error("wiki-search.js did not expose both static search classes");
    }

    const search = new StaticSearchIndex(searchData);
    const facts = new StaticFactIndex(factData, search);
    const factById = new Map(factData.facts.map((fact) => [fact.id, fact]));

    function structuredResult(result) {
      return {
        factId: result.factId,
        slug: result.slug,
        title: result.title,
        status: result.status,
        capacityMw: result.capacityMw,
      };
    }

    function storageLike(fact) {
      const facets = new Set(fact.facets || []);
      const text = [fact.name, fact.project_type, fact.source_layer]
        .filter(Boolean)
        .join(" ")
        .toLowerCase();
      return facets.has("storage")
        || /\b(?:storage|reservoir)\b/.test(text)
        || Number.isFinite(Number(fact.total_storage_mcm))
        || Number.isFinite(Number(fact.effective_storage_mcm));
    }

    function snapshot(query, limit = 100) {
      const analysis = facts.analyze(query, { limit });
      const structured = analysis.results.map(structuredResult);
      return {
        structured,
        lexical: search.seek(query, { limit: 10 }).map((result) => ({
          slug: result.slug,
          title: result.title,
        })),
        intent: {
          noFacts: analysis.intent.constraints.noFacts,
          statuses: analysis.intent.constraints.statuses,
          requestedStatuses: analysis.intent.constraints.requestedStatuses,
        },
        answer: analysis.answer,
        nonStorageFactIds: structured
          .map((result) => factById.get(result.factId))
          .filter((fact) => fact && !storageLike(fact))
          .map((fact) => fact.id),
      };
    }

    const output = {
      upperExact: snapshot("Upper Karnali"),
      upperAttribute: snapshot("what is the status of Upper Karnali?"),
      stalled: snapshot("which hydropower projects are stalled?"),
      storageOver500: snapshot("storage projects above 500 MW"),
      largestKarnaliStorage: snapshot("largest storage project in Karnali"),
      conflictingStatuses: snapshot("stalled and operating hydropower projects"),
      dudhkoshiAlias: snapshot("Dudh Koshi storage"),
      solarDrySeason: snapshot("What role can solar play in the dry season?"),
    };

    process.stdout.write(JSON.stringify(output));
    """
)


class ExplorerSearchRuntimeTests(unittest.TestCase):
    """Exercise actual JavaScript behavior against actual generated data."""

    @classmethod
    def setUpClass(cls) -> None:
        node = shutil.which("node")
        if node is None:
            raise unittest.SkipTest("Node.js is not installed")

        for required in (SEARCH_JS, SEARCH_INDEX, FACT_INDEX):
            if not required.is_file():
                raise AssertionError(f"required explorer artifact is missing: {required}")

        completed = subprocess.run(
            [
                node,
                "-e",
                NODE_PROBE,
                str(SEARCH_JS),
                str(SEARCH_INDEX),
                str(FACT_INDEX),
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        if completed.returncode:
            raise AssertionError(
                "JavaScript explorer search probe failed\n"
                f"stdout:\n{completed.stdout}\n"
                f"stderr:\n{completed.stderr}"
            )
        try:
            cls.results = json.loads(completed.stdout)
        except json.JSONDecodeError as exc:
            raise AssertionError(
                f"JavaScript explorer search probe returned invalid JSON: {completed.stdout!r}"
            ) from exc

    def test_upper_karnali_exact_and_attribute_lookup(self) -> None:
        exact = self.results["upperExact"]
        attribute = self.results["upperAttribute"]

        self.assertEqual(exact["lexical"][0]["slug"], "upper-karnali")
        self.assertEqual(
            [result["factId"] for result in attribute["structured"]],
            ["hydro:upper-karnali"],
        )
        self.assertEqual(attribute["structured"][0]["status"], "stalled")
        self.assertEqual(attribute["answer"]["title"], "Upper Karnali")
        self.assertEqual(attribute["answer"]["summary"], "Stalled · 900 MW.")

    def test_stalled_projects_are_the_exact_structured_set(self) -> None:
        stalled = self.results["stalled"]
        self.assertEqual(
            [result["factId"] for result in stalled["structured"]],
            ["project:pancheshwar", "hydro:upper-karnali", "project:west-seti"],
        )
        self.assertEqual(stalled["intent"]["statuses"], ["stalled"])
        self.assertTrue(all(result["status"] == "stalled" for result in stalled["structured"]))

    def test_storage_above_500_excludes_run_of_river_and_sorts_capacity(self) -> None:
        storage = self.results["storageOver500"]
        capacities = [result["capacityMw"] for result in storage["structured"]]

        self.assertGreater(len(capacities), 1)
        self.assertTrue(all(capacity > 500 for capacity in capacities))
        self.assertEqual(capacities, sorted(capacities, reverse=True))
        self.assertEqual(storage["nonStorageFactIds"], [])

    def test_largest_karnali_storage_is_first(self) -> None:
        largest = self.results["largestKarnaliStorage"]["structured"][0]
        self.assertEqual(largest["factId"], "hydro:mugu-karnali-storage-hep")
        self.assertEqual(largest["capacityMw"], 1902)

    def test_conflicting_statuses_do_not_emit_generic_fact_results(self) -> None:
        conflicting = self.results["conflictingStatuses"]
        self.assertCountEqual(conflicting["intent"]["statuses"], ["stalled", "operating"])
        self.assertEqual(len(conflicting["structured"]), 0)

    def test_dudhkoshi_spaced_alias_resolves_to_project(self) -> None:
        alias = self.results["dudhkoshiAlias"]
        self.assertEqual(alias["lexical"][0]["slug"], "dudhkoshi-storage")
        self.assertEqual(alias["structured"][0]["factId"], "storage:dudhkoshi-storage")
        self.assertEqual(alias["structured"][0]["slug"], "dudhkoshi-storage")

    def test_dry_season_solar_question_stays_editorial(self) -> None:
        result = self.results["solarDrySeason"]
        self.assertEqual(result["structured"], [])
        self.assertTrue(result["intent"]["noFacts"])
        self.assertFalse(result["answer"]["applicable"])
        self.assertEqual(result["lexical"][0]["slug"], "solar-hydro-complementarity")


if __name__ == "__main__":
    unittest.main()
