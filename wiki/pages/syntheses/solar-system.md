---
title: Solar in Nepal's Electricity System
type: synthesis
created: 2026-07-19
updated: 2026-07-20
reviewed: 2026-07-20
review_due: 2026-10-20
as_of: 2026-01-09
sources: [nea-annual-report-fy2024-25, doed-solar-power-plants-table, nea-solar-loi-2024, wb-esmap-solar-resource-assessment, nepal-ndc-3-2025]
tags: [solar, pv, winter, pipeline, registry]
excerpt: The operating solar baseline, award-only pipeline evidence and the role solar can play alongside seasonal hydropower.
caveat: NEA award records do not verify construction or operation; output and precise geography remain sparse for much of the inventory.
maturity: verified-core
page_quality: flagship
---

# Solar in Nepal's Electricity System

## Verified baseline

NEA reports **141.940 MW of installed solar** in FY2024/25. The wiki's DoED-derived solar registry contains 25 records marked operating, totalling **141.74 MW** as of the source-table update. The small difference reflects source and compilation boundaries and should not be silently reconciled.

## Award records are not operating projects

The separate NEA solar procurement dataset contains 63 letter-of-intent award records totalling **960 MW**. Awarded tariffs range from **NPR 4.99 to 5.54/kWh**, with a capacity-weighted average of about **NPR 5.43/kWh**. These records establish an award event and its stated price. They do not by themselves establish PPA execution, financing, construction, final tariff or operation. This wiki therefore labels the cohort **award-only / delivery status unknown**, rather than calling all 960 MW a current construction pipeline. See [[nea-solar-loi-2024]].

## System role

Solar's dry-season daytime profile can complement weak winter hydropower. It cannot by itself supply the evening peak, replace seasonal water storage or bypass grid constraints. Its system value depends on siting, connection capacity, storage or flexible demand, and verified delivery.

The World Bank ESMAP source record reviewed for this wiki describes a 2015–2019 measurement programme with 14 solar stations and 10-minute and hourly observations. That evidence supports spatial and seasonal resource analysis, not a claim that a particular parcel is developable or that a project will achieve modelled output. See [[wb-esmap-solar-resource-assessment]] and [[solar-resource-geography-nepal]].

## Current data model

Solar records distinguish:

- evidence kind: operating registry or procurement award;
- delivery status and the evidence that supports it;
- DC/AC capacity basis where known;
- source date and verification date;
- geography and coordinate precision;
- expected output and its estimation basis;
- explicit missing-field notes.

Coverage is scored separately for lifecycle evidence, output, geography and provenance. A well-populated award record is not called operationally complete.

## Evidence trail

| Evidence class | Count / capacity | Status this wiki can support | What remains unverified |
|---|---:|---|---|
| NEA annual installed-capacity snapshot | 141.940 MW | Installed solar in FY2024/25 | Plant-level annual and seasonal output |
| DoED operating registry | 25 records / 141.74 MW | Operating, grid-connected registry records as of 9 January 2026 | Parcel boundaries, output and a fixed registry update cycle |
| NEA corrected LoI table | 63 records / 960 MW | Procurement award / pre-PPA snapshot dated 12 November 2024 | PPA, financing, construction and commissioning for each award |

The 0.20 MW difference between the NEA and DoED totals is retained because the sources have different dates and compilation boundaries. It is not treated as an error or silently averaged. Row-level status and missing-field coverage are maintained in [[data-solar-fleet-inventory]].

## Official direction

Nepal's NDC 3.0 groups solar with mini/micro hydro, wind and bio-energy in a non-large-hydro share target of 10% of renewable electricity capacity by 2030 and 15% by 2035. It does not allocate a solar-only MW trajectory or prove delivery.

## Evidence gaps

- Current status of each award after the LoI.
- Verified AC and DC capacity basis.
- Plant-level annual and seasonal generation.
- Precise coordinates, substations and hosting capacity for many records.
- A current public registry for distributed rooftop and institutional systems.

These gaps prevent a defensible conversion rate from award to operation. No aggregate delivery forecast is inferred from the 960 MW award total.

## Related

[[data-solar-fleet-inventory]] · [[solar-hydro-complementarity]] · [[solar-role-in-winter-deficit]] · [[storage-and-flexibility]]
