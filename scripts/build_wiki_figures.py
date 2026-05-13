#!/usr/bin/env python3
from __future__ import annotations

import csv
import datetime as dt
import json
import os
import re
import shutil
from pathlib import Path

os.environ.setdefault("MPLBACKEND", "Agg")
os.environ.setdefault("MPLCONFIGDIR", "/private/tmp/nepal-energy-matplotlib")

import matplotlib.pyplot as plt

from chart_style import PALETTE, apply_chart_style, save_svg


ROOT = Path(os.environ.get("NEPAL_ENERGY_ROOT", Path(__file__).resolve().parent.parent))
FIGURE_DIR = ROOT / "wiki" / "assets" / "figures"
MANIFEST_PATH = ROOT / "wiki" / "explorer" / "shared" / "wiki-figure-manifest.json"
FIGURE_INDEX_PAGE = ROOT / "wiki" / "pages" / "data" / "figure-index.md"
TODAY = dt.date.today().isoformat()
LEGACY_FIGURE_DIR = ROOT / "figures"

MONTHS = [
    "Shrawan",
    "Bhadra",
    "Ashwin",
    "Kartik",
    "Mangsir",
    "Poush",
    "Magh",
    "Falgun",
    "Chaitra",
    "Baishakh",
    "Jestha",
    "Ashadh",
]
MONTH_LABELS = ["Shr", "Bhd", "Ash", "Kar", "Man", "Pou", "Mag", "Fal", "Cha", "Bai", "Jes", "Asa"]
TRADE_MONTH_COLUMNS = {
    "Shrawan": "Shrawan",
    "Bhadra": "Bhadra",
    "Ashwin": "Ashwin",
    "Kartik": "Kartik",
    "Mangsir": "Mangshir",
    "Poush": "Poush",
    "Magh": "Magh",
    "Falgun": "Falgun",
    "Chaitra": "Chaitra",
    "Baishakh": "Baishakh",
    "Jestha": "Jestha",
    "Ashadh": "Ashadh",
}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def figure_rel_path(figure_id: str, suffix: str = "svg") -> str:
    return f"../assets/figures/{figure_id}.{suffix}"


def parse_percent_metric(raw: str) -> tuple[float | None, str]:
    if not raw or raw == "NA":
        return None, ""
    range_match = re.search(r"(\d+(?:\.\d+)?)\s*-\s*(\d+(?:\.\d+)?)\s*%", raw)
    if range_match:
        low = float(range_match.group(1))
        high = float(range_match.group(2))
        return (low + high) / 2, f"{low:g}-{high:g}%"
    match = re.search(r"(\d+(?:\.\d+)?)\s*%", raw)
    if match:
        value = float(match.group(1))
        return value, f"{value:g}%"
    return None, ""


def build_monthly_trade_3y() -> dict:
    figure_id = "monthly_trade_3y"
    source = ROOT / "data" / "processed" / "tables" / "nea_cross_border_trade_monthly_gwh_fy2079_80_to_2081_82.csv"
    rows = read_csv(source)
    years = ["2079_80", "2080_81", "2081_82"]
    year_labels = {"2079_80": "FY 2079/80", "2080_81": "FY 2080/81", "2081_82": "FY 2081/82"}
    colors = {
        "2079_80": PALETTE["blue"],
        "2080_81": PALETTE["yellow"],
        "2081_82": PALETTE["green"],
    }

    fig, ax = plt.subplots(figsize=(8.4, 4.7))
    for year in years:
        export_row = next(r for r in rows if r["fiscal_year"] == year and r["flow_direction"] == "EXPORT_GWh")
        import_row = next(r for r in rows if r["fiscal_year"] == year and r["flow_direction"] == "IMPORT_GWh")
        net = [
            float(export_row[TRADE_MONTH_COLUMNS[month]]) - float(import_row[TRADE_MONTH_COLUMNS[month]])
            for month in MONTHS
        ]
        ax.plot(MONTH_LABELS, net, marker="o", linewidth=2.2, markersize=4.5, color=colors[year], label=year_labels[year])
    ax.axhline(0, color=PALETTE["ink"], linewidth=1)
    ax.axvspan(3.5, 9.5, color="#efe1c4", alpha=0.38, zorder=0)
    ax.text(6.5, 410, "dry import season", ha="center", fontsize=8.5, color=PALETTE["muted"], style="italic")
    ax.text(0.2, 470, "net export", ha="left", fontsize=8.5, color=PALETTE["green"])
    ax.text(0.2, -430, "net import", ha="left", fontsize=8.5, color=PALETTE["red"])
    ax.set_ylim(-480, 560)
    ax.set_ylabel("Net export, GWh")
    ax.set_xlabel("Nepali fiscal month")
    ax.set_title("Nepal's cross-border trade flips with the season", loc="left", fontsize=13, pad=12)
    ax.grid(axis="y", alpha=0.42)
    ax.grid(axis="x", visible=False)
    ax.legend(ncol=3, loc="lower center", bbox_to_anchor=(0.5, -0.26), fontsize=9, frameon=False)
    ax.tick_params(axis="both", labelsize=9)
    fig.subplots_adjust(left=0.10, right=0.98, top=0.86, bottom=0.29)
    save_svg(
        fig,
        FIGURE_DIR / f"{figure_id}.svg",
        figure_id=figure_id,
        source_note="NEA annual-report trade comparison",
        caveat="comparison-chart totals differ from narrative totals",
        generated_date=TODAY,
    )
    return {
        "figure_id": figure_id,
        "title": "Monthly cross-border trade, FY 2079/80 to 2081/82",
        "path": figure_rel_path(figure_id),
        "source_files": [rel(source)],
        "source_slugs": ["nea-annual-report-fy2024-25"],
        "target_pages": ["data-trade-time-series"],
        "caption": "Three-year monthly net-trade seasonality from NEA annual-report trade comparison tables.",
        "caveat": "Annual-report comparison chart totals differ slightly from NEA narrative totals.",
        "license": "CC-BY 4.0",
        "generator_script": "scripts/build_wiki_figures.py",
        "last_generated": TODAY,
    }


def build_fleet_capacity_mix() -> dict:
    figure_id = "fleet_capacity_mix"
    source_page = ROOT / "wiki" / "pages" / "data" / "data-fleet-composition.md"
    capacity_labels = ["RoR", "PRoR", "Storage", "Other / rounding"]
    capacity_values = [85.7, 9.9, 3.7, max(0.0, 100 - 85.7 - 9.9 - 3.7)]
    seasonal_labels = ["Dry season\n(Poush–Ashadh)", "Wet season\n(Shrawan–Mangsir)"]
    seasonal_values = [2437, 6533]
    stack_colors = [PALETTE["blue"], PALETTE["cyan"], PALETTE["green"], PALETTE["gray"]]

    fig, axes = plt.subplots(1, 2, figsize=(8.2, 4.6),
                             gridspec_kw={"width_ratios": [1.2, 1], "wspace": 0.38})

    # ── left: stacked horizontal bar ─────────────────────────────────────────
    left = 0.0
    for label, value, color in zip(capacity_labels, capacity_values, stack_colors):
        axes[0].barh([0], [value], left=left, height=0.52, color=color, label=label, linewidth=0)
        if value >= 4:
            axes[0].text(left + value / 2, 0, f"{value:g}%",
                         ha="center", va="center", fontsize=9.5,
                         color="white" if color != PALETTE["cyan"] else PALETTE["ink"])
        left += value
    axes[0].set_xlim(0, 100)
    axes[0].set_ylim(-0.55, 0.55)
    # no y-tick label — the bar is the only category; title explains it
    axes[0].set_yticks([])
    axes[0].set_xlabel("Share of installed hydro capacity (%)", labelpad=9)
    axes[0].set_title("Installed MW are mostly RoR / PRoR", loc="left", fontsize=10.5, pad=12)
    axes[0].legend(
        loc="upper center",
        bbox_to_anchor=(0.5, -0.22),
        ncol=2,
        fontsize=9,
        columnspacing=1.2,
        handletextpad=0.5,
        borderaxespad=0,
        frameon=False,
    )
    axes[0].grid(axis="x", alpha=0.35)
    axes[0].grid(axis="y", visible=False)
    axes[0].spines["left"].set_visible(False)

    # ── right: seasonal generation bar ───────────────────────────────────────
    bars = axes[1].bar(seasonal_labels, seasonal_values,
                       color=[PALETTE["red"], PALETTE["green"]], width=0.58)
    axes[1].set_title("Generation is wet-season weighted", loc="left", fontsize=10.5, pad=12)
    axes[1].set_ylabel("Hydro generation (GWh)", labelpad=8)
    axes[1].grid(axis="y", alpha=0.35)
    axes[1].grid(axis="x", visible=False)
    axes[1].margins(x=0.18)
    ymax = max(seasonal_values) * 1.22
    axes[1].set_ylim(0, ymax)
    for bar, value in zip(bars, seasonal_values):
        axes[1].text(bar.get_x() + bar.get_width() / 2,
                     value + ymax * 0.015, f"{value:,}",
                     ha="center", va="bottom", fontsize=9.5)
    axes[1].text(0.5, 0.50,
                 "2.68× wet / dry ratio",
                 ha="center", fontsize=10.5, fontweight="bold",
                 color=PALETTE["ink"], transform=axes[1].transAxes)
    axes[1].tick_params(axis="x", labelsize=9)

    fig.suptitle("Hydro Capacity Is Not The Same As Dry-Season Firmness",
                 fontsize=12.5, fontweight="bold")
    fig.subplots_adjust(left=0.08, right=0.98, top=0.86, bottom=0.31, wspace=0.42)
    save_svg(
        fig,
        FIGURE_DIR / f"{figure_id}.svg",
        figure_id=figure_id,
        source_note="NEA review summarized in data-fleet-composition",
        caveat="taxonomy varies; seasonal split is single-year",
        generated_date=TODAY,
    )
    return {
        "figure_id": figure_id,
        "title": "Hydropower fleet capacity mix and seasonal generation split",
        "path": figure_rel_path(figure_id),
        "source_files": [rel(source_page)],
        "source_slugs": ["nea-annual-report-fy2024-25", "wecs-energy-synopsis-2024"],
        "target_pages": ["data-fleet-composition"],
        "caption": "Installed hydropower is dominated by RoR/PRoR, while annual generation remains strongly wet-season weighted.",
        "caveat": "Fleet taxonomy varies by reporting source; FY 2022/23 seasonal split is single-year.",
        "license": "CC-BY 4.0",
        "generator_script": "scripts/build_wiki_figures.py",
        "last_generated": TODAY,
    }


def build_basin_seasonality_compare() -> dict:
    figure_id = "basin_seasonality_compare"
    source = ROOT / "data" / "processed" / "tables" / "nepal_basin_seasonality_baseline.csv"
    rows = []
    for row in read_csv(source):
        value, label = parse_percent_metric(row.get("monsoon_metric", ""))
        if value is None:
            continue
        rows.append(
            {
                "basin": row["basin"],
                "value": value,
                "label": label,
                "type": row["basin_type"],
            }
        )
    rows.sort(key=lambda item: item["value"])

    n = len(rows)
    fig, ax = plt.subplots(figsize=(8.2, 4.9))
    colors = [PALETTE["blue"] if "major" in row["type"] else PALETTE["yellow"] for row in rows]
    bars = ax.barh([row["basin"] for row in rows], [row["value"] for row in rows],
                   color=colors, height=0.62)
    ax.axvline(70, color=PALETTE["red"], linewidth=1.3, linestyle="--", alpha=0.85, zorder=0)
    ax.text(70.8, n - 0.55, "70% reference",
            ha="left", va="top", fontsize=8.5, color=PALETTE["red"])
    ax.set_xlim(0, 90)
    ax.set_xlabel("Monsoon share of annual metric (%)", labelpad=8)
    ax.set_title(
        "Checked basins concentrate roughly 70-80% of water in monsoon",
        loc="left", fontsize=12, pad=12,
    )
    ax.tick_params(axis="both", labelsize=9)
    ax.grid(axis="x", alpha=0.35)
    ax.grid(axis="y", visible=False)
    ax.margins(y=0.04)
    for bar, row in zip(bars, rows):
        ax.text(row["value"] + 1.0, bar.get_y() + bar.get_height() / 2,
                row["label"], ha="left", va="center", fontsize=8.2)

    fig.subplots_adjust(left=0.18, right=0.98, top=0.86, bottom=0.19)
    save_svg(
        fig,
        FIGURE_DIR / f"{figure_id}.svg",
        figure_id=figure_id,
        source_note="WECS basin-plan extracts",
        caveat="metrics mix runoff, flow, and rainfall",
        generated_date=TODAY,
    )
    return {
        "figure_id": figure_id,
        "title": "Basin monsoon concentration comparison",
        "path": figure_rel_path(figure_id),
        "source_files": [rel(source)],
        "source_slugs": ["wecs-river-basin-plan-2024", "national-water-plan-nepal"],
        "target_pages": ["data-basin-discharge"],
        "caption": "Basin-level monsoon concentration from the checked public source stack.",
        "caveat": "Metrics mix runoff, surface flow, and rainfall depending on available public source.",
        "license": "CC-BY 4.0",
        "generator_script": "scripts/build_wiki_figures.py",
        "last_generated": TODAY,
    }


def build_storage_gap() -> dict:
    figure_id = "storage_gap"
    source = ROOT / "data" / "processed" / "tables" / "nepal_storage_dry_energy_shortlist.csv"
    labels = ["Operating\nstorage hydro", "2032 BAU\nstorage need", "2032 high-\ndemand need"]
    values = [106, 1993, 3154]
    colors = [PALETTE["green"], PALETTE["yellow"], PALETTE["red"]]

    fig, ax = plt.subplots(figsize=(8.0, 4.8))
    bars = ax.bar(labels, values, color=colors, width=0.58)
    ax.set_title("Nepal's Storage Gap Is Structural, Not Marginal", loc="left", fontsize=12.5, pad=12)
    ax.set_ylabel("MW")
    ax.set_ylim(0, 3600)
    ax.grid(axis="y", alpha=0.35)
    ax.grid(axis="x", visible=False)
    for bar, value in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width() / 2, value + 65, f"{value:,} MW",
                ha="center", va="bottom", fontsize=9.5, fontweight="bold")
    ax.text(
        0.02,
        0.72,
        "Current operating storage\nis Kulekhani I-III",
        transform=ax.transAxes,
        fontsize=9,
        color=PALETTE["muted"],
    )
    fig.subplots_adjust(left=0.10, right=0.98, top=0.84, bottom=0.23)
    save_svg(
        fig,
        FIGURE_DIR / f"{figure_id}.svg",
        figure_id=figure_id,
        source_note="WB/JICA figures summarized in storage data page",
        caveat="storage need is planning estimate, not project list",
        generated_date=TODAY,
    )
    return {
        "figure_id": figure_id,
        "title": "Current storage capacity versus JICA-estimated storage need",
        "path": figure_rel_path(figure_id),
        "source_files": [rel(source), "wiki/pages/data/data-storage-comparison.md"],
        "source_slugs": ["wb-water-sector-diagnostic", "jica-ipsdp-main-report-vol2"],
        "target_pages": ["data-storage-comparison"],
        "caption": "Nepal's current operational storage hydro is tiny relative to the 2032 storage need cited in planning literature.",
        "caveat": "JICA storage-need estimates are electricity-system planning needs; current storage uses Kulekhani operational capacity.",
        "license": "CC-BY 4.0",
        "generator_script": "scripts/build_wiki_figures.py",
        "last_generated": TODAY,
    }


def build_electricity_trade_shift() -> dict:
    figure_id = "electricity_trade_shift"
    source = ROOT / "wiki" / "pages" / "data" / "data-trade-time-series.md"
    years = ["2018", "FY 2024/25"]
    imports = [2582, 1681]
    exports = [3, 2380]
    x = list(range(len(years)))
    width = 0.34

    fig, ax = plt.subplots(figsize=(8.0, 4.8))
    ax.bar([i - width / 2 for i in x], imports, width=width, color=PALETTE["red"], label="Imports")
    ax.bar([i + width / 2 for i in x], exports, width=width, color=PALETTE["green"], label="Exports")
    for idx, value in enumerate(imports):
        ax.text(idx - width / 2, value + 55, f"{value:,}", ha="center", va="bottom", fontsize=9.5)
    for idx, value in enumerate(exports):
        ax.text(idx + width / 2, value + 55, f"{value:,}", ha="center", va="bottom", fontsize=9.5)
    ax.set_xticks(x, years)
    ax.set_ylabel("GWh")
    ax.set_ylim(0, 2850)
    ax.set_title("Annual Trade Shifted, But Seasonality Still Matters", loc="left", fontsize=12.5, pad=12)
    ax.legend(ncol=2, loc="upper center", bbox_to_anchor=(0.5, -0.14), fontsize=9, frameon=False)
    ax.grid(axis="y", alpha=0.35)
    ax.grid(axis="x", visible=False)
    fig.subplots_adjust(left=0.10, right=0.98, top=0.84, bottom=0.25)
    save_svg(
        fig,
        FIGURE_DIR / f"{figure_id}.svg",
        figure_id=figure_id,
        source_note="WB 2018 and NEA FY2024/25 annual totals",
        caveat="annual totals hide monthly dry-season imports",
        generated_date=TODAY,
    )
    return {
        "figure_id": figure_id,
        "title": "Electricity trade shift from net import to seasonal export",
        "path": figure_rel_path(figure_id),
        "source_files": [rel(source)],
        "source_slugs": ["wb-country-economic-memo-2025", "nea-annual-report-fy2024-25"],
        "target_pages": ["data-trade-time-series"],
        "caption": "Annual trade volumes show Nepal's transition from heavy importer to seasonal exporter.",
        "caveat": "Annual totals hide the wet-export and dry-import monthly structure shown in monthly_trade_3y.",
        "license": "CC-BY 4.0",
        "generator_script": "scripts/build_wiki_figures.py",
        "last_generated": TODAY,
    }


def build_lead1_trade_vs_storage() -> dict:
    figure_id = "lead1_fy2081_82_trade_vs_storage"
    source = ROOT / "data" / "processed" / "lead1_trade" / "lead1_monthly_import_export_storage_fy2081_82.csv"
    rows = read_csv(source)
    months = [MONTH_LABELS[int(row["fiscal_month_order"]) - 1] for row in rows]
    imports = [float(row["import_gwh_trade_chart"]) for row in rows]
    exports = [float(row["export_gwh_trade_chart"]) for row in rows]
    storage = [float(row["storage_gwh_energy_balance"]) for row in rows]

    fig, ax = plt.subplots(figsize=(8.6, 4.8))
    ax.axvspan(4.5, 10.5, color="#efe1c4", alpha=0.38, zorder=0)
    ax.bar(months, imports, color=PALETTE["red"], alpha=0.75, label="Import")
    ax.bar(months, exports, color=PALETTE["green"], alpha=0.75, label="Export")
    ax.plot(months, storage, color=PALETTE["blue"], marker="o", linewidth=2.1, label="Storage generation")
    ax.set_title("FY 2081/82 Trade Swings More Than Storage Output", loc="left", fontsize=12.5, pad=12)
    ax.set_ylabel("GWh")
    ax.grid(axis="y", alpha=0.35)
    ax.grid(axis="x", visible=False)
    ax.legend(ncol=3, loc="upper center", bbox_to_anchor=(0.5, -0.16), fontsize=9, frameon=False)
    ax.tick_params(axis="x", labelsize=9)
    fig.subplots_adjust(left=0.09, right=0.98, top=0.84, bottom=0.26)
    save_svg(
        fig,
        FIGURE_DIR / f"{figure_id}.svg",
        figure_id=figure_id,
        source_note="NEA FY2081/82 trade and energy balance tables",
        caveat="daily-report points excluded from compact wiki figure",
        generated_date=TODAY,
    )
    return {
        "figure_id": figure_id,
        "title": "FY 2081/82 trade versus storage generation",
        "path": figure_rel_path(figure_id),
        "source_files": [rel(source)],
        "source_slugs": ["nea-annual-report-fy2024-25"],
        "target_pages": ["data-trade-time-series"],
        "caption": "Imports, exports, and storage generation in the same FY 2081/82 monthly frame.",
        "caveat": "Compact wiki figure excludes daily-report parsed points; see the lead-1 table for daily subset coverage.",
        "license": "CC-BY 4.0",
        "generator_script": "scripts/build_wiki_figures.py",
        "last_generated": TODAY,
    }


def build_license_type_mix() -> dict:
    figure_id = "license_type_mix"
    source = ROOT / "data" / "processed" / "naxa_hydropower_projects.csv"
    rows = read_csv(source)
    counts: dict[str, int] = {}
    capacity: dict[str, float] = {}
    for row in rows:
        license_type = row["license_type"].strip() or "Unknown"
        counts[license_type] = counts.get(license_type, 0) + 1
        capacity[license_type] = capacity.get(license_type, 0.0) + float(row["capacity"] or 0)
    order = sorted(counts, key=lambda key: capacity[key], reverse=True)

    fig, axes = plt.subplots(1, 2, figsize=(8.8, 4.8), gridspec_kw={"wspace": 0.35})
    colors = [PALETTE["blue"], PALETTE["yellow"], PALETTE["green"], PALETTE["gray"]]
    axes[0].bar(order, [counts[key] for key in order], color=colors[:len(order)])
    axes[0].set_title("Project count", loc="left", fontsize=10.5, pad=10)
    axes[0].set_ylabel("Projects")
    axes[0].grid(axis="y", alpha=0.35)
    axes[0].grid(axis="x", visible=False)
    axes[1].bar(order, [capacity[key] for key in order], color=colors[:len(order)])
    axes[1].set_title("Licensed capacity", loc="left", fontsize=10.5, pad=10)
    axes[1].set_ylabel("MW")
    axes[1].grid(axis="y", alpha=0.35)
    axes[1].grid(axis="x", visible=False)
    for ax in axes:
        ax.tick_params(axis="x", rotation=25, labelsize=9)
    fig.suptitle("Hydropower Pipeline Mix Depends On The Unit Of Count", fontsize=12.5, fontweight="bold")
    fig.subplots_adjust(left=0.08, right=0.98, top=0.82, bottom=0.28)
    save_svg(
        fig,
        FIGURE_DIR / f"{figure_id}.svg",
        figure_id=figure_id,
        source_note="public hydropower portal snapshot",
        caveat="license stage is administrative status",
        generated_date=TODAY,
    )
    return {
        "figure_id": figure_id,
        "title": "Hydropower license-stage mix",
        "path": figure_rel_path(figure_id),
        "source_files": [rel(source)],
        "source_slugs": ["doed-licensing-directive-2075"],
        "target_pages": ["data-fleet-composition"],
        "caption": "Pipeline split by license stage in the public hydropower project dataset.",
        "caveat": "Licensing-stage counts are administrative status snapshots, not financing readiness.",
        "license": "CC-BY 4.0",
        "generator_script": "scripts/build_wiki_figures.py",
        "last_generated": TODAY,
    }


def build_top_operational_projects() -> dict:
    figure_id = "top_operational_projects"
    source = ROOT / "data" / "processed" / "naxa_hydropower_projects.csv"
    rows = [
        row for row in read_csv(source)
        if row["license_type"].strip().lower() == "operation"
    ]
    rows.sort(key=lambda row: float(row["capacity"] or 0), reverse=True)
    rows = rows[:10]
    rows.reverse()

    fig, ax = plt.subplots(figsize=(8.4, 5.3))
    labels = [row["project"] for row in rows]
    values = [float(row["capacity"] or 0) for row in rows]
    bars = ax.barh(labels, values, color=PALETTE["blue"], height=0.62)
    ax.set_title("Operational MW Are Concentrated In A Few Larger Plants", loc="left", fontsize=12.5, pad=12)
    ax.set_xlabel("Capacity (MW)")
    ax.grid(axis="x", alpha=0.35)
    ax.grid(axis="y", visible=False)
    ax.tick_params(axis="y", labelsize=8.5)
    for bar, value in zip(bars, values):
        ax.text(value + 4, bar.get_y() + bar.get_height() / 2, f"{value:g}", va="center", fontsize=8.5)
    ax.set_xlim(0, max(values) * 1.18)
    fig.subplots_adjust(left=0.34, right=0.97, top=0.86, bottom=0.16)
    save_svg(
        fig,
        FIGURE_DIR / f"{figure_id}.svg",
        figure_id=figure_id,
        source_note="public hydropower portal snapshot",
        caveat="portal status can lag commissioning updates",
        generated_date=TODAY,
    )
    return {
        "figure_id": figure_id,
        "title": "Largest operational hydropower projects",
        "path": figure_rel_path(figure_id),
        "source_files": [rel(source)],
        "source_slugs": ["doed-licensing-directive-2075"],
        "target_pages": ["data-fleet-composition"],
        "caption": "Operating MW are concentrated in a small set of larger plants.",
        "caveat": "Public-portal operating status and capacity values can lag commissioning updates.",
        "license": "CC-BY 4.0",
        "generator_script": "scripts/build_wiki_figures.py",
        "last_generated": TODAY,
    }


def build_wecs_basin_potential() -> dict:
    figure_id = "wecs_basin_potential"
    source = ROOT / "data" / "processed" / "wecs_hydropower_potential_2019.txt"
    basins = ["Koshi", "Karnali", "Gandaki", "All other\nbasins"]
    values = [27805, 20385, 19803, 4551]
    colors = [PALETTE["blue"], PALETTE["yellow"], PALETTE["green"], PALETTE["gray"]]

    fig, ax = plt.subplots(figsize=(8.2, 4.8))
    bars = ax.bar(basins, values, color=colors, width=0.62)
    total = sum(values)
    ax.set_title("Three Basins Hold Most Gross Hydropower Potential", loc="left", fontsize=12.5, pad=12)
    ax.set_ylabel("Gross potential (MW)")
    ax.grid(axis="y", alpha=0.35)
    ax.grid(axis="x", visible=False)
    ax.set_ylim(0, 31000)
    for bar, value in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width() / 2, value + 600,
                f"{value:,}\n{value / total:.1%}", ha="center", va="bottom", fontsize=9)
    fig.subplots_adjust(left=0.10, right=0.98, top=0.84, bottom=0.21)
    save_svg(
        fig,
        FIGURE_DIR / f"{figure_id}.svg",
        figure_id=figure_id,
        source_note="WECS 2019 gross potential table",
        caveat="gross potential is not buildable capacity",
        generated_date=TODAY,
    )
    return {
        "figure_id": figure_id,
        "title": "WECS basin distribution of gross hydropower potential",
        "path": figure_rel_path(figure_id),
        "source_files": [rel(source)],
        "source_slugs": ["wecs-hydropower-potential-2019"],
        "target_pages": ["data-basin-discharge", "data-potential-pyramid"],
        "caption": "Gross hydropower potential is concentrated in the Koshi, Karnali, and Gandaki basins.",
        "caveat": "Gross potential is not equivalent to economically developable or transmission-ready capacity.",
        "license": "CC-BY 4.0",
        "generator_script": "scripts/build_wiki_figures.py",
        "last_generated": TODAY,
    }


def build_capacity_balance_fy2024_25() -> dict:
    figure_id = "capacity_balance_fy2024_25"
    source = ROOT / "data" / "processed" / "tables" / "nea_monthly_capacity_balance_fy2024_2025.csv"
    rows = {row["metric"]: row for row in read_csv(source)}
    components = [
        ("IPP", "IPP", PALETTE["green"]),
        ("NEA_SUBSIDIARY", "NEA subsidiary", PALETTE["blue"]),
        ("NEA_ROR_PROR", "NEA RoR/PRoR", PALETTE["cyan"]),
        ("NEA_STORAGE", "Storage", PALETTE["purple"]),
        ("IMPORT", "Import", PALETTE["red"]),
    ]
    x = list(range(len(MONTHS)))
    bottom = [0.0 for _ in MONTHS]

    fig, ax = plt.subplots(figsize=(8.8, 5.1))
    for metric, label, color in components:
        values = [float(rows[metric][month]) for month in MONTHS]
        ax.bar(x, values, bottom=bottom, color=color, width=0.72, label=label, linewidth=0)
        bottom = [b + v for b, v in zip(bottom, values)]
    national_peak = [float(rows["MONTHLY_NATIONAL_PEAK_DEMAND"][month]) for month in MONTHS]
    system_peak = [float(rows["MONTHLY_SYSTEM_PEAK_DEMAND"][month]) for month in MONTHS]
    ax.plot(x, national_peak, color=PALETTE["ink"], marker="o", linewidth=2.0, label="National peak")
    ax.plot(x, system_peak, color=PALETTE["gray"], marker="o", linewidth=1.4, linestyle="--", label="System peak")
    ax.axvspan(4.5, 10.5, color="#efe1c4", alpha=0.28, zorder=0)
    ax.set_xticks(x, MONTH_LABELS)
    ax.set_ylabel("MW")
    ax.set_title("FY 2024/25 Monthly Capacity Stack Still Needs Dry-Season Imports", loc="left", fontsize=12.3, pad=12)
    ax.grid(axis="y", alpha=0.35)
    ax.grid(axis="x", visible=False)
    ax.legend(ncol=3, loc="upper center", bbox_to_anchor=(0.5, -0.17), fontsize=8.5, frameon=False)
    fig.subplots_adjust(left=0.09, right=0.98, top=0.84, bottom=0.29)
    save_svg(
        fig,
        FIGURE_DIR / f"{figure_id}.svg",
        figure_id=figure_id,
        source_note="NEA FY2024/25 monthly capacity balance",
        caveat="capacity-side monthly peaks, not hourly dispatch",
        generated_date=TODAY,
    )
    return {
        "figure_id": figure_id,
        "title": "FY 2024/25 monthly capacity balance",
        "path": figure_rel_path(figure_id),
        "source_files": [rel(source)],
        "source_slugs": ["nea-annual-report-fy2024-25"],
        "target_pages": ["data-domestic-demand", "data-fleet-composition"],
        "caption": "Monthly capacity contribution by IPPs, NEA plants, imports, and storage against national and system peak demand.",
        "caveat": "Monthly capacity-balance rows do not replace hourly dispatch or adequacy modeling.",
        "license": "CC-BY 4.0",
        "generator_script": "scripts/build_wiki_figures.py",
        "last_generated": TODAY,
    }


def build_export_revenue_fy2025_26() -> dict:
    figure_id = "export_revenue_fy2025_26"
    source = ROOT / "wiki" / "pages" / "data" / "data-trade-time-series.md"
    months = ["Shrawan", "Bhadra", "Ashoj", "Kartik", "Mangsir"]
    labels = ["Shr", "Bhd", "Ash", "Kar", "Man"]
    revenue = [3.87, 4.49, 5.03, 3.76, 1.10]
    x = list(range(len(months)))

    fig, ax = plt.subplots(figsize=(8.1, 4.7))
    bars = ax.bar(x, revenue, color=[PALETTE["green"], PALETTE["green"], PALETTE["green"], PALETTE["yellow"], PALETTE["red"]], width=0.62)
    ax.plot(x, revenue, color=PALETTE["ink"], linewidth=1.8, marker="o")
    ax.set_xticks(x, labels)
    ax.set_ylabel("Export revenue (NPR billion)")
    ax.set_ylim(0, 5.8)
    ax.set_title("Export Revenue Falls Fast As Dry Season Arrives", loc="left", fontsize=12.5, pad=12)
    ax.grid(axis="y", alpha=0.35)
    ax.grid(axis="x", visible=False)
    for bar, value in zip(bars, revenue):
        ax.text(bar.get_x() + bar.get_width() / 2, value + 0.12, f"{value:.2f}",
                ha="center", va="bottom", fontsize=9.2)
    ax.annotate(
        "exports halt after Mangsir\nas imports resume",
        xy=(4, revenue[-1]),
        xytext=(3.05, 3.0),
        arrowprops={"arrowstyle": "->", "color": PALETTE["muted"], "lw": 1},
        fontsize=9,
        color=PALETTE["muted"],
        ha="left",
    )
    fig.subplots_adjust(left=0.10, right=0.98, top=0.84, bottom=0.20)
    save_svg(
        fig,
        FIGURE_DIR / f"{figure_id}.svg",
        figure_id=figure_id,
        source_note="FY2025/26 NEA export-revenue reports",
        caveat="first five months only",
        generated_date=TODAY,
    )
    return {
        "figure_id": figure_id,
        "title": "FY 2025/26 first-five-month export revenue",
        "path": figure_rel_path(figure_id),
        "source_files": [rel(source)],
        "source_slugs": ["nea-annual-report-fy2024-25"],
        "target_pages": ["data-trade-time-series"],
        "caption": "First-five-month FY 2025/26 export revenue peaks in Ashoj and collapses by Mangsir as dry-season conditions return.",
        "caveat": "First five months only; this is not a full-year revenue curve.",
        "license": "CC-BY 4.0",
        "generator_script": "scripts/build_wiki_figures.py",
        "last_generated": TODAY,
    }


def build_potential_pyramid_funnel() -> dict:
    figure_id = "potential_pyramid_funnel"
    source = ROOT / "wiki" / "pages" / "data" / "data-potential-pyramid.md"
    rows = [
        ("Legacy theoretical", 83000),
        ("WECS gross", 72544),
        ("Technical", 44000),
        ("Techno-economic", 32680),
        ("Realistic by 2040", 12500),
        ("Installed FY 2024/25", 3591),
    ]
    labels = [row[0] for row in rows][::-1]
    values = [row[1] for row in rows][::-1]

    fig, ax = plt.subplots(figsize=(8.4, 5.0))
    colors = [PALETTE["red"], PALETTE["yellow"], PALETTE["green"], PALETTE["cyan"], PALETTE["blue"], PALETTE["gray"]]
    bars = ax.barh(labels, values, color=colors, height=0.62)
    ax.set_xlabel("MW")
    ax.set_title("The 83,000 MW Slogan Shrinks Through Successive Filters", loc="left", fontsize=12.3, pad=12)
    ax.grid(axis="x", alpha=0.35)
    ax.grid(axis="y", visible=False)
    ax.tick_params(axis="y", labelsize=9)
    ax.set_xlim(0, 88000)
    for bar, value in zip(bars, values):
        ax.text(value + 1400, bar.get_y() + bar.get_height() / 2,
                f"{value:,}", va="center", fontsize=9)
    ax.text(
        0.63,
        0.14,
        "Installed is ~4% of the legacy theoretical headline",
        transform=ax.transAxes,
        fontsize=9,
        color=PALETTE["muted"],
    )
    fig.subplots_adjust(left=0.24, right=0.98, top=0.86, bottom=0.18)
    save_svg(
        fig,
        FIGURE_DIR / f"{figure_id}.svg",
        figure_id=figure_id,
        source_note="WECS/WB/NEA levels summarized in potential page",
        caveat="intermediate filters are order-of-magnitude estimates",
        generated_date=TODAY,
    )
    return {
        "figure_id": figure_id,
        "title": "Hydropower potential pyramid",
        "path": figure_rel_path(figure_id),
        "source_files": [rel(source)],
        "source_slugs": ["wecs-hydropower-potential-2019", "wb-nepal-power-sector-reform-2022", "nea-annual-report-fy2024-25"],
        "target_pages": ["data-potential-pyramid"],
        "caption": "The headline theoretical hydropower number narrows sharply as physical, technical, economic, and delivery filters are applied.",
        "caveat": "Intermediate levels are compiled order-of-magnitude estimates, not definitive ceilings.",
        "license": "CC-BY 4.0",
        "generator_script": "scripts/build_wiki_figures.py",
        "last_generated": TODAY,
    }


def copy_legacy_figure(
    *,
    figure_id: str,
    filename: str,
    title: str,
    source_files: list[str],
    source_slugs: list[str],
    target_pages: list[str],
    caption: str,
    caveat: str,
    license_text: str = "CC-BY 4.0",
    raster_ok: bool = False,
) -> dict:
    source = LEGACY_FIGURE_DIR / filename
    suffix = source.suffix.lower()
    if suffix not in {".png", ".svg"}:
        raise ValueError(f"Unsupported legacy figure format: {source}")
    target = FIGURE_DIR / f"{figure_id}{suffix}"
    if not source.exists():
        raise FileNotFoundError(source)
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)
    return {
        "figure_id": figure_id,
        "title": title,
        "path": f"../assets/figures/{figure_id}{suffix}",
        "source_files": source_files,
        "source_slugs": source_slugs,
        "target_pages": target_pages,
        "caption": caption,
        "caveat": caveat,
        "license": license_text,
        "generator_script": "scripts/build_wiki_figures.py",
        "last_generated": TODAY,
        "format": suffix.removeprefix("."),
        "legacy_source": rel(source),
        "raster_ok": raster_ok,
    }


def write_manifest(figures: list[dict]) -> None:
    manifest = {
        "version": 1,
        "_doc": "Published wiki figure registry. Figure paths resolve relative to wiki/explorer/.",
        "generated_at": TODAY,
        "default_license": "CC-BY 4.0",
        "figures": {entry["figure_id"]: entry for entry in figures},
    }
    MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_figure_index(figures: list[dict]) -> None:
    lines = [
        "---",
        "title: Figure Index",
        "type: data",
        "created: 2026-05-13",
        f"updated: {TODAY}",
        "figure_type: table",
        "sources: []",
        "tags: [figures, charts, manifest, data]",
        "page_quality: record",
        "generator: figures",
        "---",
        "",
        "# Figure Index",
        "",
        "## Summary",
        "",
        "Registry of published wiki figures generated from `wiki/explorer/shared/wiki-figure-manifest.json`.",
        "",
        "## Published Figures",
        "",
        "| Figure | Format | Target Pages | Sources | Caveat |",
        "|--------|--------|--------------|---------|--------|",
    ]
    for entry in figures:
        path = "../../../wiki/" + entry["path"].removeprefix("../")
        label = entry["figure_id"]
        fmt = Path(entry["path"]).suffix.removeprefix(".").upper()
        targets = ", ".join(f"[[{slug}]]" for slug in entry.get("target_pages", [])) or "-"
        sources = ", ".join(f"[[{slug}]]" for slug in entry.get("source_slugs", [])) or "-"
        caveat = entry.get("caveat", "")
        lines.append(f"| [{label}]({path}) | {fmt} | {targets} | {sources} | {caveat} |")
    lines.extend(
        [
            "",
            "## Regeneration",
            "",
            "Run from the workspace root:",
            "",
            "```bash",
            "make wiki-figures",
            "```",
            "",
            "The generated manifest is the source of truth for figure paths, source files, target pages, caveats, and license metadata.",
        ]
    )
    FIGURE_INDEX_PAGE.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    apply_chart_style()
    figures = [
        build_monthly_trade_3y(),
        build_fleet_capacity_mix(),
        build_basin_seasonality_compare(),
        build_storage_gap(),
        build_electricity_trade_shift(),
        build_lead1_trade_vs_storage(),
        build_license_type_mix(),
        build_top_operational_projects(),
        build_wecs_basin_potential(),
        build_capacity_balance_fy2024_25(),
        build_export_revenue_fy2025_26(),
        build_potential_pyramid_funnel(),
        copy_legacy_figure(
            figure_id="hydropower_license_map",
            filename="hydropower_license_map.png",
            title="Hydropower project licensing map",
            source_files=["figures/hydropower_license_map.png"],
            source_slugs=["doed-licensing-directive-2075"],
            target_pages=["data-potential-pyramid"],
            caption="Licensed project locations cluster along Nepal's Himalayan hydropower arc.",
            caveat="Static map is a portfolio snapshot; use the explorer map for current interactive filtering.",
            raster_ok=True,
        ),
    ]
    write_manifest(figures)
    write_figure_index(figures)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
