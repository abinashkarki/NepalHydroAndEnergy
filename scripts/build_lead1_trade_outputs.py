#!/usr/bin/env python3

import csv
from pathlib import Path

import matplotlib.pyplot as plt


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

MONTH_ORDER = {month: index + 1 for index, month in enumerate(MONTHS)}
TRADE_CHART_MONTH_COLUMNS = {
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


def read_csv(path: Path) -> list[dict]:
    with path.open(encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def build_trade_chart_long(rows: list[dict]) -> list[dict]:
    long_rows = []
    for row in rows:
        for month in MONTHS:
            long_rows.append(
                {
                    "fiscal_year": row["fiscal_year"],
                    "flow_direction": row["flow_direction"],
                    "bs_month_name": month,
                    "fiscal_month_order": MONTH_ORDER[month],
                    "gwh": f"{float(row[TRADE_CHART_MONTH_COLUMNS[month]]):.4f}",
                    "reported_total_gwh": row["reported_total"],
                    "source_note": row["source_note"],
                }
            )
    return long_rows


def build_fy2081_82_panel(
    trade_chart_rows: list[dict],
    energy_balance_rows: list[dict],
    daily_monthly_rows: list[dict],
) -> list[dict]:
    trade_lookup: dict[tuple[str, str], float] = {}
    for row in trade_chart_rows:
        trade_lookup[(row["flow_direction"], row["bs_month_name"])] = float(row["gwh"])

    energy_lookup: dict[str, dict] = {}
    for row in energy_balance_rows:
        energy_lookup[row["metric"]] = row

    daily_lookup: dict[str, dict] = {}
    for row in daily_monthly_rows:
        if row["fiscal_year"] == "2081_2082":
            daily_lookup[row["bs_month_name"]] = row

    panel_rows = []
    for month in MONTHS:
        daily_row = daily_lookup.get(month, {})
        panel_rows.append(
            {
                "fiscal_year": "2081_2082",
                "bs_month_name": month,
                "fiscal_month_order": MONTH_ORDER[month],
                "import_gwh_trade_chart": f"{trade_lookup.get(('IMPORT_GWh', month), 0.0):.4f}",
                "export_gwh_trade_chart": f"{trade_lookup.get(('EXPORT_GWh', month), 0.0):.4f}",
                "import_gwh_energy_balance": energy_lookup["IMPORT"][month],
                "storage_gwh_energy_balance": energy_lookup["NEA_STORAGE"][month],
                "ror_pror_gwh_energy_balance": energy_lookup["NEA_ROR_PROR"][month],
                "ipp_gwh_energy_balance": energy_lookup["IPP"][month],
                "nea_subsidiary_gwh_energy_balance": energy_lookup["NEA_SUBSIDIARY"][month],
                "system_demand_gwh_energy_balance": energy_lookup["MONTHLY_SYSTEM_ENERGY_DEMAND"][month],
                "daily_import_gwh": (
                    f"{float(daily_row['import_mwh']) / 1000:.3f}" if daily_row else ""
                ),
                "daily_export_gwh": (
                    f"{float(daily_row['export_mwh']) / 1000:.3f}" if daily_row else ""
                ),
                "daily_days_covered": daily_row.get("days_count", ""),
            }
        )
    return panel_rows


def plot_three_year_trade(long_rows: list[dict], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    years = ["2079_80", "2080_81", "2081_82"]
    fig, axes = plt.subplots(2, 1, figsize=(12, 8), sharex=True)
    colors = {
        "2079_80": "#4f6d7a",
        "2080_81": "#dd6e42",
        "2081_82": "#2a9d8f",
    }
    for axis, direction, title in [
        (axes[0], "EXPORT_GWh", "Exports To India By Fiscal Month"),
        (axes[1], "IMPORT_GWh", "Imports From India By Fiscal Month"),
    ]:
        for year in years:
            points = [
                float(row["gwh"])
                for row in long_rows
                if row["flow_direction"] == direction and row["fiscal_year"] == year
            ]
            axis.plot(MONTHS, points, marker="o", linewidth=2, label=year, color=colors[year])
        axis.set_title(title)
        axis.set_ylabel("GWh")
        axis.grid(axis="y", alpha=0.25)
        axis.legend(frameon=False)
    axes[1].tick_params(axis="x", rotation=30)
    fig.suptitle("NEA Monthly Cross-Border Trade Shape, FY 2079/80 To 2081/82")
    fig.tight_layout()
    fig.savefig(output_path, dpi=220, bbox_inches="tight")
    plt.close(fig)


def plot_fy2081_panel(panel_rows: list[dict], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    months = [row["bs_month_name"] for row in panel_rows]
    imports = [float(row["import_gwh_trade_chart"]) for row in panel_rows]
    exports = [float(row["export_gwh_trade_chart"]) for row in panel_rows]
    storage = [float(row["storage_gwh_energy_balance"]) for row in panel_rows]
    daily_imports = [
        float(row["daily_import_gwh"]) if row["daily_import_gwh"] else None for row in panel_rows
    ]

    fig, ax = plt.subplots(figsize=(12, 5.5))
    ax.axvspan(5 - 0.5, 10 - 0.5, color="#f4e6c8", alpha=0.45, label="Dry-import season")
    ax.bar(months, imports, color="#d1495b", alpha=0.75, label="Import (trade chart)")
    ax.bar(months, exports, color="#2a9d8f", alpha=0.75, label="Export (trade chart)")
    ax.plot(months, storage, color="#264653", marker="o", linewidth=2, label="Storage generation")

    daily_points_x = [months[index] for index, value in enumerate(daily_imports) if value is not None]
    daily_points_y = [value for value in daily_imports if value is not None]
    if daily_points_x:
        ax.scatter(
            daily_points_x,
            daily_points_y,
            color="#1d3557",
            s=45,
            zorder=4,
            label="Daily-report aggregate",
        )

    ax.set_title("FY 2081/82 Trade Versus Storage Generation")
    ax.set_ylabel("GWh")
    ax.grid(axis="y", alpha=0.25)
    ax.tick_params(axis="x", rotation=30)
    ax.legend(frameon=False, ncol=2)
    fig.tight_layout()
    fig.savefig(output_path, dpi=220, bbox_inches="tight")
    plt.close(fig)


def main() -> int:
    project_root = Path("/Users/hi/projects/nepalEnergy")
    trade_chart_path = project_root / "data/processed/tables/nea_cross_border_trade_monthly_gwh_fy2079_80_to_2081_82.csv"
    energy_balance_path = project_root / "data/processed/tables/nea_monthly_energy_balance_fy2024_2025.csv"
    daily_monthly_path = project_root / "data/processed/lead1_trade/nea_daily_trade_monthly_aggregated.csv"

    trade_chart_rows = read_csv(trade_chart_path)
    energy_balance_rows = read_csv(energy_balance_path)
    daily_monthly_rows = read_csv(daily_monthly_path) if daily_monthly_path.exists() else []

    long_rows = build_trade_chart_long(trade_chart_rows)
    panel_rows = build_fy2081_82_panel(long_rows, energy_balance_rows, daily_monthly_rows)

    write_csv(
        project_root / "data/processed/lead1_trade/nea_trade_chart_monthly_long.csv",
        long_rows,
        [
            "fiscal_year",
            "flow_direction",
            "bs_month_name",
            "fiscal_month_order",
            "gwh",
            "reported_total_gwh",
            "source_note",
        ],
    )
    write_csv(
        project_root / "data/processed/lead1_trade/lead1_monthly_import_export_storage_fy2081_82.csv",
        panel_rows,
        [
            "fiscal_year",
            "bs_month_name",
            "fiscal_month_order",
            "import_gwh_trade_chart",
            "export_gwh_trade_chart",
            "import_gwh_energy_balance",
            "storage_gwh_energy_balance",
            "ror_pror_gwh_energy_balance",
            "ipp_gwh_energy_balance",
            "nea_subsidiary_gwh_energy_balance",
            "system_demand_gwh_energy_balance",
            "daily_import_gwh",
            "daily_export_gwh",
            "daily_days_covered",
        ],
    )

    plot_three_year_trade(
        long_rows,
        project_root / "figures/lead1_monthly_trade_3year.png",
    )
    plot_fy2081_panel(
        panel_rows,
        project_root / "figures/lead1_fy2081_82_trade_vs_storage.png",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
