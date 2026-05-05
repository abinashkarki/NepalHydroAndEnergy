---
title: NEA Triple-Authority Conflict
type: concept
created: 2026-05-02
updated: 2026-05-02
sources: [nea-annual-report-fy2024-25, fenner-school-nepal-state-of-knowledge-renewables-psh]
tags: [NEA, governance, PPA, dispatch, curtailment, AD-penalties, IPP, regulation, accountability]
---

# NEA Triple-Authority Conflict

The **NEA Triple-Authority Conflict** describes how the Nepal Electricity Authority simultaneously holds three powers over private hydropower producers (IPPs) that, in a well-designed market, would be separated across independent institutions:

1. **Dispatcher** — through the National Load Dispatch Centre (NLDC), NEA decides which plants run and which are curtailed.
2. **Single Buyer** — under the standard PPA framework, NEA is the sole off-taker. IPPs cannot sell to third parties, enter direct corporate PPAs, or export independently.
3. **Penalty Administrator** — NEA calculates, levies, and deducts Availability Declaration (AD) penalties from IPP receivables.

The same entity controls the physical flow of electrons, the commercial flow of money, and the enforcement flow of penalties. No independent arbiter exists between these roles.

## The structural double-bind

When NEA exercises role (1) to curtail a project — citing grid stability, N-1 transmission limits, or low domestic demand — the project's revenue stops. When NEA then exercises role (3), it can apply AD penalties for the generation shortfall that **it itself ordered**. Because role (2) guarantees no alternative market, the IPP cannot recoup the loss elsewhere.

The standard PPA contains **no explicit exemption clause** protecting an IPP from AD penalties when the root cause of the generation shortfall was an NLDC/NEA curtailment instruction. Exhaustive reviews of legacy PPA templates have not found such a carve-out. This means NEA can legally order a project off-line and legally extract cash for it being off-line, in the same transaction.

## The incentive to favor NEA-owned generation

NEA generates approximately 34% of national power through its own plants and subsidiaries. When NLDC dispatches an NEA-subsidiary plant, NEA pays itself — no cash leaves the institution. When NLDC dispatches a private IPP, NEA must release budget funds. The structure gives NEA a built-in incentive to prioritize its own output, particularly during periods of surplus when curtailment decisions must be made.

This structural favoritism has been independently verified in academic audit. The Fenner School of Environment and Society (Australian National University), *Nepal State of Knowledge Report — Renewables and PSH*, states:

> "The major complaint of the rising IPPs is that the playing field is not level, that NEA as generator, transmitter and distributor gives preferential terms to its own projects compared to IPPs; and indeed, this is seen in the case of the Chilime hydropower company that is owned by the NEA and its staff."

Citation: Fenner School of Environment and Society, ANU, *Nepal State of Knowledge Report — Renewables and PSH*, p. 20. URL: https://fennerschool.anu.edu.au/files/Nepal%20State%20of%20Knowledge%20Report%20-%20Renewables%20%26%20PSH.pdf.

No published merit order or dispatch protocol exists. NLDC's curtailment decisions affecting billions of rupees in annual revenue are made without public criteria. Neither the Auditor General nor any parliamentary committee has formally investigated dispatch discrimination.

## Primary case study: Barahi Hydropower

The Barahi Hydropower case provides the wiki's primary audited documentation of this double-bind in operation. NEA deducted AD penalties from a sub-10 MW project despite an explicit ERC statutory exemption (ERC Bylaws 2076, Clause 8(2)), and the project was forced to classify the deductions as "receivable from NEA" — a forced loan to the off-taker. See [[ad-penalties]] for full case detail and [[barahi-hydropower]] for the entity page.

## The AD penalty formula

The standard penalty formula documented in investment and tender materials is:

**Penalty = (0.8 × Contracted Energy − Electricity Output) × Electricity Tariff**

If a project's generation falls beneath 80% of its contracted energy (or declared availability, depending on the specific PPA tier), the developer pays a penalty effectively equal to the revenue of the undelivered power. These penalties are deducted directly from trade receivables owed by NEA — not remitted to an independent fund.

Industry sources assert that AD penalties can consume **up to 16% of project revenue**. This figure is not a statutory ceiling — it is an IPPAN-circulated aggregate derived from the PPA penalty formula: Penalty = (0.80 × contracted − actual) × tariff. Exhaustive search of IPPAN, ERC, ICRA/CARE, and media sources confirms no legal cap or named project case study verifying a 16% ceiling exists. The figure represents the formula's mathematical outcome during severe dry-season shortfalls, not a codified statutory limit. The penalty impact is variable and project-specific.

See [[ad-penalties]].

## The metrological impossibility

The AD system requires generators to declare their available generation 30 days in advance. For a run-of-river project with no storage reservoir, predicting daily output in a Himalayan monsoon watershed 30 days ahead is not an engineering failure — it is an inherently unsolvable forecasting problem.

The ERC formally acknowledged this for small projects, amending by-laws to allow plants under 10 MW to declare availability one week in advance and exempting them from financial damages. However, the Barahi case demonstrates that even explicit statutory exemption does not prevent NEA from deducting penalties when the institutional structure gives it unilateral power over cash disbursement.

## Reform models

A healthy market would separate the three functions:

- **Independent system operator (ISO)** — dispatch decisions separated from NEA's commercial interests.
- **Multiple buyers or open access** — IPPs able to sell to alternative off-takers (industrial consumers, export markets, trading companies).
- **Neutral penalty authority** — AD enforcement managed by the ERC or an independent entity, not the off-taker.

The 2003 World Bank Nepal power sector review recommended "eliminating conflicts of interest" in NEA's structure. The draft 2025 Open Access policy envisions moving beyond the single-buyer model. No legislation implementing these reforms has been enacted.

## Analytical links

The Triple-Authority Conflict is the institutional mechanism underlying:

- [[stranded-generation]] — curtailment without compensation
- [[seasonal-arbitrage-trap]] — pricing structure that extracts value from IPPs
- [[ad-penalties]] — the penalty mechanics enforced through this conflict
- [[ppa-pricing]] — rate-setting by the same entity that enforces performance
- [[barahi-hydropower]] — primary audited case study of penalty enforcement
- [[sahas-urja]] — why the standard IPP rate succeeds only at exceptional scale, not as a replicable model
- [[chameliya-hydropower]] — state capital inefficiency absorbed off-balance sheet while private developers face rigid caps
- [[hydro-insurance]] — the insurance market failure that compounds the financial squeeze when NEA applies penalties during claim settlement gaps
