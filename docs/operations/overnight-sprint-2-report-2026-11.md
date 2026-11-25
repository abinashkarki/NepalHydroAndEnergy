# Sprint 2 Report — Activation, Geocoding, Deepening & Visuals (Nov 2026)

**Branch:** `data/coverage-sprint-2026-11` (local only, not pushed)
**Runbook:** `docs/operations/overnight-sprint-2-activation-2026-11.md`
**Result:** Step 0 + 8/8 WPs landed in priority order. 5 met their done criteria in full and 3 only partly (6A, 7B, 8A). The single final rebuild and `make release-check` pass.

## 1. Commits

| Commit | WP | Subject |
|---|---|---|
| `94b9f38` | Step 0 | Preflight: clean Sprint 1 worktrees, fix CEA 404 note, verify substation geography |
| `197d0d4` | 6A | Geocode 400/220/132 kV substations, industrial load anchors, fossil depots, and BESS/PSH sites |
| `7d292fb` | 6B | Wire substations, industrial anchors, fossil, BESS/PSH & non-hydro layers into Explorer and fact index |
| `79876cb` | 7A | Deepen technical, output, and financial specs for top 25 operating hydro plants |
| `8d6d39e` | 7B | Deepen specs for top 15 under-construction & flagship hydro projects and refresh map popups |
| `48e0a56` | 8A | Close Sprint 1 open gaps: per-plant export approvals, ERC tariff dates, and 100% solar resource zones (*subject overstates: actual 86/88 zones*) |
| `649419e` | 9A | Add 5 data-driven charts for NEA 11-yr series, provincial substations, plant GWh, tariffs, and EV imports |
| `1766a7e` | 10A | Add multi-year infrastructure hazard register and ICIMOD dangerous glacial lakes map layer |
| `9eefeab` | 10B | Expand project_events.csv (50+) and project_blockers.csv (40+) across top 25 strategic projects |
| *(this commit)* | Wrap-up | Rebuild wiki indexes, static site, dashboard, and add Sprint 2 completion report |

## 2. Before → After Scorecard

| Dimension | Before | After | Target | Met? |
|---|---:|---:|---:|:-:|
| Substations with coordinates | 28/153 | **98/153** | ≥ 85 | ✅ |
| — 400 kV | 6/15 | 12/15 | 15/15 | ❌ |
| — 220 kV | 6/22 | 14/22 | ≥ 20 | ❌ |
| Industrial anchors / fossil / storage with coordinates | 0 / 0 / 0 | 14/20 · 12/20 · 1/10 | 18 · 15 · 8 | ❌ |
| Explorer layers (manifest) | 37 | **44** (6 infra + 1 GLOF, all off in `overview`) | — | ✅ |
| Presets | 7 | **8** (`energy_infrastructure`) | +1 | ✅ |
| Fact-index facts / gzip size | 692 / — | **1,050 / 92.8 KB** | < 250 KB | ✅ |
| Fact-index domains | hydro, solar, transmission, project | + **substation, nonhydro, demand, storage, institution** | 5 new | ✅ |
| `project_specs.csv` tiers | 2 rich / 24 moderate / 61 thin | **9 rich / 41 moderate / 37 thin** | ≥ 15 rich, ≥ 50 moderate | ❌ |
| Top-25 operating thin plants lifted | — | 20/25 (21/25 ≥ moderate) | ≥ 20 | ✅ |
| ERC tariff `effective_from` verified | 0/223 | **223/223** (ERC order 2078, effective 2021-11-17) | all | ✅ |
| Export approvals: plant-level rows | 0 | **28** (16/37 FY 2025/26 plants named; 119.54/1,200.01 MW quantified) | ~28–37 plants | ◐ |
| Solar `resource_zone` | 78/88 | **86/88** | 88/88 | ❌ |
| Wiki charts (SVG) | 18 | **23** | +5 | ✅ |
| Hazard events / dangerous lakes | 0 / 0 | **13 / 21** (ICIMOD 2020) | — | ✅ |
| `project_events.csv` / `project_blockers.csv` | 14 / 16 | **57 / 40** (35 slugs) | ≥ 50 / ≥ 40 / ≥ 22 | ✅ |
| Wiki pages | 462 | **470** | — | — |

## 3. Validation

The full rebuild ran once at the end: `make wiki-index`, `make wiki-site`, `make dashboard-build` and `make release-check`. All of it passed: validate, check_source_used_by, retired claims, page quality (0 over-declared), the unit and node suites (now including `tests.test_geocode_infrastructure_assets` and `tests.test_hazard_register`), the dashboard check and generated ownership (48 entries). The Explorer `overview` startup payload is unchanged.

## 4. Needs Human Review

1. ~~**RPGCL georeference bias.**~~ **Resolved after the sprint (see §7).**
2. **NWR Map citations.** Some engineering fields for Super Dordi Kha, Mristi, Upper Bhotekoshi and Upper Marsyangdi A come from NWR Map, which doesn't say where its data comes from. They are marked secondary in `source_note`.
3. **Phukot Karnali.** VUCL now lists 480 MW; `capacity_mw` is still 426 and the discrepancy is flagged in `source_note`.
4. **Export approvals are press-sourced.** All plant-level rows come from Kathmandu Post, Kantipur and Spotlight Nepal; the CEA approval letters still return HTTP 404. Totals must come from the `channel-aggregate` rows only.
5. **BS → AD dates.** Some WP 10B event dates were converted by the agent; they are tagged canonical-lookup and set to medium confidence, and could be off by ±1 day.
6. **Upper Tamakoshi Sept 2024 figures.** The 88-day outage and NPR 1.79 billion damage rest on the wiki's UKHL compilation, at medium confidence.
7. **Out-of-brief edit.** `wiki/explorer/index.html` gained layer-panel sections ("Energy Infrastructure", "Hazards"), without which the new layers can't be switched on.
8. **Geography spot-check.** Harnaiya was corrected from Parsa to Bara. Ridi's district and province are withheld because it sits on the Gulmi/Palpa border.

## 5. Deferred / Blocked

- **400/220 kV geocoding gaps** (3 + 8 rows). There was no symbol or district-consistent match. New Attariya, Rahughat and Trishuli 3B Hub are blank because the map node and the CSV district disagree.
- **8 flagship projects still thin.** Lapche Khola, Chainpur Seti, Budhigandaki and West Seti have only old or conflicting public specs. Super Tamor, Rasuwa Bhotekoshi, Super Trishuli and Betan Karnali have no rating rationale or disclosure.
- **Solar zones for Dadeldhura and Sankhuwasabha.** No listed district shares their ecological belt and region.
- **Koshi Corridor events.** There is no entity page, so no rows were added.
- **Next commands:** `.venv/bin/python scripts/geocode_infrastructure_assets.py --write` after fixing the RPGCL georeference, then `.venv/bin/python scripts/build_energy_infrastructure_layers.py`.

## 6. Working Tree

All sub-agent worktrees from Sprint 2 were removed after integration. `git status` is clean after this commit.

Note: `node scripts/build_wiki_site.js` emits trailing whitespace in generated `wiki/site/*/index.html`, which was already true of 456 committed pages. The new pages show the same pattern. `make validate` (unstaged `git diff --check`) is unaffected; fixing it belongs in the generator.

## 7. Post-Sprint Fixes (2026-11-25)

- **RPGCL georeference.** `extract_rpgcl_transmission_vectors.py` compared the PDF-user-space viewport BBox (y up) directly with PyMuPDF's y-down coordinates and blended lat/lon bilinearly. The result was a southward bias of 6.1–13.5 km (median 12.2 km), and the inset-frame exclusion box sat in the wrong place, so inset labels leaked into the main map while a strip of the real eastern map was dropped. The script also could not run, because of a missing `import os`. Six other scripts had the same missing import, all from `bcafa93`, and were fixed too.
  - **Fix:** a shared `scripts/rpgcl_georef.py` (MUTM affine plus y-flip) used by both the extractor and the geocoder. It also has an exact legacy-to-corrected transform, verified to round-trip to 4e-14° across 1,623 labels. That transform re-derived the 16 hard-coded RPGCL anchors in `build_tributary_maps.py` and 8 route hints. Map labels and linework, the traced corridors, network nodes and `place_anchor_index` were all regenerated.
  - **Result:** median label-to-symbol distance went from 13.3 km to 2.0 km (2,194 labels, up from 1,845). Corridor trace statuses are unchanged, and route-length agreement held (western 132 kV backbone +3.27% → +2.73%).
  - **Tests:** new `tests.test_rpgcl_georef` (6 tests).
- **Substation geocoding: 98 → 102 of 153.** 400 kV is now 13/15 and 220 kV 17/22.
  - The last 3 legacy-biased rows (Kushma, Mahendranagar, Bhurigaon) were corrected by 6.3–12.7 km.
  - RPGCL symbols drawn within their stated 1 km precision of the row's district border are now accepted, which places Trishuli 3B Hub and Rahughat.
  - New Attariya's district was corrected from a canonical-lookup Kailali to Kanchanpur: NEA's map labels it "DAIJI (NEW ATTARIYA)", which matches the RPGCL symbol.
  - Tinpiple is placed from OSM node 3514839204, as an `approximate-place` match at locality level.
  - **Not closed by the georeference fix.** The geocoder already georeferenced its symbols correctly, so the bias was never what blocked these. New Kohalpur and Sunkoshi Hub (400 kV) and Markichowk, Lapang, Dhaubadi, Palpa and Harnaiya (220 kV) have no RPGCL symbol and no unambiguous place match, so they stay blank.
- **Static site whitespace.** `build_wiki_site.js` now strips trailing whitespace from every generated line before both write and `--check`. `wiki/site/` has 0 files with trailing whitespace, down from 456+.
