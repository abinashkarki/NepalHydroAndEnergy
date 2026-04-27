---
title: Internal Data: Transmission Topology Nodes
type: data
created: 2026-04-25
updated: 2026-04-25
figure_type: map-layer-label
sources: [data-map-inventory]
tags: [maps, geojson, layers, explorer, legend]
---

# Internal Data: Transmission Topology Nodes

**Explorer label:** Not shown as a map-control layer  
**Layer group:** Internal transmission audit data  
**Feature count:** 56

Generated endpoint and junction nodes used to validate corridor topology.

## What It Represents

This point dataset is generated from traced corridor endpoints, inferred junctions, and supporting grid anchors. It helps validate whether the mapped network connects coherently, but it is no longer exposed as a public map control because many nodes are topology artifacts rather than visitor-facing infrastructure.

## How To Read It

Use it when maintaining the transmission pipeline: checking whether a line has plausible endpoints, where generated joins are happening, or whether topology is being over-interpreted.

## Caveats

These are internal topology nodes. Some represent real substations or hubs, while others are generated endpoint clusters. Do not read every marker as a surveyed asset.

## Related

- [[nepal-transmission-landscape-2025]]
- [[claim-transmission-immediate-blocker]]
- [[data-map-inventory]]

- [[data-map-layer-labels]]
- [[data-map-inventory]]
