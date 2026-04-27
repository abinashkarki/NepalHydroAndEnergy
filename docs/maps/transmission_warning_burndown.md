# Transmission Warning Burn-Down

Purpose: record the source review and product decision for every corridor currently flagged by the connected transmission-network validation.

The rule for this pass is conservative: do not make the public map look more complete by inventing linework. A corridor only gets connected where the source geometry, endpoint names, and length checks support the connection. Everything else stays visible as a QA warning or becomes a source-recovery task.

## Current result

- Original active warning list reviewed: 5 corridors
- Validator artifact resolved: 1 corridor
- Atlas trace repair completed: 1 corridor
- Active warning list after MCA atlas, Udipur RAP, HBB source-trace, and HDDI RAP repairs: 0 corridors
- Corridors needing source recovery or route re-digitization: 0 corridors

## Decisions by corridor

| corridor_id | What the warning meant | Source checked | Product decision | Next move |
| --- | --- | --- | --- | --- |
| `kabeli_132` | The validator was treating branch terminals as if they were missing linear joins. | NEA Kabeli IEE pages 25-27 confirm the route bifurcates at Soyak, with Godak and Amarpur/Phidim arms. | Resolved as a validator issue. Keep as a branch corridor, not a single forced line. | Later quality pass can improve branch lengths from the IEE route map, but do not connect branch ends to each other. |
| `udipur_damauli_bharatpur_220` | The old public trace used 16 disconnected RPGCL overview fragments. The earlier 85 km comparison was too broad for the currently represented route. | NEA Marsyangdi RAP pages 22-24. Text gives 64.45 km for Udipur-Markichowk-Bharatpur; Figure 2.1 labels the same line as 67 km. | Resolved into a default-visible RAP trace. Treat the geometry as a schematic corridor, not a tower-level alignment; keep Khudi-Udipur outside this segment until separately sourced. | Keep looking for any newer route-alignment source, but this no longer blocks the public connected network. |
| `hddi_400` | The RPGCL vector extraction was materially short and visually too straight against the official route-length basis. It also hid the mixed status of the two major sections. | World Bank HDDTL RAP location map, route text, and affected VDC/municipality corridor; NEA FY2024/25 project status and line inventory. | Resolved into two default-visible, caveated public segments: Hetauda-Dhalkebar marked under construction, and Dhalkebar-Inaruwa marked operational. No inferred connectors or endpoint gaps remain. | Keep looking for a tower/alignment-sheet source, but this no longer blocks the connected public network. |
| `hetauda_bharatpur_bardaghat_220` | The old public trace over-selected adjacent RPGCL 220 kV fragments and mixed route-km/circuit-km comparisons. | RPGCL 2021 geospatial 220 kV linework for Hetauda-New Bharatpur; NEA Bharatpur-Bardaghat SIA route basis; NEA annual-book circuit-km table; current public status references for 73 km Hetauda-Bharatpur and 74/73.5 km Bharatpur-Bardaghat. | Resolved into two default-visible, caveated public segments: Hetauda-New Bharatpur and New Bharatpur-Bardaghat. No inferred connectors or endpoint gaps remain. | Keep looking for a downloadable route map/alignment sheet, but this no longer blocks the connected public network. |
| `mca_central_400` | The old public trace used fragmented RPGCL overview linework. | MCC Nepal Compact provides the five-segment topology and 308.65 route-km component basis; MCA Annex D-1 is now indexed as a 193-page route atlas and backs the five atlas-trace segments. | Resolved into a default-visible, high-confidence atlas trace. No MCA inferred connectors or endpoint gaps remain. | Keep sheet provenance and construction-status evidence under periodic review. |

## Builder changes made in this pass

- Inferred connectors are no longer created between endpoints that already belong to the same source edge.
- Endpoints clustered to the same node are no longer connected with zero-length inferred connectors.
- Gap reporting is now component-aware, so valid branch networks are not penalized for having multiple terminal ends.
- Official-vector fragments use the stricter 2 km snap threshold; the 5 km threshold is reserved for medium-confidence manual/document traces.
- `udipur_damauli_bharatpur_220` now compares against the source-supported 64.45 km Udipur-Markichowk-Bharatpur route basis rather than the broader 85 km package assumption.
- `mca_central_400` now uses five MCA Annex D-1 atlas-trace segments and compares against the MCC Compact 308.65 route-km basis; the compact 617.3 km figure is treated as circuit-km accounting.
- `udipur_damauli_bharatpur_220` now uses a single NEA RAP trace in the public traced layer instead of the broken RPGCL overview fragments. Validation result: 0 connectors, 0 remaining gaps, and +1.34% length delta.
- `hetauda_bharatpur_bardaghat_220` now uses two public source-controlled segments instead of five over-selected RPGCL fragments. Validation result: 0 connectors, 0 remaining gaps, and -2.14% length delta against a 146.5 route-km basis.
- `hddi_400` now uses two World Bank RAP-controlled public segments instead of four oversimplified RPGCL overview fragments. Validation result: 0 connectors, 0 remaining gaps, and -1.22% length delta against the current 288 route-km basis.

## Active warning queue

No active corridor-level validation warnings remain after this pass.

## Product interpretation

The current map is publishable as a source-aware corridor map, not as a final engineering alignment map. The public layer should continue to show these major corridors because they are important to understanding Nepal's power system, but the popups and QA layers must keep telling readers where the line is source-traced, where it is inferred, and where the evidence still needs improvement.
