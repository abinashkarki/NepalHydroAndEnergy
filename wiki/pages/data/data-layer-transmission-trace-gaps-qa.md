---
title: Internal Data: Transmission Trace Gaps
type: data
created: 2026-04-25
updated: 2026-05-13
figure_type: map-layer-label
sources: [data-map-inventory]
tags: [maps, geojson, layers, explorer, legend]
page_quality: analysis
---

# Internal Data: Transmission Trace Gaps

**Explorer label:** Not shown as a map-control layer  
**Layer group:** Internal transmission audit data  
**Feature count:** 0

Evidence gaps in traced geometry when they exist. These are audit markers, not physical lines.

## Summary

This internal dataset records evidence gaps in reconstructed transmission geometry when such gaps exist. It is an audit layer for tracing confidence, not a physical-grid layer.

## What It Represents

This dataset is the pipeline's honesty layer for transmission tracing. It records where linework has gaps, breaks, or uncertainty so the public map does not make incomplete geometry look more authoritative than it is. It is currently empty after the latest corridor repair pass and no longer appears as a reader-facing layer.

## How To Read It

Use it when validating the grid layers or reviewing where source recovery remains incomplete. It records why a corridor may appear disconnected or why a connected-network layer includes inferred segments.

## Coverage / Method

The dataset currently has 0 features. When populated, features document gaps, breaks, or uncertainty in reconstructed transmission linework so internal QA can distinguish evidence limitations from real-world grid gaps.

## Caveats

An audit gap is not necessarily a real-world gap in the grid. It is a gap in the reconstructed map evidence or tracing confidence.

## Related

- [[data-map-inventory]]
- [[project-roadmap]]
- [[nepal-transmission-landscape-2025]]

- [[data-map-layer-labels]]
- [[data-map-inventory]]
