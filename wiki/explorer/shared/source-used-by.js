// Computed backlink / source Used By renderer.
(function () {
if (window.NepalExplorer && window.NepalExplorer._sourceUsedByLoaded) return;

function escapeHtml(s) {
  return String(s || "").replace(/[<>&"']/g, (c) => ({ "<": "&lt;", ">": "&gt;", "&": "&amp;", '"': "&quot;", "'": "&#39;" }[c]));
}

function cleanContext(value) {
  const text = String(value || "")
    .replace(/<!--[\s\S]*?-->/g, " ")
    .replace(/\[\[([^\]|]+)(?:\|([^\]]+))?\]\]/g, (_, slug, label) => label || slug)
    .replace(/\[([^\]]+)\]\([^)]+\)/g, "$1")
    .replace(/(?:^|\s)#{1,6}\s+/g, " ")
    .replace(/\bgenerated(?::[a-z-]+)*(?::start|:end)?\b/gi, " ")
    .replace(/\s+/g, " ")
    .trim()
    .replace(/^[…\s:;|\-]+|[\s:;|\-]+$/g, "");
  if (!text || /^(?:see also|related|sources?|references?)\.?$/i.test(text)) return "";
  return text;
}

function backlinkRow(r, spatialSlugs) {
  const sp = spatialSlugs && spatialSlugs.has(r.slug) ? " spatial" : "";
  const context = cleanContext(r.context);
  const linkAttrs = window.NepalExplorer && window.NepalExplorer.wikiPageLinkAttrs
    ? window.NepalExplorer.wikiPageLinkAttrs(r.slug)
    : `href="/wiki/explorer/?page=${encodeURIComponent(r.slug)}"`;
  return `<li class="backlink-item">
    <a class="wikilink${sp}" ${linkAttrs}>${escapeHtml(r.title)}</a>
    ${context ? `<div class="backlink-context">${escapeHtml(context)}</div>` : ""}
  </li>`;
}

function renderReferenceSection(refs, options = {}) {
  if (!refs || !refs.length) return "";
  const byCat = {};
  for (const r of refs) {
    (byCat[r.category] = byCat[r.category] || []).push(r);
  }
  const catLabel = {
    entities: "Entities",
    concepts: "Concepts",
    syntheses: "Syntheses",
    claims: "Claims",
    sources: "Sources",
    data: "Data",
    interventions: "Decision Dossiers",
  };
  const spatialSlugs = options.spatialSlugs;
  const parts = [];
  for (const cat of ["entities", "syntheses", "concepts", "claims", "interventions", "sources", "data"]) {
    const items = byCat[cat];
    if (!items || !items.length) continue;
    const initialLimit = Number.isFinite(options.initialLimit) ? options.initialLimit : 6;
    const firstRows = items.slice(0, initialLimit).map((r) => backlinkRow(r, spatialSlugs)).join("");
    const remaining = items.slice(initialLimit);
    const more = remaining.length
      ? `<details class="backlinks-more"><summary>Show ${remaining.length} more</summary><ul class="backlinks-list">${remaining.map((r) => backlinkRow(r, spatialSlugs)).join("")}</ul></details>`
      : "";
    parts.push(
      `<div class="backlinks-group"><div class="backlinks-cat">${catLabel[cat] || escapeHtml(cat)} <span class="backlinks-count">${items.length}</span></div><ul class="backlinks-list">${firstRows}</ul>${more}</div>`
    );
  }
  const heading = options.heading || "Referenced by";
  return `<section class="backlinks-section"><h2 class="backlinks-heading">${escapeHtml(heading)} <span class="backlinks-total">${refs.length}</span></h2>${parts.join("")}</section>`;
}

window.NepalExplorer = window.NepalExplorer || {};
Object.assign(window.NepalExplorer, { renderReferenceSection });
window.NepalExplorer._sourceUsedByLoaded = true;
})();
