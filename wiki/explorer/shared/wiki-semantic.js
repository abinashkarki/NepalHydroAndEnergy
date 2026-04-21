// Semantic search via transformers.js (all-MiniLM-L6-v2).
// First run downloads the model (~25MB) and embeds all pages; both cached in IndexedDB.
// All offline after that. Heavy but lazy: only loaded when user activates "Semantic" mode.
(function () {
if (window.NepalExplorer && window.NepalExplorer._semanticLoaded) return;

const MODEL_ID = "Xenova/all-MiniLM-L6-v2";
const DB_NAME = "nepal-explorer-embeddings";
const STORE = "embeddings";
const SCHEMA_VERSION = 2;

let _extractor = null;
let _docVecs = null; // [{slug, title, category, vec: Float32Array}]
let _meta = null;

function openDB() {
  return new Promise((resolve, reject) => {
    const req = indexedDB.open(DB_NAME, SCHEMA_VERSION);
    req.onupgradeneeded = () => {
      const db = req.result;
      if (db.objectStoreNames.contains(STORE)) db.deleteObjectStore(STORE);
      db.createObjectStore(STORE);
    };
    req.onsuccess = () => resolve(req.result);
    req.onerror = () => reject(req.error);
  });
}

async function dbGet(key) {
  const db = await openDB();
  return new Promise((res, rej) => {
    const tx = db.transaction(STORE, "readonly").objectStore(STORE).get(key);
    tx.onsuccess = () => res(tx.result);
    tx.onerror = () => rej(tx.error);
  });
}
async function dbSet(key, value) {
  const db = await openDB();
  return new Promise((res, rej) => {
    const tx = db.transaction(STORE, "readwrite").objectStore(STORE).put(value, key);
    tx.onsuccess = () => res();
    tx.onerror = () => rej(tx.error);
  });
}

async function loadExtractor(progressCb) {
  if (_extractor) return _extractor;
  if (progressCb) progressCb({ phase: "model", progress: 0, message: "loading transformers.js…" });
  // Dynamic ESM import from CDN. Falls back to CDN module if local missing.
  const mod = await import("https://cdn.jsdelivr.net/npm/@huggingface/transformers@3.0.0/+esm");
  if (progressCb) progressCb({ phase: "model", progress: 0.2, message: `downloading ${MODEL_ID}…` });
  _extractor = await mod.pipeline("feature-extraction", MODEL_ID, {
    progress_callback: (p) => {
      if (!progressCb) return;
      const pct = p.progress != null ? p.progress / 100 : (p.loaded && p.total ? p.loaded / p.total : 0);
      progressCb({ phase: "model", progress: 0.2 + 0.6 * pct, message: `${p.status || "loading"} · ${Math.round(pct * 100)}%` });
    },
  });
  if (progressCb) progressCb({ phase: "model", progress: 0.85, message: "model ready" });
  return _extractor;
}

async function embedText(text) {
  const extractor = _extractor || await loadExtractor();
  const result = await extractor(text.slice(0, 1500), { pooling: "mean", normalize: true });
  return new Float32Array(result.data);
}

function cosine(a, b) {
  let s = 0;
  const n = a.length;
  for (let i = 0; i < n; i++) s += a[i] * b[i];
  return s;
}

async function ensureIndex(meta, progressCb) {
  if (_docVecs) return _docVecs;
  _meta = meta;

  // Try cache.
  const cached = await dbGet("docs");
  if (cached && cached.modelId === MODEL_ID && cached.version === SCHEMA_VERSION && cached.totalPages === meta.pages.length) {
    _docVecs = cached.docs.map((d) => ({ ...d, vec: new Float32Array(d.vec) }));
    if (progressCb) progressCb({ phase: "ready", progress: 1, message: `loaded ${_docVecs.length} cached embeddings` });
    return _docVecs;
  }

  await loadExtractor(progressCb);
  if (progressCb) progressCb({ phase: "embedding", progress: 0, message: `indexing ${meta.pages.length} pages…` });

  const docs = [];
  for (let i = 0; i < meta.pages.length; i++) {
    const p = meta.pages[i];
    // Compose a context-rich string for embedding: title, headings, and body lead.
    const blob = `${p.title}. ${(p.tags || []).join(", ")}. ${(p.headings || []).slice(0, 6).join(". ")}. ${p.excerpt}. ${p.body_text}`;
    const vec = await embedText(blob);
    docs.push({ slug: p.slug, title: p.title, category: p.category, type: p.type, subcategory: p.subcategory, vec });
    if (progressCb) progressCb({ phase: "embedding", progress: (i + 1) / meta.pages.length, message: `indexed ${i + 1} / ${meta.pages.length}` });
  }
  _docVecs = docs;

  await dbSet("docs", {
    modelId: MODEL_ID,
    version: SCHEMA_VERSION,
    totalPages: meta.pages.length,
    docs: docs.map((d) => ({ slug: d.slug, title: d.title, category: d.category, type: d.type, subcategory: d.subcategory, vec: Array.from(d.vec) })),
    builtAt: Date.now(),
  });
  if (progressCb) progressCb({ phase: "ready", progress: 1, message: `indexed ${docs.length} pages` });
  return _docVecs;
}

async function search(query, opts = {}) {
  const limit = opts.limit ?? 20;
  if (!_docVecs) throw new Error("Index not built; call ensureIndex first");
  const qv = await embedText(query);
  const scored = _docVecs.map((d) => ({ slug: d.slug, title: d.title, category: d.category, type: d.type, subcategory: d.subcategory, score: cosine(qv, d.vec) }));
  scored.sort((a, b) => b.score - a.score);
  const top = scored.slice(0, limit);
  // Attach excerpts from meta for snippet display.
  if (_meta) {
    const bySlug = Object.fromEntries(_meta.pages.map((p) => [p.slug, p]));
    for (const r of top) {
      const p = bySlug[r.slug];
      r.snippet = p ? (p.excerpt || (p.body_text || "").slice(0, 220)) : "";
    }
  }
  return top;
}

async function clearCache() {
  const db = await openDB();
  return new Promise((res) => { db.transaction(STORE, "readwrite").objectStore(STORE).clear().onsuccess = res; });
}

window.NepalExplorer = window.NepalExplorer || {};
Object.assign(window.NepalExplorer, {
  semantic: { ensureIndex, search, embedText, clearCache, MODEL_ID },
});
window.NepalExplorer._semanticLoaded = true;
})();
