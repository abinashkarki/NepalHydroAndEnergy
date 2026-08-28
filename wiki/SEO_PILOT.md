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

`wiki/seo-pilot-sitemap.xml` is the production sitemap for this five-page pilot. It can be submitted directly after deployment, but it is not yet advertised by the domain-root robots file. Domain-root `https://transparentgov.ai/robots.txt`, `/sitemap.xml`, redirects and branded 404 behavior remain owned by the separate TransparentGov deployment project and can be coordinated in the broader SEO phase.

The generated routes and manifest are approved for this bounded production pilot. This approval does not authorize expansion beyond the five listed pages. Before a broader rollout:

1. Confirm the deployed host serves `/wiki/<slug>/index.html` as `/wiki/<slug>/`.
2. Confirm invalid routes return a real 404.
3. Decide redirect timing for `/wiki/explorer/?page=<slug>`.
4. Publish a full-wiki sitemap through the domain-root deployment.
5. Submit the sitemap and monitor indexing through Search Console.
