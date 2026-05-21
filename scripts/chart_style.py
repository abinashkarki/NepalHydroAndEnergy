from __future__ import annotations

import datetime as dt
import textwrap
from pathlib import Path

import matplotlib.pyplot as plt


PALETTE = {
    "blue": "#4477aa",
    "cyan": "#66ccee",
    "green": "#228833",
    "yellow": "#ccbb44",
    "red": "#ee6677",
    "purple": "#aa3377",
    "gray": "#667085",
    "ink": "#25211d",
    "muted": "#6b6259",
    "grid": "#d8d2ca",
    "panel": "#fbfaf7",
}


def apply_chart_style() -> None:
    plt.style.use("seaborn-v0_8-whitegrid")
    plt.rcParams.update(
        {
            "font.family": "sans-serif",
            "font.sans-serif": ["DejaVu Sans", "Arial", "Helvetica", "Liberation Sans", "sans-serif"],
            "mathtext.fontset": "dejavusans",
            "font.size": 10,
            "axes.facecolor": PALETTE["panel"],
            "figure.facecolor": PALETTE["panel"],
            "axes.edgecolor": PALETTE["muted"],
            "axes.labelcolor": PALETTE["ink"],
            "axes.titlecolor": PALETTE["ink"],
            "axes.titleweight": "bold",
            "text.color": PALETTE["ink"],
            "xtick.color": PALETTE["ink"],
            "ytick.color": PALETTE["ink"],
            "grid.color": PALETTE["grid"],
            "grid.linewidth": 0.8,
            "legend.frameon": False,
            "svg.fonttype": "none",
            "figure.dpi": 160,
        }
    )


def add_figure_footer(
    fig,
    *,
    figure_id: str,
    source_note: str,
    caveat: str,
    generated_date: str | None = None,
    license_text: str = "CC-BY 4.0",
) -> None:
    generated = generated_date or dt.date.today().isoformat()
    footer = f"{figure_id} | {source_note} | Caveat: {caveat} | {generated} | {license_text}"
    wrapped = textwrap.fill(footer, width=118)
    fig.text(
        0.01,
        0.01,
        wrapped,
        ha="left",
        va="bottom",
        fontsize=7.0,
        color=PALETTE["muted"],
    )


def save_svg(
    fig,
    path: Path,
    *,
    figure_id: str,
    source_note: str,
    caveat: str,
    generated_date: str | None = None,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    add_figure_footer(
        fig,
        figure_id=figure_id,
        source_note=source_note,
        caveat=caveat,
        generated_date=generated_date,
    )
    fig.savefig(
        path,
        format="svg",
        bbox_inches="tight",
        pad_inches=0.14,
        metadata={
            "Date": generated_date or dt.date.today().isoformat(),
            "Creator": "TransparentGov Nepal Energy Wiki",
            "Rights": "CC-BY 4.0",
            "Description": f"{figure_id}: {source_note}. Caveat: {caveat}",
        },
    )
    path.write_text(
        "\n".join(line.rstrip() for line in path.read_text(encoding="utf-8").splitlines()) + "\n",
        encoding="utf-8",
    )
    plt.close(fig)
