// Fully static Search/Seek index. No model loading, no IndexedDB, no API.
(function () {
if (window.NepalExplorer && window.NepalExplorer._staticSearchLoaded) return;

const STOPWORDS = new Set("a an the and or but if else for of in on at to from by with as is are was were be been being have has had do does did not no nor so very can could should would may might must will shall this that these those it its i you he she they we us them his her him their our your my me one two three some any all most more less than then also too here there when where why how which what who whom whose into onto over under between within across about against amongst per via while during after before since until also although still yet only just even ever never really often always sometimes maybe perhaps because however therefore thus hence such each both either neither many few several other another same different new old high low big small large great good bad first second next last own out up down off above below near far inside outside through throughout off through s t d m re ve ll".split(/\s+/));
const TOKEN_RE = /[a-z0-9][a-z0-9\-_/]+/g;
const TOKEN_SPLIT_RE = /[-_/]+/g;
const SOURCE_INTENT_TERMS = new Set(["annual", "data", "feasibility", "fy", "guideline", "guidelines", "proposal", "record", "report", "source", "status", "study", "summary", "table"]);
const SOURCE_SEEK_TERMS = new Set(["citation", "citations", "document", "documents", "evidence", "reference", "references", "report", "reports", "source", "sources"]);
const PROJECT_TERMS = new Set(["plant", "plants", "project", "projects", "scheme", "schemes"]);
const ATTRIBUTE_TERMS = new Set(["capacity", "developer", "district", "promoter", "river", "basin", "status", "stage", "mw"]);
const GENERIC_NAME_TERMS = new Set(["hep", "hpp", "hydroelectric", "hydropower", "power", "plant", "project", "scheme", "storage", "multipurpose"]);
const INTENT_CONTROL_TERMS = new Set([
  ...SOURCE_SEEK_TERMS,
  ...PROJECT_TERMS,
  ...ATTRIBUTE_TERMS,
  "above", "below", "between", "biggest", "blocked", "built", "commissioned", "conceptual", "construction",
  "delayed", "existing", "greater", "highest", "largest", "least", "less", "licensed", "licence",
  "license", "lowest", "maximum", "minimum", "operating", "operation", "planned", "pre", "producing",
  "proposed", "running", "smallest", "stalled", "survey", "under", "working",
  "hydro", "hydropower", "solar", "transmission", "grid", "corridor", "interconnection", "line", "pv", "ror",
]);

const STATUS_DEFINITIONS = [
  { status: "pre-construction", requested: "pre-construction", re: /\b(?:pre[\s-]?construction|pre[\s-]?build|preparatory)\b/g },
  { status: "under-construction", requested: "under-construction", re: /\b(?:under[\s-]?construction|in[\s-]?construction|being built|buildout|building)\b/g },
  { status: "stalled", requested: "stalled", re: /\b(?:stalled|stranded|suspended|on hold|not moving)\b/g },
  { status: "stalled", requested: "delayed", re: /\b(?:delayed|overdue|behind schedule)\b/g },
  { status: "stalled", requested: "blocked", re: /\b(?:blocked|stuck|impeded)\b/g },
  { status: "operating", requested: "operating", re: /\b(?:operating|operational|in operation|existing|built|commissioned|working|running|producing)\b/g },
  { status: "conceptual", requested: "conceptual", re: /\b(?:conceptual|concept-stage|idea-stage)\b/g },
  { status: "planned", requested: "planned", re: /\b(?:planned|proposed|pipeline|prospective|future)\b/g },
  { status: "survey", requested: "survey", re: /\b(?:survey|surveyed|survey-stage|licensed|licence|license)\b/g },
];

function tokenize(text) {
  const tokens = [];
  for (const raw of String(text).toLowerCase().match(TOKEN_RE) || []) {
    if (isSearchToken(raw)) tokens.push(raw);
    for (const part of raw.split(TOKEN_SPLIT_RE)) {
      if (part !== raw && isSearchToken(part)) tokens.push(part);
    }
  }
  return tokens;
}

function isSearchToken(token) {
  return !STOPWORDS.has(token) && (token.length > 2 || /^\d+$/.test(token));
}

function normalizeSearchText(text) {
  return String(text || "").toLowerCase().replace(/[^a-z0-9]+/g, " ").trim().replace(/\s+/g, " ");
}

function compactSearchText(text) {
  return normalizeSearchText(text).replace(/\s+/g, "");
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
    const queryTerms = tokenize(query);
    const terms = this.expandTerms(query, queryTerms);
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
    this.applyTitleBoost(query, queryTerms, scores, reasons);

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

  applyTitleBoost(query, queryTerms, scores, reasons) {
    const qNorm = normalizeSearchText(query);
    const qCompact = compactSearchText(query);
    const qTermSet = new Set(queryTerms);
    if (!qNorm || !qTermSet.size) return;
    const sourceIntent = queryTerms.some((term) => SOURCE_INTENT_TERMS.has(term));

    for (let docId = 0; docId < this.pages.length; docId++) {
      const page = this.pages[docId];
      const titleNorm = normalizeSearchText(page.t);
      const slugNorm = normalizeSearchText(page.s);
      const titleCompact = compactSearchText(page.t);
      const slugCompact = compactSearchText(page.s);
      const titleTerms = new Set([...tokenize(page.t), ...tokenize(page.s)]);
      const covered = [...qTermSet].filter((term) => titleTerms.has(term)).length;
      const compactContains = qCompact.length >= 5 && (titleCompact.includes(qCompact) || slugCompact.includes(qCompact));
      const titleInQuery = titleNorm.length >= 5 && qNorm.includes(titleNorm);
      const slugInQuery = slugNorm.length >= 5 && qNorm.includes(slugNorm);
      if (!covered && !titleNorm.includes(qNorm) && !slugNorm.includes(qNorm) && !compactContains && !titleInQuery && !slugInQuery) continue;

      let boost = 0;
      if (titleNorm === qNorm || slugNorm === qNorm || titleCompact === qCompact || slugCompact === qCompact) boost += 30;
      else if (titleNorm.includes(qNorm) || slugNorm.includes(qNorm)) boost += 18;
      if (titleInQuery || slugInQuery) boost += 18;
      if (compactContains) boost += 14;
      if (qCompact.length >= 5 && (titleCompact.startsWith(qCompact) || slugCompact.startsWith(qCompact))) boost += 8;
      if (covered) boost += 9 * (covered / qTermSet.size);
      if (covered === qTermSet.size) boost += 12;
      if (!sourceIntent && page.c === "entities" && boost > 0) boost += 4;
      if (sourceIntent && page.c === "sources" && boost > 0) boost += 3;
      if (!sourceIntent && page.c === "sources" && boost > 0) boost -= 2;
      if (boost <= 0) continue;
      scores.set(docId, (scores.get(docId) || 0) + boost);
      if (!reasons.has(docId) || boost >= 18) reasons.set(docId, "title");
    }
  }

  resultForPage(p, score, reason, snippet) {
    return {
      slug: p.s,
      title: p.t,
      category: p.c,
      type: p.y,
      subcategory: p.u,
      maturity: p.m || (p.pq === "flagship" ? "verified-core" : (p.pq === "record" || p.stub ? "registry-record" : "working-page")),
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
    this.locationIndex = this.buildLocationIndex();
    this.lastIntent = null;
    this.lastAnswer = null;
  }

  seek(query, opts = {}) {
    return this.analyze(query, opts).results;
  }

  analyze(query, opts = {}) {
    const intent = this.classify(query);
    const limit = opts.limit ?? intent.constraints.limit ?? 8;
    const ranked = intent.constraints.noFacts ? [] : this.rankFacts(intent);
    const resultLimit = intent.constraints.singleBest ? 1 : limit;
    const results = ranked.slice(0, resultLimit).map((fact, i) => this.resultForFact(fact, i, intent)).filter(Boolean);
    const answer = this.buildAnswer(intent, ranked.length, results.length, ranked[0] || null);
    this.lastIntent = intent;
    this.lastAnswer = answer;
    // Arrays preserve the established seek() contract. These non-enumerable
    // properties give the UI structured context without affecting iteration,
    // JSON serialization, or legacy merge logic.
    Object.defineProperties(results, {
      intent: { value: intent, enumerable: false, configurable: true },
      answer: { value: answer, enumerable: false, configurable: true },
    });
    return { query: String(query || ""), intent, answer, results };
  }

  classify(query) {
    const q = normalizeSearchText(query);
    const terms = tokenize(q);
    const termSet = new Set(terms);
    const hasPhrase = (...phrases) => phrases.some((phrase) => new RegExp(`\\b${phrase.replace(/[-/\\^$*+?.()|[\]{}]/g, "\\$&").replace(/\\ /g, "\\s+")}\\b`).test(q));

    const domains = [];
    if (hasPhrase("hydro", "hydropower", "run of river", "ror", "hep", "hpp")) domains.push("hydro");
    if (hasPhrase("solar", "photovoltaic", "pv")) domains.push("solar");
    if (hasPhrase("transmission", "grid", "corridor", "interconnection", "power line", "substation")) domains.push("transmission");

    const storageMention = hasPhrase("storage", "reservoir", "reservoir storage", "dry season", "peaking");
    if (storageMention && !domains.length) domains.push("hydro");

    const statuses = [];
    const requestedStatuses = [];
    for (const definition of STATUS_DEFINITIONS) {
      definition.re.lastIndex = 0;
      if (!definition.re.test(q)) continue;
      if (!statuses.includes(definition.status)) statuses.push(definition.status);
      if (!requestedStatuses.includes(definition.requested)) requestedStatuses.push(definition.requested);
    }
    const statusUnion = statuses.length > 1 && (
      /\bwhich\b[\s\S]*\bwhich\b/.test(q)
      || /\b(?:versus|vs|or)\b/.test(q)
    );
    const contradictoryStatuses = statuses.length > 1 && !statusUnion;

    const capacity = parseCapacityConstraint(q);
    const sourceSeeking = terms.some((term) => SOURCE_SEEK_TERMS.has(term)) || hasPhrase("where did", "according to", "proof for");
    const attributeSeeking = terms.some((term) => ATTRIBUTE_TERMS.has(term));
    const superlative = hasPhrase("biggest", "largest", "highest capacity", "top", "most mw", "smallest", "lowest capacity", "second", "third");
    const singleBest = superlative && !/\b(?:projects|plants|schemes)\b/.test(q);
    const sort = hasPhrase("smallest", "lowest capacity") ? "asc" : "desc";
    const hasProjectTerm = terms.some((term) => PROJECT_TERMS.has(term));
    const locations = this.matchLocations(q);
    const targetFactIds = this.matchNamedFacts(termSet, q);
    const targetNames = targetFactIds.map((id) => this.factById.get(id)?.name).filter(Boolean);
    const subjectTerms = terms.filter((term) => !INTENT_CONTROL_TERMS.has(term) && !/^\d+(?:\.\d+)?$/.test(term));
    const storageConstraint = storageMention && (
      hasProjectTerm
      || superlative
      || statuses.length > 0
      || Boolean(capacity)
      || targetFactIds.length > 0
    );
    const hasDomainTerm = domains.length > 0 || storageMention;
    const locationScoped = locations.length > 0 && targetFactIds.length === 0 && (hasProjectTerm || hasDomainTerm || hasPhrase("basin", "river", "district"));
    const constrainedList = statuses.length > 0 || Boolean(capacity) || locationScoped || storageConstraint;
    const targetedLookup = targetFactIds.length > 0 && (sourceSeeking || attributeSeeking || statuses.length > 0 || Boolean(capacity));
    const factish = superlative || targetedLookup || constrainedList || (hasProjectTerm && hasDomainTerm) || (sourceSeeking && (hasDomainTerm || hasProjectTerm));

    // Generic "largest project" questions refer to generation assets unless a
    // user names another domain. Status-only queries deliberately remain
    // cross-domain so stalled transmission and hydropower records can coexist.
    if (!domains.length && superlative) domains.push("hydro");

    const primaryStatus = statuses.length === 1 ? statuses[0] : (statuses.length ? "multiple" : "any");
    return {
      relevant: factish,
      kind: sourceSeeking ? "source-seeking" : ((targetedLookup || singleBest) ? "fact-lookup" : "project-list"),
      sourceSeeking,
      attributeSeeking,
      constraints: {
        noFacts: !factish,
        domains,
        requiredFacets: storageConstraint ? ["storage"] : [],
        statuses,
        statusMode: statusUnion ? "any" : "all",
        contradictoryStatuses,
        excludedStatuses: statuses.length ? [] : ["conceptual"],
        requestedStatuses,
        status: primaryStatus,
        locations,
        capacity,
        targetFactIds,
        targetNames,
        subjectTerms,
        sourceSeeking,
        metric: "capacity_mw",
        requiresCapacity: Boolean(capacity) || superlative,
        superlative,
        singleBest,
        sort,
        limit: 5,
      },
    };
  }

  rankFacts(intent) {
    const c = intent.constraints || intent;
    if (c.contradictoryStatuses) return [];
    const domains = new Set(c.domains || []);
    const requiredFacets = new Set(c.requiredFacets || []);
    const statuses = new Set(c.statuses || (c.status && c.status !== "any" ? [c.status] : []));
    const excludedStatuses = new Set(c.excludedStatuses || []);
    const targetFactIds = new Set(c.targetFactIds || []);
    const hardTarget = targetFactIds.size > 0 && (intent.kind === "fact-lookup" || intent.sourceSeeking);
    return this.facts
      .filter((fact) => {
        const facets = new Set(fact.facets || [fact.domain]);
        if (domains.size && ![...domains].some((domain) => facets.has(domain) || fact.domain === domain)) return false;
        if ([...requiredFacets].some((facet) => !this.factHasFacet(fact, facet, facets))) return false;
        if (excludedStatuses.has(fact.status)) return false;
        if (statuses.size && !this.factMatchesStatuses(fact, statuses)) return false;
        if (hardTarget && !targetFactIds.has(fact.id)) return false;
        if (c.locations?.length && !this.factMatchesLocations(fact, c.locations)) return false;
        if (c.capacity && !capacityMatches(fact.capacity_mw, c.capacity)) return false;
        if (c.requiresCapacity && finiteNumber(fact.capacity_mw) == null) return false;
        return true;
      })
      .sort((a, b) => {
        if (targetFactIds.has(a.id) !== targetFactIds.has(b.id)) return targetFactIds.has(a.id) ? -1 : 1;
        const aCapacity = finiteNumber(a.capacity_mw);
        const bCapacity = finiteNumber(b.capacity_mw);
        const aFinite = aCapacity != null;
        const bFinite = bCapacity != null;
        if (aFinite !== bFinite) return aFinite ? -1 : 1;
        if (aFinite && aCapacity !== bCapacity) return c.sort === "asc" ? aCapacity - bCapacity : bCapacity - aCapacity;
        return String(a.name || "").localeCompare(String(b.name || ""));
      });
  }

  resultForFact(fact, i, intent = null) {
    const slug = fact.wiki_slug || fact.slug || "";
    const page = slug ? this.pageBySlug.get(slug) : null;
    const evidenceUrls = Array.isArray(fact.evidence_urls) ? fact.evidence_urls : [];
    const sources = Array.isArray(fact.sources) ? fact.sources : [];
    const details = [formatMw(fact.capacity_mw), fact.status_display || fact.status_raw || fact.status, fact.river, fact.district].filter(Boolean);
    return {
      kind: slug ? "wiki" : "fact",
      structured: true,
      factId: fact.id,
      slug,
      title: fact.name,
      category: page?.c || "facts",
      type: page?.y || "fact",
      subcategory: page?.u || "",
      maturity: page?.m || (page?.pq === "flagship" ? "verified-core" : (page?.pq === "record" || page?.stub ? "registry-record" : "working-page")),
      score: 1 - i * 0.04,
      reason: "fact",
      chip: fact.status || "fact",
      status: fact.status || "",
      domain: fact.domain || "",
      facets: fact.facets || [],
      capacityMw: finiteNumber(fact.capacity_mw),
      river: fact.river || "",
      basin: fact.basin || "",
      district: fact.district || "",
      asOf: fact.as_of || fact.last_updated || "",
      confidence: fact.confidence || "",
      evidenceCount: evidenceUrls.length,
      evidenceUrls,
      sources,
      sourceSeeking: Boolean(intent?.sourceSeeking),
      snippetHtml: escapeHtml(details.join(" · ")),
    };
  }

  buildLocationIndex() {
    const locations = new Map();
    for (const fact of this.facts) {
      for (const field of ["basin", "river", "district", "province"]) {
        const value = String(fact[field] || "").trim();
        const normalized = normalizeSearchText(value);
        if (!normalized || normalized.length < 4) continue;
        const current = locations.get(normalized) || { normalized, labels: new Set(), fields: new Set() };
        current.labels.add(value);
        current.fields.add(field);
        locations.set(normalized, current);
      }
    }
    return Array.from(locations.values())
      .map((item) => ({ normalized: item.normalized, label: Array.from(item.labels)[0], fields: Array.from(item.fields) }))
      .sort((a, b) => b.normalized.length - a.normalized.length);
  }

  matchLocations(normalizedQuery) {
    const matches = [];
    for (const location of this.locationIndex) {
      const re = new RegExp(`(?:^|\\s)${location.normalized.replace(/[.*+?^${}()|[\]\\]/g, "\\$&").replace(/\\ /g, "\\s+")}(?:$|\\s)`);
      if (!re.test(normalizedQuery)) continue;
      if (!matches.some((item) => item.normalized === location.normalized)) matches.push(location);
    }
    return matches;
  }

  matchNamedFacts(queryTerms, normalizedQuery) {
    const matches = [];
    for (const fact of this.facts) {
      const nameTerms = normalizeSearchText(fact.name).split(" ").filter((term) => term && !STOPWORDS.has(term) && !GENERIC_NAME_TERMS.has(term));
      if (!nameTerms.length) continue;
      const allPresent = nameTerms.every((term) => queryTerms.has(term));
      const namePhrase = normalizeSearchText(fact.name).replace(/\b(?:hep|hpp|hydroelectric|hydropower|power plant|project|scheme)\b/g, "").trim().replace(/\s+/g, " ");
      const phrasePresent = namePhrase.length >= 5 && (` ${normalizedQuery} `).includes(` ${namePhrase} `);
      const specificEnough = nameTerms.length > 1 || nameTerms[0].length >= 6;
      if ((allPresent && specificEnough) || phrasePresent) matches.push(fact.id);
    }
    return matches;
  }

  factHasFacet(fact, facet, knownFacets = null) {
    const facets = knownFacets || new Set(fact.facets || [fact.domain]);
    if (facets.has(facet)) return true;
    if (facet !== "storage") return false;
    const storageText = normalizeSearchText([fact.name, fact.project_type, fact.source_layer].filter(Boolean).join(" "));
    return /\b(?:storage|reservoir)\b/.test(storageText)
      || finiteNumber(fact.total_storage_mcm) != null
      || finiteNumber(fact.effective_storage_mcm) != null;
  }

  factMatchesStatuses(fact, statuses) {
    if (statuses.has(fact.status)) return true;
    // A partially energized corridor is relevant to an "operating" query,
    // while its more precise status remains visible in the result chip.
    return statuses.has("operating") && fact.status === "partially-operational";
  }

  factMatchesLocations(fact, locations) {
    const haystack = normalizeSearchText([fact.basin, fact.river, fact.district, fact.province, fact.name].filter(Boolean).join(" "));
    return locations.every((location) => (` ${haystack} `).includes(` ${location.normalized} `));
  }

  buildAnswer(intent, totalCount, shownCount, topFact = null) {
    const c = intent.constraints;
    if (c.noFacts) {
      return {
        kind: "none",
        title: "",
        summary: "",
        count: 0,
        shownCount: 0,
        hasMore: false,
        empty: true,
        applicable: false,
        status: c.status,
        statuses: c.statuses || [],
        requestedStatuses: c.requestedStatuses || [],
        domains: c.domains || [],
        facets: c.requiredFacets || [],
        locations: c.locations || [],
        capacity: c.capacity || null,
        sourceSeeking: intent.sourceSeeking,
      };
    }
    const statusLabels = c.requestedStatuses?.length ? c.requestedStatuses : c.statuses;
    const descriptors = c.targetNames?.length ? c.targetNames : [
      ...(statusLabels || []),
      ...(c.requiredFacets || []),
      ...(c.domains || []).map((domain) => domain === "hydro" ? "hydropower" : domain),
      ...(c.locations || []).slice(0, 2).map((location) => location.label),
    ];
    const uniqueDescriptors = [...new Set(descriptors)];
    const subject = uniqueDescriptors.length ? uniqueDescriptors.join(" · ") : "structured project";
    const title = intent.sourceSeeking
      ? `Evidence for ${subject}`
      : (intent.kind === "fact-lookup" && topFact ? String(topFact.name || subject) : `${subject[0].toUpperCase()}${subject.slice(1)} projects`);
    const capacityText = formatCapacityConstraint(c.capacity);
    const qualifier = capacityText ? ` ${capacityText}` : "";
    const lookupDetails = intent.kind === "fact-lookup" && topFact
      ? [topFact.status_display || topFact.status_raw || topFact.status, formatMw(topFact.capacity_mw)].filter(Boolean).join(" · ")
      : "";
    const summary = c.contradictoryStatuses
      ? `No single structured record can satisfy the conflicting statuses ${statusLabels.join(" and ")}.`
      : lookupDetails
        ? `${lookupDetails}.`
      : totalCount
        ? `${totalCount} ${subject} ${totalCount === 1 ? "record matches" : "records match"}${qualifier}.`
        : `No structured ${subject} records match${qualifier}.`;
    return {
      kind: intent.kind,
      title,
      summary,
      count: totalCount,
      shownCount,
      hasMore: totalCount > shownCount,
      empty: totalCount === 0,
      applicable: true,
      status: c.status,
      statuses: c.statuses || [],
      requestedStatuses: c.requestedStatuses || [],
      contradictoryStatuses: Boolean(c.contradictoryStatuses),
      domains: c.domains || [],
      facets: c.requiredFacets || [],
      locations: c.locations || [],
      capacity: c.capacity || null,
      sourceSeeking: intent.sourceSeeking,
      factId: topFact ? topFact.id : null,
    };
  }

  getFact(id) {
    return this.factById.get(id) || null;
  }
}

function parseCapacityConstraint(query) {
  const q = String(query || "").replace(/,/g, "");
  const number = "(\\d+(?:\\.\\d+)?)";
  let match = q.match(new RegExp(`\\bbetween\\s+${number}\\s*(?:mw)?\\s+(?:and|to)\\s+${number}\\s*mw?\\b`));
  if (match) return { min: Number(match[1]), minInclusive: true, max: Number(match[2]), maxInclusive: true, unit: "MW" };
  match = q.match(new RegExp(`\\b(?:at least|minimum(?: of)?|no less than)\\s+${number}\\s*mw?\\b`));
  if (match) return { min: Number(match[1]), minInclusive: true, max: null, maxInclusive: false, unit: "MW" };
  match = q.match(new RegExp(`\\b(?:over|above|more than|greater than|exceeding)\\s+${number}\\s*mw?\\b`));
  if (match) return { min: Number(match[1]), minInclusive: false, max: null, maxInclusive: false, unit: "MW" };
  match = q.match(new RegExp(`\\b${number}\\s*mw\\s*(?:or more|and above)\\b`));
  if (match) return { min: Number(match[1]), minInclusive: true, max: null, maxInclusive: false, unit: "MW" };
  match = q.match(new RegExp(`\\b(?:at most|maximum(?: of)?|up to|no more than)\\s+${number}\\s*mw?\\b`));
  if (match) return { min: null, minInclusive: false, max: Number(match[1]), maxInclusive: true, unit: "MW" };
  match = q.match(new RegExp(`\\b(?:under|below|less than)\\s+${number}\\s*mw?\\b`));
  if (match) return { min: null, minInclusive: false, max: Number(match[1]), maxInclusive: false, unit: "MW" };
  return null;
}

function capacityMatches(value, constraint) {
  const capacity = finiteNumber(value);
  if (capacity == null) return false;
  if (constraint.min != null && (constraint.minInclusive ? capacity < constraint.min : capacity <= constraint.min)) return false;
  if (constraint.max != null && (constraint.maxInclusive ? capacity > constraint.max : capacity >= constraint.max)) return false;
  return true;
}

function formatCapacityConstraint(constraint) {
  if (!constraint) return "";
  if (constraint.min != null && constraint.max != null) return `between ${formatMw(constraint.min)} and ${formatMw(constraint.max)}`;
  if (constraint.min != null) return `${constraint.minInclusive ? "at least" : "over"} ${formatMw(constraint.min)}`;
  if (constraint.max != null) return `${constraint.maxInclusive ? "at most" : "under"} ${formatMw(constraint.max)}`;
  return "";
}

function formatMw(value) {
  const n = finiteNumber(value);
  if (n == null) return "";
  return `${n.toLocaleString(undefined, { maximumFractionDigits: n >= 100 ? 0 : 2 })} MW`;
}

function finiteNumber(value) {
  if (value == null || value === "" || typeof value === "boolean") return null;
  const number = Number(value);
  return Number.isFinite(number) ? number : null;
}

window.NepalExplorer = window.NepalExplorer || {};
Object.assign(window.NepalExplorer, { StaticSearchIndex, StaticFactIndex, staticSearchTokenize: tokenize });
window.NepalExplorer._staticSearchLoaded = true;
})();
