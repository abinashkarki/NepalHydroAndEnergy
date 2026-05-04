# Corridor Tracing Workflow

## Purpose

This workflow upgrades the current transmission-corridor map from indicative substation spines to source-backed traced geometry.

The key rule is simple:

- traced route geometry should only come from route-grade source maps
- corridor spines remain as fallback geometry when traced segments do not yet exist

## Current source stack

Best currently downloaded route-grade or near-route-grade sources:

- [RPGCL Nepal Transmission Network Map Revised 2021](./data/raw/corridor_tracing/rpgcl/nepal_transmission_network_map_revised1.pdf)
- [MCA-Nepal Annex D-1 Alignment Maps](./data/raw/corridor_tracing/mca/mca_annex_d1_alignment_maps.pdf)
- [MCA-Nepal Project Summary Report](./data/raw/corridor_tracing/mca/mca_project_summary_report.pdf)
- [World Bank HDDTL RAP](./data/raw/corridor_tracing/world_bank/world_bank_hddtl_rap.pdf)
- [MoEWRI IPSDP Executive Summary 2025](./data/raw/corridor_tracing/moewri/moewri_ipsdp_exec_summary_2025.pdf)
- [JICA IPSDP Report Part 2](./data/raw/corridor_tracing/jica/jica_ipsdp_report_part2.pdf)
- [ADB SASEC Operational Plan Update](./data/raw/corridor_tracing/adb_sasec_operational_plan_update.pdf)
- [NEA Annual Report FY 2024/25](./data/raw/projects_storage/nea_annual_report_2024_2025.pdf)
- [NEA Marsyangdi RAP](./data/raw/corridor_tracing/nea/nea_marsyangdi_rap.pdf)
- [NEA Upper Marsyangdi RAP](./data/raw/corridor_tracing/nea/nea_marsyangdi_rap_upper.pdf)
- [NEA Kabeli IEE](./data/raw/corridor_tracing/nea/nea_kabeli_iee.pdf)
- [NEA Kabeli SMEF](./data/raw/corridor_tracing/nea/nea_kabeli_smef.pdf)

## Canonical files

Source inventory and manifest:

- [corridor_source_inventory.csv](./data/processed/corridor_tracing/manifests/corridor_source_inventory.csv)
- [corridor_trace_manifest.csv](./data/processed/corridor_tracing/manifests/corridor_trace_manifest.csv)
- [corridor_source_inventory.json](./data/processed/corridor_tracing/manifests/corridor_source_inventory.json)
- [corridor_trace_manifest.json](./data/processed/corridor_tracing/manifests/corridor_trace_manifest.json)

Page indexes:

- `data/processed/corridor_tracing/manifests/*_page_index.json`

Rendered page outputs:

- `data/processed/corridor_tracing/rendered_pages/`
- `data/processed/corridor_tracing/mca_annex_d1/`

Generated transmission geometry and QA outputs:

- `data/processed/maps/transmission_corridor_traced_segments.geojson`
- `data/processed/maps/transmission_corridor_traced_network.geojson`
- `data/processed/maps/transmission_network_nodes.geojson`
- `data/processed/maps/cross_border_interconnection_lines.geojson`
- `data/processed/maps/transmission_trace_gap_report.geojson`
- `data/processed/maps/transmission_corridor_validation_report.json`
- `data/processed/maps/transmission_corridor_validation_report.csv`
- `data/processed/maps/transmission_network_build_report.json`
- `data/processed/maps/transmission_corridor_dossiers.json`
- `data/processed/maps/cross_border_interconnection_dossiers.json`
- `docs/maps/grid_confidence_report.md`
- `docs/maps/transmission_warning_burndown.md`
- `data/processed/maps/rpgcl_transmission_official_linework.geojson`
- `data/processed/maps/rpgcl_transmission_official_labels.geojson`
- `data/processed/maps/rpgcl_transmission_trace_report.json`
- `data/raw/corridor_tracing/mca/mca_central_400_atlas_trace.geojson`
- `data/raw/corridor_tracing/nea/hetauda_bharatpur_bardaghat_220_source_trace.geojson`
- `data/raw/corridor_tracing/nea/udipur_damauli_bharatpur_220_rap_trace.geojson`

## Scripts

Build source inventory and manifest:

```bash
./.venv/bin/python ./scripts/build_corridor_tracing_manifest.py
```

Index PDF pages with pypdf text and OCR fallback:

```bash
./.venv/bin/python ./scripts/index_corridor_pdf_pages.py --source-id mca_annex_d1_alignment_maps --force-ocr
```

Build the visual sheet index for the scanned MCA Annex D-1 atlas:

```bash
./.venv/bin/python ./scripts/build_mca_annex_atlas_index.py
```

Render the manifest-listed pages:

```bash
./.venv/bin/python ./scripts/render_corridor_pdf_pages.py --corridor-id hddi_400
```

Extract official vector linework and traced corridors from the RPGCL geospatial PDF:

```bash
./.venv/bin/python ./scripts/extract_rpgcl_transmission_vectors.py
```

For `mca_central_400`, the extraction step uses `data/raw/corridor_tracing/mca/mca_central_400_atlas_trace.geojson` when present. That atlas trace replaces the older RPGCL overview fragments in the public traced segment output while preserving the RPGCL linework files for audit.

For `hetauda_bharatpur_bardaghat_220`, the extraction step uses `data/raw/corridor_tracing/nea/hetauda_bharatpur_bardaghat_220_source_trace.geojson` when present. That source trace replaces over-selected RPGCL overview fragments in the public traced segment output while preserving the RPGCL linework files for audit.

For `hddi_400`, the extraction step uses `data/raw/corridor_tracing/world_bank/hddi_400_rap_trace.geojson` when present. That RAP-controlled source trace replaces the oversimplified RPGCL overview fragments in the public traced segment output while preserving the RPGCL linework files for audit.

For `udipur_damauli_bharatpur_220`, the extraction step uses `data/raw/corridor_tracing/nea/udipur_damauli_bharatpur_220_rap_trace.geojson` when present. That RAP trace replaces the older RPGCL overview fragments in the public traced segment output while preserving the RPGCL linework files for audit.

Build the connected public network, conservative cross-border lines, nodes, validation report, and gap diagnostics:

```bash
./.venv/bin/python ./scripts/build_transmission_network_layers.py
```

Build the source-confidence dossiers and reader-facing grid confidence report:

```bash
./.venv/bin/python ./scripts/build_grid_confidence_report.py
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

## Connected network model

The public default layer is `transmission_corridor_traced_network.geojson`, not the raw traced-fragment layer. It is generated from `transmission_corridor_traced_segments.geojson`, the curated corridor spine, place anchors, cross-border point metadata, and the corridor manifest.

Every network edge carries:

- `corridor_id`
- `segment_id`
- `segment_name`
- `voltage_kv`
- `status`
- `geometry_role`
- `trace_method`
- `trace_confidence`
- `source_id`
- `source_pdf`
- `source_page_or_sheet`
- `from_node_id`
- `to_node_id`
- `length_km`
- `length_delta_pct`
- `geometry_basis`
- `notes`

`geometry_role=source_trace` means the geometry came from official vector linework. `geometry_role=manual_trace` means the geometry was manually traced from a source document. `geometry_role=inferred_connector` means only a short topology connector was added between traced endpoints inside the explicit snap threshold. The connector is never treated as source-traced infrastructure.

## Quality gates

Before a traced segment replaces a spine:

- both endpoints must land on the correct named nodes
- the segment must be tied to a specific source page or sheet
- traced length should be checked against any official length in the source
- if the source is schematic rather than route-accurate, mark the confidence down instead of overstating precision
- inferred connectors must stay visually and structurally distinguishable from source/manual traces
- endpoint gaps outside the automatic snap threshold must remain in `transmission_trace_gap_report.geojson`
- route-km and circuit-km must not be compared without stating the basis
- planned, implementation-stage, and under-construction cross-border links must not render like operational links

## Current state

As of this pass:

- the repo has a stable local packet structure for corridor tracing
- the World Bank HDDTL route packet and MCA alignment atlas are local
- the manifest distinguishes route-grade sources from reference-only sources
- the page-index and page-render scripts are in place
- the official RPGCL geospatial PDF is local and now drives a vector extraction workflow
- the repo contains traced geometry for seven corridor families:
  - `hddi_400`
  - `hetauda_bharatpur_bardaghat_220`
  - `mca_central_400`
  - `udipur_damauli_bharatpur_220`
  - `kabeli_132`
  - `marsyangdi_upper_220`
  - `solu_tingla_mirchaiya_132`
- `hddi_400`, `hetauda_bharatpur_bardaghat_220`, `kabeli_132`, `marsyangdi_upper_220`, and `solu_tingla_mirchaiya_132` are now represented as manual/document-grounded traces rather than default RPGCL vector extraction where the document evidence is more faithful than the overview map
- `solu_tingla_mirchaiya_132` should be read against a 90 km route-km basis; the 180 km NEA annual-report entry appears to be circuit-km
- the connected-network builder adds short inferred connectors only inside conservative thresholds and leaves larger breaks as QA gap features
