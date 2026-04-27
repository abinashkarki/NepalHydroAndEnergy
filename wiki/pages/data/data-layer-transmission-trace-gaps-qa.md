---
title: Internal Data: Transmission Trace Gaps
type: data
created: 2026-04-25
updated: 2026-04-25
figure_type: map-layer-label
sources: [data-map-inventory]
tags: [maps, geojson, layers, explorer, legend]
---

# Internal Data: Transmission Trace Gaps

**Explorer label:** Not shown as a map-control layer  
**Layer group:** Internal transmission audit data  
**Feature count:** 0

Evidence gaps in traced geometry when they exist. These are audit markers, not physical lines.

## What It Represents

This dataset is the pipeline's honesty layer for transmission tracing. It records where linework has gaps, breaks, or uncertainty so the public map does not make incomplete geometry look more authoritative than it is. It is currently empty after the latest corridor repair pass and no longer appears as a reader-facing layer.

## How To Read It

Use it when validating the grid layers or deciding where source recovery should improve next. It explains why a corridor may appear disconnected or why a connected-network layer includes inferred segments.

## Caveats

An audit gap is not necessarily a real-world gap in the grid. It is a gap in the reconstructed map evidence or tracing confidence.

## Related

- [[data-map-inventory]]
- [[project-roadmap]]
- [[nepal-transmission-landscape-2025]]

- [[data-map-layer-labels]]
- [[data-map-inventory]]
