#!/usr/bin/env python3
"""Build explorer metadata for governed claim cards."""

from __future__ import annotations

import json
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = ROOT / "data" / "claim_registry.yaml"
OUTPUT_PATH = ROOT / "wiki" / "explorer" / "shared" / "claim-governance.json"


def metric_label(metric_id: str) -> str:
    explicit = {
        "aepc_distributed_solar_base": "AEPC distributed solar base",
        "conversion_thesis_portfolio": "Conversion thesis",
        "cross_border_transfer_capacity": "Cross-border transfer capacity",
        "doed_operating_registry_apr_2026": "DoED operating registry",
        "dry_season_hydro_floor_current": "Dry-season hydro floor",
        "fleet_pror_share": "PRoR fleet share",
        "fleet_ror_share": "RoR fleet share",
        "fleet_storage_share": "Storage fleet share",
        "floating_pv_candidate_count": "Floating PV candidate count",
        "governance_financial_squeeze": "Governance financial squeeze",
        "governance_institutional_conflict": "Institutional conflict",
        "grid_electricity_share_final_energy": "Grid electricity share of final energy",
        "hkh_glacier_decline_1990_2020": "HKH glacier decline",
        "india_market_corridor_roles": "India market/corridor roles",
        "india_project_export_approval": "India project export approval",
        "karnali_climate_seasonal_band": "Karnali climate seasonal band",
        "kulekhani_storage_anchor": "Kulekhani storage anchor",
        "monsoon_export_surplus_current": "Monsoon export surplus",
        "monsoon_peak_production_current": "Monsoon peak production",
        "nea_hydro_capacity_fy2024_25": "NEA hydro capacity",
        "nea_total_capacity_fy2024_25": "NEA total capacity",
        "pror_daily_peaking_window": "PRoR daily peaking window",
        "seasonal_storage_requirement": "Seasonal storage requirement",
        "solar_2035_pipeline_mwp": "Solar pipeline to 2035",
        "solar_960mw_tender_tariff_band": "960 MW solar tender tariff band",
        "solar_short_cycle_window": "Solar short-cycle window",
    }
    if metric_id in explicit:
        return explicit[metric_id]
    replacements = {
        "aepc": "AEPC",
        "bess": "BESS",
        "doed": "DoED",
        "fy": "FY",
        "hkh": "HKH",
        "km3": "km³",
        "kulekhani": "Kulekhani",
        "mw": "MW",
        "mwp": "MWp",
        "nea": "NEA",
        "npr": "NPR",
        "ppa": "PPA",
        "pror": "PRoR",
        "pv": "PV",
        "ror": "RoR",
    }
    words = []
    for raw in metric_id.split("_"):
        if raw in replacements:
            words.append(replacements[raw])
        elif raw.isdigit():
            words.append(raw)
        else:
            words.append(raw.capitalize())
    return " ".join(words)


def metric_value(metric: dict) -> str:
    values = [str(v) for v in metric.get("canonical_text") or []]
    if not values:
        return ""
    return "; ".join(values)


def build_payload(registry: dict) -> dict:
    metrics = registry.get("metrics") or {}
    claims = registry.get("claims") or {}
    by_slug = {}
    for claim_id, claim in claims.items():
        slug = claim.get("slug")
        if not slug:
            continue
        depends_on = claim.get("depends_on") or []
        rows = []
        for metric_id in depends_on:
            metric = metrics.get(metric_id) or {}
            rows.append(
                {
                    "id": metric_id,
                    "name": metric.get("label") or metric_label(metric_id),
                    "value": metric_value(metric),
                    "source_slug": metric.get("source_slug") or "",
                }
            )
        by_slug[slug] = {
            "claim_id": str(claim_id),
            "tier": claim.get("tier") or "",
            "metrics": rows,
        }
    return {
        "generated_from": "data/claim_registry.yaml",
        "bySlug": dict(sorted(by_slug.items())),
    }


def main() -> None:
    registry = yaml.safe_load(REGISTRY_PATH.read_text(encoding="utf-8")) or {}
    payload = build_payload(registry)
    OUTPUT_PATH.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"wrote {OUTPUT_PATH.relative_to(ROOT)} ({len(payload['bySlug'])} governed claims)")


if __name__ == "__main__":
    main()
