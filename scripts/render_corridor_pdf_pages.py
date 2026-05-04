from __future__ import annotations

import argparse
import csv
import subprocess
from pathlib import Path


ROOT = Path(os.environ.get("NEPAL_ENERGY_ROOT", Path(__file__).resolve().parent.parent))
MANIFEST = ROOT / "data" / "processed" / "corridor_tracing" / "manifests" / "corridor_trace_manifest.csv"
OUTPUT = ROOT / "data" / "processed" / "corridor_tracing" / "rendered_pages"


def render_pages(pdf_path: Path, page_start: int, page_end: int, out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        [
            "pdftoppm",
            "-png",
            "-f",
            str(page_start),
            "-l",
            str(page_end),
            str(pdf_path),
            str(out_dir / "page"),
        ],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--corridor-id", help="Only render one corridor")
    args = parser.parse_args()

    with MANIFEST.open() as handle:
        rows = list(csv.DictReader(handle))

    for row in rows:
        if args.corridor_id and row["corridor_id"] != args.corridor_id:
            continue
        if row["status"] == "missing_local_pdf":
            continue
        if not row["page_start"] or not row["page_end"]:
            continue
        pdf_path = Path(row["source_path"])
        if not pdf_path.exists():
            continue
        out_dir = OUTPUT / row["corridor_id"] / row["source_id"] / row["segment_id"]
        render_pages(pdf_path, int(row["page_start"]), int(row["page_end"]), out_dir)
        print(f"[ok] rendered {row['corridor_id']} {row['source_id']} {row['page_start']}-{row['page_end']} -> {out_dir}")


if __name__ == "__main__":
    main()
