---
title: For Investors
type: synthesis
created: 2026-05-13
updated: 2026-05-13
sources: []
tags: [persona-landing, investors, briefing-pack, navigation]
page_quality: analysis
brief:
  headline: "Per-project and system-level briefs covering capacity, generation, tariff, financing, and current signal — public knowledge, not investment advice."
  what: "An entry door for developers, IPP CFOs, DFIs, and analysts. The wiki is a public research surface, not a project-finance overlay; use it for context and verify project-level financials in audited filings."
  metrics:
    - { label: "Project briefs (operating)",  value: "2 (Kali Gandaki A, Upper Tamakoshi)" }
    - { label: "System-level claim briefs",   value: "3" }
    - { label: "Intervention briefs",         value: "1" }
    - { label: "Hydro projects in spec CSV",  value: "25" }
    - { label: "Solar projects in spec CSV",  value: "88" }
    - { label: "Unverified flags",            value: "0" }
  signal: green
  signal_note: "Public source discipline; not a substitute for due diligence or audited disclosures."
  why_it_matters: "If you need a fast read on the system-level constraints behind any project — tariff, transmission, storage, India interface — this is the starting page."
  audiences: []
---

# For Investors

<!-- generated:brief:start -->

## Brief

<p class="wiki-brief-signal" data-signal="green"><strong>Signal: Green.</strong> Public source discipline; not a substitute for due diligence or audited disclosures.</p>

**Per-project and system-level briefs covering capacity, generation, tariff, financing, and current signal — public knowledge, not investment advice.** An entry door for developers, IPP CFOs, DFIs, and analysts. The wiki is a public research surface, not a project-finance overlay; use it for context and verify project-level financials in audited filings.

| Project briefs (operating) | System-level claim briefs | Intervention briefs | Hydro projects in spec CSV | Solar projects in spec CSV | Unverified flags |
|---|---|---|---|---|---|
| 2 (Kali Gandaki A, Upper Tamakoshi) | 3 | 1 | 25 | 88 | 0 |

_Why it matters: If you need a fast read on the system-level constraints behind any project — tariff, transmission, storage, India interface — this is the starting page._

<!-- generated:brief:end -->


This page is the investor entry door. It is for developers, IPP CFOs, DFI analysts, and retail or institutional investors evaluating Nepal hydropower or solar projects. The wiki is a public, source-disciplined research product; **it is not investment advice**, does not score projects, does not estimate IRRs, and does not predict returns. Use it for system context and to verify the claims you encounter elsewhere.

## What this site is — and is not

| The wiki does | The wiki does not |
|---|---|
| Provide source-linked technical specs for major operating and under-construction projects | Score projects or rank them by investment quality |
| Track system-level constraints (transmission, storage, tariff, India trade) | Compute LCOE, equity IRR, debt-service coverage |
| Maintain a public structured-data layer (`data/project_specs.csv`) | Audit individual sponsor financial statements |
| Surface signals (red / amber / green) at the system level | Issue ratings, recommendations, or price targets |

## System-level reads every investor should do once

Before any project-level diligence, these five briefs explain the constraints that determine value at the system level. The signals here apply to most operating IPP equity, not to a specific transaction.

| Page | Signal | What it constrains |
|---|---|---|
| [[claim-transmission-immediate-blocker]] | Amber | Stranded-generation risk on every IPP not yet connected to a completed corridor |
| [[claim-storage-physical-fix]] | Green | Dry-season tariff value and the long-run portfolio mix |
| [[claim-mw-not-equal-value]] | Green | Why public "potential" and "installed" figures cannot be plugged into a project model directly |
| [[claim-solar-cheaper-than-small-hydro]] | Green | The marginal-cost benchmark new RoR PPAs now have to beat |
| [[claim-governance-binding]] | Amber | Institutional risk that does not show up on a balance sheet but binds completion timelines |

## Operating-project briefs

The wiki has two hand-authored operating-project briefs and a growing set of auto-derived briefs from the project specs CSV. The auto-derived briefs are visible only in the JSON index at [`briefing-packs/`](../../explorer/briefing-packs/); hand-authored briefs appear at the top of each project page.

| Project | Signal | Why it appears here |
|---|---|---|
| [[upper-tamakoshi]] | Red | Nepal's flagship asset, in formal default at near-design generation — the case study in tariff-debt mismatch |
| [[kali-gandaki-a]] | Amber | The two-decade reference case for an NEA-operated, multilaterally-financed plant |

Other large operating-fleet pages with rich context (no top-level brief yet) include [[marsyangdi]], [[kulekhani-i]], [[chilime]], [[khimti-i]], and [[likhu-1]]. Use the [[data-layer-hydropower-operating]] page to navigate the full fleet on the map.

## Reading paths

**The fifteen-minute version.** Read the brief on [[claim-transmission-immediate-blocker]] and [[upper-tamakoshi]]. That is the binding constraint and the cautionary tale for what happens when it interacts with a non-pass-through tariff.

**The one-hour version.** Add [[master-thesis]], [[claim-storage-physical-fix]], [[claim-mw-not-equal-value]], [[stranded-generation]], and [[ppa-pricing]].

**Before a board memo.** Read [[bottleneck-hierarchy]], [[twenty-year-strategy]], [[nea-triple-authority]], and the relevant intervention pages — those four together give you the system-level frame most other briefings will reference.

## Where this site is intentionally shallow

This is also where you should look elsewhere:

- **Project finance overlays.** No LCOE, equity IRR, or DSCR computation. Use UKHLL, Chilime, and other listed-company audited filings for actual cash flow data.
- **Sponsor / counterparty rating.** ICRA Nepal and CARE Ratings Nepal publish the working credit views.
- **Live secondary-market signals.** Sharesansar, MeroLagani, and the NEPSE feed.
- **PPA template text and amendment history.** Not yet in the wiki; tracked as a research gap in the repository `wiki/FLAGGED_FOR_REVIEW.md` log.
- **Tariff curve evolution / ERC dockets.** Use the Electricity Regulatory Commission's published orders directly.

The wiki is the layer underneath those — the structured context that makes the project-finance overlays comprehensible.

## Downloadable pack

The full system-level brief pack is at [`briefing-packs/investors.md`](../../explorer/briefing-packs/investors.md). It is regenerated each time `scripts/build_briefs.py` runs and is intended to be saved alongside your project file, not used as a standalone diligence document.

## Cite this page

Cite the underlying claim or entity pages, not this landing. Project-level numbers always trace back to a named source page (NEA Annual Report, UKHLL accounts, ICRA disclosure, etc.). The landing page may change; the source pages are versioned in git.

## Related

- [[start-here]] — the general public entry point
- [[for-policymakers]] — the policy-advisor entry door
- [[for-journalists]] — the journalist entry door
- [[stranded-generation]] — the transmission-risk frame for IPP equity
- [[nea-triple-authority]] — why NEA's three roles create structural counterparty risk
- [[ppa-pricing]] — the tariff structure that determines project economics
