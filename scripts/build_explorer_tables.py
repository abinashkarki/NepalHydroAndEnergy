#!/usr/bin/env python3
"""Copy the Explorer Data Tables CSVs into the deployable ``wiki/explorer/tables/``.

Production serves only ``wiki/`` and ``data/processed/maps/``, so the registry
CSVs the Data Tables view reads must ship under ``wiki/``.  The copies are
byte-identical to their curated sources; ``--check`` fails on any drift.
The Explorer fetches these files only when a user opens the Tables view.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "wiki" / "explorer" / "tables"

TABLES = {
    "substation_specs.csv": "data/substation_specs.csv",
    "project_specs.csv": "data/project_specs.csv",
    "erc_retail_tariffs.csv": "data/erc_retail_tariffs.csv",
    "doed_nonhydro_registry.csv": "data/processed/tables/doed_nonhydro_registry.csv",
    "industrial_load_anchors.csv": "data/industrial_load_anchors.csv",
    "energy_institutions.csv": "data/energy_institutions.csv",
}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="fail if any copy differs from its source")
    args = parser.parse_args(argv)

    stale: list[str] = []
    for name, rel in TABLES.items():
        source = (ROOT / rel).read_bytes()
        target = OUT_DIR / name
        if args.check:
            if not target.exists() or target.read_bytes() != source:
                stale.append(target.relative_to(ROOT).as_posix())
            continue
        OUT_DIR.mkdir(parents=True, exist_ok=True)
        if not target.exists() or target.read_bytes() != source:
            target.write_bytes(source)
    extra = sorted(p.name for p in OUT_DIR.glob("*.csv") if p.name not in TABLES) if OUT_DIR.exists() else []
    if args.check:
        if stale or extra:
            print("FAIL: explorer tables stale (run scripts/build_explorer_tables.py): " + ", ".join(stale + extra), file=sys.stderr)
            return 1
        print(f"OK: {len(TABLES)} explorer tables match their sources")
        return 0
    for name in extra:
        (OUT_DIR / name).unlink()
    print(f"wrote {len(TABLES)} explorer tables to {OUT_DIR.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
