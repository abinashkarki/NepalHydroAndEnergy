---
title: Layer: Top-10 Capacity Projects
type: data
created: 2026-04-25
updated: 2026-04-25
figure_type: map-layer-label
sources: [data-map-inventory]
tags: [maps, geojson, layers, explorer, legend]
---

# Layer: Top-10 Capacity Projects

**Explorer label:** Top 10 largest  
**Layer group:** Hydropower layers  
**Feature count:** 10

Largest hydropower projects in the display set, useful for separating headline MW from deliverable system value.

## What It Represents

This layer highlights the ten largest hydropower projects in the display set by installed capacity. It is intentionally blunt: it makes the headline-MW story visible so the rest of the wiki can test whether capacity alone explains value.

The layer is a comparator, not a recommendation list. It should be read beside [[data-layer-storage-shortlist]], [[data-layer-priority-watchlist]], basin seasonality, and transmission layers. Large MW can be valuable, but only if the project can produce at the right time, evacuate power through the grid, manage financing and construction risk, and clear domestic or cross-border commercial constraints.

## Included Projects

| Rank | Project | MW | River | District | Status | Promoter |
|-----:|---------|---:|-------|----------|--------|----------|
| 1 | Mugu Karnali Storage HEP | 1,902 | Karnali | Bajura | Survey | Vidhyut Utpadan Company Limited |
| 2 | Arun 3 | 900 | Arun | Sankhuwasabha | Survey | Satluj Jal Vidyut Nigam Limited |
| 3 | Upper Karnali | 900 | Karnali | Surkhet | Survey | GMR, Upper Karnali Hydropower Limited |
| 4 | Uttarganga Storage Hydropower Project | 828 | Uttar Ganga | Baglung | Survey | Nepal Electricity Authority |
| 5 | Betan Karnali HP | 688 | Karnali | Achham | Survey | Betan Karnali Sanchayakarta Hydropower Company Ltd |
| 6 | Tamakoshi 3 | 650 | Tama Koshi | Dolakha | Survey | TBI Holding Co. Ltd. |
| 7 | Upper Tamakoshi HPP | 456 | Tama Koshi | Dolakha | Generation | Upper Tamakoshi Hydropower Limited |
| 8 | Kimathanka Arun HEP | 450 | Arun | Sankhuwasabha | Survey | Vidhyut Utpadan Company Limited |
| 9 | Bheri-1 HEP | 440 | Bheri | Rukum West | Survey | Gezhouba Group Power Investment Nepal Pvt. Ltd. |
| 10 | Phukot Karnali | 426 | Karnali | Kalikot | Survey | Vidhyut Utpadan Company Limited |

The list is dominated by Karnali, Arun/Koshi, and Tama Koshi projects. That matters because the biggest capacity markers are not evenly distributed across Nepal; they cluster in remote or corridor-dependent basins where transmission, access, financing, and export arrangements often decide whether MW becomes useful energy.

## How To Read It

Use it to compare project scale, basin location, license status, and promoter context. Then cross-check every marker against:

| Cross-Check | Why It Matters |
|-------------|----------------|
| Storage shortlist | Shows whether the project can help the dry-season deficit or mainly adds wet-season energy. |
| Basin seasonality | Reveals whether the basin's hydrology reinforces the seasonal mismatch. |
| Transmission corridors | Tests whether the project has a credible route to load centers or export gateways. |
| Cross-border links and gateways | Matters for projects whose economics depend on selling surplus power outside Nepal. |
| Priority watchlist | Shows whether the project is analytically important beyond size alone. |

The top-10 layer is especially useful for challenging simple capacity narratives. For example, Mugu Karnali is by far the largest marker, but its strategic meaning is different from Upper Tamakoshi, which is already in the generation-stage stack, or Tanahu, which is smaller but more important to near-term storage. Big capacity is the beginning of the question, not the answer.

The key fields are:

| Field | How To Use It |
|-------|---------------|
| `rank` | Capacity rank within this display set. |
| Capacity (`capacity_mw`) | Installed capacity used for ranking. |
| Status (`license_type`) | Indicates whether the marker is survey-stage or generation-stage. |
| `promoter` | Helps connect the project to public, private, foreign, or mixed delivery structures. |
| Location source (`location_basis`) | Explains how the map point was anchored. |
| `precision_label` | Distinguishes stronger river-aligned references from lower-confidence registry references. |

## Caveats

Capacity rank is a blunt lens. It can overvalue wet-season energy, ignore grid bottlenecks, and hide financing, resettlement, environmental, construction, and geopolitical risk. The layer is useful precisely because it exposes the temptation to equate MW with value.

Most records in this layer are survey-stage. A survey-stage 900 MW marker is not equivalent to an operating 900 MW plant, and a large marker does not imply near-term delivery. Marker precision also varies. Bheri-1 is explicitly marked as a low-confidence registry reference, while Mugu Karnali and Phukot Karnali use document-backed project-area centers or river-aligned references.

## Linked Data

- [top_capacity_project_annotations.geojson](../../../data/processed/maps/top_capacity_project_annotations.geojson) - 10-feature capacity-rank annotation layer.
- [[data-layer-priority-watchlist]] - strategic subset that overlaps with, but is not identical to, capacity rank.
- [[data-layer-storage-shortlist]] - dry-season value comparator.

## Related

- [[claim-mw-not-equal-value]]
- [[twenty-year-strategy]]
- [[storage-deficit]]
- [[claim-transmission-immediate-blocker]]
- [[data-layer-basin-seasonality]]

- [[data-map-layer-labels]]
- [[data-map-inventory]]
