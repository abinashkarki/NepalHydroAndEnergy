#!/usr/bin/env node
"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

const ROOT = path.resolve(__dirname, "..");
const source = fs.readFileSync(path.join(ROOT, "wiki/explorer/shared/wiki-loader.js"), "utf8");
const window = {};
vm.runInNewContext(source, { window, console, Date, encodeURIComponent });

const {
  frontmatterScalar,
  frontmatterList,
  publicMaturity,
  renderPageStatus,
  renderSourceProvenance,
  renderClaimGovernance,
} = window.NepalExplorer;

const sourceFrontmatter = `
title: "Grid source: annual report"
maturity: verified-core
source_type: annual-report
source_author: Nepal Electricity Authority
source_date: 2025-07-15
source_url: https://example.test/report.pdf
verified_on: 2026-07-19
caveat: Figures are fiscal-year aggregates.
`;

assert.equal(frontmatterScalar(sourceFrontmatter, "title"), "Grid source: annual report");
assert.equal(publicMaturity(sourceFrontmatter), "verified-core");
assert.equal(publicMaturity("page_quality: flagship"), "verified-core");
assert.equal(publicMaturity("generator: auto-stub"), "registry-record");
assert.equal(publicMaturity("page_quality: analysis"), "working-page");

const blockList = `sources:
  - nea-annual-report-fy2024-25
  - doed-solar-power-plants-table`;
assert.deepEqual(
  Array.from(frontmatterList(blockList, "sources")),
  ["nea-annual-report-fy2024-25", "doed-solar-power-plants-table"],
);

const sourceCard = renderSourceProvenance(sourceFrontmatter);
assert.match(sourceCard, /Source provenance/);
assert.match(sourceCard, /Nepal Electricity Authority/);
assert.match(sourceCard, /2026-07-19/);
assert.match(sourceCard, /Open source/);
assert.match(sourceCard, /Figures are fiscal-year aggregates/);

const unsafeCard = renderSourceProvenance("source_url: javascript:alert(1)");
assert.doesNotMatch(unsafeCard, /href=/);

const omittedLocalCard = renderSourceProvenance("source_url: ../../../data/raw/research/report.pdf");
assert.doesNotMatch(omittedLocalCard, /href=/);
assert.match(omittedLocalCard, /Asset not included in public release/);

const omittedLocalCardWithStatus = renderSourceProvenance(`
source_url: /data/raw/research/report.pdf?download=1
source_access: archived copy
`);
assert.doesNotMatch(omittedLocalCardWithStatus, /href=/);
assert.match(omittedLocalCardWithStatus, /Archived Copy · Asset not included in public release/);

const bundledLocalCard = renderSourceProvenance("source_url: /wiki/assets/report.pdf");
assert.match(bundledLocalCard, /href="\/wiki\/assets\/report\.pdf"/);
assert.match(bundledLocalCard, /Open source/);

const pageStatus = renderPageStatus("maturity: working-page\nupdated: 2026-07-19\nreview_due: 2020-01-01");
assert.match(pageStatus.line, /Working Page/);
assert.match(pageStatus.line, /Review overdue/);

const claimCard = renderClaimGovernance(
  "seasonal-mismatch",
  `claim_id: C-TEST
confidence: medium
status: active
verified_on: 2026-07-19
sources: [nea-annual-report-fy2024-25, doed-solar-power-plants-table]`,
  {
    slugToTitle: {
      "nea-annual-report-fy2024-25": "NEA Annual Report FY2024/25",
      "doed-solar-power-plants-table": "DoED Solar Registry",
    },
  },
);
assert.match(claimCard, /Claim evidence/);
assert.match(claimCard, /C-TEST/);
assert.match(claimCard, /NEA Annual Report FY2024\/25/);
assert.match(claimCard, /DoED Solar Registry/);

console.log("OK: wiki reader metadata tests passed");
