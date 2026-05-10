# Wiki Ontology

Canonical definitions for terms that agents and contributors must not fragment, rename, or silently alias.

**Rule:** If you want to introduce a term not on this list, flag it in `wiki/FLAGGED_FOR_REVIEW.md` before using it. Do not create pages for near-synonyms without review.

---

## Core System Concepts

### Seasonal mismatch
**Definition:** The structural misalignment between Nepal's monsoon-peaking hydropower generation profile and its comparatively stable year-round electricity demand.
**Allowed aliases:** monsoon-winter imbalance, hydro seasonality problem
**Disallowed aliases:** winter crisis (too narrow — implies shortage only), export paradox (conflates symptom with cause)
**Parent syntheses:** seasonal-arbitrage-trap, storage-deficit
**Related pages:** run-of-river-hydropower, firm-power, solar-hydro-complementarity

### Storage deficit
**Definition:** The gap between Nepal's operational reservoir storage capacity (~5 m³/capita) and the volume needed for seasonal water regulation and dry-season firm power.
**Allowed aliases:** storage gap, seasonal inventory shortage
**Disallowed aliases:** dam shortage (too narrow — dams are one of several storage forms), water crisis (broader than the energy-relevant definition)
**Parent syntheses:** storage-deficit
**Related pages:** kulekhani-cascade, dudhkoshi-storage, buildability, seasonal-mismatch

### Firm power
**Definition:** Electricity that can be depended upon at the times the grid needs it most — not nameplate capacity, not annual energy, but deliverable output during scarcity hours.
**Allowed aliases:** dependable capacity, dispatchable power
**Disallowed aliases:** base load (different concept — firm power can be peaking), installed capacity (conflates hardware with reliability)
**Parent syntheses:** master-thesis, seasonal-arbitrage-trap
**Related pages:** run-of-river-hydropower, storage-deficit, claim-timing-not-volume, claim-mw-not-equal-value

### Run-of-river hydropower (RoR)
**Definition:** Hydropower that generates from river flow without significant reservoir storage. Output follows the natural hydrograph.
**Allowed aliases:** RoR, run-of-river, diversion hydropower
**Disallowed aliases:** continuous power (false — RoR is seasonally variable), small hydro (size-independent concept; small hydro can be storage)
**Parent syntheses:** master-thesis, seasonal-mismatch
**Related pages:** peaking-run-of-river, storage-deficit, q-design-discharge

### Seasonal arbitrage trap
**Definition:** The value destruction pattern where Nepal exports cheap monsoon electricity and imports expensive dry-season electricity, producing negative net revenue despite positive net energy.
**Allowed aliases:** trade timing problem, monsoon-export-dry-import asymmetry
**Disallowed aliases:** trade deficit (refers to energy, not value), export failure (implies exports are wrong; the trap is about timing, not exporting per se)
**Parent syntheses:** master-thesis, twenty-year-strategy
**Related pages:** seasonal-mismatch, data-trade-time-series, india-energy-relationship, stranded-generation

### Stranded generation
**Definition:** Available generation that cannot be monetized because grid capacity, market access, or transmission corridors are insufficient.
**Allowed aliases:** curtailment, spilled power, unevacuated energy
**Disallowed aliases:** surplus (surplus implies excess demand, not infrastructure failure)
**Parent syntheses:** bottleneck-hierarchy, claim-transmission-immediate-blocker
**Related pages:** transmission-corridors, seasonal-mismatch, hetauda-dhalkebar-inaruwa-backbone

### Solar-hydro complementarity
**Definition:** The physical alignment between Nepal's dry-season solar resource (clear winter skies) and its dry-season hydropower weakness, creating a portfolio effect.
**Allowed aliases:** solar-hydro seasonal fit, winter solar value
**Disallowed aliases:** solar replacement (solar does not replace hydro; it complements it), solar solution (solar alone does not solve evening peak or seasonal storage)
**Parent syntheses:** solar-in-the-master-narrative, solar-role-in-winter-deficit
**Related pages:** solar-resource-geography-nepal, nea-960mw-solar-tender, storage-deficit

### Buildability
**Definition:** The set of non-market constraints — terrain, geology, access, seismic hazard, resettlement, financing, institutional capacity — that determine whether a project that looks good on paper can actually be built and operated.
**Allowed aliases:** execution risk, construction feasibility
**Disallowed aliases:** engineering challenge (too narrow — buildability includes social, financial, and political dimensions)
**Parent syntheses:** master-thesis, bottleneck-hierarchy
**Related pages:** sediment-as-design-constraint, glof-risk, hydro-geopolitics

---

## Institutional & Governance Concepts

### NEA triple authority
**Definition:** The conflict of interest created when NEA simultaneously acts as regulator (sets tariffs), shareholder (owns equity in generation), and sole off-taker (buys power at regulated rates).
**Allowed aliases:** triple-role conflict, NEA structural conflict
**Disallowed aliases:** NEA monopoly (monopoly is only one dimension; the triple role is the specific problem)
**Parent syntheses:** intervention-nea-structural-separation, claim-governance-binding
**Related pages:** ppa-pricing, nea, intervention-nea-structural-separation

### Q-design discharge
**Definition:** The river flow percentile used to set a hydropower project's design energy and PPA contracted output. Q65 means the flow is exceeded 65% of the time (dry-season design); Q40 means exceeded 40% of the time (wetter, riskier design).
**Allowed aliases:** design flow, exceedance flow
**Disallowed aliases:** average flow (Q-design is a percentile, not a mean), minimum flow (different concept — environmental release)
**Parent syntheses:** master-thesis, claim-climate-harder-not-easier
**Related pages:** run-of-river-hydropower, hydropower-potential-categories, climate-adjusted-hydrology

### PPA pricing
**Definition:** The tariff structure in Nepal's Power Purchase Agreements, typically differentiated by season (wet/dry) and project type (RoR/PRoR/storage).
**Allowed aliases:** power purchase agreement tariff, NEA off-take rate
**Disallowed aliases:** electricity price (PPA rate is wholesale; retail price is different), market price (PPA is regulated, not market-driven)
**Parent syntheses:** claim-mw-not-equal-value, nea-triple-authority
**Related pages:** nea-960mw-solar-tender, claim-solar-cheaper-than-small-hydro, chilime

---

## Environmental & Geophysical Concepts

### Sediment as design constraint
**Definition:** The recognition that Himalayan river sediment — abrasive, high-volume, and variable — is not merely an O&M issue but a factor that can determine whether a project is physically and financially viable.
**Allowed aliases:** sediment hazard, silt abrasion risk
**Disallowed aliases:** sediment problem (too vague — the concept is that sediment determines design, not just causes trouble)
**Parent syntheses:** master-thesis, claim-sediment-core-issue
**Related pages:** glof-risk, buildability, kulekhani-cascade, peak-water

### GLOF risk
**Definition:** Glacial Lake Outburst Flood risk — the hazard that moraine-dammed glacial lakes can release high-energy sediment slurries that exceed historical design flood bases.
**Allowed aliases:** glacial lake outburst flood, outburst flood hazard
**Disallowed aliases:** glacier flood (implies meltwater, not moraine-breach dynamics), climate flood (too broad)
**Parent syntheses:** claim-climate-harder-not-easier, buildability
**Related pages:** sediment-as-design-constraint, peak-water, koshi-basin, dudhkoshi-storage

### Peak water
**Definition:** The period of maximum glacial meltwater runoff, after which declining ice volumes reduce long-term river flow — a transition window that affects hydropower planning horizons.
**Allowed aliases:** glacial peak runoff, meltwater maximum
**Disallowed aliases:** water peak (ambiguous — could mean demand peak), glacial maximum (refers to ice extent, not runoff)
**Parent syntheses:** master-thesis, claim-climate-harder-not-easier
**Related pages:** glof-risk, sediment-as-design-constraint, wecs-river-basin-plan-2024

---

## Geopolitical Concepts

### Hydro-geopolitics
**Definition:** The intersection of transboundary river geography, bilateral energy trade, and sovereignty questions that shapes Nepal's hydropower strategy and project siting.
**Allowed aliases:** water geopolitics, transboundary hydro politics
**Disallowed aliases:** India threat (too adversarial; hydro-geopolitics includes cooperation and market integration), river politics (too broad — includes irrigation, not just energy)
**Parent syntheses:** master-thesis, downstream-river-geopolitics
**Related pages:** india-energy-relationship, domestic-led-hydro-strategy, arun-3, pancheshwar

### Domestic-led hydro strategy
**Definition:** The strategic priority to build hydropower for domestic productive use and dry-season reliability first, using exports to monetize surplus rather than defining the master strategy around export markets.
**Allowed aliases:** domestic-first strategy, productive-use-first hydro
**Disallowed aliases:** anti-export (the strategy uses exports, just does not lead with them), self-sufficiency (implies autarky, not strategic sequencing)
**Parent syntheses:** master-thesis, twenty-year-strategy
**Related pages:** india-energy-relationship, hydro-geopolitics, energy-substitution-pathway, seasonal-arbitrage-trap

---

## Key Claims (Canonical IDs)

These claim pages are the authoritative formulations. Do not restate their arguments on other pages without linking to them.

| Claim slug | Canonical formulation | Confidence |
|---|---|---|
| `claim-timing-not-volume` | Nepal has a timing problem, not an energy shortage | high |
| `claim-mw-not-equal-value` | Installed MW, energy, seasonality, and firm power are routinely conflated | high |
| `claim-transmission-immediate-blocker` | Grid delivery is the #1 immediate monetization bottleneck | medium-high |
| `claim-storage-physical-fix` | Storage, not more RoR, is the physical solution to seasonal mismatch | high |
| `claim-solar-cheaper-than-small-hydro` | Utility solar is now cheaper than small RoR hydro on blended tariff | high |
| `claim-climate-harder-not-easier` | Climate change increases hydrological volatility and tail risks | high |
| `claim-governance-binding` | Institutional failures are now the binding constraint | medium-high |
| `claim-sediment-core-issue` | Sediment is a design constraint, not an O&M footnote | high |
| `claim-systems-conversion-failure` | Nepal fails to convert hydrological advantage into deliverable power | high |
| `claim-india-decisive-actor` | India's market rules and corridor control shape Nepal's options | high |
| `claim-domestic-led-strategy` | A domestic-first hydro strategy is economically and politically preferable to export-led | medium |
| `claim-ror-dominance` | >90% of Nepal's hydropower is RoR/PRoR, structurally amplifying seasonal mismatch | high |
| `claim-pror-not-storage` | Peaking run-of-river is often mistaken for seasonal storage | high |
| `claim-floating-pv-leverage` | Floating PV on reservoirs can improve dry-season output and reduce evaporation | medium |
| `claim-solar-terai-only-short-cycle-build` | Terai solar has shorter construction cycles than mountain hydro | high |
| `claim-solar-political-coalition-is-rural` | Solar's rural land-use footprint creates a different political coalition than hydro | medium |

---

## Disallowed Near-Synonyms

Do not create pages or use these terms as if they were distinct concepts. They are either disallowed aliases or should redirect to the canonical term.

| Disallowed term | Canonical term | Why |
|---|---|---|
| winter crisis | seasonal-mismatch | Too narrow; seasonal mismatch includes monsoon surplus as well as dry shortage |
| export paradox | seasonal-arbitrage-trap | Conflates symptom with mechanism |
| dam shortage | storage-deficit | Dams are one form of storage; the deficit is about seasonal inventory, not hardware count |
| base load | firm-power | Different concept; firm power can be peaking |
| solar replacement | solar-hydro-complementarity | Solar does not replace hydro |
| NEA monopoly | nea-triple-authority | Monopoly is only one dimension of the triple-role conflict |
| sediment problem | sediment-as-design-constraint | Vague; the concept is that sediment determines design viability |
| India threat | hydro-geopolitics | Too adversarial; hydro-geopolitics includes market integration |
| anti-export | domestic-led-hydro-strategy | Mischaracterizes the strategy; exports are used, just not led by |
| trade deficit | seasonal-arbitrage-trap | Refers to energy volume, not value destruction |

---

## Growth Protocol

This list is intentionally incomplete. New terms will be added through use. The protocol:

1. A term is used in a page and flagged in `wiki/FLAGGED_FOR_REVIEW.md`.
2. A human reviews whether it overlaps with existing canonical terms.
3. If it is genuinely new, it is added here with definition, aliases, and parent syntheses.
4. If it is a near-synonym, the page is redirected or merged.
5. If it is a disallowed alias, it is listed in the disallowed table.

**Last updated:** 2026-05-10
**Next review:** 2026-06-10
