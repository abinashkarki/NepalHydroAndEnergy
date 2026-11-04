#!/usr/bin/env node
"use strict";

// Static reader site: one lightweight, crawlable article per wiki page.
//
// Output goes to wiki/site/ and is overlaid onto /wiki/ at deploy time, so
// wiki/site/<slug>/index.html is served as https://transparentgov.ai/wiki/<slug>/.
// The interactive explorer (wiki/explorer/) stays the map and research tool;
// every article links into it. Source of truth remains wiki/pages/.

const fs = require("fs");
const path = require("path");
const { marked } = require("../wiki/explorer/shared/marked.min.js");

const ROOT = path.resolve(__dirname, "..");
const WIKI = path.join(ROOT, "wiki");
const OUT = path.join(WIKI, "site");
const PAGE_INDEX_PATH = path.join(WIKI, "explorer", "shared", "wiki-page-index.json");
const PAGE_META_PATH = path.join(WIKI, "explorer", "shared", "wiki-page-meta.json");
const BACKLINKS_PATH = path.join(WIKI, "explorer", "shared", "wiki-backlinks.json");
const SITE_CONFIG_PATH = path.join(WIKI, "site-config.json");
const CHECK = process.argv.includes("--check");
const GENERATOR = "scripts/build_wiki_site.js";
// Applies a stored theme choice before first paint (see wiki/assets/site/theme.js).
const THEME_BOOT = '<script>try{var t=localStorage.getItem("np-theme");if(t==="light"||t==="dark")document.documentElement.setAttribute("data-theme",t)}catch(e){}</script>';
const THEME_TOGGLE = `<button class="theme-toggle" type="button" data-theme-toggle aria-label="Switch theme" title="Switch theme"><svg class="icon-moon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M20 14.5A8 8 0 0 1 9.5 4a8 8 0 1 0 10.5 10.5z"/></svg><svg class="icon-sun" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" aria-hidden="true"><circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/></svg></button>`;

// Reader-facing names for the internal ontology categories, in display order.
const SECTIONS = [
  { category: "syntheses", label: "Analysis", blurb: "Argued, sourced pages that explain how the system works and where it fails." },
  { category: "claims", label: "Claims", blurb: "Single governed statements with a confidence rating, evidence and caveats." },
  { category: "concepts", label: "Explainers", blurb: "Plain-language definitions of the ideas the analysis depends on." },
  { category: "interventions", label: "Policy options", blurb: "Decision dossiers that compare what could be done and what evidence is missing." },
  { category: "entities", label: "Projects & places", blurb: "Records for hydropower projects, transmission lines, rivers, basins and institutions." },
  { category: "data", label: "Data", blurb: "Datasets, map layers and indicators, with their limits." },
  { category: "sources", label: "Sources", blurb: "Notes on the documents behind the wiki: what each provides and how far it can be trusted." },
];
const SECTION_BY_CATEGORY = new Map(SECTIONS.map((section) => [section.category, section]));
const MATURITY_LABEL = {
  "verified-core": "Verified core",
  "working-page": "Working page",
  "registry-record": "Registry record",
};
const CALLOUT_LABEL = {
  note: "Note",
  warning: "Caution",
  important: "Important",
  contradiction: "Conflicting sources",
  gap: "Evidence gap",
  cite: "Source note",
  finding: "Finding",
};
// Reserved names under /wiki/ that a page slug must never shadow.
const RESERVED = new Set(["explorer", "pages", "assets", "site", "index.html", "404.html", "sitemap.xml"]);

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

function splitFrontmatter(text) {
  if (!text.startsWith("---\n")) return { frontmatter: "", body: text };
  const end = text.indexOf("\n---", 4);
  if (end === -1) return { frontmatter: "", body: text };
  return { frontmatter: text.slice(4, end).trim(), body: text.slice(end + 4).replace(/^\s+/, "") };
}

function frontmatterScalar(frontmatter, key) {
  const escapedKey = key.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
  const match = frontmatter.match(new RegExp(`^${escapedKey}:\\s*(.*?)\\s*$`, "m"));
  if (!match) return "";
  const value = match[1].trim();
  if (/^".*"$/.test(value)) {
    try { return JSON.parse(value); } catch (_error) { return value.slice(1, -1); }
  }
  return value.replace(/^'(.*)'$/, "$1");
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

function pageHref(slug) {
  return `/wiki/${encodeURIComponent(slug)}/`;
}

function explorerHref(slug) {
  return `/wiki/explorer/?page=${encodeURIComponent(slug)}`;
}

function isOverdue(reviewDue, today) {
  return Boolean(reviewDue) && /^\d{4}-\d{2}-\d{2}$/.test(reviewDue) && reviewDue < today;
}

function rewriteWikilinks(markdown, known, titles) {
  return markdown.replace(/\[\[([^\]|]+)(?:\|([^\]]+))?\]\]/g, (_whole, rawTarget, rawLabel) => {
    const slug = rawTarget.trim();
    const label = (rawLabel || titles[slug] || slug).trim();
    if (!known.has(slug)) return escapeHtml(label);
    return `<a href="${pageHref(slug)}">${escapeHtml(label)}</a>`;
  });
}

function renderCallouts(html) {
  return html.replace(
    /<blockquote>\s*<p>\[!([a-z]+)\]\s*([\s\S]*?)<\/blockquote>/gi,
    (_whole, typeRaw, body) => {
      const type = String(typeRaw).toLowerCase();
      const label = CALLOUT_LABEL[type] || "Note";
      return `<aside class="callout callout-${escapeHtml(type)}"><div class="callout-label">${label}</div><div class="callout-body"><p>${body.trim()}</div></aside>`;
    },
  );
}

function renderBody(body, known, titles) {
  // Drop the leading H1: the page header renders the title.
  const withoutTitle = body.replace(/^#\s+[^\n]*\n+/, "");
  const linked = rewriteWikilinks(withoutTitle, known, titles);
  const html = sanitizeRenderedHtml(marked.parse(linked, { gfm: true }))
    .replace(/(src|href)="\.\.\/assets\//g, '$1="/wiki/assets/')
    .replace(/<table>/g, '<div class="table-wrap"><table>')
    .replace(/<\/table>/g, "</table></div>");
  return renderCallouts(html);
}

function renderFacts({ category, frontmatter, meta, today }) {
  const rows = [];
  if (category === "claims") {
    const claimId = frontmatterScalar(frontmatter, "claim_id");
    const confidence = frontmatterScalar(frontmatter, "confidence");
    const status = frontmatterScalar(frontmatter, "status");
    if (claimId) rows.push(["Claim", claimId]);
    if (confidence) rows.push(["Confidence", confidence]);
    if (status) rows.push(["Status", status.replace(/-/g, " ")]);
  }
  const maturity = MATURITY_LABEL[meta.maturity] || (meta.is_stub === true ? "Registry record" : "");
  if (maturity) rows.push(["Page status", maturity]);
  if (meta.updated) rows.push(["Updated", meta.updated]);
  const reviewed = frontmatterScalar(frontmatter, "reviewed");
  const reviewDue = frontmatterScalar(frontmatter, "review_due");
  if (reviewed) rows.push(["Last reviewed", reviewed]);
  if (reviewDue) rows.push(["Review due", isOverdue(reviewDue, today) ? `${reviewDue} (overdue)` : reviewDue]);
  if (!rows.length) return "";
  const items = rows.map(([label, value]) => `<div><dt>${escapeHtml(label)}</dt><dd>${escapeHtml(value)}</dd></div>`).join("");
  return `<dl class="facts">${items}</dl>`;
}

function renderProvenance(category, frontmatter) {
  if (category !== "sources") return "";
  const rows = [
    ["Author", frontmatterScalar(frontmatter, "source_author")],
    ["Source date", frontmatterScalar(frontmatter, "source_date")],
    ["Source type", frontmatterScalar(frontmatter, "source_type")],
    ["Verification", frontmatterScalar(frontmatter, "verification_status").replace(/-/g, " ")],
  ].filter(([, value]) => value);
  const url = safeExternalUrl(frontmatterScalar(frontmatter, "source_url"));
  if (!rows.length && !url) return "";
  const items = rows.map(([label, value]) => `<div><dt>${escapeHtml(label)}</dt><dd>${escapeHtml(value)}</dd></div>`).join("");
  const link = url ? `<a class="source-link" href="${escapeHtml(url)}" rel="noopener noreferrer">Open the original document ↗</a>` : "";
  return `<aside class="provenance" aria-label="Source record"><h2>Source record</h2><dl>${items}</dl>${link}</aside>`;
}

function renderBacklinks(slug, category, backlinks) {
  const references = (backlinks.backlinks || {})[slug] || [];
  if (!references.length) return "";
  const heading = category === "sources" ? "Pages that use this source" : "Pages that link here";
  const items = references.map((item) => {
    const section = SECTION_BY_CATEGORY.get(item.category);
    return `<li><a href="${pageHref(item.slug)}">${escapeHtml(item.title || item.slug)}</a><span>${escapeHtml(section ? section.label : item.category || "")}</span></li>`;
  }).join("");
  return `<aside class="backlinks" aria-label="${heading}"><h2>${heading} <span>${references.length}</span></h2><ul>${items}</ul></aside>`;
}

function siteHeader(config) {
  const nav = SECTIONS.map((section) => `<a href="/wiki/#${section.category}">${section.label}</a>`).join("");
  return `<header class="site-header">
  <div class="site-bar">
    <a class="site-name" href="/wiki/">${escapeHtml(config.site_name)}</a>
    <form class="site-search" action="/wiki/explorer/" method="get" role="search">
      <label class="visually-hidden" for="site-q">Search the wiki</label>
      <input id="site-q" name="q" type="search" placeholder="Search projects, claims, sources…" />
    </form>
    <div class="site-actions">
      <a class="site-map" href="/wiki/explorer/">Map</a>
      ${THEME_TOGGLE}
    </div>
  </div>
  <nav class="site-nav" aria-label="Sections">${nav}</nav>
</header>`;
}

function siteFooter(config) {
  return `<footer class="site-footer">
  <p>${escapeHtml(config.site_name)} is a citizen-led evidence project by <a href="https://transparentgov.ai/">TransparentGov</a>. Every page links to its sources; confidence ratings and caveats are part of the answer.</p>
  <p><a href="${escapeHtml(config.film.page)}">Watch the film: ${escapeHtml(config.film.title)}</a> · <a href="${escapeHtml(config.repository)}">Source on GitHub</a> · <a href="/wiki/start-here/">Start here</a></p>
</footer>`;
}

function document({ title, description, canonical, jsonLd, body, config, robots = "index,follow,max-image-preview:large", ogType = "article" }) {
  const ld = jsonLd ? `\n  <script type="application/ld+json">${JSON.stringify(jsonLd).replace(/</g, "\\u003c")}</script>` : "";
  return `<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <meta name="generator" content="${GENERATOR}" />
  <title>${escapeHtml(title)}</title>
  <meta name="description" content="${escapeHtml(description)}" />
  <meta name="robots" content="${robots}" />${canonical ? `\n  <link rel="canonical" href="${escapeHtml(canonical)}" />` : ""}
  <meta property="og:type" content="${ogType}" />
  <meta property="og:site_name" content="${escapeHtml(config.site_name)}" />
  <meta property="og:title" content="${escapeHtml(title)}" />
  <meta property="og:description" content="${escapeHtml(description)}" />${canonical ? `\n  <meta property="og:url" content="${escapeHtml(canonical)}" />` : ""}
  <meta name="twitter:card" content="summary" />
  ${THEME_BOOT}
  <link rel="stylesheet" href="/wiki/assets/site/theme.css" />
  <link rel="stylesheet" href="/wiki/assets/site/wiki.css" />
  <script src="/wiki/assets/site/theme.js" defer></script>
  <link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'%3E%3Crect width='64' height='64' rx='12' fill='%230b6b57'/%3E%3C/svg%3E" />${ld}
</head>
<body>
${siteHeader(config)}
${body}
${siteFooter(config)}
</body>
</html>
`;
}

function articleJsonLd({ canonical, category, description, frontmatter, meta, config }) {
  const sourceUrl = safeExternalUrl(frontmatterScalar(frontmatter, "source_url"));
  const sourceAuthor = frontmatterScalar(frontmatter, "source_author");
  const created = frontmatterScalar(frontmatter, "created");
  const article = {
    "@type": category === "sources" ? "Report" : "Article",
    "@id": `${canonical}#article`,
    headline: meta.title,
    name: meta.title,
    description,
    url: canonical,
    datePublished: created || undefined,
    dateModified: meta.updated || undefined,
    publisher: { "@type": "Organization", name: "TransparentGov", url: "https://transparentgov.ai/" },
  };
  if (category === "sources" && sourceUrl) article.isBasedOn = sourceUrl;
  if (category === "sources" && sourceAuthor) article.author = { "@type": "Organization", name: sourceAuthor };
  Object.keys(article).forEach((key) => article[key] === undefined && delete article[key]);
  const section = SECTION_BY_CATEGORY.get(category);
  return {
    "@context": "https://schema.org",
    "@graph": [
      article,
      {
        "@type": "BreadcrumbList",
        itemListElement: [
          { "@type": "ListItem", position: 1, name: config.site_name, item: `${config.canonical_base}/` },
          { "@type": "ListItem", position: 2, name: section ? section.label : category, item: `${config.canonical_base}/#${category}` },
          { "@type": "ListItem", position: 3, name: meta.title, item: canonical },
        ],
      },
    ],
  };
}

function filmCallout(slug, config) {
  if (!(config.film.related_pages || []).includes(slug)) return "";
  return `<aside class="film-callout"><div class="callout-label">Watch</div><p>This page is part of the evidence behind the TransparentGov film <a href="${escapeHtml(config.film.page)}"><em>${escapeHtml(config.film.title)}</em></a>.</p></aside>`;
}

function renderArticle({ slug, category, meta, markdown, known, titles, backlinks, config, today }) {
  const { frontmatter, body } = splitFrontmatter(markdown);
  const description = cleanDescription(meta.excerpt || meta.body_text || meta.title);
  const canonical = `${config.canonical_base}/${encodeURIComponent(slug)}/`;
  const section = SECTION_BY_CATEGORY.get(category);
  const caveat = frontmatterScalar(frontmatter, "caveat");
  const overdue = isOverdue(frontmatterScalar(frontmatter, "review_due"), today);
  const superseded = body.match(/<!--\s*superseded-by:\s*(\S+)\s*-->/);
  const notices = [
    superseded && known.has(superseded[1])
      ? `<aside class="callout callout-note"><div class="callout-label">Updated page available</div><div class="callout-body"><p>See <a href="${pageHref(superseded[1])}">${escapeHtml(titles[superseded[1]] || superseded[1])}</a>.</p></div></aside>`
      : "",
    caveat ? `<aside class="callout callout-warning"><div class="callout-label">Caveat</div><div class="callout-body"><p>${escapeHtml(caveat)}</p></div></aside>` : "",
    overdue ? `<aside class="callout callout-gap"><div class="callout-label">Review overdue</div><div class="callout-body"><p>This page is past its scheduled evidence review. Figures may have changed since it was last checked.</p></div></aside>` : "",
  ].join("");
  const html = `<main class="page">
  <nav class="crumbs" aria-label="Breadcrumb"><a href="/wiki/">Wiki</a> › <a href="/wiki/#${category}">${escapeHtml(section ? section.label : category)}</a></nav>
  <article>
    <header class="page-head">
      <h1>${escapeHtml(meta.title)}</h1>
      ${frontmatterScalar(frontmatter, "excerpt") ? `<p class="dek">${escapeHtml(frontmatterScalar(frontmatter, "excerpt"))}</p>` : ""}
      ${renderFacts({ category, frontmatter, meta, today })}
      <p class="page-actions"><a href="${explorerHref(slug)}">Open in the interactive explorer and map</a></p>
    </header>
    ${notices}${renderProvenance(category, frontmatter)}
    <div class="prose">${renderBody(body, known, titles)}</div>
    ${filmCallout(slug, config)}
  </article>
  ${renderBacklinks(slug, category, backlinks)}
</main>`;
  return {
    canonical,
    description,
    html: document({
      title: `${meta.title} · ${config.site_name}`,
      description,
      canonical,
      jsonLd: articleJsonLd({ canonical, category, description, frontmatter, meta, config }),
      body: html,
      config,
    }),
  };
}

function renderHome({ pagesByCategory, metaBySlug, config }) {
  const titleOf = (slug) => (metaBySlug.get(slug) || {}).title || slug;
  const questions = config.home.questions.map((question) => {
    const links = question.pages.map((slug) => `<li><a href="${pageHref(slug)}">${escapeHtml(titleOf(slug))}</a></li>`).join("");
    return `<section class="question"><h2>${escapeHtml(question.title)}</h2><p>${escapeHtml(question.answer)}</p><ul>${links}</ul></section>`;
  }).join("");
  const sections = SECTIONS.map((section) => {
    const pages = (pagesByCategory.get(section.category) || []).slice().sort((a, b) => a.title.localeCompare(b.title));
    const items = pages.map((page) => `<li><a href="${pageHref(page.slug)}">${escapeHtml(page.title)}</a></li>`).join("");
    return `<section class="directory-section" id="${section.category}">
    <h2>${section.label} <span>${pages.length}</span></h2>
    <p>${section.blurb}</p>
    <ul class="directory">${items}</ul>
  </section>`;
  }).join("\n");
  const body = `<main class="page home">
  <header class="home-head">
    <h1>${escapeHtml(config.home.title)}</h1>
    <p class="dek">${escapeHtml(config.home.lead)}</p>
    <p class="page-actions"><a href="/wiki/start-here/">Start here</a> · <a href="/wiki/master-thesis/">Read the argument</a> · <a href="/wiki/state-of-the-system/">State of the system</a> · <a href="/wiki/explorer/">Explore the map</a></p>
  </header>
  <div class="questions">${questions}</div>
  <aside class="film-callout home-film"><div class="callout-label">Film</div><p><a href="${escapeHtml(config.film.page)}"><em>${escapeHtml(config.film.title)}</em></a> (${escapeHtml(config.film.runtime)}) tells the story; this wiki holds the evidence behind each claim in it.</p></aside>
  ${sections}
</main>`;
  const canonical = `${config.canonical_base}/`;
  return document({
    title: `${config.site_name}: ${config.home.title}`,
    description: cleanDescription(config.home.lead),
    canonical,
    ogType: "website",
    jsonLd: {
      "@context": "https://schema.org",
      "@type": "WebSite",
      "@id": `${canonical}#website`,
      name: config.site_name,
      url: canonical,
      description: config.home.lead,
      publisher: { "@type": "Organization", name: "TransparentGov", url: "https://transparentgov.ai/" },
      potentialAction: { "@type": "SearchAction", target: "https://transparentgov.ai/wiki/explorer/?q={query}", "query-input": "required name=query" },
    },
    body,
    config,
  });
}

function renderNotFound(config) {
  const body = `<main class="page">
  <h1>Page not found</h1>
  <p class="dek">There is no wiki page at this address. It may have been renamed or merged.</p>
  <p class="page-actions"><a href="/wiki/">Browse all pages</a> · <a href="/wiki/explorer/">Search in the explorer</a></p>
</main>`;
  return document({ title: `Page not found · ${config.site_name}`, description: "No wiki page exists at this address.", canonical: "", body, config, robots: "noindex" });
}

function expectedOutputs() {
  const config = readJSON(SITE_CONFIG_PATH);
  config.canonical_base = config.canonical_base.replace(/\/$/, "");
  const pageIndex = readJSON(PAGE_INDEX_PATH);
  const pageMeta = readJSON(PAGE_META_PATH);
  const backlinks = readJSON(BACKLINKS_PATH);
  const today = config.as_of;
  const metaBySlug = new Map((pageMeta.pages || []).map((page) => [page.slug, page]));
  const known = new Set(pageIndex.allSlugs || []);
  const titles = pageIndex.slugToTitle || {};
  const outputs = new Map();
  const pagesByCategory = new Map();
  const sitemap = [{ loc: `${config.canonical_base}/`, lastmod: config.as_of }];

  for (const question of config.home.questions) {
    for (const slug of question.pages) if (!known.has(slug)) throw new Error(`home question links unknown page: ${slug}`);
  }
  for (const slug of [...known].sort()) {
    if (RESERVED.has(slug)) throw new Error(`page slug collides with a reserved /wiki/ path: ${slug}`);
    const category = pageIndex.slugToCategory[slug];
    const sourcePath = path.join(WIKI, "pages", category, `${slug}.md`);
    const meta = metaBySlug.get(slug);
    if (!meta || !fs.existsSync(sourcePath)) throw new Error(`missing input for page: ${slug}`);
    const rendered = renderArticle({
      slug, category, meta, markdown: fs.readFileSync(sourcePath, "utf8"), known, titles, backlinks, config, today,
    });
    outputs.set(path.join(OUT, slug, "index.html"), rendered.html);
    if (!pagesByCategory.has(category)) pagesByCategory.set(category, []);
    pagesByCategory.get(category).push({ slug, title: meta.title });
    sitemap.push({ loc: rendered.canonical, lastmod: meta.updated && meta.updated !== "None" ? meta.updated : "" });
  }
  outputs.set(path.join(OUT, "index.html"), renderHome({ pagesByCategory, metaBySlug, config }));
  outputs.set(path.join(OUT, "404.html"), renderNotFound(config));
  const urls = sitemap.map((entry) => `  <url><loc>${escapeHtml(entry.loc)}</loc>${entry.lastmod ? `<lastmod>${escapeHtml(entry.lastmod)}</lastmod>` : ""}</url>`).join("\n");
  outputs.set(path.join(OUT, "sitemap.xml"), `<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n${urls}\n</urlset>\n`);
  return outputs;
}

function existingOutputs(dir) {
  if (!fs.existsSync(dir)) return [];
  const found = [];
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    const full = path.join(dir, entry.name);
    if (entry.isDirectory()) found.push(...existingOutputs(full));
    else found.push(full);
  }
  return found;
}

function main() {
  const outputs = expectedOutputs();
  const expected = new Set([...outputs.keys()].map((entry) => path.resolve(entry)));
  const orphans = existingOutputs(OUT).filter((file) => !expected.has(path.resolve(file)));
  const stale = [];
  for (const [outputPath, content] of outputs) {
    const current = fs.existsSync(outputPath) ? fs.readFileSync(outputPath, "utf8") : null;
    if (current === content) continue;
    if (CHECK) { stale.push(path.relative(ROOT, outputPath)); continue; }
    fs.mkdirSync(path.dirname(outputPath), { recursive: true });
    fs.writeFileSync(outputPath, content, "utf8");
  }
  if (CHECK) {
    if (stale.length || orphans.length) {
      console.error(`FAIL: static wiki site is stale (${stale.length} changed, ${orphans.length} orphaned); run node ${GENERATOR}`);
      [...stale, ...orphans.map((file) => path.relative(ROOT, file))].slice(0, 20).forEach((file) => console.error(`  ${file}`));
      process.exitCode = 1;
    } else {
      console.log(`OK: static wiki site is current (${outputs.size} files)`);
    }
    return;
  }
  for (const orphan of orphans) fs.rmSync(orphan);
  for (const dir of fs.readdirSync(OUT, { withFileTypes: true })) {
    const full = path.join(OUT, dir.name);
    if (dir.isDirectory() && !fs.readdirSync(full).length) fs.rmdirSync(full);
  }
  console.log(`wrote ${outputs.size} static wiki files to ${path.relative(ROOT, OUT)}/ (removed ${orphans.length} orphaned)`);
}

main();
