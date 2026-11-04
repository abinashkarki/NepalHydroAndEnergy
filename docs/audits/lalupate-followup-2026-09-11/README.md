# Stage-one follow-up — 11 September 2026

Fixed the three authorized review items locally:

1. Makefile test target now runs tests/test_lalupate_stage_one.js; release-check depends on test.
2. Search maps licensed/licenced/licence/license to the corpus licensed bucket rather than survey. Explicit survey licence/license phrases retain survey matching. This changes query interpretation, not any project's source status.
3. Empty structured answers have no open-best-match or map actions, including source-seeking queries with lexical fallback. Related reading remains available below, explicitly identified as not satisfying all constraints.

Scope: Makefile, wiki/explorer/shared/wiki-search.js, wiki/explorer/index.html, tests/test_lalupate_stage_one.js, this report and test log. Search cache token updated. Unrelated checkout edits preserved. No deployment, index rebuild, capacity or company-data changes.

Validation: focused stage-one and follow-up regressions passed; structured intent suite and six Python search-runtime tests passed; internal dashboard JS tests passed. Browser at http://127.0.0.1:8765/wiki/explorer/ confirmed licensed Dana Khola returns the Generation licence fact first; Dana Khola over 20 MW shows an empty answer without action buttons. Formatter/short-name regressions remain passing. Production answer-card tests cover empty and ordinary lexical actions.

Full make test ran 95 Python tests and stopped with one failure: tests.test_static_seo.StaticSeoPilotTests.test_generated_outputs_are_current. Five generated SEO pages are stale; see make-test.log. The later Node/search commands were run separately because make stopped before reaching them. No claim of a green full release gate. Original stage-one delivery hashes describe the earlier version and are intentionally not rewritten.
