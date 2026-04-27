---
title: Udipur-Damauli-Bharatpur 220 kV Reinforcement
type: entity
category: transmission-corridor
created: 2026-04-25
updated: 2026-04-25
sources: [nepal-transmission-landscape-2025, nea_marsyangdi_rap]
tags: [transmission, 220kv, marsyangdi, under-construction, traced-corridor]
---

# Udipur-Damauli-Bharatpur 220 kV Reinforcement

The Udipur-Damauli-Bharatpur 220 kV reinforcement is the lower Marsyangdi evacuation route from the Udipur area toward Bharatpur/Aptari. In the map it is represented as the source-backed **Udipur-Markichowk-Bharatpur** line because that is the route basis stated in the recovered NEA Marsyangdi RAP.

## Key Facts

| Parameter | Value |
|-----------|-------|
| Voltage | 220 kV |
| Status | Under construction |
| Corridor ID | `udipur_damauli_bharatpur_220` |
| Public map feature | `udipur_markichowk_bharatpur_220_rap_trace` |
| Source basis | NEA Marsyangdi RAP pages 22-24 |
| Official route length | 64.45 km |
| Traced network length | 65.311 km |
| Validation delta | +1.34% |

## Map Interpretation

This corridor is now represented by a single RAP-backed trace in the connected transmission layer. It replaces the older RPGCL overview extraction, which showed the same corridor as many disconnected fragments.

The trace should be read as a corridor-level alignment, not a tower-by-tower engineering route. The RAP text gives 64.45 route-km, while the project map labels the same Udipur-Markichowk-Bharatpur line as 67 km. The current map trace falls inside that source envelope.

## Confidence

Public decision: **default-visible, high confidence**.

The confidence comes from three checks: the route is backed by a project RAP, the public feature has no inferred connectors, and the traced length is within 2% of the RAP route-length basis.

## Caveats

Khudi-Udipur is not forced into this corridor. It should remain a separate scope item unless a route-grade source confirms that it belongs in this segment rather than in the upper Marsyangdi package.

## See also

- [[marsyangdi-upper-220]]
- [[mca-central-400]]
- [[data-layer-transmission-connected-traced-network]]
- [[claim-transmission-immediate-blocker]]
