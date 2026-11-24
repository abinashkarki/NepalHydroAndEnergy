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

1. **RPGCL georeference bias.** The committed RPGCL labels, linework, `place_anchor_index` and network nodes sit about 7–14 km south of the true position. 11 substation rows were re-derived from the GeoPDF symbols, with the old values kept in their notes. The shared layers still carry the bias and need a separate fix in `extract_rpgcl_transmission_vectors.py`.
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
