---
title: Hetauda–Dhalkebar–Inaruwa 400 kV Backbone
type: entity
category: transmission-corridor
created: 2026-04-20
updated: 2026-04-25
sources: [nepal-transmission-landscape-2025, nea-annual-report-fy2024-25, nea-transmission-annual-book-2077]
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
---

# Hetauda–Dhalkebar–Inaruwa 400 kV Backbone

<figure class="wiki-inline-figure">
  <img src="../assets/images/hetauda-dhalkebar-inaruwa-backbone/nea2077-p069-img01.png" alt="220 kV Substation at Dhalkebar">
  <figcaption>220 kV Substation at Dhalkebar</figcaption>
</figure>

Nepal's first — and, until the MCA corridor finishes, only — 400 kV transmission line. The
eastern spine that carries the country's aggregated hydropower output from central Nepal to
the **[[dhalkebar-muzaffarpur]]** border crossing and onward to India.

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

## Limitations & Open Questions

- **Single-point of failure for exports.** With no parallel 400 kV inside
  Nepal until the MCA corridor commissions, any HDDI outage collapses
  export revenue within hours. This is the operational form of the
  [[claim-transmission-immediate-blocker]] argument.
- **Thermal margin tightens as generation grows.** NEA has flagged
  loading rates approaching design limits during the 2024 monsoon peak;
  [[mca-central-400]] cannot arrive soon enough.
- **N-1 reliability not fully certified.** Sub-station-level redundancy
  at Dhalkebar is the subject of ongoing reinforcement projects.
- **Map precision caveat.** The public trace is now source-bounded and length
  consistent, but it is still not a tower-level engineering alignment. A future
  pass should replace it only if NEA or a lender publishes alignment sheets or
  tower coordinates.

## See also

- [[mca-central-400]] — the parallel 400 kV spine
- [[dhalkebar-muzaffarpur]] — the border link HDDI feeds
- [[inaruwa-purnea-interconnection]] — future secondary export route off HDDI
- [[claim-transmission-immediate-blocker]]
- [[nepal-transmission-landscape-2025]]
