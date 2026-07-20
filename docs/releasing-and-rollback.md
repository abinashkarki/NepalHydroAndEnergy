# Wiki Release and Rollback Runbook

This wiki is published inside the separate
[`abinashkarki/TransparentGov`](https://github.com/abinashkarki/TransparentGov)
application. Coolify builds that application, and its Dockerfile downloads this
repository using the `NEPAL_ENERGY_REF` build argument.

Production must use a full 40-character wiki commit SHA for that argument. A
branch name such as `main` is convenient during development but is mutable and
does not identify what was deployed.

## Release contract

- `make release-check` is the content and explorer release gate.
- `release/production.json` records the last verified production release.
- `wiki-vX.Y.Z` annotated tags provide human-readable, immutable release names.
- `NEPAL_ENERGY_REF=<full commit SHA>` tells the TransparentGov Docker build
  exactly which wiki revision to fetch.
- A new TransparentGov commit or Coolify **Force deploy (without cache)** is
  required when Coolify would otherwise reuse an image built from the same
  TransparentGov commit.

Never move or reuse a published release tag. The full commit SHA remains the
deployment authority even when an annotated tag is available.

## Release procedure

1. Merge the reviewed wiki change into `main` and fetch it locally.

   ```bash
   git fetch origin main --tags
   git switch main
   git pull --ff-only origin main
   make release-check
   ```

2. Record the exact commit and preflight an annotated tag. Replace the example
   version and SHA deliberately.

   ```bash
   WIKI_RELEASE_COMMIT="$(git rev-parse origin/main)"
   scripts/tag_wiki_release.sh 1.1.0 "$WIKI_RELEASE_COMMIT"
   scripts/tag_wiki_release.sh 1.1.0 "$WIKI_RELEASE_COMMIT" --push
   ```

   The script refuses short SHAs, commits not reachable from `origin/main`, and
   any release tag that already exists on the remote.

3. In Coolify, set the TransparentGov application's build argument/environment
   value to the immutable source revision:

   ```text
   NEPAL_ENERGY_REF=<the full WIKI_RELEASE_COMMIT value>
   ```

   Save the setting before triggering the build. This is a required manual
   production setting; the repository scripts cannot inspect the logged-in
   Coolify configuration.

4. Trigger a build using one of these paths:

   - Select **Force deploy (without cache)** in Coolify; or
   - create a clean, empty TransparentGov trigger commit through the guarded
     script below. This changes the parent application's commit SHA, preventing
     Coolify from treating the existing image as current.

   ```bash
   scripts/trigger_transparentgov_rebuild.sh "$WIKI_RELEASE_COMMIT"
   CONFIRM_COOLIFY_REF="$WIKI_RELEASE_COMMIT" \
     scripts/trigger_transparentgov_rebuild.sh "$WIKI_RELEASE_COMMIT" --execute
   ```

   The first command is read-only. The second requires an authenticated `gh`
   session with Contents write permission to `abinashkarki/TransparentGov` (or
   a `GH_TOKEN` with that permission). It creates an empty commit using the
   current remote `main` tree and performs a non-forced, fast-forward ref update.
   It does not use or modify a local TransparentGov checkout.

5. Confirm that the Coolify log ran the Docker build and downloaded the pinned
   wiki ref. A message saying the build was skipped because the same image was
   found means the release has not been rebuilt.

6. Verify production before updating the record:

   - the explorer returns HTTP 200;
   - `state-of-the-system` and one map-heavy page render;
   - the production page-index count is expected;
   - selected asset SHA-256 hashes match the source commit;
   - the browser console has no new errors.

7. Update `release/production.json` in a follow-up reviewed commit with the
   deployed wiki SHA, TransparentGov SHA, deployment identifier, UTC timestamps,
   page count, and verification hashes. Then run:

   ```bash
   make release-record-check
   ```

## Rollback procedure

Rollback is a new deployment of a previously verified commit, not a force-push
and not a moved tag.

1. Read the last known-good immutable SHA from Git history for
   `release/production.json` or from a prior release tag.
2. Confirm the commit exists and inspect the release record.
3. Set Coolify's `NEPAL_ENERGY_REF` to that full SHA.
4. use **Force deploy (without cache)** or run the guarded TransparentGov rebuild
   trigger with the rollback SHA.
5. Repeat the production verification checks.
6. Commit a new production record describing the rollback and its reason.

If only the wiki is affected, do not roll back the database or other
TransparentGov services. If the parent application is also faulty, use the
TransparentGov repository's own rollback procedure in addition to pinning the
wiki SHA.

## Cache-trap explanation

The wiki repository is downloaded during the TransparentGov Docker build. A
regular Coolify redeploy can reuse the existing image when the TransparentGov
Git commit has not changed, even if this repository's `main` branch has moved.
Changing the wiki branch alone therefore does not prove that production was
rebuilt. Pinning the wiki SHA makes the intended input auditable; forcing a
no-cache build or advancing the parent commit makes Coolify execute the build.
