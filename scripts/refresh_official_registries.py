#!/usr/bin/env python3
"""One-command quarterly refresh of the official registries and derived outputs.

Modes (mutually exclusive; ``--dry-run`` is the default):

  --dry-run         print the validated step plan and exit (no side effects)
  --offline         run only the local, deterministic enrichers/builders/reports
  --fetch-official  also re-scrape the DoED hydropower and non-hydro registers
                    (30 s network timeout per request) and rebuild the DoED
                    crosswalk/status overlay from the fresh scrape

Steps run in canonical dependency order and stop at the first failure. After a
run, a before/after summary prints row counts and cell fill rates for every
tracked registry so the operator can see exactly what changed.

The single full wiki rebuild (``make wiki-index``, ``make wiki-site``,
``make dashboard-build``, ``make release-check``) is intentionally *not* part of
this script; run it once after reviewing the diff (see
docs/operations/quarterly-refresh-playbook.md).
"""
from __future__ import annotations

import argparse
import csv
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FETCH_TIMEOUT_S = 30


@dataclass(frozen=True)
class Step:
    name: str
    script: str
    args: tuple[str, ...] = ()
    fetch: bool = False
    after: tuple[str, ...] = ()
    outputs: tuple[str, ...] = field(default_factory=tuple)

    def command(self, python: str) -> list[str]:
        return [python, self.script, *self.args]


STEPS: tuple[Step, ...] = (
    Step("doed-hydro-scrape", "scripts/build_doed_hydropower_registry.py", ("--timeout", str(FETCH_TIMEOUT_S)), fetch=True,
         outputs=("data/processed/tables/doed_hydropower_registry.csv",)),
    Step("doed-nonhydro-scrape", "scripts/build_doed_nonhydro_registry.py", ("--timeout", str(FETCH_TIMEOUT_S)), fetch=True,
         outputs=("data/processed/tables/doed_nonhydro_registry.csv",)),
    # The crosswalk/overlay only has new information after a fresh scrape; run without
    # one, it merely re-serialises its outputs (timestamp, line endings, indentation),
    # so it is grouped with the network steps to keep --offline byte-stable.
    Step("doed-status-overlay", "scripts/build_doed_project_status_overlay.py", fetch=True,
         after=("doed-hydro-scrape",), outputs=("data/processed/tables/doed_project_status_overlay.csv", "data/processed/tables/doed_project_crosswalk_review.csv")),
    Step("doed-apply-overlay", "scripts/apply_doed_project_status_overlay.py", fetch=True, after=("doed-status-overlay",),
         outputs=("data/processed/maps/hydropower_project_display_points.geojson",)),
    Step("enrich-solar-specs", "scripts/enrich_solar_specs.py", outputs=("data/solar_project_specs.csv",)),
    Step("canonical-geography", "scripts/enrich_canonical_geography.py",
         outputs=("data/substation_specs.csv", "data/industrial_load_anchors.csv")),
    Step("substation-links", "scripts/build_substation_specs_links.py", after=("enrich-solar-specs", "canonical-geography"),
         outputs=("data/substation_specs.csv",)),
    Step("energy-infrastructure-layers", "scripts/build_energy_infrastructure_layers.py", after=("substation-links",),
         outputs=("data/processed/maps/grid_substations.geojson", "data/processed/maps/industrial_load_anchors.geojson")),
    Step("siting-readiness", "scripts/build_siting_readiness.py", after=("substation-links", "canonical-geography"),
         outputs=("data/clean_industry_siting_index.csv", "data/processed/maps/clean_industry_siting.geojson")),
    Step("explorer-tables", "scripts/build_explorer_tables.py", after=("substation-links", "doed-nonhydro-scrape"),
         outputs=("wiki/explorer/tables/substation_specs.csv",)),
    Step("dataset-catalog", "scripts/build_dataset_catalog.py", after=("siting-readiness", "doed-hydro-scrape", "doed-nonhydro-scrape"),
         outputs=("data/processed/tables/dataset_catalog.json",)),
    Step("hydro-completeness-report", "scripts/report_spec_completeness.py", ("--all",),
         outputs=("data/processed/tables/spec_completeness_report.csv",)),
    Step("solar-completeness-report", "scripts/report_solar_spec_completeness.py", ("--all",), after=("enrich-solar-specs",),
         outputs=("data/processed/tables/solar_spec_completeness_report.csv",)),
)


def plan(fetch_official: bool) -> list[Step]:
    return [s for s in STEPS if fetch_official or not s.fetch]


def validate_plan(steps: tuple[Step, ...] | list[Step] = STEPS) -> list[str]:
    """Return a list of problems: missing scripts, unknown or out-of-order dependencies, duplicate names."""
    problems: list[str] = []
    names = [s.name for s in steps]
    if len(names) != len(set(names)):
        problems.append("duplicate step names")
    position = {name: i for i, name in enumerate(names)}
    for i, step in enumerate(steps):
        if not (ROOT / step.script).exists():
            problems.append(f"{step.name}: missing script {step.script}")
        for dep in step.after:
            if dep not in position:
                problems.append(f"{step.name}: unknown dependency {dep}")
            elif position[dep] >= i:
                problems.append(f"{step.name}: dependency {dep} must run first")
    return problems


def tracked_tables() -> list[Path]:
    paths = sorted((ROOT / "data").glob("*.csv"))
    for rel in ("doed_hydropower_registry.csv", "doed_nonhydro_registry.csv", "doed_project_status_overlay.csv"):
        p = ROOT / "data" / "processed" / "tables" / rel
        if p.exists():
            paths.append(p)
    return paths


def snapshot() -> dict[str, tuple[int, float]]:
    """rel path -> (data rows, % non-empty cells)."""
    out: dict[str, tuple[int, float]] = {}
    for path in tracked_tables():
        with path.open(newline="", encoding="utf-8-sig") as handle:
            reader = csv.reader(handle)
            header = next(reader, [])
            rows = list(reader)
        cells = len(rows) * len(header)
        filled = sum(1 for r in rows for v in r if v.strip())
        out[path.relative_to(ROOT).as_posix()] = (len(rows), round(100 * filled / cells, 1) if cells else 0.0)
    return out


def diff_summary(before: dict[str, tuple[int, float]], after: dict[str, tuple[int, float]]) -> list[str]:
    lines = []
    for key in sorted(set(before) | set(after)):
        b = before.get(key)
        a = after.get(key)
        if b == a:
            continue
        if b is None and a is not None:
            lines.append(f"  + {key}: {a[0]} rows, {a[1]}% filled (new)")
        elif a is None and b is not None:
            lines.append(f"  - {key}: removed (was {b[0]} rows)")
        elif a is not None and b is not None:
            lines.append(f"  ~ {key}: rows {b[0]} -> {a[0]} ({a[0] - b[0]:+d}), filled {b[1]}% -> {a[1]}%")
    return lines


def print_plan(steps: list[Step], python: str) -> None:
    print("Refresh plan (canonical dependency order):")
    for i, step in enumerate(steps, 1):
        tag = " [network]" if step.fetch else ""
        print(f"  {i:2d}. {step.name}{tag}: {' '.join(step.command(python)[1:])}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--dry-run", action="store_true", help="print the plan only (default)")
    mode.add_argument("--offline", action="store_true", help="run local deterministic steps only")
    mode.add_argument("--fetch-official", action="store_true", help="also re-scrape DoED registers (network)")
    parser.add_argument("--python", default=sys.executable, help="interpreter for child steps")
    args = parser.parse_args(argv)

    problems = validate_plan()
    if problems:
        print("FAIL: invalid refresh plan:\n  " + "\n  ".join(problems), file=sys.stderr)
        return 1

    steps = plan(fetch_official=args.fetch_official)
    print_plan(steps, args.python)
    if not (args.offline or args.fetch_official):
        skipped = [s.name for s in STEPS if s.fetch]
        print(f"\nDry run: nothing executed. Official-refresh steps ({', '.join(skipped)}) run only with --fetch-official.")
        return 0

    before = snapshot()
    for i, step in enumerate(steps, 1):
        print(f"\n[{i}/{len(steps)}] {step.name}")
        result = subprocess.run(step.command(args.python), cwd=ROOT, text=True, capture_output=True)
        tail = (result.stdout or "").strip().splitlines()[-3:]
        for line in tail:
            print(f"    {line}")
        if result.returncode != 0:
            print(f"FAIL: step {step.name} exited {result.returncode}", file=sys.stderr)
            if result.stderr.strip():
                print(result.stderr.strip()[-2000:], file=sys.stderr)
            return result.returncode
    after = snapshot()

    print("\nBefore/after registry summary:")
    changes = diff_summary(before, after)
    print("\n".join(changes) if changes else "  no row-count or fill-rate changes")
    print("\nNext: review `git diff`, then run the single full rebuild and release gate (see the quarterly playbook).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
