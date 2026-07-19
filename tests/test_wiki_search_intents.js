#!/usr/bin/env node
"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

const ROOT = path.resolve(__dirname, "..");
const source = fs.readFileSync(path.join(ROOT, "wiki/explorer/shared/wiki-search.js"), "utf8");
const window = {};
vm.runInNewContext(source, { window, console, Intl });

const { StaticFactIndex } = window.NepalExplorer;
const facts = [
  fact("hydro:mugu", "Mugu Karnali Storage HEP", "hydro", ["hydro"], "pre-construction", 1902, { river: "Karnali", basin: "Karnali", district: "Bajura", project_type: "Storage", total_storage_mcm: 4843.2, evidence_urls: ["https://example.test/mugu"] }),
  fact("hydro:upper-karnali", "Upper Karnali", "hydro", ["hydro"], "stalled", 900, { river: "Karnali", basin: "Karnali", district: "Surkhet", evidence_urls: ["https://example.test/upper-karnali"] }),
  fact("hydro:arun-3", "Arun 3", "hydro", ["hydro"], "under-construction", 900, { river: "Arun", basin: "Arun", district: "Sankhuwasabha" }),
  fact("hydro:kimathanka", "Kimathanka Arun HEP", "hydro", ["hydro"], "survey", 450, { river: "Arun", basin: "Arun", district: "Sankhuwasabha" }),
  fact("hydro:operating", "Upper Tamakoshi HPP", "hydro", ["hydro"], "operating", 456, { river: "Tama Koshi", basin: "Tama Koshi", district: "Dolakha" }),
  fact("hydro:planned", "Example Planned Hydro", "hydro", ["hydro"], "planned", 300, { river: "Trishuli", basin: "Trishuli", district: "Rasuwa" }),
  fact("solar:planned-10", "Example Solar Ten", "solar", ["solar"], "planned", 10, { district: "Parasi" }),
  fact("solar:planned-20", "Example Solar Twenty", "solar", ["solar"], "planned", 20, { district: "Parasi" }),
  fact("solar:operating", "Example Operating Solar", "solar", ["solar"], "operating", 15, { district: "Kapilbastu" }),
  fact("transmission:cross-border", "Gorakhpur–New Butwal Interconnection", "transmission", ["transmission"], "under-construction", null, { district: "Rupandehi" }),
];

const pages = facts.map((item) => ({ s: item.wiki_slug, t: item.name, c: "entities", y: "entity", u: "project" }));
const index = new StaticFactIndex({ version: 1, facts }, { pages });

function fact(id, name, domain, facets, status, capacity, extra = {}) {
  const slug = id.split(":")[1];
  return {
    id,
    name,
    domain,
    facets,
    status,
    status_display: status.replace(/(^|-)([a-z])/g, (_, prefix, char) => `${prefix ? " " : ""}${char.toUpperCase()}`),
    capacity_mw: capacity,
    wiki_slug: slug,
    sources: ["fixture"],
    ...extra,
  };
}

function titles(results) {
  return results.map((result) => result.title);
}

function statusCase(query, expectedStatus, expectedRequested = expectedStatus) {
  const intent = index.classify(query);
  assert.deepEqual([...intent.constraints.statuses], [expectedStatus], query);
  assert.deepEqual([...intent.constraints.requestedStatuses], [expectedRequested], query);
}

statusCase("stalled hydropower projects", "stalled");
statusCase("delayed hydropower projects", "stalled", "delayed");
statusCase("blocked projects", "stalled", "blocked");
statusCase("pre-construction hydro projects", "pre-construction");
statusCase("planned hydro projects", "planned");
statusCase("operating hydro plants", "operating");
statusCase("hydro projects under construction", "under-construction");
statusCase("survey-stage hydro projects", "survey");

const storage = index.seek("pre-construction storage projects over 700 MW in Karnali", { limit: 8 });
assert.deepEqual(titles(storage), ["Mugu Karnali Storage HEP"]);
assert.deepEqual([...storage.intent.constraints.requiredFacets], ["storage"]);
assert.equal(storage.intent.constraints.capacity.min, 700);
assert.equal(storage.intent.constraints.capacity.minInclusive, false);
assert.equal(storage.answer.count, 1);

const arun = index.seek("survey hydropower projects in Arun basin over 200 MW");
assert.deepEqual(titles(arun), ["Kimathanka Arun HEP"]);
assert.equal(arun[0].basin, "Arun");

const plannedSolar = index.seek("planned solar projects under 20 MW");
assert.deepEqual(titles(plannedSolar), ["Example Solar Ten"]);
assert.equal(plannedSolar.answer.capacity.maxInclusive, false);

const sources = index.seek("sources for Upper Karnali");
assert.deepEqual(titles(sources), ["Upper Karnali"]);
assert.equal(sources.intent.kind, "source-seeking");
assert.equal(sources[0].sourceSeeking, true);
assert.equal(sources[0].evidenceCount, 1);
assert.equal(sources.answer.title, "Evidence for Upper Karnali");

// An entity name that happens to contain a basin name stays with lexical
// search instead of prepending an unrelated basin-wide capacity list.
const exactEntity = index.seek("Upper Karnali");
assert.equal(exactEntity.length, 0);
assert.equal(exactEntity.intent.constraints.noFacts, true);

const targetedStatus = index.seek("stalled Upper Karnali project");
assert.deepEqual(titles(targetedStatus), ["Upper Karnali"]);

const transmission = index.seek("under-construction transmission corridors");
assert.deepEqual(titles(transmission), ["Gorakhpur–New Butwal Interconnection"]);
assert.equal(transmission[0].capacityMw, null);

const impossible = index.seek("stalled solar projects over 10 MW");
assert.equal(Array.isArray(impossible), true);
assert.equal(impossible.length, 0);
assert.equal(impossible.answer.empty, true);
assert.equal(impossible.answer.count, 0);
assert.match(impossible.answer.summary, /^No structured/);

const contradictory = index.seek("stalled and operating hydropower projects");
assert.equal(contradictory.length, 0);
assert.equal(contradictory.answer.contradictoryStatuses, true);
assert.match(contradictory.answer.summary, /conflicting statuses/);

const statusComparison = index.seek("which hydropower projects are operating and which are planned");
assert.deepEqual(titles(statusComparison), ["Upper Tamakoshi HPP", "Example Planned Hydro"]);
assert.equal(statusComparison.intent.constraints.statusMode, "any");

const ordinary = index.seek("seasonal mismatch in Nepal");
assert.equal(ordinary.length, 0);
assert.equal(ordinary.intent.constraints.noFacts, true);
assert.equal(ordinary.answer.applicable, false);
assert.equal(ordinary.answer.summary, "");
assert.equal(index.lastIntent, ordinary.intent);
assert.equal(index.lastAnswer, ordinary.answer);
assert.deepEqual(Object.keys(ordinary), []);

// Mentioning storage or a season in an explanatory question must not turn the
// query into a project-registry constraint or produce a misleading "no record"
// answer. The explorer should remain on lexical/editorial search for this.
const solarDrySeason = index.seek("What role can solar play in the dry season?");
assert.equal(solarDrySeason.length, 0);
assert.equal(solarDrySeason.intent.constraints.noFacts, true);
assert.equal(solarDrySeason.answer.applicable, false);
assert.equal(solarDrySeason.answer.summary, "");

const analysis = index.analyze("status of Arun 3");
assert.deepEqual(titles(analysis.results), ["Arun 3"]);
assert.equal(analysis.intent.kind, "fact-lookup");
assert.equal(analysis.answer.count, 1);

console.log("OK: structured wiki search intent tests passed");
