---
title: MCA Central 400 kV Corridor (Lapsiphedi–Ratmate–Hetauda–Damauli–Butwal)
type: entity
category: transmission-corridor
created: 2026-04-20
updated: 2026-04-25
sources: [nepal-transmission-landscape-2025, nea-annual-report-fy2024-25, mca_annex_d1_alignment_maps]
tags: [transmission, 400kv, mca, central-corridor, under-construction]
---

# MCA Central 400 kV Corridor

The second 400 kV spine Nepal is building — the Millennium Challenge
Account (MCA-Nepal) compact's headline infrastructure, running from
**Lapsiphedi** (Kathmandu Valley ring) through **Ratmate, Hetauda,
Damauli** and terminating at **New Butwal**, where it feeds the
**[[gorakhpur-butwal-interconnection]]**. When complete, this corridor
ends the single-point-of-failure problem on the eastern backbone.

## Key Facts

| Parameter | Value |
|-----------|-------|
| Voltage | 400 kV |
| Status | Under construction (partial energisation 2025) |
| Route-length basis | 308.65 route-km |
| Circuit-length basis | 617.3 circuit-km |
| Owner | [[nea]] (construction by MCA-Nepal contractors) |
| Terminal substations | Lapsiphedi · Ratmate · Hetauda · Damauli · New Butwal |
| Financing | US MCC grant (~US$500M corridor share) + Government of Nepal |
| Target full commissioning | 2026–2027 |
| Corridor ID | `mca_central_400` |

## Map Interpretation

The connected transmission layer now uses a source-aware MCA atlas trace rather than the older RPGCL overview fragments. It is modeled as five project segments: Lapsiphedi-Ratmate, Ratmate-New Hetauda, Ratmate-New Damauli, New Damauli-New Butwal, and New Butwal-India border.

Public decision: **default-visible, high confidence**.

Validation shows 5 atlas-derived features, no inferred connectors, no endpoint gaps, and a -1.32% delta against the 308.65 route-km compact basis.

## Significance

- **Second 400 kV spine.** Parallels [[hetauda-dhalkebar-inaruwa-backbone]]
  via an entirely different geographic axis (Kathmandu → Western Terai),
  providing real N-1 redundancy for the first time.
- **Gateway to the second cross-border link.** Terminates at New Butwal,
  the Nepal end of [[gorakhpur-butwal-interconnection]].
- **Evacuates the western IPP cluster.** Picks up output from the
  Marsyangdi and Kali Gandaki basins that has historically been trapped
  behind legacy 132 kV — partially solving [[claim-transmission-immediate-blocker]]
  for the west.
- **Symbolic role.** First large US-funded infrastructure grant in Nepal;
  its progress is read as a proxy for Nepal's willingness to diversify
  foreign partners beyond India and China.

## Limitations & Open Questions

- **Right-of-way disputes.** Sections through Nuwakot and Kavre saw
  protracted community opposition over tower siting and compensation.
- **Partial commissioning ≠ full rating.** Early 2025 energisation
  covers the Ratmate–Hetauda link only; the full end-to-end 400 kV
  transfer capability awaits terminal substation completion at
  Damauli and New Butwal.
- **Dependent on cross-border terminal.** Full value is unlocked only
  when [[gorakhpur-butwal-interconnection]] also commissions.
- **Atlas trace, not tower survey.** The public geometry is route-grade
  for map and topology use, with sheet-level provenance, but it should
  not be read as a cadastral tower alignment.

## See also

- [[hetauda-dhalkebar-inaruwa-backbone]] — the existing backbone it parallels
- [[gorakhpur-butwal-interconnection]] — the border link it feeds
- [[dana-kushma-butwal-corridor]] — the 220 kV it relieves
- [[claim-transmission-immediate-blocker]]
