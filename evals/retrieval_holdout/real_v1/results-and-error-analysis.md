# Nepal Energy retrieval holdout v1: results and error analysis

## Evaluation status

- Query set: `nepal-energy-real-v1-30`
- Frozen at: `2026-06-20T07:38:00Z`
- Frozen query-set SHA-256: `ad77ea74883e6c80977bc64a752480457d9bb60de6f260d76a5b6f89109f198f`
- Run: `explorer-static-real-v1`
- Adapter execution: one read-only execution after freeze
- Run generated at: `2026-06-20T07:40:55.189121+00:00`
- Ranked depth: 30 documents per query
- Scoring cutoffs: 1, 3, 5, 10

No aliases, ranking logic, generated indexes, queries, or judgments were changed after the run. Personas are simulated and all judgments are internal; this evaluation is not external user research.

## Overall results

| Metric | Result |
|---|---:|
| Hit@1 | 0.633333 |
| Hit@3 | 0.800000 |
| Hit@5 | 0.866667 |
| Hit@10 | 0.966667 |
| MRR | 0.740171 |
| nDCG@1 | 0.538095 |
| nDCG@3 | 0.505938 |
| nDCG@5 | 0.545550 |
| nDCG@10 | 0.623710 |

Twenty-nine queries retrieved at least one judged-relevant document in the top 10. The only top-10 failure was `real-v1-15`, the storage-project roadmap query; its first judged relevant document was at rank 26.

## Results by simulated persona

| Persona | Hit@1 | Hit@3 | Hit@5 | Hit@10 | MRR | nDCG@10 |
|---|---:|---:|---:|---:|---:|---:|
| P1 — citizen/general reader | 0.60 | 0.80 | 1.00 | 1.00 | 0.750000 | 0.504622 |
| P2 — energy-policy student | 0.40 | 0.80 | 0.80 | 1.00 | 0.622222 | 0.614749 |
| P3 — investor | 0.60 | 0.60 | 0.60 | 0.80 | 0.629915 | 0.511281 |
| P4 — transmission engineer | 0.80 | 1.00 | 1.00 | 1.00 | 0.866667 | 0.724931 |
| P5 — journalist/source verifier | 0.80 | 0.80 | 1.00 | 1.00 | 0.850000 | 0.797959 |
| P6 — local/community stakeholder | 0.60 | 0.80 | 0.80 | 1.00 | 0.722222 | 0.588716 |

The strongest performance is for precise transmission and source-verification needs. The weakest persona is the investor, driven by poor ranking for general PPA rules and the storage-project portfolio query.

## Results by query type

| Query type | Queries | Hit@1 | Hit@3 | Hit@5 | Hit@10 | MRR | nDCG@10 |
|---|---:|---:|---:|---:|---:|---:|---:|
| attribute_lookup | 5 | 0.20 | 0.40 | 0.60 | 1.00 | 0.361111 | 0.259979 |
| comparative | 2 | 0.50 | 0.50 | 0.50 | 1.00 | 0.555555 | 0.471746 |
| conceptual | 7 | 0.714286 | 1.00 | 1.00 | 1.00 | 0.857143 | 0.724250 |
| exact_entity | 2 | 1.00 | 1.00 | 1.00 | 1.00 | 1.000000 | 0.745865 |
| multi_constraint | 5 | 0.80 | 0.80 | 0.80 | 0.80 | 0.807692 | 0.673260 |
| source_seeking | 9 | 0.666667 | 0.888889 | 1.00 | 1.00 | 0.805556 | 0.726680 |

Exact entities are reliably found. Attribute lookups have perfect eventual top-10 recall but poor early precision and grading quality. Multi-constraint performance looks strong in aggregate but contains the only top-10 miss.

## Concrete failure classes

### 1. Entity-list dominance over task intent

For `real-v1-15` (“Which major storage hydropower projects are on Nepal's roadmap, and what stage is each one at?”), ranks 1–10 were mostly individual project entities. The judged portfolio and milestone pages did not appear until rank 26 or below. The system matched “storage hydropower projects” but underweighted the roadmap-and-stage intent.

The same pattern affected:

- `real-v1-11`, where eight storage/project entities preceded `ppa-pricing` at rank 9.
- `real-v1-26`, where eight hydropower project entities preceded `environmental-flow-policy` at rank 9.

This suggests a broad project/fact route is overpowering policy, rules, and portfolio terms.

### 2. Resource geography confused with existing projects

For `real-v1-05` (“Which parts of Nepal have the best solar power potential?”), the first three results were a solar-zone entity followed by named operating/project entities; the judged concept page appeared at rank 4. Project location is being treated as a proxy for resource quality.

### 3. Weak early precision for named infrastructure attributes

`real-v1-19` asked for substations identified as capacity bottlenecks. A historical substation-capacity page appeared at rank 3, but higher-ranked material was broad project or bottleneck context. The specifically judged New Khimti and Bharatpur evidence did not reach the top 10.

### 4. Broad synthesis outranks verification sources

For `real-v1-24`, broad synthesis pages occupied the first three ranks. The directly relevant India relationship page appeared at rank 4 and the Indian policy source at rank 7. The query eventually succeeds, but a verifier must pass general narrative before reaching the governing-source page.

### 5. Good performance on exact names and distinctive figures

This is a positive error-analysis boundary rather than a failure. Exact-entity questions and claims with distinctive numbers performed well:

- Hetauda-Dhalkebar-Inaruwa and Sanima Mai entity queries hit relevant pages at rank 1.
- The FY 2024/25 NEA primary-source query hit the correct source at rank 1 with nDCG@10 of 1.0.
- The deliberately misstated 72,544 MW “economically feasible” claim was corrected by the right WECS/potential pages at the top.

The retrieval weakness is therefore not general inability to retrieve the corpus; it is intent discrimination among project, policy, concept, and portfolio pages.

## Post-run judgment-gap flags

The frozen v1 judgments were not changed. Ranking inspection exposed plausible unjudged relevant pages that should be considered only in a future `real_v2` assessment:

- `real-v1-15`: individual pages such as `mugu-karnali-storage`, `dudhkoshi-storage`, `uttarganga-storage`, and `tamor-storage` contain project stage information and may deserve positive grades. Their presence in the top 10 means the v1 top-10 failure partly reflects a judgment-pool gap, not only retrieval failure.
- `real-v1-05`: `mustang-high-altitude-solar-zone` and `data-layer-solar-strategic-suitability` may be relevant to the geographic-resource need, while named solar plants remain weaker lexical matches.
- `real-v1-01`: `data-domestic-demand` and `seasonal-arbitrage-trap` may substantially answer the seasonal import/export explanation.

These are flagged, not retroactively labeled. Consequently, v1 nDCG values should be read with the scorer's explicit convention that unjudged documents receive zero gain. Top-10 lists contain many unjudged documents—typically six to ten per query—because this is a manually bounded judgment pool rather than exhaustive corpus labeling.

## Bottom-performing queries

| Query | First relevant rank | MRR | nDCG@10 | Interpretation |
|---|---:|---:|---:|---|
| real-v1-15 storage roadmap | 26 | 0.038462 | 0.000000 | Portfolio intent lost to project entities; also a flagged judgment-pool gap |
| real-v1-09 storage vs RoR roles | 9 | 0.111111 | 0.209339 | Comparative conceptual pages ranked behind less direct material |
| real-v1-11 hydropower PPA rules | 9 | 0.111111 | 0.224343 | Project entities dominate general rule intent |
| real-v1-26 environmental-flow rules | 9 | 0.111111 | 0.224343 | Project entities dominate policy intent |
| real-v1-05 solar geography | 4 | 0.250000 | 0.233402 | Plant/entity geography outranks resource-zone explanation |

## Conclusion

The static Explorer retrieval path has strong top-10 coverage and good performance for exact entities, conceptual explanations, and distinctive source-verification queries. Its main weakness is early-rank intent discrimination: “rules,” “roadmap,” “environmental flow,” “resource potential,” and “bottleneck” modifiers are often overwhelmed by high-scoring project entities. The result is suitable as an untuned v1 baseline. Any future ranking or alias work should be evaluated on a new run without modifying this frozen query set or its judgments.
