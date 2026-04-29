// Lazy query-vector boost for Seek. The corpus is precomputed at build time;
// only the user's query is embedded in the browser.
(function () {
if (window.NepalExplorer && window.NepalExplorer._vectorSearchLoaded) return;

function decodeInt8Base64(b64) {
  const bin = atob(b64);
  const bytes = new Int8Array(bin.length);
  for (let i = 0; i < bin.length; i++) bytes[i] = bin.charCodeAt(i) << 24 >> 24;
  return bytes;
}

function dotQueryInt8(query, encoded) {
  let score = 0;
  const n = Math.min(query.length, encoded.length);
  for (let i = 0; i < n; i++) score += query[i] * (encoded[i] / 127);
  return score;
}

class VectorSeekBoost {
  constructor(index, opts = {}) {
    this.index = index || {};
    this.chunks = (this.index.chunks || []).map((chunk) => ({ ...chunk, _v: decodeInt8Base64(chunk.v) }));
    this.model = this.index.model || {};
    this.onStatus = opts.onStatus || (() => {});
    this.extractor = null;
    this.loading = null;
    this.failed = null;
    this.backend = "";
  }

  async ensureExtractor() {
    if (this.extractor) return this.extractor;
    if (this.failed) throw this.failed;
    if (this.loading) return this.loading;
    this.loading = this.loadExtractor();
    return this.loading;
  }

  async loadExtractor() {
    try {
      this.onStatus({ state: "loading", message: "Loading meaning boost..." });
      const mod = await import("https://cdn.jsdelivr.net/npm/@huggingface/transformers@3.8.1/+esm");
      const modelId = this.model.browser_id || this.model.id;
      const attempts = [];
      if (navigator.gpu) attempts.push({ device: "webgpu", dtype: "fp16", label: "WebGPU" });
      attempts.push({ dtype: "q8", label: "WASM q8" });
      let lastErr = null;
      for (const attempt of attempts) {
        try {
          this.onStatus({ state: "loading", message: `Preparing ${attempt.label} meaning boost...` });
          const { label, ...options } = attempt;
          this.extractor = await mod.pipeline("feature-extraction", modelId, {
            ...options,
            progress_callback: (p) => {
              if (p && p.status) this.onStatus({ state: "loading", message: `${p.status}` });
            },
          });
          this.backend = label;
          this.onStatus({ state: "ready", message: `Meaning boost ready (${label})` });
          return this.extractor;
        } catch (err) {
          lastErr = err;
        }
      }
      throw lastErr || new Error("No browser embedding backend available");
    } catch (err) {
      this.failed = err;
      this.onStatus({ state: "failed", message: "Meaning boost unavailable; showing fast Seek results." });
      throw err;
    }
  }

  async search(query, opts = {}) {
    const limit = opts.limit ?? 40;
    const extractor = await this.ensureExtractor();
    const prefix = this.model.query_prefix || "";
    const output = await extractor(prefix + query, { pooling: "mean", normalize: true });
    const qv = output.data || output;
    const pageScores = new Map();
    const chunkHits = new Map();
    for (const chunk of this.chunks) {
      const score = dotQueryInt8(qv, chunk._v);
      if (score <= 0) continue;
      const prev = pageScores.get(chunk.p) || 0;
      const boosted = Math.max(prev, score) + Math.min(prev, score) * 0.16;
      pageScores.set(chunk.p, boosted);
      if (!chunkHits.has(chunk.p) || chunkHits.get(chunk.p).score < score) {
        chunkHits.set(chunk.p, { score, heading: chunk.h, snippet: chunk.s });
      }
    }
    return Array.from(pageScores.entries())
      .sort((a, b) => b[1] - a[1])
      .slice(0, limit)
      .map(([pageId, score]) => ({ pageId, score, ...(chunkHits.get(pageId) || {}) }));
  }
}

window.NepalExplorer = window.NepalExplorer || {};
Object.assign(window.NepalExplorer, { VectorSeekBoost });
window.NepalExplorer._vectorSearchLoaded = true;
})();
