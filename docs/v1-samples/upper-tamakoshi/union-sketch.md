---
title: Upper Tamakoshi
mode: union-sketch
subject: upper-tamakoshi
record_checked: 2026-07-10
---

# Upper Tamakoshi

**456 MW · Operating · Tama Koshi, Dolakha · Run-of-river (peaking) · Record checked 10 Jul 2026**

One page, three layers. Each layer has one job and one rule, and they sit in a fixed order.

<div class="layer layer-reference">
<div class="layer-tag">Layer 1 · Reference · neutral, always visible</div>

Upper Tamakoshi is a 456 MW run-of-river hydropower plant on the Tama Koshi River in Dolakha district. It is owned by Upper Tamakoshi Hydropower Limited (UTKHPL), a company established by the Nepal Electricity Authority. It began commercial operation in 2021 and is Nepal's largest operating hydropower plant. The company has reported financial distress since a September 2024 flood. Its latest quarterly filing shows a profit.

*The lead above is written by hand. The table below is generated from Layer 3.*

| Fact | Value | As of | Grade |
|---|---|---|---|
| Capacity | 456 MW | 2026-07-10 | registry |
| Design energy | 2,281 GWh/yr | 2026-07-10 | registry |
| Revenue, FY2080/81 | NPR 8.679 bn | filed 2026-04-06 | **primary** |
| Net result, FY2082/83 to Q3 | NPR +0.287 bn (unaudited) | filed 2026-05-13 | **primary** |
| Generation, FY2080/81 | 2,058 GWh (90.2% of design) | — | secondary |
| Credit rating | ICRA "D", FY2081/82 | — | secondary |
| Rolwaling diversion | +216.51 GWh expected; NPR 2.103 bn capital work in progress; no schedule | 2026-05-13 | **primary** |

**Disputed:** the year of the earlier ~8.68 bn revenue figure · 7 vs 11 years of construction · wet tariff of 3.74 vs 3.63 · whether the Q3 figures cover one quarter or nine months. Details are in Layer 3's conflicts register.

</div>

<div class="layer layer-notebook">
<div class="layer-tag">Layer 2 · Notebook · interpretive, dated, signed</div>

<details open>
<summary><strong>Why this plant matters for understanding the sector</strong> · written 2026-07-10 · <span class="stale">⚠ 1 input changed since written</span></summary>

**The puzzle.** The plant that ended load-shedding went into default. How can a plant be technically successful and financially broken?

**What it teaches:**

1. **Hydrology was not the main problem.** Generation of about 90% of design (`generation_pct_of_contracted · FY2080/81`) means the river delivered. That separates "does the river deliver" from "does the contract pay". See [[q-design-discharge]].
2. **Fixed tariff vs. rising debt.** Leverage rose from 75/25 in the original model to 88:12 at commissioning (`debt_equity_effective_at_cod`). The tariff did not move. Revenue implies about NPR 4.22/kWh (`revenue_npr_bn · FY2080/81` ÷ `generation_gwh · FY2080/81`). Interest takes about three-quarters of that. See [[ppa-pricing]] and [[nea-triple-authority]].
3. **Insurance exclusions decide who absorbs a flood.** This is secondary evidence and not yet confirmed. See [[hydro-insurance]].

**Open question.** `net_profit_loss_npr_bn · FY2082/83-Q3` is positive. If that holds in the audited year, then "structurally inevitable default" was wrong. It would have been a crisis of one bad year plus leverage.

**What would change my mind:** the audited FY2081/82 and FY2082/83 accounts, the ICRA rating letter, and the insurance settlement amount.

</details>

*Rule: the notebook may interpret, but every number it uses points to a Layer 3 row. When a cited row changes, the entry is flagged automatically (see the warning above) instead of silently going stale.*

</div>

<div class="layer layer-record">
<div class="layer-tag">Layer 3 · Record · structured, append-only</div>

<details>
<summary><strong>Time series, events, open items</strong> · 60 facts · 11 events · 12 open items</summary>

| Metric | FY2079/80 | FY2080/81 | FY2081/82 | FY2082/83 Q3 |
|---|---|---|---|---|
| Generation (GWh) | 1,945.83 · C | 2,058.36 · C | 1,529.07 · C | — |
| Revenue (NPR bn) | ⚠ ~8.68 · C | **8.679 · P** (⚠ 9.3–9.5 · D) | ~6.9 · C | **7.718 · P** |
| Net result (NPR bn) | (2.52) · C | (1.39) · C | (2.57) · C | **+0.287 · P** |
| Interest / finance cost | ~6.68 · C | ~6.7 · C | — | **4.052 · P** |
| Rating | — | Distressed · C | D · C | — |

P = primary filing · C = research compilation · D = derived

**Recent events:** 2026-05-13 Q3 report published (P) · 2026-04-06 annual reports FY2079/80–80/81 published (P) · 2024-09 flood, 88-day shutdown (C)

**Top open items:** transcribe primary FY2080/81 net result and interest · confirm the Q3 period · insurance outcome · Rolwaling schedule

**To update:** append rows to `facts.csv`. The Layer 1 table re-renders, and any notebook entry citing a changed row gets a warning flag.

</details>

</div>

## How the three layers fit

| | Reference | Notebook | Record |
|---|---|---|---|
| Who writes it | Generated, plus a hand-written 3–4 sentence lead | You, deliberately and occasionally | Whoever ingests a filing |
| May interpret? | No | Yes, dated and signed | No |
| Holds numbers? | Displays them from the record | Cites record rows only | **The only place numbers live** |
| Needed for every project? | Yes, generated | **No.** Only where the case teaches something | Yes |
| When new data arrives | Re-renders | Gets a warning flag, and you decide | Append a row |
