// Shared map plumbing across all design demos.
// Tiny on purpose: one map, one layer manager, one popup template.
// Wrapped in IIFE so re-evaluation (bfcache, hot navigation) does not throw on duplicate declarations.
(function () {
if (window.NepalExplorer && window.NepalExplorer._leafletInitLoaded) return;

const NEPAL_VIEW = { center: [28.2, 84.0], zoom: 7 };
const HYDROPOWER_FALLBACK_LAYERS = new Set([
  "hydropower_operating",
  "hydropower_construction",
  "hydropower_survey",
]);

// ---- Warm Technical / Living Atlas: style resolver ----

const ROLE_STYLES = {
  primary:    { visible: true, opacity: 1,    fillOpacity: 0.95, strokeOpacity: 1,    labelOpacity: 1,    zIndex: 500 },
  secondary:  { visible: true, opacity: 0.72, fillOpacity: 0.65, strokeOpacity: 0.75, labelOpacity: 0.65, zIndex: 400 },
  context:    { visible: true, opacity: 0.42, fillOpacity: 0.25, strokeOpacity: 0.45, labelOpacity: 0.4,  zIndex: 300 },
  annotation: { visible: true, opacity: 0.85, fillOpacity: 0.8,  strokeOpacity: 0.85, labelOpacity: 0.9,  zIndex: 600 },
  muted:      { visible: true, opacity: 0.22, fillOpacity: 0.14, strokeOpacity: 0.25, labelOpacity: 0,    zIndex: 200 },
  off:        { visible: false },
};

const BASEMAP_ADJUSTMENTS = {
  "Carto Positron": { badgeHalo: "none",   iconHalo: "subtle", lineContrastBoost: 0 },
  "Topographic":     { badgeHalo: "medium", iconHalo: "medium", lineContrastBoost: 0.15 },
  "Satellite":       { badgeHalo: "strong", iconHalo: "strong", lineContrastBoost: 0.25 },
};

function resolveLayerStyle(layerDef, preset, basemap, zoom, key) {
  const role = (layerDef.roleByPreset && layerDef.roleByPreset[preset]) || "off";

  // Zoom discipline: at national zoom, demote dense secondary layers
  let effectiveRole = role;
  if (zoom != null && zoom < 7) {
    // Dense survey/pipeline layers become OFF at national zoom (don't render at all)
    if (key === "hydropower_survey" && (role === "secondary" || role === "context")) {
      effectiveRole = "off";
    }
  }
  // Construction projects: keep OFF longer (2 extra zoom levels) so they only
  // appear when there's enough space and clearance.
  if (zoom != null && zoom < 9 && preset === "power_system" && key === "hydropower_construction" && role === "primary") {
    effectiveRole = "off";
  }
  // Regional zoom: construction is visible but secondary (not competing with operating)
  if (zoom != null && zoom >= 9 && zoom < 11 && preset === "power_system" && key === "hydropower_construction" && role === "primary") {
    effectiveRole = "secondary";
  }
  // Tributaries preset: operating plants follow same zoom discipline as construction in power
  // (hidden until zoom 9 so national view stays clean)
  if (zoom != null && zoom < 9 && preset === "tributaries" && key === "hydropower_operating") {
    effectiveRole = "off";
  }

  const roleStyle = ROLE_STYLES[effectiveRole] || ROLE_STYLES.off;
  const basemapStyle = BASEMAP_ADJUSTMENTS[basemap] || BASEMAP_ADJUSTMENTS["Carto Positron"];
  return { role: effectiveRole, roleStyle, basemapStyle };
}

function getZoomBehavior(zoom) {
  if (zoom < 7)  return "national";
  if (zoom < 10) return "regional";
  return "local";
}


// Called by L.geoJSON style option and pointToLayer. Returns a Leaflet
// style object. Role-aware adjustments are applied post-render by
// _applyRoleVisibility(); this function keeps the base style intact so
// the map doesn't throw when rendering lines/polygons/points.
function styleForFeature(baseStyle, layerDef, props) {
  return baseStyle;
}
// App-level cache buster. A single value derived from the page-load time
// means every JSON fetched during one session sees consistent data, but a
// reload after scripts/gen_wiki_stubs.py always busts the browser cache.
const _APP_CB = (() => {
  try {
    const m = document.querySelector('meta[name="np-build"]');
    if (m && m.content) return m.content;
  } catch (e) {}
  return String(Date.now());
})();

function bustify(path) {
  return path + (path.includes("?") ? "&" : "?") + "cb=" + _APP_CB;
}

async function loadJSON(path) {
  const r = await fetch(bustify(path));
  if (!r.ok) throw new Error(`fetch failed: ${path}`);
  return r.json();
}

// Three basemaps, identical to the ones in docs/maps/*.html.
function makeBaseLayers() {
  const positron = L.tileLayer(
    "https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png",
    {
      attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>',
      subdomains: "abcd",
      maxZoom: 20,
      detectRetina: true,
    }
  );
  const topo = L.tileLayer(
    "https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png",
    {
      attribution: "Map data: OpenStreetMap contributors, SRTM | Map style: OpenTopoMap",
      subdomains: "abc",
      maxZoom: 17,
    }
  );
  const sat = L.tileLayer(
    "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
    {
      attribution: "Tiles &copy; Esri",
      maxZoom: 18,
    }
  );
  return {
    "Carto Positron": positron,
    "Topographic": topo,
    "Satellite": sat,
  };
}

function makeMap(elId, opts = {}) {
  const map = L.map(elId, {
    center: opts.center || NEPAL_VIEW.center,
    zoom: opts.zoom || NEPAL_VIEW.zoom,
    zoomControl: false,
    // SVG, not canvas. With canvas every layer shares one hit-test surface and
    // priority becomes "last-added wins" — fragile across toggle paths. With
    // SVG we can additionally give polygons / lines / points their own panes
    // (below) so click priority is enforced by CSS z-index, not insertion order.
    preferCanvas: false,
  });

  // Dedicated panes per kind. CircleMarker (and all vector layers) default to
  // overlayPane (z-index 400), where polygons would sit at the same level as
  // points. By splitting them across panes with strictly increasing z-indices
  // (polygons 410 < lines 420 < points 430), the browser's native event
  // dispatch always picks the smallest, topmost element when they overlap —
  // the polygon under the click never steals the marker's event.
  map.createPane("np-polygons");  map.getPane("np-polygons").style.zIndex = 410;
  map.createPane("np-lines");     map.getPane("np-lines").style.zIndex     = 420;
  map.createPane("np-points");    map.getPane("np-points").style.zIndex    = 430;

  const baseLayers = makeBaseLayers();
  const defaultBase = opts.defaultBase || "Carto Positron";
  baseLayers[defaultBase].addTo(map);
  L.control.zoom({ position: "bottomright" }).addTo(map);
  L.control.scale({ imperial: false }).addTo(map);
  return { map, baseLayers };
}

function popupHTML(props, popupFields, opts = {}) {
  const title = props.label_title || props.name || props.project || props.short_label || props.label || props.display_name || props.id || "Feature";
  const rows = (popupFields || []).map((f) => {
    const field = typeof f === "string" ? f : f.field;
    const label = typeof f === "string" ? humanizeField(f) : (f.label || humanizeField(f.field));
    let v = props[field];
    if (v === undefined || v === null || v === "") return "";
    if (typeof f !== "string" && f.value_map && f.value_map[v] !== undefined) {
      v = f.value_map[v];
    }
    return `<div class="popup-row"><b>${label}:</b> ${v}</div>`;
  }).join("");
  let cta = "";
  if (opts.wikiSlug) {
    const isCurrent = opts.currentSlug && opts.currentSlug === opts.wikiSlug;
    // Always keep the CTA actionable. When the page is already open we style
    // it as a confirmation ("✓ Showing in reader") instead of a dead label
    // so the click→navigate flow doesn't read as "no page for this marker".
    if (isCurrent) {
      cta = `<a class="popup-cta popup-cta-current" href="javascript:void(0)"
               title="Reopen / scroll to top"
               onclick="window.openWikiPage && window.openWikiPage('${opts.wikiSlug}')">✓ Showing in reader</a>`;
    } else {
      cta = `<a class="popup-cta" href="javascript:void(0)" onclick="window.openWikiPage && window.openWikiPage('${opts.wikiSlug}')">Open explanation →</a>`;
    }
  } else if (opts.allowDraft) {
    cta = `<span class="popup-no-page" title="This feature is in the data layer but doesn't have a narrative wiki page yet.">Data-only · no wiki page</span>`;
  }
  return `<div class="popup-title">${title}</div>${rows}${cta}`;
}

function tooltipHTML(props, tooltipFields) {
  const title = props.label_title || props.name || props.label || props.display_name || props.project || props.id;
  if (!tooltipFields || !tooltipFields.length) {
    return title ? `<b>${escapeHtml(title)}</b>` : "";
  }
  const rows = tooltipFields
    .map((f) => {
      const field = typeof f === "string" ? f : f.field;
      const label = typeof f === "string" ? humanizeField(f) : (f.label || humanizeField(f.field));
      let v = props[field];
      if (v === undefined || v === null || v === "") return null;
      if (typeof f !== "string" && f.value_map && f.value_map[v] !== undefined) {
        v = f.value_map[v];
      }
      return `<tr><th>${escapeHtml(label)}</th><td>${escapeHtml(String(v))}</td></tr>`;
    })
    .filter(Boolean)
    .join("");
  if (!rows) return title ? `<b>${escapeHtml(title)}</b>` : "";
  return `<table class="np-tooltip">${rows}</table>`;
}

function escapeHtml(s) {
  return String(s).replace(/[<>&"']/g, (c) => ({ "<": "&lt;", ">": "&gt;", "&": "&amp;", '"': "&quot;", "'": "&#39;" }[c]));
}

// Substitute ${field} tokens with values from props. Empty/missing values
// collapse the surrounding " · " separators so leads stay tidy.
function renderTemplate(tpl, props) {
  let out = String(tpl).replace(/\$\{([\w.]+)\}/g, (_, k) => {
    const v = props[k];
    return (v === undefined || v === null || v === "") ? "\u0000" : String(v);
  });
  // Drop bullet-separated empty segments
  out = out
    .split(/\s*·\s*/)
    .filter((s) => s && !s.includes("\u0000"))
    .join(" · ");
  return out;
}

function humanizeField(f) {
  return String(f).replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase());
}

function slugifyWikiCandidate(name) {
  return String(name || "").toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-+|-+$/g, "");
}

// Reverse index: feature → wiki slug. Built once from bindings.
// A single feature can be referenced by many pages (e.g., Koshi system is the
// canonical entity page, but also appears in claim-sediment and glof-risk),
// so each key maps to a list of candidate {slug, type, primary} bindings.
function buildReverseIndex(bindings) {
  const idx = {};
  for (const [slug, page] of Object.entries(bindings.pages || {})) {
    const type = page.type || "concept";
    for (const f of page.features || []) {
      const entry = { slug, type, primary: !!f.primary };
      if (f.id) {
        const k = `${f.layer}:${f.id}`;
        (idx[k] = idx[k] || []).push(entry);
      }
      const m = f.match;
      if (m && (m.field === "project" || m.field === "name")) {
        // Two forms authored in bindings.json:
        //   { field, value_contains: "Kulekhani" }  → substring match
        //   { field, value: "Tanahu HEP" }          → exact (case-insensitive)
        // Both index under a single lookup bucket per layer, distinguished by
        // a prefix; lookupSlug iterates and checks the kind.
        if (m.value_contains) {
          const k = `__substr__${f.layer}:${m.field}:${m.value_contains.toLowerCase()}`;
          (idx[k] = idx[k] || []).push(entry);
        }
        if (m.value != null) {
          const k = `__exact__${f.layer}:${m.field}:${String(m.value).toLowerCase()}`;
          (idx[k] = idx[k] || []).push(entry);
        }
      }
    }
  }
  return idx;
}

// When multiple pages bind the same feature, we pick the most "canonical" one:
// an entity page (a page about the thing itself) wins over a concept/claim page
// that merely cites the feature as an example. `primary: true` always wins.
const _SLUG_TYPE_RANK = { entity: 0, "trade-route": 1, concept: 2, claim: 3 };
function _rankCandidate(c) {
  if (c.primary) return -1;
  return _SLUG_TYPE_RANK[c.type] ?? 99;
}

function lookupSlug(reverseIdx, layerKey, props, aliases, hydropowerSlugAliases, knownSlugs) {
  const id = props.id || props.corridor_id;
  const candidates = [];
  // Try the layer's own key plus any aliases it declares (e.g. the three
  // hydropower_* split layers all alias the historical "hydropower_points"
  // key that bindings.json was authored against).
  const keys = [layerKey, ...(aliases || [])];
  if (id) {
    for (const k of keys) {
      const direct = reverseIdx[`${k}:${id}`];
      if (direct) candidates.push(...direct);
    }
  }
  const propProject = (props.project || "").toLowerCase();
  const propName    = (props.name    || "").toLowerCase();
  for (const k of Object.keys(reverseIdx)) {
    if (k.startsWith("__substr__") || k.startsWith("__exact__")) {
      // key format: __kind__<layer>:<field>:<lowercased needle>
      const [prefix, rest] = [k.slice(0, k.indexOf("__", 2) + 2), k.slice(k.indexOf("__", 2) + 2)];
      const firstColon = rest.indexOf(":");
      if (firstColon < 0) continue;
      const lyr = rest.slice(0, firstColon);
      if (!keys.includes(lyr)) continue;
      const rem = rest.slice(firstColon + 1);
      const secondColon = rem.indexOf(":");
      if (secondColon < 0) continue;
      const field  = rem.slice(0, secondColon);
      const needle = rem.slice(secondColon + 1);
      const hay = field === "name" ? propName : propProject;
      const hit = prefix === "__exact__" ? hay === needle : hay.includes(needle);
      if (hit) candidates.push(...reverseIdx[k]);
    }
  }
  if (candidates.length) {
    candidates.sort((a, b) => _rankCandidate(a) - _rankCandidate(b));
    return candidates[0].slug;
  }

  // Final fallback: hydropower registry markers can resolve directly from the
  // project name when a page exists, even if bindings.json has no entry yet.
  if (!HYDROPOWER_FALLBACK_LAYERS.has(layerKey)) return null;
  const rawSlug = slugifyWikiCandidate(props.project || "");
  if (!rawSlug) return null;
  const slug = (hydropowerSlugAliases || {})[rawSlug] || rawSlug;
  if (!knownSlugs || !knownSlugs.has(slug)) return null;
  return slug;
}

// Filter a GeoJSON FeatureCollection in-memory so several manifest layers can
// share one source file. Spec: { field, equals } or { field, in: [...] }.
function applyLayerFilter(data, spec) {
  if (!spec || !spec.field) return data;
  if (!data || data.type !== "FeatureCollection") return data;
  const field = spec.field;
  const test = "equals" in spec
    ? (v) => v === spec.equals
    : Array.isArray(spec.in)
      ? (v) => spec.in.includes(v)
      : () => true;
  const filtered = data.features.filter((f) => test((f.properties || {})[field]));
  return Object.assign({}, data, { features: filtered });
}

// Build a (props) → radius function for circleMarker layers when the style
// declares radius_field. Uses sqrt scaling by default (good for capacity-
// like quantities where area should scale with the value).
function makeRadiusFn(style, data) {
  const field = style && style.radius_field;
  if (!field) return null;
  const min = style.radius_min != null ? style.radius_min : (style.radius || 3);
  const max = style.radius_max != null ? style.radius_max : (min + 8);
  const mode = style.radius_scale || "sqrt";
  // Compute domain max from the data so scaling is layer-relative.
  let domainMax = 0;
  const feats = (data && data.features) || [];
  for (const f of feats) {
    const v = Number((f.properties || {})[field]);
    if (Number.isFinite(v) && v > domainMax) domainMax = v;
  }
  if (domainMax <= 0) return () => min;
  const transform = mode === "linear" ? ((x) => x) : Math.sqrt;
  const tMax = transform(domainMax);
  return (props) => {
    const v = Number(props[field]);
    if (!Number.isFinite(v) || v <= 0) return min;
    const t = transform(v) / tMax;
    return min + t * (max - min);
  };
}

// Layer manager. Lazily loads + caches GeoJSON; keeps persistent L.layer
// references so add/remove can toggle map presence without recreating
// (works well with L.control.layers).
class LayerManager {
  constructor(map, manifest, reverseIdx, options = {}) {
    this.map = map;
    this.manifest = manifest;
    this.reverseIdx = reverseIdx || {};
    this.cache = {};        // key → geojson data
    this.layers = {};       // key → L.GeoJSON layer (persistent reference)
    this.featureLookup = {};
    this.options = options; // { onFeatureClick(slug, props), onLayerToggle(key, on) }

    // Belt-and-braces: any layer added by something other than this manager
    // (notably the L.control.layers checkboxes, which call layer.addTo(map)
    // directly) still triggers a z-order normalization. Without this, toggling
    // a polygon on after a point would put the polygon on top in the canvas
    // hit-test order and steal the point's clicks.
    map.on("overlayadd", () => this.normalizeZOrder());
    this._markerMode = "badges";
    this._preset = options.preset || "";
    this._basemap = options.basemap || "Carto Positron";
    this._activeSet = new Set();
    this._manualSet = new Set();

    // Zoom-aware simplification
    map.on("zoomend", () => {
      const zoom = map.getZoom();
      const behavior = getZoomBehavior(zoom);
      this._zoomBehavior = behavior;
      // Re-evaluate role visibility (layers may get hidden/shown at national zoom)
      this._applyRoleVisibility();
      // At national zoom: reduce marker radius for non-primary layers
      // At regional zoom: slightly reduce secondary layers so they don't compete with primary
      for (const [key, layer] of Object.entries(this.layers)) {
        if (!this._activeSet.has(key)) continue;
        const def = this.manifest.layers[key];
        if (!def) continue;
        const { role } = resolveLayerStyle(def, this._preset, this._basemap, zoom, key);
        if (def.kind !== "point") continue;
        let scale = 1;
        if (behavior === "national" && role !== "primary" && role !== "annotation") {
          scale = 0.55;
        } else if (behavior === "regional" && role === "secondary") {
          scale = 0.82;
        }
        if (scale === 1) continue;
        try {
          if (layer.eachLayer) {
            layer.eachLayer((m) => {
              if (typeof m.setRadius === "function") {
                const origR = m.options.radius || 8;
                m.setRadius(Math.max(origR * scale, 2.5));
              }
            });
          }
        } catch (e) {}
        // Gradual reveal: re-apply capacity filter on zoom change
        if (key === "hydropower_construction" && this._preset === "power_system" && !this._manualSet.has(key)) {
          this._applyConstructionFilter(layer, zoom);
        }
        // National zoom density guard: re-apply top-10 filter on zoom change
        if (key === "hydropower_operating" && this._preset === "power_system" && !this._manualSet.has(key)) {
          this._applyOperatingFilter(layer, zoom);
        }
      }
    });
  }

  async _data(key) {
    if (!this.cache[key]) {
      this.cache[key] = await loadJSON(this.manifest.layers[key].path);
    }
    return this.cache[key];
  }

  // Build the L.GeoJSON object once; do NOT add to map.
  async preload(key) {
    if (this.layers[key]) return this.layers[key];
    const def = this.manifest.layers[key];
    if (!def) { console.warn("unknown layer", key); return null; }
    const rawData = await this._data(key);
    // Optional filter — lets multiple manifest entries share one source file
    // (e.g. hydropower_operating / _construction / _survey all read the same
    // 572-feature GeoJSON and partition it by license_type).
    const data = applyLayerFilter(rawData, def.filter);
    const reverseIdx = this.reverseIdx;
    const onFeatClick = this.options.onFeatureClick;
    const baseStyle = def.style || {};
    const interactive = def.interactive !== false;
    const aliases = def.aliases || [];

    // Optional per-feature radius scaling for circleMarker layers.
    // style.radius_field=<numeric prop>, radius_min, radius_max, radius_scale=sqrt|linear
    const radiusFn = makeRadiusFn(baseStyle, data);

    const getCurrentSlug = this.options.getCurrentSlug || (() => null);
    // Route each kind to its own pane so click priority is enforced by CSS
    // z-index (polygons under, points over). See makeMap() for the panes.
    const KIND_PANE = { polygon: "np-polygons", line: "np-lines", point: "np-points" };
    const pane = KIND_PANE[def.kind];
    const styleWithPane = pane ? Object.assign({}, baseStyle, { pane }) : baseStyle;
    // Coverage stats (how many features in this layer have a bound wiki slug).
    // We compute the slug up-front so pointToLayer can give orphan markers a
    // distinct className ("np-marker-orphan") that CSS uses for both the
    // ghosted look and the "only bound" filter.
    let coverageBound = 0;
    let coverageTotal = 0;
    const pagesWithImages = this.options.pagesWithImages || new Set();
    const stubSlugs       = this.options.stubSlugs       || new Set();
    const hydropowerSlugAliases = this.options.hydropowerSlugAliases || {};
    const knownSlugs = this.options.knownSlugs || new Set();
    const slugFor = (feat) => {
      const props = feat.properties || {};
      return interactive ? lookupSlug(reverseIdx, key, props, aliases, hydropowerSlugAliases, knownSlugs) : null;
    };
    const layer = L.geoJSON(data, {
      style: (feat) => styleForFeature(styleWithPane, def, (feat && feat.properties) || {}),
      interactive: interactive,
      pane: pane,
      pointToLayer: (feat, latlng) => {
        if (!latlng || !Number.isFinite(latlng.lat) || !Number.isFinite(latlng.lng)) {
          return L.layerGroup();
        }
        const slug = slugFor(feat);
        coverageTotal++;
        if (slug) coverageBound++;
        const hasImages = slug && pagesWithImages.has(slug);
        const isStub    = slug && stubSlugs.has(slug);
        // Tier classes drive both visual differentiation AND the "narrated /
        // wiki / all" filter. Only apply them to layers that opt in via
        // `tiered: true` in the manifest — i.e., the raw registry layers.
        // Curated highlight layers (Top-10, Priority watchlist, Storage
        // shortlist, ...) get a neutral class so the tier filter never hides
        // them; they're hand-picked and the point of surfacing them as
        // separate layers is that they must always be visible.
        const classes = ["np-marker"];
        if (def.tiered) {
          if (!slug)         classes.push("np-marker-orphan");
          else if (isStub)   classes.push("np-marker-stub");
          else               classes.push("np-marker-narrated");
          if (hasImages)     classes.push("np-marker-hasimg");
        } else {
          classes.push("np-marker-curated");
          if (hasImages)     classes.push("np-marker-hasimg");
        }
        const opts = Object.assign({}, styleForFeature(styleWithPane, def, feat.properties || {}), { className: classes.join(" ") });
        const r = radiusFn ? radiusFn(feat.properties || {}) : (opts.radius || 8);
        // Look up the icon key from layer panel sections (symbol field)
        const iconKey = (() => {
          try {
            const secs = window.NepalExplorer && window.NepalExplorer.LAYER_PANEL_SECTIONS;
            if (!secs) return "";
            for (const s of secs) {
              if (s.isGroup) {
                for (const sub of s.sections || []) {
                  for (const row of sub.rows || []) {
                    if (row.key === key && row.symbol) return row.symbol;
                  }
                }
              } else {
                for (const row of s.rows || []) {
                  if (row.key === key && row.symbol) return row.symbol;
                }
              }
            }
          } catch (e) {}
          return "";
        })();
        // Badge mode: colored circle + white SVG icon
        const badgeR = Math.max(r, 8);
        const borderColor = opts.color || "#666";
        const fillColor = opts.fillColor || opts.color || "#999";
        const svgSize = Math.max(Math.round(badgeR * 1.2), 10);  // icon ≈ 60% of badge diameter per brief §5.3
        const iconBody = this._svgIconHtml(iconKey);
        const basemapClass = (this._basemap === "Topographic") ? "np-badge-terrain" : (this._basemap === "Satellite") ? "np-badge-satellite" : "np-badge-light";
        const divHtml = `<div class="np-marker-badge ${basemapClass}" style="width:${badgeR*2}px;height:${badgeR*2}px;background:${fillColor};border-color:${borderColor};"><svg viewBox="0 0 24 24" width="${svgSize}" height="${svgSize}" fill="none" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">${iconBody}</svg></div>`;
        const divIcon = L.divIcon({
          html: divHtml,
          className: classes.join(" ") + " np-marker-badge-wrap",
          iconSize: [badgeR*2, badgeR*2],
          iconAnchor: [badgeR, badgeR],
          popupAnchor: [0, -badgeR],
        });
        return L.marker(latlng, { icon: divIcon, pane: opts.pane, interactive: interactive });
      },
      onEachFeature: (feat, lyr) => {
        const props = feat.properties || {};
        this.featureLookup[this._featureKey(key, feat)] = lyr;
        if (!interactive) return;
        const slug = slugFor(feat);
        if (def.kind !== "point") {
          // Non-point layers don't hit pointToLayer, so tally here.
          coverageTotal++;
          if (slug) coverageBound++;
        }
        // Bind as a function so the CTA reflects the *current* page each time
        // the popup opens (lets us mute the button when its target is already open).
        lyr.bindPopup(
          () => popupHTML(props, def.popup_fields, {
            wikiSlug: slug,
            allowDraft: def.allow_draft,
            currentSlug: getCurrentSlug(),
          }),
          { maxWidth: 320 }
        );
        if (def.tooltip_fields !== false) {
          const tip = tooltipHTML(props, def.tooltip_fields);
          if (tip) {
            lyr.bindTooltip(tip, {
              direction: def.kind === "polygon" ? "auto" : "top",
              sticky: def.kind === "line",
              offset: [0, def.kind === "polygon" ? 0 : -4],
              className: "np-leaflet-tooltip",
            });
          }
        }
        if (onFeatClick) {
          lyr.on("click", (e) => {
            onFeatClick({ key, props, slug, layer: lyr, latlng: e.latlng });
          });
        }
      },
    });
    layer._npCoverage = { bound: coverageBound, total: coverageTotal };
    // Gradual reveal: compute 75th-percentile capacity for construction layer
    // so only the largest projects show at the zoom threshold where the layer
    // first becomes visible (zoom 9–10); all appear at zoom 11+.
    if (key === "hydropower_construction" && data.features && data.features.length) {
      const caps = data.features
        .map((f) => Number(f.properties && f.properties.capacity_mw) || 0)
        .sort((a, b) => a - b);
      const idx = Math.floor(caps.length * 0.75);
      layer._topCapacityThreshold = caps[idx] || 0;
    }
    // National zoom density guard: compute the 10th-largest capacity for
    // operating plants so only the biggest 10 show at zoom <= 6 in the power preset.
    if (key === "hydropower_operating" && data.features && data.features.length) {
      const caps = data.features
        .map((f) => Number(f.properties && f.properties.capacity_mw) || 0)
        .filter((c) => c > 0)
        .sort((a, b) => b - a);
      // caps is descending; index 9 = 10th largest (or last element if fewer than 10)
      const idx = Math.min(9, caps.length - 1);
      layer._top10Threshold = caps[idx] || 0;
    }
    this.layers[key] = layer;
    return layer;
  }

  coverageFor(key) {
    const l = this.layers[key];
    return l && l._npCoverage;
  }

  _applyConstructionFilter(layer, zoom) {
    // Gradual reveal for construction projects in power preset:
    // at zoom 9–10 only the top-quartile by capacity are shown;
    // zoom 11+ shows all.
    if (!layer || !layer.eachLayer) return;
    const threshold = layer._topCapacityThreshold;
    if (threshold == null) return;
    const showAll = zoom >= 11;
    layer.eachLayer((m) => {
      const cap = m.feature && m.feature.properties && m.feature.properties.capacity_mw;
      const show = showAll || (cap != null && cap >= threshold);
      const opacity = show ? 1 : 0;
      try {
        if (typeof m.setOpacity === "function") {
          m.setOpacity(opacity);
        } else if (m.getElement) {
          m.getElement().style.opacity = String(opacity);
        }
      } catch (e) {}
    });
  }

  _applyOperatingFilter(layer, zoom) {
    // National zoom density guard for operating plants in power preset:
    // at zoom <= 6 only the top-10 largest plants are shown;
    // zoom 7+ shows all 81.
    if (!layer || !layer.eachLayer) return;
    const threshold = layer._top10Threshold;
    if (threshold == null) return;
    const showAll = zoom >= 7;
    layer.eachLayer((m) => {
      const cap = m.feature && m.feature.properties && m.feature.properties.capacity_mw;
      const show = showAll || (cap != null && cap >= threshold);
      const opacity = show ? 1 : 0;
      try {
        if (typeof m.setOpacity === "function") {
          m.setOpacity(opacity);
        } else if (m.getElement) {
          m.getElement().style.opacity = String(opacity);
        }
      } catch (e) {}
    });
  }

  _resetPointOpacity(layer) {
    if (!layer || !layer.eachLayer) return;
    layer.eachLayer((m) => {
      try {
        if (typeof m.setOpacity === "function") {
          m.setOpacity(1);
        } else if (m.getElement) {
          m.getElement().style.opacity = "1";
        }
      } catch (e) {}
    });
  }

  _svgIconHtml(iconKey) {
    if (!this._iconsCache) this._iconsCache = {};
    if (this._iconsCache[iconKey]) return this._iconsCache[iconKey];
    // Warm Technical / Living Atlas — point-layer icon family (Phase 3)
    // All: 24×24 viewBox, single-stroke, fill="none", round caps+joins.
    const byKey = {
      live:      `<path d="M12.5 2.5 6 10h4L7 20l6.5-9.5h-3.5L12.5 2.5z"/><path d="M4 21c2.5-1 4.5 1 6.5 0s4 1 6.5 0"/>`,
      build:     `<path d="M12 20V5"/><path d="M6 6h12"/><path d="M18 6V3.5"/>`,
      pipeline:  `<path d="M5.5 3.5h8l5 5V20.5H5.5z"/><path d="M13.5 3.5v5h5"/><path d="M9 12.5l2.5-1.5 2.5 1.5"/><path d="M9 15.5c2-.5 3.5.8 5 0"/>`,
      watch:     `<path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="2.8"/>`,
      storage:   `<path d="M4 6.5h16v3H4z"/><path d="M7 9.5l5 8 5-8z"/>`,
      big:       `<path d="M12 2.5l2.8 5.6 6.2.8-4.5 4.3 1 6.3-5.5-2.8-5.5 2.8 1-6.3-4.5-4.3 6.2-.8z"/><circle cx="12" cy="12" r="1.2"/>`,
      solar:     `<path d="M6 5h10v8.5H6z"/><path d="M8 7.5h6M8 10h6"/><circle cx="18.5" cy="6" r="2.2"/>`,
      floating:  `<path d="M7 4.5h11v7H7z"/><path d="M8.5 6.5h8M8.5 8.5h8"/><path d="M4 14c2.5-1.5 4 .8 6 0s4 .8 6 0 4 .8 6 0"/><path d="M4 17c2.5-1.5 4 .8 6 0s4 .8 6 0 4 .8 6 0"/>`,
      gateway:   `<circle cx="4" cy="12" r="2.2"/><path d="M6.2 12h5"/><path d="M11.2 10l3 2-3 2"/><path d="M14.2 12h4"/><circle cx="20" cy="12" r="2.2"/>`,
      substation:`<path d="M12 2.5l6.5 6.5-6.5 6.5-6.5-6.5z"/><path d="M9 9h6"/><path d="M12 5.5v7"/><path d="M12 13v3"/>`,
      impact:    `<circle cx="12" cy="12" r="7"/><circle cx="12" cy="12" r="4"/>`,
      source:    `<path d="M12 2.5l5.5 4-5.5 4-5.5-4z"/><path d="M12 6.5v4"/><circle cx="12" cy="11.5" r="1.5"/>`,
      season:    `<circle cx="12" cy="6" r="2.8"/><path d="M12 2v1.2"/><path d="M6 13.5c3-1.5 4 1 5 0s4 1 5 0"/><path d="M7 17c2.5-1.5 3.5 1 5 0s3.5 1 5 0"/>`,
    };
    const body = byKey[iconKey] || "";
    this._iconsCache[iconKey] = body;
    return body;
  }

  setMarkerMode(mode) {
    this._markerMode = mode;
  }

  setPreset(preset) {
    if (this._preset === preset) return;
    this._preset = preset;
    this._applyRoleVisibility();
  }

  setBasemap(basemap) {
    if (this._basemap === basemap) return;
    this._basemap = basemap;
    this._applyBasemapToMarkers();
  }

  _applyRoleVisibility() {
    // Update layer visibility/opacity based on role in current preset + zoom + basemap.
    // Iterate over the user-selected set so layers removed for zoom discipline
    // are still re-evaluated when zoom changes.
    for (const key of this._activeSet) {
      const layer = this.layers[key];
      if (!layer) continue;
      const def = this.manifest.layers[key];
      if (!def) continue;
      let { role, roleStyle } = resolveLayerStyle(def, this._preset, this._basemap, this.map.getZoom(), key);
      if (!roleStyle.visible && this._manualSet.has(key)) {
        role = "primary";
        roleStyle = ROLE_STYLES.primary;
      }
      if (!roleStyle.visible) {
        try { this.map.removeLayer(layer); } catch (e) {}
        continue;
      }
      // Re-add if removed
      if (!this.map.hasLayer(layer)) {
        try { layer.addTo(this.map); } catch (e) {}
      }
      if (def.kind === "point" && this._manualSet.has(key)) {
        this._resetPointOpacity(layer);
      }
      // Apply opacity to line/polygon layers (points handled at marker level)
      if (def.kind !== "point") {
        try {
          const orig = def.style || {};
          const isPolygon = def.kind === "polygon";
          // Geometry-aware: polygons get softer fill so they don't dominate
          // Light/terrain: moderate softness; Satellite: even softer (dark bg)
          const isSat = this._basemap === "Satellite";
          const fillMult = isPolygon ? (isSat ? 0.22 : 0.32) : 1;
          const strokeMult = isPolygon ? (isSat ? 0.42 : 0.55) : 1;
          layer.setStyle({
            opacity: (orig.opacity || 1) * roleStyle.opacity * strokeMult,
            fillOpacity: (orig.fillOpacity != null ? orig.fillOpacity : 0.2) * roleStyle.fillOpacity * fillMult,
          });
        } catch (e) {}
      }
      // Adjust zIndex
      try {
        const pane = layer.options && layer.options.pane;
        if (pane && layer.setZIndex) {
          layer.setZIndex(roleStyle.zIndex);
        }
      } catch (e) {}
      // Gradual reveal: construction projects show top-quartile only at zoom 9–10
      if (key === "hydropower_construction" && this._preset === "power_system" && def.kind === "point" && !this._manualSet.has(key)) {
        this._applyConstructionFilter(layer, this.map.getZoom());
      }
      // National zoom density guard: operating plants show top-10 only at zoom <= 6
      if (key === "hydropower_operating" && this._preset === "power_system" && def.kind === "point" && !this._manualSet.has(key)) {
        this._applyOperatingFilter(layer, this.map.getZoom());
      }
    }
    this.normalizeZOrder();
  }

  _applyBasemapToMarkers() {
    // Update data-basemap attribute on map container so CSS can scope
    const container = this.map.getContainer();
    if (!container) return;
    container.setAttribute("data-basemap", this._basemap
      .replace("Carto Positron", "light")
      .replace("Topographic", "terrain")
      .replace("Satellite", "satellite"));
  }

  async rebuildPointLayers() {
    const active = this.activeKeys();
    for (const key of active) {
      const def = this.manifest.layers[key];
      if (!def || def.kind !== "point") continue;
      if (this.map.hasLayer(this.layers[key])) {
        this.map.removeLayer(this.layers[key]);
      }
      delete this.layers[key];
    }
    for (const key of active) {
      const def = this.manifest.layers[key];
      if (!def || def.kind !== "point") continue;
      await this.add(key);
    }
    this.normalizeZOrder();
  }

  _featureKey(key, feat) {
    const p = feat.properties || {};
    return `${key}:${p.id || p.corridor_id || p.segment_id || p.project || p.name}`;
  }

  async add(key, opts = {}) {
    const layer = await this.preload(key);
    if (opts.manual) this._manualSet.add(key);
    this._activeSet.add(key);
    if (layer && !this.map.hasLayer(layer)) {
      layer.addTo(this.map);
      if (this.options.onLayerToggle) this.options.onLayerToggle(key, true);
    }
    this._applyRoleVisibility();
    this.normalizeZOrder();
    return layer;
  }

  remove(key) {
    this._manualSet.delete(key);
    const layer = this.layers[key];
    if (layer && this.map.hasLayer(layer)) {
      this.map.removeLayer(layer);
      if (this.options.onLayerToggle) this.options.onLayerToggle(key, false);
    }
    this._activeSet.delete(key);
  }

  has(key) {
    const layer = this.layers[key];
    return !!(layer && this.map.hasLayer(layer));
  }

  isManual(key) {
    return this._manualSet.has(key);
  }

  activeKeys() {
    // Return user-selected / preset keys, regardless of current zoom visibility
    return [...this._activeSet];
  }

  async setActive(keys) {
    this._manualSet.clear();
    // Remove layers that are no longer in the desired set
    this._activeSet = new Set(keys);
    for (const k of Object.keys(this.layers)) {
      if (!this._activeSet.has(k)) this.remove(k);
    }
    // Preload / add all desired layers so they're available for zoom toggling
    for (const k of keys) {
      await this.add(k);
    }
    this._applyRoleVisibility();
    this.normalizeZOrder();
  }

  // With preferCanvas:true every layer shares a single canvas, and the canvas
  // hit-test picks the LAST-added layer at a point. That breaks click priority
  // when a basin polygon happens to be added after a hydropower point — the
  // polygon eats clicks meant for the marker. Re-stack on every change so
  // points always sit on top, then lines, then polygons.
  normalizeZOrder() {
    const KIND_RANK = { polygon: 0, line: 1, point: 2 };
    const sorted = Object.keys(this.layers)
      .filter((k) => this.has(k))
      .sort((a, b) => {
        const ka = KIND_RANK[(this.manifest.layers[a] || {}).kind] ?? 0;
        const kb = KIND_RANK[(this.manifest.layers[b] || {}).kind] ?? 0;
        return ka - kb;
      });
    for (const k of sorted) {
      const lyr = this.layers[k];
      if (lyr && typeof lyr.bringToFront === "function") {
        try { lyr.bringToFront(); } catch (e) {}
      }
    }
  }

  // Expand a binding's layer key into the set of actual manifest keys to
  // search. A binding may reference an alias (e.g. "hydropower_points"); any
  // manifest layer whose `aliases` includes that alias also gets searched.
  _resolveLayerKeys(bindingLayer) {
    const out = [];
    if (this.layers[bindingLayer]) out.push(bindingLayer);
    for (const k of Object.keys(this.manifest.layers)) {
      if (k === bindingLayer) continue;
      const aliases = (this.manifest.layers[k] || {}).aliases || [];
      if (aliases.includes(bindingLayer) && this.layers[k]) out.push(k);
    }
    return out;
  }

  findFeaturesForSlug(slug, bindings) {
    const page = (bindings.pages || {})[slug];
    if (!page) return [];
    const out = [];
    for (const f of page.features || []) {
      const keys = this._resolveLayerKeys(f.layer);
      const primary = !!f.primary;
      for (const key of keys) {
        const lyr = this.layers[key];
        if (!lyr) continue;
        lyr.eachLayer((sub) => {
          const p = sub.feature.properties || {};
          let hit = false;
          if (f.id && (p.id === f.id || p.corridor_id === f.id || p.segment_id === f.id)) hit = true;
          else if (f.all) hit = true;
          else if (f.match && f.match.field) {
            const v = (p[f.match.field] || "").toString().toLowerCase();
            if (f.match.value != null && v === String(f.match.value).toLowerCase()) hit = true;
            if (f.match.value_contains && v.includes(f.match.value_contains.toLowerCase())) hit = true;
          }
          if (hit) out.push({ key, layer: sub, props: p, primary });
        });
      }
    }
    return out;
  }

  findFeatureByRef(ref) {
    if (!ref || !ref.layer) return null;
    const keys = this._resolveLayerKeys(ref.layer);
    for (const key of keys) {
      const lyr = this.layers[key];
      if (!lyr) continue;
      let found = null;
      lyr.eachLayer((sub) => {
        if (found) return;
        const p = sub.feature && sub.feature.properties ? sub.feature.properties : {};
        if (ref.id && (p.id === ref.id || p.corridor_id === ref.id || p.segment_id === ref.id || p.project === ref.id || p.name === ref.id || p.label_title === ref.id)) {
          found = { key, layer: sub, props: p, primary: true };
          return;
        }
        if (ref.match_field && ref.match_value != null) {
          const value = String(p[ref.match_field] || "").toLowerCase();
          if (value === String(ref.match_value).toLowerCase()) found = { key, layer: sub, props: p, primary: true };
        }
      });
      if (found) return found;
    }
    return null;
  }

  // Choose the best feature to flash a card on. Returns null when the hit is
  // too broad to warrant a card (e.g., a basin polygon, or 8 transmission segments).
  pickCardFeature(features) {
    if (!features.length) return null;

    // 1) explicit primary wins — the binding author told us which one
    const explicit = features.find((f) => f.primary);
    if (explicit) return explicit;

    // 2) if any feature is a region-scale polygon/multi-segment line, we
    //    default to broad behavior. The user is looking at "the area" not "the dot".
    const hasRegional = features.some((f) => {
      const L_ = f.layer;
      // No getLatLng → polygon or polyline. Test bounds size.
      if (typeof L_.getLatLng === "function") return false;
      if (typeof L_.getBounds !== "function") return false;
      const b = L_.getBounds();
      if (!b.isValid()) return false;
      // ~50 km diagonal threshold for "regional"
      const km = b.getNorthWest().distanceTo(b.getSouthEast()) / 1000;
      return km > 50;
    });
    if (hasRegional) return null;

    // 3) exactly 1 feature → direct hit
    if (features.length === 1) return features[0];

    // 4) all features within ~150 m of each other → same place, pick the
    //    point with the richest manifest card_fields
    const points = features.filter((f) => typeof f.layer.getLatLng === "function");
    if (points.length >= 1) {
      const c = points[0].layer.getLatLng();
      const allClose = points.every((f) => f.layer.getLatLng().distanceTo(c) < 150);
      if (allClose) {
        const ranked = points.slice().sort((a, b) => {
          const ca = (this.manifest.layers[a.key] || {}).card_fields;
          const cb = (this.manifest.layers[b.key] || {}).card_fields;
          const sa = ca ? (Array.isArray(ca.body) ? ca.body.length : 0) + 1 : 0;
          const sb = cb ? (Array.isArray(cb.body) ? cb.body.length : 0) + 1 : 0;
          return sb - sa;
        });
        return ranked[0];
      }
    }

    // 5) otherwise: too broad — caller should fall back to bounds + halo only
    return null;
  }

  // Resolve a feature's properties into a {title, lead, body, pageHref} card spec
  // using the layer's `card_fields` config from the manifest.
  buildCardSpec(featureRef, opts = {}) {
    if (!featureRef) return null;
    const def = this.manifest.layers[featureRef.key] || {};
    const cf = def.card_fields;
    const p = featureRef.props || {};

    const title = cf && cf.title
      ? p[cf.title]
      : (p.label_title || p.name || p.project || p.label || def.label || "Feature");

    let lead = "";
    if (cf && cf.lead_field) lead = p[cf.lead_field] || "";
    else if (cf && cf.lead_template) lead = renderTemplate(cf.lead_template, p);

    let body = [];
    if (cf && Array.isArray(cf.body)) {
      body = cf.body
        .map((row) => {
          const v = p[row.field];
          if (v === undefined || v === null || v === "") return null;
          const value = String(v) + (row.suffix || "");
          return { label: row.label, value };
        })
        .filter(Boolean);
    } else if (Array.isArray(def.tooltip_fields)) {
      body = def.tooltip_fields
        .map((field) => {
          const v = p[field];
          if (v === undefined || v === null || v === "") return null;
          return { label: humanizeField(field), value: String(v) };
        })
        .filter(Boolean);
    }

    return { title: String(title || "Feature"), lead: String(lead || ""), body, pageHref: opts.pageHref, linkLabel: opts.linkLabel };
  }

  flyToFeatures(features, opts = {}) {
    if (!features.length) return;
    const group = L.featureGroup(features.map((x) => x.layer));
    const b = group.getBounds();
    if (b.isValid()) {
      this.map.flyToBounds(b, { padding: [60, 60], duration: opts.duration || 0.8, maxZoom: opts.maxZoom || 11 });
    }
  }

  highlight(features, opts = {}) {
    const revertAfterMs = opts.revertAfterMs || 4000;
    features.forEach(({ layer }) => {
      try {
        if (layer.bringToFront) layer.bringToFront();

        // Branch: circleMarker (point) vs path (line/polygon)
        if (typeof layer.getRadius === "function") {
          // Point: pulse the radius + add a temporary halo ring
          this._pulsePoint(layer, revertAfterMs);
        } else if (typeof layer.setStyle === "function") {
          const orig = { ...layer.options };
          layer.setStyle({
            color: "#1d4ed8",
            weight: Math.max(4, (orig.weight || 2) + 2),
            opacity: 0.95,
            dashArray: null,
          });
          setTimeout(() => { try { layer.setStyle(orig); } catch (e) {} }, revertAfterMs);
        }
      } catch (e) { /* swallow — best-effort visual */ }
    });
  }

  // For circleMarker: scale radius up and back down, plus a fading halo ring.
  _pulsePoint(marker, revertAfterMs) {
    const origR = marker.getRadius();
    const peakR = Math.max(origR * 2.2, origR + 6);
    const latlng = marker.getLatLng();
    const halo = L.circleMarker(latlng, {
      radius: peakR + 4,
      color: "#1d4ed8",
      weight: 2.5,
      opacity: 0.85,
      fillColor: "#3b82f6",
      fillOpacity: 0.25,
      interactive: false,
      pane: marker.options.pane,
    }).addTo(this.map);

    // 3 quick pulses — radius animation via stepped setStyle/setRadius
    const start = performance.now();
    const dur = Math.min(revertAfterMs, 1500);
    const tick = (now) => {
      const t = (now - start) / dur;
      if (t >= 1) {
        try { marker.setRadius(origR); } catch (e) {}
        try { halo.setStyle({ opacity: 0, fillOpacity: 0 }); } catch (e) {}
        setTimeout(() => { try { this.map.removeLayer(halo); } catch (e) {} }, 200);
        return;
      }
      // 3 pulses: |sin(3πt)| envelope, decaying
      const env = Math.abs(Math.sin(3 * Math.PI * t)) * (1 - t * 0.6);
      try { marker.setRadius(origR + (peakR - origR) * env); } catch (e) {}
      try {
        halo.setStyle({
          opacity: 0.85 * (1 - t),
          fillOpacity: 0.25 * (1 - t),
        });
        halo.setRadius(peakR + 4 + 12 * t);
      } catch (e) {}
      requestAnimationFrame(tick);
    };
    requestAnimationFrame(tick);
  }

  // Open a styled "card" popup on a single feature for direct hits.
  // cardSpec: { title, lead?, body? (array of {label, value}), pageHref? }
  // Auto-dismisses after opts.dismissAfterMs unless the cursor is hovering it.
  flashCard(featureRef, cardSpec, opts = {}) {
    if (!featureRef || !featureRef.layer) return null;
    const layer = featureRef.layer;

    const titleHtml = `<div class="np-card-title">${escapeHtml(cardSpec.title || "")}</div>`;
    const leadHtml = cardSpec.lead ? `<div class="np-card-lead">${escapeHtml(cardSpec.lead)}</div>` : "";
    let bodyHtml = "";
    if (Array.isArray(cardSpec.body) && cardSpec.body.length) {
      bodyHtml = `<dl class="np-card-body">` + cardSpec.body
        .map((row) => `<dt>${escapeHtml(row.label)}</dt><dd>${escapeHtml(row.value)}</dd>`)
        .join("") + `</dl>`;
    }
    const footerHtml = cardSpec.pageHref
      ? `<div class="np-card-footer"><a class="np-card-link" href="${cardSpec.pageHref}">${escapeHtml(cardSpec.linkLabel || "Open page →")}</a></div>`
      : "";
    const html = `<div class="np-card">${titleHtml}${leadHtml}${bodyHtml}${footerHtml}</div>`;

    if (!layer) return null;

    // Anchor: lat/lng of the marker, or feature centroid for non-point
    let latlng;
    if (typeof layer.getLatLng === "function") latlng = layer.getLatLng();
    else if (typeof layer.getBounds === "function") latlng = layer.getBounds().getCenter();
    if (!latlng) return null;

    const popup = L.popup({
      className: "np-card-popup",
      maxWidth: 280,
      minWidth: 220,
      autoPan: true,
      autoPanPadding: [40, 60],
      closeButton: true,
      offset: typeof layer.getRadius === "function" ? [0, -(layer.getRadius() + 4)] : [0, -8],
    })
      .setLatLng(latlng)
      .setContent(html)
      .openOn(this.map);

    // The card is a richer version of the layer's hover tooltip — they show
    // overlapping info and stack visually. Leaflet only auto-suppresses a
    // layer's bound tooltip when its OWN bound popup opens, but `flashCard`
    // uses a free-floating popup, so we have to silence the tooltip ourselves
    // and restore it once the card closes.
    let tipContent = null, tipOpts = null;
    const layerTip = (typeof layer.getTooltip === "function") ? layer.getTooltip() : null;
    if (layerTip) {
      tipContent = (typeof layerTip.getContent === "function") ? layerTip.getContent() : layerTip._content;
      tipOpts = layerTip.options ? Object.assign({}, layerTip.options) : undefined;
      try { layer.unbindTooltip(); } catch (e) {}
    }
    const restoreTooltip = () => {
      if (tipContent != null) {
        try { layer.bindTooltip(tipContent, tipOpts); } catch (e) {}
        tipContent = null;
      }
    };
    popup.on("remove", restoreTooltip);

    // Auto-dismiss with hover-to-pin behavior
    const dismissAfterMs = opts.dismissAfterMs || 6500;
    let timer = setTimeout(() => { try { this.map.closePopup(popup); } catch (e) {} }, dismissAfterMs);
    setTimeout(() => {
      const el = popup.getElement && popup.getElement();
      if (!el) return;
      el.addEventListener("mouseenter", () => { if (timer) { clearTimeout(timer); timer = null; } });
      el.addEventListener("mouseleave", () => {
        if (!timer) {
          timer = setTimeout(() => { try { this.map.closePopup(popup); } catch (e) {} }, 2500);
        }
      });
    }, 0);
    return popup;
  }
}

// Build a Labels overlay from one or more annotation specs.
// Each spec: { layer, field, tier, placement?, format?, dedupe? }
//   placement = "label_xy" (use label_lat/lon, fallback centroid)  [default]
//             | "midpoint" (walk polyline, place at half-arclength point) — best for long lines
//             | "centroid" (force centroid)
//   format(props) → custom label text override
//   dedupe = true → only one label per unique text (useful for multi-segment corridors)
function buildLabelsOverlay(lm, manifest, specs) {
  const group = L.layerGroup();
  group._npLabels = { specs, lm, built: false, manifest };
  group._npRebuild = async function () {
    group.clearLayers();
    for (const spec of specs) {
      let data;
      try {
        data = await lm._data(spec.layer);
      } catch (e) { continue; }
      const feats = (data.type === "FeatureCollection") ? data.features : [data];
      const seen = new Set();
      for (const f of feats) {
        if (!f || !f.properties) continue;
        const p = f.properties;
        let text;
        if (typeof spec.format === "function") {
          text = spec.format(p);
        } else {
          text = p[spec.field] || p.name || p.label_title;
        }
        if (!text) continue;
        if (spec.dedupe) {
          if (seen.has(text)) continue;
          seen.add(text);
        }
        let lat, lon;
        const placement = spec.placement || "label_xy";
        if (placement === "label_xy") {
          lat = p.label_lat; lon = p.label_lon;
          if ((!lat || !lon) && f.geometry) {
            const c = approxCentroid(f.geometry);
            if (c) { lat = c[0]; lon = c[1]; }
          }
        } else if (placement === "midpoint" && f.geometry) {
          const c = lineMidpoint(f.geometry) || approxCentroid(f.geometry);
          if (c) { lat = c[0]; lon = c[1]; }
        } else if (f.geometry) {
          const c = approxCentroid(f.geometry);
          if (c) { lat = c[0]; lon = c[1]; }
        }
        lat = Number(lat);
        lon = Number(lon);
        if (!Number.isFinite(lat) || !Number.isFinite(lon)) continue;
        const icon = L.divIcon({
          html: `<div class="np-label np-label-${spec.tier || "river"}">${escapeHtml(text)}</div>`,
          className: "np-label-wrap",
          iconSize: [0, 0],
          iconAnchor: [0, 0],
        });
        L.marker([lat, lon], { icon, interactive: false, keyboard: false }).addTo(group);
      }
    }
    group._npLabels.built = true;
  };
  return group;
}

function approxCentroid(geom) {
  if (!geom) return null;
  if (geom.type === "Point") return [geom.coordinates[1], geom.coordinates[0]];
  const flat = [];
  function collect(coords) {
    if (typeof coords[0] === "number") {
      flat.push(coords);
    } else {
      coords.forEach(collect);
    }
  }
  try {
    collect(geom.coordinates);
    if (!flat.length) return null;
    let lat = 0, lon = 0;
    for (const [x, y] of flat) { lon += x; lat += y; }
    return [lat / flat.length, lon / flat.length];
  } catch (e) { return null; }
}

// For LineString / MultiLineString: walk the path and find the point at
// half the total arc length. Much better placement than centroid for long
// corridors (centroid can fall off-line).
function lineMidpoint(geom) {
  if (!geom) return null;
  let lines = [];
  if (geom.type === "LineString") lines = [geom.coordinates];
  else if (geom.type === "MultiLineString") lines = geom.coordinates;
  else return null;
  // Pick the longest sub-line (avoids small spurs)
  let bestLine = null, bestLen = -1;
  for (const ln of lines) {
    let len = 0;
    for (let i = 1; i < ln.length; i++) {
      const dx = ln[i][0] - ln[i-1][0], dy = ln[i][1] - ln[i-1][1];
      len += Math.sqrt(dx * dx + dy * dy);
    }
    if (len > bestLen) { bestLen = len; bestLine = ln; }
  }
  if (!bestLine || bestLine.length < 2) return null;
  const half = bestLen / 2;
  let acc = 0;
  for (let i = 1; i < bestLine.length; i++) {
    const dx = bestLine[i][0] - bestLine[i-1][0], dy = bestLine[i][1] - bestLine[i-1][1];
    const seg = Math.sqrt(dx * dx + dy * dy);
    if (acc + seg >= half) {
      const t = (half - acc) / (seg || 1);
      const lon = bestLine[i-1][0] + t * dx;
      const lat = bestLine[i-1][1] + t * dy;
      return [lat, lon];
    }
    acc += seg;
  }
  const last = bestLine[bestLine.length - 1];
  return [last[1], last[0]];
}

window.NepalExplorer = window.NepalExplorer || {};
Object.assign(window.NepalExplorer, {
  loadJSON, makeMap, makeBaseLayers, popupHTML, tooltipHTML,
  buildReverseIndex, lookupSlug, LayerManager, NEPAL_VIEW,
  buildLabelsOverlay,
  getZoomBehavior, ROLE_STYLES, BASEMAP_ADJUSTMENTS, resolveLayerStyle,
});
window.NepalExplorer._leafletInitLoaded = true;
})();
