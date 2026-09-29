---
title: "Upper Tamakoshi as a lens: how can the plant that ended load-shedding be in trouble?"
mode: learning-instrument
subject: upper-tamakoshi
as_of: 2026-07-10
evidence_basis: [utkhpl-disclosures-2026, ukhl-financials-generation-fy2079-82, ukhl-annual-report, upper-tamakoshi, q-design-discharge, ppa-pricing, nea-triple-authority, hydro-insurance, run-of-river-hydropower, firm-power, seasonal-mismatch]
---

# Upper Tamakoshi: a notebook

## The puzzle

The 456 MW plant that ended load-shedding is, according to the current page, "formally insolvent." Both statements sit in [[upper-tamakoshi]]. How can a plant be technically successful and financially broken? And is "broken" even still the right word? The newest filing shows a quarterly profit.

## What I thought vs. what the evidence shows

Learning log, oldest belief first:

1. **Belief:** the distress is a hydrology story. FY2079/80 generation was back-calculated from revenue at about 1,340 GWh (~59% of contracted), so I read it as the [[q-design-discharge]] failure mode: the promise was too big for the river.
2. **Correction:** the research compilation gives actual dispatch of 1,945.83 GWh (85.3%) in FY2079/80 and 2,058.36 GWh (90.2%) in FY2080/81. The revenue back-calculation was wrong, so hydrology was not the main problem.
3. **Consequence:** this makes the financial argument stronger. A plant at ~90% of contracted energy still posted a loss, so the mismatch is between tariff and capital structure, not river and turbine.
4. **Second correction, new:** the page puts ~NPR 8.68B of revenue in FY2079/80. The primary filing puts NPR 8.679B in **FY2080/81**. I was leaning on a number attached to the wrong year.

The lesson for me: I should check which year a figure belongs to before I reason from it.

## Working through it

**Inputs, with provenance.**

| Input | Value | Basis |
|---|---|---|
| FY2080/81 electricity-sales revenue | NPR 8.679B | Primary (utkhpl-disclosures-2026) |
| FY2080/81 generation | 2,058.36 GWh | Secondary (research compilation) |
| PPA rates, first year | 3.74 wet / 6.96 dry NPR/kWh | Spec table and page; escalation unchecked |
| Interest expense, FY2079/80 | ~NPR 6.68B | Secondary |
| FY2080/81 net loss | ~NPR 1.39B | Secondary |

**Step 1: what tariff did the plant actually earn?**
8.679B ÷ 2,058.36 GWh ≈ **NPR 4.22/kWh**. That is above the wet rate of 3.74 and far below the dry rate of 6.96. If only the two first-year rates applied, the dry-rate share of energy would be d, where 3.74 + 3.22d = 4.22, so d ≈ 0.15. That is my inference. The CSV's dry-share field is blank, so I cannot check it.

**Step 2: does the page's "9.3–9.5B ceiling" survive?** No. I cannot reproduce it from published inputs. The primary revenue figure is about NPR 0.6–0.8B *below* it. The page's own text calls it a computed maximum, not an observed result. The ceiling argument was a modelled upper bound, and the real number is lower.

**Step 3: coverage against interest.**
6.68B ÷ 8.679B ≈ **77%** of revenue goes to interest. This mixes years, since the interest figure is FY2079/80 and secondary. I read it as "roughly three-quarters" and no more precise. Operating costs, principal and taxes come out of the remaining ~2B. That is consistent with a reported loss and DSCR below 1.0x, though I have not seen a primary DSCR.

**Step 4: what would Rolwaling add?**
The filing says the diversion is expected to add **216.51 GWh** to Upper Tamakoshi. The compilation and the page say 212 GWh, so the two sources disagree by about 2%. At the implied 4.22 average, 212–217 GWh is ~NPR 0.9B. At the dry rate it is ~NPR 1.5B, at the top of the page's 1.2–1.5B range. Against ~77% interest burden, that helps but does not obviously close the gap.

**Step 5: the awkward new data point.**
The May 2026 quarterly statement (unaudited) shows electricity revenue of NPR 7.718B, finance costs of NPR 4.052B and **net profit of NPR 286.8M**. I cannot tell whether that is a single quarter or nine months cumulative. A single quarter would be implausibly large next to an 8.7B year, so I suspect cumulative. Either way, finance cost is about half of revenue, not 77%, and the period is profitable. This does not fit the "structurally inevitable loss" story, and I don't yet know why. Candidates: a wet-season-heavy period, restructured debt, or a different cut-off.

## What this case teaches about the system

1. **A tariff fixed early can outlive the capital structure it was built for.** The rates were set against a 75:25 model. The compilation says the effective ratio at COD was 88:12 after ~NPR 14B of interest during construction. The rate did not move. See [[ppa-pricing]].
2. **One institution wearing three hats limits the remedies.** NEA is buyer, regulator-adjacent and shareholder. Note the caveat on that page: it describes a *conflict risk*, not proven misconduct. It explains why "renegotiate the PPA" has no obvious owner. See [[nea-triple-authority]].
3. **Design discharge protects you from hydrology risk only if you check it.** 90% delivery shows Q-design can be right and the project can still fail. That separates "does the river deliver" from "does the contract pay." See [[q-design-discharge]].
4. **Insurance exclusions decide who eats a flood.** The compilation says the lost-profit cover excluded transmission failure. That is not confirmed by the primary filing. What is primary: the FY2080/81 insurance expense was NPR 99.3M (1.14% of revenue), and claims were "in settlement processing." One project-year is not a sector trend. See [[hydro-insurance]].
5. **Big RoR is a wet-season asset with a dry-season price.** Peaking pondage helps within a day, not across seasons. The plant's dry-season energy is the valuable part, and Rolwaling is aimed at exactly that. See [[run-of-river-hydropower]], [[firm-power]] and [[seasonal-mismatch]].

## Confidence map

- **High (primary):** FY2080/81 revenue of NPR 8.679B, insurance expense NPR 99.3M, the Rolwaling figures (22 MW, 216.51 GWh, NPR 2.103B CWIP), and claims lodged and not yet settled as of the annual report's cut-off.
- **Medium (compilation, plausible, not verified):** the three generation figures, the 88:12 ratio, interest expense, losses, and the 2024 flood damage and claim amounts.
- **Low (compilation, and nothing primary in the wiki):** the ICRA "D" rating and the "default" framing. I should not treat "formally insolvent" as established.
- **Inference (mine):** the ~15% dry-share estimate, the ~77% interest burden, and any view on Rolwaling's impact.
- **Unresolved contradictions:** construction took "roughly seven years" in one place and "11 years" in another. The CSV's start year is blank, so I cannot settle it. Debt/equity is 75/25 in the CSV and 88:12 in the prose. I read these as *original model vs. effective at COD*, but the page's spec table lists only the former.

## Open questions and what would change my mind

- **Audited FY2081/82 statements.** They would give a primary generation figure and interest and settle whether 67.0% and the 88-day shutdown are right.
- **The Q3 FY2082/83 period.** Is it a quarter or cumulative? If a profitable quarter is real, "structural default" needs softening.
- **An ICRA rating letter or lender notice.** Without one, "D" stays unverified.
- **Insurance settlement.** A paid amount would show whether the transmission exclusion applied.
- **Rolwaling progress.** CWIP is a balance, not a milestone. I would want a package percentage and a commissioning date.
- **The tariff realized vs. contracted.** Escalation clauses or dry-share data would test my 4.22/kWh reading.

## Next thing to read or check

Find the FY2080/81 annual statements in the [combined annual report PDF](http://utkhpl.org.np/wp-content/uploads/2026/04/Annual-Report-2079-80-2080-81.pdf). I want two things from them: the FY2080/81 finance cost and net result as primary figures, and the number of months in the Q3 statement. That would replace three of my four mixed-basis inputs with primary ones.
