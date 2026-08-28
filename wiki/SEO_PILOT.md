# Unified Wiki Route Pilot

This bounded pilot materializes five governed wiki pages at clean routes while preserving the existing explorer as the only reader experience:

- `/wiki/glof-risk/`
- `/wiki/rasuwagadhi/`
- `/wiki/icimod-ndrrma-thame-glof-2024/`
- `/wiki/ndrrma-rasuwa-glacial-flood-sitrep-2025/`
- `/wiki/nea-engineering-annual-report-2081-82/`

The source of truth remains `wiki/pages/`. Rebuild the pilot with:

```bash
make seo-pilot
```

Each generated route is a copy of `wiki/explorer/index.html`, not a separate landing-page design. The generator injects page-specific metadata, JSON-LD, a query-free canonical, readable article HTML in the existing reader pane and initial-page bootstrap data. A base URL keeps the explorer's shared scripts, styles, wiki data and map data resolving from their existing locations. After JavaScript initializes, the normal explorer loads the same topic and its existing map binding.

The five slugs exercise the approved coverage:

- `rasuwagadhi`: spatial project and map-focus behavior.
- `glof-risk`: concept page with substantial related links.
- `icimod-ndrrma-thame-glof-2024`: non-spatial source and provenance.
- `ndrrma-rasuwa-glacial-flood-sitrep-2025`: long nested-route edge case.
- `nea-engineering-annual-report-2081-82`: source page with meaningful pilot backlinks.

Links to pages outside the pilot continue to use `/wiki/explorer/?page=<slug>`. The legacy query route remains compatible. Redirecting or canonicalizing all legacy page queries is a deployment decision for after the full clean-route set is approved.

`wiki/seo-pilot-sitemap.xml` is a review artifact, not the production sitemap. It is intentionally not advertised in a repository-local robots file. The domain-root `https://transparentgov.ai/robots.txt`, `/sitemap.xml`, redirects and 404 behavior are owned by the separate TransparentGov deployment project and must be coordinated there after this pilot passes human review and a live nested-index probe.

The generated routes and manifest are marked non-deployable until human review. Before expanding beyond five pages:

1. Confirm the deployed host serves `/wiki/<slug>/index.html` as `/wiki/<slug>/`.
2. Confirm invalid routes return a real 404.
3. Approve the unified explorer experience and decide redirect timing for `/wiki/explorer/?page=<slug>`.
4. Publish the full 406-page sitemap through the domain-root deployment.
5. Submit the sitemap and monitor indexing through Search Console.
