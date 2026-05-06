---
title: AD Penalties
type: concept
created: 2026-05-02
updated: 2026-05-02
sources: [erc-bylaws-2076, barahi-hydropower-audited-financials, ad-penalty-clause-research]
tags: [AD-penalties, PPA, NEA, IPP, regulation, ERC]
page_quality: analysis
---

# AD Penalties

**Availability Declaration (AD) penalties** are financial deductions levied by NEA against hydropower producers when actual generation falls below the availability the producer declared in advance. The AD penalty mechanism is the primary financial instrument through which the [[nea-triple-authority]] conflict operates.

## The Penalty Mechanism

The Availability Declaration system requires hydropower projects to declare their expected generation output in advance. When actual generation falls below the declared threshold, the project incurs a financial penalty deducted directly from its trade receivables owed by NEA.

**Verified penalty formula:**

**Penalty = (0.8 × Contracted Energy − Actual Output) × Tariff**

The 0.8 threshold means a project must achieve at least 80% of its contracted energy output before penalties cease. Any shortfall below this threshold is penalized at the full per-unit tariff rate on the gap.

**Penalty destination:** Penalties are deducted directly from the project's NEA trade receivables. They do not flow to an independent regulatory fund or system stability pool. NEA retains the deducted amount. [REQUIRES EXACT CITATION: statutory confirmation of destination mechanism — from PPA clause or ERC regulation]

**Revenue impact:** The Independent Power Producers' Association, Nepal (IPPAN) and
industry estimates suggest AD penalties can consume up to **16% of project revenue**
in severe cases. This figure is **not a statutory ceiling** — exhaustive search of IPPAN
publications, ERC directives, ICRA/CARE rating rationales, and energy journalism
archives confirms no legal cap or named project case study exists. The 16% figure is
best understood as an aggregate empirical observation derived from the PPA penalty
formula: Penalty = (0.80 × contracted energy − actual energy) × tariff. During severe
dry seasons when a project generates well below 50% of contracted energy, the
mathematical outcome of the formula approaches 16% of contracted energy value.
The figure circulates as an IPPAN advocacy benchmark rather than a legally verified
ceiling.

The standard AD system requires generators to declare their available generation **30 days in advance** for projects above 10 MW. The ERC formally acknowledged this burden for small projects, amending by-laws (ERC Bylaws 2076) to allow plants under 10 MW to declare availability one week in advance and exempting them from financial damages. See [[nea-triple-authority]] for the institutional framework.

## The Barahi Hydropower Case

**Barahi Hydropower Public Limited** is the best-documented case of the AD penalty mechanism overriding its own exemption clause.

Barahi is a sub-10 MW run-of-river project. The Electricity Regulatory Commission (ERC) Bylaws 2076, Clause 8(2) and Schedule 5, explicitly exempt projects below 10 MW from AD penalties.

Despite this exemption, NEA deducted penalty amounts for short supply from Barahi's invoices. Out of Rs 14.9 million in trade receivables, Barahi's management was forced to classify the deducted penalties as **"receivable from NEA"** in audited financial statements — publicly stating that NEA's actions contradict the prevailing ERC By-laws.

Because NEA controls cash disbursement, the IPP carries the deducted penalty on its balance sheet while the ERC exemption exists on paper with no enforcement mechanism. The independent arbiter is absent.

- Project: Barahi Hydropower Public Limited
- Capacity: sub-10 MW (RoR)
- Regulatory protection: ERC Bylaws 2076, Clause 8(2), Schedule 5
- Penalty deducted: part of Rs 14.9M in receivables
- Accounting treatment: "receivable from NEA" in audited financial statements
- Source: Barahi Hydropower audited financial statements [UNVERIFIED: exact fiscal year to be confirmed]

The Barahi case is significant precisely because it documents the penalty mechanism overriding its own exemption clause. The project recorded the deduction as "receivable from NEA" — a forced loan to the off-taker with no resolution timeline on record.

See [[barahi-hydropower]].

## The Structural Impossibility

For run-of-river projects without storage, predicting output 30 days in advance in a Himalayan monsoon basin is not an engineering failure — it is an inherently unsolvable forecasting problem. RoR projects, lacking storage reservoirs, are at the absolute mercy of daily river hydrology. Holding RoR developers financially liable for standard deviation in monsoon hydrology via punitive AD penalties is fundamentally irrational from an engineering and grid-design perspective.

The ERC acknowledged this by exempting projects under 10 MW from 30-day declarations and financial damages. The structural impossibility for larger projects remains unaddressed in regulatory or judicial rulings. [Under research — no primary regulatory or judicial source found yet.]

## The Curtailment-Penalty Double-Bind — Confirmed

The most consequential structural question about Nepal's AD penalty regime — whether
any PPA version contains an exemption for shortfalls caused by NEA/NLDC curtailment
orders — has now been confirmed by direct PPA text analysis.

**The answer is no.**

Article 10.2 of the standard PPA specifies the penalty formula:

> Compensation = [0.80 × min(Monthly Contract Energy, Availability Declaration) −
> (Actual Energy Delivered + Scheduled Outage Energy + Forced Outage Energy +
> Force Majeure Energy)] × Purchase Rate

The formula counts only **declared outages** and **force majeure** as excusable
causes. Curtailment by the off-taker is not listed. No PPA clause carves out
NLDC dispatch orders from the penalty trigger.

This is the double-bind in contractual form: the off-taker controls dispatch *and*
enforces availability penalties, with no mechanism for the generator to claim
relief when the two obligations conflict.

International standard (IFC model PPAs) treats off-taker curtailment as a
compensable "deemed generation" event — the IPP is paid as if it had generated,
because the shortfall was caused by the buyer's decision, not the seller's failure.
Nepal's PPA contains no such provision. Analysts have explicitly recommended
adding deemed-generation protection in renegotiations, confirming its current absence.

Source: Parajuli, S. (2023), "What does a RoR PPA contain?" — direct PPA text analysis.

## The 10% Reserve Margin — Zero Compensation

Article 10.1(Ka) of the standard PPA explicitly permits NEA/NLDC to withhold up to
**10% of peak-period Contract Energy** as a system reserve — with **zero compensation**
to the IPP for that withheld energy. NEA can simultaneously:

1. Order an IPP to reduce output (curtailment) or withhold up to 10% as reserve
2. Apply a penalty for any shortfall below 80% of contracted energy
3. Face no compensation obligation for the generation it prevented

The 10% reserve withholding, combined with the Article 10.2 penalty formula that
excludes curtailment from excusable causes, means NEA can legally reduce a
project's actual generation below the 80% penalty threshold through its own
dispatch decisions — and then fine the project for the resulting shortfall.

This makes the [[nea-triple-authority]] conflict not just an institutional design
problem but a **contractually encoded feature**: the same entity controls both
dispatch and penalty enforcement, and the PPA's penalty formula treats off-taker
curtailment identically to generator failure.

## Challenge Cases and Outcomes

Beyond Barahi, no documented ERC arbitration rulings or court judgments on AD penalty disputes have been found in research passes to date. Any IPPAN legal challenges, ERC proceedings, or judicial outcomes concerning AD penalties should be documented here when located. [Under research.]

## Analytical links

- [[nea-triple-authority]] — the institutional framework this mechanism operates within
- [[barahi-hydropower]] — primary audited case study
- [[q-design-discharge]] — how design discharge sets the contracted energy threshold that triggers penalties
- [[hydro-insurance]] — the insurance market failure that strips working capital during penalty periods
