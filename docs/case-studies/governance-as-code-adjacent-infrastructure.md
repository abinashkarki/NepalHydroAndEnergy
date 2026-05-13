# Governance as code-adjacent infrastructure

*Keeping multi-session LLM editing honest on a public research wiki.*

## Summary

This case study is about the Nepal Energy Wiki and the repository-level mechanisms that let it absorb many LLM-assisted editing sessions without losing source discipline, accreting unsupported claims, or collapsing evidence and interpretation into one note layer.

The interesting result is not that LLMs can edit a wiki. The interesting result is that governance documents, templates, ontology files, validators, and an audit log — *code-adjacent infrastructure* — turned the repository into the control surface. Prompts point editors at the rules; the rules and validators constrain what can land in `main`.

This document explains how that works, what the audit log shows empirically, and where it still fails.

## Table of contents

1. [The problem](#1-the-problem)
2. [Repository as control surface](#2-repository-as-control-surface)
3. [The five mechanisms](#3-the-five-mechanisms)
4. [What the system actually caught](#4-what-the-system-actually-caught)
5. [What did not work](#5-what-did-not-work)
6. [Why this generalizes](#6-why-this-generalizes)
7. [Files you can lift](#7-files-you-can-lift)
8. [Open questions](#8-open-questions)
9. [Provenance](#9-provenance)

---

## 1. The problem

LLM editing of a long-lived knowledge corpus fails differently from LLM editing of code.

In code, bad outcomes are often loud: type errors, failing tests, CI red. In a wiki, bad outcomes are quiet: *epistemic drift*, *terminology fragmentation*, *citation inflation*, *unsourced numbers*, *confident summaries of contested evidence*. Each diff looks plausible. The damage shows up after many sessions, when readers cannot tell whether a paragraph is evidence or conclusion.

Concrete failure modes we saw before the governance layer hardened:

- **Hierarchy violations** — interpretation on source pages, strategic implications on data pages, prescriptions on concept pages.
- **Terminology drift** — near-synonyms used as if they were distinct concepts (`winter crisis` vs `seasonal mismatch`).
- **Backlink inflation** — `## Used By` lists built from memory instead of exact backlinks.
- **Confident summary** — two sources disagree; prose smooths them into agreement.
- **Scope creep** — a session meant for five pages touches twenty; the diff becomes unreviewable.

None of these are uniquely “agent” failures. They are what happens when any mixed team edits a corpus without *enforceable* discipline in the repo.

## 2. Repository as control surface

The pattern is small: a handful of markdown files plus Python validators. Together they are the control surface — legible in Git, reviewable in PRs, runnable locally.

```text
wiki/GOVERNANCE.md          # authority hierarchy + invariants
wiki/ONTOLOGY.md            # canonical terms, allowed/disallowed aliases
wiki/TEMPLATES.md           # section structure per page type
wiki/QUALITY_RUBRIC.md      # tier definitions
wiki/FLAGGED_FOR_REVIEW.md  # unresolved issues log
wiki/WIKI_AUDIT_LOG.md      # session-by-session record
docs/session-template.md    # prompt wrapper for editing sessions
scripts/validate_repo.py    # structural checks (fail + warn)
scripts/check_source_used_by.py
```

Principle: **the rules live in the repository**, not only in chat prompts. `AGENTS.md` and `CONTRIBUTING.md` point contributors at those files before they edit.

## 3. The five mechanisms

### 3.1 Authority hierarchy

`wiki/GOVERNANCE.md` defines a four-level hierarchy. Interpretive freedom increases **upward only**; pushing interpretation downward corrupts the structure.

| Level | Page types | Role | Must not |
|---|---|---|---|
| **L1 — Sources** | `sources/*` | Ingest and describe primary materials | Interpretation, synthesis conclusions, “so what” |
| **L2 — Data / Entities / Claims** | `data/*`, `entities/*`, `claims/*` | Facts, records, evidence-backed arguments | Data: no strategic implications. Entities: no prescriptions. Claims: no conclusions beyond cited evidence |
| **L3 — Syntheses** | `syntheses/*` | Connect evidence into arguments | Invent new primary facts |
| **L4 — Master thesis** | `syntheses/master-thesis.md` | Cross-synthesis framing | Ungrounded claims |

**Hard rule:** a page at level N may reference pages at any level ≤ N. It must not push interpretive content downward.

Ten **non-negotiable invariants** follow (full text in `GOVERNANCE.md`), including: no quantitative claim without source linkage; no interpretation inside source pages; no synthesis conclusions on data pages; no confidence inheritance across claims; never remove interpretive content without verifying downstream existence (invariant #10 documents that this rule “proved its value three times in the first cycle”).

### 3.2 Ontology

`wiki/ONTOLOGY.md` locks canonical terms: definition, allowed aliases, disallowed aliases (with *why*), parent syntheses, related pages. New terms are flagged in `FLAGGED_FOR_REVIEW.md` before they spread. That slows vocabulary growth; it also stops silent synonym explosion across sessions.

### 3.3 Templates

`wiki/TEMPLATES.md` ties each page category to a canonical section order and to **exemplar pages** (e.g. claim exemplar `claim-mw-not-equal-value`, source exemplar `wb-country-economic-memo-2025`). New pages copy shape, not prose.

### 3.4 Validators

`scripts/validate_repo.py` checks wikilinks, generated caches, map manifest, tracked-file hygiene, CSV/spec contracts, claim-registry integrity, public-facing language on entry files, and more.

It also warns (tier-aware) when pages lack required headings per `TEMPLATES.md` — e.g. claims need `## Boundary Conditions`; concepts need `## Summary`, `## Simple Explanation`, `## Common Misunderstandings`; data pages need `## Summary`, `## Coverage / Method`, `## Caveats`. Record-tier pages are skipped where the rubric says minimal pages are correct.

`scripts/check_source_used_by.py` compares each source page’s `## Used By` list to **exact backlinks** from the rest of the wiki (excluding other pages’ own `## Used By` bodies). That catches “looks cited” lists that are wrong.

### 3.5 Bounded sessions and audit log

`docs/session-template.md` caps work at **five pages per session**, requires reading `GOVERNANCE.md` and `ONTOLOGY.md` first, and defines a per-page loop: diagnose → propose → flag → confirm. Source `## Used By` must be built from grep/backlinks, not memory.

Every session that edits pages should append to `wiki/WIKI_AUDIT_LOG.md`: agent, pages touched, validation result, flags raised, patterns observed, decisions made. That log is the longitudinal dataset for “what keeps breaking.”

---

## 4. What the system actually caught

These patterns are documented in `wiki/WIKI_AUDIT_LOG.md` (primary evidence for this case study).

### 4.1 Hierarchy violations cluster by category

After early multi-week passes, the log recorded **highest violation rates on data and source pages** — where analysis is easiest to park next to numbers or next to a PDF summary. Claim and entity passes often showed **zero** hierarchy violations in the same batch size, while data/source batches showed interpretive language that belonged in syntheses or interventions.

Invariant #9 was added explicitly: **no policy prescriptions on concept or data pages** — prescriptions belong in syntheses and interventions.

### 4.2 Structural “cohort gaps”

Many pages were written **before** templates existed. The dominant fix was not “agents forgot sections” but **retrofitting**: missing `## Boundary Conditions` on claims, missing `## Simple Explanation` on concepts, missing `## Limitations` / `## Used By` on sources. The validator’s summary-by-category output turned that into a measurable burn-down (warning counts dropping session over session once tier-aware skipping was added).

### 4.3 Used By rebuilt from memory

The audit log records a failure mode where `## Used By` was reconstructed from recall rather than grep — plausible but false. The session template now mandates grep/backlinks; `check_source_used_by.py` enforces equality with actual backlinks.

### 4.4 Audit log vs disk

The log also recorded cases where the log said a change was applied but the file on disk did not match — a reminder that **the audit log is a claim**, not ground truth, until verified against `git diff` / file contents before push.

### 4.5 Cheap structural drift

Examples include section headings present but **wrong casing** (`## Boundary conditions` vs `## Boundary Conditions`), which strict heading checks surface. Small fixes, but they illustrate why “string match the template” beats “looks fine in preview.”

---

## 5. What did not work

**Throughput.** Five pages per session is slow for a large wiki. Relaxed batching only works when every page has the same structural diagnosis and zero factual flags.

**Validators ≠ research quality.** Structure can be perfect while a number is wrong. Confidence calibration and argument soundness remain human work; automated checks can flag inconsistencies (registry, duplicate IDs, missing sources) but not “is this claim true.”

**Confidence and ontology can disagree** — page vs canonical table. Resolution needs human judgment; the repo can record the decision and update one side.

**Ontology backlog is permanent** — new terms arrive faster than monthly review closes them. The protocol is “flag, don’t silently alias,” not “finish ontology.”

**Category renames are expensive** — validators, templates, paths, and log conventions move together; there is no single atomic “rename a page type.”

---

## 6. Why this generalizes

The five mechanisms transfer to any **long-lived corpus edited in sessions** — internal wikis, policy primers, compliance libraries, multi-author literature reviews — as long as you replace the *content* of ontology and templates with domain terms and section shapes.

One cross-cutting prediction worth keeping: **interpretation tends to accumulate on the lowest-authority pages** (data, sources) because they sit closest to raw evidence. Downward pressure is structural. The hierarchy and downstream-check rules resist that pressure for the life of the corpus, not for one editorial pass.

---

## 7. Files you can lift

| File | Role |
|---|---|
| `wiki/GOVERNANCE.md` | Hierarchy + invariants + session rules |
| `wiki/ONTOLOGY.md` | Canonical vocabulary |
| `wiki/TEMPLATES.md` | Section contracts + exemplars |
| `wiki/QUALITY_RUBRIC.md` | Tier semantics |
| `wiki/FLAGGED_FOR_REVIEW.md` | Open issues queue |
| `wiki/WIKI_AUDIT_LOG.md` | Session accountability + empirical patterns |
| `docs/session-template.md` | Reusable edit-session prompt |
| `scripts/validate_repo.py` | Fail/warn structural checks |
| `scripts/check_source_used_by.py` | Exact Used By ↔ backlinks |
| `AGENTS.md`, `CONTRIBUTING.md` | Entry points for humans and agents |

---

## 8. Open questions

- **Cross-session memory** — agents start cold; the full audit log is long. A short “primer” or generated state file may help without re-reading thousands of lines.
- **Analytical consistency checks** — same metric cited two ways on two pages; same claim with two confidences. Partial automation may be possible beyond current claim-registry checks.
- **Parallel human editors** — merge conflicts on the same page in one week are not fully exercised by a mostly single-human workflow.
- **Staleness** — annual sources (NEA reports, COD shifts) need a cadence; today that is partly manual plus flags.
- **Validator-driven authoring** — surfacing “next missing section” as the default task may shorten retrofit cycles.

---

## 9. Provenance

This case study describes mechanisms that exist in this repository. For authoritative wording of rules, read `wiki/GOVERNANCE.md`, `wiki/TEMPLATES.md`, and `wiki/ONTOLOGY.md`. For empirical session notes (violation rates, warning burn-down, Used By incidents, audit-vs-disk mismatches), read `wiki/WIKI_AUDIT_LOG.md`.

The Nepal Energy Wiki product overview remains in [transparentgov-nepal-energy-wiki.md](transparentgov-nepal-energy-wiki.md). The shorter agent workflow note is in [../architecture/transparentgov-agent-workflow.md](../architecture/transparentgov-agent-workflow.md).

---

*If you reuse this kit elsewhere and the same empirical patterns appear — or fail to appear — documenting that comparison would strengthen the general claim.*
