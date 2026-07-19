# Nepal Energy retrieval holdout v1: simulated personas and query design

Created: 2026-06-20T07:34:52Z

These personas are simulated research instruments created internally for retrieval evaluation. They are not people who were recruited, interviewed, surveyed, or observed, and this work is not external user research.

The query wording below was fixed as the drafting baseline before inspecting or running the candidate search system. Relevance judgments are also internal assessor judgments, not labels supplied by external users.

## Simulated personas

### P1 — Nepali citizen and general reader

- Knowledge level: familiar with everyday electricity supply, bills, LPG use, and public discussion of exports, but not power-system terminology.
- Information needs: plain-language explanations of seasonal shortages, household energy, electric cooking, and where renewable resources are located.
- Typical wording: conversational “why,” “is it true,” and “where” questions without official vocabulary.

### P2 — Energy-policy student

- Knowledge level: undergraduate or early graduate familiarity with energy policy, but still learning Nepal-specific institutions and technical distinctions.
- Information needs: definitions, defensible comparisons, system-level evidence, and reusable datasets or sources for coursework.
- Typical wording: conceptual distinctions, comparative questions, and requests for evidence.

### P3 — Hydropower and renewable-energy investor

- Knowledge level: financially literate and familiar with projects, PPAs, generation, and listed-company reporting, but not necessarily an engineer.
- Information needs: revenue and generation evidence, tariff and contract context, financing risk, technology cost comparisons, and project pipeline status.
- Typical wording: commercially focused questions naming companies, prices, risks, or investability.

### P4 — Transmission planning engineer

- Knowledge level: technically advanced; understands voltage levels, substations, evacuation corridors, interconnections, and network data quality.
- Information needs: asset-specific status and capacity, cross-border topology, provenance and trace gaps, bottlenecks, and generation-evacuation routes.
- Typical wording: precise infrastructure names, capacities, corridor relationships, and source-quality constraints.

### P5 — Journalist and source verifier

- Knowledge level: broad sector familiarity and strong verification instincts, but variable specialist depth.
- Information needs: primary or strongest available sources, dates, exact figures, causal evidence, and checks on prominent public claims.
- Typical wording: “what source,” “verify,” “evidence,” and claim-testing questions.

### P6 — Local and community stakeholder

- Knowledge level: place- and livelihood-specific knowledge; limited familiarity with sector acronyms or finance models.
- Information needs: environmental flows, benefit promises, rural access support, land and compensation issues, and local impacts of large projects.
- Typical wording: practical questions about rights, effects, promised benefits, and available programs.

## Exactly 30 drafted queries

| ID | Persona | Query type | Natural query |
|---|---|---|---|
| real-v1-01 | P1 | conceptual | Why does Nepal export electricity in the monsoon but still import power in winter? |
| real-v1-02 | P1 | conceptual | Is most of Nepal's hydropower run-of-river, and what does that mean in the dry months? |
| real-v1-03 | P1 | attribute_lookup | How much of household energy in Nepal still comes from firewood compared with electricity? |
| real-v1-04 | P1 | conceptual | Would switching to electric cooking really reduce Nepal's LPG imports and indoor air pollution? |
| real-v1-05 | P1 | attribute_lookup | Which parts of Nepal have the best solar power potential? |
| real-v1-06 | P2 | conceptual | What is the difference between Nepal's theoretical, technical, and economically feasible hydropower potential? |
| real-v1-07 | P2 | source_seeking | What evidence supports the claim that transmission is Nepal's immediate power-sector bottleneck? |
| real-v1-08 | P2 | conceptual | What does firm power mean, and why is installed megawatts not the same as dependable supply? |
| real-v1-09 | P2 | comparative | How do storage hydropower and run-of-river projects play different roles in Nepal's seasonal electricity system? |
| real-v1-10 | P2 | source_seeking | Is there a dataset showing Nepal's electricity imports and exports over recent years? |
| real-v1-11 | P3 | attribute_lookup | What PPA prices and tariff rules apply to new hydropower projects in Nepal? |
| real-v1-12 | P3 | exact_entity | How has Sanima Mai's generation compared with its contracted energy, and what PPA rates does it receive? |
| real-v1-13 | P3 | conceptual | Why are some Nepali hydropower IPO companies struggling to service debt even after their plants start operating? |
| real-v1-14 | P3 | comparative | Is utility-scale solar now cheaper than small hydropower in Nepal on an LCOE basis? |
| real-v1-15 | P3 | multi_constraint | Which major storage hydropower projects are on Nepal's roadmap, and what stage is each one at? |
| real-v1-16 | P4 | exact_entity | What is the status and capacity of the Hetauda-Dhalkebar-Inaruwa 400 kV backbone? |
| real-v1-17 | P4 | multi_constraint | Which Nepal-India cross-border transmission lines are operating now, and which high-voltage links are planned? |
| real-v1-18 | P4 | source_seeking | Where does the Nepal transmission map have traced gaps or approximate alignments rather than authoritative line geometry? |
| real-v1-19 | P4 | attribute_lookup | Which substations are identified as capacity bottlenecks in Nepal's grid? |
| real-v1-20 | P4 | multi_constraint | Which transmission corridor is supposed to evacuate power from Arun-3, and how does it connect toward India? |
| real-v1-21 | P5 | source_seeking | What is the best primary source for Nepal's installed capacity, generation, imports, and exports in FY 2024/25? |
| real-v1-22 | P5 | source_seeking | What evidence explains the delays and cost overruns at the Chameliya hydropower project? |
| real-v1-23 | P5 | source_seeking | What source supports the estimate that Nepal has about 72,544 MW of economically feasible hydropower potential? |
| real-v1-24 | P5 | source_seeking | Can I verify the claim that India approves Nepal power exports project by project rather than allowing open access? |
| real-v1-25 | P5 | multi_constraint | What evidence links glacier change and sediment risks to the future reliability of Nepal's hydropower? |
| real-v1-26 | P6 | attribute_lookup | What environmental-flow rules are hydropower projects in Nepal supposed to follow? |
| real-v1-27 | P6 | source_seeking | Why has the Upper Karnali project still not started, and what is holding up the project agreement? |
| real-v1-28 | P6 | source_seeking | What support is available for rural households that need off-grid solar or mini-grid electricity? |
| real-v1-29 | P6 | conceptual | How are land acquisition, compensation, and local disputes handled for transmission-line projects in Nepal? |
| real-v1-30 | P6 | multi_constraint | What local impacts and resettlement issues are expected around the Dudhkoshi storage project? |

## Coverage intent

The set deliberately mixes plain-language, entity-specific, conceptual, comparative, source-verification, and multi-constraint needs. Five queries belong to each simulated persona. No query was copied from the existing development benchmark.

Two questions were tightened during the independent pre-freeze review, before any candidate-system inspection or execution. The reasons and original wording are preserved in `independent-review.md`.
