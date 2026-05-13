---
title: For Journalists
type: synthesis
created: 2026-05-13
updated: 2026-05-13
sources: []
tags: [persona-landing, journalists, briefing-pack, navigation]
page_quality: analysis
brief:
  headline: "Story-ready evidence. Every brief has six numbers, a traffic-light signal, and a source one click away."
  what: "An entry door for reporters working a Nepal energy story on a deadline. The briefs are written to be verifiable in under five minutes; the underlying source pages list the primary documents the numbers come from."
  metrics:
    - { label: "Briefs (verified)",       value: "8" }
    - { label: "Source pages",            value: "57" }
    - { label: "Interventions tracked",   value: "5" }
    - { label: "Unverified flags",        value: "0" }
    - { label: "Refresh cadence",         value: "monthly" }
    - { label: "License",                 value: "see LICENSE" }
  signal: green
  signal_note: "Public, source-disciplined; cite the underlying claim/source pages, not this landing."
  why_it_matters: "If you have an hour before deadline, this page is the route from a Nepal energy headline back to a primary document."
  audiences: []
---

# For Journalists

<!-- generated:brief:start -->

## Brief

<p class="wiki-brief-signal" data-signal="green"><strong>Signal: Green.</strong> Public, source-disciplined; cite the underlying claim/source pages, not this landing.</p>

**Story-ready evidence. Every brief has six numbers, a traffic-light signal, and a source one click away.** An entry door for reporters working a Nepal energy story on a deadline. The briefs are written to be verifiable in under five minutes; the underlying source pages list the primary documents the numbers come from.

| Briefs (verified) | Source pages | Interventions tracked | Unverified flags | Refresh cadence | License |
|---|---|---|---|---|---|
| 8 | 57 | 5 | 0 | monthly | see LICENSE |

_Why it matters: If you have an hour before deadline, this page is the route from a Nepal energy headline back to a primary document._

<!-- generated:brief:end -->


This page is the journalist entry door to the Nepal Energy Wiki. The wiki separates **sources** (what a document says), **data and entities** (what the system contains), **claims** (what is argued), and **syntheses** (what it adds up to). For a story, you usually want to start at the brief, walk one step back to the claim, then one more step back to the source.

## Verify a number in three clicks

Most Nepal energy headlines reduce to one of about a dozen numbers. Here is where each one is anchored.

| If the story says... | Verify at... | Underlying source |
|---|---|---|
| "Nepal has 83,000 MW of hydropower potential" | [[claim-mw-not-equal-value]], [[hydropower-potential-categories]] | WECS Hydropower Potential 2019 |
| "Installed capacity is around 3,500 MW" | [[claim-mw-not-equal-value]] | NEA Annual Report FY 2024/25; DoED operating registry |
| "Nepal exported NPR 17 billion of electricity in FY 2024/25" | [[india-energy-relationship]] | NEA Annual Report FY 2024/25 |
| "700–800 MW spilled in monsoon" | [[claim-transmission-immediate-blocker]], [[stranded-generation]] | NEA disclosures; corridor synthesis |
| "Upper Tamakoshi is in default" | [[upper-tamakoshi]] | UKHLL accounts; ICRA Nepal downgrade notice |
| "Kulekhani's reservoir is half-filled with silt" | [[kulekhani-i]], [[sediment-as-design-constraint]] | JICA Storage Master Plan Vol 1; 2021 bathymetry |
| "Hetauda–Dhalkebar is 98% complete" | [[intervention-transmission-completion]] | NEA April 2026 status; Energy Minister statement |
| "Solar is now cheaper than small hydro" | [[claim-solar-cheaper-than-small-hydro]] | NEA tender awards; PPA tariff schedule |
| "Nepal will hit 28,500 MW by 2035" (IPSDP) | [[data-ipsdp-milestone-ladder-2022-2040]] | DoED IPSDP 2025 |

If a number you need to check is not in the table, search the explorer's Seek box. If the wiki cannot trace the number to a source, that is itself the story.

## Story angles that are already in the wiki

Each of the five interventions is a structured argument with a current status, a "what this unlocks" section, and a research gap list. Reporters can lift the structure of the argument from these pages without lifting the prose — every claim has a wikilink back to the source.

| Story angle | Page |
|---|---|
| The 14 towers still blocking the eastern backbone | [[intervention-transmission-completion]] |
| NEA's three roles (regulator, owner, off-taker) and why they conflict | [[intervention-nea-structural-separation]], [[nea-triple-authority]] |
| Listed hydropower IPOs and disclosure quality | [[intervention-sebon-data-transparency]] |
| Electric cooking — why uptake has stayed under 1% of households | [[intervention-electric-cooking-transition]] |
| Q-design discharge and climate-adjusted hydrology | [[intervention-q-design-climate-adjustment]], [[q-design-discharge]] |

The full set of major claim briefs is in the [`briefing-packs/journalists.md`](../../explorer/briefing-packs/journalists.md) download.

## How sources are handled

Every quantitative claim on a claim page links to a source page; every source page summarises the primary document (PDF, report, registry, dataset) and lists what other wiki pages cite it. This is enforced by the wiki's governance rules:

- Source pages describe evidence, not policy implications.
- Data pages describe datasets and caveats, not strategy.
- Claim pages carry the bounded argument, with explicit confidence and boundary conditions.
- Synthesis pages — including this one — are the only places "so what" is allowed.

When in doubt about whether a number is a single-source claim or a synthesis-of-multiple-sources claim, open the source page and read the "Used By" section.

## Cite this page

Cite the underlying claim or source page, not this landing. A typical attribution form:

> Nepal Energy Wiki, _Transmission and Delivery May Be the #1 Immediate Monetization Bottleneck_, updated 2026-05-13. transparentgov.ai/wiki/explorer/?page=claim-transmission-immediate-blocker

For the project pages, use the project slug, the wiki title, and the source page that the numbers in your story actually came from (NEA, JICA, ICRA, etc.) — not the wiki page itself. The wiki is the index; the source is the citation.

## A note on dates and updates

Every page has an `updated:` line in its frontmatter that the build pipeline reflects in the explorer header. If you are reading a brief that has not been updated in the current month and a story is breaking that touches it, treat the brief as out of date and check the underlying source.

## Related

- [[start-here]] — the general public entry point
- [[for-policymakers]] — the policy-advisor entry door
- [[for-investors]] — the investor entry door
- [[unresolved-questions]] — the longer-running open questions the wiki has not yet resolved
