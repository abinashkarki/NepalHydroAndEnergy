---
title: Layer: Priority Watchlist
type: data
created: 2026-04-25
updated: 2026-04-25
figure_type: map-layer-label
sources: [data-map-inventory]
tags: [maps, geojson, layers, explorer, legend]
---

# Layer: Priority Watchlist

**Explorer label:** Priority watchlist  
**Layer group:** Hydropower layers  
**Feature count:** 12

Curated strategically important projects by size, storage value, basin leverage, financing, or transmission dependence.

## What It Represents

The priority watchlist is a hand-picked set of hydropower projects that should stay visible even when the wider operating, generation-license, and survey clouds are switched off. It is not meant to be exhaustive. It is a reading layer for projects that carry disproportionate analytical weight in the wiki's core argument about seasonal value, grid constraints, and delivery risk.

The layer deliberately mixes two kinds of records:

| Group | Projects | Why They Stay Visible |
|-------|----------|-----------------------|
| Priority operating / buildout | Upper Bhotekoshi, Kali Gandaki A, Andhi Khola, Upper Tamakoshi, Tanahu, Upper Trishuli-1 | Operating or generation-stage anchors that make the abstract system argument concrete: visible sites, central corridors, storage relevance, or large commissioned capacity. |
| Radar survey | Nalsyau Gad, Mugu Karnali Storage, Arun 3, Upper Karnali, Betan Karnali, Phukot Karnali | Survey-stage projects that shape the long-run strategic map because of size, basin position, storage value, export relevance, or Karnali/Koshi corridor leverage. |

This is the layer to use when the map needs a strategic reading list rather than a licensing inventory. It links the project geography to articles such as [[storage-deficit]], [[claim-mw-not-equal-value]], [[claim-transmission-immediate-blocker]], and [[twenty-year-strategy]].

## Included Projects

| Project | MW | River / Basin Signal | Status | Why It Is On The Watchlist |
|---------|---:|----------------------|--------|----------------------------|
| Upper Bhotekoshi | 45 | Bhote Koshi | Operation | Existing valley plant with legible site geometry; useful for checking whether mapped hydro points behave like real assets. |
| Kali Gandaki A | 144 | Kali Gandaki | Operation | Major operating Gandaki anchor and benchmark for the older public hydro fleet. |
| Andhi Khola | 9.4 | Andhi Khola / Gandaki | Operation | Small operating plant, but analytically important because Andhi Khola also appears in storage-comparison work. |
| Upper Tamakoshi | 456 | Tama Koshi | Generation | Largest commissioned domestic project in the stack; a required reference point for capacity versus delivered value. |
| Tanahu | 140 | Seti Khola / Gandaki | Generation | Most practical near-term new storage addition in the checked official set. |
| Upper Trishuli-1 | 216 | Trishuli | Generation | Central-north project tied to the Trishuli evacuation corridor and grid-first reading of project value. |
| Nalsyau Gad | 410 | Nalsyau / Karnali | Survey | Best dry-energy performer in the JICA promising-storage set. |
| Mugu Karnali Storage | 1,902 | Karnali | Survey | Largest survey-stage project in the registry and a headline test case for capacity, storage, and remoteness. |
| Arun 3 | 900 | Arun / Koshi | Survey | National-scale eastern corridor project with export and construction-system implications. |
| Upper Karnali | 900 | Karnali | Survey | Strategic Karnali project whose value depends as much on politics, financing, and evacuation as on MW. |
| Betan Karnali | 688 | Karnali | Survey | Large Karnali-basin candidate relevant to the storage-and-seasonality story. |
| Phukot Karnali | 426 | Karnali | Survey | Major Karnali project with a stronger document-backed project-area anchor than many survey records. |

## How To Read It

Turn this layer on first when orienting around the power-system map. Then add operating hydropower, survey-stage hydropower, storage shortlist, transmission corridors, and cross-border interconnections to see what each priority marker depends on.

The most important fields are:

| Field | How To Use It |
|-------|---------------|
| `group` / `group_label` | Separates current-system anchors from long-run radar projects. |
| `capacity_mw` | Shows scale, but should be read against storage, dry energy, and evacuation context. |
| `license_type` | Distinguishes operating or generation-stage assets from survey-stage possibilities. |
| `priority_read` | Gives the editorial reason the project was promoted into the watchlist. |
| `location_basis` | Explains whether the marker comes from a registry point, a document-backed anchor, or a river-aligned reference. |
| `precision_label` | Tells the reader how much locational confidence to attach to the marker. |

The watchlist is also a navigation device. If a marker raises a question, the next step is usually an entity page, a corridor page, or a concept page rather than another marker layer.

## Caveats

The watchlist is editorial. It is not a ranking by commercial readiness, social acceptability, government priority, benefit-cost ratio, or environmental acceptability. It reflects the analytical frame of this wiki: winter value, system bottlenecks, geopolitical leverage, and delivery risk.

Survey-stage markers should not be read as precise dam coordinates unless the `location_basis` says so. Several records are river-aligned references built from public project data, not site-grade engineering linework. That is intentional: the layer is for strategic map reading, while project-level due diligence still requires the underlying feasibility, EIA, RAP, licensing, and transmission documents.

## Linked Data

- [priority_project_watchlist.geojson](../../../data/processed/maps/priority_project_watchlist.geojson) - 12-feature watchlist layer used by the explorer.
- [[data-layer-storage-shortlist]] - overlapping storage and storage-like candidates.
- [[data-layer-top-10-capacity-projects]] - pure capacity-rank comparator.

## Related

- [[twenty-year-strategy]]
- [[storage-deficit]]
- [[claim-mw-not-equal-value]]
- [[claim-transmission-immediate-blocker]]
- [[project-roadmap]]

- [[data-map-layer-labels]]
- [[data-map-inventory]]
