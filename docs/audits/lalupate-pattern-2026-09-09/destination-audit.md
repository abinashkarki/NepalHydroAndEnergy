# Destination and capacity audit

This is a read-only audit of the seven deployed snapshots under `evidence/`, captured for the Lalupate-pattern review. Counts below were computed from the saved JSON; downloaded JavaScript was inspected as text only and was not executed.

## Destination coverage

The deployed fact index contains 666 facts in total, of which 568 are `domain: hydro` (fact-index snapshot, `stats` and `facts` in the single-line JSON file). Of those 568 hydro facts:

| Check | Count | Denominator | Result |
|---|---:|---:|---|
| Nonempty `wiki_slug` | 104 | 568 hydro facts | 18.3% have a wiki destination |
| Empty `wiki_slug` | 464 | 568 hydro facts | 81.7% are map/fact destinations only |
| Nonempty `slug` fallback | 104 | 568 hydro facts | No additional coverage beyond `wiki_slug` |
| Nonempty slug absent from `wiki-page-index.json` | 0 | 104 slugged hydro facts | No dangling page-index destination |
| Slugged fact also present in `bindings.json` | 103 | 104 slugged hydro facts | `kali-gandaki-upper` / Kaligandaki Upper is indexed as a page but has no map binding |

The 464 empty-slug records are not automatically broken links. In the deployed reader, `resultForFact()` assigns `kind: "fact"` when no slug exists (`wiki-search.js:351-364`), and the result renderer routes a fact result to `openFactDetail(factId)` with a `?fact=` URL (`index.html:3920-3928`). The fact detail explicitly presents “Map data only · no wiki page yet” when `wiki_slug` is empty (`index.html:4631-4637`). This makes a complete named fact such as Dana Khola a valid map-fact destination despite lacking a wiki page.

For comparison, the hydropower display snapshot contains 572 feature rows and 569 unique project names. It has no slug property in the feature properties; page/map linkage is supplied separately through bindings. The fact index therefore has a broader structured-record surface than the wiki-page surface. Examples of slugless hydro records include Budhi Gandaki Hydropower Project, Adhikhola Storage HEP, Seti Nadi-3, and Dana Khola Hydropower Project. All 464 slugless hydro facts have `tariff_npr_kwh: null`; this is a data absence, not a zero tariff.

## Capacity reconciliation

Exactly 44 of the 572 display feature rows (7.7%) carry all four reconciliation fields: `legacy_capacity_mw`, `current_official_capacity_mw`, `capacity_difference_mw`, and `capacity_reconciliation`. Every one is marked `dual_value_material_conflict`. In all 44 rows, the displayed `capacity_mw` equals the legacy value and differs from the current-official value; zero of 44 displayed values equals the current-official value.

The difference direction is mixed: 29 current values are higher and 15 are lower than legacy values. Differences range from -339.0 MW to +252.5 MW, with a median of +11.67 MW. Representative rows from the display snapshot are:

| Project | Display `capacity_mw` | Legacy | Current official | Difference |
|---|---:|---:|---:|---:|
| Dana Khola Hydropower Project | 19.0 | 19.0 | 49.95 | +30.95 |
| Bagmati Nadi | 22.0 | 22.0 | 32.0 | +10.0 |
| Betan Karnali HP | 688.0 | 688.0 | 439.0 | -249.0 |
| Upper Tamor HEP | 32.5 | 32.5 | 285.0 | +252.5 |

Joining by normalized project name finds a corresponding fact-index record for 43 of the 44 dual rows. The normalization used here is `lowercase` followed by removal of every character outside `a-z` and `0-9` (so punctuation and spacing are ignored). For all 43 joined rows, the fact/search `capacity_mw` exactly equals the legacy/display value and not the current-official value. Upper Tamor HEP is the one unmatched display name; the fact index instead contains `Upper Tamor` at 285.0 MW, with slug `upper-tamor`. Therefore the 44-row map reconciliation cannot be described as 44 matching search rows: 43 are exact normalized joins, while the remaining display row is an identity mismatch against a separate 285.0 MW search fact.

## Search and suppression mechanism

The deployed page loads the static lexical search index and fact index together (`index.html:5607-5627`) and sets `spatialSlugs` from the keys of `bindings.pages` (`index.html:5633-5635`). Each query first computes up to 30 lexical results and up to 8 structured fact results (`index.html:3538-3545`). `mergeFactResults()` emits all fact results first and suppresses a lexical result only when its nonempty slug has already appeared in the fact results (`index.html:3608-3619`). Thus a slugless fact does not suppress a lexical page result by slug, but it remains independently openable as a fact record.

For structured project-list queries, the first three structured results are placed before supporting lexical results (`index.html:3622-3628`). Source-seeking queries put source pages first, then structured results (`index.html:3629-3634`). A structured empty answer is allowed to yield to lexical analysis only when there is no explicit status/capacity/target/superlative/source constraint and lexical matches are editorial categories (`index.html:3636-3649`). Exact-title or slug matches are separately recognized for answer-card rendering (`index.html:3780-3795`).

Fact ranking uses `fact.capacity_mw` as its sole capacity metric: finite capacities sort before missing values and then descending by default (`wiki-search.js:317-348`); capacity constraints also test only `fact.capacity_mw` (`wiki-search.js:335-337`, `542-547`). Consequently, the 43 joined dual rows expose a concrete consistency risk: their primary map capacity and structured search agree on the legacy number, while the current-official number remains present only in map reconciliation fields and is not used for fact ranking, filtering, or the fact detail's displayed capacity (`index.html:4600-4610`).

The fact detail's tariff formatter converts `null` with JavaScript `Number(value)` before checking finiteness (`index.html:4071-4075`): `Number(null) === 0`, so a null `tariff_npr_kwh` is rendered as `NPR 0/kWh`. All 464 slugless hydro records are null in the captured fact data, meaning their fact detail can visibly display a zero tariff even though the stored value is missing; this is a presentation/data-typing issue, not evidence of a zero tariff.

## Caveats

The JSON snapshots are minified single-line artifacts, so their exact data evidence is file-level rather than human line-level: `evidence/wiki__explorer__shared__wiki-fact-index.json`, `wiki-page-index.json`, `bindings.json`, and `data__processed__maps__hydropower_project_display_points.geojson`. Counts above use the captured values and normalized-name joins; punctuation, abbreviations, and identity aliases can change join results. This audit does not claim that every map feature has a unique project identity, that a legacy value is wrong, or that a slugless fact should receive a wiki page.
