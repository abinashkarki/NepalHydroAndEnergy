# Naxa promoter identity audit

This is a read-only audit of the promoter/company field from `data/raw/projects_storage/hydro_naxa_datasets.csv` into the saved deployed snapshots. It does not modify source data or generated assets. The snapshots are under `docs/audits/lalupate-pattern-2026-09-09/evidence/` and were treated as the deployed artifacts for this audit.

## Result

The source CSV contains 572 rows and a nonblank `Promoter` value in all 572 rows. It contains 569 distinct project names; three names are duplicated as separate licensed records (`Ghunsa Khola HPP`, `Phalakhu Khola HPP`, and `Seti Khola HPP`). The saved display-point GeoJSON contains 572 features and the same 569 distinct project names, so the project-name join is complete at row level (572/572) and at distinct-name level (569/569).

Promoter identity is lost at the display-point boundary: none of the 572 display features has a `promoter` property, and none has a nonblank promoter value. This is a 572/572 row loss (100%) from the source field into the display-point asset. The display asset does retain a `developer` field only where it came from curated specs; just 10 display features have a nonblank developer value, which is a different field and does not restore the Naxa promoter column.

The fact snapshot contains 666 facts overall, 568 hydro-domain facts, and 560 facts whose `sources` include `hydropower_project_display_points`. Exact `fact.name == CSV.Project` matching gives 563 row pairs representing 560 distinct source project names. Nine of the 569 distinct source names have no exact-name fact. Of the 560 matched identities, 10 retain a nonblank `promoter` and 550 are blank: 550/560 (98.2%) matched identities lose promoter visibility. The 10 retained values are curated project-spec/company values merged into facts; they do not demonstrate retention of the Naxa promoter field through the display-point serializer.

The three duplicate source names collapse to one fact each, so pair counts must not be mistaken for identity counts. The 563 row pairs are therefore 3 more than the 560 matched identities, not 6. For the same reason, the fact-index denominator is 560 matched identities rather than 572 source rows.

## Reproducible method and counts

The following read-only Python calculation was used conceptually (paths are relative to the repository root):

```python
import csv, json
from collections import defaultdict

src = list(csv.DictReader(open(
    "data/raw/projects_storage/hydro_naxa_datasets.csv",
    encoding="utf-8-sig", newline="")))
display = json.load(open(
    "docs/audits/lalupate-pattern-2026-09-09/evidence/"
    "data__processed__maps__hydropower_project_display_points.geojson"))['features']
facts = json.load(open(
    "docs/audits/lalupate-pattern-2026-09-09/evidence/"
    "wiki__explorer__shared__wiki-fact-index.json"))['facts']
fact_display = [f for f in facts
                if 'hydropower_project_display_points' in f.get('sources', [])]
by_name = defaultdict(list)
for fact in fact_display:
    by_name[fact['name']].append(fact)
matched = [row for row in src if row['Project'] in by_name]
blank = [row for row in matched
         if not any((f.get('promoter') or '').strip()
                    for f in by_name[row['Project']])]
```

Observed outputs:

| Boundary / measure | Count | Denominator | Result |
|---|---:|---:|---:|
| CSV rows | 572 | — | source row count |
| CSV distinct project names | 569 | — | 3 duplicated names |
| Display features | 572 | 572 source rows | 100% row-level project-name coverage |
| Display distinct project names | 569 | 569 source names | 100% identity-name coverage |
| Display features with `promoter` key | 0 | 572 | 0% retained |
| CSV rows with nonblank `Promoter` | 572 | 572 | 100% available upstream |
| Fact records with display-point source | 560 | — | post-merge fact identities |
| Source names with exact display-source fact | 560 | 569 | 98.4% identity coverage |
| Source rows paired to exact-name facts | 563 | 572 | duplicates create 3 extra pairings over 560 identities |
| Matched fact identities with nonblank `promoter` | 10 | 560 | 1.8% retained |
| Matched fact identities with blank `promoter` | 550 | 560 | 98.2% lost |

The saved deployed display-point snapshot contains 572 features with the property shape counted above. The local generated display asset has the same row and identity counts, but the deployed snapshot is the authority for the reported deployed counts; the fact numbers use the saved deployed fact snapshot, not an in-memory rebuild.

## Representative company queries

These are exact project-name/attribute probes for the company field. The source value is present, while the deployed fact record is blank unless noted. The query wording is diagnostic; UI parsing and whether a plain-name query is treated as an attribute query are a separate interaction question.

| Diagnostic query | Exact source row(s) | Upstream `Promoter` | Deployed fact `promoter` |
|---|---:|---|---|
| “Who promotes Dana Khola Hydropower Project?” | CSV line 65 | Lalupate Hydropower Company Pvt. Ltd. | blank |
| “Who promotes Aayu Chhatigad Hydropower Project?” | CSV line 2 | Puwa Khola-1 Hydro Power Pvt.Ltd. | blank |
| “Who promotes Adhikhola Storage HEP?” | CSV line 4 | Nepal Electricity Authority | blank |
| “Who promotes Andhi Khola?” | CSV line 6 | Butwal Power Company | blank |
| “Who promotes Balephi?” | CSV line 17 | Balephi Jalbidhut Company Ltd | blank |
| “Who promotes Ghunsa Khola HPP?” | CSV lines 104–105 | Remit Hydro Ltd; RM Investment Company Pvt. Ltd. | blank; one fact after duplicate-name collapse |
| “Who promotes Phalakhu Khola HPP?” | CSV lines 325–326 | Betrawati Hydroelectric Co. Ltd; Rasuwa Hydropower Company Pvt Ltd | blank; one fact after duplicate-name collapse |
| “Who promotes Chilime?” | CSV line 57 | Chilime Hydropower Company Limited | `promoter` retained via curated specs (positive control) |

The Lalupate example is therefore directly representative of the broad pattern, while Chilime is a retained-field positive control. The duplicate examples also expose an identity hazard: exact project-name matching cannot distinguish separate promoter records when the registry repeats a project name.

The field-retention result is separate from query execution. In the deployed explorer snapshot, `matchNamedFacts` is defined at `evidence/wiki__explorer__shared__wiki-search.js:415` and the fact-like lookup gate is at `:277-288`; the name match does not infer a promoter value from the source CSV when the fact's `promoter` field is blank. A company/attribute query can therefore be affected by both the missing field and the query parser's decision about whether to perform an attribute lookup. This audit establishes the former; UI query behavior is a separate acceptance check.

The nine source names without an exact display-source fact are: `Mai Cascade HPP`, `Mewa khola HPP`, `Mugu Karnali HPP`, `Rawa Khola HEP`, `Rawa Khola HPP`, `Rolwaling Khola HPP`, `Sabha Khola A HEP`, `Thulo Khola Hydropower Project`, and `Upper Tamor HEP`. They are unmatched under exact spelling only; this audit does not classify them as absent from the wider fact index or assert that similarly named records are equivalent.

## Local cause

The builder reads `data/raw/projects_storage/naxa_hydropower_projects.geojson`, not the CSV directly, in `scripts/build_tributary_maps.py:3301-3303`. That GeoJSON carries the promoter upstream: `scripts/build_tributary_maps.py:3349` copies `props["promoter"]` into each internal project row. However, `hydropower_display_points_geojson()` constructs a new property allowlist at `scripts/build_tributary_maps.py:3003-3042`; its base properties include project, licence, capacity, location, and geography, while its enrichment allowlist at `scripts/build_tributary_maps.py:3006-3014` includes curated `developer` but not `promoter`. The serializer then emits only those selected properties at `scripts/build_tributary_maps.py:3022-3042`, dropping promoter before the GeoJSON is written.

The fact builder derives `promoter` from map properties (`scripts/build_wiki_fact_index.py:386`) and `developer` from map/spec properties (`scripts/build_wiki_fact_index.py:414`). Its curated specs overlay only accepts selected text fields (`scripts/build_wiki_fact_index.py:189-193`), including `developer` but not `promoter`; therefore the 10 retained promoter values come from other curated fact inputs/merges, while the Naxa display-point path supplies none. The merge retains a nonblank promoter only when some other source already has one (`scripts/build_wiki_fact_index.py:455-457`).

## Status and uncertainty boundary

The source CSV's `License Type` counts are Survey 311, Generation 180, and Operation 81. The display snapshot counts are Survey 311, Generation 177, and Operation 84, because the local builder applies named licence-type overrides (`scripts/build_tributary_maps.py:3305-3314`) and DoED status overlays. The display also exposes a richer, separately sourced `doed_status_display` classification: Generation licence 239, Operating record 201, Survey licence cancelled 24, Generation-licence application 23, Survey licence 18, Survey application cancelled 12, Generation licence cancelled 11, Survey-licence application 9, Government project under study 5, Generation application cancelled 3, and 27 records without that overlay field.

These status differences are not promoter evidence. The Naxa CSV is a registry/licensing snapshot with an unstated extraction date in the CSV itself; the display's DoED overlay is dated `2026-07-02` in the asset. A displayed status such as “Operating record” or “Survey licence cancelled” should therefore be read as the overlay's current classification at its stated update date, while the original CSV `License Type` remains historical/source context. No claim is made here that a promoter is current, legally controlling, or the same entity as a developer/owner.

## Evidence files and line locators

- Source rows and promoter values: `data/raw/projects_storage/hydro_naxa_datasets.csv:1-573` (header plus 572 data rows; representative rows listed above).
- Deployed display-point snapshot: `docs/audits/lalupate-pattern-2026-09-09/evidence/data__processed__maps__hydropower_project_display_points.geojson:1`.
- Deployed fact snapshot: `docs/audits/lalupate-pattern-2026-09-09/evidence/wiki__explorer__shared__wiki-fact-index.json:1`.
- Deployed query behavior: `docs/audits/lalupate-pattern-2026-09-09/evidence/wiki__explorer__shared__wiki-search.js:277-288` and `:415`.
- Builder input and promoter copy: `scripts/build_tributary_maps.py:3301-3349`.
- Display-point property selection: `scripts/build_tributary_maps.py:3003-3042`.
- Fact extraction and curated overlay: `scripts/build_wiki_fact_index.py:189-193`, `scripts/build_wiki_fact_index.py:348-386`, `scripts/build_wiki_fact_index.py:414-416`, and `scripts/build_wiki_fact_index.py:455-457`.
