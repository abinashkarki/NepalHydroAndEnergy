---
title: Marsyangdi Corridor Manang-Khudi-Udipur 220 kV
type: entity
category: transmission-corridor
created: 2026-04-25
updated: 2026-04-25
sources: [nepal-transmission-landscape-2025, nea_marsyangdi_rap_upper]
tags: [transmission, 220kv, marsyangdi, under-construction, traced-corridor]
generator: manual
page_quality: analysis
---

# Marsyangdi Corridor Manang-Khudi-Udipur 220 kV

The Marsyangdi upper 220 kV corridor is the upstream evacuation path from the Manang/upper Marsyangdi area south through Khudi and Besishahar toward Udipur. It matters because western and central hydropower build-out depends on moving generation out of the Marsyangdi basin without overloading older lower-voltage paths.

## Key Facts

| Parameter | Value |
|-----------|-------|
| Voltage | 220 kV |
| Status | Under construction |
| Corridor ID | `marsyangdi_upper_220` |
| Public map feature | `marsyangdi_upper_220_main` |
| Source basis | Upper Marsyangdi RAP pages 33-36 |
| Official route length | 46.0 km |
| Traced network length | 40.385 km |
| Validation delta | -12.21% |

## Map Interpretation

The map trace is document-grounded: it follows the recovered upper Marsyangdi RAP location, project-area, and access-map context, anchored to Dharapani, Khudi, Besishahar, and Udipur.

This is not an official GIS alignment. It is better than a conceptual substation spine, but it should still be read as a basin-corridor trace rather than a precise tower alignment.

## Confidence

Public decision: **default-visible, caveated**.

The feature has no endpoint gaps in the connected network. The caveat is precision: the current trace is manual/document-grounded and about 12% short against the working 46 km route basis.

## Caveats

The next improvement is source triangulation rather than topology repair. The branch endpoints and route length should be checked against the upper Marsyangdi RAP and the EIB/NEA companion material before promoting this to a higher-confidence route.

## See also

- [[udipur-damauli-bharatpur-220]]
- [[marsyangdi]]
- [[mca-central-400]]
- [[data-layer-transmission-connected-traced-network]]
