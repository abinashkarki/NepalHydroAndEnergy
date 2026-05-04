from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
from typing import Any

from pypdf import PdfReader


ROOT = Path(os.environ.get("NEPAL_ENERGY_ROOT", Path(__file__).resolve().parent.parent))
RAW = ROOT / "data" / "raw" / "corridor_tracing"
PROCESSED = ROOT / "data" / "processed" / "corridor_tracing" / "manifests"


SOURCE_CATALOG = [
    {
        "source_id": "world_bank_hddtl_rap_2017",
        "title": "World Bank HDDTL RAP",
        "publisher": "World Bank",
        "source_type": "RAP",
        "source_url": "https://documents1.worldbank.org/curated/en/522221483681808545/pdf/IPP476-v2-Box396344B-PUBLIC-disclosed-1-5-17.pdf",
        "local_path": RAW / "world_bank" / "world_bank_hddtl_rap_2017.pdf",
        "rotation_degrees": 0,
        "notes": "Useful for route confirmation and page references, but Figure 1 is a locator map rather than a trace-grade alignment sheet.",
    },
    {
        "source_id": "mca_annex_d1_alignment_maps",
        "title": "MCA Annex D-1 Alignment Maps",
        "publisher": "MCA-Nepal",
        "source_type": "Alignment map sheets",
        "source_url": "https://mcanp.org/Content/GetPdf?filePath=%2FMCANP%2FEIAReports%2FAnnexD_1_Alignment-Maps.pdf&section=EIAReports&guid=90d56f40-0b72-4cb0-9e2b-fa8eeaba72d3",
        "local_path": RAW / "mca" / "mca_annex_d1_alignment_maps.pdf",
        "rotation_degrees": 180,
        "notes": "Primary trace-grade source for the MCA central corridor. OCR is required because the PDF is image-based.",
    },
    {
        "source_id": "mca_volume_8_project_summary",
        "title": "MCA Volume 8 Project Summary Report",
        "publisher": "MCA-Nepal",
        "source_type": "Project summary",
        "source_url": "https://mcanp.org/Content/GetPdf?filePath=%2FMCANP%2FFeasibilityStudiesReports%2FVolume-8-Project-Summary-Report.pdf&section=FeasibilityStudiesReports&guid=02f6a408-fd36-4732-a580-0ae2af8b35ae",
        "local_path": RAW / "mca" / "mca_volume_8_project_summary.pdf",
        "rotation_degrees": 0,
        "notes": "Text-grade source for historical Naubise nomenclature, segment lengths, and substation naming.",
    },
    {
        "source_id": "nea_marsyangdi_route_pdf",
        "title": "NEA Marsyangdi route RAP/SEP PDF",
        "publisher": "NEA",
        "source_type": "Route map PDF",
        "source_url": "https://www.nea.org.np/admin/assets/uploads/supportive_docs/17560727.pdf",
        "local_path": RAW / "nea" / "nea_marsyangdi_route_pdf.pdf",
        "rotation_degrees": 0,
        "notes": "Primary target source for route-faithful tracing of the Udipur-Markichowk-Bharatpur line when a stable local copy is available.",
    },
    {
        "source_id": "nea_kabeli_iee_volume_iiia",
        "title": "NEA Kabeli Corridor IEE Volume IIIA",
        "publisher": "NEA",
        "source_type": "IEE / route map PDF",
        "source_url": "https://www.nea.org.np/admin/assets/uploads/supportive_docs/1657536461_Volume%20IIIA%20--%20EIB-W2.pdf",
        "local_path": RAW / "nea" / "nea_kabeli_iee_volume_iiia.pdf",
        "rotation_degrees": 0,
        "notes": "Expected trace-grade source for Godak-Amarpur-Soyak / Kabeli routing once fetched successfully.",
    },
]


MANIFEST_ROWS = [
    {
        "corridor_id": "hddi_400",
        "corridor_name": "Hetauda-Dhalkebar-Inaruwa 400 kV backbone",
        "source_id": "world_bank_hddtl_rap_2017",
        "source_priority": "high",
        "segment_scope": "Full corridor",
        "page_targets": "16,18",
        "figure_targets": "Figure 1 on page 16; transmission route text on page 18",
        "role": "route confirmation",
        "trace_grade": "support_only",
        "notes": "Use for official route description and district/VDC coverage, not for detailed digitization.",
    },
    {
        "corridor_id": "hddi_400",
        "corridor_name": "Hetauda-Dhalkebar-Inaruwa 400 kV backbone",
        "source_id": "mca_annex_d1_alignment_maps",
        "source_priority": "high",
        "segment_scope": "Target sheet range to be identified via OCR index",
        "page_targets": "",
        "figure_targets": "",
        "role": "trace geometry",
        "trace_grade": "expected_high",
        "notes": "This is the most likely trace-grade packet if the HDDTL alignment appears in the annex set; sheet range should be resolved via OCR index or manual review.",
    },
    {
        "corridor_id": "mca_central_400",
        "corridor_name": "Lapsiphedi-Ratmate-Hetauda-Damauli-Butwal 400 kV central corridor",
        "source_id": "mca_volume_8_project_summary",
        "source_priority": "high",
        "segment_scope": "Historical planning nomenclature and segment lengths",
        "page_targets": "5,7,12",
        "figure_targets": "Project list on page 5; segment length list on page 7; alignment/naming references around page 12",
        "role": "nomenclature and segment metadata",
        "trace_grade": "support_only",
        "notes": "This source uses Naubise / New Damauli terminology and should be treated as historical naming support, not the final geometry source.",
    },
    {
        "corridor_id": "mca_central_400",
        "corridor_name": "Lapsiphedi-Ratmate-Hetauda-Damauli-Butwal 400 kV central corridor",
        "source_id": "mca_annex_d1_alignment_maps",
        "source_priority": "very_high",
        "segment_scope": "Lapsiphedi-Ratmate-Hetauda-Damauli-Butwal",
        "page_targets": "",
        "figure_targets": "",
        "role": "trace geometry",
        "trace_grade": "trace_primary",
        "notes": "Primary trace-grade source. Current hub name is Ratmate; earlier feasibility sources refer to Naubise.",
    },
    {
        "corridor_id": "marsyangdi_220",
        "corridor_name": "Udipur-Markichowk-Bharatpur / Marsyangdi corridor 220 kV",
        "source_id": "nea_marsyangdi_route_pdf",
        "source_priority": "very_high",
        "segment_scope": "Udipur-Markichowk-Bharatpur",
        "page_targets": "",
        "figure_targets": "",
        "role": "trace geometry",
        "trace_grade": "trace_primary",
        "notes": "Fetch pending from NEA. Once available, this should become the primary route source.",
    },
    {
        "corridor_id": "kabeli_132",
        "corridor_name": "Kabeli / Godak-Amarpur-Soyak 132 kV corridor",
        "source_id": "nea_kabeli_iee_volume_iiia",
        "source_priority": "very_high",
        "segment_scope": "Sabitra Chowk-Lakhanpur-Soyak split to Godak and Amarpur",
        "page_targets": "",
        "figure_targets": "",
        "role": "trace geometry",
        "trace_grade": "trace_primary",
        "notes": "Fetch pending from NEA. Use source figures once stable local access is available.",
    },
]


def sha256_file(path: Path) -> str | None:
    if not path.exists():
        return None
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def pdf_page_count(path: Path) -> int | None:
    if not path.exists():
        return None
    return len(PdfReader(str(path)).pages)


def build_source_catalog() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for source in SOURCE_CATALOG:
        local_path = Path(source["local_path"])
        exists = local_path.exists()
        rows.append(
            {
                **source,
                "local_path": str(local_path),
                "local_exists": exists,
                "page_count": pdf_page_count(local_path) if exists else None,
                "sha256": sha256_file(local_path) if exists else None,
            }
        )
    return rows


def build_manifest_rows(source_catalog: list[dict[str, Any]]) -> list[dict[str, Any]]:
    lookup = {row["source_id"]: row for row in source_catalog}
    rows: list[dict[str, Any]] = []
    for row in MANIFEST_ROWS:
        source = lookup[row["source_id"]]
        rows.append(
            {
                **row,
                "source_url": source["source_url"],
                "local_path": source["local_path"],
                "local_exists": source["local_exists"],
                "page_count": source["page_count"],
                "rotation_degrees": source["rotation_degrees"],
            }
        )
    return rows


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("")
        return
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    PROCESSED.mkdir(parents=True, exist_ok=True)
    source_catalog = build_source_catalog()
    manifest_rows = build_manifest_rows(source_catalog)

    (PROCESSED / "source_catalog.json").write_text(json.dumps(source_catalog, indent=2))
    (PROCESSED / "corridor_source_manifest.json").write_text(json.dumps(manifest_rows, indent=2))
    write_csv(PROCESSED / "corridor_source_manifest.csv", manifest_rows)

    summary = {
        "source_count": len(source_catalog),
        "local_source_count": sum(1 for row in source_catalog if row["local_exists"]),
        "manifest_row_count": len(manifest_rows),
        "unresolved_sources": [row["source_id"] for row in source_catalog if not row["local_exists"]],
    }
    (PROCESSED / "corridor_source_manifest_summary.json").write_text(json.dumps(summary, indent=2))
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
