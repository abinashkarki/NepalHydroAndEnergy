#!/usr/bin/env node
"use strict";

const fs = require("fs");
const path = require("path");
const { marked } = require("../wiki/explorer/shared/marked.min.js");

const ROOT = path.resolve(__dirname, "..");
const WIKI = path.join(ROOT, "wiki");
const CONFIG_PATH = path.join(WIKI, "seo-pilot-slugs.json");
const PAGE_INDEX_PATH = path.join(WIKI, "explorer", "shared", "wiki-page-index.json");
const PAGE_META_PATH = path.join(WIKI, "explorer", "shared", "wiki-page-meta.json");
const BACKLINKS_PATH = path.join(WIKI, "explorer", "shared", "wiki-backlinks.json");
const EXPLORER_TEMPLATE_PATH = path.join(WIKI, "explorer", "index.html");
const MANIFEST_PATH = path.join(WIKI, "seo-pilot-manifest.json");
const SITEMAP_PATH = path.join(WIKI, "seo-pilot-sitemap.xml");
const CHECK = process.argv.includes("--check");
const APPROVED_PILOT_SLUGS = [
  "glof-risk",
  "rasuwagadhi",
  "icimod-ndrrma-thame-glof-2024",
  "ndrrma-rasuwa-glacial-flood-sitrep-2025",
  "nea-engineering-annual-report-2081-82",
];

function readJSON(filePath) {
  return JSON.parse(fs.readFileSync(filePath, "utf8"));
}

function escapeHtml(value) {
  return String(value ?? "").replace(/[&<>"']/g, (char) => ({
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
    '"': "&quot;",
    "'": "&#39;",
  }[char]));
}

function escapeXml(value) {
  return escapeHtml(value);
}

function replaceOnce(source, marker, replacement, label) {
  const first = source.indexOf(marker);
  if (first === -1) throw new Error(`explorer template marker missing: ${label}`);
  if (source.indexOf(marker, first + marker.length) !== -1) {
    throw new Error(`explorer template marker is not unique: ${label}`);
  }
  return `${source.slice(0, first)}${replacement}${source.slice(first + marker.length)}`;
}

function splitFrontmatter(text) {
  if (!text.startsWith("---\n")) return { frontmatter: "", body: text };
  const end = text.indexOf("\n---", 4);
  if (end === -1) return { frontmatter: "", body: text };
  return {
    frontmatter: text.slice(4, end).trim(),
    body: text.slice(end + 4).replace(/^\s+/, ""),
  };
}

function frontmatterScalar(frontmatter, key) {
  const escapedKey = key.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
  const match = frontmatter.match(new RegExp(`^${escapedKey}:\\s*(.*?)\\s*$`, "m"));
  if (!match) return "";
  return match[1].trim().replace(/^(["'])(.*)\1$/, "$2");
}

function cleanDescription(value, maxLength = 160) {
  const clean = String(value || "").replace(/\s+/g, " ").trim();
  if (clean.length <= maxLength) return clean;
  const boundary = clean.lastIndexOf(" ", maxLength - 1);
  return `${clean.slice(0, boundary > 100 ? boundary : maxLength - 1).trim()}…`;
}

function safeExternalUrl(value) {
  if (!value) return "";
  try {
    const parsed = new URL(value);
    return parsed.protocol === "https:" || parsed.protocol === "http:" ? parsed.href : "";
  } catch (_error) {
    return "";
  }
}

function sanitizeRenderedHtml(value) {
  return String(value)
    .replace(/<!--[\s\S]*?-->/g, "")
    .replace(/<(script|style|iframe|object|embed)\b[^>]*>[\s\S]*?<\/\1>/gi, "")
    .replace(/<(script|style|iframe|object|embed)\b[^>]*\/?>/gi, "")
    .replace(/\s+on[a-z]+\s*=\s*("[^"]*"|'[^']*'|[^\s>]+)/gi, "")
    .replace(/\s+style\s*=\s*("[^"]*"|'[^']*'|[^\s>]+)/gi, "")
    .replace(/\s+(href|src)\s*=\s*(["'])\s*(?:javascript|data):[\s\S]*?\2/gi, ' $1="#"');
}

function routeForSlug(slug, pilotSlugs) {
  if (pilotSlugs.has(slug)) return `/wiki/${encodeURIComponent(slug)}/`;
  return `/wiki/explorer/?page=${encodeURIComponent(slug)}`;
}

function rewriteWikilinks(markdown, pageIndex, pilotSlugs) {
  const known = new Set(pageIndex.allSlugs || []);
  return markdown.replace(/\[\[([^\]|]+)(?:\|([^\]]+))?\]\]/g, (_whole, rawTarget, rawLabel) => {
    const slug = rawTarget.trim();
    const label = (rawLabel || (pageIndex.slugToTitle || {})[slug] || slug).trim();
    if (!known.has(slug)) return escapeHtml(label);
    const href = routeForSlug(slug, pilotSlugs);
    const route = pilotSlugs.has(slug) ? "canonical-page" : "explorer-fallback";
    return `<a href="${escapeHtml(href)}" data-route="${route}">${escapeHtml(label)}</a>`;
  });
}

function renderBacklinks(slug, category, backlinks, pilotSlugs) {
  const references = (backlinks.backlinks || {})[slug] || [];
  if (!references.length) return "";
  const heading = category === "sources" ? "Used By" : "Referenced By";
  const items = references.map((item) => {
    const href = routeForSlug(item.slug, pilotSlugs);
    const route = pilotSlugs.has(item.slug) ? "canonical-page" : "explorer-fallback";
    return `<li><a href="${escapeHtml(href)}" data-route="${route}">${escapeHtml(item.title || item.slug)}</a><span>${escapeHtml(item.category || "page")}</span></li>`;
  }).join("\n");
  return `<aside class="backlinks" aria-labelledby="backlinks-heading">
    <h2 id="backlinks-heading">${heading} <span>${references.length}</span></h2>
    <ul>${items}</ul>
  </aside>`;
}

function renderProvenance(category, frontmatter) {
  if (category !== "sources") return "";
  const author = frontmatterScalar(frontmatter, "source_author");
  const date = frontmatterScalar(frontmatter, "source_date");
  const type = frontmatterScalar(frontmatter, "source_type");
  const url = safeExternalUrl(frontmatterScalar(frontmatter, "source_url"));
  const rows = [
    ["Author", author],
    ["Source date", date],
    ["Source type", type],
  ].filter(([, value]) => value).map(([label, value]) => `<div><dt>${escapeHtml(label)}</dt><dd>${escapeHtml(value)}</dd></div>`).join("\n");
  const sourceLink = url
    ? `<a class="source-link" href="${escapeHtml(url)}" rel="noopener noreferrer">Open the original source ↗</a>`
    : "";
  return `<aside class="provenance" aria-labelledby="provenance-heading">
    <h2 id="provenance-heading">Source record</h2>
    <dl>${rows}</dl>
    ${sourceLink}
  </aside>`;
}

function structuredData({ canonical, category, description, frontmatter, meta, siteName }) {
  const sourceUrl = safeExternalUrl(frontmatterScalar(frontmatter, "source_url"));
  const sourceAuthor = frontmatterScalar(frontmatter, "source_author");
  const created = frontmatterScalar(frontmatter, "created");
  const entityType = category === "sources" ? "Report" : "Article";
  const mainEntity = {
    "@type": entityType,
    "@id": `${canonical}#article`,
    name: meta.title,
    headline: meta.title,
    description,
    url: canonical,
    datePublished: category === "sources" ? undefined : created || undefined,
    dateModified: meta.updated || undefined,
    keywords: (meta.tags || []).join(", ") || undefined,
  };
  if (category === "sources" && sourceUrl) mainEntity.sameAs = sourceUrl;
  if (category === "sources" && sourceAuthor) {
    mainEntity.author = { "@type": "Organization", name: sourceAuthor };
  }
  Object.keys(mainEntity).forEach((key) => mainEntity[key] === undefined && delete mainEntity[key]);
  return {
    "@context": "https://schema.org",
    "@graph": [
      {
        "@type": "WebPage",
        "@id": canonical,
        url: canonical,
        name: meta.title,
        description,
        datePublished: created || undefined,
        dateModified: meta.updated || undefined,
        isPartOf: {
          "@type": "WebSite",
          "@id": "https://transparentgov.ai/#website",
          name: siteName,
          url: "https://transparentgov.ai/wiki/explorer/",
        },
        mainEntity: { "@id": `${canonical}#article` },
      },
      mainEntity,
      {
        "@type": "BreadcrumbList",
        "@id": `${canonical}#breadcrumbs`,
        itemListElement: [
          { "@type": "ListItem", position: 1, name: siteName, item: "https://transparentgov.ai/wiki/explorer/" },
          { "@type": "ListItem", position: 2, name: meta.title, item: canonical },
        ],
      },
    ],
  };
}

function renderPage({ slug, category, meta, markdown, pageIndex, backlinks, config, pilotSlugs, explorerTemplate }) {
  const { frontmatter, body } = splitFrontmatter(markdown);
  const description = cleanDescription(meta.excerpt || meta.body_text || meta.title);
  const canonical = `${config.canonical_base.replace(/\/$/, "")}/${encodeURIComponent(slug)}/`;
  const explorerUrl = `/wiki/explorer/?page=${encodeURIComponent(slug)}`;
  const linkedMarkdown = rewriteWikilinks(body, pageIndex, pilotSlugs);
  const articleHtml = sanitizeRenderedHtml(marked.parse(linkedMarkdown, { gfm: true }));
  const jsonLd = JSON.stringify(structuredData({ canonical, category, description, frontmatter, meta, siteName: config.site_name }))
    .replace(/</g, "\\u003c");
  const updated = meta.updated ? `<time datetime="${escapeHtml(meta.updated)}">Updated ${escapeHtml(meta.updated)}</time>` : "";
  const quality = meta.page_quality ? `<span>${escapeHtml(meta.page_quality)}</span>` : "";
  const provenance = renderProvenance(category, frontmatter);
  const backlinkHtml = renderBacklinks(slug, category, backlinks, pilotSlugs);
  const title = `${meta.title} · ${config.site_name}`;
  const routeBootstrap = JSON.stringify({ mode: "subject", slug, canonical }).replace(/</g, "\\u003c");
  const preRenderedArticle = `<!-- wiki-route-prerender:start -->
  <div class="wiki-route-prerender">
    <div style="font-family:var(--sans);font-size:11px;text-transform:uppercase;letter-spacing:.06em;color:var(--ink-soft);margin-bottom:6px">${escapeHtml(category)} · ${escapeHtml(slug)}${updated ? ` · ${updated}` : ""}${quality ? ` · ${quality}` : ""}</div>
${provenance ? `    ${provenance}\n` : ""}    <article class="wiki-article">${articleHtml}</article>
${backlinkHtml ? `    ${backlinkHtml}\n` : ""}  </div>
  <!-- wiki-route-prerender:end -->`;
  const head = `  <meta name="generator" content="scripts/build_wiki_seo.js" />
  <meta name="np-initial-page" content="${escapeHtml(slug)}" />
  <base href="/wiki/explorer/" />
  <title>${escapeHtml(title)}</title>
  <meta name="description" content="${escapeHtml(description)}" />
  <meta name="robots" content="index,follow,max-image-preview:large" />
  <link rel="canonical" href="${escapeHtml(canonical)}" />
  <meta property="og:type" content="article" />
  <meta property="og:site_name" content="${escapeHtml(config.site_name)}" />
  <meta property="og:title" content="${escapeHtml(title)}" />
  <meta property="og:description" content="${escapeHtml(description)}" />
  <meta property="og:url" content="${escapeHtml(canonical)}" />
  <meta name="twitter:card" content="summary" />
  <meta name="twitter:title" content="${escapeHtml(title)}" />
  <meta name="twitter:description" content="${escapeHtml(description)}" />
  <script type="application/ld+json">${jsonLd}</script>
  <script>window.__WIKI_ROUTE_BOOTSTRAP__ = ${routeBootstrap};</script>`;
  let shellHtml = replaceOnce(
    explorerTemplate,
    "  <title>Nepal Energy · Wiki & Map</title>",
    head,
    "generic explorer title",
  );
  shellHtml = replaceOnce(
    shellHtml,
    '      <div class="markdown" id="page"></div>',
    `      <div class="markdown" id="page" data-prerendered-slug="${escapeHtml(slug)}">${preRenderedArticle}</div>`,
    "reader page slot",
  );

  return {
    canonical,
    description,
    explorerUrl,
    html: shellHtml,
  };
}

function expectedOutputs() {
  const config = readJSON(CONFIG_PATH);
  const pageIndex = readJSON(PAGE_INDEX_PATH);
  const pageMeta = readJSON(PAGE_META_PATH);
  const backlinks = readJSON(BACKLINKS_PATH);
  const explorerTemplate = fs.readFileSync(EXPLORER_TEMPLATE_PATH, "utf8");
  const metaBySlug = new Map((pageMeta.pages || []).map((page) => [page.slug, page]));
  const pilotSlugs = new Set(config.slugs || []);
  const allSlugs = new Set(pageIndex.allSlugs || []);
  const outputs = new Map();
  const manifestPages = [];

  if (pilotSlugs.size !== (config.slugs || []).length) throw new Error("seo pilot contains duplicate slugs");
  if (JSON.stringify(config.slugs || []) !== JSON.stringify(APPROVED_PILOT_SLUGS)) {
    throw new Error("seo pilot config does not match the user-approved five-page scope");
  }
  for (const slug of config.slugs || []) {
    if (!allSlugs.has(slug)) throw new Error(`unknown seo pilot slug: ${slug}`);
    const category = pageIndex.slugToCategory[slug];
    const sourcePath = path.join(WIKI, "pages", category, `${slug}.md`);
    const meta = metaBySlug.get(slug);
    if (!meta || !fs.existsSync(sourcePath)) throw new Error(`missing input for seo pilot slug: ${slug}`);
    const rendered = renderPage({
      slug,
      category,
      meta,
      markdown: fs.readFileSync(sourcePath, "utf8"),
      pageIndex,
      backlinks,
      config,
      pilotSlugs,
      explorerTemplate,
    });
    const outputPath = path.join(WIKI, slug, "index.html");
    outputs.set(outputPath, rendered.html);
    manifestPages.push({
      slug,
      category,
      title: meta.title,
      updated: meta.updated || null,
      source: path.relative(ROOT, sourcePath),
      output: path.relative(ROOT, outputPath),
      canonical: rendered.canonical,
      explorer_url: rendered.explorerUrl,
      description: rendered.description,
    });
  }

  const manifest = `${JSON.stringify({
    version: 1,
    mode: "unified-explorer-route-pilot",
    discovery_status: "not-advertised-pending-host-review",
    root_robots_owner: "TransparentGov deployment project (outside this repository)",
    total_wiki_pages: (pageIndex.allSlugs || []).length,
    generated_pages: manifestPages.length,
    pages: manifestPages,
  }, null, 2)}\n`;
  outputs.set(MANIFEST_PATH, manifest);

  const sitemapEntries = manifestPages.map((page) => `  <url>\n    <loc>${escapeXml(page.canonical)}</loc>\n    ${page.updated ? `<lastmod>${escapeXml(page.updated)}</lastmod>\n    ` : ""}<changefreq>monthly</changefreq>\n  </url>`).join("\n");
  outputs.set(SITEMAP_PATH, `<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n${sitemapEntries}\n</urlset>\n`);
  return outputs;
}

function unexpectedGeneratedPages(outputs) {
  const expected = new Set([...outputs.keys()].map((entry) => path.resolve(entry)));
  const unexpected = [];
  for (const entry of fs.readdirSync(WIKI, { withFileTypes: true })) {
    if (!entry.isDirectory()) continue;
    const candidate = path.join(WIKI, entry.name, "index.html");
    if (!fs.existsSync(candidate) || expected.has(path.resolve(candidate))) continue;
    const content = fs.readFileSync(candidate, "utf8");
    if (content.includes('name="generator" content="scripts/build_wiki_seo.js"')) {
      unexpected.push(path.relative(ROOT, candidate));
    }
  }
  return unexpected;
}

function main() {
  const outputs = expectedOutputs();
  const unexpected = unexpectedGeneratedPages(outputs);
  if (unexpected.length) {
    console.error(`FAIL: unexpected generated SEO page(s):\n${unexpected.join("\n")}`);
    process.exitCode = 1;
    return;
  }
  const stale = [];
  for (const [outputPath, content] of outputs) {
    if (CHECK) {
      const current = fs.existsSync(outputPath) ? fs.readFileSync(outputPath, "utf8") : null;
      if (current !== content) stale.push(path.relative(ROOT, outputPath));
      continue;
    }
    fs.mkdirSync(path.dirname(outputPath), { recursive: true });
    fs.writeFileSync(outputPath, content, "utf8");
    console.log(`wrote ${path.relative(ROOT, outputPath)}`);
  }
  if (stale.length) {
    console.error(`FAIL: stale SEO pilot output(s):\n${stale.join("\n")}`);
    process.exitCode = 1;
  } else if (CHECK) {
    console.log(`OK: ${outputs.size} SEO pilot outputs are current`);
  }
}

main();
