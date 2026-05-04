from __future__ import annotations

import argparse
import json
import shutil
import subprocess
from pathlib import Path
from typing import Any

from pypdf import PdfReader


ROOT = Path(os.environ.get("NEPAL_ENERGY_ROOT", Path(__file__).resolve().parent.parent))
RAW = ROOT / "data" / "raw"
PROCESSED = ROOT / "data" / "processed" / "corridor_tracing" / "manifests"
TMP = ROOT / "tmp" / "pdfs"

PDF_SOURCES = {
    "mca_annex_d1_alignment_maps": RAW / "corridor_tracing" / "mca" / "mca_annex_d1_alignment_maps.pdf",
    "world_bank_hddtl_rap": RAW / "corridor_tracing" / "world_bank" / "world_bank_hddtl_rap.pdf",
    "mca_project_summary_report": RAW / "corridor_tracing" / "mca" / "mca_project_summary_report.pdf",
    "moewri_ipsdp_exec_summary_2025": RAW / "corridor_tracing" / "moewri" / "moewri_ipsdp_exec_summary_2025.pdf",
    "adb_sasec_operational_plan_update": RAW / "corridor_tracing" / "adb_sasec_operational_plan_update.pdf",
    "jica_ipsdp_report_part2": RAW / "corridor_tracing" / "jica" / "jica_ipsdp_report_part2.pdf",
    "jica_ipsdp_main_report_vol2": RAW / "corridor_tracing" / "jica" / "jica_ipsdp_main_report_vol2.pdf",
    "rpgcl_transmission_network_map_revised1": RAW / "corridor_tracing" / "rpgcl" / "nepal_transmission_network_map_revised1.pdf",
    "nea_annual_report_2024_2025": RAW / "projects_storage" / "nea_annual_report_2024_2025.pdf",
    "nea_transmission_annual_book_2077": RAW / "corridor_tracing" / "nea" / "nea_transmission_annual_book_2077.pdf",
    "nea_marsyangdi_rap": RAW / "corridor_tracing" / "nea" / "nea_marsyangdi_rap.pdf",
    "nea_marsyangdi_rap_upper": RAW / "corridor_tracing" / "nea" / "nea_marsyangdi_rap_upper.pdf",
    "nea_kabeli_iee": RAW / "corridor_tracing" / "nea" / "nea_kabeli_iee.pdf",
    "nea_kabeli_smef": RAW / "corridor_tracing" / "nea" / "nea_kabeli_smef.pdf",
    "eib_marsyangdi_cia": RAW / "corridor_tracing" / "nea" / "eib_marsyangdi_cia.pdf",
}


def run_ocr(pdf_path: Path, page_num: int, source_id: str) -> str:
    page_dir = TMP / source_id
    page_dir.mkdir(parents=True, exist_ok=True)
    prefix = page_dir / f"page_{page_num:03d}"
    png_path = page_dir / f"page_{page_num:03d}-1.png"
    subprocess.run(
        [
            "pdftoppm",
            "-png",
            "-f",
            str(page_num),
            "-l",
            str(page_num),
            str(pdf_path),
            str(prefix),
        ],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    result = subprocess.run(
        ["tesseract", str(png_path), "stdout"],
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def build_index(source_id: str, force_ocr: bool) -> list[dict[str, Any]]:
    pdf_path = PDF_SOURCES[source_id]
    reader = PdfReader(str(pdf_path))
    rows: list[dict[str, Any]] = []
    for page_num, page in enumerate(reader.pages, start=1):
        try:
            text = (page.extract_text() or "").strip()
        except Exception:
            text = ""
        method = "pypdf" if text else "none"
        if (force_ocr or not text) and shutil.which("tesseract") and shutil.which("pdftoppm"):
            try:
                ocr_text = run_ocr(pdf_path, page_num, source_id)
            except subprocess.CalledProcessError:
                ocr_text = ""
            if ocr_text:
                text = ocr_text
                method = "ocr"
        rows.append(
            {
                "source_id": source_id,
                "page": page_num,
                "text_method": method,
                "text_length": len(text),
                "text": text,
            }
        )
    return rows


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-id", choices=sorted(PDF_SOURCES.keys()), help="Single source to index")
    parser.add_argument("--all", action="store_true", help="Index all configured sources")
    parser.add_argument("--force-ocr", action="store_true", help="Run OCR even when pypdf text exists")
    args = parser.parse_args()

    source_ids = [args.source_id] if args.source_id else []
    if args.all:
        source_ids = sorted(PDF_SOURCES.keys())
    if not source_ids:
        parser.error("Use --source-id or --all")

    PROCESSED.mkdir(parents=True, exist_ok=True)
    for source_id in source_ids:
        rows = build_index(source_id, force_ocr=args.force_ocr)
        out_path = PROCESSED / f"{source_id}_page_index.json"
        out_path.write_text(json.dumps(rows, indent=2))
        print(f"[ok] indexed {source_id}: {len(rows)} pages -> {out_path}")


if __name__ == "__main__":
    main()
