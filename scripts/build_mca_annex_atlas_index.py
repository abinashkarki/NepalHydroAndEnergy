from __future__ import annotations

import argparse
import csv
import json
import math
import shutil
import subprocess
from pathlib import Path
from typing import Any

import fitz
import numpy as np
from PIL import Image, ImageDraw, ImageFont


ROOT = Path(os.environ.get("NEPAL_ENERGY_ROOT", Path(__file__).resolve().parent.parent))
PDF_PATH = ROOT / "data" / "raw" / "corridor_tracing" / "mca" / "mca_annex_d1_alignment_maps.pdf"
OUT_DIR = ROOT / "data" / "processed" / "corridor_tracing" / "mca_annex_d1"
THUMB_DIR = OUT_DIR / "thumbnails"
REVIEW_DIR = OUT_DIR / "review_pages"
CONTACT_DIR = OUT_DIR / "contact_sheets"
INDEX_JSON = OUT_DIR / "mca_annex_d1_atlas_index.json"
INDEX_CSV = OUT_DIR / "mca_annex_d1_atlas_index.csv"


def ensure_dirs() -> None:
    for path in (OUT_DIR, THUMB_DIR, REVIEW_DIR, CONTACT_DIR):
        path.mkdir(parents=True, exist_ok=True)


def render_page(page: fitz.Page, dpi: int) -> Image.Image:
    pix = page.get_pixmap(matrix=fitz.Matrix(dpi / 72, dpi / 72), alpha=False)
    image = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
    if image.height > image.width:
        image = image.rotate(-90, expand=True)
    return image


def detect_red_alignment(image: Image.Image) -> dict[str, Any]:
    array = np.asarray(image.convert("RGB"))
    red = array[:, :, 0].astype(int)
    green = array[:, :, 1].astype(int)
    blue = array[:, :, 2].astype(int)
    mask = (red > 130) & (green < 130) & (blue < 130) & ((red - np.maximum(green, blue)) > 35)
    ys, xs = np.where(mask)
    if len(xs) == 0:
        return {
            "red_pixel_count": 0,
            "red_alignment_bbox_px": None,
            "red_alignment_bbox_pct": None,
        }
    bbox = [int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())]
    width, height = image.size
    return {
        "red_pixel_count": int(len(xs)),
        "red_alignment_bbox_px": bbox,
        "red_alignment_bbox_pct": [
            round(bbox[0] / width, 4),
            round(bbox[1] / height, 4),
            round(bbox[2] / width, 4),
            round(bbox[3] / height, 4),
        ],
    }


def detect_route_markers(image: Image.Image) -> int:
    array = np.asarray(image.convert("RGB"))
    red = array[:, :, 0].astype(int)
    green = array[:, :, 1].astype(int)
    blue = array[:, :, 2].astype(int)
    orange_ring = (red > 120) & (green > 65) & (green < 170) & (blue < 120)
    ys, xs = np.where(orange_ring)
    if len(xs) == 0:
        return 0

    # Coarse grid count avoids pulling in scipy/OpenCV just to estimate route point density.
    cell = max(8, min(image.size) // 80)
    occupied = {(int(x // cell), int(y // cell)) for x, y in zip(xs, ys)}
    return len(occupied)


def ocr_thumbnail(image_path: Path) -> str:
    if not shutil.which("tesseract"):
        return ""
    try:
        result = subprocess.run(
            ["tesseract", str(image_path), "stdout", "--psm", "6"],
            check=True,
            capture_output=True,
            text=True,
            timeout=20,
        )
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
        return ""
    text = " ".join(result.stdout.split())
    return text[:500]


def draw_overlay(image: Image.Image, row: dict[str, Any]) -> Image.Image:
    review = image.copy()
    draw = ImageDraw.Draw(review)
    bbox = row.get("red_alignment_bbox_px")
    if bbox:
        draw.rectangle(bbox, outline=(255, 255, 0), width=6)
    draw.rectangle((0, 0, 430, 70), fill=(255, 255, 255))
    draw.text((16, 14), f"Annex D-1 page {row['page']:03d}", fill=(0, 0, 0))
    draw.text((16, 38), f"red_px={row['red_pixel_count']} markers={row['likely_route_marker_cells']}", fill=(0, 0, 0))
    return review


def make_contact_sheet(rows: list[dict[str, Any]], sheet_index: int, cols: int = 4) -> None:
    thumbs = [Image.open(row["thumbnail_path"]).convert("RGB") for row in rows]
    if not thumbs:
        return
    thumb_w, thumb_h = thumbs[0].size
    label_h = 28
    rows_count = math.ceil(len(thumbs) / cols)
    sheet = Image.new("RGB", (cols * thumb_w, rows_count * (thumb_h + label_h)), "white")
    draw = ImageDraw.Draw(sheet)
    for idx, (thumb, row) in enumerate(zip(thumbs, rows)):
        x = (idx % cols) * thumb_w
        y = (idx // cols) * (thumb_h + label_h)
        sheet.paste(thumb, (x, y + label_h))
        label = f"{row['page']:03d} red={row['red_pixel_count']} markers={row['likely_route_marker_cells']}"
        draw.text((x + 8, y + 6), label, fill=(0, 0, 0))
    sheet.save(CONTACT_DIR / f"mca_annex_d1_contact_{sheet_index:02d}.jpg", quality=88)


def build_index(thumb_dpi: int, review_dpi: int, ocr: bool) -> list[dict[str, Any]]:
    ensure_dirs()
    doc = fitz.open(PDF_PATH)
    rows: list[dict[str, Any]] = []
    for page_index, page in enumerate(doc, start=1):
        thumbnail = render_page(page, thumb_dpi)
        thumb_path = THUMB_DIR / f"page-{page_index:03d}.jpg"
        thumbnail.save(thumb_path, quality=86)
        red_meta = detect_red_alignment(thumbnail)
        row = {
            "source_id": "mca_annex_d1_alignment_maps",
            "source_pdf": PDF_PATH.name,
            "page": page_index,
            "thumbnail_path": str(thumb_path.relative_to(ROOT)),
            "review_page_path": "",
            "orientation": "landscape_upright",
            "review_status": "needs_sheet_assignment",
            "likely_route_marker_cells": detect_route_markers(thumbnail),
            "ocr_text": ocr_thumbnail(thumb_path) if ocr else "",
            **red_meta,
        }
        rows.append(row)

    review_pages = sorted(
        {
            1,
            len(rows),
            *(row["page"] for row in sorted(rows, key=lambda item: item["red_pixel_count"], reverse=True)[:16]),
        }
    )
    for page_num in review_pages:
        page = doc[page_num - 1]
        image = render_page(page, review_dpi)
        row = rows[page_num - 1]
        review_path = REVIEW_DIR / f"page-{page_num:03d}.jpg"
        draw_overlay(image, row).save(review_path, quality=90)
        row["review_page_path"] = str(review_path.relative_to(ROOT))

    for sheet_index, start in enumerate(range(0, len(rows), 24), start=1):
        make_contact_sheet(rows[start : start + 24], sheet_index)

    return rows


def write_outputs(rows: list[dict[str, Any]]) -> None:
    INDEX_JSON.write_text(json.dumps(rows, indent=2))
    fieldnames = [
        "source_id",
        "source_pdf",
        "page",
        "thumbnail_path",
        "review_page_path",
        "orientation",
        "review_status",
        "red_pixel_count",
        "red_alignment_bbox_px",
        "red_alignment_bbox_pct",
        "likely_route_marker_cells",
        "ocr_text",
    ]
    with INDEX_CSV.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description="Build a visual index for the MCA Annex D-1 alignment atlas.")
    parser.add_argument("--thumb-dpi", type=int, default=72)
    parser.add_argument("--review-dpi", type=int, default=160)
    parser.add_argument("--no-ocr", action="store_true")
    args = parser.parse_args()

    rows = build_index(args.thumb_dpi, args.review_dpi, ocr=not args.no_ocr)
    write_outputs(rows)
    print(f"Wrote {INDEX_JSON.relative_to(ROOT)} ({len(rows)} pages)")
    print(f"Wrote {INDEX_CSV.relative_to(ROOT)}")
    print(f"Wrote contact sheets under {CONTACT_DIR.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
