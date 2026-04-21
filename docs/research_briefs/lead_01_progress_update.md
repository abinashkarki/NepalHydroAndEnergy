# Lead 01 Progress Update

## What now exists

Lead 01 now has three working research assets:

1. [lead_01_seasonality_storage_trade.md](/Users/hi/projects/nepalEnergy/docs/research_briefs/lead_01_seasonality_storage_trade.md)
2. [nepal_basin_seasonality_baseline.csv](/Users/hi/projects/nepalEnergy/data/processed/tables/nepal_basin_seasonality_baseline.csv)
3. [nepal_storage_dry_energy_shortlist.csv](/Users/hi/projects/nepalEnergy/data/processed/tables/nepal_storage_dry_energy_shortlist.csv)

It also now has a real NEA daily-report ingestion pipeline:

- [build_nea_daily_trade_series.py](/Users/hi/projects/nepalEnergy/scripts/build_nea_daily_trade_series.py)
- [nea_daily_report_manifest.csv](/Users/hi/projects/nepalEnergy/data/processed/lead1_trade/nea_daily_report_manifest.csv)
- [nea_daily_trade_parsed.csv](/Users/hi/projects/nepalEnergy/data/processed/lead1_trade/nea_daily_trade_parsed.csv)
- [nea_daily_trade_monthly_aggregated.csv](/Users/hi/projects/nepalEnergy/data/processed/lead1_trade/nea_daily_trade_monthly_aggregated.csv)

Lead 01 also now has a reusable monthly-series builder and first-pass visuals:

- [build_lead1_trade_outputs.py](/Users/hi/projects/nepalEnergy/scripts/build_lead1_trade_outputs.py)
- [nea_trade_chart_monthly_long.csv](/Users/hi/projects/nepalEnergy/data/processed/lead1_trade/nea_trade_chart_monthly_long.csv)
- [lead1_monthly_import_export_storage_fy2081_82.csv](/Users/hi/projects/nepalEnergy/data/processed/lead1_trade/lead1_monthly_import_export_storage_fy2081_82.csv)
- [lead1_monthly_trade_3year.png](/Users/hi/projects/nepalEnergy/figures/lead1_monthly_trade_3year.png)
- [lead1_fy2081_82_trade_vs_storage.png](/Users/hi/projects/nepalEnergy/figures/lead1_fy2081_82_trade_vs_storage.png)

## What was verified in this pass

### Daily NEA report pipeline

The daily archive on the NEA transmission-directorate site is valid and machine-tractable.

- archive page works: `https://td.neasite.dryicesolutions.net/en/category/daily-operational-reports-1`
- detail pages expose direct PDF links under `/uploads/shares/Daily_op_reports/`
- the first-page PDF layout is parseable with `pdftotext -layout`

The parser has been validated well beyond the first proof-of-concept slice:

- page-1 slice: BS dates `2081/09/18` to `2081/09/27`, `10/10` parsed
- four-page backfill: BS dates `2081/08/18` to `2081/09/27`, `40/40` parsed
- older `R1` pages required two fixes:
  - PDF path fallback for `/uploads/shares/press_release/`
  - date parsing that accepts single-digit BS month/day

The archive depth is now known:

- `64` archive pages
- operational daily coverage from `2080-01-01` to `2081-09-27`
- this is strong enough for a serious operational series, but it does **not** fully cover FY `2079/80`

That means the NEA annual-report monthly trade chart remains necessary for the earliest months.

### Multi-year monthly trade shape

The NEA annual-report comparison chart has now been reshaped into a long-form monthly series and plotted.

Key read:

- exports are concentrated in `Shrawan` through `Kartik`, with a second spike in `Ashadh`
- imports surge from `Poush` through `Baishakh`
- the current-year export pattern in FY `2081/82` is stronger than FY `2079/80` and `2080/81` in early wet-season months
- the import season remains persistent across all three years, which supports the timing-and-storage hypothesis more strongly than a one-year anomaly would

### FY 2081/82 trade versus storage

The new panel chart makes the central imbalance visually obvious:

- wet-season exports are several hundred GWh per month
- dry-season imports rise to roughly `300-360 GWh` per month
- NEA storage generation stays tiny by comparison, mostly in the `5-50 GWh` range per month
- the currently parsed daily archive already tracks the `Poush` import spike closely enough to validate the monthly chart structure

This is the cleanest visual support so far for the claim that Nepal's problem is controlled timing rather than annual resource scarcity.

### Basin seasonality

The strongest official seasonality anchors now in hand are:

- Mahakali: about `73%` of runoff in the four monsoon months
- Karnali: `72%` monsoon runoff, `12%` post-monsoon, `7%` winter, `9%` pre-monsoon
- Gandaki: `74%` monsoon runoff, `12%` post-monsoon, `6%` winter, `8%` pre-monsoon
- Koshi: `67-78%` monsoon runoff, with Jan-Mar flows dropping to about one-tenth of August peak
- West Rapti: about `73.5%` of runoff in the four monsoon months and still a dry-season deficit basin

### Storage shortlist

The highest-value dry-season candidates now visible are:

- current system anchor: `Kulekhani I-III`
- practical near-term build: `Tanahu`
- strongest quantified dry-energy blocks: `Dudhkoshi Storage`, `Nalsyau Gad`, `Lower Badigad`, `Naumure`, `Sun Koshi No.3`

## Read on the argument right now

The structure is getting harder to evade:

- basin hydrology is monsoon-heavy almost everywhere
- Nepal's current storage contribution is tiny relative to system demand and dry-season imports
- the best storage candidates are not just large-MW projects; some are valuable because they contribute meaningful `dry energy`
- the NEA daily reports provide the missing operational bridge between hydrology and actual seasonal exchange with India, at least from `2080-01-01` onward

That means the main lead remains intact: Nepal's energy bottleneck still looks more like `timing + storage + system design` than `lack of annual hydropower resource`.

## Immediate next task

Finish the full daily parse and then rerun [build_lead1_trade_outputs.py](/Users/hi/projects/nepalEnergy/scripts/build_lead1_trade_outputs.py) so the figures and panel table reflect the full `2080-01-01` to `2081-09-27` operational archive.

In parallel, keep probing NEA monthly operational reports as a blocked-but-promising source:

- the `NMOR` PDF naming pattern is real enough to appear in search results
- direct fetches from this environment are currently blocked by the NEA site security layer
- if that barrier can be bypassed or sourced another way, the monthly reports could close the remaining FY `2079/80` gap

Then aggregate the cleaned daily series against:

- the annual-report monthly trade chart for FY `2079/80` to `2081/82`
- the FY `2024/25` monthly energy-balance table
- the basin seasonality table
- the storage dry-energy shortlist

That is the point where this stops being a research brief and becomes a tested chapter.
