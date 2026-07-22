# Nepal Energy Wiki Infrastructure

This file is the short operational map for the wiki. It defines which local
checkout is authoritative, how a reviewed revision reaches production, and
which older workspaces must not be used for releases.

## Canonical locations

| Role | Location | Authority |
|---|---|---|
| Active wiki development and releases | `/Users/hi/projects/nepalEnergy-wiki` | Clean checkout of `abinashkarki/NepalHydroAndEnergy`; use this folder for wiki changes, validation, tags and production records. |
| Hosting application | `/Users/hi/projects/transparentgov-app` | Clean checkout of `abinashkarki/TransparentGov`; use this folder for Docker and FastAPI hosting changes. |
| Original research and documentary workspace | `/Users/hi/projects/nepalEnergy` | Preserved working tree with pre-existing local changes. It is not a release checkout. |
| Mobile/beta worktree | `/Users/hi/projects/nepalEnergy-mobile-ux` | Temporary branch worktree; merge or archive its branch explicitly. It is not a release checkout. |
| Frozen migration precursor | `/Users/hi/projects/archive/nepalEnergy-v1-frozen-2026-07-22` | Recoverable historical snapshot. Do not develop or deploy from it. |

The current production pointer is recorded in `release/production.json`. That
record, rather than a folder name or mutable branch, is the authority for what
is live.

## Production path

```text
NepalHydroAndEnergy reviewed commit
        |
        | GitHub tarball for NEPAL_ENERGY_REF=<full commit SHA>
        v
TransparentGov Docker build
        |
        | copies wiki/ and data/processed/maps/
        v
/app/static/wiki and /app/static/data/processed/maps
        |
        | FastAPI StaticFiles, Uvicorn, Coolify/Traefik
        v
https://transparentgov.ai/wiki/explorer/
```

Merging wiki changes does not update production by itself. Coolify is pinned to
an immutable wiki commit and must rebuild the TransparentGov image before a new
wiki revision becomes live.

## Routine commands

```bash
cd /Users/hi/projects/nepalEnergy-wiki
make release-check
make serve
python scripts/check_production_wiki.py --expect-local
```

For a release, follow `docs/releasing-and-rollback.md`. In summary:

1. Merge a reviewed wiki PR.
2. Tag the exact merge commit with `scripts/tag_wiki_release.sh`.
3. Set Coolify `NEPAL_ENERGY_REF` to that full commit SHA.
4. Force a build without cache.
5. Run the production probe and browser QA.
6. Record the verified deployment in `release/production.json`.

## Repository boundary

Keep the repositories separate:

- `NepalHydroAndEnergy` owns wiki content, explorer code, structured energy
  data, generated indexes, map layers and release evidence.
- `TransparentGov` owns the hosting shell, FastAPI service, Docker image,
  domain routing and runtime headers.

This separation keeps content review independent from platform deployment while
the immutable `NEPAL_ENERGY_REF` makes the integration reproducible.

