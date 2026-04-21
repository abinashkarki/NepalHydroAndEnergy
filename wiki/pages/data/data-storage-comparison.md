---
title: Storage Capacity Comparison
type: data
created: 2026-04-14
updated: 2026-04-15
figure_type: chart-spec
sources: [wb-water-sector-diagnostic, wb-ganges-strategic-basin-assessment]
tags: [storage, dams, per-capita, international-comparison]
---

# Storage Capacity Comparison

Nepal's water storage infrastructure compared to regional and global peers. This is the single most dramatic infrastructure gap in the entire analysis.

## Per-Capita Dam Storage

| Country | Per-Capita Storage (m³/person) | Notes | Source |
|---------|-------------------------------|-------|--------|
| Norway | ~15,100 | Wide glacial valleys, stable geology, hydro model | Claude |
| China | ~664 | Massive dam-building programme | Claude |
| Global average | ~900 | | Claude |
| India | ~180 | Itself criticized as inadequate | Claude |
| **Nepal** | **~5** | Almost entirely [[kulekhani-cascade]] | Claude |

Nepal has **1/36th** of India's per-capita storage, which is itself well below global average.

## Nepal's Current Storage

| Facility | Capacity (MW) | Storage Volume | Generation (FY 2024/25) |
|----------|--------------|----------------|------------------------|
| Kulekhani I | 60 | ~85 MCM active | |
| Kulekhani II | 32 | (cascade) | |
| Kulekhani III | 14 | (cascade) | |
| **Total** | **106** | **~85–150 MCM** | **279.8 GWh** |

> [!contradiction]
> World Bank Water Diagnostic cites 85 MCM active storage. Claude cites 130–150 MCM total. Likely different boundaries (active vs gross reservoir volume). Both are negligible relative to need.

## Storage Need

- Seasonal storage requirement: **29.86 km³** ([[wb-water-sector-diagnostic]])
- Current storage: ~0.085–0.15 km³
- Gap: **~200x shortfall**
- JICA estimate: Nepal needs **1,993–3,154 MW** of storage hydropower by 2032

## Dry-Energy Shortlist From The Merged Research Workspace

The code repo added a machine-readable shortlist that is more useful than headline MW alone because it ranks projects by **dry-energy contribution**:

| Project | Basin | Installed MW | Dry Energy (GWh) | Dry Share | Why It Matters |
|---------|-------|-------------:|-----------------:|----------:|----------------|
| [[dudhkoshi-storage]] | [[koshi-basin]] | 670 | **1,252.0** | **37.1%** | Strongest Nepal-side dry-season block in the checked official set |
| Nalsyau Gad | [[karnali-basin]] | 410 | **581.8** | **41.4%** | Best dry-energy share in the JICA promising-project shortlist |
| Lower Badigad | [[gandaki-basin]] | 380.3 | **354.7** | **26.0%** | Large Gandaki carryover storage with meaningful winter value |
| Naumure (W. Rapti) | West Rapti | 245 | **309.9** | **26.8%** | Medium-basin storage with unusually high seasonal-regulation value |
| Sun Koshi No.3 | [[koshi-basin]] | 536 | **335.9** | **17.8%** | Large reservoir block with meaningful dry support even if dry share is lower |

## Valley-Shape Paradox

| Dam | Height (m) | Storage Volume | Terrain |
|-----|-----------|----------------|---------|
| Aswan (Egypt) | 111 | 162 BCM | Flat desert |
| Andhi Khola (Nepal, proposed) | 110 | 0.9 BCM | V-shaped Himalayan valley |

Same dam height, **180x less storage**. Nepal's topography simultaneously enables hydropower (steep head) and prevents easy storage (narrow valleys).

## Off-River Pumped Hydro: The Bypass Route

A 2021 Oxford University study (Blakers et al., *Clean Energy*) identified **~2,800 off-river pumped hydro energy storage sites** in Nepal with combined storage capacity of **~50 TWh**. To balance a 100% renewable Nepal at advanced-economy consumption levels (~500 TWh/yr), only **~1.5 TWh** of storage is needed. Nepal has **17x more pumped-hydro potential than it would ever need** — entirely off-river, avoiding the valley-shape paradox.

This reframes the storage deficit: Nepal is not storage-poor in potential — it is storage-poor in **executed infrastructure**. The bottleneck is capital, governance, and institutional will, not geology. See also [[data-mountain-hydro-comparison]].

## Linked Data

- [nepal_storage_dry_energy_shortlist.csv](../../../data/processed/tables/nepal_storage_dry_energy_shortlist.csv) — 12-project storage shortlist with total storage, effective storage, annual energy, dry energy, and editorial priority notes.

## Linked Figures

- [storage_gap.png](../../../figures/storage_gap.png) — current storage versus JICA-estimated storage need.

## Chart Specification

Bar chart of per-capita storage across countries (log scale recommended given the range from 5 to 15,100). Nepal's bar should be visually striking. Second panel: the valley-shape paradox as a simple side-by-side cross-section diagram. Third panel: Nepal's 50 TWh pumped-hydro potential vs 1.5 TWh need — a simple ratio bar.
