---
title: Solu Corridor Tingla-Mirchaiya 132 kV
type: entity
category: transmission-corridor
created: 2026-04-25
updated: 2026-04-25
sources: [nepal-transmission-landscape-2025, nea-transmission-annual-book-2077]
tags: [transmission, 132kv, solu, operational, traced-corridor]
---

# Solu Corridor Tingla-Mirchaiya 132 kV

The Solu Corridor Tingla-Mirchaiya 132 kV line evacuates generation from the Solu/Okhaldhunga area south toward Mirchaiya. It is operational, but the public route geometry is still lower-confidence than the main 220 kV and 400 kV corridors because the current trace is reconstructed from NEA narrative and anchor points rather than an alignment atlas.

## Key Facts

| Parameter | Value |
|-----------|-------|
| Voltage | 132 kV |
| Status | Operational |
| Corridor ID | `solu_tingla_mirchaiya_132` |
| Public map feature | `solu_tingla_mirchaiya_132_main` |
| Source basis | NEA Transmission Annual Book 2077 pages 47-52 |
| Official route length | 90.0 km route basis |
| Traced network length | 78.844 km |
| Validation delta | -12.40% |

## Map Interpretation

The map trace is a corridor-level reconstruction from the source-stated Mirchaiya and Tingla terminals, the Maruwa/Katari reroute context, and the municipal corridor through Okhaldhunga.

It should be read as a faithful directional corridor, not as final engineering alignment.

## Confidence

Public decision: **default-visible with explicit QA warning**.

The line is important and operational, so it remains visible. The warning exists because the geometry is low-confidence and because NEA sources appear to mix route-km and circuit-km: the older yearbook describes a 90 km route, while later inventory-style reporting lists 180 km, likely double-circuit conductor accounting.

## Caveats

This corridor needs a true route-grade IEE/RAP/alignment source before it can be promoted. Until then, the map should keep the confidence caveat visible.

## See also

- [[data-layer-transmission-connected-traced-network]]
- [[nea-transmission-annual-book-2077]]
- [[claim-transmission-immediate-blocker]]
