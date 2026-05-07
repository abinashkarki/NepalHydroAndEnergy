#!/usr/bin/env python3
"""Build a sub-daily evening-peak dispatch model for Nepal's 2035 portfolio.

Reads Phase 1 monthly energy totals, applies an hourly diurnal dispatch profile
(RoR flat, reservoir held for evening, solar zero after sunset, BESS 4h window,
demand-shaping peak reduction), and computes residual evening peak MW at 18:30.

Quantifies exactly how many MW Budhigandaki (1,200 MW storage) contributes to
the evening firm capacity requirement.

Usage:
  python scripts/build_diurnal_peak_model.py              # dry-run (default)
  python scripts/build_diurnal_peak_model.py --write       # persist output CSVs
  python scripts/build_diurnal_peak_model.py --peak-ratio 1.2  # override peak/average
"""

from __future__ import annotations

import argparse
import csv
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent

EVENING_PEAK_HOUR = 18.5

BS_DAYS = {"Mangsir": 29, "Poush": 29, "Magh": 29, "Falgun": 30}

MONTH_LABELS = {"Mangsir": "Dec", "Poush": "Jan", "Magh": "Feb", "Falgun": "Mar"}

EVENING_PEAK_WINDOW = (17.0, 21.0)

BESS_WINDOW = (17.5, 21.5)

DEFAULT_DEMAND_SHAPING_PEAK_MW = 400.0


# --------------------------------------------------------------------------- #
#  I/O helpers (matching Phase 1 conventions)                                  #
# --------------------------------------------------------------------------- #

def read_csv(path: Path) -> list[dict]:
    with path.open(encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def _float(v: Any, default: float = 0.0) -> float:
    try:
        return float(v)
    except (TypeError, ValueError):
        return default


# --------------------------------------------------------------------------- #
#  Dataclasses                                                                 #
# --------------------------------------------------------------------------- #

@dataclass
class ScenarioParams:
    scenario_id: str
    label: str
    solar_mwp: float
    storage_mw_active: float
    bess_gwh: float
    demand_shaping_seasonal_gwh: float
    demand_shaping_dec_feb_gwh: float
    post_2035_assumption: bool


@dataclass
class EveningPeakResult:
    scenario_id: str
    label: str
    month: str
    month_gregorian: str
    days: int
    peak_demand_mw: float
    ror_hydro_mw: float
    reservoir_dispatch_mw: float
    solar_mw_at_peak: float
    bess_discharge_mw: float
    demand_shaping_mw: float
    residual_mw: float
    residual_pct_demand: float
    peak_to_average_ratio: float
    reservoir_dispatch_factor: float
    peak_hour: float
    post_2035_assumption: bool


# --------------------------------------------------------------------------- #
#  Interpolation                                                               #
# --------------------------------------------------------------------------- #

def interpolate_to_hourly(data_points: list[tuple[float, float]], target_hours: int = 24) -> list[float]:
    """Linearly interpolate unevenly-spaced (hour, value) pairs to 24 hourly values.

    Assumes the profile repeats daily (wraps from hour 23 to hour 0).
    """
    n = len(data_points)
    result: list[float] = []

    for h in range(target_hours):
        h_float = float(h)
        for i in range(n):
            h0, v0 = data_points[i]
            h1, v1 = data_points[(i + 1) % n]

            if i == n - 1 and h_float >= h0:
                h1 += target_hours

            if h0 <= h_float <= h1 or (i == n - 1 and h_float >= h0):
                if h1 == h0:
                    result.append(v0)
                else:
                    frac = (h_float - h0) / (h1 - h0)
                    result.append(v0 + frac * (v1 - v0))
                break

    return result


def interpolate_at_hour(data_points: list[tuple[float, float]], target_hour: float) -> float:
    """Linearly interpolate unevenly-spaced (hour, value) pairs at one hour."""
    points = sorted(data_points)
    target = target_hour % 24
    n = len(points)

    for i in range(n):
        h0, v0 = points[i]
        h1, v1 = points[(i + 1) % n]
        t = target

        if i == n - 1:
            h1 += 24
            if t < h0:
                t += 24

        if h0 <= t <= h1:
            if h1 == h0:
                return v0
            frac = (t - h0) / (h1 - h0)
            return v0 + frac * (v1 - v0)

    return points[-1][1]


def interpolate_diurnal_profile(rows: list[dict], target_hours: int = 24) -> tuple[list[float], list[float], list[float]]:
    """Interpolate uneven diurnal profile points to hourly arrays.

    Returns (demand_pct, ror_hydro_pct, solar_pct_1gw) each as 24-element lists.
    """
    demand_points = [(float(r["hour"]), float(r["demand_pct_of_peak"])) for r in rows]
    ror_points = [(float(r["hour"]), float(r["ror_hydro_pct_of_peak"])) for r in rows]
    solar_points = [(float(r["hour"]), float(r["solar_pct_of_1gw_clear"])) for r in rows]

    demand_hourly = interpolate_to_hourly(demand_points, target_hours)
    ror_hourly = interpolate_to_hourly(ror_points, target_hours)
    solar_hourly = interpolate_to_hourly(solar_points, target_hours)

    return demand_hourly, ror_hourly, solar_hourly


def compute_peak_to_average_ratio(hourly_demand_pct: list[float]) -> float:
    peak = max(hourly_demand_pct)
    avg = sum(hourly_demand_pct) / len(hourly_demand_pct)
    return peak / avg


def in_window(hour: float, window: tuple[float, float]) -> bool:
    start, end = window
    return start <= hour < end


# --------------------------------------------------------------------------- #
#  Input readers                                                               #
# --------------------------------------------------------------------------- #

def read_monthly_data(path: Path, target_scenarios: set[str], month_filter: str | None = None) -> dict[str, list[dict]]:
    """Read monthly energy balance CSV and extract winter month rows per scenario.

    Returns dict[scenario_id, list of monthly rows for winter months].
    """
    rows = read_csv(path)
    by_scenario: dict[str, list[dict]] = {}
    for row in rows:
        sid = row["scenario_id"]
        if sid not in target_scenarios:
            continue
        month = row["bs_month"]
        if month not in BS_DAYS:
            continue
        if month_filter and month != month_filter:
            continue
        by_scenario.setdefault(sid, []).append(row)
    return by_scenario


def read_scenario_params(path: Path, target_scenarios: set[str]) -> dict[str, ScenarioParams]:
    """Read model_parameters.csv for scenario-level storage and shaping params."""
    rows = read_csv(path)
    params: dict[str, ScenarioParams] = {}
    for row in rows:
        sid = row["scenario_id"]
        if sid not in target_scenarios:
            continue
        seasonal = _float(row.get("demand_shaping_seasonal_gwh", "0"))
        dec_feb = 0.0
        params[sid] = ScenarioParams(
            scenario_id=sid,
            label=row["label"],
            solar_mwp=_float(row.get("solar_mwp", "0")),
            storage_mw_active=_float(row.get("storage_mw_active", "0")),
            bess_gwh=_float(row.get("bess_gwh", "0")),
            demand_shaping_seasonal_gwh=seasonal,
            demand_shaping_dec_feb_gwh=dec_feb,
            post_2035_assumption=row.get("post_2035_assumption", "False").strip().lower() == "true",
        )
    return params


def read_seasonal_summary(path: Path) -> dict[str, float]:
    """Read seasonal_summary.csv to get demand_shaping_dec_feb_gwh per scenario."""
    rows = read_csv(path)
    result: dict[str, float] = {}
    for row in rows:
        result[row["scenario_id"]] = _float(row.get("demand_shaping_dec_feb_gwh", "0"))
    return result


# --------------------------------------------------------------------------- #
#  Dispatch computation                                                        #
# --------------------------------------------------------------------------- #

def compute_evening_peak(
    params: ScenarioParams,
    monthly_rows: list[dict],
    demand_pct_hourly: list[float],
    demand_pct_at_target: float,
    solar_pct_at_target: float,
    peak_to_average_ratio: float,
    args: argparse.Namespace,
) -> list[EveningPeakResult]:
    """Compute evening peak residual for a single scenario across winter months."""
    results: list[EveningPeakResult] = []

    for row in monthly_rows:
        month = row["bs_month"]
        days = BS_DAYS.get(month, 30)
        gregorian = MONTH_LABELS.get(month, month)

        demand_gwh = _float(row["demand_gwh"])
        hydro_ror_gwh = _float(row["hydro_ror_gwh"])

        avg_demand_mw = demand_gwh * 1000 / (days * 24)
        peak_demand_mw = avg_demand_mw * peak_to_average_ratio
        target_demand_mw = peak_demand_mw * (demand_pct_at_target / 100.0)

        ror_hydro_mw = hydro_ror_gwh * 1000 / (days * 24)

        if in_window(args.peak_hour, EVENING_PEAK_WINDOW):
            reservoir_dispatch_mw = params.storage_mw_active * args.reservoir_dispatch_factor
        else:
            reservoir_dispatch_mw = 0.0

        solar_mw_at_peak = params.solar_mwp * (solar_pct_at_target / 100.0)

        # BESS: 2 GWh / 4h = 500 MW. Only active if scenario has BESS.
        if params.bess_gwh > 0 and in_window(args.peak_hour, BESS_WINDOW):
            bess_discharge_mw = args.bess_discharge_mw
        else:
            bess_discharge_mw = 0.0

        # Demand shaping is an explicit peak-MW assumption, activated only for
        # scenarios that include seasonal shaping energy. Do not reuse GWh as MW.
        if params.demand_shaping_dec_feb_gwh > 0 and in_window(args.peak_hour, EVENING_PEAK_WINDOW):
            demand_shaping_mw = args.demand_shaping_peak_mw
        else:
            demand_shaping_mw = 0.0

        residual_mw = (
            target_demand_mw
            - ror_hydro_mw
            - reservoir_dispatch_mw
            - solar_mw_at_peak
            - bess_discharge_mw
            - demand_shaping_mw
        )

        residual_pct = (residual_mw / target_demand_mw * 100) if target_demand_mw > 0 else 0.0

        results.append(EveningPeakResult(
            scenario_id=params.scenario_id,
            label=params.label,
            month=month,
            month_gregorian=gregorian,
            days=days,
            peak_demand_mw=round(target_demand_mw, 0),
            ror_hydro_mw=round(ror_hydro_mw, 0),
            reservoir_dispatch_mw=round(reservoir_dispatch_mw, 0),
            solar_mw_at_peak=round(solar_mw_at_peak, 0),
            bess_discharge_mw=round(bess_discharge_mw, 0),
            demand_shaping_mw=round(demand_shaping_mw, 0),
            residual_mw=round(residual_mw, 0),
            residual_pct_demand=round(residual_pct, 1),
            peak_to_average_ratio=round(peak_to_average_ratio, 3),
            reservoir_dispatch_factor=args.reservoir_dispatch_factor,
            peak_hour=args.peak_hour,
            post_2035_assumption=params.post_2035_assumption,
        ))

    return results


# --------------------------------------------------------------------------- #
#  Main                                                                        #
# --------------------------------------------------------------------------- #

def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    ap.add_argument("--write", action="store_true",
                    help="Actually write output CSVs (default: dry-run)")
    ap.add_argument("--peak-ratio", type=float, default=None,
                    help="Override peak-to-average ratio (default: derived from diurnal profile)")
    ap.add_argument("--peak-hour", type=float, default=EVENING_PEAK_HOUR,
                    help=f"Target peak hour (default: {EVENING_PEAK_HOUR})")
    ap.add_argument("--reservoir-dispatch-factor", type=float, default=0.9,
                    help="Availability factor for reservoir dispatch (default: 0.9)")
    ap.add_argument("--bess-discharge-mw", type=float, default=500.0,
                    help="BESS discharge power in MW (default: 500)")
    ap.add_argument("--demand-shaping-peak-mw", type=float, default=DEFAULT_DEMAND_SHAPING_PEAK_MW,
                    help=f"Peak reduction for scenarios with demand shaping (default: {DEFAULT_DEMAND_SHAPING_PEAK_MW:.0f} MW)")
    ap.add_argument("--month", type=str, default="Magh",
                    choices=list(BS_DAYS.keys()),
                    help="BS month to use as canonical reference (default: Magh≈Feb)")
    args = ap.parse_args()

    target_scenarios = {
        "2035_full", "2035_no_solar", "2035_solar_only",
        "2035_no_budhigandaki", "2035_with_budhigandaki",
    }

    paths = {
        "monthly_balance": ROOT / "data/processed/tables/winter_deficit_model/monthly_energy_balance.csv",
        "model_params": ROOT / "data/processed/tables/winter_deficit_model/model_parameters.csv",
        "seasonal_summary": ROOT / "data/processed/tables/winter_deficit_model/seasonal_summary.csv",
        "hourly_shape": ROOT / "data/winter_deficit_model/hourly_demand_shape.csv",
    }

    for key, p in paths.items():
        if not p.exists():
            print(f"ERROR: missing input file: {p}", file=sys.stderr)
            return 1

    hourly_rows = read_csv(paths["hourly_shape"])
    demand_pct, ror_pct, solar_pct = interpolate_diurnal_profile(hourly_rows)
    demand_points = [(float(r["hour"]), float(r["demand_pct_of_peak"])) for r in hourly_rows]
    solar_points = [(float(r["hour"]), float(r["solar_pct_of_1gw_clear"])) for r in hourly_rows]
    demand_pct_at_target = interpolate_at_hour(demand_points, args.peak_hour)
    solar_pct_at_target = interpolate_at_hour(solar_points, args.peak_hour)

    profile_peak_ratio = compute_peak_to_average_ratio(demand_pct)
    peak_to_average_ratio = args.peak_ratio if args.peak_ratio is not None else profile_peak_ratio

    # Read monthly data for target scenarios, filtered to the canonical month.
    monthly_by_scenario = read_monthly_data(paths["monthly_balance"], target_scenarios, args.month)

    params_by_scenario = read_scenario_params(paths["model_params"], target_scenarios)

    seasonal_shaping = read_seasonal_summary(paths["seasonal_summary"])

    for sid, sp in params_by_scenario.items():
        dec_feb_val = seasonal_shaping.get(sid, 0.0)
        sp.demand_shaping_dec_feb_gwh = dec_feb_val

    header_shown = False
    all_results: list[EveningPeakResult] = []

    ordered_scenarios = [
        "2035_no_solar", "2035_solar_only",
        "2035_full", "2035_no_budhigandaki", "2035_with_budhigandaki",
    ]

    for sid in ordered_scenarios:
        if sid not in params_by_scenario:
            continue
        params = params_by_scenario[sid]
        monthly = monthly_by_scenario.get(sid, [])
        if not monthly:
            print(f"WARN: no monthly data for {sid}", file=sys.stderr)
            continue

        results = compute_evening_peak(
            params, monthly, demand_pct, demand_pct_at_target,
            solar_pct_at_target, peak_to_average_ratio, args,
        )
        all_results.extend(results)

        if not header_shown:
            print(f"\nDiurnal profile: {len(hourly_rows)} timepoints interpolated to 24 hourly values")
            print(f"Profile-implied peak-to-average ratio: {profile_peak_ratio:.3f}")
            if args.peak_ratio is not None:
                print(f"  Overridden by --peak-ratio: {peak_to_average_ratio:.3f}")
            print(f"Canonical month: {args.month} ({MONTH_LABELS[args.month]} approx)")
            print(f"Target hour: {args.peak_hour:.1f}")
            print(f"Demand at target hour: {demand_pct_at_target:.1f}% of profile peak")
            print(f"Solar at target hour: {solar_pct_at_target:.1f}% of 1 GW clear-sky output")
            print(f"Reservoir dispatch factor: {args.reservoir_dispatch_factor}")
            print(f"BESS discharge: {args.bess_discharge_mw:.0f} MW")
            print(f"Demand shaping peak reduction: {args.demand_shaping_peak_mw:.0f} MW")
            print()
            print(f"=== Dispatch Summary ({args.peak_hour:.1f} target hour) ===")
            print(f"{'Scenario':<30} {'DemandMW':>10} {'RoR':>10} {'Reservoir':>10} "
                  f"{'Solar':>8} {'BESS':>8} {'Shaping':>8} {'Residual':>10} {'Resid%':>8}")
            print("-" * 110)
            header_shown = True

        for r in results:
            flag = " *** ASPIRATIONAL (post-2035)" if r.post_2035_assumption else ""
            warn = ""
            if r.residual_pct_demand > 10:
                warn = "  WARN: material evening capacity gap remains"
            print(f"{r.scenario_id:<30} {r.peak_demand_mw:>10.0f} {r.ror_hydro_mw:>10.0f} "
                  f"{r.reservoir_dispatch_mw:>10.0f} {r.solar_mw_at_peak:>8.0f} "
                  f"{r.bess_discharge_mw:>8.0f} {r.demand_shaping_mw:>8.0f} "
                  f"{r.residual_mw:>10.0f} {r.residual_pct_demand:>7.1f}%{flag}{warn}")

    if all_results:
        full_result = None
        budhi_result = None
        for r in all_results:
            if r.scenario_id == "2035_full":
                full_result = r
            if r.scenario_id == "2035_with_budhigandaki":
                budhi_result = r

        if full_result and budhi_result:
            delta = full_result.residual_mw - budhi_result.residual_mw
            delta_pct = full_result.residual_pct_demand - budhi_result.residual_pct_demand
            print()
            print("=== Budhigandaki Evening Firm Capacity Contribution ===")
            print(f"  2035_full residual (excl. Budhi):  {full_result.residual_mw:>8.0f} MW ({full_result.residual_pct_demand}% of peak)")
            print(f"  2035_with_budhigandaki residual:    {budhi_result.residual_mw:>8.0f} MW ({budhi_result.residual_pct_demand}% of peak)")
            print(f"  Budhigandaki shaves:                 {delta:>8.0f} MW ({delta_pct:.1f} pp) off the evening peak")
            print()
            print(f"  Budhigandaki nameplate:              {1200:>8.0f} MW")
            print(f"  At dispatch factor {args.reservoir_dispatch_factor}:          {1200 * args.reservoir_dispatch_factor:>8.0f} MW effective contribution")
            print(f"  Reservoir dispatch delta:            {budhi_result.reservoir_dispatch_mw - full_result.reservoir_dispatch_mw:>8.0f} MW")
            print()

    if args.write:
        out_dir = ROOT / "data/processed/tables/diurnal_peak_model"
        fieldnames = [
            "scenario_id", "label", "month", "month_gregorian", "days",
            "peak_demand_mw", "ror_hydro_mw", "reservoir_dispatch_mw",
            "solar_mw_at_peak", "bess_discharge_mw", "demand_shaping_mw",
            "residual_mw", "residual_pct_demand",
            "peak_to_average_ratio", "reservoir_dispatch_factor", "peak_hour",
            "post_2035_assumption",
        ]
        result_dicts: list[dict] = []
        for r in all_results:
            result_dicts.append({
                "scenario_id": r.scenario_id,
                "label": r.label,
                "month": r.month,
                "month_gregorian": r.month_gregorian,
                "days": r.days,
                "peak_demand_mw": f"{r.peak_demand_mw:.0f}",
                "ror_hydro_mw": f"{r.ror_hydro_mw:.0f}",
                "reservoir_dispatch_mw": f"{r.reservoir_dispatch_mw:.0f}",
                "solar_mw_at_peak": f"{r.solar_mw_at_peak:.0f}",
                "bess_discharge_mw": f"{r.bess_discharge_mw:.0f}",
                "demand_shaping_mw": f"{r.demand_shaping_mw:.0f}",
                "residual_mw": f"{r.residual_mw:.0f}",
                "residual_pct_demand": f"{r.residual_pct_demand:.1f}",
                "peak_to_average_ratio": f"{r.peak_to_average_ratio:.3f}",
                "reservoir_dispatch_factor": f"{r.reservoir_dispatch_factor:.2f}",
                "peak_hour": f"{r.peak_hour:.1f}",
                "post_2035_assumption": str(r.post_2035_assumption),
            })
        write_csv(out_dir / "evening_peak_summary.csv", result_dicts, fieldnames)
        print(f"Wrote {len(result_dicts)} rows → {out_dir / 'evening_peak_summary.csv'}")
    else:
        print(f"\n[dry-run] {len(all_results)} evening peak rows computed across "
              f"{len(params_by_scenario)} scenarios. Rerun with --write to persist.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
