---
title: Kabeli / Godak-Soyak-Amarpur 132 kV Corridor
type: entity
category: transmission-corridor
created: 2026-04-25
updated: 2026-04-25
sources: [nepal-transmission-landscape-2025, nea_kabeli_iee]
tags: [transmission, 132kv, kabeli, under-construction, traced-corridor]
---

# Kabeli / Godak-Soyak-Amarpur 132 kV Corridor

The Kabeli 132 kV corridor is an eastern Nepal branch network around the Soyak-Godak-Amarpur/Phidim area. It is represented as a branch corridor because the recovered NEA Kabeli IEE describes a bifurcated route rather than a single linear line.

## Key Facts

| Parameter | Value |
|-----------|-------|
| Voltage | 132 kV |
| Status | Under construction |
| Corridor ID | `kabeli_132` |
| Public map features | `kabeli_132_trunk`, `kabeli_132_godak_branch`, `kabeli_132_amarpur_branch` |
| Source basis | NEA Kabeli IEE pages 25-27 |
| Official route length | 83.74 km |
| Traced network length | 94.112 km |
| Validation delta | +12.39% |

## Map Interpretation

The connected network keeps Kabeli as a branch system: a southern trunk up to Soyak, one arm toward Godak, and one arm toward Phidim/Amarpur. The branch ends are not artificially connected to one another.

This matters for reader trust. A single forced line would look cleaner, but it would misrepresent the project structure.

## Confidence

Public decision: **default-visible, caveated**.

The branch topology is source-supported and has no remaining endpoint gaps. The caveat is route precision: the current manual trace is still a document-grounded reconstruction, not a digitized alignment sheet.

## Caveats

The highest-value improvement is to digitize the branch geometry more carefully from the Kabeli IEE route figures while preserving the trunk, Godak branch, and Amarpur/Phidim branch as separate network features.

## See also

- [[data-layer-transmission-connected-traced-network]]
- [[claim-transmission-immediate-blocker]]
- [[nepal-transmission-landscape-2025]]
