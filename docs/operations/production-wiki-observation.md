# Production Wiki Observation

## Purpose

The production probe checks whether the deployed wiki is a complete, internally
consistent static release. It is safe to run against production: it only makes
GET requests and does not require Coolify credentials.

Run the routine health check from the repository root:

```bash
python scripts/check_production_wiki.py
```

After a deployment, also compare the production release with the current local
checkout:

```bash
python scripts/check_production_wiki.py --expect-local
```

`--expect-local` compares the explorer shell, page index, wiki loader and map
manifest byte-for-byte. Use it from the exact commit or tag intended for
production. A normal development branch is expected to differ from production.
Use `--json` when a CI job or uptime monitor needs machine-readable output.

## What the probe covers

- Explorer HTML and essential JavaScript, CSS and JSON assets return HTTP 200.
- The page index, lexical search index and vector index agree on page coverage,
  the structured fact index is non-empty, and the 14-page editorial spine is
  present.
- Every unique GeoJSON file referenced by the deployed layer manifest exists and
  parses as a Feature or FeatureCollection.
- Representative wiki pages load from the category declared by the live index.
- A deliberately missing asset returns 404 rather than a misleading HTML shell.
- Static responses carry a cache validator; missing explicit cache policy is
  reported as a warning.
- Response latency is summarized and individual responses over two seconds are
  warned about, not failed, because a single operator-side probe is not an SLO.
- The explorer declares a mobile viewport and ships responsive CSS breakpoints.

The command exits `0` when the publication contract passes and `1` when it finds
a broken endpoint, malformed index, missing core page, malformed map file or
release-identity mismatch. Warnings do not change the exit status.

## Post-deployment runbook

1. Run the local release gate before deploying.
2. Deploy from the intended immutable release reference.
3. Run `python scripts/check_production_wiki.py --expect-local` from that exact
   checkout.
4. Open the production explorer at desktop and mobile widths. Confirm that the
   overview and solar presets render, search returns results, and a map feature
   can open its linked wiki page. Check the browser console for errors.
5. Record the deployment reference, probe output and any visual exceptions in
   the release log. If identity fails, do not describe the release as live.

## Observation recorded 2026-07-20

The production explorer passed the static publication contract with 418 indexed
pages and all layer-manifest GeoJSON assets available. The deployed core release
assets matched the release checkout at the time of observation.

Static responses provide `ETag` and/or `Last-Modified` validators, but no
explicit `Cache-Control` header was observed. That is not an availability
failure, although an explicit policy would make browser and CDN freshness more
predictable. GeoJSON currently arrives as `text/plain` rather than a JSON media
type. Browsers can still parse it with `response.json()`, but serving
`application/geo+json` or `application/json` would make the contract clearer.

## Remaining monitoring gaps

This probe is synthetic and operator-triggered. It does not provide continuous
uptime history, real-user performance, client-side exception collection,
unsuccessful-search telemetry, broken outbound-source monitoring or automated
visual regression. It also cannot prove that touch interactions, Leaflet tiles,
popups and panel transitions work merely from HTTP responses; the browser step
in the runbook remains required.

If analytics are added, prefer aggregate, privacy-respecting events: page slug,
preset, successful versus empty search, coarse load timing and browser error
class. Do not collect search text, precise location, IP-derived profiles or
persistent user identifiers.
