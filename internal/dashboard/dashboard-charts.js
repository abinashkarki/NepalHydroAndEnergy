"use strict";

(function initDashboardCharts(global) {
  const NS = "http://www.w3.org/2000/svg";
  const SECTIONS = ["engineering", "output", "financial", "governance", "schedule", "storage"];
  let chartSequence = 0;

  const htmlEl = (tag, className, text) => {
    const node = document.createElement(tag);
    if (className) node.className = className;
    if (text !== undefined && text !== null) node.textContent = String(text);
    return node;
  };

  const svgEl = (tag, attrs = {}, text) => {
    const node = document.createElementNS(NS, tag);
    Object.entries(attrs).forEach(([name, value]) => node.setAttribute(name, String(value)));
    if (text !== undefined && text !== null) node.textContent = String(text);
    return node;
  };

  const short = (value, limit = 30) => {
    const text = String(value || "Unknown");
    return text.length > limit ? `${text.slice(0, limit - 1)}…` : text;
  };

  const number = value => {
    const parsed = Number(value);
    return Number.isFinite(parsed) ? parsed : null;
  };

  const pct = value => Math.max(0, Math.min(100, number(value) || 0));

  const human = value => String(value ?? "unknown").replaceAll("_", " ").replaceAll("-", " ");

  const format = (value, digits = 1) => new Intl.NumberFormat("en-US", { maximumFractionDigits: digits }).format(value);

  function chartShell(kicker, title, note, legendItems = []) {
    const shell = htmlEl("section", "dither-chart");
    const header = htmlEl("div", "dither-chart-head");
    const copy = htmlEl("div");
    copy.append(htmlEl("p", "dither-kicker", kicker), htmlEl("h3", "", title));
    if (note) copy.append(htmlEl("p", "dither-note", note));
    header.append(copy);
    if (legendItems.length) {
      const legend = htmlEl("div", "dither-legend");
      legend.setAttribute("aria-label", "Chart legend");
      legendItems.forEach(item => {
        const entry = htmlEl("span", "dither-legend-item", item.label);
        const swatch = htmlEl("i", `dither-swatch ${item.className || "dots"}`);
        entry.prepend(swatch);
        legend.append(entry);
      });
      header.append(legend);
    }
    const stage = htmlEl("div", "dither-stage");
    const tooltip = htmlEl("div", "dither-tooltip");
    tooltip.hidden = true;
    tooltip.setAttribute("role", "status");
    stage.append(tooltip);
    shell.append(header, stage);
    return { shell, stage, tooltip };
  }

  function addPatterns(svg, prefix) {
    const defs = svgEl("defs");
    const patterns = [
      ["dots-green", "#176b55", "dots"],
      ["dots-blue", "#315d87", "dots"],
      ["dots-amber", "#a55b08", "dots"],
      ["dots-red", "#a43d35", "dots"],
      ["hatch-green", "#176b55", "hatch"],
      ["hatch-blue", "#315d87", "hatch"],
      ["hatch-amber", "#a55b08", "hatch"],
      ["hatch-red", "#a43d35", "hatch"],
    ];
    patterns.forEach(([name, color, type]) => {
      const pattern = svgEl("pattern", {
        id: `${prefix}-${name}`,
        width: type === "dots" ? 6 : 7,
        height: type === "dots" ? 6 : 7,
        patternUnits: "userSpaceOnUse",
      });
      if (type === "dots") {
        pattern.append(svgEl("circle", { cx: 1.5, cy: 1.5, r: 1.15, fill: color }));
      } else {
        pattern.append(svgEl("path", { d: "M-2 2 L2 -2 M0 7 L7 0 M5 9 L9 5", stroke: color, "stroke-width": 1.45 }));
      }
      defs.append(pattern);
    });
    const glow = svgEl("filter", { id: `${prefix}-glow`, x: "-80%", y: "-80%", width: "260%", height: "260%" });
    glow.append(svgEl("feGaussianBlur", { stdDeviation: 3, result: "blur" }), svgEl("feMerge"));
    const merge = glow.lastChild;
    merge.append(svgEl("feMergeNode", { in: "blur" }), svgEl("feMergeNode", { in: "SourceGraphic" }));
    defs.append(glow);
    svg.append(defs);
  }

  function makeSvg(stage, width, height, label, description) {
    const svg = svgEl("svg", {
      class: "dither-svg",
      viewBox: `0 0 ${width} ${height}`,
      role: "img",
      "aria-label": label,
      preserveAspectRatio: "xMinYMin meet",
    });
    svg.append(svgEl("title", {}, label), svgEl("desc", {}, description));
    stage.prepend(svg);
    return svg;
  }

  function positionTooltip(stage, tooltip, event, content) {
    tooltip.replaceChildren();
    if (Array.isArray(content)) {
      content.forEach((line, index) => tooltip.append(htmlEl(index === 0 ? "strong" : "span", "", line)));
    } else {
      tooltip.textContent = String(content);
    }
    const stageRect = stage.getBoundingClientRect();
    const clientX = event?.clientX || stageRect.left + stageRect.width / 2;
    const clientY = event?.clientY || stageRect.top + 24;
    tooltip.style.left = `${Math.max(10, Math.min(stageRect.width - 220, clientX - stageRect.left + 12))}px`;
    tooltip.style.top = `${Math.max(8, clientY - stageRect.top - 8)}px`;
    tooltip.hidden = false;
  }

  function bindMark(mark, stage, tooltip, content, onActivate) {
    mark.classList.add("dither-mark");
    mark.setAttribute("tabindex", "0");
    mark.setAttribute("role", onActivate ? "button" : "img");
    const show = event => positionTooltip(stage, tooltip, event, typeof content === "function" ? content() : content);
    mark.addEventListener("pointerenter", show);
    mark.addEventListener("pointermove", show);
    mark.addEventListener("focus", show);
    mark.addEventListener("pointerleave", () => { tooltip.hidden = true; });
    mark.addEventListener("blur", () => { tooltip.hidden = true; });
    if (onActivate) {
      mark.addEventListener("click", onActivate);
      mark.addEventListener("keydown", event => {
        if (event.key === "Enter" || event.key === " ") {
          event.preventDefault();
          onActivate();
        }
      });
    }
  }

  function ditherFill(prefix, value, hue = "green") {
    if (value <= 0) return "#ebe9e1";
    if (value < 25) return `url(#${prefix}-dots-${hue})`;
    if (value < 60) return `url(#${prefix}-hatch-${hue})`;
    return hue === "blue" ? "#315d87" : hue === "amber" ? "#a55b08" : hue === "red" ? "#a43d35" : "#176b55";
  }

  function signalCard(title, value, note, measures, mode = "share") {
    const card = htmlEl("article", "dither-signal");
    card.append(htmlEl("p", "dither-kicker", title), htmlEl("strong", "dither-signal-value", value), htmlEl("p", "dither-signal-note", note));
    const list = htmlEl("div", "dither-signal-list");
    const total = Math.max(1, measures.reduce((sum, item) => sum + item.value, 0));
    measures.forEach(item => {
      const row = htmlEl("div", "dither-signal-row");
      const label = htmlEl("span", "dither-signal-label", item.label);
      const display = htmlEl("strong", "dither-signal-measure", item.display ?? item.value);
      const track = htmlEl("span", "dither-signal-track");
      const fill = htmlEl("i", item.className || "dots-green");
      const width = mode === "percent" ? pct(item.value) : item.value / total * 100;
      fill.style.width = `${Math.max(item.value > 0 ? 3 : 0, width)}%`;
      track.append(fill);
      row.append(label, display, track);
      list.append(row);
    });
    card.append(list);
    return card;
  }

  function overviewSignals(data) {
    const section = htmlEl("section", "section");
    const head = htmlEl("div", "section-head");
    const copy = htmlEl("div");
    copy.append(htmlEl("p", "eyebrow", "What the charts say"), htmlEl("h2", "", "Three findings worth acting on"));
    head.append(copy, htmlEl("p", "", "The headline is the conclusion; the bars show how the records are distributed."));
    section.append(head);
    const grid = htmlEl("div", "dither-signal-grid");

    const coverageSegments = SECTIONS.map((name, index) => {
      const filled = data.coverage.projects.reduce((sum, project) => sum + (project.completeness.sections[name]?.filled || 0), 0);
      const total = data.coverage.projects.reduce((sum, project) => sum + (project.completeness.sections[name]?.total || 0), 0);
      const value = total ? filled / total * 100 : 0;
      return { label: human(name), value, display: `${format(value)}%`, className: index % 2 ? "hatch-green" : "dots-green" };
    });
    const weakest = [...coverageSegments].sort((a, b) => a.value - b.value)[0];
    grid.append(signalCard(
      "Which evidence area is weakest?",
      `${weakest.label}: ${weakest.display} filled`,
      "Financial evidence is the largest structured research gap across the 25 project dossiers.",
      coverageSegments,
      "percent",
    ));

    const conflictBins = [
      { label: "<10%", value: 0, className: "dots-green" },
      { label: "10–25%", value: 0, className: "hatch-amber" },
      { label: "25–50%", value: 0, className: "dots-red" },
      { label: "50%+", value: 0, className: "hatch-red" },
    ];
    data.reconciliation.capacity_conflicts.forEach(row => {
      const local = number(row.local_capacity_mw), external = number(row.external_capacity_mw);
      if (local === null || external === null || Math.max(local, external) <= 0) return;
      const difference = Math.abs(local - external) / Math.max(local, external);
      conflictBins[difference < .1 ? 0 : difference < .25 ? 1 : difference < .5 ? 2 : 3].value += 1;
    });
    const material = conflictBins[2].value + conflictBins[3].value;
    const conflictTotal = conflictBins.reduce((sum, item) => sum + item.value, 0);
    grid.append(signalCard(
      "How many capacity records materially disagree?",
      `${material} of ${conflictTotal} comparisons`,
      "These unresolved comparisons differ by at least 25% between the local and external records.",
      conflictBins,
    ));

    const asOf = new Date(`${data.data_as_of}T00:00:00Z`);
    const ageBins = [
      { label: "<1y", value: 0, className: "dots-green" },
      { label: "1–3y", value: 0, className: "hatch-amber" },
      { label: "3–5y", value: 0, className: "dots-red" },
      { label: "5y+", value: 0, className: "hatch-red" },
    ];
    data.monitoring.projects.flatMap(project => project.blockers).filter(blocker => blocker.status === "active").forEach(blocker => {
      const observed = new Date(`${blocker.first_observed_date}T00:00:00Z`);
      const years = (asOf - observed) / 31557600000;
      ageBins[years < 1 ? 0 : years < 3 ? 1 : years < 5 ? 2 : 3].value += 1;
    });
    const blockerTotal = ageBins.reduce((sum, item) => sum + item.value, 0);
    grid.append(signalCard(
      "How old are the unresolved blockers?",
      `${ageBins[3].value} of ${blockerTotal} are 5+ years old`,
      "Age is measured from first observation in this repository, not the proven start of the underlying constraint.",
      ageBins,
    ));

    section.append(grid);
    return section;
  }

  function coverageHeatmap(rows, onProject) {
    const { shell, stage, tooltip } = chartShell(
      "Research gaps by project",
      "Which project dossiers need research first?",
      "Each cell is the share of required fields already filled. Low percentages are gaps to investigate; they do not mean the project itself is performing poorly.",
      [
        { label: "Empty · 0%", className: "empty" },
        { label: "Mostly missing · 1–24%", className: "dots-green" },
        { label: "Partly filled · 25–59%", className: "hatch-green" },
        { label: "Mostly filled · 60–100%", className: "solid-green" },
      ],
    );
    if (!rows.length) return shell;
    const prefix = `coverage-${++chartSequence}`;
    const left = 255, top = 68, cellWidth = 98, rowHeight = 29, right = 84;
    const width = left + cellWidth * SECTIONS.length + right;
    const height = top + rowHeight * rows.length + 42;
    const svg = makeSvg(stage, width, height, "Specification coverage heatmap", "Each project is a row and each specification domain is a column.");
    addPatterns(svg, prefix);

    SECTIONS.forEach((section, column) => {
      const x = left + column * cellWidth + cellWidth / 2;
      svg.append(svgEl("text", { x, y: 24, class: "dither-axis dither-axis-heading", "text-anchor": "middle" }, short(human(section), 12)));
      const average = rows.reduce((sum, project) => sum + pct(project.completeness.sections[section]?.pct), 0) / rows.length;
      svg.append(svgEl("text", { x, y: 44, class: "dither-axis", "text-anchor": "middle" }, `${format(average)}% avg`));
    });
    svg.append(svgEl("text", { x: left + cellWidth * SECTIONS.length + 38, y: 24, class: "dither-axis dither-axis-heading", "text-anchor": "middle" }, "overall"));

    rows.forEach((project, rowIndex) => {
      const y = top + rowIndex * rowHeight;
      if (rowIndex % 2 === 0) svg.append(svgEl("rect", { x: 0, y: y - 4, width, height: rowHeight, class: "dither-row-band" }));
      const label = svgEl("text", { x: 8, y: y + 13, class: "dither-row-label" }, short(project.title, 34));
      label.setAttribute("aria-hidden", "true");
      svg.append(label);
      SECTIONS.forEach((section, column) => {
        const value = pct(project.completeness.sections[section]?.pct);
        const x = left + column * cellWidth + 5;
        const rect = svgEl("rect", { x, y, width: cellWidth - 10, height: 21, rx: 2, fill: ditherFill(prefix, value, "green") });
        rect.setAttribute("aria-label", `${project.title}, ${human(section)}: ${format(value)} percent populated`);
        bindMark(rect, stage, tooltip, [project.title, `${human(section)} · ${format(value)}% populated`, `${project.completeness.sections[section]?.filled || 0} of ${project.completeness.sections[section]?.total || 0} fields`], () => onProject(project.slug));
        svg.append(rect, svgEl("text", { x: x + (cellWidth - 10) / 2, y: y + 14, class: `dither-cell-value ${value >= 60 ? "inverse" : ""}`, "text-anchor": "middle", "pointer-events": "none" }, `${format(value)}%`));
      });
      const overallX = left + cellWidth * SECTIONS.length + 38;
      const overall = pct(project.completeness.pct);
      svg.append(svgEl("circle", { cx: overallX, cy: y + 10.5, r: 8, fill: ditherFill(prefix, overall, "blue") }), svgEl("text", { x: overallX + 14, y: y + 14, class: "dither-axis" }, `${format(overall)}%`));
    });
    return shell;
  }

  function capacityParity(rows, onSelect) {
    const usable = rows
      .map(row => {
        const local = number(row.local_capacity_mw);
        const external = number(row.external_capacity_mw);
        return { row, local, external, difference: local > 0 && external > 0 ? Math.abs(local - external) / Math.max(local, external) * 100 : null };
      })
      .filter(item => item.difference !== null)
      .sort((a, b) => b.difference - a.difference);
    const { shell, stage, tooltip } = chartShell(
      "Largest disagreements first",
      "Which capacity records disagree most?",
      `Bar length is the gap as a share of the larger stated capacity. 0% means agreement. Showing the ${Math.min(15, usable.length)} largest gaps among ${usable.length} visible comparisons.`,
      [
        { label: "Small · under 10%", className: "dots-green" },
        { label: "Review · 10–24%", className: "hatch-amber" },
        { label: "Material · 25%+", className: "dots-red" },
      ],
    );
    if (!usable.length) return shell;
    const prefix = `parity-${++chartSequence}`;
    const visible = usable.slice(0, 15);
    const width = 1080, left = 280, right = 245, top = 54, rowHeight = 34, bottom = 42;
    const plotWidth = width - left - right;
    const height = top + visible.length * rowHeight + bottom;
    const x = value => left + pct(value) / 100 * plotWidth;
    const svg = makeSvg(stage, width, height, "Largest capacity disagreements", "Horizontal bars rank the largest percentage differences between local and external capacity records.");
    addPatterns(svg, prefix);

    [0, 25, 50, 75, 100].forEach(value => {
      svg.append(
        svgEl("line", { x1: x(value), y1: top - 18, x2: x(value), y2: height - bottom + 4, class: "dither-grid" }),
        svgEl("text", { x: x(value), y: 22, class: "dither-axis", "text-anchor": "middle" }, `${value}%`),
      );
    });
    svg.append(svgEl("text", { x: left + plotWidth / 2, y: height - 10, class: "dither-axis dither-axis-heading", "text-anchor": "middle" }, "Difference between the two stated capacities"));

    visible.forEach(({ row, local, external, difference }, index) => {
      const y = top + index * rowHeight;
      if (index % 2 === 0) svg.append(svgEl("rect", { x: 0, y: y - 9, width, height: rowHeight, class: "dither-row-band" }));
      svg.append(svgEl("text", { x: 8, y: y + 7, class: "dither-row-label" }, short(row.local_name, 39)));
      const fill = difference >= 50 ? `url(#${prefix}-hatch-red)` : difference >= 25 ? `url(#${prefix}-dots-red)` : difference >= 10 ? `url(#${prefix}-hatch-amber)` : `url(#${prefix}-dots-green)`;
      const bar = svgEl("rect", { x: left, y: y - 7, width: Math.max(3, x(difference) - left), height: 18, rx: 2, fill, style: `animation-delay:${Math.min(index * 25, 350)}ms` });
      bar.setAttribute("aria-label", `${row.local_name}: local ${format(local, 3)} megawatts, external ${format(external, 3)} megawatts, ${format(difference)} percent difference`);
      bindMark(bar, stage, tooltip, [row.local_name, `Local ${format(local, 3)} MW · external ${format(external, 3)} MW`, `${format(difference)}% apart · select to filter the table`], () => onSelect(row));
      svg.append(
        bar,
        svgEl("text", { x: width - right + 14, y: y + 7, class: "dither-annotation" }, `${format(local, 3)} vs ${format(external, 3)} MW`),
        svgEl("text", { x: width - 10, y: y + 7, class: "dither-row-value", "text-anchor": "end" }, `${format(difference)}% apart`),
      );
    });
    return shell;
  }

  function monitoringTimeline(projects, asOfValue, onProject) {
    const asOf = new Date(`${asOfValue}T00:00:00Z`).getTime();
    const rows = projects.map(project => {
      const active = project.blockers.filter(blocker => blocker.status === "active" && blocker.first_observed_date);
      const oldest = active.sort((a, b) => a.first_observed_date.localeCompare(b.first_observed_date))[0] || null;
      const years = oldest ? Math.max(0, (asOf - new Date(`${oldest.first_observed_date}T00:00:00Z`).getTime()) / 31557600000) : 0;
      return { project, active, oldest, years };
    }).sort((a, b) => b.years - a.years);
    const { shell, stage, tooltip } = chartShell(
      "Oldest unresolved issue by project",
      "How long have active blockers been on record?",
      "One bar per project, measured from its oldest active blocker to the evidence date. This is time since first observation here—not proof that the underlying problem began then.",
      [
        { label: "Under 1 year", className: "dots-green" },
        { label: "1–5 years", className: "hatch-amber" },
        { label: "5+ years", className: "dots-red" },
      ],
    );
    if (!projects.length) return shell;
    const prefix = `timeline-${++chartSequence}`;
    const width = 1040, left = 280, right = 190, top = 54, rowHeight = 40, bottom = 44;
    const maxYears = Math.max(1, Math.ceil(Math.max(...rows.map(row => row.years))));
    const plotWidth = width - left - right;
    const height = top + rows.length * rowHeight + bottom;
    const x = value => left + Math.min(value, maxYears) / maxYears * plotWidth;
    const svg = makeSvg(stage, width, height, "Age of active project blockers", "Horizontal bars show the years since the oldest active blocker was first observed for each project.");
    addPatterns(svg, prefix);

    const tickStep = maxYears > 12 ? 3 : maxYears > 6 ? 2 : 1;
    for (let year = 0; year <= maxYears; year += tickStep) {
      svg.append(
        svgEl("line", { x1: x(year), y1: top - 20, x2: x(year), y2: height - bottom + 5, class: "dither-grid" }),
        svgEl("text", { x: x(year), y: 22, class: "dither-axis", "text-anchor": "middle" }, `${year}y`),
      );
    }
    svg.append(svgEl("text", { x: left + plotWidth / 2, y: height - 10, class: "dither-axis dither-axis-heading", "text-anchor": "middle" }, `Years on record · evidence as of ${asOfValue}`));

    rows.forEach(({ project, active, oldest, years }, index) => {
      const y = top + index * rowHeight;
      if (index % 2 === 0) svg.append(svgEl("rect", { x: 0, y: y - 10, width, height: rowHeight, class: "dither-row-band" }));
      svg.append(
        svgEl("text", { x: 8, y: y + 5, class: "dither-row-label" }, short(project.title, 38)),
        svgEl("text", { x: 8, y: y + 20, class: "dither-axis" }, human(project.status)),
      );
      if (!oldest) {
        svg.append(
          svgEl("circle", { cx: left + 4, cy: y + 4, r: 4, fill: "#b8beb9" }),
          svgEl("text", { x: width - 10, y: y + 8, class: "dither-row-value", "text-anchor": "end" }, "No active blocker recorded"),
        );
        return;
      }
      const fill = years >= 5 ? `url(#${prefix}-dots-red)` : years >= 1 ? `url(#${prefix}-hatch-amber)` : `url(#${prefix}-dots-green)`;
      const bar = svgEl("rect", { x: left, y: y - 5, width: Math.max(5, x(years) - left), height: 20, rx: 2, fill, style: `animation-delay:${Math.min(index * 35, 350)}ms` });
      bar.setAttribute("aria-label", `${project.title}: oldest active blocker first observed ${oldest.first_observed_date}, ${format(years)} years on record, ${active.length} active blockers`);
      bindMark(bar, stage, tooltip, [project.title, `${format(years)} years since first observation`, `${active.length} active blocker${active.length === 1 ? "" : "s"} · first recorded ${oldest.first_observed_date}`], () => onProject(project.slug));
      svg.append(
        bar,
        svgEl("text", { x: width - 10, y: y + 8, class: "dither-row-value", "text-anchor": "end" }, `${format(years)} years · ${active.length} active`),
      );
    });
    return shell;
  }

  function sourceReliance(rows, onSource) {
    const { shell, stage, tooltip } = chartShell(
      "Most-used records first",
      "Which sources does the wiki rely on most?",
      `A longer bar means more wiki pages depend on that source. Showing the ${Math.min(12, rows.length)} most-used among ${rows.length} visible sources; warning fills flag missing metadata.`,
      [
        { label: "Date and direct record available", className: "dots-green" },
        { label: "Publication date missing", className: "hatch-amber" },
        { label: "Direct record missing", className: "dots-red" },
      ],
    );
    if (!rows.length) return shell;
    const prefix = `sources-${++chartSequence}`;
    const parsed = rows
      .map(row => ({ row, used: number(row.used_by_count) || 0 }))
      .sort((a, b) => b.used - a.used)
      .slice(0, 12);
    const width = 1080, left = 365, right = 175, top = 52, rowHeight = 42, bottom = 44;
    const maxUsed = Math.max(...parsed.map(item => item.used), 1);
    const plotWidth = width - left - right;
    const height = top + parsed.length * rowHeight + bottom;
    const x = value => left + value / maxUsed * plotWidth;
    const svg = makeSvg(stage, width, height, "Sources ranked by wiki dependency", "Horizontal bars rank sources by the number of wiki pages that use them.");
    addPatterns(svg, prefix);

    const tickStep = maxUsed > 40 ? 10 : maxUsed > 20 ? 5 : maxUsed > 8 ? 2 : 1;
    for (let value = 0; value <= maxUsed; value += tickStep) {
      svg.append(
        svgEl("line", { x1: x(value), y1: top - 18, x2: x(value), y2: height - bottom + 4, class: "dither-grid" }),
        svgEl("text", { x: x(value), y: 22, class: "dither-axis", "text-anchor": "middle" }, value),
      );
    }
    svg.append(svgEl("text", { x: left + plotWidth / 2, y: height - 10, class: "dither-axis dither-axis-heading", "text-anchor": "middle" }, "Wiki pages that cite or use this source"));

    parsed.forEach(({ row, used }, index) => {
      const y = top + index * rowHeight;
      const dateLabel = row.has_source_date ? `Published ${String(row.source_date).slice(0, 4)}` : "Publication date missing";
      const directLabel = row.has_url ? "direct record available" : "direct record missing";
      if (index % 2 === 0) svg.append(svgEl("rect", { x: 0, y: y - 10, width, height: rowHeight, class: "dither-row-band" }));
      svg.append(
        svgEl("text", { x: 8, y: y + 4, class: "dither-row-label" }, short(row.title, 50)),
        svgEl("text", { x: 8, y: y + 20, class: `dither-axis ${!row.has_url || !row.has_source_date ? "warning" : ""}` }, `${dateLabel} · ${directLabel}`),
      );
      const fill = !row.has_url ? `url(#${prefix}-dots-red)` : !row.has_source_date ? `url(#${prefix}-hatch-amber)` : `url(#${prefix}-dots-green)`;
      const bar = svgEl("rect", { x: left, y: y - 6, width: Math.max(3, x(used) - left), height: 20, rx: 2, fill, style: `animation-delay:${Math.min(index * 30, 330)}ms` });
      bar.setAttribute("aria-label", `${row.title}, used by ${used} wiki pages, ${dateLabel}, ${directLabel}`);
      bindMark(bar, stage, tooltip, [row.title, `Used by ${used} wiki page${used === 1 ? "" : "s"}`, `${dateLabel} · ${directLabel} · select to filter the table`], () => onSource(row));
      svg.append(bar, svgEl("text", { x: width - 10, y: y + 8, class: "dither-row-value", "text-anchor": "end" }, `${used} page${used === 1 ? "" : "s"}`));
    });
    return shell;
  }

  global.DashboardCharts = {
    overviewSignals,
    coverageHeatmap,
    capacityParity,
    monitoringTimeline,
    sourceReliance,
  };
}(window));
