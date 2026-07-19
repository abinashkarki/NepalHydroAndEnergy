# Repository Boundaries

This repository is both a public knowledge product and a research production
workspace. Release readiness depends on keeping source material, generated
assets, deployable files, local scratch, and experiments distinct.

## Path Classes

| Class | Paths | Rule |
|---|---|---|
| Source | `wiki/pages/`, `data/project_specs.csv`, `data/solar_project_specs.csv`, `wiki/*.md`, `docs/`, `AGENTS.md`, `README.md`, `CONTRIBUTING.md` | Hand-authored or hand-curated. Review content and provenance directly. |
| Generated | `wiki/explorer/shared/wiki-*.json`, `wiki/explorer/shared/claim-governance.json`, `data/processed/maps/`, `data/processed/tables/`, selected `wiki/assets/figures/` | Rebuild from declared scripts. Do not hand-edit unless the owning script documents that workflow. |
| Deployable | `wiki/`, `wiki/explorer/`, `wiki/assets/`, `data/processed/maps/` | Public-facing static site surface. Must not contain local-only debug artifacts. |
| Development | `scripts/`, `tests/`, `notes/`, `data/raw/`, `requirements*.txt`, `Makefile` | Tooling, raw-source inventory, and working research support. |
| Internal tools | `internal/` | Committed, localhost-only research operations interfaces. Must not be linked from or copied into public deployable surfaces. |
| Local-only | `.venv/`, `.playwright-cli/`, `output/`, `tmp/`, `test-results/`, local screenshot folders, browser traces | Never track unless explicitly promoted to documented fixtures. |
| Experimental | `wiki/explorer/3d-terrain.*`, `wiki/explorer/lib/cesium/`, documentary/video production workspace | Keep out of release surfaces unless promoted through a documented product decision. |

## Release Rules

- `make release-check` is the public release gate.
- `make validate` is the fast structural gate and includes the source-page
  computed `Used By` policy.
- `make test` is the stricter behavior/search/source-integrity gate.
- Generated files committed to the repo must be listed in
  `docs/generated-assets.json`.
- Local screenshots, browser logs, backup files, and debug captures should not
  be tracked in product directories.
- Source-page `Used By` lists are rendered from
  `wiki/explorer/shared/wiki-backlinks.json`; source markdown must not contain
  manually maintained `## Used By` sections.

## Analysis Layer

The public analytical layer sits above the governed wiki hierarchy:

```text
sources -> data/entities/claims -> syntheses/interventions -> analysis/public narrative
```

Analysis should draw from the governed corpus and evidence trails. It should not
push interpretation back down into source pages, data pages, or project records.
