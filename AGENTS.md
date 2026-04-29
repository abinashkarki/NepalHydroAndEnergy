# AGENTS.md — nepalEnergy

Instructions for AI agents (Claude, Codex, etc.) working in this repository.

## Deployment Architecture

This repo is a **content source**, not a deployed app. The live site at `https://transparentgov.ai/wiki/explorer/` is served by a separate project:

| Repo | Role |
|---|---|
| **`abinashkarki/NepalHydroAndEnergy`** (this repo) | Wiki content, map data, explorer frontend |
| **`abinashkarki/TransparentGov`** | Production site — Coolify/Docker host |

### How deployment works

TransparentGov's [`Dockerfile`](https://github.com/abinashkarki/TransparentGov/blob/main/Dockerfile) pulls this repo's wiki and map data at **build time** via GitHub tarball:

```dockerfile
ARG NEPAL_ENERGY_REF=main
RUN curl -L \
  "https://github.com/abinashkarki/NepalHydroAndEnergy/archive/${NEPAL_ENERGY_REF}.tar.gz" ...
COPY --from=wiki-fetch /src/nepalEnergy/wiki ./static/wiki
COPY --from=wiki-fetch /src/nepalEnergy/data/processed/maps ./static/data/processed/maps
```

### What gets deployed

Only two directories are shipped to production:
- `wiki/` — wiki pages, explorer frontend (index.html), shared metadata
- `data/processed/maps/` — GeoJSON layer data

Other directories (`scripts/`, `docs/`, `notes/`, `figures/`, `data/raw/`) are **not deployed**.

### Branch flow

| Branch | Purpose |
|---|---|
| **`main`** | Production. Pushed here → redeploy TransparentGov to go live. |
| `codex/*` | Feature branches. Merged into `main` when ready. |

### Deploy checklist

1. Push changes to `main` on this repo
2. Redeploy TransparentGov on Coolify (or wait for auto-deploy if configured)
3. The Docker build will pull the latest `main` tarball

To pin a specific commit instead of `main`, set the `NEPAL_ENERGY_REF` env var in Coolify to a commit SHA.

### TransparentGov project location

The sibling repo is at `/Users/hi/projects/TransparentGov` on the local machine. Its Dockerfile and Coolify config control the live deployment.

## Local Development

```bash
# Install deps
python -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt

# Regenerate wiki metadata (backlinks, search index, page index, presets)
make wiki-index

# Validate generated files
make validate

# Serve explorer locally
make serve     # or: ./wiki/explorer/serve.sh 8765
# Then open: http://localhost:8765/wiki/explorer/
```

## Key Paths

| Path | What |
|---|---|
| `wiki/explorer/index.html` | Main explorer app (Leaflet map + wiki browser) |
| `wiki/explorer/shared/` | Layer manifest, presets, bindings, tour, search index, page metadata |
| `scripts/build_tributary_maps.py` | Main geo-data builder (annotations, corridors, scenario layers) |
| `data/processed/maps/` | Built GeoJSON outputs — shipped to production |
| `wiki/pages/` | Wiki content (markdown, interlinked) |

## CesiumJS / 3D Terrain

A 3D terrain explorer PoC exists locally under `wiki/explorer/3d-terrain.html` with CesiumJS in `wiki/explorer/lib/cesium/`. This is **not production-ready** and should not be committed or pushed. Keep it local-only until the phase matures.
