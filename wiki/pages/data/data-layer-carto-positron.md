---
title: Layer: Carto Positron Basemap
type: data
created: 2026-04-25
updated: 2026-05-13
figure_type: map-layer-label
sources: [data-map-inventory]
tags: [maps, geojson, layers, explorer, legend]
page_quality: analysis
---

# Layer: Carto Positron Basemap

**Explorer label:** Carto Positron  
**Layer group:** Basemaps  
**Feature count:** basemap

Neutral light basemap for reading dense hydrology, project, and transmission overlays without heavy terrain shading.

## Summary

This data page describes the Carto Positron basemap layer used as the explorer's neutral visual ground plane. It provides a quiet reference map for reading hydrology, project, transmission, and basin overlays without treating the basemap itself as project evidence.

## What It Represents

Carto Positron is the default visual ground plane for the explorer. It is intentionally quiet: roads, settlements, borders, water bodies, and labels remain visible, but the style avoids strong terrain color and imagery texture that would compete with project markers or basin polygons.

## How To Read It

Use this basemap when comparing several overlays at once. It is best for dense views such as operating plus construction hydropower, basin polygons with tributaries, or transmission corridors with node layers. If the question is about layer relationships rather than landform interpretation, this should usually be the first choice.

## Coverage / Method

The layer is a basemap option in the explorer rather than a project, hydrology, or transmission dataset. Its coverage and behavior are documented through [[data-map-inventory]] and the explorer layer configuration.

## Caveats

Because the basemap is visually restrained, it is not the right layer for judging slopes, ridges, road access, reservoir surfaces, or land-cover constraints. Switch to Topographic or Satellite when geography itself is the evidence.

## Related

- [[data-map-inventory]]
- [[buildability]]

- [[data-map-layer-labels]]
- [[data-map-inventory]]
