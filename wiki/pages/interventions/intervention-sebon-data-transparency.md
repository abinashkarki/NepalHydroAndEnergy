---
title: SEBON Data Transparency
Category: interventions
Type: intervention
Tags: [SEBON, NEPSE, data, IPO, rights-shares, transparency, retail-investors, civic-tech]
Excerpt: Mandate machine-readable financial disclosures from SEBON for all listed hydropower companies, and independently build a public dataset of Nepal's hydro IPO/rights share history cross-referenced against AD penalty exposure and hydrological performance.
page_quality: analysis
---

# SEBON Data Transparency

## The Intervention

This intervention has two parallel tracks:

### Track A — Regulatory (SEBON mandate)
Amend SEBON's disclosure regulations to require that IPO prospectuses, rights share issuance documents, and annual financial statements of listed hydropower companies be filed in **machine-readable structured formats** (XBRL or equivalent, with tagged data fields), not as scanned PDFs. Specific mandated fields would include:
- IPO/rights proceeds: actual use-of-funds breakdown (bank debt retirement vs. promoter bridge loan repayment vs. new project investment)
- PPA terms: contracted energy, tariff structure (seasonal split), and the existence of any AD penalty clause references
- Risk disclosures: explicit modelling of generation shortfall scenarios (80%, 65% of contracted energy) and their impact on debt service
- AD penalty exposure: penalties paid, by fiscal year, with reconciliation to ERC protections

### Track B — Civic data project (independently executable)
Build and publish a machine-readable dataset of Nepal's hydropower IPO and rights share history, cross-referenced against:
- AD penalty exposure (from audited financial statements and the [[ad-penalties]] mechanism)
- Hydrological performance (contracted energy vs. actual generation, from project-level data in [[q-design-discharge]])
- PPA architecture (subsidiary rate advantage documented in [[chilime]], standard IPP rates from [[ppa-pricing]])
- NEPSE trading suspensions and regulatory actions (e.g. Upper Syange, Khani Khola)

This dataset would be built using AI/data engineering tools and published as an open civic resource. It is independently executable without waiting for SEBON regulatory change.

## Theory of Change

The entire structure of Nepal's hydro IPO market — pre-revenue listing, rights share bailouts, undisclosed AD penalty exposure — operates in a data vacuum. The [[ipo-hydropower-bailout]] page documents what is known: six companies, NPR billions raised, many for debt retirement. But the full picture is unresolvable because SEBON's systemic use of non-machine-readable scanned PDFs blocks automated analysis.

Making disclosures machine-readable would:
- **Enable automated accountability.** Researchers, journalists, and analysts could programmatically compare prospectus promises against audited outcomes — revealing whether IPO funds were used as stated.
- **Force risk disclosure.** If SEBON mandates structured fields for PPA terms and AD penalty exposure, prospectuses would have to state, in machine-readable form, what retail investors are buying. Currently, investors in rights shares of distressed hydro companies are not informed that the off-taker can curtail the project and then penalise it.
- **Improve market efficiency.** Machine-readable disclosures would enable comparative analysis across all listed hydro companies, allowing retail investors to distinguish between Chilime (pre-IPO profitability, conservative Q-design, subsidiary rate advantage) and pre-revenue IPOs with unrealistic contracted energy targets.

The civic data track (Track B) creates value immediately by building the dataset that should exist but doesn't. Even before SEBON reforms, publishing a cross-referenced dataset would:
- Make the [[ipo-hydropower-bailout]] analysis fully data-backed rather than reliant on six partially-verified company entries
- Create a public resource usable by journalists, parliamentarians, and NRB regulators
- Demonstrate the feasibility of machine-readable energy-sector transparency, creating pressure for official adoption

## Current Status

**PARTIALLY VERIFIED:**
- SEBON's IPO disclosure system is confirmed to use non-machine-readable scanned PDFs. The [[ipo-hydropower-bailout]] page's entire "What is missing" section exists because SEBON's filing format blocks automated extraction.
- Six hydro companies have issued IPOs and rights shares, documented from media and secondary rating agency sources — but SEBON prospectuses have not been independently audited.

**UNVERIFIED:**
- What percentage of IPO/rights proceeds was actually used to retire promoter bridge loans vs. bank debt vs. new project investment
- What risk disclosures about hydrological underperformance, PPA rate risk, and AD penalty exposure actually appear in hydro IPO prospectuses
- The full list of NEPSE-listed hydro companies that issued rights shares within 3 years of IPO
- NRB's specialised hydro loan book — the true extent of off-balance-sheet restructuring and informal forbearance
- Whether any hydro IPO prospectus models the scenario where AD penalties consume a portion of revenue ([[ad-penalties]] estimates up to 16%)

**NEPSE has suspended trading on multiple hydro companies** (Upper Syange for insider trading and delayed rights share disclosure; Khani Khola for controversial Q4 reporting and promoter share dumping) — indicating market-level problems but without transparent data infrastructure to diagnose their systemic nature.

## What This Unlocks

- **Retail investor protection.** When a pre-revenue hydro project floats an IPO at Rs 100/share and six months later issues rights shares at Rs 50 to pay off bank loans, machine-readable disclosures would make this pattern visible across the sector.
- **Systemic risk monitoring.** NRB and the Ministry of Finance cannot currently see the aggregate exposure of retail investors to distressed hydro debt because the data is PDF-locked. Machine-readable disclosures would enable portfolio-level stress testing.
- **Market integrity.** Structured disclosure requirements would make it harder for promoters to dump shares before announcing rights share bailouts — the kind of behaviour that triggered the Upper Syange NEPSE suspension.
- **The civic dataset (Track B) specifically unlocks:** journalists can write data-backed stories; parliamentarians can ask quantified questions; NRB can cross-reference its loan book against public data. This is the fastest route to visibility because it requires no regulatory change.

## Research Gaps

- **Full list of listed hydro companies.** The wiki currently tracks six companies. NEPSE likely has 15-20 listed hydro entities. A complete roster with listing dates, IPO amounts, rights share history, and trading status is needed.
- **SEBON's current disclosure format policy.** Has SEBON ever considered machine-readable filing? Has any pilot been attempted? What is the technical specification of SEBON's current filing system?
- **NRB's specialised hydro loan book.** The extent of off-balance-sheet restructuring and informal forbearance is the hidden counterpart to the public equity story. NRB data would complete the picture.
- **International precedent.** India's SEBI mandated XBRL for listed companies in phases from 2008-2011. Bangladesh's BSEC adopted machine-readable disclosure in 2019. What is the nearest applicable regulatory model for Nepal?

## Political Feasibility

**Track A (regulatory): Medium-low in near term, medium in medium term.**
- SEBON is not the most resistant regulator in Nepal's institutional landscape, but mandating structured data filing requires technical capacity SEBON may not possess. The cost of implementing XBRL taxonomy for hydro-specific disclosures would need to be borne by either SEBON or the listed companies.
- The hydro company lobby — which benefits from opacity about PPA risk and AD penalty exposure — would resist mandatory structured risk disclosures.
- **Countervailing force:** NRB's recent climate-exposure directive and growing NPL pressure in the hydro book create financial-sector demand for better data. NRB could push SEBON from the systemic risk angle.

**Track B (civic data): Immediately executable. High feasibility.**
- The dataset can be built using publicly available SEBON/NEPSE filings, company annual reports, media archives, and AI-assisted text extraction from scanned PDFs.
- Publication as an open dataset (CSV/JSON with documentation) under a permissive license creates a public good that requires no government permission.
- The dataset would serve as both an accountability tool and a proof-of-concept for machine-readable energy-sector transparency — demonstrating to regulators what they could mandate.
- This track is a near-term action item for the wiki's author, leveraging AI/data engineering capability to produce a resource that currently exists nowhere in Nepal's public domain.

## Related Pages

- [[ipo-hydropower-bailout]] — the IPO-to-bailout pattern this data intervention targets
- [[nea-triple-authority]] — the institutional structure that AD penalty exposure reflects
- [[q-design-discharge]] — the generation underperformance that makes hydro IPOs risky
- [[ad-penalties]] — the penalty mechanism whose aggregate impact remains hidden without data
- [[chilime]] — the irreplicable success case that prospectuses invoke without context
- [[barahi-hydropower]] — the case that proves penalties can override their own exemptions
- [[ppa-pricing]] — the rate structure whose differential impact on IPPs is invisible without data
