---
title: Stranded Generation
type: concept
created: 2026-04-14
updated: 2026-07-10
sources: [nea-annual-report-fy2024-25, nea-operational-reporting-portals-2026, likhu-cascade-research-compilation, nea-standard-ppa-clauses]
tags: [curtailment, transmission, grid, monsoon, IPP, nepal]
page_quality: analysis
---

# Stranded Generation

## Summary

Stranded generation is the condition where a power plant could produce,
but the grid cannot absorb or move its electricity—so water is spilled,
output is reduced or a dispatch instruction stops generation. In Nepal,
the mechanism is plausible in a run-of-river system with constrained
transmission and export paths, but the public source corpus does not
provide a national, plant-level curtailment series to measure its scale.

## Simple Explanation

Nepal can add hydropower faster than the lines, substations, domestic
demand and cross-border access needed to use it. During high-flow
periods, that can leave available generation without an outlet. A low
annual generation figure alone is not proof of curtailment: it can also
reflect hydrology, maintenance, forced outage, transmission failure or
plant availability.

## What the Current Evidence Establishes

During wet-season peaks, run-of-river output, domestic demand, export
access and internal transmission capacity can diverge (see
[[seasonal-mismatch]]). The NEA annual report is an essential system
snapshot, but it does not publish the plant-by-plant available energy,
dispatch instruction, rejected MWh or reason code needed to quantify
national curtailment.

As checked on 10 July 2026, NEA's Generation Directorate public
operational-report page was marked `Coming soon`, while its Transmission
Directorate published daily aggregate system reports. Neither public
surface supplies the plant-level availability and dispatch-event fields
needed for a curtailment series. See
[[nea-operational-reporting-portals-2026]].

The Likhu cascade is the best-documented corridor case in the current
corpus. A research compilation attributes Likhu-2's FY 2023/24
underperformance to the New Khimti transformer constraint and records
improved performance after an upgrade. This is useful evidence of a
specific bottleneck mechanism, not a national curtailment rate or a
representative sample. See [[buildability]] for the delivery-risk
context.

The public evidence supports a transmission-and-market risk, not a
precise current daily spill figure. Installed capacity, exports and
annual sales cannot be subtracted from one another to obtain
curtailment, because they use different time bases and omit hydrology,
availability, imports, storage, losses and dispatch constraints.

## Contract Exposure Is Distinct From Observed Losses

Secondary analysis of standard NEA PPA clauses identifies a possible
contractual exposure where dispatch curtailment is not treated as a
compensable deemed-generation event. It does not provide a signed-PPA
corpus, a dispatch-order log or adjudicated outcomes. The effect on
individual IPPs therefore remains a question for contract and
plant-level evidence, rather than a fact established by the current
page.

## Minimum Disclosure Needed to Measure the Problem

An auditable monthly public dataset should publish, for each generator
or an appropriately anonymised cohort:

| Field | Why it is required |
|---|---|
| Available generation (MWh) and actual accepted generation (MWh) | Separates physical availability from accepted output |
| Curtailment MWh and timestamp | Makes the amount and system period measurable |
| Reason code | Distinguishes transmission, system-security, market, maintenance and hydrology causes |
| Affected transmission node/corridor | Connects a loss to an investment or operating constraint |
| Dispatch instruction and restoration time | Establishes whether curtailment was ordered and for how long |
| Contractual treatment and compensation status | Separates physical curtailment from the resulting financial loss |

Until that data exists, project-level reports should be labelled as
individual research leads, not combined into a national total. This is
the highest-priority operational-data request in [[unresolved-questions]].

## Common Misunderstandings

- **"Stranded generation means plants are broken."** It may instead be
  a grid, market or dispatch constraint; the reason must be observed.
- **"More generation automatically solves supply needs."** Generation
  without transmission, demand and usable market access can increase
  the risk of unavailable output in particular hours or seasons.
- **"Annual energy reveals curtailment."** It cannot do so without an
  availability baseline and dispatch-cause data.

## Analytical Links

Stranded energy is the physical mirror of
[[seasonal-arbitrage-trap]]: surplus energy without priced scarcity,
dispatchable demand or firm export paths does not necessarily become
useful electricity. The institutional counterpart is whether [[nea]] and
regulators can align incentives so that installed MW stops diverging
from delivered MWh.

## Related

- [[seasonal-mismatch]]
- [[intervention-transmission-completion]]
- [[data-domestic-demand]]
- [[likhu-2]]
- [[unresolved-questions]]
