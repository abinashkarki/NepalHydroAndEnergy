from scripts.build_tributary_maps import (
    _capacity_authority_fields,
    hydropower_display_points_geojson,
)


def test_large_exact_official_capacity_conflict_preserves_both_values():
    fields = _capacity_authority_fields(
        420,
        {
            "doed_match_status": "exact",
            "doed_match_confidence": "high",
            "doed_capacity_mw": 81,
        },
        True,
    )

    assert fields["legacy_capacity_mw"] == 420
    assert fields["current_official_capacity_mw"] == 81
    assert fields["capacity_difference_mw"] == 339
    assert fields["capacity_mw_basis"] == "legacy_snapshot_preserved"
    assert fields["capacity_reconciliation"] == "dual_value_material_conflict"


def test_capacity_authority_fields_rejects_unreviewed_or_small_differences():
    assert not _capacity_authority_fields(
        100,
        {
            "doed_match_status": "suggested",
            "doed_match_confidence": "medium",
            "doed_capacity_mw": 200,
        },
        True,
    )
    assert not _capacity_authority_fields(
        100,
        {
            "doed_match_status": "exact",
            "doed_match_confidence": "high",
            "doed_capacity_mw": 109.9,
        },
        True,
    )


def test_reviewed_ten_mw_conflict_is_material():
    fields = _capacity_authority_fields(
        22,
        {
            "doed_match_status": "exact",
            "doed_match_confidence": "high",
            "doed_capacity_mw": 32,
        },
        True,
    )

    assert fields["legacy_capacity_mw"] == 22
    assert fields["current_official_capacity_mw"] == 32
    assert fields["capacity_difference_mw"] == 10


def test_capacity_authority_fields_requires_explicit_review_decision():
    assert not _capacity_authority_fields(
        420,
        {
            "doed_match_status": "exact",
            "doed_match_confidence": "high",
            "doed_capacity_mw": 81,
        },
    )


def test_display_points_publish_approved_dual_value_fields():
    project = {
        "project": "Bagmati Nadi",
        "license_type": "Operation",
        "capacity_mw": 22,
        "river": "Bagmati",
        "district": "Makwanpur",
        "municipality": None,
        "province": "Bagmati",
        "precision_tier": "source_exact",
        "precision_label": "Source exact",
        "location_basis": "Registry point",
        "map_match_basis": None,
        "nearest_river_distance_m": None,
        "display_offset_m": 0,
        "raw_lat": 27.4,
        "raw_lon": 85.2,
        "display_lat": 27.4,
        "display_lon": 85.2,
        "legacy_capacity_mw": 22,
        "legacy_capacity_source": "Naxa registry snapshot",
        "current_official_capacity_mw": 32,
        "current_official_capacity_source": "Department of Electricity Development",
        "capacity_difference_mw": 10,
        "capacity_reconciliation": "dual_value_material_conflict",
        "capacity_mw_basis": "legacy_snapshot_preserved",
    }

    props = hydropower_display_points_geojson([project])["features"][0]["properties"]

    assert props["capacity_mw"] == 22
    assert props["legacy_capacity_mw"] == 22
    assert props["current_official_capacity_mw"] == 32
    assert props["capacity_reconciliation"] == "dual_value_material_conflict"
