---
title: Hetauda–Dhalkebar–Inaruwa 400 kV Backbone
type: entity
category: transmission-corridor
created: 2026-04-20
updated: 2026-11-04
reviewed: 2026-11-04
review_due: 2026-12-04
as_of: 2026-10-07
sources: [world-bank-hddi-rap, nepal-transmission-landscape-2025, nea-annual-report-fy2025-26, nea-annual-report-fy2024-25, nea-transmission-annual-book-2077, nea-hddi-construction-notices-july-2026]
tags: [transmission, 400kv, backbone, hddi, internal-grid]
images:
  - src: hetauda-dhalkebar-inaruwa-backbone/nea2077-p066-img02.png
    caption: "400 kV GIS Hall at Dhalkebar"
    credit: "Nepal Electricity Authority, A Year in Review FY 2019/20 (B.S. 2077)"
    license: gov-permissive
    source_url: "../../../data/raw/corridor_tracing/nea/nea_transmission_annual_book_2077.pdf"
  - src: hetauda-dhalkebar-inaruwa-backbone/nea2077-p061-img01.png
    caption: "Ongoing Stringing work at Dhankuta Section"
    credit: "Nepal Electricity Authority, A Year in Review FY 2019/20 (B.S. 2077)"
    license: gov-permissive
    source_url: "../../../data/raw/corridor_tracing/nea/nea_transmission_annual_book_2077.pdf"
generator: manual
excerpt: Nepal's first domestic 400 kV backbone is operational east of Dhalkebar; on Hetauda–Dhalkebar the construction dispute is resolved and charging was announced as imminent in October 2026, but energisation is not yet verified.
page_quality: flagship
maturity: verified-core
caveat: No NEA energisation or commissioning notice for Hetauda–Dhalkebar was located as of 4 November 2026; the latest tower count is an NEA official quoted in the press on 7 October 2026.
---

# Hetauda–Dhalkebar–Inaruwa 400 kV Backbone

<figure class="wiki-inline-figure">
  <img src="../assets/images/hetauda-dhalkebar-inaruwa-backbone/nea2077-p069-img01.png" alt="220 kV Substation at Dhalkebar">
  <figcaption>220 kV Substation at Dhalkebar</figcaption>
</figure>

## Summary

Nepal's first major domestic 400 kV backbone, represented as two
segments with different delivery states. Dhalkebar–Inaruwa is
operational; Hetauda–Dhalkebar remains under construction. Describing
the entire corridor simply as "operational" would overstate the current
east–west transfer path to the **[[dhalkebar-muzaffarpur]]** gateway.

## Key Facts

| Parameter | Value |
|-----------|-------|
| Voltage | 400 kV |
| Status | Partially operational: Dhalkebar-Inaruwa operational; Hetauda-Dhalkebar still under construction |
| Total spine length | ~288 km route basis |
| Owner | [[nea]] (Nepal Electricity Authority) |
| Key substations | Hetauda · Dhalkebar · Inaruwa |
| Segment status | Hetauda-Dhalkebar: under construction · Dhalkebar-Inaruwa: operational since June 2024 |
| Financing | ADB, KfW, World Bank (segment-wise) |
| Pane of operation | Central / Eastern Terai belt |
| Corridor ID | `hddi_400` |

## Current Status

**Evidence checked through 4 November 2026:** partially operational. NEA's FY 2025/26 annual report says the decade-long construction dispute "has finally been resolved" and that work resumed, with completion expected "in few months" ([[nea-annual-report-fy2025-26]], PDF pp.13–14). On 7 October 2026, NEA's executive director said 14 of the 16 towers on the outstanding stretch were built, with two multi-circuit towers in their final stage, and that the line would be charged in about 15 days; transfer between Hetauda and Dhalkebar was limited to about 300 MW, against about 2,000 MW once complete ([Spotlight Nepal, 7 Oct 2026](https://www.spotlightnepal.com/2026/10/07/hetaudadhalkebar-400-kv-transmission-line-to-be-charged-within-two-weeks/)). No energisation notice had been located by 4 November 2026. The
corridor's status is stored by segment in `data/corridor_specs.csv`,
while the map uses document-bounded corridor geometry rather than a
tower-by-tower engineering alignment.

| Segment | Status | Status date/basis | Principal dependency |
|---|---|---|---|
| Hetauda–Dhalkebar | Under construction; charging announced as imminent but not verified | NEA FY 2025/26 report; NEA executive director, 7 Oct 2026 | Two remaining multi-circuit towers and energisation |
| Dhalkebar–Inaruwa | Operating | June 2024 / NEA FY 2024/25 reporting | Completion of the western segment for a continuous backbone |

## Recent Updates

| Date | Update |
|---|---|
| FY 2024/25 | NEA reporting distinguishes the operating eastern section from the unfinished Hetauda–Dhalkebar section |
| 3–5 Jul 2026 | NEA operational notices document local shutdowns for conductor-stringing work on the Hetauda–Dhalkebar section |
| 19 Jul 2026 | Public NEA surfaces rechecked; construction activity is established, but completion and energisation remain unverified |
| 18 Aug 2026 | NEA FY 2025/26 annual report: dispute resolved, works resumed, completion expected within months |
| 7 Oct 2026 | NEA executive director: 14 of 16 towers on the outstanding stretch built; charging expected in about 15 days ([Spotlight Nepal, 7 Oct 2026](https://www.spotlightnepal.com/2026/10/07/hetaudadhalkebar-400-kv-transmission-line-to-be-charged-within-two-weeks/)) |
| 4 Nov 2026 | No energisation or commissioning notice located; status remains under construction |

## Active Blockers

| Blocker | Prevents | Evidence basis |
|---|---|---|
| Remaining Hetauda–Dhalkebar works and right-of-way resolution | Continuous 400 kV operation across the full backbone | [[world-bank-hddi-rap]] and [[nea-hddi-construction-notices-july-2026]] |

## Map Interpretation

In the connected transmission layer, HDDI is represented as two World Bank RAP-controlled corridor features: Hetauda-Dhalkebar and Dhalkebar-Inaruwa. The RPGCL overview fragments remain available in the raw audit/source layer, but they no longer drive the public connected network because they made the corridor read too straight and materially short.

Public decision: **default-visible, caveated**.

The current validation result has 0 inferred connectors, 0 remaining gaps, and a -1.22% length delta against the current 288 route-km basis. The geometry is still a document-grounded corridor trace, not a tower-by-tower alignment.

## Significance

- **First 400 kV domestic backbone.** The operational Dhalkebar-Inaruwa section
  and the partly complete Hetauda-Dhalkebar section are the core east-west
  transfer path behind Nepal's export-readiness story.
- **Aggregation point for IPP clusters.** Evacuates the [[khimti-dhalkebar-corridor]],
  Sunkoshi, Tamakoshi and (once online) [[arun-3]] blocks toward India.
- **Decouples load centres.** Before HDDI, the Kathmandu Valley and the
  eastern Terai were weakly linked; HDDI re-wrote the grid topology.
- **Mixed construction and operating state.** Dhalkebar-Inaruwa is operational,
  while Hetauda-Dhalkebar remains in the build queue. Treating the whole
  backbone as operational would overstate current transfer readiness.

## Limitations & Controversies

- **Concentrated transfer dependency.** Until parallel 400 kV paths are
  commissioned, outages or unfinished sections constrain domestic
  transfer and export routing. See
  [[claim-transmission-immediate-blocker]].
- **Thermal margin tightens as generation grows.** NEA has flagged
  loading rates approaching design limits during the 2024 monsoon peak;
  [[mca-central-400]] cannot arrive soon enough.
- **N-1 reliability not fully certified.** Sub-station-level redundancy
  at Dhalkebar is the subject of ongoing reinforcement projects.
- **Map precision caveat.** The public trace is now source-bounded and length
  consistent, but it is still not a tower-level engineering alignment. A future
  pass should replace it only if NEA or a lender publishes alignment sheets or
  tower coordinates.
- **Current milestone caveat.** NEA's FY 2024/25 report provides a July 2025
  construction snapshot. July 2026 outage notices confirm later stringing work,
  but neither source establishes a current remaining-tower count or commissioning.

## See also

- [[mca-central-400]] — the parallel 400 kV spine
- [[dhalkebar-muzaffarpur]] — the border link HDDI feeds
- [[inaruwa-purnea-interconnection]] — future secondary export route off HDDI
- [[claim-transmission-immediate-blocker]]
- [[nepal-transmission-landscape-2025]]

## Sources

- [[world-bank-hddi-rap|World Bank NIETTP Hetauda–Dhalkebar–Inaruwa Resettlement Action Plan]]
- [[nepal-transmission-landscape-2025|Nepal Transmission System — 400 kV Landscape & Cross-Border Plan (2025)]]
- [[nea-annual-report-fy2024-25|NEA Annual Report FY 2024/25]]
- [[nea-transmission-annual-book-2077|NEA Transmission Annual Book 2077]]
- [[nea-hddi-construction-notices-july-2026|NEA Hetauda–Dhalkebar Construction Notices, July 2026]]
