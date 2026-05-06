---
title: Dana–Kushma–New Butwal 220 kV Corridor
type: entity
category: transmission-corridor
created: 2026-04-20
updated: 2026-04-25
sources: [nepal-transmission-landscape-2025, nea-annual-report-fy2024-25, nea-transmission-annual-book-2077]
tags: [transmission, 220kv, kali-gandaki-basin, west-central, ipp]
images:
  - src: dana-kushma-butwal-corridor/nea2077-p131-img01.png
    caption: "each at Rautahat and Saptari."
    credit: "Nepal Electricity Authority, A Year in Review FY 2019/20 (B.S. 2077)"
    license: gov-permissive
    source_url: "../../../data/raw/corridor_tracing/nea/nea_transmission_annual_book_2077.pdf"
  - src: dana-kushma-butwal-corridor/nea2077-p131-img02.png
    caption: "On-site Awareness Training at Rautahat"
    credit: "Nepal Electricity Authority, A Year in Review FY 2019/20 (B.S. 2077)"
    license: gov-permissive
    source_url: "../../../data/raw/corridor_tracing/nea/nea_transmission_annual_book_2077.pdf"
  - src: dana-kushma-butwal-corridor/nea2077-p147-img01.png
    caption: "220 kV Kushma Substation"
    credit: "Nepal Electricity Authority, A Year in Review FY 2019/20 (B.S. 2077)"
    license: gov-permissive
    source_url: "../../../data/raw/corridor_tracing/nea/nea_transmission_annual_book_2077.pdf"
  - src: dana-kushma-butwal-corridor/nea2077-p147-img02.png
    caption: "be commissioned by December 2020."
    credit: "Nepal Electricity Authority, A Year in Review FY 2019/20 (B.S. 2077)"
    license: gov-permissive
    source_url: "../../../data/raw/corridor_tracing/nea/nea_transmission_annual_book_2077.pdf"
generator: manual
page_quality: analysis
---

# Dana–Kushma–New Butwal 220 kV Corridor

The west-central hydropower evacuation corridor — running from the
upper **Kali Gandaki** valley (Dana, Kushma, Parbat) down to **New Butwal**.
Built to pick up the cluster of IPPs in the Modi and Kaligandaki
tributaries and tie them into the growing western grid.

## Key Facts

| Parameter | Value |
|-----------|-------|
| Voltage | 220 kV |
| Status | Operational |
| Length basis | 127.57 route-km / 255.6 circuit-km |
| Owner | [[nea]] |
| Terminals | Dana (Myagdi) · Kushma (Parbat) · New Butwal (Rupandehi) |
| Commissioned | Dana-Kushma and Kushma-New Butwal sections now operational; New Butwal fully operational since October 2023 |
| Corridor ID | `dana_kushma_butwal_220` |

## Map Interpretation

The major transmission network now represents this corridor as two source-backed 220 kV double-circuit features: Dana-Kushma and Kushma-New Butwal. The geometry comes from RPGCL official vector linework, while the length/status basis comes from NEA transmission and annual reports.

Current validation result: 2 features, 0 inferred connectors, 0 remaining endpoint gaps, and 128.027 km traced length against a 127.57 route-km basis. Public decision: default-visible, operational, high confidence.

## Significance

- **Unlocks a trapped basin.** Before this corridor, the Modi / upper
  Kali Gandaki IPP cluster had to evacuate through congested 132 kV
  toward Pokhara. Dana–Kushma–New Butwal gave the basin its own exit.
- **Pre-positions for 400 kV.** Terminates at New Butwal, the same
  substation that will host the [[mca-central-400]] terminus and the
  [[gorakhpur-butwal-interconnection]].
- **Significance for [[kali-gandaki-a]]'s downstream cascade.** The
  corridor accommodates future cascade additions in the basin.

## Limitations & Open Questions

- **Terrain risk.** Myagdi-Parbat segment climbs steep, landslide-prone
  terrain; 2023 monsoon damage required emergency tower reinforcement.
- **Still 220 kV.** As the [[gandaki-basin]] pipeline grows, 220 kV may
  again become the bottleneck; the [[mca-central-400]] and
  [[gorakhpur-butwal-interconnection]] make New Butwal the reinforcement
  point to watch.

## See also

- [[kali-gandaki-a]] — the basin anchor
- [[mca-central-400]] — the 400 kV it links to
- [[gorakhpur-butwal-interconnection]] — the cross-border at New Butwal
- [[data-layer-transmission-connected-traced-network]] — the public layer where this corridor now appears
