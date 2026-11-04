#!/usr/bin/env node
"use strict";

// Focused stage-one regressions for structured project search and tariff
// rendering.  This loads the checked-in corpus so records without wiki pages
// remain part of the contract under test.
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

const ROOT = path.resolve(__dirname, "..");
const searchSource = fs.readFileSync(path.join(ROOT, "wiki/explorer/shared/wiki-search.js"), "utf8");
const window = {};
vm.runInNewContext(searchSource, { window, console, Intl });
const { StaticFactIndex } = window.NepalExplorer;
const corpus = JSON.parse(fs.readFileSync(path.join(ROOT, "wiki/explorer/shared/wiki-fact-index.json"), "utf8"));
const pages = JSON.parse(fs.readFileSync(path.join(ROOT, "wiki/explorer/shared/wiki-search-index.json"), "utf8"));
const index = new StaticFactIndex(corpus, pages);

function resultFor(query, expectedId) {
  const results = index.seek(query, { limit: 8 });
  const result = results.find((item) => item.factId === expectedId);
  assert.ok(result, `${query} should return ${expectedId}; got ${results.map((item) => item.title).join(", ")}`);
  assert.equal(results[0].factId, expectedId, `${query} should rank its record first`);
  assert.equal(index.getFact(result.factId).id, expectedId);
  return result;
}

const danaId = "hydro:dana-khola-hydropower-project";
const sutiId = "hydro:suti-khola-hydropower-project";

// Ordinary names must reach the structured record without requiring the
// generic “Hydropower Project” suffix. Both records intentionally have no wiki
// article and therefore must retain valid fact-reader destinations.
for (const [name, id] of [["Dana Khola", danaId], ["Suti Khola", sutiId]]) {
  const short = resultFor(name, id);
  assert.equal(short.kind, "fact", `${name} should be a slugless fact result`);
  assert.equal(short.slug, "");
  assert.equal(short.structured, true);
  assert.equal(short.factId, id);

  const full = resultFor(`${name} Hydropower Project`, id);
  assert.equal(full.factId, id);
  assert.equal(full.kind, "fact");
  assert.equal(index.getFact(full.factId).wiki_slug || "", "");
}

// Covered project control: an existing wiki-backed fact still opens its
// matching record and retains the wiki destination.
const upper = resultFor("Upper Tamakoshi", "hydro:upper-tamakoshi-hpp");
assert.equal(upper.kind, "wiki");
assert.equal(upper.slug, "upper-tamakoshi");
assert.equal(upper.factId, "hydro:upper-tamakoshi-hpp");

// Editorial wording that merely contains a project name stays in ordinary
// search; the fact classifier must not turn it into a targeted lookup.
const editorial = index.analyze("Upper Tamakoshi environmental impacts");
assert.equal(editorial.intent.constraints.noFacts, true);
assert.equal(editorial.intent.kind, "project-list");
assert.equal(editorial.results.length, 0);
const ordinaryEditorial = index.analyze("seasonal mismatch");
assert.equal(ordinaryEditorial.intent.constraints.noFacts, true);
assert.equal(ordinaryEditorial.results.length, 0);

// Explicit source/attribute/status/capacity controls remain structured-query
// gates and target the named record.
assert.equal(resultFor("sources for Dana Khola", danaId).sourceSeeking, true);
assert.equal(resultFor("capacity of Dana Khola", danaId).factId, danaId);
assert.equal(resultFor("operating Upper Tamakoshi", "hydro:upper-tamakoshi-hpp").status, "operating");
assert.equal(index.seek("operating Dana Khola").length, 0);
const capacity = resultFor("Dana Khola over 10 MW", danaId);
assert.equal(capacity.capacityMw, 19);
assert.equal(capacity.factId, danaId);
assert.equal(index.seek("Dana Khola over 20 MW").length, 0);

// Extract the production formatter from the HTML and execute that function,
// rather than duplicating its implementation in this test.
const html = fs.readFileSync(path.join(ROOT, "wiki/explorer/index.html"), "utf8");
const formatterMatch = html.match(/function formatTariff\(value\) \{[\s\S]*?\n\s*\}/);
assert.ok(formatterMatch, "formatTariff should remain discoverable in explorer HTML");
const formatTariff = vm.runInNewContext(`(${formatterMatch[0]})`, { Intl });
for (const unknown of [null, undefined, "", "   ", false, true, NaN, Infinity, -Infinity, "not-a-number"]) {
  assert.equal(formatTariff(unknown), "", `unknown tariff ${String(unknown)} should remain blank for UI fallback`);
}
assert.equal(formatTariff(0), "NPR 0/kWh");
assert.equal(formatTariff("0"), "NPR 0/kWh");
assert.equal(formatTariff(12.5), "NPR 12.5/kWh");
assert.equal(formatTariff("12.5"), "NPR 12.5/kWh");

console.log("OK: Lalupate stage-one regression tests passed");

// Licence lookup must use the generation-licence bucket, not survey.
for (const q of ['licensed Dana Khola', 'licenced Dana Khola', 'generation licence Dana Khola', 'generation license Dana Khola']) {
  assert.equal(resultFor(q, danaId).status, 'licensed');
}
assert.deepEqual(Array.from(index.classify('survey licence projects').constraints.statuses), ['survey']);
assert.deepEqual(Array.from(index.classify('survey license projects').constraints.statuses), ['survey']);
assert.equal(index.seek('survey Dana Khola').length, 0);

// Exercise the production answer renderer with a lexical fallback: it must
// remain readable below the answer, never become a qualifying answer action.
const cardSource = html.slice(html.indexOf('      function answerCardHtml('), html.indexOf('      function searchToolsHtml('));
const renderCard = vm.runInNewContext(`(${cardSource.trim()})`, {
  lastSearchQuery: '', exactSearchResults: () => [], factForResult: () => null,
  preferredAnswerResult: results => results[0], humanResultLabel: () => '',
  plainSearchText: text => text, escapeHtml: text => String(text), escapeAttr: text => String(text),
  mapEligibleResults: results => results,
});
const fallback = {title:'Related wiki page', slug:'related', kind:'wiki'};
for (const sourceSeeking of [false, true]) {
  const emptyCard = renderCard([fallback], {sourceSeeking, answer:{applicable:true, empty:true, title:'No matches'}});
  assert.ok(!emptyCard.includes('data-answer-open'));
  assert.ok(!emptyCard.includes('data-search-map'));
}
const normalCard = renderCard([fallback], {answer:{applicable:false}});
assert.ok(normalCard.includes('data-answer-open'));
console.log('OK: licence vocabulary and empty-answer actions passed');
