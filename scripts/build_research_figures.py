from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
from urllib.request import urlopen


ROOT = Path("/Users/hi/projects/nepalEnergy")
RAW = ROOT / "data" / "raw"
FIGURES = ROOT / "figures"


def set_style() -> None:
    plt.style.use("seaborn-v0_8-whitegrid")
    plt.rcParams.update(
        {
            "figure.dpi": 160,
            "axes.facecolor": "#f6f3ee",
            "figure.facecolor": "#f6f3ee",
            "axes.edgecolor": "#3a3530",
            "axes.labelcolor": "#2e2a26",
            "text.color": "#2e2a26",
            "xtick.color": "#2e2a26",
            "ytick.color": "#2e2a26",
            "grid.color": "#d8cfc3",
            "font.size": 11,
            "axes.titleweight": "bold",
        }
    )


def ensure_nepal_boundary() -> Path:
    target = RAW / "core" / "nepal_boundary.geojson"
    if target.exists():
        return target

    url = "https://raw.githubusercontent.com/johan/world.geo.json/master/countries/NPL.geo.json"
    with urlopen(url, timeout=30) as response:
        target.write_bytes(response.read())
    return target


def load_project_points() -> list[dict]:
    path = RAW / "projects_storage" / "naxa_hydropower_projects.geojson"
    with path.open() as f:
        data = json.load(f)

    rows = []
    for feature in data["features"]:
        props = feature["properties"]
        coords = feature["geometry"]["coordinates"]
        rows.append(
            {
                "license_type": props["license_type"],
                "capacity_mw": float(props["capacity"]),
                "lon": coords[0],
                "lat": coords[1],
            }
        )
    return rows


def plot_trade_shift() -> None:
    years = ["2018", "2023"]
    imports = [2582, 1895]
    exports = [3, 1946]
    net = [i - e for i, e in zip(imports, exports)]
    colors = {"Imports": "#b24c3d", "Exports": "#2e7d5b", "Net": "#3b5874"}

    fig, ax = plt.subplots(figsize=(9.5, 5.5))
    x = range(len(years))
    width = 0.25

    ax.bar([i - width for i in x], imports, width=width, color=colors["Imports"], label="Imports")
    ax.bar(x, exports, width=width, color=colors["Exports"], label="Exports")
    ax.bar([i + width for i in x], net, width=width, color=colors["Net"], label="Net imports")

    for idx, value in enumerate(imports):
        ax.text(idx - width, value + 40, f"{value:,}", ha="center", va="bottom", fontsize=10)
    for idx, value in enumerate(exports):
        ax.text(idx, value + 40, f"{value:,}", ha="center", va="bottom", fontsize=10)
    for idx, value in enumerate(net):
        ax.text(idx + width, value + 40, f"{value:,}", ha="center", va="bottom", fontsize=10)

    ax.axhline(0, color="#3a3530", lw=1)
    ax.set_title("Nepal Electricity Trade Shift: 2018 vs 2023")
    ax.set_ylabel("GWh")
    ax.set_xticks(list(x), years)
    ax.legend(frameon=False, ncols=3, loc="upper right")
    ax.text(
        0.02,
        -0.18,
        "Source: World Bank Nepal Country Economic Memorandum (2025).",
        transform=ax.transAxes,
        fontsize=9,
    )
    fig.tight_layout()
    fig.savefig(FIGURES / "electricity_trade_shift.png", bbox_inches="tight")
    plt.close(fig)


def plot_storage_gap() -> None:
    labels = ["Current\noperational\nstorage hydro", "2032 BAU\nstorage need", "2032 high-\ndemand need"]
    values = [106, 1993, 3154]
    colors = ["#6f7f5a", "#c28e0e", "#b24c3d"]

    fig, ax = plt.subplots(figsize=(8.5, 5.5))
    bars = ax.bar(labels, values, color=colors, width=0.6)
    ax.set_title("Nepal's Storage Gap Is Structural, Not Marginal")
    ax.set_ylabel("MW")
    ax.set_ylim(0, 3500)

    for bar, value in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width() / 2, value + 55, f"{value:,} MW", ha="center", va="bottom")

    ax.text(
        0.02,
        -0.22,
        "Current operational storage hydro is Kulekhani I-III (60 + 32 + 14 MW).\n"
        "Future storage needs from JICA estimates cited in the World Bank Water Sector Diagnostic.",
        transform=ax.transAxes,
        fontsize=9,
    )
    fig.tight_layout()
    fig.savefig(FIGURES / "storage_gap.png", bbox_inches="tight")
    plt.close(fig)


def _iter_boundary_rings(geometry: dict) -> list[list[list[float]]]:
    if geometry["type"] == "Polygon":
        return geometry["coordinates"]
    if geometry["type"] == "MultiPolygon":
        rings = []
        for polygon in geometry["coordinates"]:
            rings.extend(polygon)
        return rings
    raise ValueError(f"Unsupported geometry type: {geometry['type']}")


def plot_license_map() -> None:
    boundary_path = ensure_nepal_boundary()
    with boundary_path.open() as f:
        boundary = json.load(f)

    rows = load_project_points()
    colors = {
        "Survey": "#c28e0e",
        "Generation": "#3b5874",
        "Operation": "#2e7d5b",
    }

    fig, ax = plt.subplots(figsize=(11, 4.8))

    geometry = boundary["features"][0]["geometry"]
    for ring in _iter_boundary_rings(geometry):
        xs = [pt[0] for pt in ring]
        ys = [pt[1] for pt in ring]
        ax.fill(xs, ys, facecolor="#ebe3d5", edgecolor="#3a3530", lw=1.0, zorder=1)

    for license_type, color in colors.items():
        subset = [r for r in rows if r["license_type"] == license_type]
        ax.scatter(
            [r["lon"] for r in subset],
            [r["lat"] for r in subset],
            s=[max(12, (r["capacity_mw"] ** 0.5) * 2.5) for r in subset],
            c=color,
            alpha=0.65,
            label=license_type,
            edgecolors="white",
            linewidths=0.2,
            zorder=2,
        )

    ax.set_title("Hydropower Project Pipeline Clusters Along Nepal's Mountain Arc")
    ax.set_xlabel("Longitude")
    ax.set_ylabel("Latitude")
    ax.legend(frameon=False, ncols=3, loc="lower left")
    ax.text(
        0.01,
        -0.15,
        "Source: public hydropower portal dataset (Naxa/DoED-linked snapshot). Dot size scales with licensed MW.",
        transform=ax.transAxes,
        fontsize=9,
    )
    fig.tight_layout()
    fig.savefig(FIGURES / "hydropower_license_map.png", bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    FIGURES.mkdir(exist_ok=True)
    set_style()
    plot_trade_shift()
    plot_storage_gap()
    plot_license_map()


if __name__ == "__main__":
    main()
