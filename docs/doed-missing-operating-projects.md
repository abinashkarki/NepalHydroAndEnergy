# DoED operating projects missing from the local registry

`scripts/build_doed_missing_operating_projects.py` turns unmatched official
operating records from the DoED crosswalk review queue into two deliberately
separate artifacts:

- `data/processed/tables/doed_operating_projects_missing_local.csv` preserves
  every unmatched operating record, including records without usable coordinates.
- `data/processed/maps/doed_operating_projects_missing_local.geojson` contains
  only records for which DoED publishes a usable licence-coordinate envelope.

The GeoJSON is an **official-additions layer**, not an extension of the legacy
Naxa registry. It must remain separately attributable until a project identity
review supports a merge.

The public explorer exposes it as the opt-in
`doed_operating_reference_midpoints` layer. It is off in every preset, and its
layer label, tooltips, and popups identify the points as reference midpoints,
not facility locations. Records without usable coordinates are not mapped.

## Coordinate contract

DoED publishes two latitude and two longitude values for these records. The
generated point is their arithmetic midpoint. It is a licence-envelope reference
for discovery and map orientation, not an asserted dam, intake, powerhouse, or
other facility location. Records containing only zero coordinates remain in the
CSV and summary but are omitted from the mapped GeoJSON.

## Build order

Run the normalized DoED registry and project crosswalk first, then:

```bash
python scripts/build_doed_missing_operating_projects.py
```

The summary records the total missing operating records, mapped reference
midpoints, and records without usable coordinates.
