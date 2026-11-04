"use strict";

const DATA_URL = "../../data/processed/dashboard/control-room.json";
const PAGE_SIZE = 50;
const TITLES = {
  overview: ["Control room", "Portfolio overview"],
  coverage: ["Evidence depth", "Coverage matrix"],
  reconciliation: ["Review workbench", "Reconciliation queues"],
  monitoring: ["Change intelligence", "Priority-project monitor"],
  sources: ["Evidence supply", "Source health"],
};

const state = {
  data: null,
  view: "overview",
  query: "",
  coverageTier: "all",
  coverageStatus: "all",
  queue: "doed_review",
  sourceFilter: "all",
  exportRows: [],
};

const $ = (selector, root = document) => root.querySelector(selector);
const $$ = (selector, root = document) => [...root.querySelectorAll(selector)];
const el = (tag, className, text) => {
  const node = document.createElement(tag);
  if (className) node.className = className;
  if (text !== undefined && text !== null) node.textContent = String(text);
  return node;
};
const human = value => String(value ?? "unknown").replaceAll("_", " ").replaceAll("-", " ");
const formatNumber = value => value === null || value === undefined ? "Unknown" : new Intl.NumberFormat("en-US", { maximumFractionDigits: 1 }).format(value);
const safePct = value => Math.max(0, Math.min(100, Number(value) || 0));
const matches = (values, query) => !query || values.some(value => String(value ?? "").toLowerCase().includes(query));

function setText(node, value) { node.textContent = value ?? ""; return node; }
function statusChip(value) {
  const chip = el("span", `status-chip ${String(value || "unknown").toLowerCase()}`, human(value));
  return chip;
}
function sectionHead(kicker, title, note = "") {
  const head = el("div", "section-head");
  const left = el("div"); left.append(el("p", "eyebrow", kicker), el("h2", "", title));
  head.append(left);
  if (note) head.append(el("p", "", note));
  return head;
}
function panel(title) { const node = el("section", "panel"); node.append(el("h3", "", title)); return node; }
function viewRoot(name) { return $(`#view-${name}`); }

function updateUrl() {
  const url = new URL(location.href);
  url.searchParams.set("view", state.view);
  if (state.query) url.searchParams.set("q", state.query); else url.searchParams.delete("q");
  history.replaceState({ view: state.view }, "", url);
}

function setView(name, { focus = false } = {}) {
  if (!TITLES[name]) name = "overview";
  state.view = name;
  $$('[data-view]').forEach(button => button.setAttribute("aria-current", button.dataset.view === name ? "page" : "false"));
  $$('[data-view-panel]').forEach(panelNode => { panelNode.hidden = panelNode.dataset.viewPanel !== name; });
  const [kicker, title] = TITLES[name];
  setText($("#view-kicker"), kicker); setText($("#view-title"), title);
  updateUrl();
  renderView(name);
  if (focus) $("#dashboard-main").focus();
}

function goToView(name) { state.query = ""; setView(name, { focus: true }); }

function renderOverview() {
  const root = viewRoot("overview"); root.replaceChildren();
  const data = state.data, o = data.overview;
  const hero = el("section", "hero");
  const heroCopy = el("div");
  heroCopy.append(el("p", "eyebrow", "Evidence before volume"), el("h2", "", "What deserves attention next?"), el("p", "", "A repository-wide operating picture of coverage, contradictions, monitoring depth, and the research queues that affect public claims."));
  const heroStat = el("div", "hero-stat"); heroStat.append(el("strong", "", `${o.registry.match_pct}%`), el("span", "", "of local hydro identities matched to current official DoED records"));
  hero.append(heroCopy, heroStat); root.append(hero);

  root.append(DashboardCharts.overviewSignals(data));

  const attention = el("section", "section"); attention.append(sectionHead("Attention", "Research operations queue", "Counts are triage signals, not truth scores."));
  const grid = el("div", "kpi-grid");
  o.attention.forEach(item => {
    const card = el("button", "kpi"); card.type = "button"; card.dataset.severity = item.severity; card.dataset.queue = item.id;
    card.append(el("span", "eyebrow", item.severity === "high" ? "Priority" : "Review"), el("span", "value", item.count), el("span", "label", item.title));
    card.addEventListener("click", () => goToView(item.view)); grid.append(card);
  });
  attention.append(grid); root.append(attention);

  const landscape = el("section", "section"); landscape.append(sectionHead("Coverage landscape", "Depth and integrity", "Separate denominators prevent false completeness."));
  const columns = el("div", "two-col");
  const coveragePanel = panel("Current denominators");
  const metrics = [
    ["Official identity coverage", o.registry.match_pct, `${o.registry.matched_local_rows} / ${o.registry.local_hydro_rows}`],
    ["Curated specs · moderate+", (o.specifications.tier_counts.moderate || 0) / o.specifications.projects * 100, `${o.specifications.tier_counts.moderate || 0} / ${o.specifications.projects}`],
    ["Sources with direct URL", o.corpus.sources_with_url / o.corpus.source_pages * 100, `${o.corpus.sources_with_url} / ${o.corpus.source_pages}`],
    ["Sources with publication date", o.corpus.sources_with_date / o.corpus.source_pages * 100, `${o.corpus.sources_with_date} / ${o.corpus.source_pages}`],
    ["Projects under monitoring", o.monitoring.projects / o.specifications.projects * 100, `${o.monitoring.projects} / ${o.specifications.projects}`],
  ];
  metrics.forEach(([label, pct, value]) => {
    const row = el("div", "metric-row"); const track = el("div", "track"); const fill = el("span", "fill"); fill.style.width = `${safePct(pct)}%`; track.append(fill); row.append(el("span", "", label), track, el("strong", "", value)); coveragePanel.append(row);
  });
  const queuePanel = panel("Attention now"); const list = el("ul", "attention-list");
  o.attention.slice(0, 5).forEach(item => { const li = el("li"); const button = el("button"); button.type = "button"; button.append(el("span", `severity-dot ${item.severity}`), el("span", "", item.title), el("span", "count-chip", item.count)); button.addEventListener("click", () => goToView(item.view)); li.append(button); list.append(li); });
  queuePanel.append(list); columns.append(coveragePanel, queuePanel); landscape.append(columns); root.append(landscape);

  const contractsSection = el("section", "section"); contractsSection.append(sectionHead("Data contracts", "What the system still cannot safely claim"));
  const contracts = panel("Contract health"); const contractGrid = el("div", "contract-grid");
  data.contracts.items.forEach(item => { const card = el("div", "contract"); card.dataset.status = item.status; card.append(statusChip(item.status), el("strong", "", item.label), el("p", "", item.detail)); contractGrid.append(card); });
  contracts.append(contractGrid); contractsSection.append(contracts); root.append(contractsSection);

  const recent = el("section", "section"); recent.append(sectionHead("Change feed", "Latest monitored events"));
  const recentPanel = panel("Most recent evidence-backed changes"); const eventList = el("ul", "event-list");
  data.monitoring.projects.flatMap(project => project.events.map(event => ({ project, event }))).sort((a,b) => (b.event.event_date || "").localeCompare(a.event.event_date || "")).slice(0, 8).forEach(({project,event}) => { const li = el("li"); li.append(el("span", "date", event.event_date), el("span", "", `${project.title} — ${event.title}`), statusChip(event.status_after)); eventList.append(li); });
  recentPanel.append(eventList); recent.append(recentPanel); root.append(recent);
  state.exportRows = o.attention;
}

function toolbar(root, options = {}) {
  const bar = el("div", "toolbar");
  const searchLabel = el("label", "search-control", "Search"); const search = el("input"); search.type = "search"; search.placeholder = options.placeholder || "Search records"; search.value = state.query; search.addEventListener("input", event => { state.query = event.target.value.trim().toLowerCase(); updateUrl(); options.onChange(); }); searchLabel.append(search); bar.append(searchLabel);
  return { bar, search };
}

function pctCell(section, label) {
  const td = el("td", "pct"); td.dataset.label = label; const pct = section?.pct ?? 0; td.append(document.createTextNode(`${formatNumber(pct)}%`)); const track = el("span", "micro-track"); const fill = el("i"); fill.style.width = `${safePct(pct)}%`; track.append(fill); td.append(track); return td;
}

function renderCoverage() {
  const root = viewRoot("coverage"); root.replaceChildren();
  root.append(sectionHead("25 curated dossiers", "Specification and monitoring coverage", "Completeness means populated fields; it does not prove correctness."));
  const controls = toolbar(root, { placeholder: "Search projects, status, identity…", onChange: renderCoverage });
  const tierLabel = el("label", "", "Depth"); const tier = el("select"); [["all","All tiers"],["thin","Thin"],["moderate","Moderate"],["rich","Rich"]].forEach(([v,t]) => { const option=el("option","",t); option.value=v; option.selected=state.coverageTier===v; tier.append(option); }); tier.addEventListener("change", e => { state.coverageTier=e.target.value; renderCoverage(); }); tierLabel.append(tier);
  const statusLabel = el("label", "", "Delivery status"); const statuses = [...new Set(state.data.coverage.projects.map(p=>p.status))].sort(); const status = el("select"); [["all","All statuses"], ...statuses.map(v=>[v,human(v)])].forEach(([v,t])=>{ const option=el("option","",t);option.value=v;option.selected=state.coverageStatus===v;status.append(option);}); status.addEventListener("change",e=>{state.coverageStatus=e.target.value;renderCoverage();}); statusLabel.append(status);
  const resultCount = el("div", "result-count"); resultCount.setAttribute("aria-live","polite"); controls.bar.append(tierLabel,statusLabel,resultCount); root.append(controls.bar);
  const q=state.query; const rows=state.data.coverage.projects.filter(row => (state.coverageTier==="all"||row.completeness.tier===state.coverageTier)&&(state.coverageStatus==="all"||row.status===state.coverageStatus)&&matches([row.title,row.slug,row.status,row.identity_state,row.monitoring_state],q));
  resultCount.textContent=`${rows.length} of ${state.data.coverage.projects.length}`;
  root.append(DashboardCharts.coverageHeatmap(rows, openProject));
  const wrap=el("div","table-wrap"); const table=el("table"); table.innerHTML="<thead><tr><th>Project</th><th>Delivery</th><th>Identity</th><th>Monitoring</th><th>Engineering</th><th>Output</th><th>Finance</th><th>Governance</th><th>Schedule</th><th>Storage</th><th>Overall</th><th>Verified</th></tr></thead>"; const body=el("tbody");
  rows.forEach(row=>{ const tr=el("tr"); tr.tabIndex=0; const name=el("td","project-cell");name.dataset.label="Project";name.append(el("strong","",row.title),el("span","",`${formatNumber(row.capacity_mw)} MW · ${row.slug}`)); tr.append(name); const delivery=el("td");delivery.dataset.label="Delivery";delivery.append(statusChip(row.status));tr.append(delivery); const identity=el("td");identity.dataset.label="Identity";identity.append(statusChip(row.identity_state));tr.append(identity); const monitor=el("td");monitor.dataset.label="Monitoring";monitor.append(statusChip(row.monitoring_state));tr.append(monitor); ["engineering","output","financial","governance","schedule","storage"].forEach(section=>tr.append(pctCell(row.completeness.sections[section],human(section)))); const overall=el("td");overall.dataset.label="Overall";overall.append(statusChip(`${row.completeness.tier}`),document.createTextNode(` ${row.completeness.pct}%`));tr.append(overall); const date=el("td","date",row.last_updated||"Unknown");date.dataset.label="Verified";tr.append(date); const open=()=>openProject(row.slug);tr.addEventListener("click",open);tr.addEventListener("keydown",e=>{if(e.key==="Enter"||e.key===" "){e.preventDefault();open();}});body.append(tr); }); table.append(body); wrap.append(table); root.append(rows.length?wrap:el("div","empty-state","No projects match these filters.")); state.exportRows=rows;
}

const QUEUES = {
  doed_review: ["DoED identity", "Official records needing human identity review"],
  doed_missing_operating: ["Missing operating coverage", "Confirmed official operating records absent from the legacy local registry"],
  hydromap_active_review: ["HydroMap comparison", "Secondary breadth benchmark; never production authority"],
  capacity_conflicts: ["Capacity conflicts", "Same-name records with differing stated MW"],
  open_flags: ["Research flags", "Human-maintained evidence and ontology backlog"],
};

function queueTitle(row) { return row.title || row.official_project || row.external_name || row.project || row.local_name || row.queue_id || row.id; }
function queueDetail(row) { return row.detail || row.suggested_local_project || row.local_name || row.external_project || row.description || row.review_decision || "Review source record"; }
function renderReconciliation() {
  const root=viewRoot("reconciliation");root.replaceChildren(); const totalItems=Object.keys(QUEUES).reduce((sum,key)=>sum+state.data.reconciliation[key].length,0);root.append(sectionHead(`${totalItems} work items`, "Identity, capacity and evidence review", "DoED is authoritative; HydroMap remains a comparative signal."));
  const tabs=el("div","queue-tabs");tabs.setAttribute("role","tablist"); Object.entries(QUEUES).forEach(([key,[label]])=>{const button=el("button","",`${label} · ${state.data.reconciliation[key].length}`);button.type="button";button.setAttribute("role","tab");button.setAttribute("aria-selected",String(state.queue===key));button.addEventListener("click",()=>{state.queue=key;state.query="";renderReconciliation();});tabs.append(button);});root.append(tabs);
  const controls=toolbar(root,{placeholder:"Search the selected queue…",onChange:renderReconciliation});const count=el("div","result-count");count.setAttribute("aria-live","polite");controls.bar.append(count);root.append(controls.bar);
  const sourceRows=state.data.reconciliation[state.queue];const rows=sourceRows.filter(row=>matches(Object.values(row),state.query));count.textContent=`${rows.length} of ${sourceRows.length} · showing first ${Math.min(PAGE_SIZE,rows.length)}`;
  if(state.queue==="capacity_conflicts")root.append(DashboardCharts.capacityParity(rows,row=>{state.query=String(row.normalized_name||row.local_name||"").toLowerCase();updateUrl();renderReconciliation();}));
  const wrap=el("div","table-wrap");const table=el("table");table.innerHTML="<thead><tr><th>Record</th><th>Context / suggestion</th><th>Source state</th><th>Capacity</th><th>Review</th></tr></thead>";const body=el("tbody");
  rows.slice(0,PAGE_SIZE).forEach(row=>{const tr=el("tr");const name=el("td","project-cell");name.dataset.label="Record";name.append(el("strong","",queueTitle(row)),el("span","",row.queue_id||row.id||row.date||""));tr.append(name);const detail=el("td","",queueDetail(row));detail.dataset.label="Context";tr.append(detail);const source=el("td","",human(row.official_regulatory_category||row.external_category||row.severity||row.queue_type));source.dataset.label="Source state";tr.append(source);const capacity=el("td","",row.absolute_difference_mw?`${row.local_capacity_mw} → ${row.external_capacity_mw} MW`:row.official_capacity_mw?`${row.official_capacity_mw} MW`:row.capacity_mw?`${row.capacity_mw} MW`:"—");capacity.dataset.label="Capacity";tr.append(capacity);const review=el("td");review.dataset.label="Review";review.append(statusChip(row.review_decision||row.local_registry_relation||row.severity||"unreviewed"));tr.append(review);body.append(tr);});table.append(body);wrap.append(table);root.append(rows.length?wrap:el("div","empty-state","No queue items match this search.")); state.exportRows=rows;
}

function renderMonitoring() {
  const root=viewRoot("monitoring");root.replaceChildren();root.append(sectionHead("10 priority records", "Current status, change and blockers", "Monitoring language appears only where dated evidence exists."));
  const controls=toolbar(root,{placeholder:"Search projects, blockers or event titles…",onChange:renderMonitoring});const count=el("div","result-count");count.setAttribute("aria-live","polite");controls.bar.append(count);root.append(controls.bar);
  const rows=state.data.monitoring.projects.filter(project=>matches([project.title,project.slug,project.status,...project.events.map(e=>e.title),...project.blockers.map(b=>b.category)],state.query));count.textContent=`${rows.length} of ${state.data.monitoring.projects.length}`;
  root.append(DashboardCharts.monitoringTimeline(rows,state.data.data_as_of,openProject));
  const grid=el("div","monitor-grid");rows.forEach(project=>{const card=el("article","monitor-card");card.tabIndex=0;card.append(el("p","eyebrow",project.last_verified?`Verified ${project.last_verified}`:"Verification unknown"),el("h3","",project.title));const chips=el("div","monitor-meta");chips.append(statusChip(project.status),statusChip(`${project.active_blocker_count} active blockers`));if(project.spec_completeness)chips.append(statusChip(`${project.spec_completeness.pct}% specs`));card.append(chips);card.append(el("p","",project.latest_event?`${project.latest_event.event_date} — ${project.latest_event.title}`:"No dated event in the current monitoring table."));const footer=el("div","monitor-footer");footer.append(el("span","",`${project.events.length} events · ${project.blockers.length} blockers`),el("span","",project.capacity_mw?`${formatNumber(project.capacity_mw)} MW`:"Corridor"));card.append(footer);const open=()=>openProject(project.slug);card.addEventListener("click",open);card.addEventListener("keydown",e=>{if(e.key==="Enter"||e.key===" "){e.preventDefault();open();}});grid.append(card);});root.append(rows.length?grid:el("div","empty-state","No monitored projects match this search."));state.exportRows=rows;
}

function renderSources() {
  const root=viewRoot("sources");root.replaceChildren();const summary=state.data.overview.corpus;root.append(sectionHead(`${summary.source_pages} governed source pages`, "Evidence supply and metadata health", "Publication date is not a last-checked date."));
  const controls=toolbar(root,{placeholder:"Search source titles and slugs…",onChange:renderSources});const filterLabel=el("label","","Metadata");const filter=el("select");[["all","All sources"],["missing-url","Missing URL"],["missing-date","Missing date"],["no-backlinks","No backlinks"]].forEach(([v,t])=>{const option=el("option","",t);option.value=v;option.selected=state.sourceFilter===v;filter.append(option);});filter.addEventListener("change",e=>{state.sourceFilter=e.target.value;renderSources();});filterLabel.append(filter);const count=el("div","result-count");count.setAttribute("aria-live","polite");controls.bar.append(filterLabel,count);root.append(controls.bar);
  const rows=state.data.sources.records.filter(row=>(state.sourceFilter==="all"||(state.sourceFilter==="missing-url"&&!row.has_url)||(state.sourceFilter==="missing-date"&&!row.has_source_date)||(state.sourceFilter==="no-backlinks"&&row.used_by_count===0))&&matches([row.title,row.slug,row.source_url],state.query)).sort((a,b)=>b.used_by_count-a.used_by_count);count.textContent=`${rows.length} of ${state.data.sources.records.length}`;
  root.append(DashboardCharts.sourceReliance(rows,row=>{state.query=row.slug.toLowerCase();updateUrl();renderSources();}));
  const wrap=el("div","table-wrap");const table=el("table");table.innerHTML="<thead><tr><th>Source</th><th>Publication date</th><th>Last checked</th><th>Used by</th><th>Direct record</th></tr></thead>";const body=el("tbody");rows.forEach(row=>{const tr=el("tr");const name=el("td","project-cell");name.dataset.label="Source";const link=el("a","",row.title);link.href=row.wiki_url;link.target="_blank";name.append(link,el("span","",row.slug));tr.append(name);const date=el("td","date",row.source_date||"Not recorded");date.dataset.label="Publication date";tr.append(date);const checked=el("td","date",row.last_checked||"Unknown");checked.dataset.label="Last checked";tr.append(checked);const used=el("td","",row.used_by_count);used.dataset.label="Used by";tr.append(used);const direct=el("td");direct.dataset.label="Direct record";if(row.source_href){const out=el("a","","Open source ↗");out.href=row.source_href;out.target="_blank";out.rel="noopener noreferrer";direct.append(out);}else direct.append(statusChip("missing"));tr.append(direct);body.append(tr);});table.append(body);wrap.append(table);root.append(rows.length?wrap:el("div","empty-state","No sources match these filters."));state.exportRows=rows;
}

function openProject(slug) {
  const project=state.data.monitoring.projects.find(row=>row.slug===slug);const coverage=state.data.coverage.projects.find(row=>row.slug===slug);if(!project&&!coverage)return;
  const record=project||coverage;setText($("#detail-title"),record.title);const body=$("#detail-body");body.replaceChildren();const stats=el("div","detail-grid");[["Delivery",record.status],["Capacity",record.capacity_mw?`${formatNumber(record.capacity_mw)} MW`:"Unknown"],["Last verified",record.last_verified||record.last_updated||"Unknown"],["Events",project?.events.length||0],["Active blockers",project?.active_blocker_count||0],["Spec depth",`${(project?.spec_completeness||coverage?.completeness)?.pct??0}%`]].forEach(([label,value])=>{const card=el("div","detail-stat");card.append(el("span","",label),el("strong","",human(value)));stats.append(card);});body.append(stats);
  if(project?.latest_event){const section=el("section","detail-section");section.append(el("h3","","Latest event"));const item=el("div","detail-item");item.append(el("strong","",`${project.latest_event.event_date} · ${project.latest_event.title}`),el("p","",project.latest_event.description));if(project.latest_event.source_url){const link=el("a","","Open evidence ↗");link.href=project.latest_event.source_url;link.target="_blank";link.rel="noopener noreferrer";item.append(link);}section.append(item);body.append(section);}
  if(project?.blockers.length){const section=el("section","detail-section");section.append(el("h3","","Blockers and monitoring constraints"));project.blockers.forEach(blocker=>{const item=el("div","detail-item");item.append(statusChip(blocker.status),el("strong","",` ${human(blocker.category)} · ${blocker.blocked_milestone}`),el("p","",blocker.description));section.append(item);});body.append(section);}
  const links=el("section","detail-section");links.append(el("h3","","Continue investigation"));const explorer=el("a","button","Open evidence page in explorer ↗");explorer.href=`/wiki/explorer/?page=${encodeURIComponent(slug)}&preset=power_system`;explorer.target="_blank";links.append(explorer);body.append(links);$("#project-detail").showModal();
}

function renderView(name) {
  if (!state.data) return;
  ({ overview:renderOverview, coverage:renderCoverage, reconciliation:renderReconciliation, monitoring:renderMonitoring, sources:renderSources }[name] || renderOverview)();
}

function csvValue(value) { const text=typeof value==="object"?JSON.stringify(value):String(value??"");return `"${text.replaceAll('"','""')}"`; }
function exportCurrentView() {
  if(!state.exportRows.length)return;const keys=[...new Set(state.exportRows.flatMap(row=>Object.keys(row)))];const csv=[keys.map(csvValue).join(","),...state.exportRows.map(row=>keys.map(key=>csvValue(row[key])).join(","))].join("\n");const blob=new Blob([csv],{type:"text/csv"});const url=URL.createObjectURL(blob);const link=document.createElement("a");link.href=url;link.download=`nepal-energy-${state.view}.csv`;link.click();URL.revokeObjectURL(url);
}

async function init() {
  const params=new URLSearchParams(location.search);state.view=TITLES[params.get("view")]?params.get("view"):"overview";state.query=(params.get("q")||"").toLowerCase();
  $$('[data-view]').forEach(button=>button.addEventListener("click",()=>goToView(button.dataset.view)));$("#close-detail").addEventListener("click",()=>$("#project-detail").close());$("#export-view").addEventListener("click",exportCurrentView);
  document.addEventListener("keydown", event => {
    if (event.key === "Escape" && $("#project-detail").open) {
      event.preventDefault();
      $("#project-detail").close();
    }
  });
  try { const response=await fetch(DATA_URL,{cache:"no-store"});if(!response.ok)throw new Error(`Dashboard data returned HTTP ${response.status}`);state.data=await response.json();setText($("#as-of"),`Evidence as of ${state.data.data_as_of||"unknown"}`);$("#load-state").hidden=true;$("#dashboard-content").hidden=false;setView(state.view); }
  catch(error){const load=$("#load-state");load.classList.add("error");load.replaceChildren(el("div","",`Dashboard unavailable: ${error.message}. Run “make dashboard-build” and serve from the repository root.`));console.error(error);}
}

window.addEventListener("popstate",()=>{const view=new URLSearchParams(location.search).get("view");if(TITLES[view])setView(view);});
document.addEventListener("DOMContentLoaded",init);
