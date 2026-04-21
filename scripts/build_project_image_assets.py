#!/usr/bin/env python3
"""Build first-pass image assets for priority Nepal energy project pages.

This script does three things:
1. Generate consistent locator images from the project's existing map anchors.
2. Download a small set of first-party layout images from official project pages.
3. Render selected official PDF figure pages into per-project image folders.

It intentionally focuses on a curated batch of high-value pages rather than
trying to solve every entity page at once.
"""
from __future__ import annotations

import json
import math
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as MplPolygon
from matplotlib.collections import LineCollection
import requests
from PIL import Image, ImageChops


ROOT = Path(__file__).resolve().parent.parent
ASSETS_DIR = ROOT / "wiki" / "assets" / "images"
MAPS_DIR = ROOT / "data" / "processed" / "maps"
TMP_DIR = ROOT / "tmp" / "project_images"


@dataclass(frozen=True)
class OfficialImageSpec:
    kind: str  # "url" or "pdf_page"
    output_name: str
    caption: str
    credit: str
    source_url: str
    url: str | None = None
    pdf_path: str | None = None
    pdf_page: int | None = None


@dataclass(frozen=True)
class ProjectSpec:
    slug: str
    title: str
    candidates: tuple[str, ...]
    zoom_deg: float
    official: OfficialImageSpec | None = None


PROJECTS: tuple[ProjectSpec, ...] = (
    ProjectSpec(
        slug="arun-3",
        title="Arun 3",
        candidates=("Arun 3",),
        zoom_deg=0.23,
    ),
    ProjectSpec(
        slug="upper-karnali",
        title="Upper Karnali",
        candidates=("Upper Karnali",),
        zoom_deg=0.28,
    ),
    ProjectSpec(
        slug="tanahu-hydropower",
        title="Tanahu Hydropower Project",
        candidates=("Tanahu HEP", "Tanahu"),
        zoom_deg=0.18,
    ),
    ProjectSpec(
        slug="dudhkoshi-storage",
        title="Dudhkoshi Storage Hydroelectric Project",
        candidates=("Dudhkoshi Storage HEP", "Dudhkoshi Storage"),
        zoom_deg=0.22,
    ),
    ProjectSpec(
        slug="upper-tamakoshi",
        title="Upper Tamakoshi",
        candidates=("Upper Tamakoshi HPP", "Upper Tamakoshi"),
        zoom_deg=0.18,
    ),
    ProjectSpec(
        slug="kali-gandaki-a",
        title="Kali Gandaki A",
        candidates=("Kali Gandaki A",),
        zoom_deg=0.18,
    ),
    ProjectSpec(
        slug="mugu-karnali-storage-hep",
        title="Mugu Karnali Storage HEP",
        candidates=("Mugu Karnali Storage HEP", "Mugu Karnali Storage"),
        zoom_deg=0.35,
        official=OfficialImageSpec(
            kind="url",
            output_name="official-layout.jpg",
            url="https://www.vucl.org/storage/projects/January2020/Mugu%20karnali%20Layout.jpg",
            caption="Official project layout image published on the VUCL Mugu Karnali Storage HEP page.",
            credit="Vidhyut Utpadan Company Limited (VUCL)",
            source_url="https://www.vucl.org/projects/mugu-karnali-storage-hep",
        ),
    ),
    ProjectSpec(
        slug="phukot-karnali",
        title="Phukot Karnali",
        candidates=("Phukot Karnali", "Phukot Karnali PROR HEP"),
        zoom_deg=0.25,
        official=OfficialImageSpec(
            kind="url",
            output_name="official-layout.jpg",
            url="https://www.vucl.org/source/Layout%20PKHEP.jpg",
            caption="Official project layout image published on the VUCL Phukot Karnali PROR HEP page.",
            credit="Vidhyut Utpadan Company Limited (VUCL)",
            source_url="https://www.vucl.org/projects/phukot-karnali-pror-hep",
        ),
    ),
    ProjectSpec(
        slug="nalsyau-gad-storage-hep",
        title="Nalsyau Gad Storage HEP",
        candidates=("Nalsyau Gad Storage HEP", "Nalsyau Gad"),
        zoom_deg=0.20,
        official=OfficialImageSpec(
            kind="pdf_page",
            output_name="jica-layout-page.png",
            pdf_path="data/raw/lead1_sources/jica_storage_master_plan_vol_2.pdf",
            pdf_page=107,
            caption="Official JICA storage master plan figure page showing Nalsyau Gad location and general layout.",
            credit="JICA / EPDC, Nationwide Master Plan Study on Storage-type Hydroelectric Power Development in Nepal",
            source_url="data/raw/lead1_sources/jica_storage_master_plan_vol_2.pdf",
        ),
    ),
    ProjectSpec(
        slug="naumure-w-rapti",
        title="Naumure (W. Rapti)",
        candidates=("Naumure (W. Rapti)",),
        zoom_deg=0.22,
        official=OfficialImageSpec(
            kind="pdf_page",
            output_name="jica-layout-page.png",
            pdf_path="data/raw/lead1_sources/jica_storage_master_plan_vol_2.pdf",
            pdf_page=110,
            caption="Official JICA storage master plan figure page showing Naumure location and general layout.",
            credit="JICA / EPDC, Nationwide Master Plan Study on Storage-type Hydroelectric Power Development in Nepal",
            source_url="data/raw/lead1_sources/jica_storage_master_plan_vol_2.pdf",
        ),
    ),
    ProjectSpec(
        slug="sun-koshi-no-3",
        title="Sun Koshi No.3",
        candidates=("Sun Koshi No.3",),
        zoom_deg=0.20,
        official=OfficialImageSpec(
            kind="pdf_page",
            output_name="jica-layout-page.png",
            pdf_path="data/raw/lead1_sources/jica_storage_master_plan_vol_2.pdf",
            pdf_page=89,
            caption="Official JICA storage master plan figure page showing Sun Koshi No.3 location and general layout.",
            credit="JICA / EPDC, Nationwide Master Plan Study on Storage-type Hydroelectric Power Development in Nepal",
            source_url="data/raw/lead1_sources/jica_storage_master_plan_vol_2.pdf",
        ),
    ),
    ProjectSpec(
        slug="andhi-khola",
        title="Andhi Khola",
        candidates=("Andhi Khola",),
        zoom_deg=0.18,
    ),
    ProjectSpec(
        slug="lower-badigad",
        title="Lower Badigad",
        candidates=("Lower Badigad",),
        zoom_deg=0.19,
        official=OfficialImageSpec(
            kind="pdf_page",
            output_name="jica-layout-page.png",
            pdf_path="data/raw/lead1_sources/jica_storage_master_plan_vol_2.pdf",
            pdf_page=92,
            caption="Official JICA storage master plan figure page showing Lower Badigad location and general layout.",
            credit="JICA / EPDC, Nationwide Master Plan Study on Storage-type Hydroelectric Power Development in Nepal",
            source_url="data/raw/lead1_sources/jica_storage_master_plan_vol_2.pdf",
        ),
    ),
    ProjectSpec(
        slug="uttarganga-storage-hydropower-project",
        title="Uttarganga Storage Hydropower Project",
        candidates=("Uttarganga Storage Hydropower Project", "Uttar Ganga Storage Hydroelectric Project"),
        zoom_deg=0.20,
    ),
)


def load_geojson(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def feature_name(props: dict[str, Any]) -> str:
    return str(
        props.get("project")
        or props.get("name")
        or props.get("label_title")
        or props.get("title")
        or ""
    ).strip()


def find_project_feature(features: list[dict[str, Any]], candidates: tuple[str, ...]) -> dict[str, Any]:
    lower = {c.lower() for c in candidates}
    for feat in features:
        name = feature_name(feat.get("properties", {})).lower()
        if name in lower:
            return feat
    raise KeyError(f"could not match project candidates: {candidates}")


def _trim_whitespace(path: Path) -> None:
    img = Image.open(path).convert("RGB")
    bg = Image.new("RGB", img.size, "white")
    diff = ImageChops.difference(img, bg)
    bbox = diff.getbbox()
    if not bbox:
        return
    pad = 8
    left = max(bbox[0] - pad, 0)
    top = max(bbox[1] - pad, 0)
    right = min(bbox[2] + pad, img.width)
    bottom = min(bbox[3] + pad, img.height)
    img.crop((left, top, right, bottom)).save(path)


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def download_file(url: str, dest: Path) -> None:
    ensure_dir(dest.parent)
    r = requests.get(url, timeout=60)
    r.raise_for_status()
    dest.write_bytes(r.content)


def render_pdf_page(pdf_path: Path, page: int, dest: Path) -> None:
    ensure_dir(dest.parent)
    prefix = TMP_DIR / f"{pdf_path.stem}_p{page}"
    ensure_dir(prefix.parent)
    subprocess.run(
        [
            "pdftoppm",
            "-f",
            str(page),
            "-l",
            str(page),
            "-png",
            str(pdf_path),
            str(prefix),
        ],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    matches = sorted(prefix.parent.glob(prefix.name + "-*.png"))
    if not matches:
        raise FileNotFoundError(f"no rendered page found for {pdf_path} page {page}")
    rendered = matches[0]
    shutil.copyfile(rendered, dest)
    _trim_whitespace(dest)


def _line_segments(geom: dict[str, Any]) -> list[list[tuple[float, float]]]:
    gtype = geom["type"]
    coords = geom["coordinates"]
    if gtype == "LineString":
        return [[tuple(pt) for pt in coords]]
    if gtype == "MultiLineString":
        return [[[float(x), float(y)] for x, y in line] for line in coords]
    return []


def _polygon_rings(geom: dict[str, Any]) -> list[list[tuple[float, float]]]:
    gtype = geom["type"]
    coords = geom["coordinates"]
    if gtype == "Polygon":
        return [[tuple(pt) for pt in ring] for ring in coords[:1]]
    if gtype == "MultiPolygon":
        out: list[list[tuple[float, float]]] = []
        for poly in coords:
            out.extend([[tuple(pt) for pt in ring] for ring in poly[:1]])
        return out
    return []


def build_locator_image(
    slug: str,
    title: str,
    feature: dict[str, Any],
    rivers: list[dict[str, Any]],
    country_outline: list[dict[str, Any]],
    out_path: Path,
    zoom_deg: float,
) -> None:
    lon, lat = feature["geometry"]["coordinates"]
    river_segments: list[list[tuple[float, float]]] = []
    for river in rivers:
        props = river.get("properties", {})
        bbox = props.get("bbox")
        if bbox:
            minx, miny, maxx, maxy = bbox
            if maxx < lon - zoom_deg or minx > lon + zoom_deg or maxy < lat - zoom_deg or miny > lat + zoom_deg:
                continue
        river_segments.extend(_line_segments(river["geometry"]))

    fig = plt.figure(figsize=(8.2, 5.4), dpi=160, facecolor="#f6f4ef")
    gs = fig.add_gridspec(1, 2, width_ratios=[1.25, 2.75], wspace=0.06)
    ax_inset = fig.add_subplot(gs[0, 0])
    ax_main = fig.add_subplot(gs[0, 1])

    for ax in (ax_inset, ax_main):
        ax.set_facecolor("#f8f6f0")
        ax.spines[:].set_visible(False)
        ax.set_xticks([])
        ax.set_yticks([])

    for ring in country_outline:
        ax_inset.add_patch(
            MplPolygon(
                ring,
                closed=True,
                facecolor="#e6ebdd",
                edgecolor="#8ea184",
                linewidth=0.8,
            )
        )
    ax_inset.scatter([lon], [lat], s=42, color="#c75a2c", edgecolors="white", linewidths=0.8, zorder=5)
    ax_inset.set_xlim(80.0, 88.3)
    ax_inset.set_ylim(26.1, 30.6)
    ax_inset.text(0.03, 0.97, "Nepal", transform=ax_inset.transAxes, va="top", ha="left", fontsize=10, color="#334155")

    if river_segments:
        lc = LineCollection(river_segments, colors="#4f86c6", linewidths=1.1, alpha=0.9)
        ax_main.add_collection(lc)
    ax_main.scatter([lon], [lat], s=110, color="#d95f02", edgecolors="white", linewidths=1.2, zorder=6)
    ax_main.text(
        lon + zoom_deg * 0.03,
        lat + zoom_deg * 0.05,
        title,
        fontsize=11,
        fontweight="bold",
        color="#1f2937",
        bbox={"facecolor": "white", "alpha": 0.85, "edgecolor": "none", "pad": 2.5},
        zorder=7,
    )
    ax_main.set_xlim(lon - zoom_deg, lon + zoom_deg)
    ax_main.set_ylim(lat - zoom_deg * 0.75, lat + zoom_deg * 0.75)
    ax_main.text(
        0.02,
        0.97,
        "Locator crop from verified project anchor",
        transform=ax_main.transAxes,
        va="top",
        ha="left",
        fontsize=9.5,
        color="#475569",
    )
    fig.suptitle(title, x=0.05, y=0.98, ha="left", fontsize=15, fontweight="bold", color="#111827")
    fig.savefig(out_path, bbox_inches="tight")
    plt.close(fig)


def write_manifest(records: list[dict[str, Any]]) -> None:
    out = ROOT / "data" / "processed" / "project_image_manifest.json"
    out.write_text(json.dumps(records, indent=2))


def main() -> None:
    TMP_DIR.mkdir(parents=True, exist_ok=True)
    project_points: list[dict[str, Any]] = []
    for layer in (
        "hydropower_project_display_points.geojson",
        "storage_shortlist_annotations.geojson",
        "priority_project_watchlist.geojson",
        "top_capacity_project_annotations.geojson",
    ):
        data = load_geojson(MAPS_DIR / layer)
        project_points.extend(data["features"])
    rivers_geojson = load_geojson(MAPS_DIR / "nepal_relevant_tributaries.geojson")["features"]
    country_geojson = load_geojson(MAPS_DIR / "nepal_country_outline.geojson")
    country_outline = _polygon_rings(country_geojson["geometry"])

    manifest: list[dict[str, Any]] = []
    for spec in PROJECTS:
        feature = find_project_feature(project_points, spec.candidates)
        slug_dir = ASSETS_DIR / spec.slug
        ensure_dir(slug_dir)

        locator_name = "locator-map.png"
        locator_path = slug_dir / locator_name
        build_locator_image(
            slug=spec.slug,
            title=spec.title,
            feature=feature,
            rivers=rivers_geojson,
            country_outline=country_outline,
            out_path=locator_path,
            zoom_deg=spec.zoom_deg,
        )
        record: dict[str, Any] = {
            "slug": spec.slug,
            "locator": {
                "src": f"{spec.slug}/{locator_name}",
                "caption": f"Locator crop centered on the mapped project anchor for {spec.title}.",
                "credit": "Nepal Energy research workspace",
                "source_url": "data/processed/maps/hydropower_project_display_points.geojson",
            },
        }

        if spec.official:
            official_path = slug_dir / spec.official.output_name
            if spec.official.kind == "url":
                assert spec.official.url
                download_file(spec.official.url, official_path)
            elif spec.official.kind == "pdf_page":
                assert spec.official.pdf_path and spec.official.pdf_page
                render_pdf_page(ROOT / spec.official.pdf_path, spec.official.pdf_page, official_path)
            else:
                raise ValueError(f"unsupported official kind: {spec.official.kind}")
            record["official"] = {
                "src": f"{spec.slug}/{spec.official.output_name}",
                "caption": spec.official.caption,
                "credit": spec.official.credit,
                "source_url": spec.official.source_url,
            }

        manifest.append(record)

    write_manifest(manifest)


if __name__ == "__main__":
    main()
