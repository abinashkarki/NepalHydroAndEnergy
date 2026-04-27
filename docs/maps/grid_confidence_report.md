# Grid Confidence Report

Purpose: define the current product-quality state of the public grid map and the next source-quality cycle.

## Product rule

The map should optimize for faithful public understanding, not visual completeness. A line can be default-visible only when its status, voltage, endpoints, source basis, and geometry role are auditable. Bigger geometry gaps stay visible in QA instead of being closed with speculative linework.

## Current state

- Corridor dossiers: 12
- Cross-border dossiers: 10
- Corridor geometry grades: {'route-grade atlas trace': 1, 'route-grade RAP trace': 2, 'document-grounded corridor': 8, 'conceptual / not traced': 1}
- Cross-border status mix: {'Operational': 5, 'Under construction': 2, 'Implementation setup': 2, 'Planned': 1}
- Corridors with explicit QA warnings: 0

## Next-cycle focus

- Hold the default public layer to source-aware geometry, not visual completeness.
- Upgrade corridor dossiers before upgrading linework.
- Prioritize 400 kV backbone/export links, then 220 kV domestic corridors, then weak 132 kV evacuation corridors.
- Keep all inferred connectors visually distinct and leave larger gaps in QA.

## Priority corridor dossiers

| priority_rank | corridor_id | status | geometry_grade | source_quality_score | length_delta_pct | remaining_gap_count | public_decision |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | mca_central_400 | Under construction | route-grade atlas trace | 100 | -1.3 | 0 | default-visible, high confidence |
| 2 | hddi_400 | Partially operational | route-grade RAP trace | 93 | -1.2 | 0 | default-visible, caveated |
| 3 | hetauda_bharatpur_bardaghat_220 | Operational | document-grounded corridor | 100 | -2.1 | 0 | default-visible, caveated |
| 4 | udipur_damauli_bharatpur_220 | Under construction | route-grade RAP trace | 93 | 1.3 | 0 | default-visible, caveated |
| 5 | marsyangdi_upper_220 | Under construction | document-grounded corridor | 93 | -12.2 | 0 | default-visible, caveated |
| 6 | kabeli_132 | Under construction | document-grounded corridor | 89 | 12.4 | 0 | default-visible, caveated |
| 7 | solu_tingla_mirchaiya_132 | Operational | document-grounded corridor | 68 | -12.4 | 0 | default-visible with explicit QA warning |
| 8 | western_132_backbone | Operational | document-grounded corridor | 100 | 3.3 | 0 | default-visible, caveated |
| 9 | chameliya_attariya_132 | Operational | document-grounded corridor | 100 | -1.1 | 0 | default-visible, caveated |
| 10 | kohalpur_surkhet_dailekh_132 | Under construction | document-grounded corridor | 100 | -9.3 | 0 | default-visible, caveated |

## Cross-border dossiers

| interconnection_id | status | connection_scope | endpoint_quality | source_id | public_decision |
| --- | --- | --- | --- | --- | --- |
| dhalkebar_muzaffarpur | Operational | endpoint_connector | defensible endpoint connector | pib_lok_sabha_2026_04_02 | default-visible, operational endpoint connector |
| kataiya_kushaha | Operational | gateway_stub | gateway stub only | pib_lok_sabha_2026_04_02 | default-visible, operational point plus conservative stub |
| raxaul_parwanipur | Operational | gateway_stub | gateway stub only | pib_lok_sabha_2026_04_02 | default-visible, operational point plus conservative stub |
| nautanwa_mainahiya | Operational | endpoint_connector | defensible endpoint connector | pib_lok_sabha_2026_04_02 | default-visible, operational endpoint connector |
| tanakpur_mahendranagar | Operational | gateway_stub | gateway stub only | pib_lok_sabha_2026_04_02 | default-visible, operational point plus conservative stub |
| nepalgunj_nanpara | Under construction | gateway_stub | gateway stub only | pib_lok_sabha_2026_04_02 | default-visible, non-operational dashed/faint |
| gorakhpur_new_butwal | Under construction | gateway_stub | gateway stub only | mcc_fy2025_annual_report | default-visible, non-operational dashed/faint |
| inaruwa_purnea | Implementation setup | endpoint_connector | defensible endpoint connector | cea_nep_volume_ii | default-visible, non-operational dashed/faint |
| lamki_bareilly | Implementation setup | endpoint_connector | defensible endpoint connector | cea_nep_volume_ii | default-visible, non-operational dashed/faint |
| chameliya_jauljibi | Planned | endpoint_connector | defensible endpoint connector | cea_nep_volume_ii | default-visible, non-operational dashed/faint |

## QA warnings to work down

No corridor-level QA warnings.

## Source checks for this cycle

| source_id | title | url | use |
| --- | --- | --- | --- |
| mcc_nepal_compact | MCC Nepal Compact | https://assets.mcc.gov/content/uploads/compact-nepal.pdf | Authoritative topology and component-length basis for the five MCA 400 kV transmission segments. |
| mcc_fy2025_annual_report | MCC Fiscal Year 2025 Annual Report | https://www.mcc.gov/resources/doc/annual-report-2025/ | Current implementation status and program-length context. |
| pib_lok_sabha_2026_04_02 | Government of India PIB Lok Sabha reply, April 2 2026 | https://www.pib.gov.in/PressReleseDetailm.aspx?PRID=2248339&lang=1&reg=3 | Official current list of Nepal-India cross-border transmission links. |
| cea_nep_volume_ii | CEA National Electricity Plan Volume II: Transmission | https://cea.nic.in/wp-content/uploads/notification/2024/10/National_Electricity_Plan_Volume_II_Transmission.pdf | India-side planning context for future and implementation-stage interconnections. |

## Stop rule

This phase is publishable when every default-visible major corridor has an auditable source basis, no planned or implementation-stage line renders as operational, inferred connectors remain visually distinct, and all remaining geometry gaps are documented in the QA layer rather than silently bridged.
