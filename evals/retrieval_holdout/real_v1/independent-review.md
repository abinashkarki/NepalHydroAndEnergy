# Nepal Energy retrieval holdout v1: independent internal reviewer pass

Review completed before candidate-system inspection or execution.

The reviewer is a second simulated internal role, not an external participant. This is an adversarial assessor pass performed within the evaluation process; it is not user research and does not claim independence at the level of a separately recruited human judge.

## Reviewer stance

The simulated reviewer acted as a skeptical information-retrieval evaluator with three priorities:

1. Would a real member of the assigned persona plausibly ask the query in this wording?
2. Does a relevance grade reflect how fully the page answers the stated need, rather than keyword overlap?
3. Are source pages, entity pages, synthesis pages, and data pages being distinguished by their actual utility?

The reviewer did not inspect generated search indexes, candidate-system code, aliases, rankings, or run output.

## Disagreements and resolutions

| Query | Challenge | Resolution |
|---|---|---|
| real-v1-01 | A reviewer initially proposed making any page mentioning both imports and exports grade 2. | Rejected. Grade 2 requires a substantial explanation of the seasonal mechanism; incidental trade figures remain grade 1. |
| real-v1-03 | “Household energy” could be confused with electricity sales rather than total residential fuel use. | Keep the natural wording. Grade `data-final-energy-mix` highest because it gives the residential fuel matrix; `data-domestic-demand` is supporting only. |
| real-v1-07 | “Immediate bottleneck” is a contestable thesis rather than a neutral fact. | Keep the query because policy students plausibly ask for evidence behind a prominent claim. Grade claim/synthesis pages for directly presenting the argument and evidence, with caveats preserved. |
| real-v1-10 | A source page and a derived data page were initially treated as interchangeable. | Grade the reusable time-series data page 3 and the annual report 2: the former directly satisfies the dataset request, while the latter is an upstream annual snapshot. |
| real-v1-12 | Original wording asked: “How much electricity does Sanima Mai generate, and what do its recent financials show?” The corpus has a strong generation/PPA record but only fragmentary company financials. | Rewrite before freeze to: “How has Sanima Mai's generation compared with its contracted energy, and what PPA rates does it receive?” This remains investor-realistic and avoids pretending the corpus contains a complete recent financial statement analysis. |
| real-v1-15 | “Major storage projects” has no universal cutoff and mixes committed, planned, and screening-stage schemes. | Retain the query but require pages to expose stage caveats. A shortlist or milestone page can be grade 3; individual project pages are supporting judgments. |
| real-v1-18 | The phrase “traced gaps” sounds like internal implementation vocabulary. | Retain it for the transmission-engineer persona, who plausibly asks about geometry provenance and confidence. Grade audit/QA pages, not generic corridor descriptions. |
| real-v1-19 | The corpus does not contain one current authoritative national bottleneck register. | Retain as a realistic difficult query. Grade pages that identify concrete New Khimti or Bharatpur constraints, and treat the historical capacity inventory as partial evidence. |
| real-v1-20 | Corpus pages conflict in how they describe Arun-3 evacuation: a project-specific Sitamarhi line versus the Inaruwa-Purnea strategic link. | Preserve both as judged relevant and document the ambiguity. Do not reconcile the corpus inside v1 judgments. |
| real-v1-21 | “Best primary source” could cause a synthesis page to outrank the primary report because it is easier to read. | Grade the NEA annual report source page 3. Derived profile and data pages are useful but lower because the user explicitly asks for a primary source. |
| real-v1-22 | Chameliya’s causal account relies partly on thin media source pages with incomplete citation metadata. | Keep them relevant but below the entity synthesis. Rationales explicitly note the metadata limitation. |
| real-v1-23 | The wording incorrectly risks treating 72,544 MW as “economically feasible.” | Keep the user’s claim-testing wording because the correct answer is that WECS labels it gross potential, while 32,680 MW is techno-economic. Pages that make this correction are highly relevant. |
| real-v1-24 | “Open access” can mean domestic grid access or Indian cross-border approval. | Interpret the query as cross-border export approval from context. The 2018 Indian guideline and India relationship pages are relevant; Nepal’s domestic open-access directive is judged non-relevant. |
| real-v1-27 | Original wording asked: “What benefits were communities promised under the Upper Karnali project agreement?” Available pages do not enumerate a defensible community-benefit package. | Rewrite before freeze to: “Why has the Upper Karnali project still not started, and what is holding up the project agreement?” This is a plausible local-stakeholder concern and is directly supported by the PDA/court record. |
| real-v1-29 | The intervention page contains current conflict-resolution detail but is partly prescriptive. | Grade it 3 because it directly explains compensation, right-of-way disputes, mediation, and the legal change; lower grades apply to corridor and bottleneck pages. |
| real-v1-30 | GLOF risk is important to Dudhkoshi but does not answer resettlement. | Grade the Dudhkoshi entity highest, the proposal record next, and GLOF/storage pages as supporting only. |

## Final reviewer conclusions

- All six personas remain distinct in expertise and information need.
- The final set contains exactly five queries per persona and exactly 30 total.
- Query wording varies between conversational, technical, commercial, source-verification, comparative, and multi-constraint forms.
- Every query has at least one page judged grade 2 or 3.
- Zero grades are used selectively to capture plausible lexical decoys or scope confusions; they are not exhaustive corpus negatives.
- Relevance labels are internal judgments based on direct wiki-page reading. No system ranking informed query drafting, review, or grading.
