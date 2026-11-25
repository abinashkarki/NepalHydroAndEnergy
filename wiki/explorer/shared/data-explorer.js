/* Nepal Energy Explorer — Data Tables view.
 *
 * Interactive, filterable, sortable registry tables rendered in the reader pane.
 * Zero dependencies and zero startup cost: nothing is fetched until a user opens
 * a table, and each CSV is fetched at most once (in-memory promise cache).
 *
 * Pure helpers (parseCSV, filterRows, sortRows, summarize, toCSV) are exported on
 * window.NepalDataExplorer for tests/test_data_explorer.js.
 */
(function (root) {
  "use strict";

  const TABLE_BASE = "tables/";

  const DATASETS = {
    substations: {
      tab: "substations",
      label: "Substations",
      file: "substation_specs.csv",
      companion: "data-substation-inventory",
      source: "NEA annual reports and RPGCL map; coordinates precision-tagged.",
      columns: [
        { key: "substation_name", label: "Substation" },
        { key: "highest_voltage_kv", label: "kV", numeric: true },
        { key: "status", label: "Status" },
        { key: "province", label: "Province" },
        { key: "district", label: "District" },
        { key: "installed_mva", label: "Installed MVA", numeric: true },
        { key: "planned_additional_mva", label: "Pipeline MVA", numeric: true },
        { key: "linked_solar_award_mw", label: "Solar linked MW", numeric: true },
      ],
      filters: [
        { key: "province", label: "Province" },
        { key: "highest_voltage_kv", label: "Voltage (kV)" },
        { key: "status", label: "Status" },
      ],
      sums: [
        { key: "installed_mva", label: "installed MVA" },
        { key: "planned_additional_mva", label: "pipeline MVA" },
      ],
      defaultSort: { key: "installed_mva", dir: "desc" },
      action(row) {
        if (!row.slug || !row.latitude) return null;
        return { kind: "fact", id: `substation:${row.slug}`, label: "Show on map" };
      },
    },
    hydro: {
      tab: "hydro",
      label: "Hydropower specs",
      file: "project_specs.csv",
      companion: "hydropower-system",
      source: "Hand-curated project specs; see each project page for sources.",
      columns: [
        { key: "slug", label: "Project", title: true },
        { key: "capacity_mw", label: "MW", numeric: true },
        { key: "status", label: "Status" },
        { key: "project_type", label: "Type" },
        { key: "river", label: "River" },
        { key: "annual_design_energy_gwh", label: "Annual GWh", numeric: true },
        { key: "dry_share_pct", label: "Dry share %", numeric: true },
        { key: "cost_per_mw_usd_m", label: "Cost/MW (USD m)", numeric: true },
      ],
      filters: [
        { key: "status", label: "Status" },
        { key: "project_type", label: "Project type" },
      ],
      sums: [
        { key: "capacity_mw", label: "MW" },
        { key: "annual_design_energy_gwh", label: "design GWh" },
      ],
      defaultSort: { key: "capacity_mw", dir: "desc" },
      action(row) {
        return row.slug ? { kind: "page", slug: row.slug, label: "Open page" } : null;
      },
    },
    tariffs: {
      tab: "tariffs",
      label: "ERC retail tariffs",
      file: "erc_retail_tariffs.csv",
      companion: "data-erc-retail-tariffs",
      source: "Electricity Regulatory Commission tariff orders.",
      columns: [
        { key: "customer_category", label: "Customer category" },
        { key: "voltage_or_ampere_tier", label: "Voltage / tier" },
        { key: "season", label: "Season" },
        { key: "time_band", label: "Time band" },
        { key: "slab_kwh_range", label: "Slab (kWh)" },
        { key: "energy_rate_npr_kwh", label: "Energy rate (NPR/kWh)", numeric: true },
        { key: "demand_charge_npr_kva", label: "Demand charge (NPR/kVA)", numeric: true },
        { key: "effective_from", label: "Effective from" },
      ],
      filters: [
        { key: "customer_category", label: "Customer category" },
        { key: "season", label: "Season" },
        { key: "time_band", label: "Time band" },
      ],
      sums: [],
      defaultSort: { key: "energy_rate_npr_kwh", dir: "desc" },
      action: () => null,
    },
    nonhydro: {
      tab: "nonhydro",
      label: "DoED non-hydro",
      file: "doed_nonhydro_registry.csv",
      companion: "data-solar-fleet-inventory",
      source: "Department of Electricity Development licence register.",
      columns: [
        { key: "project", label: "Project" },
        { key: "technology", label: "Technology" },
        { key: "regulatory_category", label: "Regulatory category" },
        { key: "capacity_mw", label: "MW", numeric: true },
        { key: "license_status", label: "Licence status" },
        { key: "delivery_status", label: "Delivery status" },
        { key: "location_text", label: "Location" },
      ],
      filters: [
        { key: "technology", label: "Technology" },
        { key: "regulatory_category", label: "Regulatory category" },
      ],
      sums: [{ key: "capacity_mw", label: "MW" }],
      defaultSort: { key: "capacity_mw", dir: "desc" },
      action: () => null,
    },
    anchors: {
      tab: "anchors",
      label: "Industrial load anchors",
      file: "industrial_load_anchors.csv",
      companion: "data-load-anchors-and-fossil-backbone",
      source: "Industrial estates, SEZs and corridors with linked substations.",
      columns: [
        { key: "anchor_name", label: "Anchor" },
        { key: "anchor_type", label: "Type" },
        { key: "district", label: "District" },
        { key: "province", label: "Province" },
        { key: "nearest_substation_name", label: "Substation" },
        { key: "supply_voltage_kv", label: "Supply kV", numeric: true },
        { key: "project_status_as_reported", label: "Status as reported" },
      ],
      filters: [
        { key: "anchor_type", label: "Type" },
        { key: "province", label: "Province" },
      ],
      sums: [],
      defaultSort: { key: "anchor_name", dir: "asc" },
      action(row) {
        return row.substation_slug ? { kind: "fact", id: `substation:${row.substation_slug}`, label: "Show substation" } : null;
      },
    },
    institutions: {
      tab: "anchors",
      label: "Core institutions",
      file: "energy_institutions.csv",
      companion: "data-energy-institutions",
      source: "Statutes and official institution websites.",
      columns: [
        { key: "short_name", label: "Short name" },
        { key: "full_name", label: "Institution" },
        { key: "institution_type", label: "Type" },
        { key: "parent_ministry", label: "Parent ministry" },
        { key: "established", label: "Established" },
      ],
      filters: [{ key: "institution_type", label: "Type" }],
      sums: [],
      defaultSort: { key: "short_name", dir: "asc" },
      action(row) {
        return row.wiki_page_slug ? { kind: "page", slug: row.wiki_page_slug, label: "Open page" } : null;
      },
    },
  };

  const TABS = [
    { id: "substations", label: "Substations", datasets: ["substations"] },
    { id: "hydro", label: "Hydropower", datasets: ["hydro"] },
    { id: "tariffs", label: "ERC tariffs", datasets: ["tariffs"] },
    { id: "nonhydro", label: "Non-hydro", datasets: ["nonhydro"] },
    { id: "anchors", label: "Load anchors & institutions", datasets: ["anchors", "institutions"] },
  ];

  // ---------------------------------------------------------------- helpers

  /** RFC 4180 CSV parser: quoted fields, embedded commas/quotes/newlines, CRLF, BOM. */
  function parseCSV(text) {
    const src = String(text || "").replace(/^﻿/, "");
    const records = [];
    let field = "";
    let record = [];
    let inQuotes = false;
    for (let i = 0; i < src.length; i += 1) {
      const ch = src[i];
      if (inQuotes) {
        if (ch === '"') {
          if (src[i + 1] === '"') { field += '"'; i += 1; } else { inQuotes = false; }
        } else {
          field += ch;
        }
      } else if (ch === '"') {
        inQuotes = true;
      } else if (ch === ",") {
        record.push(field); field = "";
      } else if (ch === "\n" || ch === "\r") {
        if (ch === "\r" && src[i + 1] === "\n") i += 1;
        record.push(field); field = "";
        records.push(record); record = [];
      } else {
        field += ch;
      }
    }
    if (field !== "" || record.length) { record.push(field); records.push(record); }
    const nonEmpty = records.filter((r) => !(r.length === 1 && r[0] === ""));
    if (!nonEmpty.length) return { columns: [], rows: [] };
    const columns = nonEmpty[0];
    const rows = nonEmpty.slice(1).map((values) => {
      const row = {};
      columns.forEach((col, idx) => { row[col] = values[idx] !== undefined ? values[idx] : ""; });
      return row;
    });
    return { columns, rows };
  }

  function toNumber(value) {
    if (value === null || value === undefined) return null;
    const s = String(value).replace(/,/g, "").trim();
    if (!s) return null;
    const n = Number(s);
    return Number.isFinite(n) ? n : null;
  }

  /** filters: {column: value} (exact match; "" = any). query: case-insensitive substring over searchKeys. */
  function filterRows(rows, { filters = {}, query = "", searchKeys = null } = {}) {
    const active = Object.entries(filters).filter(([, v]) => v !== "" && v !== null && v !== undefined);
    const q = String(query || "").trim().toLowerCase();
    return rows.filter((row) => {
      for (const [key, value] of active) {
        if (String(row[key] ?? "") !== String(value)) return false;
      }
      if (!q) return true;
      const keys = searchKeys || Object.keys(row);
      return keys.some((k) => String(row[k] ?? "").toLowerCase().includes(q));
    });
  }

  /** Stable sort; numeric sorts put blanks last in both directions. */
  function sortRows(rows, key, dir = "asc", numeric = false) {
    const sign = dir === "desc" ? -1 : 1;
    return rows
      .map((row, idx) => ({ row, idx }))
      .sort((a, b) => {
        let cmp;
        if (numeric) {
          const x = toNumber(a.row[key]);
          const y = toNumber(b.row[key]);
          if (x === null && y === null) cmp = 0;
          else if (x === null) return 1;
          else if (y === null) return -1;
          else cmp = (x - y) * sign;
        } else {
          cmp = String(a.row[key] ?? "").localeCompare(String(b.row[key] ?? ""), undefined, { numeric: true, sensitivity: "base" }) * sign;
          const blankA = !String(a.row[key] ?? "").trim();
          const blankB = !String(b.row[key] ?? "").trim();
          if (blankA !== blankB) return blankA ? 1 : -1;
        }
        return cmp || a.idx - b.idx;
      })
      .map((item) => item.row);
  }

  function summarize(rows, sums = []) {
    const out = { count: rows.length, totals: {} };
    sums.forEach(({ key }) => {
      let total = 0;
      let counted = 0;
      rows.forEach((row) => {
        const n = toNumber(row[key]);
        if (n !== null) { total += n; counted += 1; }
      });
      out.totals[key] = { total: Math.round(total * 100) / 100, counted };
    });
    return out;
  }

  function csvEscape(value) {
    const s = String(value ?? "");
    return /[",\r\n]/.test(s) ? `"${s.replace(/"/g, '""')}"` : s;
  }

  function toCSV(columns, rows) {
    return [columns.map(csvEscape).join(",")]
      .concat(rows.map((row) => columns.map((c) => csvEscape(row[c])).join(",")))
      .join("\r\n") + "\r\n";
  }

  function distinctValues(rows, key) {
    const values = new Set();
    rows.forEach((row) => { const v = String(row[key] ?? "").trim(); if (v) values.add(v); });
    return [...values].sort((a, b) => a.localeCompare(b, undefined, { numeric: true }));
  }

  function escapeHtml(value) {
    return String(value ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  }

  function formatCell(value, numeric) {
    if (!numeric) return escapeHtml(value);
    const n = toNumber(value);
    return n === null ? "" : n.toLocaleString("en-US", { maximumFractionDigits: 2 });
  }

  function titleFromSlug(slug, hooks) {
    const t = hooks && typeof hooks.pageTitle === "function" ? hooks.pageTitle(slug) : null;
    return t || String(slug || "").replace(/-/g, " ").replace(/\b\w/g, (c) => c.toUpperCase());
  }

  // ---------------------------------------------------------------- view

  function createExplorer({ fetchImpl, hooks = {}, base = TABLE_BASE } = {}) {
    const cache = {};
    const state = { tab: "substations", dataset: "substations", filters: {}, query: "", sort: null };
    let container = null;

    function load(datasetId) {
      const ds = DATASETS[datasetId];
      if (!cache[datasetId]) {
        const doFetch = fetchImpl || root.fetch.bind(root);
        cache[datasetId] = doFetch(base + ds.file)
          .then((r) => { if (!r.ok) throw new Error(`fetch failed: ${ds.file}`); return r.text(); })
          .then(parseCSV)
          .catch((err) => { delete cache[datasetId]; throw err; });
      }
      return cache[datasetId];
    }

    function currentView(data) {
      const ds = DATASETS[state.dataset];
      const searchKeys = ds.columns.map((c) => c.key);
      const filtered = filterRows(data.rows, { filters: state.filters, query: state.query, searchKeys });
      const sort = state.sort || ds.defaultSort;
      const col = ds.columns.find((c) => c.key === sort.key);
      const sorted = sortRows(filtered, sort.key, sort.dir, Boolean(col && col.numeric));
      return { ds, sorted, sort, summary: summarize(sorted, ds.sums) };
    }

    function renderShell() {
      const tabs = TABS.map((t) => `<button type="button" role="tab" class="dt-tab${t.id === state.tab ? " active" : ""}" data-dt-tab="${t.id}" aria-selected="${t.id === state.tab}">${escapeHtml(t.label)}</button>`).join("");
      const tab = TABS.find((t) => t.id === state.tab);
      const variants = tab.datasets.length > 1
        ? `<div class="dt-variants" role="group" aria-label="Table">${tab.datasets.map((id) => `<button type="button" class="dt-variant${id === state.dataset ? " active" : ""}" data-dt-dataset="${id}" aria-pressed="${id === state.dataset}">${escapeHtml(DATASETS[id].label)}</button>`).join("")}</div>`
        : "";
      return `<article class="page data-tables" aria-label="Data tables">
        <div class="fact-kicker">Open data · interactive registries</div>
        <h1>Data Tables</h1>
        <p class="muted">Filter, sort and download the wiki's core registries. Every file is listed with its schema and freshness in the Open Data Catalog.</p>
        <div class="dt-tabs" role="tablist">${tabs}</div>
        ${variants}
        <div class="dt-body" id="dt-body"><div class="placeholder">loading table…</div></div>
      </article>`;
    }

    function renderBody(data) {
      const { ds, sorted, sort, summary } = currentView(data);
      const filterHtml = ds.filters.map((f) => {
        const opts = distinctValues(data.rows, f.key).map((v) => `<option value="${escapeHtml(v)}"${state.filters[f.key] === v ? " selected" : ""}>${escapeHtml(v)}</option>`).join("");
        return `<label class="dt-filter"><span>${escapeHtml(f.label)}</span><select data-dt-filter="${f.key}"><option value="">All</option>${opts}</select></label>`;
      }).join("");
      const totals = ds.sums.map((s) => {
        const t = summary.totals[s.key];
        return `<span><b>${t.total.toLocaleString("en-US", { maximumFractionDigits: 2 })}</b> ${escapeHtml(s.label)}</span>`;
      }).join("");
      const head = ds.columns.map((c) => {
        const active = sort.key === c.key;
        const arrow = active ? (sort.dir === "asc" ? " ▲" : " ▼") : "";
        return `<th scope="col" class="${c.numeric ? "num" : ""}" aria-sort="${active ? (sort.dir === "asc" ? "ascending" : "descending") : "none"}"><button type="button" data-dt-sort="${c.key}">${escapeHtml(c.label)}${arrow}</button></th>`;
      }).join("") + "<th scope=\"col\"><span class=\"sr-only\">Action</span></th>";
      const body = sorted.map((row, idx) => {
        const cells = ds.columns.map((c) => {
          const value = c.title ? escapeHtml(titleFromSlug(row[c.key], hooks)) : formatCell(row[c.key], c.numeric);
          return `<td class="${c.numeric ? "num" : ""}">${value}</td>`;
        }).join("");
        const action = ds.action(row);
        const btn = action ? `<button type="button" class="dt-row-action" data-dt-row="${idx}">${escapeHtml(action.label)} →</button>` : "";
        return `<tr>${cells}<td>${btn}</td></tr>`;
      }).join("");
      const companionTitle = titleFromSlug(ds.companion, hooks);
      return `<div class="dt-controls">
          <label class="dt-filter dt-search"><span>Search</span><input type="search" data-dt-query value="${escapeHtml(state.query)}" placeholder="Filter rows…" aria-label="Filter rows" /></label>
          ${filterHtml}
          <button type="button" class="dt-reset" data-dt-reset>Clear filters</button>
        </div>
        <div class="dt-summary" aria-live="polite"><span><b>${summary.count.toLocaleString("en-US")}</b> of ${data.rows.length.toLocaleString("en-US")} rows</span>${totals}
          <span class="dt-downloads"><button type="button" data-dt-download>Download filtered CSV</button> <a href="${escapeHtml(base + ds.file)}" download>Download full CSV</a></span>
        </div>
        <div class="dt-scroll"><table class="dt-table"><thead><tr>${head}</tr></thead><tbody>${body || `<tr><td colspan="${ds.columns.length + 1}" class="muted">No rows match these filters.</td></tr>`}</tbody></table></div>
        <p class="muted dt-source">${escapeHtml(ds.source)} About this dataset: <a href="?page=${encodeURIComponent(ds.companion)}" data-dt-page="${escapeHtml(ds.companion)}">${escapeHtml(companionTitle)}</a> · <a href="?page=data-open-data-catalog" data-dt-page="data-open-data-catalog">Open Data Catalog</a></p>`;
    }

    async function refresh() {
      if (!container) return;
      const bodyEl = container.querySelector("#dt-body");
      const datasetAtCall = state.dataset;
      try {
        const data = await load(datasetAtCall);
        if (datasetAtCall !== state.dataset || !container.querySelector("#dt-body")) return;
        container.querySelector("#dt-body").innerHTML = renderBody(data);
      } catch (err) {
        if (bodyEl) bodyEl.innerHTML = `<div class="placeholder">Could not load ${escapeHtml(DATASETS[datasetAtCall].file)}.</div>`;
      }
    }

    function selectDataset(datasetId) {
      state.dataset = datasetId;
      state.filters = {};
      state.query = "";
      state.sort = null;
      if (hooks.onDatasetChange) hooks.onDatasetChange(datasetId);
    }

    async function onClick(event) {
      const t = event.target.closest("[data-dt-tab],[data-dt-dataset],[data-dt-sort],[data-dt-reset],[data-dt-download],[data-dt-row],[data-dt-page]");
      if (!t || !container.contains(t)) return;
      if (t.dataset.dtTab) {
        state.tab = t.dataset.dtTab;
        selectDataset(TABS.find((x) => x.id === state.tab).datasets[0]);
        container.innerHTML = renderShell();
        return refresh();
      }
      if (t.dataset.dtDataset) {
        selectDataset(t.dataset.dtDataset);
        container.innerHTML = renderShell();
        return refresh();
      }
      if (t.dataset.dtSort) {
        const ds = DATASETS[state.dataset];
        const cur = state.sort || ds.defaultSort;
        const col = ds.columns.find((c) => c.key === t.dataset.dtSort);
        state.sort = cur.key === col.key
          ? { key: col.key, dir: cur.dir === "asc" ? "desc" : "asc" }
          : { key: col.key, dir: col.numeric ? "desc" : "asc" };
        return refresh();
      }
      if (t.hasAttribute("data-dt-reset")) {
        state.filters = {}; state.query = "";
        return refresh();
      }
      const data = await load(state.dataset);
      const { ds, sorted } = currentView(data);
      if (t.hasAttribute("data-dt-download")) {
        const blob = new Blob([toCSV(data.columns, sorted)], { type: "text/csv;charset=utf-8" });
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = ds.file.replace(/\.csv$/, "-filtered.csv");
        document.body.appendChild(a); a.click(); a.remove();
        setTimeout(() => URL.revokeObjectURL(url), 1000);
        return undefined;
      }
      if (t.dataset.dtPage) {
        event.preventDefault();
        if (hooks.openPage) hooks.openPage(t.dataset.dtPage);
        return undefined;
      }
      if (t.dataset.dtRow) {
        const action = ds.action(sorted[Number(t.dataset.dtRow)]);
        if (!action) return undefined;
        if (action.kind === "page" && hooks.openPage) hooks.openPage(action.slug);
        if (action.kind === "fact" && hooks.openFact) hooks.openFact(action.id);
      }
      return undefined;
    }

    function onInput(event) {
      const t = event.target;
      if (t.matches("[data-dt-filter]")) { state.filters[t.dataset.dtFilter] = t.value; refresh(); }
      else if (t.matches("[data-dt-query]")) {
        state.query = t.value;
        const pos = t.selectionStart;
        refresh().then(() => {
          const input = container && container.querySelector("[data-dt-query]");
          if (input) { input.focus(); try { input.setSelectionRange(pos, pos); } catch (e) { /* noop */ } }
        });
      }
    }

    return {
      state,
      load,
      /** Render the Tables view into `el` and fetch only the selected table. */
      open(el, opts = {}) {
        if (container !== el) {
          if (container) { container.removeEventListener("click", onClick); container.removeEventListener("change", onInput); container.removeEventListener("input", onInput); }
          container = el;
          container.addEventListener("click", onClick);
          container.addEventListener("change", onInput);
          container.addEventListener("input", onInput);
        }
        if (opts.dataset && DATASETS[opts.dataset]) {
          state.tab = DATASETS[opts.dataset].tab;
          selectDataset(opts.dataset);
        }
        container.innerHTML = renderShell();
        return refresh();
      },
      close() {
        if (!container) return;
        container.removeEventListener("click", onClick);
        container.removeEventListener("change", onInput);
        container.removeEventListener("input", onInput);
        container = null;
      },
    };
  }

  root.NepalDataExplorer = { DATASETS, TABS, parseCSV, filterRows, sortRows, summarize, toCSV, toNumber, createExplorer };
})(typeof window !== "undefined" ? window : globalThis);
