# Corridor Tracing Workflow

## Purpose

This workflow upgrades the current transmission-corridor map from indicative substation spines to source-backed traced geometry.

The key rule is simple:

- traced route geometry should only come from route-grade source maps
- corridor spines remain as fallback geometry when traced segments do not yet exist

## Current source stack

Best currently downloaded route-grade or near-route-grade sources:

- [RPGCL Nepal Transmission Network Map Revised 2021](/Users/hi/projects/nepalEnergy/data/raw/corridor_tracing/rpgcl/nepal_transmission_network_map_revised1.pdf)
- [MCA-Nepal Annex D-1 Alignment Maps](/Users/hi/projects/nepalEnergy/data/raw/corridor_tracing/mca/mca_annex_d1_alignment_maps.pdf)
- [MCA-Nepal Project Summary Report](/Users/hi/projects/nepalEnergy/data/raw/corridor_tracing/mca/mca_project_summary_report.pdf)
- [World Bank HDDTL RAP](/Users/hi/projects/nepalEnergy/data/raw/corridor_tracing/world_bank/world_bank_hddtl_rap.pdf)
- [MoEWRI IPSDP Executive Summary 2025](/Users/hi/projects/nepalEnergy/data/raw/corridor_tracing/moewri/moewri_ipsdp_exec_summary_2025.pdf)
- [JICA IPSDP Report Part 2](/Users/hi/projects/nepalEnergy/data/raw/corridor_tracing/jica/jica_ipsdp_report_part2.pdf)
- [ADB SASEC Operational Plan Update](/Users/hi/projects/nepalEnergy/data/raw/corridor_tracing/adb_sasec_operational_plan_update.pdf)
- [NEA Annual Report FY 2024/25](/Users/hi/projects/nepalEnergy/data/raw/projects_storage/nea_annual_report_2024_2025.pdf)

Desired NEA route PDFs still need recovery into the local packet:

- `nea_marsyangdi_rap.pdf`
- `nea_kabeli_iee.pdf`

## Canonical files

Source inventory and manifest:

- [corridor_source_inventory.csv](/Users/hi/projects/nepalEnergy/data/processed/corridor_tracing/manifests/corridor_source_inventory.csv)
- [corridor_trace_manifest.csv](/Users/hi/projects/nepalEnergy/data/processed/corridor_tracing/manifests/corridor_trace_manifest.csv)
- [corridor_source_inventory.json](/Users/hi/projects/nepalEnergy/data/processed/corridor_tracing/manifests/corridor_source_inventory.json)
- [corridor_trace_manifest.json](/Users/hi/projects/nepalEnergy/data/processed/corridor_tracing/manifests/corridor_trace_manifest.json)

Page indexes:

- `data/processed/corridor_tracing/manifests/*_page_index.json`

Rendered page outputs:

- `data/processed/corridor_tracing/rendered_pages/`

Future traced geometry target:

- `data/processed/maps/transmission_corridor_traced_segments.geojson`
- `data/processed/maps/rpgcl_transmission_official_linework.geojson`
- `data/processed/maps/rpgcl_transmission_official_labels.geojson`
- `data/processed/maps/rpgcl_transmission_trace_report.json`

## Scripts

Build source inventory and manifest:

```bash
/Users/hi/projects/nepalEnergy/.venv/bin/python /Users/hi/projects/nepalEnergy/scripts/build_corridor_tracing_manifest.py
```

Index PDF pages with pypdf text and OCR fallback:

```bash
/Users/hi/projects/nepalEnergy/.venv/bin/python /Users/hi/projects/nepalEnergy/scripts/index_corridor_pdf_pages.py --source-id mca_annex_d1_alignment_maps --force-ocr
```

Render the manifest-listed pages:

```bash
/Users/hi/projects/nepalEnergy/.venv/bin/python /Users/hi/projects/nepalEnergy/scripts/render_corridor_pdf_pages.py --corridor-id hddi_400
```

Extract official vector linework and traced corridors from the RPGCL geospatial PDF:

```bash
/Users/hi/projects/nepalEnergy/.venv/bin/python /Users/hi/projects/nepalEnergy/scripts/extract_rpgcl_transmission_vectors.py
```

## Trace order

1. `hddi_400`
2. `mca_central_400`
3. `hetauda_bharatpur_bardaghat_220`
4. `udipur_damauli_bharatpur_220`
5. `kabeli_132`
6. `solu_tingla_mirchaiya_132`

## Data model for traced segments

Each traced segment should be stored as one feature, not one whole-corridor line.

Minimum properties:

- `corridor_id`
- `segment_id`
- `segment_name`
- `status`
- `voltage_kv`
- `source_id`
- `page_start`
- `page_end`
- `trace_method`
- `trace_confidence`
- `official_length_km`
- `geometry_basis`
- `notes`

## Quality gates

Before a traced segment replaces a spine:

- both endpoints must land on the correct named nodes
- the segment must be tied to a specific source page or sheet
- traced length should be checked against any official length in the source
- if the source is schematic rather than route-accurate, mark the confidence down instead of overstating precision

## Current state

As of this pass:

- the repo has a stable local packet structure for corridor tracing
- the World Bank HDDTL route packet and MCA alignment atlas are local
- the manifest distinguishes route-grade sources from reference-only sources
- the page-index and page-render scripts are in place
- the official RPGCL geospatial PDF is local and now drives a vector extraction workflow
- the repo now contains committed traced geometry for four corridors:
  - `hddi_400`
  - `hetauda_bharatpur_bardaghat_220`
  - `mca_central_400`
  - `udipur_damauli_bharatpur_220`
- the eastern 132 kV cases remain intentionally unresolved in traced form because the public map’s Kathmandu inset overlaps the underlying national map and the NEA route-grade RAP/IEE packets are still missing locally
