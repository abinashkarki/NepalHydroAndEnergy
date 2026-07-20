# V1 implementation log

## 2026-07-19 — standalone baseline

- Copied the governed wiki, explorer runtime, selected assets, runtime map layers, curated data inputs and focused build/test scripts into an independent sibling repository.
- Excluded documentary, raw source corpora, bulk GIS inputs, caches, local outputs, screenshots and unrelated internal/deployment surfaces.
- Baseline source validator: passed in the original repository.
- Baseline standalone validator: passed after including `wiki/schema.md` and `wiki/log.md`, which are explicit public-language validation inputs.
- Source repository modified: no.

## 2026-07-19 — Priority 0 trust repair

- Retired the unsupported national daily curtailment estimate and stale Hetauda remaining-tower counts across the canonical claim, corridor entity, journalist landing and transmission policy surface.
- Added a primary-source-bounded July 2026 NEA construction-notice record.
- Rebuilt the transmission intervention as a Decision Dossier and documented the transfer limits of the Bharatpur–Bardaghat mediation comparison.
- Added a machine-enforced downstream retired-claim scan to `make validate`.

## 2026-07-19 — Priority 1 provenance and maturity

- Introduced the public three-class maturity model: Verified Core, Working Page and Registry Record.
- Added `wiki/core-pages.json` as the targeted 14-page V1 flagship registry.
- Added explicit excerpts, caveats, review dates and provenance metadata to the flagship spine and its priority sources.
- Added visible source and claim evidence cards, freshness states and bounded evidence wording in the explorer.
- Promoted five project pages to lighthouse dossiers with dated status/performance provenance while keeping them Working Pages where evidence remains incomplete.

## 2026-07-19 — Priority 2 editorial spine and explorer

- Added a neutral [[state-of-the-system]] page above the explicitly editorial [[master-thesis]].
- Added flagship branches for hydropower, transmission/trade, distribution/reliability, solar, storage/flexibility, demand/electrification, institutions/finance/delivery, environmental/social impacts, and climate/decarbonization.
- Converted all five interventions into six-section Decision Dossiers and added a public dossier index/navigation path.
- Added generated long-page navigation, quieter/collapsible backlinks and explicit excerpts.
- Fixed structured-search facet leakage and added safe lexical fallback so analysis is not misreported as “no record.”

## 2026-07-19 — Priority 3 selective depth

- Added a V1 solar evidence schema and deterministic CSV migration: 25 operating-registry records (141.74 MW) remain separate from 63 award-only records (960 MW) whose delivery status is unknown.
- Replaced the misleading single solar completeness tier with independent lifecycle, output, geography and provenance axes.
- Removed unsupported 2–3 year and 2028/2032/2035 solar projections from the governed claim dependency registry; the associated claim now remains a medium-confidence qualitative hypothesis.
- Added compact source-linked indicator and evidence-gap registers for distribution/reliability, demand/electrification and flexibility.
- Removed an unsupported electric-cooking demand scenario from the observed-data page.

## 2026-07-19 — final release gate

- Regenerated all page, metadata, backlink, fact, claim-governance, lexical-search and vector caches at 418 pages.
- Full release gate passed: 418 pages, 666 structured facts, 16 governed claims, 81 Python tests, structured-search Node tests, generated-asset ownership, source Used By, retired-claim scan and diff hygiene.
- Reader metadata, JavaScript syntax and seven browser-runtime tests passed separately.
- Visual QA passed at 1375×732 desktop and 390×844 mobile; mobile horizontal overflow was zero and no browser warnings/errors were observed.
- Verified source provenance, claim evidence, maturity labels, TOCs, collapsed backlinks and Decision Dossier identity in the rendered explorer.
- Confirmed the dry-season solar query safely returns lexical analysis rather than a false structured “no record” result.
- Original repository remained at source HEAD `ee6f4aea8ed4e7da935b63f5b4aeed97256a0139` with its pre-existing 258 status entries and 401 pages.

## 2026-07-20 — Find interface simplification

- Reduced the empty Find view to one search field, one short instruction and the existing seven browse sections.
- Removed the duplicated intent buttons, introductory feature card, page/source counts and repeated explanatory copy without changing the search engine, structured answers, filters or result ranking.
- Shortened the input placeholder to `Search this wiki…` and verified the revised surface at desktop and 390×844 mobile widths.
- Confirmed a `solar winter` query still returns results and that the browser console remains clear.
