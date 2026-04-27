---
title: Internal Data: Source Trace Fragments
type: data
created: 2026-04-25
updated: 2026-04-25
figure_type: map-layer-label
sources: [data-map-inventory]
tags: [maps, geojson, layers, explorer, legend]
---

# Internal Data: Source Trace Fragments

**Explorer label:** Not shown as a map-control layer  
**Layer group:** Internal transmission audit data  
**Feature count:** 22

Source/manual trace fragments preserved behind the scenes for audit and reproducibility.

## What It Represents

This dataset preserves the traced segments recovered from transmission maps and reports before the public network presentation is simplified. It is useful for audit trails and geometry QA, but it is no longer exposed as a separate reader-facing map layer because it substantially overlaps the major transmission network.

## How To Read It

Use it when maintaining the pipeline and checking where a corridor trace came from, how many pieces it has, or how a source map was translated into explorer geometry.

## Caveats

Source trace does not mean perfect. Segments can be partial, approximate, or source-map dependent. The reader-facing grid layer is [[data-layer-transmission-connected-traced-network]].

## Related

- [[nepal-transmission-landscape-2025]]
- [[data-map-inventory]]
- [[claim-transmission-immediate-blocker]]

- [[data-map-layer-labels]]
- [[data-map-inventory]]
