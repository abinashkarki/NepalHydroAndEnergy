# Lead 01 Research Brief: Seasonality, Storage, and Trade

## Purpose

This brief turns the first lead into a disciplined research program:

- explain Nepal's wet-season electricity surplus and dry-season deficit as a timing problem, not just a generation problem
- connect basin hydrology to actual monthly system behavior
- test whether storage is the main missing bridge between hydrology and value capture
- define the exact datasets, charts, and reconciliation steps needed before this becomes essay-grade

This is not the final essay. It is the operating brief for the next research pass.

## Main question

How much of Nepal's electricity instability and cross-border trade pattern is driven by seasonal river flow and weak storage, rather than by lack of total annual generation?

## Thesis tests

These are the claims the research now needs to prove or kill.

1. Nepal's core energy bottleneck is timing, regulation, and storage, not raw annual water volume.
2. Nepal exports low-value wet-season electricity and imports higher-value dry-season electricity because the system cannot shift water and power across seasons.
3. A small number of storage and dispatch upgrades would reduce dry-season dependence more effectively than adding more monsoon-heavy run-of-river capacity.
4. The trade story cannot be understood from annual totals alone; it must be read month by month.

## What the current evidence already says

### 1. Hydrology is strongly seasonal

- A DHM-linked flood analysis finds roughly `70-80%` of annual river flow occurs during the monsoon.
- The same evidence base shows extreme flows in the Karnali, Narayani, and Koshi outlets are overwhelmingly concentrated from mid-June to early September.
- Nepal's hydropower problem therefore has to be analyzed against time, not just annual averages.

### 2. Dry-season generation weakness is already acknowledged in official hydropower studies

- The WECS `Hydropower Potential of Nepal (2019)` study states that because Nepal relies overwhelmingly on run-of-river and peaking run-of-river plants, hydropower production falls to about `one-third of installed capacity during the dry flow season`.
- The same report says Kulekhani is the country's only reservoir-type hydropower plant in operation.

### 3. The NEA monthly balance table shows a clear seasonal trade pattern

Using the FY `2081/82 (2024/25)` energy-balance table in the NEA annual report:

- official exports in the table total `2,380 GWh`
- official imports in the table total `1,712 GWh`
- official NEA storage generation totals only `280 GWh`
- official monthly system energy demand totals `16,447 GWh`
- official monthly national energy demand totals `14,067 GWh`

The pattern is clear even before deeper modeling:

- about `90%` of reported import energy occurs from `Poush` through `Baishakh`
- about `94%` of reported export energy occurs in `Shrawan`, `Bhadra`, `Ashwin`, `Kartik`, and `Ashadh`
- NEA storage generation is only about `1.7%` of annual system energy demand
- NEA storage generation is only about `16.4%` of annual reported import energy

That is the current structural read: Nepal is not short of hydropower in the abstract. It is short of controlled timing.

### 4. The source stack already reveals a reconciliation problem

The NEA annual report contains multiple trade summaries that do not line up perfectly:

- narrative summary: `1,681 GWh` imports, `2,380 GWh` exports
- monthly energy-balance table: `1,712 GWh` imports, `2,380 GWh` exports
- trade comparison chart: `1,711.5272 GWh` imports, `2,331.7360 GWh` exports

This is not a reason to stop. It is a reason to separate source functions:

- use the monthly energy-balance table for system-shape analysis
- use the trade comparison chart for multi-year monthly trade comparison
- use daily or monthly operational reports to build the authoritative time series for publication-grade charts

## Exact questions to answer next

1. What is the cleanest basin-by-basin measure of monsoon concentration for Nepal's major river systems?
2. How much does domestic generation fall from the wet season into the dry season in the actual NEA system balance?
3. How much of the dry-season gap is currently covered by imports versus storage generation?
4. What share of Nepal's reported electricity trade is simply seasonal swapping rather than durable surplus?
5. Does the import season line up more closely with hydrological low flow, with demand peaks, or with both?
6. What is the minimum storage addition needed to materially reduce dry-season imports?
7. Which storage projects have the strongest dry-energy contribution, not just large MW headline capacity?
8. Is the limiting factor after storage mostly transmission, market access, or domestic demand absorption?

## Definitions to lock before further analysis

- `Monsoon concentration`: share of annual runoff or discharge occurring in the monsoon months; basin source must be stated.
- `Dry season`: for power-system analysis, use the NEA fiscal months where imports surge, not only the meteorological label.
- `Storage generation`: the `NEA STORAGE` row in the annual system table, currently dominated by the Kulekhani system.
- `System demand` vs `national demand`: use NEA labels exactly until the report's accounting distinction is traced.
- `Trade value gap`: the mismatch between wet-season export timing and dry-season import timing, plus price if recoverable.

## Required datasets

### Dataset A: Basin seasonality baseline

Use for hydrology framing.

- `National Water Plan` runoff baselines for major river systems
- `WECS River Basin Plan, Hydropower Development Master Plan and Strategic Environmental and Social Assessment (2024)` for basin monthly runoff, demand, and planning scenarios
- DHM/peer-reviewed basin studies for monsoon shares and seasonal variability

Minimum fields:

- basin
- mean annual runoff or discharge
- monsoon share
- dry-season share
- source type classification
- source year or study period

### Dataset B: Historical station series

Use for stronger basin claims and later visual overlays.

- DHM hydrological data service
- DHM station inventory
- DHM real-time streamflow and river-watch pages for station references

Minimum fields:

- station ID
- river
- basin
- latitude / longitude
- daily discharge
- daily water level
- record coverage

Status:

- not openly packaged in full
- must be requested from DHM for serious long-series work

### Dataset C: NEA monthly system energy balance

Use for monthly system-shape analysis.

Source:

- FY `2024/25` annual report table, already extracted into a local CSV

Fields:

- month
- IPP energy
- NEA subsidiary energy
- NEA ROR/PROR energy
- import energy
- storage energy
- solar
- interruption
- system demand
- export
- national demand

### Dataset D: NEA monthly capacity balance

Use for monthly peak and import-capacity dependence.

Fields:

- month
- import MW
- storage MW
- national peak demand
- system peak demand
- export MW

### Dataset E: Multi-year monthly cross-border trade

Use for 3-year trend analysis.

Sources:

- NEA annual report trade comparison charts
- NEA yearly summary reports
- NEA monthly operational reports
- NEA daily operational reports
- CERC monthly market-monitoring reports
- CEA cross-border approval records

Fields:

- fiscal year
- month
- import GWh
- export GWh
- source
- accounting note

### Dataset F: Storage asset and candidate project pack

Use for the "what would actually fix this?" section.

Sources:

- NEA annual report
- JICA / NEA `Nationwide Master Plan Study on Storage-type Hydroelectric Power Development in Nepal`
- DoED live license rosters

Minimum fields:

- project
- basin
- installed MW
- total storage
- effective storage
- annual energy
- dry energy
- status

## Dataset hierarchy

Use the sources in this order.

1. `NEA daily operational reports` for publication-grade trade chronology.
2. `NEA monthly operational reports` when daily files are incomplete.
3. `NEA annual report monthly tables` for clean top-level monthly structure.
4. `WECS river-basin and hydropower studies` for system interpretation and basin context.
5. `DHM` for station truth where historical series can be obtained.
6. `CERC` and `CEA` for India-side cross-checks on trade and approvals.

## Priority charts

1. Monthly stacked energy balance for FY `2024/25`
2. Monthly imports vs exports vs storage generation
3. Monthly import MW vs storage MW vs national peak demand
4. Basin seasonality comparison for Koshi, Gandaki, Karnali, Mahakali, and medium rivers
5. Dry-season deficit panel: domestic generation, imports, storage, and demand
6. Storage-candidate comparison by `dry energy`, not just MW
7. Three-year monthly trade heatmap from FY `2079/80` to `2081/82`
8. Timeline of trade-regime changes: PTA, Indian approvals, Dhalkebar-Muzaffarpur export events, Bangladesh export event

## Recommended work split

### Workstream A: Hydrology

- build the basin seasonality table
- identify which basins are most stable in the dry season
- note where public DHM data is insufficient and requires request

### Workstream B: System balance

- standardize the NEA monthly energy and capacity tables
- scrape NEA daily or monthly reports into one trade series
- reconcile trade totals across report tables

### Workstream C: Storage

- build a shortlist of storage projects ranked by dry-energy contribution
- separate large-MW headlines from genuinely useful seasonal regulation value

### Workstream D: Synthesis

- test whether storage alone explains the gap or whether grid and trade access still dominate
- produce the claim set for the final essay

## Known issues that must be preserved

1. NEA trade totals differ across the narrative, monthly balance table, and comparison chart.
2. Some report tables are internally inconsistent at the one- or two-unit level after text extraction, so the rendered PDF page remains the final reference.
3. DHM long discharge series are not openly bundled and require formal request.
4. Plant-level dry-season generation and curtailment remain weakly public.

## Deliverables for the next pass

1. One cleaned monthly trade table built from NEA daily or monthly reports for at least FY `2079/80` to `2081/82`
2. One basin seasonality table with source quality labels
3. One ranked storage-project shortlist using dry-energy contribution
4. One short synthesis memo answering whether Nepal's real bottleneck is storage-timing or something else

## Local files created for this brief

- [lead_01_seasonality_storage_trade.md](/Users/hi/projects/nepalEnergy/docs/research_briefs/lead_01_seasonality_storage_trade.md)
- [nea_monthly_energy_balance_fy2024_2025.csv](/Users/hi/projects/nepalEnergy/data/processed/tables/nea_monthly_energy_balance_fy2024_2025.csv)
- [nea_monthly_capacity_balance_fy2024_2025.csv](/Users/hi/projects/nepalEnergy/data/processed/tables/nea_monthly_capacity_balance_fy2024_2025.csv)
- [nea_cross_border_trade_monthly_gwh_fy2079_80_to_2081_82.csv](/Users/hi/projects/nepalEnergy/data/processed/tables/nea_cross_border_trade_monthly_gwh_fy2079_80_to_2081_82.csv)

## High-value sources

- NEA annual report FY `2024/25` local copy: [nea_annual_report_2024_2025.pdf](/Users/hi/projects/nepalEnergy/data/raw/projects_storage/nea_annual_report_2024_2025.pdf)
- WECS hydropower potential local copy: [wecs_hydropower_potential_2019.pdf](/Users/hi/projects/nepalEnergy/data/raw/projects_storage/wecs_hydropower_potential_2019.pdf)
- WECS River Basin Plan local copy: [wecs_river_basin_plan_2024.pdf](/Users/hi/projects/nepalEnergy/data/raw/lead1_sources/wecs_river_basin_plan_2024.pdf)
- JICA storage master plan volume 1 local copy: [jica_storage_master_plan_vol_1.pdf](/Users/hi/projects/nepalEnergy/data/raw/lead1_sources/jica_storage_master_plan_vol_1.pdf)
- JICA storage master plan volume 2 local copy: [jica_storage_master_plan_vol_2.pdf](/Users/hi/projects/nepalEnergy/data/raw/lead1_sources/jica_storage_master_plan_vol_2.pdf)
- DHM hydrological data request form local copy: [dhm_hydrological_data_request_form.pdf](/Users/hi/projects/nepalEnergy/data/raw/lead1_sources/dhm_hydrological_data_request_form.pdf)
- DHM data service: [dhm.gov.np/data-service](https://www.dhm.gov.np/data-service)
- DHM hydrological network page: [dhm.gov.np/hydology/hydrological-data-network](https://dhm.gov.np/hydology/hydrological-data-network)
- DHM real-time streamflow: [dhm.gov.np/hydrology/realtime-stream](https://dhm.gov.np/hydrology/realtime-stream)
- NEA reports page: [nea.org.np/index.php/report](https://www.nea.org.np/index.php/report)
- NEA daily report archive: [td.neasite.dryicesolutions.net daily operational reports](https://td.neasite.dryicesolutions.net/en/category/daily-operational-reports-1)
- WECS Energy Sector Synopsis 2024: [wecs.gov.np energy sector synopsis 2024](https://wecs.gov.np/content/56/energy-sector-synopsis-report-2024--fy-2079-80-/)
- WECS River Basin Planning DSS: [dss.wecs.gov.np](https://dss.wecs.gov.np)
- MoEWRI power trade agreement page: [moewri.gov.np power trade agreement](https://moewri.gov.np/content/72/agreement-nepal-india-on-electric-power-trade-cross-border-transmission-interconnection-and-grid-connectivity-2014/)
- CEA cross-border electricity approvals: [cea.nic.in import-export cross-border electricity](https://cea.nic.in/import-export-cross-border-of-electricity/?lang=en)
- CERC monthly short-term market reports: [cercind.gov.in market monitoring reports](https://cercind.gov.in/report_MM.html)
