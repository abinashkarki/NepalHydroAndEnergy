---
title: Upper Trishuli 3A
type: entity
created: 2026-04-20
updated: 2026-05-06
sources: [nea-transmission-annual-book-2077, nea-annual-report-fy2024-25]
tags: [project, operating, gandaki, rasuwa, nuwakot]
images:
  - src: upper-trishuli-3a/nea2077-p002-img01.png
    caption: "Inauguration of Upper Trisuli 3A Hydroelectric Project"
    credit: "Nepal Electricity Authority, A Year in Review FY 2019/20 (B.S. 2077)"
    license: gov-permissive
    source_url: "../../../data/raw/corridor_tracing/nea/nea_transmission_annual_book_2077.pdf"
  - src: upper-trishuli-3a/nea2077-p028-img01.png
    caption: "Excitation Floor"
    credit: "Nepal Electricity Authority, A Year in Review FY 2019/20 (B.S. 2077)"
    license: gov-permissive
    source_url: "../../../data/raw/corridor_tracing/nea/nea_transmission_annual_book_2077.pdf"
generator: specs-refresh
---

# Upper Trishuli 3A

<figure class="wiki-inline-figure">
  <img src="../assets/images/upper-trishuli-3a/nea2425-p023-img01.png" alt="Lifting of upper bracket during overhauling">
  <figcaption>Lifting of upper bracket during overhauling</figcaption>
</figure>

60 MW · operating · on the Trishuli · in Rasuwa and Nuwakot districts.

<!-- generated:specs:start -->

## Specifications

| Parameter | Value |
|-----------|-------|
| Capacity | 60 MW |
| Status | Under construction (Generation licence) |
| River | Trishuli ([[gandaki-basin]]) |
| District | Rasuwa |
| Province | Bagmati Pradesh |

<!-- generated:specs:end -->

<!-- generated:sources:start -->

## Sources

- [[nea-transmission-annual-book-2077|NEA Transmission Annual Book 2077]]
- [[nea-annual-report-fy2024-25|NEA Annual Report FY 2024/25]]

<!-- generated:sources:end -->

## Specifications (NEA FY 2081/82)

Upper Trishuli 3A is NEA's **second-largest plant by annual design energy**
(489.76 GWh) despite only 60 MW of installed capacity — a reflection of the
Trishuli River's high and relatively stable discharge. Two 30 MW vertical
Francis units operate at 70% probability of exceedance as a pure run-of-river
plant (not peaking RoR — it runs on whatever the river provides).

| Parameter | Value |
|-----------|-------|
| Type | Run-of-river (ROR) |
| Units | 2 × 30 MW Francis |
| PE design basis | 70% POE |
| Design generation | 489.76 GWh/yr |
| FY 2081/82 generation | 356 GWh |
| FY 2081/82 vs design | 72.7% |
| FY 2081/82 vs target | 78% |
| Year-over-year change | −17% |
| Cumulative lifetime generation | 2,391.5 GWh |
| Districts | Rasuwa and Nuwakot, Bagmati Province |

> [!warning] **Status correction.** The Ministry of Energy registry and
> the auto-generated spec table list the plant as "Under construction
> (Generation licence)." The NEA's FY 2024/25 report covers it as an
> operating station with multi-year generation data, cumulative lifetime
> output, completed overhauls, and operational incident reporting. The
> plant is operating. The registry status is stale.

For the first time in FY 2081/82, NEA's in-house maintenance team
overhauled both Units 1 and 2 — a significant operational milestone
that included repairs to draft tube gates, inlet valves, and head covers.
Radial gates received major maintenance with seal, plate, and rail bar
replacements. SCADA systems and communication links were restored with
sensor and PLC upgrades, and pre-monsoon civil works included concrete
repairs and gabion spur construction near the tailrace.

## The 73% Problem — Why Design Energy Fails Here

At **72.7% of design generation**, Upper Trishuli 3A has the lowest
design-performance ratio in NEA's large-plant fleet alongside Chameliya
(77.3%). Compare:

| Plant | MW | % of Design (FY 2081/82) | Type |
|---|---|---|---|
| Middle Marsyangdi | 70 | **107.6%** | PROR, glacier-fed |
| Kali Gandaki A | 144 | 102.5% | PROR with pondage |
| Marsyangdi | 69 | 97.0% | PROR |
| Chameliya | 30 | 77.3% | PROR, major construction failure |
| **Upper Trishuli 3A** | **60** | **72.7%** | **ROR, high-design-energy** |

The 489.76 GWh design figure is aggressive for a 60 MW plant — it implies
a plant load factor of ~93%, which would place it among the highest PLFs
in the global hydro fleet. At 356 GWh actual, the PLF is ~68% — still
respectable for a RoR plant but dramatically below the design assumption.

This is the [[q-design-discharge]] problem at NEA scale. A plant built
on 70% POE hydrology with a 93% PLF design has almost no margin for
actual seasonal variability. The 17% year-over-year decline (FY 2080/81
to 2081/82) suggests the hydrology assumption was tested and failed.

## The Flood Event — Climate-Resilience in Real Time

On the morning of **2081/03/24 at approximately 4:30 AM**, a sudden flood
caused by intense rainfall in the upper catchment sent uncontrolled water
and debris into the dam premises. Because there was no early warning
system, several key structures were affected before operators could
respond.

**Damage summary:**
- Diversion Radial Gate-1: ~1.5 m of lower gate skin plate detached;
  control panel and hydraulic unit submerged
- Gates 2, 3, and 4: structurally intact but currently inoperative due
  to damaged hydraulic systems
- Gate-2's pressure unit submerged; Gate-3's hydraulic cylinder broken
- Stoplog gantry crane and lifting mechanism damaged
- Control building, piers, staff quarters, and operating platforms
  impacted by debris and silt deposition
- Gate operating panels, motors, and sensors submerged

No human casualties were reported. But the event is a real-world test of
what Nepal's RoR fleet faces as rainfall intensity increases in the
Himalayan catchment. The missing early warning system — flagged in the
NEA's own incident report — is the operational gap that climate-resilient
design would need to close across the fleet. See [[glof-risk]] and
[[buildability]] for the broader infrastructure-resilience context.

## Significance — NEA's Highest-Design-Energy RoR Asset

Upper Trishuli 3A's design energy (489.76 GWh from 60 MW) reflects
what the Trishuli River basin can deliver: reliable, year-round baseflow
from a catchment that drains the Langtang-Helambu massif. At 356 GWh
actual, it still delivers more energy per MW than any other NEA RoR
plant — a function of basin hydrology, not engineering superiority.

But the plant also demonstrates that no RoR asset, regardless of basin
quality, can guarantee its design energy. The 489.76 GWh target is the
high-end assumption; 356 GWh is reality. The gap between them is the
structural reason Nepal's RoR-heavy fleet cannot close the
[[seasonal-mismatch]] without storage — even in its best basins.

## See also

- [[q-design-discharge]] — why 72.7% of design is a structural signal
- [[seasonal-mismatch]] — the system problem even a well-sited RoR cannot fix
- [[buildability]] — how flood events test infrastructure resilience
- [[glof-risk]] — the broader hazard context for Himalayan RoR headworks
- [[gandaki-basin]] — basin context; the Trishuli feeds the Narayani
- [[run-of-river-hydropower]]
