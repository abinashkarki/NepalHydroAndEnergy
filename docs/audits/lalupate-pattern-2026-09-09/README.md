# Lalupate-pattern audit — 9 September 2026

Investigation only. No production code, wiki pages, datasets, or deployment were changed. Two GPT-5.6 Luna agents handled bounded data audits; the coordinator tested the live UI, checked the findings, and owns this synthesis. One agent exhausted its quota during corrections; the coordinator completed those locally.

## What this investigation establishes

Lalupate is a reproducible example of several distinct problems. They should not be treated as one missing-keyword problem or as grounds for automatically creating hundreds of wiki pages.

| Pattern | Evidence and extent | Interpretation |
|---|---|---|
| Promoter data is dropped | All 572 source CSV rows have a promoter; all 572 deployed display features omit `promoter`. Of 560 exact-name matched fact identities, 550 have blank promoters. | Systematic loss of an available source field. Historical promoter identity still needs provenance; it is not automatically current ownership. |
| Plain project names can bypass fact search | `Dana Khola` and `Suti Khola` show unrelated results initially; adding `Hydropower Project` puts the correct record first. | A separate search-intent problem. Retaining company data alone will not solve it. |
| Unknown becomes zero | Dana Khola's fact reader shows `NPR 0/kWh` although its tariff is null. All 464 hydro facts without wiki slugs have null tariffs and use this reader path. | Confirmed formatting defect, with 464 records exposed; only Dana was opened in the UI for this check. |
| Reconciliation is lost across surfaces | 44 map feature rows preserve conflicting historical/current-official capacities. 43 join to fact records by normalized name, and all 43 use the historical capacity. The fact records omit the reconciliation context. | Search, capacity filters and fact cards can present a historical number without its newer competing evidence. Choosing an authoritative value is a separate evidence decision. |
| Repeated project names collapse | Ghunsa Khola HPP, Phalakhu Khola HPP and Seti Khola HPP each have two registry rows with different licence numbers, capacities and promoters, but one exact-name fact. | Identity ambiguity to investigate before company aliases or merging rules are expanded. This audit does not resolve whether each pair represents different schemes, revisions or other registry relationships. |

## Correction to the initial diagnosis

A missing wiki page is not a missing destination. There are 568 hydro facts: 104 have wiki slugs and 464 use map/fact records. None of the 104 wiki slugs is absent from the deployed page index. The live Dana Khola result opens a working `?fact=` reader stating “Map data only · no wiki page yet.” A dedicated page may improve coverage, but it is not a prerequisite for finding the existing record.

One of the 104 slugged hydro facts, `kali-gandaki-upper`, lacks a map binding. That is a linkage observation, not proof of a broken reader.

## Actual browser checks

| Query | Observed deployed behavior |
|---|---|
| Lalupate | No matches, confirmed in the initial investigation on the same date. |
| Nilganga | No matches. The source registry associates it with Suti Khola. |
| Sayapatri | No matches. The source registry associates it with Daram Khola-A. |
| Dana Khola | Unrelated corridor first, followed by other Khola projects; Dana absent from initial visible results. |
| Dana Khola Hydropower Project | Correct fact first; opens successfully; 19 MW and an erroneous zero tariff shown. |
| Suti Khola | Other Khola projects in the initial results. |
| Suti Khola Hydropower Project | Correct fact first, 17 MW. |
| Upper Tamakoshi | Positive control: correct best match and wiki destination, with evidence links. |

These are selected diagnostic examples, not a representative failure-rate sample. No current engineering, operating-status, ownership or tariff research was performed for the additional projects.

## Mechanisms established

1. The local map builder reads a Naxa GeoJSON and retains `promoter` internally, then omits it from the display-feature serializer. The corresponding CSV provides a convenient matching source table; it is not the direct input to this builder. Other curated sources restore a few company values downstream.
2. In deployed `wiki-search.js`, `matchNamedFacts` checks project names only. Even a recognized name does not by itself enable structured lookup: `targetedLookup` requires additional source/attribute/status/capacity intent, and `factish` has additional gates (lines 265–297). This explains why a plain short name can miss a fact that a longer project phrase exposes. Company lookup therefore has both data and search-rule gaps.
3. Deployed `formatTariff` calls `Number(value)`; `Number(null)` is zero, which passes the finite-number check. The reader then renders that string. Unknown tariff must not be interpreted as evidence of free electricity.
4. Capacity selection for fact ranking/filtering uses `capacity_mw`. Map reconciliation fields do not survive into the corresponding fact record. Dana is 19 versus 49.95 MW; Betan Karnali is 688 versus 439 MW in the captured map data. These are stored source differences, not newly verified project specifications.

## Identity cases worth resolving before implementation

The source has 572 rows but 569 distinct project names. Examples requiring licence-aware treatment:

| Repeated name | Source licence/capacity/promoter pairs |
|---|---|
| Ghunsa Khola HPP | 737 / 71.5 MW / Remit Hydro; 991 / 155.82 MW / RM Investment |
| Phalakhu Khola HPP | 162 / 14.7 MW / Betrawati Hydroelectric; 161 / 5 MW / Rasuwa Hydropower |
| Seti Khola HPP | 205 / 3.5 MW / Parbat Paiyu Khola Hydropower; 803 / 30 MW / Vision Lumbini |

Nine source names have no exact-name fact. That does not establish nine missing projects: renamed/merged records can account for some. In particular, `Upper Tamor HEP` is 32.5 MW in the map's historical field, whereas the differently named `Upper Tamor` fact is 285 MW. The per-lane reports distinguish exact-name absence from absence of a project.

## Decision scope for the next phase, not fixes already chosen

Before implementation, settle four contracts:

- Identity: how source record IDs, licence numbers, project identities and historical/current company relationships are kept distinct; how ambiguous names produce multiple candidates.
- Retrieval: which ordinary project and company queries must return existing records, including those without articles; unrelated fallback matches must remain distinguishable.
- Evidence display: how unknown values and competing dated values appear consistently in search, filters, map cards and fact readers.
- Coverage: when a registry fact is sufficient and when a researched wiki article is warranted. Empty page slugs alone should not drive bulk page creation.

A later acceptance set can reuse the eight UI queries above, the three duplicate-name cases, the 44 capacity-conflict rows and null-tariff records. This audit does not authorize an automatic value replacement, broad rebuild or deployment.

## Evidence and limits

- [Identity audit](identity-audit.md): source-field retention, counts, local builder trace and source caveats.
- [Destination/capacity audit](destination-audit.md): destination counts, capacity joins and rendering/ranking source references.
- [UI log](ui-checks.json): observed interaction outcomes.
- [Snapshot manifest](evidence/manifest.json): seven downloaded deployed assets, URLs, sizes and SHA-256 hashes.

The checkout is dirty and behind its recorded origin/main reference. Six of seven downloaded assets differ byte-for-byte from local counterparts; only display GeoJSON matches. Deployed counts and behavior therefore come from the saved deployed assets and live browser. Local builder code is a candidate causal trace, not proof of the exact deployed build revision. Source dates are retained as source dates; this is not an assertion that July registry status is current in September.
