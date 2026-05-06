---
title: Hetauda–Bharatpur–Bardaghat 220 kV Corridor
type: entity
category: transmission-corridor
created: 2026-04-20
updated: 2026-04-25
sources: [nepal-transmission-landscape-2025, nea-annual-report-fy2024-25, nea-transmission-annual-book-2077]
tags: [transmission, 220kv, east-west, central-nepal]
generator: manual
page_quality: analysis
---

# Hetauda–Bharatpur–Bardaghat 220 kV Corridor

The 220 kV east–west spine across central Nepal, running through the
**Hetauda → Bharatpur → Bardaghat** load corridor. This is the line
that carried Nepal's grid before the 400 kV era — and still carries
the majority of Terai distribution load.

## Key Facts

| Parameter | Value |
|-----------|-------|
| Voltage | 220 kV (double circuit) |
| Status | Operational |
| Length basis | 146.5 route-km / 293.0 circuit-km |
| Owner | [[nea]] |
| Terminals | Hetauda (Makwanpur) · Bharatpur (Chitwan) · Bardaghat (Nawalparasi) |
| Corridor ID | `hetauda_bharatpur_bardaghat_220` |

## Map Interpretation

The connected transmission layer now represents this corridor as two source-controlled features: Hetauda-New Bharatpur and New Bharatpur-Bardaghat. This replaced the older over-selected RPGCL extraction, which mixed adjacent 220 kV fragments into the HBB corridor.

Current validation result: 2 features, 0 inferred connectors, 0 remaining endpoint gaps, and 143.365 km traced length against a 146.5 route-km basis.

Public decision: **default-visible, caveated**.

## Significance

- **Load-centre spine.** Serves the Bharatpur–Hetauda–Butwal urban belt,
  Nepal's second-largest consumption cluster after the Kathmandu Valley.
- **Redundancy for 400 kV.** During HDDI outages this corridor provides
  a lower-voltage fallback for east–west flow, at reduced capacity.
- **Tie-in for western generation.** Connects Marsyangdi-basin and
  Kali Gandaki-basin output to the central grid before the
  [[mca-central-400]] fully commissions.

## Limitations & Open Questions

- **Legacy capacity.** 220 kV thermal limits constrain the amount of
  surplus generation the corridor can absorb; during monsoon peak,
  IPPs in the west are partly curtailed despite availability.
- **Substation bottlenecks.** Bharatpur's bus configuration has been
  flagged as a weak link in NEA's 2024 reliability review.
- **Geometry precision remains caveated.** The public route is now coherent
  and source-bounded, but the Bharatpur-Bardaghat portion is still a
  corridor-level SIA trace rather than a tower-by-tower alignment.

## See also

- [[mca-central-400]] — the 400 kV reinforcement
- [[dana-kushma-butwal-corridor]] — the 220 kV it links with in the west
- [[hetauda-dhalkebar-inaruwa-backbone]]
