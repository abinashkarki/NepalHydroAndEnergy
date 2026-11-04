# Lalupate-pattern stage one — verified local implementation

Implemented on 10 September 2026 in the existing checkout. No deployment, publication, commit, staging, worktree, data rebuild, or source-data change. Original September 9 audit evidence is intact: all seven snapshot hashes verified before and after implementation.

## Result

| Case | Local before | Verified local after |
|---|---|---|
| Dana Khola | Unrelated Dana–Kushma corridor best match | Correct Dana fact first; opens `?fact=hydro:dana-khola-hydropower-project` |
| Suti Khola | Unrelated IPO Hydropower Bailout best match | Correct Suti fact first; opens `?fact=hydro:suti-khola-hydropower-project` |
| Full Dana/Suti names | Correct records available | Same correct records and destinations |
| Null tariff in Dana reader | NPR 0/kWh | Tariff: Not available; also checked in Suti reader |
| Actual zero tariff | NPR 0/kWh | NPR 0/kWh, separately regression-tested |
| Upper Tamakoshi | Wiki best match | Structured answer, 456 MW, two evidence links; correct existing wiki page |
| Seasonal mismatch | Editorial best match | Same editorial best match and wiki destination |

The current local corpus has 568 hydro facts, 464 without wiki slugs. These records already have fact-reader destinations. Six of the seven local assets still differed from the saved deployed snapshots at task start; the display GeoJSON matched. Public behavior has not been reverified or changed by this implementation.

## Exact implementation scope

- `wiki/explorer/shared/wiki-search.js`: allow recognized plain project names to activate targeted retrieval. Every query token must belong to one matched name; adding editorial subject words does not independently enable fact lookup. Existing name matching, ranking, source/attribute gates, and status/capacity filters remain in place.
- `wiki/explorer/index.html`: reject absent, blank, nonnumeric and non-scalar tariff values before number conversion; show “Not available” for unknown. Update the search-script version token because browser reload initially retained the old script.
- `tests/test_wiki_search_intents.js`: update the earlier plain Upper Karnali expectation to its single correct structured record, preserving the protection against a basin-wide list.
- `tests/test_lalupate_stage_one.js`: new real-corpus search and production-formatter regressions, including correct first result, slugless destinations, covered/editorial controls, constraints, missing/null/blank/invalid versus numeric/string zero and positive tariffs.
- This delivery note. Local QA artifacts are under `output/playwright/lalupate-stage-one/`; Playwright also wrote its usual `.playwright-cli/` session artifacts.

Both production files and the existing intent test already contained local work. The checkout was on `main`, 0 ahead / 16 behind its recorded `origin/main`; no fetch, reset, or merge was performed. Use the [task-only production patch](../../../output/playwright/lalupate-stage-one/production.patch), not the aggregate Git diff, to inspect this task's production edits.

## Verification

Passing commands: `node tests/test_lalupate_stage_one.js`, `node tests/test_wiki_search_intents.js`, `python3 scripts/test_explorer_search_runtime.py` (six tests), and `git diff --check`. The two existing suites and whitespace check also passed before editing. The new Dana regression failed against the original code. [Before/after runtime comparison](../../../output/playwright/lalupate-stage-one/baseline-comparison.json) independently records both original defects.

Actual headed Chromium checks at 1440×900 used text entry and clicks: all four Dana/Suti short/full queries and fact destinations; Upper Tamakoshi and Seasonal Mismatch wiki destinations; source and capacity attribute queries; operating status, capacity exclusion, conflicting statuses, storage above 500 MW, and an editorial phrase containing Upper Tamakoshi. A 390×844 Find → Suti search → Read interaction passed and its screenshot was visually inspected. Basin layer toggle state persisted through zoom and restored; Minimal/Overview preset switching worked. These are browser checks, separate from static tests.

Evidence: [project interactions](../../../output/playwright/lalupate-stage-one/browser-after-projects.txt), [controls](../../../output/playwright/lalupate-stage-one/browser-after-controls.txt), [mobile](../../../output/playwright/lalupate-stage-one/browser-mobile.txt), [layer toggle](../../../output/playwright/lalupate-stage-one/layer-check.txt), [desktop image](../../../output/playwright/lalupate-stage-one/dana-desktop.png), [mobile image](../../../output/playwright/lalupate-stage-one/suti-mobile.png), [asset comparison](../../../output/playwright/lalupate-stage-one/asset-comparison.json).

## Remaining limitations and pre-existing issues

- CARTO basemap imagery contains “API KEY REQUIRED” watermarks. The semantic-search dependency emits two content-length warnings and two ONNX provider warnings logged at error level. Both reproduce with the saved pre-edit HTML/JS served against the same local assets: [baseline image](../../../output/playwright/lalupate-stage-one/baseline-map.png), [baseline console](../../../output/playwright/lalupate-stage-one/console-baseline.log), [after console](../../../output/playwright/lalupate-stage-one/console-after.log). No new application exception was observed.
- Existing status vocabulary maps the word `licensed` to `survey`, while Dana's fact status is `licensed`. Thus `licensed Dana Khola` returns no structured record before and after this patch. This is a separate vocabulary defect, recorded rather than changing status semantics in stage one.
- Explicit capacity exclusion still gives an empty structured answer with supporting lexical results and an “Open best match” action. This existing fallback behavior was preserved; it is not evidence that a returned editorial result satisfies the capacity constraint.
- Name aliases, company/promoter relationships, duplicate identities, capacity authority, missing registry identities, and wiki coverage remain outside this stage. Dana's displayed 19 MW is unchanged, not an authoritative capacity selection. No generic alias or company-search expansion was added.
- No generated assets changed, so no index/map rebuild was run. Full release checks and public deployment remain a separate decision.

Inspect the running [local preview](http://localhost:8765/wiki/explorer/?q=Dana+Khola&fact=hydro%3Adana-khola-hydropower-project). Restart it with `./wiki/explorer/serve.sh 8765` if needed.
