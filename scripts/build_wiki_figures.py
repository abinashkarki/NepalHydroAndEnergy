#!/usr/bin/env python3
from __future__ import annotations

import csv
import datetime as dt
import hashlib
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


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def source_file_hashes(entry: dict) -> dict[str, str]:
    hashes: dict[str, str] = {}
    for source_file in entry.get("source_files", []):
        source_path = ROOT / source_file
        if source_path.exists():
            hashes[source_file] = file_sha256(source_path)
    return hashes


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


ENERGY_BALANCE_FY2025_26 = ROOT / "data" / "processed" / "tables" / "nea_energy_balance_monthly_fy2025_26.csv"
ENERGY_BALANCE_MONTHS = ["Shrawan", "Bhadra", "Ashwin", "Kartik", "Mangshir", "Poush", "Magh", "Falgun",
                         "Chaitra", "Baishakh", "Jestha", "Ashadh"]
DOMESTIC_ROWS = ["IPP", "NEA_SUBSIDIARY", "NEA_ROR_PROR", "STORAGE", "SOLAR", "THERMAL"]


def read_energy_balance_fy2025_26() -> dict:
    rows = {row["metric"]: row for row in read_csv(ENERGY_BALANCE_FY2025_26)}
    series: dict = {metric: [float(row[m]) for m in ENERGY_BALANCE_MONTHS] for metric, row in rows.items()}
    series["DOMESTIC"] = [sum(series[r][i] for r in DOMESTIC_ROWS) for i in range(12)]
    # NEA's printed row totals; monthly cells can differ by rounding.
    series["TOTALS"] = {metric: float(row["Total"]) for metric, row in rows.items()}
    return series


def build_energy_balance_fy2025_26() -> dict:
    figure_id = "energy_balance_fy2025_26"
    s = read_energy_balance_fy2025_26()
    x = list(range(12))
    gen, demand = s["DOMESTIC"], s["MONTHLY_NATIONAL_ENERGY_DEMAND"]
    fig, ax = plt.subplots(figsize=(8.4, 4.8))
    ax.fill_between(x, gen, demand, where=[g >= d for g, d in zip(gen, demand)], interpolate=True,
                    color=PALETTE["green"], alpha=0.18, linewidth=0, label="Surplus (exported)")
    ax.fill_between(x, gen, demand, where=[g < d for g, d in zip(gen, demand)], interpolate=True,
                    color=PALETTE["red"], alpha=0.25, linewidth=0, label="Deficit (imported)")
    ax.plot(x, gen, color=PALETTE["blue"], linewidth=2.4, marker="o", markersize=4, label="Domestic generation")
    ax.plot(x, demand, color=PALETTE["ink"], linewidth=1.8, linestyle="--", label="National demand")
    bhadra, falgun = 1, 7
    ax.annotate(f"Bhadra: {gen[bhadra]:,.0f} GWh generated,\n{s['EXPORT'][bhadra]:,.0f} GWh exported",
                xy=(bhadra, gen[bhadra]), xytext=(1.6, 2350), fontsize=8.5, color=PALETTE["ink"],
                arrowprops={"arrowstyle": "-", "color": PALETTE["muted"], "linewidth": 0.8})
    ax.annotate(f"Falgun: {gen[falgun]:,.0f} GWh generated,\n{s['IMPORT'][falgun]:,.0f} GWh imported",
                xy=(falgun, gen[falgun]), xytext=(4.6, 380), fontsize=8.5, color=PALETTE["ink"],
                arrowprops={"arrowstyle": "-", "color": PALETTE["muted"], "linewidth": 0.8})
    ax.set_xticks(x, MONTH_LABELS)
    ax.set_ylim(0, 2600)
    ax.set_ylabel("GWh per month")
    ax.set_xlabel("Nepali fiscal month, FY 2025/26 (mid-July 2025 to mid-July 2026)")
    ax.set_title("A record net-export year still ran a dry-season deficit", loc="left", fontsize=13, pad=12)
    ax.grid(axis="y", alpha=0.42)
    ax.grid(axis="x", visible=False)
    ax.legend(ncol=4, loc="lower center", bbox_to_anchor=(0.5, -0.33), fontsize=8.5, frameon=False)
    fig.subplots_adjust(left=0.10, right=0.98, top=0.88, bottom=0.30)
    save_svg(fig, FIGURE_DIR / f"{figure_id}.svg", figure_id=figure_id,
             source_note="NEA Annual Report FY 2025/26, energy balance p.166",
             caveat="monthly table; summary trade totals differ slightly", generated_date=TODAY)
    return {
        "figure_id": figure_id,
        "title": "Monthly domestic generation and national demand, FY 2025/26",
        "path": figure_rel_path(figure_id),
        "source_files": [rel(ENERGY_BALANCE_FY2025_26)],
        "source_slugs": ["nea-annual-report-fy2025-26"],
        "target_pages": ["master-thesis", "seasonal-mismatch"],
        "caption": "Domestic generation exceeded national demand from Baishakh to Mangshir and fell short from Poush to Chaitra, even though FY 2025/26 ended with 2,794 GWh of net exports.",
        "caveat": "Monthly energy-balance table totals (exports 3,938 GWh, imports 1,155 GWh) differ slightly from the managing director's summary (3,965 and 1,171 GWh).",
        "license": "CC-BY 4.0",
        "generator_script": "scripts/build_wiki_figures.py",
        "last_generated": TODAY,
    }


def build_storage_vs_imports_fy2025_26() -> dict:
    figure_id = "storage_vs_imports_fy2025_26"
    s = read_energy_balance_fy2025_26()
    x = list(range(12))
    width = 0.4
    fig, ax = plt.subplots(figsize=(8.4, 4.6))
    ax.bar([i - width / 2 for i in x], s["IMPORT"], width=width, color=PALETTE["red"], label=f"Imports ({s['TOTALS']['IMPORT']:,.0f} GWh in the year)")
    ax.bar([i + width / 2 for i in x], s["STORAGE"], width=width, color=PALETTE["purple"], label=f"Kulekhani storage cascade ({s['TOTALS']['STORAGE']:,.0f} GWh)")
    ax.set_xticks(x, MONTH_LABELS)
    ax.set_ylabel("GWh per month")
    ax.set_xlabel("Nepali fiscal month, FY 2025/26")
    ax.set_title("Nepal's only reservoir cascade is small beside the dry-season gap", loc="left", fontsize=12.5, pad=12)
    ax.grid(axis="y", alpha=0.42)
    ax.grid(axis="x", visible=False)
    ax.legend(loc="upper left", fontsize=8.8, frameon=False)
    fig.subplots_adjust(left=0.10, right=0.98, top=0.87, bottom=0.17)
    save_svg(fig, FIGURE_DIR / f"{figure_id}.svg", figure_id=figure_id,
             source_note="NEA Annual Report FY 2025/26, energy balance p.166 and plant table",
             caveat="storage row = Kulekhani I-III output", generated_date=TODAY)
    return {
        "figure_id": figure_id,
        "title": "Monthly imports versus seasonal-storage generation, FY 2025/26",
        "path": figure_rel_path(figure_id),
        "source_files": [rel(ENERGY_BALANCE_FY2025_26)],
        "source_slugs": ["nea-annual-report-fy2025-26"],
        "target_pages": ["storage-deficit"],
        "caption": "The Kulekhani cascade generated 92 GWh across FY 2025/26, most of it in Baishakh and Jestha; Nepal imported 1,155 GWh, most of it from Poush to Chaitra.",
        "caveat": "The energy-balance STORAGE row equals the Kulekhani I-III plant totals (53.0, 26.4 and 12.9 GWh) in NEA's generation table.",
        "license": "CC-BY 4.0",
        "generator_script": "scripts/build_wiki_figures.py",
        "last_generated": TODAY,
    }


def build_mw_vs_dependable_fy2025_26() -> dict:
    figure_id = "mw_vs_dependable_fy2025_26"
    s = read_energy_balance_fy2025_26()
    falgun_days = 30  # Falgun 2082: 13 February to 14 March 2026
    falgun_avg_mw = s["DOMESTIC"][7] * 1000 / (falgun_days * 24)
    labels = ["Installed generation capacity", "National peak demand", "Average domestic output in Falgun", "Operating seasonal storage (Kulekhani)"]
    values = [4120, 2479, falgun_avg_mw, 106]
    colors = [PALETTE["gray"], PALETTE["ink"], PALETTE["blue"], PALETTE["purple"]]
    fig, ax = plt.subplots(figsize=(8.4, 3.6))
    bars = ax.barh(labels[::-1], values[::-1], color=colors[::-1], height=0.55)
    for bar, value in zip(bars, values[::-1]):
        ax.text(value + 50, bar.get_y() + bar.get_height() / 2, f"{value:,.0f} MW", va="center", fontsize=9.5, fontweight="bold")
    ax.set_xlim(0, 4800)
    ax.set_xlabel("MW")
    ax.set_title("Megawatts installed are not megawatts available in the dry season", loc="left", fontsize=12.5, pad=12)
    ax.grid(axis="x", alpha=0.35)
    ax.grid(axis="y", visible=False)
    fig.subplots_adjust(left=0.36, right=0.97, top=0.85, bottom=0.17)
    save_svg(fig, FIGURE_DIR / f"{figure_id}.svg", figure_id=figure_id,
             source_note="NEA Annual Report FY 2025/26, pp.1, 3, 166, 175",
             caveat="Falgun output is a monthly average, not a peak-hour capability", generated_date=TODAY)
    return {
        "figure_id": figure_id,
        "title": "Installed capacity, peak demand and dry-season output, FY 2025/26",
        "path": figure_rel_path(figure_id),
        "source_files": [rel(ENERGY_BALANCE_FY2025_26)],
        "source_slugs": ["nea-annual-report-fy2025-26"],
        "target_pages": ["master-thesis", "claim-mw-not-equal-value"],
        "caption": "4,120 MW was installed and national peak demand reached 2,479 MW, but domestic generation in Falgun averaged about 1,110 MW across the month; operating seasonal storage is 106 MW.",
        "caveat": "The Falgun figure divides 801 GWh by the hours in a 30-day month. It is an average, not dependable peak-hour capacity, which is not published.",
        "license": "CC-BY 4.0",
        "generator_script": "scripts/build_wiki_figures.py",
        "last_generated": TODAY,
    }


def build_nea_cost_structure_fy2025_26() -> dict:
    figure_id = "nea_cost_structure_fy2025_26"
    revenue = 148.625  # NRs billion, net revenue from energy sales incl. 29.314 exports (PDF pp.12-13)
    items = [
        ("Power purchases", 96.104),
        ("Distribution", 13.113),
        ("Foreign-exchange losses", 11.517),
        ("Depreciation and amortisation", 11.196),
        ("Interest", 7.597),
        ("Transmission", 2.523),
        ("Generation", 2.305),
        ("Royalties incl. ERC fee", 1.902),
        ("Power-service export charges", 1.440),
    ]
    labels = [label for label, _ in items][::-1]
    values = [value for _, value in items][::-1]
    fig, ax = plt.subplots(figsize=(8.4, 4.8))
    bars = ax.barh(labels, values, color=[PALETTE["red"] if v > 50 else PALETTE["gray"] for v in values], height=0.6)
    for bar, value in zip(bars, values):
        ax.text(value + 1.2, bar.get_y() + bar.get_height() / 2, f"{value:,.1f} ({value / revenue:.0%})", va="center", fontsize=9)
    ax.set_xlim(0, 120)
    ax.set_xlabel("NRs billion (share of NRs 148.6 billion energy-sales revenue)")
    ax.set_title("Buying power from producers is NEA's dominant cost", loc="left", fontsize=12.5, pad=12)
    ax.grid(axis="x", alpha=0.35)
    ax.grid(axis="y", visible=False)
    fig.subplots_adjust(left=0.33, right=0.97, top=0.88, bottom=0.14)
    save_svg(fig, FIGURE_DIR / f"{figure_id}.svg", figure_id=figure_id,
             source_note="NEA Annual Report FY 2025/26, managing director's report pp.2-3",
             caveat="pre-audit figures; shares are of energy-sales revenue", generated_date=TODAY)
    return {
        "figure_id": figure_id,
        "title": "NEA cost lines as a share of energy-sales revenue, FY 2025/26",
        "path": figure_rel_path(figure_id),
        "source_files": ["wiki/pages/sources/nea-annual-report-fy2025-26.md"],
        "source_slugs": ["nea-annual-report-fy2025-26"],
        "target_pages": ["nea-triple-authority"],
        "caption": "Power purchases of NRs 96.1 billion equalled 65% of NEA's NRs 148.6 billion energy-sales revenue in FY 2025/26, up 23.97% on the year.",
        "caveat": "Managing director's report figures, pre-audit. Cost lines are not exhaustive and do not sum to revenue minus profit because other income and provisions are excluded.",
        "license": "CC-BY 4.0",
        "generator_script": "scripts/build_wiki_figures.py",
        "last_generated": TODAY,
    }


def build_schedule_slippage() -> dict:
    figure_id = "schedule_slippage"
    # (project, planned year, latest year, latest label, finished?) from the linked entity pages.
    rows = [
        ("Chameliya (30 MW)", 2011.45, 2018.11, "commissioned Feb 2018", True),
        ("Tanahu (140 MW reservoir)", 2020.99, 2026.54, "~78% complete, mid-2026", False),
        ("Arun-3 (900 MW)", 2028.0, 2029.2, "expected FY 2028/29 Q3 (May 2026)", False),
    ]
    planned_labels = ["planned Jun 2011", "planned end-2020 (ADB 2013)", "expected FY 2027/28 (May 2025)"]
    fig, ax = plt.subplots(figsize=(8.4, 3.6))
    for i, ((_name, planned, latest, label, finished), plabel) in enumerate(zip(rows, planned_labels)):
        y = len(rows) - 1 - i
        ax.plot([planned, latest], [y, y], color=PALETTE["grid"], linewidth=6, solid_capstyle="round", zorder=1)
        ax.scatter([planned], [y], s=70, color=PALETTE["blue"], zorder=3)
        ax.scatter([latest], [y], s=70, color=PALETTE["red"] if finished else "white",
                   edgecolors=PALETTE["red"], linewidths=2, zorder=3)
        ax.text(planned - 0.15, y + 0.22, plabel, ha="right", fontsize=8.3, color=PALETTE["blue"])
        ax.text(latest + 0.15, y + 0.22, label, ha="left", fontsize=8.3, color=PALETTE["red"])
    ax.set_yticks(range(len(rows)), [r[0] for r in rows][::-1])
    ax.set_xlim(2008, 2036)
    ax.set_ylim(-0.6, len(rows) - 0.3)
    ax.set_xlabel("Year (filled red = commissioned; hollow = not yet)")
    ax.set_title("Large hydropower projects finish years after their plans", loc="left", fontsize=12.5, pad=12)
    ax.grid(axis="x", alpha=0.35)
    ax.grid(axis="y", visible=False)
    fig.subplots_adjust(left=0.26, right=0.98, top=0.86, bottom=0.18)
    save_svg(fig, FIGURE_DIR / f"{figure_id}.svg", figure_id=figure_id,
             source_note="Chameliya, Tanahu and Arun-3 entity pages (ADB 2013; NEA FY 2025/26; SJVN 2025-26)",
             caveat="Arun-3 points are successive developer expectations, not an original target", generated_date=TODAY)
    return {
        "figure_id": figure_id,
        "title": "Planned versus actual or latest expected completion for three hydropower projects",
        "path": figure_rel_path(figure_id),
        "source_files": ["wiki/pages/entities/chameliya-hydropower.md", "wiki/pages/entities/tanahu-hydropower.md", "wiki/pages/entities/arun-3.md"],
        "source_slugs": ["adb-tanahu-project-documents-2026", "nea-annual-report-fy2025-26"],
        "target_pages": ["buildability"],
        "caption": "Chameliya was planned for June 2011 and commissioned in February 2018; Tanahu was appraised for completion by end-2020 and was about 78% complete in mid-2026; Arun-3's expected commissioning moved a year later between May 2025 and May 2026.",
        "caveat": "Arun-3's two points are successive developer expectations, not the original target. Mid-year positions are approximate.",
        "license": "CC-BY 4.0",
        "generator_script": "scripts/build_wiki_figures.py",
        "last_generated": TODAY,
    }


def build_contracted_energy_performance() -> dict:
    figure_id = "contracted_energy_performance"
    # Actual generation as % of contracted energy, from the table on the Q-design page.
    # Likhu-2 FY 2023/24 (~60%) is excluded there as a transmission bottleneck, not hydrology.
    rows = [
        ("Chilime (22.1 MW)", [("FY 2075/76", 115.6), ("FY 2076/77", 110.1)]),
        ("Upper Tamakoshi (456 MW)", [("FY 2079/80", 85.3), ("FY 2080/81", 90.2)]),
        ("Sanima Mai (22 MW)", [("FY 2076/77", 96.0), ("FY 2077/78", 88.0), ("FY 2078/79", 73.0), ("FY 2079/80", 85.0)]),
        ("Likhu-2 (55 MW)", [("FY 2024/25", 91.0)]),
        ("Api Power (8 MW)", [("FY 2075/76", 68.0)]),
    ]
    fig, ax = plt.subplots(figsize=(8.4, 3.9))
    for i, (_name, points) in enumerate(rows):
        y = len(rows) - 1 - i
        values = [v for _, v in points]
        ax.plot([min(values), max(values)], [y, y], color=PALETTE["grid"], linewidth=5, solid_capstyle="round", zorder=1)
        ax.scatter(values, [y] * len(values), s=55, color=[PALETTE["green"] if v >= 100 else PALETTE["blue"] for v in values], zorder=3)
    ax.axvline(100, color=PALETTE["ink"], linewidth=1.2, linestyle="--")
    ax.text(100.8, len(rows) - 0.55, "contracted energy", fontsize=8.5, color=PALETTE["ink"])
    ax.set_yticks(range(len(rows)), [r[0] for r in rows][::-1])
    ax.set_xlim(60, 120)
    ax.set_ylim(-0.6, len(rows) - 0.3)
    ax.set_xlabel("Actual annual generation as % of contracted energy (each dot is one fiscal year)")
    ax.set_title("Most projects deliver less energy than their contracts assume", loc="left", fontsize=12.5, pad=12)
    ax.grid(axis="x", alpha=0.35)
    ax.grid(axis="y", visible=False)
    fig.subplots_adjust(left=0.27, right=0.97, top=0.87, bottom=0.17)
    save_svg(fig, FIGURE_DIR / f"{figure_id}.svg", figure_id=figure_id,
             source_note="Q-design discharge page: CHCL, UKHLL, CARE and ICRANP records",
             caveat="small non-random sample; Likhu-2 FY 2023/24 excluded (transmission)", generated_date=TODAY)
    return {
        "figure_id": figure_id,
        "title": "Actual generation as a share of contracted energy, selected projects",
        "path": figure_rel_path(figure_id),
        "source_files": ["wiki/pages/concepts/q-design-discharge.md"],
        "source_slugs": ["chilime-annual-report-fy2078-79", "care-ratings-sanima-mai", "ukhl-annual-report"],
        "target_pages": ["q-design-discharge"],
        "caption": "Only Chilime exceeded its contracted energy in the years shown; the others delivered 68–96% of contract, with Sanima Mai falling to 73% in FY 2078/79.",
        "caveat": "A small, non-random sample from company reports and ratings; no central public database tracks generation against contract. Likhu-2's FY 2023/24 shortfall reflected a substation bottleneck and is excluded.",
        "license": "CC-BY 4.0",
        "generator_script": "scripts/build_wiki_figures.py",
        "last_generated": TODAY,
    }


# ── Sprint 2 data-registry figures (values read only from committed CSVs) ─────


def _num(raw: str) -> float | None:
    raw = (raw or "").strip().replace(",", "")
    try:
        return float(raw)
    except ValueError:
        return None


def _slugs(values) -> list[str]:
    return sorted({slug.strip() for value in values for slug in (value or "").split(";") if slug.strip()})


def _style_axis(ax, *, grid_axis: str = "y") -> None:
    ax.grid(axis=grid_axis, alpha=0.42)
    ax.grid(axis="x" if grid_axis == "y" else "y", visible=False)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    ax.tick_params(axis="both", labelsize=8.5)


def build_nea_system_trajectory() -> dict:
    figure_id = "nea_system_trajectory_11yr"
    source = ROOT / "data" / "nea_system_annual_timeseries.csv"
    rows = read_csv(source)
    years = [r["fiscal_year_ad"] for r in rows]
    labels = [y.replace("20", "", 1) for y in years]  # "2015/16" -> "15/16"
    nea = [_num(r["energy_nea_gwh"]) or 0 for r in rows]
    sub = [_num(r["energy_nea_subsidiary_gwh"]) or 0 for r in rows]
    ipp = [_num(r["energy_ipp_gwh"]) or 0 for r in rows]
    imports = [_num(r["energy_import_gwh"]) or 0 for r in rows]
    exports = [_num(r["energy_export_gwh"]) or 0 for r in rows]
    loss = [_num(r["system_loss_pct"]) for r in rows]
    x = list(range(len(rows)))

    fig, axes = plt.subplots(3, 1, figsize=(8.4, 8.6), sharex=True,
                             gridspec_kw={"height_ratios": [1.5, 1.0, 0.8], "hspace": 0.32})
    ax = axes[0]
    bottom = [0.0] * len(rows)
    for values, label, color in (
        (nea, "NEA own plants", PALETTE["blue"]),
        (sub, "NEA subsidiaries", PALETTE["cyan"]),
        (ipp, "Independent power producers", PALETTE["green"]),
    ):
        ax.bar(x, values, bottom=bottom, width=0.68, color=color, label=label,
               edgecolor=PALETTE["panel"], linewidth=1.0)
        bottom = [b + v for b, v in zip(bottom, values)]
    ax.text(x[0], bottom[0] + 300, f"{bottom[0]:,.0f}", ha="center", fontsize=8, color=PALETTE["ink"])
    ax.text(x[-1], bottom[-1] + 300, f"{bottom[-1]:,.0f}", ha="center", fontsize=8, color=PALETTE["ink"])
    ax.set_ylim(0, max(bottom) * 1.12)
    ax.set_ylabel("Domestic generation, GWh")
    ax.set_title("Nepal's power system, FY 2015/16 to 2025/26", loc="left", fontsize=13, pad=10)
    ax.legend(ncol=3, loc="upper left", fontsize=8.5, frameon=False)
    _style_axis(ax)

    ax = axes[1]
    ax.plot(x, imports, marker="o", linewidth=2, markersize=5, color=PALETTE["red"], label="Imports")
    ax.plot(x, exports, marker="o", linewidth=2, markersize=5, color=PALETTE["purple"], label="Exports")
    ax.text(x[-1] + 0.15, imports[-1], f"{imports[-1]:,.0f}", va="center", fontsize=8, color=PALETTE["ink"])
    ax.text(x[-1] + 0.15, exports[-1], f"{exports[-1]:,.0f}", va="center", fontsize=8, color=PALETTE["ink"])
    ax.set_ylabel("Cross-border, GWh")
    ax.set_ylim(0, max(imports + exports) * 1.15)
    ax.legend(ncol=2, loc="upper left", fontsize=8.5, frameon=False)
    _style_axis(ax)

    ax = axes[2]
    lx = [i for i, v in zip(x, loss) if v is not None]
    ly = [v for v in loss if v is not None]
    ax.plot(lx, ly, marker="o", linewidth=2, markersize=5, color=PALETTE["gray"])
    ax.text(lx[0], ly[0] + 1.4, f"{ly[0]:.2f}%", ha="center", fontsize=8, color=PALETTE["ink"])
    ax.text(lx[-1], ly[-1] + 1.4, f"{ly[-1]:.2f}%", ha="center", fontsize=8, color=PALETTE["ink"])
    ax.set_ylim(0, max(ly) * 1.25)
    ax.set_ylabel("System loss, %")
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.set_xlabel("Fiscal year (AD)")
    _style_axis(ax)
    fig.subplots_adjust(left=0.11, right=0.95, top=0.94, bottom=0.10)
    save_svg(fig, FIGURE_DIR / f"{figure_id}.svg", figure_id=figure_id,
             source_note="NEA annual-report statistics appendices FY 2024/25 and 2025/26",
             caveat="subsidiary/NEA split changes from FY 2021/22; loss is NEA system loss", generated_date=TODAY)
    return {
        "figure_id": figure_id,
        "title": "Nepal power system trajectory, FY 2015/16 to 2025/26",
        "path": figure_rel_path(figure_id),
        "source_files": [rel(source)],
        "source_slugs": _slugs(r["source_slug"] for r in rows),
        "target_pages": ["data-nea-system-annual-timeseries"],
        "caption": (f"Domestic generation rose from {bottom[0]:,.0f} GWh to {bottom[-1]:,.0f} GWh, exports from "
                    f"{exports[0]:,.0f} to {exports[-1]:,.0f} GWh, and system loss fell from {ly[0]:.2f}% to {ly[-1]:.2f}%."),
        "caveat": "The jump in NEA-subsidiary generation from FY 2021/22 reflects plants reported under subsidiaries (such as Upper Tamakoshi), not only new capacity.",
        "license": "CC-BY 4.0",
        "generator_script": "scripts/build_wiki_figures.py",
        "last_generated": TODAY,
    }


PROVINCE_ORDER = ["Koshi", "Madhesh", "Bagmati", "Gandaki", "Lumbini", "Karnali", "Sudurpashchim"]


def build_substation_province_capacity() -> dict:
    figure_id = "substation_province_capacity"
    source = ROOT / "data" / "substation_specs.csv"
    rows = read_csv(source)
    installed: dict[str, float] = {}
    pipeline: dict[str, float] = {}
    for row in rows:
        province = row["province"].strip() or "Province not assigned"
        installed[province] = installed.get(province, 0.0) + (_num(row["installed_mva"]) or 0.0)
        pipeline[province] = pipeline.get(province, 0.0) + (_num(row["planned_additional_mva"]) or 0.0)
    provinces = sorted((p for p in installed if p in PROVINCE_ORDER), key=lambda p: installed[p])
    if "Province not assigned" in installed:
        provinces = ["Province not assigned"] + provinces
    y = list(range(len(provinces)))
    h = 0.38

    fig, ax = plt.subplots(figsize=(8.4, 5.0))
    inst_vals = [installed[p] for p in provinces]
    pipe_vals = [pipeline[p] for p in provinces]
    ax.barh([i + h / 2 for i in y], inst_vals, height=h, color=PALETTE["blue"], label="Installed MVA",
            edgecolor=PALETTE["panel"], linewidth=1.0)
    ax.barh([i - h / 2 for i in y], pipe_vals, height=h, color=PALETTE["yellow"],
            label="Planned additional MVA (under construction + planned)", edgecolor=PALETTE["panel"], linewidth=1.0)
    xmax = max(inst_vals + pipe_vals)
    for i, (a, b) in enumerate(zip(inst_vals, pipe_vals)):
        ax.text(a + xmax * 0.01, i + h / 2, f"{a:,.0f}", va="center", fontsize=8, color=PALETTE["ink"])
        ax.text(b + xmax * 0.01, i - h / 2, f"{b:,.0f}", va="center", fontsize=8, color=PALETTE["muted"])
    ax.set_yticks(y)
    ax.set_yticklabels(provinces)
    ax.set_xlim(0, xmax * 1.12)
    ax.set_xlabel("Transformer capacity, MVA (sum over grid substations)")
    ax.set_title("Grid substation capacity by province", loc="left", fontsize=13, pad=10)
    ax.legend(loc="lower right", fontsize=8.5, frameon=False)
    _style_axis(ax, grid_axis="x")
    fig.subplots_adjust(left=0.24, right=0.97, top=0.90, bottom=0.17)
    save_svg(fig, FIGURE_DIR / f"{figure_id}.svg", figure_id=figure_id,
             source_note="substation_specs.csv from NEA FY 2025/26 Appendix 8 and project tables",
             caveat="installed MVA sums transformer ratings; planned MVA is NEA's listed addition", generated_date=TODAY)
    top = max(PROVINCE_ORDER, key=lambda p: installed.get(p, 0.0))
    low = min((p for p in PROVINCE_ORDER if p in installed), key=lambda p: installed[p])
    return {
        "figure_id": figure_id,
        "title": "Grid substation capacity by province, installed vs planned",
        "path": figure_rel_path(figure_id),
        "source_files": [rel(source)],
        "source_slugs": _slugs(r["source_slug"] for r in rows),
        "target_pages": ["data-substation-inventory"],
        "caption": (f"{top} holds {installed[top]:,.0f} MVA of installed substation capacity against "
                    f"{installed[low]:,.0f} MVA in {low}; planned additions are spread more evenly."),
        "caveat": "Substations without a sourced province are shown separately. Installed MVA is summed nameplate transformer capacity, not firm capacity.",
        "license": "CC-BY 4.0",
        "generator_script": "scripts/build_wiki_figures.py",
        "last_generated": TODAY,
    }


def build_plant_generation_vs_design() -> dict:
    figure_id = "plant_generation_vs_design"
    source = ROOT / "data" / "plant_annual_generation.csv"
    rows = read_csv(source)
    by_plant: dict[str, dict[str, dict[str, str]]] = {}
    for row in rows:
        by_plant.setdefault(row["plant_name"], {})[row["fiscal_year_ad"]] = row
    plants = []
    for name, years in by_plant.items():
        latest = years.get("2025/26")
        prior = years.get("2024/25")
        if not latest or not prior:
            continue
        design = _num(latest["contracted_or_design_gwh"])
        capacity = _num(latest["installed_capacity_mw"]) or 0.0
        if not design or capacity < 14 or latest["ownership_class"] == "thermal":
            continue
        plants.append((name, capacity, design, _num(prior["actual_generation_gwh"]) or 0.0,
                       _num(latest["actual_generation_gwh"]) or 0.0))
    plants.sort(key=lambda p: p[4] / p[2])
    y = list(range(len(plants)))
    h = 0.38
    prior_pct = [p[3] / p[2] * 100 for p in plants]
    latest_pct = [p[4] / p[2] * 100 for p in plants]

    fig, ax = plt.subplots(figsize=(8.4, 6.0))
    ax.barh([i + h / 2 for i in y], prior_pct, height=h, color=PALETTE["cyan"], label="FY 2024/25",
            edgecolor=PALETTE["panel"], linewidth=1.0)
    ax.barh([i - h / 2 for i in y], latest_pct, height=h, color=PALETTE["blue"], label="FY 2025/26",
            edgecolor=PALETTE["panel"], linewidth=1.0)
    ax.axvline(100, color=PALETTE["ink"], linewidth=1, linestyle="--")
    ax.text(100.8, len(plants) - 0.4, "design energy", fontsize=8, color=PALETTE["muted"], va="center")
    for i, p in enumerate(plants):
        ax.text(latest_pct[i] + 1, i - h / 2, f"{p[4]:,.0f} / {p[2]:,.0f} GWh", va="center", fontsize=7.5,
                color=PALETTE["ink"])
    ax.set_yticks(y)
    ax.set_yticklabels([f"{p[0]} ({p[1]:g} MW)" for p in plants])
    ax.set_xlim(0, max(prior_pct + latest_pct + [100]) * 1.28)
    ax.set_xlabel("Actual generation as % of design energy (FY 2025/26 fact-sheet value)")
    ax.set_title("NEA and Upper Tamakoshi plants against design energy", loc="left", fontsize=13, pad=10)
    ax.legend(loc="lower right", fontsize=8.5, frameon=False)
    _style_axis(ax, grid_axis="x")
    fig.subplots_adjust(left=0.30, right=0.97, top=0.92, bottom=0.14)
    save_svg(fig, FIGURE_DIR / f"{figure_id}.svg", figure_id=figure_id,
             source_note="plant_annual_generation.csv from NEA annual reports FY 2024/25 and 2025/26",
             caveat="both years compared with the FY 2025/26 design value; plants of 14 MW or more", generated_date=TODAY)
    return {
        "figure_id": figure_id,
        "title": "NEA plant generation against design energy, FY 2024/25 and 2025/26",
        "path": figure_rel_path(figure_id),
        "source_files": [rel(source)],
        "source_slugs": _slugs(r["source_slug"] for r in rows),
        "target_pages": ["data-plant-annual-generation"],
        "caption": "Labels give FY 2025/26 actual over design GWh. The Kulekhani storage plants fell to about a quarter of design energy in FY 2025/26, while Upper Tamakoshi rose above design.",
        "caveat": "Design energy is printed only in the FY 2025/26 report and is applied to both years. Plants under 14 MW and thermal plants are omitted.",
        "license": "CC-BY 4.0",
        "generator_script": "scripts/build_wiki_figures.py",
        "last_generated": TODAY,
    }


def build_tariff_ppa_ladder() -> dict:
    figure_id = "tariff_ppa_ladder"
    retail_src = ROOT / "data" / "erc_retail_tariffs.csv"
    ppa_src = ROOT / "data" / "ppa_standard_rates.csv"
    retail = {r["tariff_id"]: r for r in read_csv(retail_src)}
    ppa = {r["rate_id"]: r for r in read_csv(ppa_src)}
    retail_items = [
        ("Domestic 5 A, 0-20 units", "dom-1ph-5a-0-20"),
        ("Domestic 5 A, 21-30 units", "dom-1ph-5a-21-30"),
        ("Domestic 5 A, 31-50 units", "dom-1ph-5a-31-50"),
        ("Domestic 5 A, 51-250 units", "dom-1ph-5a-51-100"),
        ("Domestic 5 A, over 250 units", "dom-1ph-5a-251plus"),
        ("Industrial 132 kV ToD, off-peak (wet)", "tod-132-industrial-wet-off-peak"),
        ("Industrial 132 kV ToD, normal", "tod-132-industrial-wet-normal"),
        ("Industrial 132 kV ToD, peak", "tod-132-industrial-wet-peak"),
        ("Public EV charging, 33 kV flat", "33kv-transportation-public-ev"),
        ("Public EV charging, LV flat", "lv-transportation-public-ev"),
    ]
    ppa_items = [
        ("RoR, wet season", "ror-opt1-wet"),
        ("RoR, dry season", "ror-opt1-dry"),
        ("PRoR 4-6 hr, dry peak", "pror-4-6hr-dry-peak"),
        ("Storage, wet (2017, withdrawn)", "storage-wet"),
        ("Storage, dry (2017, withdrawn)", "storage-dry"),
        ("Solar 2024 award, min", "solar-award-2024-min"),
        ("Solar 2024 award, max", "solar-award-2024-max"),
        ("NEA average purchase FY 2025/26", "nea-avg-purchase-fy2025-26"),
    ]
    r_vals = [(label, _num(retail[key]["energy_rate_npr_kwh"])) for label, key in retail_items]
    p_vals = [(label, _num(ppa[key]["rate_npr_kwh"])) for label, key in ppa_items]
    xmax = max(v for _, v in r_vals + p_vals if v is not None) * 1.18

    fig, axes = plt.subplots(1, 2, figsize=(9.2, 5.4), sharex=True, gridspec_kw={"wspace": 0.95})
    for ax, vals, color, title in (
        (axes[0], r_vals, PALETTE["blue"], "What consumers pay (energy charge)"),
        (axes[1], p_vals, PALETTE["green"], "What NEA pays generators"),
    ):
        y = list(range(len(vals)))[::-1]
        ax.barh(y, [v or 0 for _, v in vals], height=0.6, color=color, edgecolor=PALETTE["panel"], linewidth=1.0)
        for yi, (_, v) in zip(y, vals):
            ax.text((v or 0) + xmax * 0.015, yi, f"{v:.2f}", va="center", fontsize=8, color=PALETTE["ink"])
        ax.set_yticks(y)
        ax.set_yticklabels([label for label, _ in vals], fontsize=8)
        ax.set_xlim(0, xmax)
        ax.set_xlabel("NPR per kWh")
        ax.set_title(title, loc="left", fontsize=10.5, pad=8)
        _style_axis(ax, grid_axis="x")
    fig.suptitle("Nepal electricity price ladder: retail tariffs and purchase rates", x=0.01, ha="left",
                 fontsize=13, fontweight="bold", color=PALETTE["ink"])
    fig.subplots_adjust(left=0.26, right=0.97, top=0.86, bottom=0.16)
    save_svg(fig, FIGURE_DIR / f"{figure_id}.svg", figure_id=figure_id,
             source_note="erc_retail_tariffs.csv (ERC order 2078) and ppa_standard_rates.csv (NEA posted rates, 2024 solar LoI)",
             caveat="energy charges only; demand and minimum charges excluded", generated_date=TODAY)
    return {
        "figure_id": figure_id,
        "title": "Retail tariff and power purchase rate ladder",
        "path": figure_rel_path(figure_id),
        "source_files": [rel(retail_src), rel(ppa_src)],
        "source_slugs": _slugs([retail[k]["source_slug"] for _, k in retail_items] + [ppa[k]["source_slug"] for _, k in ppa_items] + ["erc-nea-consumer-tariff-order-2078"]),
        "target_pages": ["data-erc-retail-tariffs", "data-ppa-standard-rates"],
        "caption": "Retail energy charges run from NRs 0 to 11.00/kWh. NEA's posted purchase rates run from NRs 4.80 (wet-season RoR) to 12.40 (withdrawn 2017 storage dry rate), and solar awards cleared at NRs 4.99-5.54.",
        "caveat": "Energy charges only, without demand, minimum or service charges, or taxes. The 51-250 unit bar uses the 51-100 slab, which equals the 101-250 slab. Storage rates are the withdrawn 2017 schedule.",
        "license": "CC-BY 4.0",
        "generator_script": "scripts/build_wiki_figures.py",
        "last_generated": TODAY,
    }


def build_ev_import_surge() -> dict:
    figure_id = "ev_import_surge"
    source = ROOT / "data" / "ev_adoption_and_charging.csv"
    rows = [r for r in read_csv(source) if r["record_type"] == "ev_imports"]
    periods = sorted({r["period"] for r in rows})
    classes = [
        ("Electric cars, jeeps & vans", ("Electric car, jeep & van (HS 8703.80)", "Electric jeep, car & van classed under HS 8702.40.49"), PALETTE["blue"]),
        ("Electric three-wheelers", ("Electric three-wheelers (HS 8703.80.1x)",), PALETTE["yellow"]),
        ("Electric buses & minibuses", ("Electric buses, minibuses & microbuses (HS 8702.40.10-30)",), PALETTE["green"]),
    ]

    def total(period: str, cats: tuple[str, ...], field: str) -> float:
        return sum(_num(r[field]) or 0.0 for r in rows if r["period"] == period and r["category"] in cats)

    fig, axes = plt.subplots(1, 2, figsize=(9.8, 4.8), gridspec_kw={"wspace": 0.3})
    n = len(classes)
    w = 0.26
    x = list(range(len(periods)))
    for ax, field, scale, ylabel in (
        (axes[0], "quantity", 1.0, "Units imported"),
        (axes[1], "value_npr_thousand", 1e6, "Import value, NPR billion"),
    ):
        for j, (label, cats, color) in enumerate(classes):
            vals = [total(p, cats, field) / scale for p in periods]
            xs = [i + (j - (n - 1) / 2) * w for i in x]
            ax.bar(xs, vals, width=w, color=color, label=label, edgecolor=PALETTE["panel"], linewidth=1.0)
            for xi, v in zip(xs, vals):
                ax.text(xi, v, f"{v:,.0f}" if scale == 1.0 else f"{v:.1f}", ha="center", va="bottom",
                        fontsize=6.8, color=PALETTE["ink"])
        ax.set_xticks(x)
        ax.set_xticklabels(periods, fontsize=8.5)
        ax.set_ylabel(ylabel)
        _style_axis(ax)
    axes[0].set_title("Units", loc="left", fontsize=10.5)
    axes[1].set_title("Customs value", loc="left", fontsize=10.5)
    fig.suptitle("Electric vehicle imports by class, FY 2080/81 to 2082/83", x=0.01, ha="left",
                 fontsize=13, fontweight="bold", color=PALETTE["ink"])
    axes[0].legend(ncol=3, loc="upper center", bbox_to_anchor=(1.08, -0.12), fontsize=8.5, frameon=False)
    fig.subplots_adjust(left=0.09, right=0.98, top=0.85, bottom=0.27)
    save_svg(fig, FIGURE_DIR / f"{figure_id}.svg", figure_id=figure_id,
             source_note="ev_adoption_and_charging.csv from Department of Customs foreign trade statistics",
             caveat="HS-code import counts, not registrations; two-wheelers and e-bicycles omitted", generated_date=TODAY)
    cars = [total(p, classes[0][1], "quantity") for p in periods]
    buses = [total(p, classes[2][1], "quantity") for p in periods]
    return {
        "figure_id": figure_id,
        "title": "Electric vehicle imports by class, FY 2080/81 to 2082/83",
        "path": figure_rel_path(figure_id),
        "source_files": [rel(source)],
        "source_slugs": _slugs(r["source_slug"] for r in rows),
        "target_pages": ["data-load-anchors-and-fossil-backbone"],
        "caption": (f"Electric car, jeep and van imports went from {cars[0]:,.0f} to {cars[-1]:,.0f} units, and electric "
                    f"bus imports from {buses[0]:,.0f} to {buses[-1]:,.0f}, while three-wheeler imports rose every year."),
        "caveat": "Customs counts of units imported under the listed HS codes, not vehicle registrations or vehicles in use. The car class combines HS 8703.80 and HS 8702.40.49 rows.",
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
    enriched_figures: dict[str, dict] = {}
    for entry in figures:
        enriched = dict(entry)
        enriched["source_file_hashes"] = source_file_hashes(enriched)
        enriched_figures[entry["figure_id"]] = enriched
    manifest = {
        "version": 1,
        "_doc": "Published wiki figure registry. Figure paths resolve relative to wiki/explorer/.",
        "generated_at": TODAY,
        "default_license": "CC-BY 4.0",
        "figures": enriched_figures,
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
        build_energy_balance_fy2025_26(),
        build_storage_vs_imports_fy2025_26(),
        build_mw_vs_dependable_fy2025_26(),
        build_nea_cost_structure_fy2025_26(),
        build_schedule_slippage(),
        build_contracted_energy_performance(),
        build_nea_system_trajectory(),
        build_substation_province_capacity(),
        build_plant_generation_vs_design(),
        build_tariff_ppa_ladder(),
        build_ev_import_surge(),
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
