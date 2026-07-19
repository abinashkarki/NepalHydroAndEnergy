# Structured monitoring data

The stable technical specification registry remains `project_specs.csv`. Stage 1 adds three complementary datasets rather than overloading that table:

- `project_events.csv` records dated, source-backed changes and disclosures.
- `project_blockers.csv` records the active constraint, responsible institution, and milestone it prevents.
- `corridor_specs.csv` records transmission status by physical segment and country.

The column and controlled-vocabulary contract is `wiki/monitoring-schema.json`. Every monitoring row must identify a canonical wiki slug, a direct evidence URL, a confidence level, and the date on which the evidence was checked. Announcements, financing proposals, approvals, effectiveness, disbursement, construction and operation are separate events; one must not be used as a proxy for another.

`curtailment-dispatch-schema.json` is a separate acquisition contract for
the operational records requested from NEA. It is a schema for records
that may be received; it does not imply that the requested records are
publicly available or complete.
