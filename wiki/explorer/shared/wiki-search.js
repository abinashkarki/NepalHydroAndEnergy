// Fully static Search/Seek index. No model loading, no IndexedDB, no API.
(function () {
if (window.NepalExplorer && window.NepalExplorer._staticSearchLoaded) return;

const STOPWORDS = new Set("a an the and or but if else for of in on at to from by with as is are was were be been being have has had do does did not no nor so very can could should would may might must will shall this that these those it its i you he she they we us them his her him their our your my me one two three some any all most more less than then also too here there when where why how which what who whom whose into onto over under between within across about against amongst per via while during after before since until also although still yet only just even ever never really often always sometimes maybe perhaps because however therefore thus hence such each both either neither many few several other another same different new old high low big small large great good bad first second next last own out up down off above below near far inside outside through throughout off through s t d m re ve ll".split(/\s+/));
const TOKEN_RE = /[a-z0-9][a-z0-9\-_/]+/g;

function tokenize(text) {
  return (String(text).toLowerCase().match(TOKEN_RE) || []).filter((t) => t.length > 2 && !STOPWORDS.has(t));
}

function escapeHtml(s) {
  return String(s || "").replace(/[<>&"']/g, (c) => ({ "<": "&lt;", ">": "&gt;", "&": "&amp;", '"': "&quot;", "'": "&#39;" }[c]));
}

class StaticSearchIndex {
  constructor(index) {
    this.version = index.version;
    this.pages = index.pages || [];
    this.postings = index.postings || {};
    this.docFreq = index.doc_freq || {};
    this.docLen = index.doc_len || [];
    this.avgDocLen = index.avg_doc_len || 1;
    this.aliases = index.aliases || {};
    this.aliasPhrases = index.alias_phrases || [];
    this.neighbors = index.neighbors || {};
    this.totalDocs = this.pages.length;
  }

  titleSearch(query, opts = {}) {
    const limit = opts.limit ?? 80;
    const q = String(query || "").trim().toLowerCase();
    if (!q) return [];
    return this.pages
      .map((p, id) => ({ p, id }))
      .filter(({ p }) => String(p.t || "").toLowerCase().includes(q))
      .slice(0, limit)
      .map(({ p }) => this.resultForPage(p, 1, "title", p.e));
  }

  seek(query, opts = {}) {
    const limit = opts.limit ?? 30;
    const terms = this.expandTerms(query, tokenize(query));
    if (!terms.length) return [];
    const scores = new Map();
    const reasons = new Map();

    for (const term of terms) {
      const rows = this.postings[term] || [];
      const df = this.docFreq[term] || rows.length || 0;
      if (!df) continue;
      const idf = Math.log(1 + (this.totalDocs - df + 0.5) / (df + 0.5));
      for (const [docId, tf] of rows) {
        const denom = tf + 1.5 * (1 - 0.75 + 0.75 * ((this.docLen[docId] || this.avgDocLen) / this.avgDocLen));
        const score = idf * ((tf * 2.5) / denom);
        scores.set(docId, (scores.get(docId) || 0) + score);
        if (!reasons.has(docId)) reasons.set(docId, term);
      }
    }

    const seedIds = Array.from(scores.entries()).sort((a, b) => b[1] - a[1]).slice(0, 12);
    for (const [seedId, seedScore] of seedIds) {
      for (const [neighborId, qScore] of this.neighbors[String(seedId)] || []) {
        const boost = seedScore * (qScore / 1000) * 0.35;
        if (boost <= 0) continue;
        if (!scores.has(neighborId) || scores.get(neighborId) < boost) {
          reasons.set(neighborId, "near " + (this.pages[seedId]?.t || "match"));
        }
        scores.set(neighborId, (scores.get(neighborId) || 0) + boost);
      }
    }

    return Array.from(scores.entries())
      .sort((a, b) => b[1] - a[1])
      .slice(0, limit)
      .map(([docId, score]) => this.resultForPage(this.pages[docId], score, reasons.get(docId) || "match"));
  }

  expandTerms(query, terms) {
    const expanded = new Set(terms);
    for (const term of terms) {
      for (const alias of this.aliases[term] || []) expanded.add(alias);
    }
    const q = String(query || "").toLowerCase();
    for (const item of this.aliasPhrases) {
      if (!item.phrase || !q.includes(item.phrase)) continue;
      for (const term of item.expand || []) expanded.add(term);
    }
    return Array.from(expanded).filter((term) => this.postings[term]);
  }

  resultForPage(p, score, reason, snippet) {
    return {
      slug: p.s,
      title: p.t,
      category: p.c,
      type: p.y,
      subcategory: p.u,
      score,
      reason,
      snippetHtml: escapeHtml(snippet || p.e || ""),
    };
  }
}

class StaticFactIndex {
  constructor(index, searchIndex) {
    this.version = index.version;
    this.facts = index.facts || [];
    this.searchIndex = searchIndex;
    this.pageBySlug = new Map((searchIndex?.pages || []).map((p) => [p.s, p]));
    this.factById = new Map(this.facts.map((fact) => [fact.id, fact]));
  }

  seek(query, opts = {}) {
    const intent = this.classify(query);
    if (intent.constraints.noFacts) return [];
    const facts = this.rankFacts(intent).slice(0, opts.limit ?? 8);
    if (!facts.length) return [];
    return facts.map((fact, i) => this.resultForFact(fact, i)).filter(Boolean);
  }

  classify(query) {
    const q = String(query || "").toLowerCase();
    const terms = tokenize(q);
    const has = (...words) => words.some((word) => q.includes(word));
    const domain = has("solar", "pv") ? "solar" : "hydro";
    let status = "any";
    if (has("operating", "operation", "existing", "generation", "built", "commissioned", "working", "active", "running", "producing")) status = "operating";
    if (has("construction", "under construction", "buildout", "building")) status = "under-construction";
    if (has("survey", "planned", "proposed", "pipeline", "licence", "license")) status = "survey";
    const storage = has("storage", "reservoir", "dry season", "firm", "peaking");
    const superlative = has("biggest", "largest", "highest", "top ", "most mw", "second", "third");

    const hasDomainTerm = terms.some((t) => ["hydro", "hydropower", "solar", "pv", "ror", "run-of-river", "storage", "projects"].includes(t));
    const factish = superlative || (has("projects") && (has("karnali") || storage || has("hydro"))) || (hasDomainTerm && superlative);
    return {
      relevant: factish,
      constraints: {
        noFacts: !factish,
        domains: storage ? [domain, "storage"] : [domain],
        status,
        metric: "capacity_mw",
        sort: "desc",
        limit: 5,
      },
    };
  }

  rankFacts(intent) {
    const c = intent.constraints || intent;
    const domains = new Set(c.domains || []);
    const status = c.status || "any";
    return this.facts
      .filter((fact) => {
        const facets = new Set(fact.facets || [fact.domain]);
        if (![...domains].some((domain) => facets.has(domain) || fact.domain === domain)) return false;
        if (status !== "any" && fact.status !== status) return false;
        return Number.isFinite(Number(fact.capacity_mw));
      })
      .sort((a, b) => Number(b.capacity_mw || 0) - Number(a.capacity_mw || 0));
  }

  resultForFact(fact, i) {
    const slug = fact.wiki_slug || fact.slug || "";
    const page = slug ? this.pageBySlug.get(slug) : null;
    return {
      kind: slug ? "wiki" : "fact",
      factId: fact.id,
      slug,
      title: fact.name,
      category: page?.c || "facts",
      type: page?.y || "fact",
      subcategory: page?.u || "",
      score: 1 - i * 0.04,
      chip: fact.status || "fact",
      snippetHtml: escapeHtml(`${formatMw(fact.capacity_mw)} · ${fact.status_raw || fact.status}${fact.river ? " · " + fact.river : ""}${fact.district ? " · " + fact.district : ""}`),
    };
  }

  getFact(id) {
    return this.factById.get(id) || null;
  }
}

function formatMw(value) {
  const n = Number(value);
  if (!Number.isFinite(n)) return "";
  return `${n.toLocaleString(undefined, { maximumFractionDigits: n >= 100 ? 0 : 2 })} MW`;
}

window.NepalExplorer = window.NepalExplorer || {};
Object.assign(window.NepalExplorer, { StaticSearchIndex, StaticFactIndex, staticSearchTokenize: tokenize });
window.NepalExplorer._staticSearchLoaded = true;
})();
