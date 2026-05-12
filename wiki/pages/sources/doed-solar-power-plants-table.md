---
title: DoED Power Plants: Solar Table
type: source
created: 2026-05-07
updated: 2026-05-07
source_type: registry
source_author: Department of Electricity Development
source_date: 2026-01-09
source_url: https://doed.gov.np/pages/powerplantssolar/
sources: []
tags: [doed, solar, registry, operating, power-plants]
page_quality: record
---

# DoED Power Plants: Solar Table

## Summary

The Department of Electricity Development operating solar power-plant table used as the registry source for mapped operating grid-connected solar plants.

## Data Extracted

- Operating solar plant names
- Owner names
- Capacity
- District
- Display coordinates where available

## Data-Quality Notes

The January 2026 registry snapshot lists 25 operating grid-connected solar plants totaling 141.74 MW. The mapped layer treats DoED coordinates as plant display anchors, not surveyed parcel boundaries. Rows with zero or unusable coordinates are mapped with lower-confidence locality anchors and should not be used for parcel-level siting.

## Limitations

- **Snapshot date:** January 2026 registry snapshot — static point-in-time data. The DoED table is not updated on a fixed schedule; plants commissioned after the snapshot date are not reflected.
- **Coordinate precision:** DoED coordinates are display anchors, not surveyed parcel boundaries. Rows with zero or unusable coordinates are mapped with lower-confidence locality anchors. Not suitable for parcel-level siting analysis.
- **Coverage scope:** Only operating grid-connected plants. Under-construction, proposed, and off-grid solar are excluded.
- **Capacity reporting:** The 141.74 MW total is a registry sum at snapshot date; individual plant capacities may differ from other registries or reporting periods.

## Used By

- [[dhalkebar-solar-1mw]]
- [[raniyapur-block-1]]
- [[dharamnagar-solar]]
- [[chandranigahpur-solar]]
- [[solar-energy-lalitpur]]
- [[ddb-saurya]]
- [[morang-utility-solar]]
- [[bel-chautara-solar]]
- [[pratappur-solar]]
- [[simara-solar]]
- [[dharamnagar-solar-ii]]
- [[banke-block-2]]
- [[dhalkebar-solar-3mw]]
- [[ramgram-solar]]
- [[jira-bhawani-sedawa]]
- [[som-radha-krishna]]
- [[shivasatakshi-jhapa]]

## Related

- [[data-solar-fleet-inventory]]
- [[data-layer-solar-plants-nea-awards]]
- [[nea-solar]]
