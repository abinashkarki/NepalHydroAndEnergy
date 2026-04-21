// Tiny BM25 search over wiki page metadata.
// Uses precomputed token_freq + doc_freq from wiki-page-meta.json.
// No external deps; instant after meta load.
(function () {
if (window.NepalExplorer && window.NepalExplorer._bm25Loaded) return;

const STOPWORDS = new Set("a an the and or but if for of in on at to from by with as is are was were be been have has do does did not no this that it its will would can could should may might must i you he she they we us them his her our your my me one two three some any all most more less than then also too here there when where why how which what who".split(/\s+/));
const TOKEN_RE = /[a-z0-9][a-z0-9\-_/]+/g;

function tokenize(text) {
  return (text.toLowerCase().match(TOKEN_RE) || []).filter((t) => t.length > 2 && !STOPWORDS.has(t));
}

class BM25Index {
  constructor(meta, opts = {}) {
    this.k1 = opts.k1 ?? 1.5;
    this.b = opts.b ?? 0.75;
    this.pages = meta.pages;
    this.docFreq = meta.doc_freq;
    this.totalDocs = meta.pages.length;
    // Precompute doc length and avg doc length using sum of token frequencies.
    let totalLen = 0;
    this.docLen = {};
    for (const p of this.pages) {
      const len = Object.values(p.token_freq).reduce((a, b) => a + b, 0);
      this.docLen[p.slug] = len;
      totalLen += len;
    }
    this.avgDocLen = totalLen / Math.max(this.totalDocs, 1);
    this.bySlug = Object.fromEntries(this.pages.map((p) => [p.slug, p]));
  }

  idf(term) {
    const df = this.docFreq[term] || 0;
    if (df === 0) return 0;
    return Math.log(1 + (this.totalDocs - df + 0.5) / (df + 0.5));
  }

  search(query, opts = {}) {
    const limit = opts.limit ?? 30;
    const terms = Array.from(new Set(tokenize(query)));
    if (!terms.length) return [];

    const results = [];
    for (const p of this.pages) {
      let score = 0;
      const matchedTerms = [];
      for (const t of terms) {
        const tf = p.token_freq[t] || 0;
        if (!tf) continue;
        const idf = this.idf(t);
        const denom = tf + this.k1 * (1 - this.b + this.b * (this.docLen[p.slug] / this.avgDocLen));
        score += idf * ((tf * (this.k1 + 1)) / denom);
        matchedTerms.push(t);
      }
      // Title boost: each query term that occurs in title adds a bonus.
      const titleLower = (p.title || "").toLowerCase();
      for (const t of terms) {
        if (titleLower.includes(t)) score += 1.6;
      }
      if (score > 0) {
        results.push({ slug: p.slug, title: p.title, category: p.category, type: p.type, subcategory: p.subcategory, score, matchedTerms, snippet: makeSnippet(p, terms) });
      }
    }
    results.sort((a, b) => b.score - a.score);
    return results.slice(0, limit);
  }
}

function makeSnippet(page, terms, maxLen = 220) {
  const body = page.body_text || page.excerpt || "";
  if (!body) return "";
  const lower = body.toLowerCase();
  let bestPos = -1;
  for (const t of terms) {
    const i = lower.indexOf(t);
    if (i >= 0 && (bestPos < 0 || i < bestPos)) bestPos = i;
  }
  if (bestPos < 0) return body.slice(0, maxLen) + (body.length > maxLen ? "…" : "");
  const start = Math.max(0, bestPos - 60);
  let snip = body.slice(start, start + maxLen);
  if (start > 0) snip = "…" + snip;
  if (start + maxLen < body.length) snip = snip + "…";
  // Highlight all term occurrences.
  for (const t of terms) {
    const re = new RegExp("(" + t.replace(/[.*+?^${}()|[\]\\]/g, "\\$&") + ")", "gi");
    snip = snip.replace(re, "<mark>$1</mark>");
  }
  return snip;
}

window.NepalExplorer = window.NepalExplorer || {};
Object.assign(window.NepalExplorer, { BM25Index, bm25Tokenize: tokenize });
window.NepalExplorer._bm25Loaded = true;
})();
