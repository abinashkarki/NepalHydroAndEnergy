#!/usr/bin/env node
"use strict";

// Contract tests for wiki/explorer/shared/data-explorer.js (Data Tables view).
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

const ROOT = path.resolve(__dirname, "..");
const MODULE = path.join(ROOT, "wiki/explorer/shared/data-explorer.js");
const source = fs.readFileSync(MODULE, "utf8");
const html = fs.readFileSync(path.join(ROOT, "wiki/explorer/index.html"), "utf8");

const plain = (x) => JSON.parse(JSON.stringify(x));
const eq = (a, b, msg) => assert.deepEqual(plain(a), plain(b), msg);

// Loading the module must not fetch anything.
let fetchCalls = 0;
const window = { fetch: () => { fetchCalls += 1; return Promise.reject(new Error("unexpected fetch")); } };
vm.runInNewContext(source, { window, console, Intl, Promise, Number, String, Math, Set, Object, Blob: function () {} });
const DX = window.NepalDataExplorer;
assert.ok(DX, "NepalDataExplorer exported");
assert.equal(fetchCalls, 0, "module load must not fetch CSVs");

// ---- CSV parsing: quotes, embedded commas/quotes/newlines, CRLF, BOM, trailing newline
{
  const text = "﻿a,b,c\r\n1,\"x, y\",\"he said \"\"hi\"\"\"\r\n2,\"line1\nline2\",\r\n";
  const parsed = DX.parseCSV(text);
  eq(parsed.columns, ["a", "b", "c"]);
  assert.equal(parsed.rows.length, 2);
  assert.equal(parsed.rows[0].b, "x, y");
  assert.equal(parsed.rows[0].c, 'he said "hi"');
  assert.equal(parsed.rows[1].b, "line1\nline2");
  assert.equal(parsed.rows[1].c, "");
  eq(DX.parseCSV("").rows, []);
  assert.equal(DX.parseCSV("a,b\n1,2").rows[0].b, "2", "no trailing newline");
}

// ---- round trip through toCSV
{
  const rows = [{ a: "1", b: "x, y" }, { a: "2", b: 'q"r' }];
  const parsed = DX.parseCSV(DX.toCSV(["a", "b"], rows));
  eq(parsed.rows, rows);
}

// ---- filtering & sorting
{
  const rows = [
    { name: "Alpha", province: "Koshi", kv: "400", mva: "1,000" },
    { name: "Beta", province: "Bagmati", kv: "220", mva: "" },
    { name: "Gamma", province: "Koshi", kv: "132", mva: "45.5" },
    { name: "Delta", province: "Koshi", kv: "220", mva: "300" },
  ];
  eq(DX.filterRows(rows, { filters: { province: "Koshi" } }).map((r) => r.name), ["Alpha", "Gamma", "Delta"]);
  eq(DX.filterRows(rows, { filters: { province: "Koshi", kv: "220" } }).map((r) => r.name), ["Delta"]);
  eq(DX.filterRows(rows, { filters: { province: "" }, query: "GAM" }).map((r) => r.name), ["Gamma"]);
  eq(DX.filterRows(rows, { query: "koshi", searchKeys: ["name"] }), []);
  eq(DX.sortRows(rows, "mva", "desc", true).map((r) => r.name), ["Alpha", "Delta", "Gamma", "Beta"], "numeric desc, blanks last");
  eq(DX.sortRows(rows, "mva", "asc", true).map((r) => r.name), ["Gamma", "Delta", "Alpha", "Beta"], "numeric asc, blanks last");
  eq(DX.sortRows(rows, "name", "asc").map((r) => r.name), ["Alpha", "Beta", "Delta", "Gamma"]);
  const sum = DX.summarize(rows, [{ key: "mva" }]);
  assert.equal(sum.count, 4);
  assert.equal(sum.totals.mva.total, 1345.5);
  assert.equal(sum.totals.mva.counted, 3);
}

// ---- dataset config is consistent with the shipped CSVs
{
  const ids = Object.keys(DX.DATASETS);
  for (const tab of DX.TABS) for (const id of tab.datasets) assert.ok(DX.DATASETS[id], `tab ${tab.id} -> ${id}`);
  eq(DX.TABS.map((t) => t.id), ["substations", "hydro", "tariffs", "nonhydro", "anchors"]);
  const expectedRows = { substations: 153, hydro: 87, tariffs: 223, nonhydro: 161, anchors: 20 };
  for (const id of ids) {
    const ds = DX.DATASETS[id];
    const file = path.join(ROOT, "wiki/explorer/tables", ds.file);
    assert.ok(fs.existsSync(file), `shipped table ${ds.file}`);
    const parsed = DX.parseCSV(fs.readFileSync(file, "utf8"));
    for (const col of ds.columns.concat(ds.filters, ds.sums)) assert.ok(parsed.columns.includes(col.key), `${id}.${col.key}`);
    if (expectedRows[id]) assert.ok(parsed.rows.length >= expectedRows[id], `${id} rows ${parsed.rows.length}`);
  }
}

// ---- lazy loading: fetch only on open/load, once per dataset (cached)
(async () => {
  const fetched = [];
  const fakeFetch = (url) => {
    fetched.push(url);
    return Promise.resolve({ ok: true, text: () => Promise.resolve("slug,substation_name,highest_voltage_kv,status,province,district,installed_mva,planned_additional_mva,linked_solar_award_mw,latitude\ns1,One,400,operating,Koshi,Morang,100,,,26.5\n") });
  };
  const explorer = DX.createExplorer({ fetchImpl: fakeFetch });
  assert.equal(fetched.length, 0, "createExplorer must not fetch");
  const a = await explorer.load("substations");
  const b = await explorer.load("substations");
  assert.ok(a === b, "cached parse is reused");
  eq(fetched, ["tables/substation_specs.csv"]);
  eq(DX.DATASETS.substations.action(a.rows[0]), { kind: "fact", id: "substation:s1", label: "Show on map" });

  // ---- index.html wiring guardrails
  assert.match(html, /<script src="shared\/data-explorer\.js\?v=[\w-]+" defer><\/script>/);
  assert.ok(html.includes('id="data-tables-btn"'), "Tables button present");
  assert.ok(!/fetch\([^)]*tables\//.test(html), "index.html must not fetch table CSVs directly");
  const initBody = html.slice(html.indexOf("async function init()"));
  assert.ok(!/createExplorer\(/.test(initBody.slice(0, initBody.indexOf("url.tables"))), "explorer is not created eagerly during init");
  console.log("data-explorer tests passed");
})().catch((err) => { console.error(err); process.exit(1); });
