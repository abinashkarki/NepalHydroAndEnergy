#!/usr/bin/env node
"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");

const ROOT = path.resolve(__dirname, "..");
const APP_DIR = path.join(ROOT, "internal", "dashboard");
const HTML_PATH = path.join(APP_DIR, "index.html");
const CSS_PATH = path.join(APP_DIR, "dashboard.css");
const JS_PATH = path.join(APP_DIR, "dashboard.js");
const CHARTS_PATH = path.join(APP_DIR, "dashboard-charts.js");
const DATA_PATH = path.join(ROOT, "data", "processed", "dashboard", "control-room.json");

function readRequired(filePath) {
  assert.ok(fs.existsSync(filePath), `required dashboard artifact is missing: ${path.relative(ROOT, filePath)}`);
  return fs.readFileSync(filePath, "utf8");
}

function assertUniqueNonblank(values, label) {
  assert.ok(values.every((value) => typeof value === "string" && value.length > 0), `${label} must be nonblank strings`);
  assert.equal(new Set(values).size, values.length, `${label} must be unique`);
}

const html = readRequired(HTML_PATH);
const css = readRequired(CSS_PATH);
const source = readRequired(JS_PATH);
const chartsSource = readRequired(CHARTS_PATH);
const dataText = readRequired(DATA_PATH);
const data = JSON.parse(dataText);

// Static DOM contract. A real-browser suite should complement this smoke test;
// these assertions deliberately need no npm dependencies.
for (const id of [
  "dashboard-main",
  "load-state",
  "dashboard-content",
  "view-overview",
  "view-coverage",
  "view-reconciliation",
  "view-monitoring",
  "view-sources",
  "project-detail",
  "detail-body",
  "export-view",
]) {
  assert.match(html, new RegExp(`id=["']${id}["']`), `index.html must expose #${id}`);
}

for (const view of ["overview", "coverage", "reconciliation", "monitoring", "sources"]) {
  assert.match(html, new RegExp(`data-view=["']${view}["']`), `index.html must expose the ${view} view`);
}

assert.match(html, /<meta[^>]+name=["']robots["'][^>]+content=["'][^"']*noindex/i, "internal dashboard must be noindex");
assert.match(html, /<script[^>]+src=["']\.\/dashboard\.js["']/i, "index.html must load the local dashboard runtime");
assert.match(html, /<script[^>]+src=["']\.\/dashboard-charts\.js["']/i, "index.html must load the local chart runtime");
assert.match(html, /<link[^>]+href=["']\.\/dashboard\.css["']/i, "index.html must load the local dashboard stylesheet");
assert.doesNotMatch(html, /<(?:script|link)[^>]+(?:src|href)=["']https?:\/\//i, "dashboard must not load third-party scripts or styles");

assert.match(css, /@media\s*\([^)]*max-width/i, "dashboard.css must define a small-screen layout");
assert.match(css, /prefers-reduced-motion/i, "dashboard.css must honor reduced-motion preferences");
assert.match(css, /44px/, "dashboard.css must include a 44px touch-target rule");

assert.match(source, /control-room\.json/, "runtime must fetch the generated control-room artifact");
assert.match(source, /URLSearchParams/, "runtime must support URL-addressable state");
assert.match(source, /popstate/, "runtime must restore state during browser history navigation");
assert.match(source, /Escape/, "runtime must support Escape-to-close for project details");
assert.match(source, /textContent/, "runtime must provide a text-only insertion path for untrusted data");
assert.doesNotMatch(source, /fetch\s*\(\s*["']https?:\/\//, "runtime must not fetch third-party resources");
for (const chart of ["overviewSignals", "coverageHeatmap", "capacityParity", "monitoringTimeline", "sourceReliance"]) {
  assert.match(chartsSource, new RegExp(`\\b${chart}\\b`), `chart runtime must expose ${chart}`);
}
assert.doesNotMatch(chartsSource, /fetch\s*\(/, "chart runtime must remain local and data-driven");

// Generated data contract and aggregate reconciliation.
assert.equal(data.schema_version, 1, "unsupported dashboard schema version");
assert.ok(/^\d{4}-\d{2}-\d{2}$/.test(data.data_as_of), "data_as_of must be an ISO date");
assert.ok(Array.isArray(data.inputs) && data.inputs.length > 0, "input provenance must be present");
for (const input of data.inputs) {
  assert.ok(typeof input.path === "string" && input.path.length > 0, "input path must be nonblank");
  assert.match(input.sha256, /^[0-9a-f]{64}$/, `input hash is invalid for ${input.path}`);
}

const coverage = data.coverage.projects;
const monitoring = data.monitoring.projects;
const sources = data.sources.records;
assert.ok(Array.isArray(coverage), "coverage.projects must be an array");
assert.ok(Array.isArray(monitoring), "monitoring.projects must be an array");
assert.ok(Array.isArray(sources), "sources.records must be an array");
assert.equal(data.overview.specifications.projects, coverage.length, "specification summary must match coverage rows");
assert.equal(data.overview.monitoring.projects, monitoring.length, "monitoring summary must match project rows");
assert.equal(data.overview.corpus.source_pages, sources.length, "source summary must match source rows");
assertUniqueNonblank(coverage.map((row) => row.slug), "coverage project slugs");
assertUniqueNonblank(monitoring.map((row) => row.slug), "monitoring project slugs");
assertUniqueNonblank(sources.map((row) => row.slug), "source slugs");

for (const queueName of ["doed_review", "doed_missing_operating", "hydromap_active_review", "capacity_conflicts"]) {
  const rows = data.reconciliation[queueName];
  assert.ok(Array.isArray(rows), `${queueName} must be an array`);
  assertUniqueNonblank(rows.map((row) => row.queue_id), `${queueName} queue IDs`);
}

// Hard local-app budgets keep the control room lightweight and prevent the
// full official registry from being accidentally embedded into first load.
const dataBytes = fs.statSync(DATA_PATH).size;
const totalBytes = [HTML_PATH, CSS_PATH, JS_PATH, CHARTS_PATH, DATA_PATH]
  .map((filePath) => fs.statSync(filePath).size)
  .reduce((total, size) => total + size, 0);
assert.ok(dataBytes <= 750_000, `control-room.json exceeds 750 KB (${dataBytes} bytes)`);
assert.ok(totalBytes <= 1_000_000, `dashboard first-load assets exceed 1 MB (${totalBytes} bytes)`);

console.log(
  `OK: internal dashboard static/runtime contract (${coverage.length} coverage rows, `
  + `${monitoring.length} monitored projects, ${sources.length} sources, ${totalBytes} bytes)`,
);
