"use strict";
const $ = (s) => document.querySelector(s),
  esc = (v) =>
    String(v ?? "").replace(
      /[&<>"']/g,
      (c) =>
        ({
          "&": "&amp;",
          "<": "&lt;",
          ">": "&gt;",
          '"': "&quot;",
          "'": "&#39;",
        })[c],
    );
const GH = "https://github.com/chirag-7/neural-data-bench",
  MODELS = ["gpt-5.6-sol", "gpt-6-sol", "gpt-6.1-sol"];
const COLORS = {
  "gpt-5.6-sol": "#9475aa",
  "gpt-6-sol": "#3c7fa4",
  "gpt-6.1-sol": "#c77735",
};
const NAMES = {
  "gpt-5.6-sol": "GPT-5.6 Sol",
  "gpt-6-sol": "GPT-6 Sol",
  "gpt-6.1-sol": "GPT-6.1 Sol",
  mountainsort5: "MountainSort5 · scheme 1",
  "yasa-eeg": "YASA · pretrained EEG",
  "pyriemann-ts-svm": "pyRiemann · TS-SVM",
  "pyriemann-aligned": "pyRiemann · aligned TS-SVM",
  "xdawn-tslr": "xDAWN · tangent-space LR",
  "canonical-posterior": "Posterior median · post-hoc audit",
  "canonical-mle": "Canonical MLE",
  "oasis-default": "OASIS · default AR1",
  "raw-calcium": "Raw calcium",
  midpoint: "Midpoint",
  "mriqc-rfc-2017": "MRIQC · archived 2017",
  deneux: "Deneux · archived",
  speiser: "Speiser · archived",
  friedrich: "Friedrich · archived",
  rupprecht: "Rupprecht · archived",
};
const CATEGORIES = {
  A: "Behavior & movement",
  B: "Spikes & sorting",
  C: "Calcium imaging",
  D: "Voltage & intracellular",
  E: "Population dynamics",
  F: "Neural encoding",
  G: "Intracortical BCI",
  H: "EEG, MEG & sleep",
  I: "Neuroimaging",
  J: "Anatomy & microscopy",
  K: "Cell & molecular data",
  L: "Statistical inference",
  M: "Cognition & control",
  N: "Analysis workflows",
};
const TITLES = {
  A09: "Social behavior classification",
  A14: "Missing-pose recovery",
  B01: "Extracellular spike sorting",
  C05: "Calcium-to-spike inference",
  D02: "Passive cell-response prediction",
  E01: "Population activity inference",
  F04: "Retinal image-response encoding",
  G01: "Cross-day finger-velocity decoding",
  H01: "EEG motor-imagery decoding",
  H02: "P300 target ranking",
  H08: "Sleep-stage classification",
  H16: "EEG artifact removal",
  I07: "fNIRS condition classification",
  I10: "MRI scan-quality classification",
  J08: "Microscopy puncta segmentation",
  K01: "Cell morphology classification",
  L04: "Place-cell count encoding",
  M04: "Cognitive parameter recovery",
  N05: "NWB file analysis",
};
const DATASETS = {
  A09: "CalMS21 · processed pose context",
  A14: "Rat7M · artificial HeadF gaps",
  B01: "MEArec · 10 s stationary simulation",
  C05: "Spikefinder · five preparations",
  D02: "Allen Cell Types · one passive cell",
  E01: "NLB · Maze, Area2, DMFC",
  F04: "Goldin 2022 · one retinal preparation",
  G01: "FALCON M2 · four recording days",
  H01: "PhysioNet EEGMMI · held-out subjects",
  H02: "Brain Invaders 2012 · 25 people",
  H08: "Sleep-EDF · eight first nights",
  H16: "EEGdenoiseNet · semisynthetic EOG mixtures",
  I07: "FRESH · tapping conditions",
  I10: "MRIQC · ABIDE → DS030",
  J08: "SynAPSeg · two held-out 2D fields",
  K01: "Allen Cell Types · ephys features",
  L04: "Kramer · one rat place cell",
  M04: "Synthetic two-choice Q-learning agents",
  N05: "Allen · one legacy NWB file",
};
let b01Metric = "primary";
let catalog,
  summary,
  records = [],
  excluded = [],
  selectedTask = "A09",
  selectedSlice = "",
  plotView = "graph",
  showAllRefs = false,
  showReferences = true,
  startAtZero = false,
  query = "",
  listMode = "measured",
  hiddenModels = new Set(),
  analysisClass = "historical_specialist";
const label = (x) =>
    NAMES[x] ||
    (x.startsWith("vassi-run-") ? "VASSI · archived " + x.slice(-2) : x),
  title = (e) => TITLES[e.id] || e.task;
const valid = (r) => r && Number.isFinite(r.score),
  rowsFor = (id) => records.filter((r) => r.benchmark_id === id),
  measured = (id) => rowsFor(id).some((r) => MODELS.includes(r.model));
const link = (url, text, cls = "") =>
  `<a class="${cls}" href="${esc(url)}" target="_blank" rel="noopener noreferrer">${text} ↗</a>`;
const route = (path, text, cls = "") =>
  `<a class="${cls}" href="#/${path}">${text}</a>`;
const fmt = (v) =>
  Number.isFinite(v)
    ? Math.abs(v) > 0 && Math.abs(v) < 0.00001
      ? v.toExponential(2)
      : v.toFixed(4)
    : "—";
function methodName(r) {
  if (r.display_name) return r.display_name;
  if (r.model === "task-baseline") {
    if (r.benchmark_id === "J08") return "StarDist · author archive";
    if (r.benchmark_id === "N05") return "Audited file reference";
    if (r.benchmark_id === "G01") return "FALCON-style ridge";
    if (r.benchmark_id === "H02") return "Shrinkage LDA · time bins";
    if (r.benchmark_id === "F04") return "PCA–Poisson GLM";
    return "Conventional task baseline";
  }
  return label(r.model);
}
function isSpecialist(r) {
  return (
    [
      "deneux",
      "speiser",
      "friedrich",
      "rupprecht",
      "oasis-default",
      "mountainsort5",
      "mriqc-rfc-2017",
      "yasa-eeg",
      "pyriemann-ts-svm",
      "pyriemann-aligned",
      "xdawn-tslr",
    ].includes(r.model) ||
    r.model.startsWith("vassi-run-") ||
    (r.benchmark_id === "J08" && r.model === "task-baseline")
  );
}
function evidence(r) {
  if (MODELS.includes(r.model)) return "General-model code";
  if (r.reference_type === "pretrained_specialist")
    return "Pretrained specialist";
  if (isSpecialist(r))
    return r.reference_type === "archived_predictions_rescored"
      ? "Archived specialist"
      : "Reproduced specialist";
  if (r.model === "canonical-posterior") return "Post-hoc mathematical audit";
  if (r.model === "canonical-mle") return "Frozen mathematical reference";
  if (r.benchmark_id === "N05") return "Deterministic correctness";
  return "Conventional baseline";
}
function best(rs) {
  const vs = rs.filter(valid);
  return vs.sort(
    (a, b) => (b.score - a.score) * (a.direction === "lower" ? -1 : 1),
  )[0];
}
function primary(id, sid) {
  const ref = summary.reference_envelopes.find(
    (r) => r.benchmark_id === id && r.slice_id === sid,
  );
  return (
    ref && rowsFor(id).find((r) => r.slice_id === sid && r.model === ref.model)
  );
}
function comparisons(id, sid) {
  const rs = rowsFor(id).filter((r) => r.slice_id === sid),
    specialists = rs.filter((r) => isSpecialist(r) && valid(r)),
    available = rs.filter((r) => !MODELS.includes(r.model) && valid(r)),
    specialist = best(specialists),
    reference = specialist || primary(id, sid) || best(available);
  return { rs, specialists, specialist, reference, frozen: primary(id, sid) };
}
function brief(id) {
  const ss = [
      ...new Set(
        rowsFor(id)
          .filter((r) => MODELS.includes(r.model))
          .map((r) => r.slice_id),
      ),
    ],
    rs = [];
  for (const model of MODELS) {
    const a = rowsFor(id).filter((r) => r.model === model && valid(r));
    if (a.length)
      rs.push({
        ...a[0],
        score: a.reduce((s, r) => s + r.score, 0) / a.length,
        line_limit_compliant: a.every((r) => r.line_limit_compliant !== false),
      });
  }
  const refs = ss.map((s) => comparisons(id, s).reference).filter(valid);
  return {
    models: rs,
    bestModel: best(rs),
    reference: refs.length
      ? {
          ...refs[0],
          score: refs.reduce((s, r) => s + r.score, 0) / refs.length,
          display_name:
            refs.length > 1 && new Set(refs.map((r) => r.model)).size > 1
              ? "Slice-equal inspected reference envelope"
              : undefined,
        }
      : null,
    nSlices: ss.length,
  };
}
function sidebar(family = "") {
  const counts = Object.fromEntries(
    catalog.families.map((f) => [
      f.code,
      catalog.entries.filter((e) => e.family_code === f.code && measured(e.id))
        .length,
    ]),
  );
  $("#sidebar").innerHTML =
    `<p class="side-label">Benchmark categories</p>${route("", '<span>All measured benchmarks</span><span class="count">' + summary.measured_tasks + "</span>", "side-link " + (!family ? "active" : ""))}${catalog.families.map((f) => route("category/" + f.code, `<span>${esc(CATEGORIES[f.code] || f.name)}</span><span class="count">${counts[f.code]}</span>`, "side-link " + (family === f.code ? "active" : ""))).join("")}<div class="side-note">Counts show tasks with model attempts. Each task has its own protocol and native metric.<br><br>${route("excluded", "Archived & excluded candidates →")}<br>${link(GH, "Source & audit trail")}</div>`;
}
function draw() {
  let p = location.hash.replace(/^#\/?/, "").split("/").filter(Boolean);
  if (p[0] === "task")
    p = ["benchmark", p[1], p[2] === "procedure" ? "evaluation" : p[2]];
  if (p[0] === "family") p = ["category", p[1]];
  if (p[0] === "trends") p = ["analysis"];
  let fam = p[0] === "category" ? p[1] : p[0] === "benchmark" ? p[1]?.[0] : "";
  sidebar(fam);
  document
    .querySelectorAll("[data-nav]")
    .forEach((a) =>
      a.classList.toggle(
        "active",
        a.dataset.nav ===
          (["models", "model"].includes(p[0])
            ? "models"
            : ["analysis", "methods"].includes(p[0])
              ? p[0]
              : "benchmarks"),
      ),
    );
  if (p[0] === "benchmark") benchmark(p[1], p[2] || "results");
  else if (p[0] === "models") modelsPage();
  else if (p[0] === "model") modelsPage(p[1]);
  else if (p[0] === "analysis") analysisPage();
  else if (p[0] === "methods") methodsPage();
  else if (p[0] === "excluded") excludedPage();
  else explorer(p[0] === "category" ? p[1] : "");
}
function mobileFilter(fam) {
  return `<div class="mobile-filter"><label class="screen-reader" for="mobile-category">Category</label><select id="mobile-category"><option value="">All categories</option>${catalog.families.map((f) => `<option value="${f.code}" ${fam === f.code ? "selected" : ""}>${esc(CATEGORIES[f.code] || f.name)}</option>`).join("")}</select></div>`;
}
function explorer(fam = "") {
  const f = catalog.families.find((f) => f.code === fam),
    es = catalog.entries.filter((e) => !fam || e.family_code === fam),
    scored = es.filter((e) => measured(e.id));
  if (scored.length && !scored.some((e) => e.id === selectedTask))
    selectedTask = scored[0].id;
  $("#app").innerHTML =
    `<p class="eyebrow">General models × specialist methods</p><h1>${f ? esc(CATEGORIES[fam] || f.name) : "Neuroscience benchmark results"}</h1><p class="lede">${f ? esc(f.tasks) : "Explore measured performance by task, compare general models with verified specialist references, and follow each result to its data and evaluation protocol. Models generate analysis code, which is then fitted locally."}</p>${mobileFilter(fam)}${!fam ? `<div class="stats"><div class="stat"><strong>${summary.measured_tasks}</strong><span>tasks with model attempts</span></div><div class="stat"><strong>${summary.measured_families} / ${catalog.families.length}</strong><span>categories represented</span></div><div class="stat"><strong>3</strong><span>general models evaluated</span></div><div class="stat"><strong>${summary.model_attempts}</strong><span>model × slice attempts</span></div></div>` : ""}${scored.length ? `<div class="toolbar"><label for="benchmark-picker" class="small">Explore a benchmark</label><select id="benchmark-picker">${scored.map((e) => `<option value="${e.id}" ${selectedTask === e.id ? "selected" : ""}>${e.id} · ${esc(title(e))}</option>`).join("")}</select>${route("benchmark/" + selectedTask, "Open benchmark →", "button secondary")}</div><div id="featured-chart"></div>` : `<div class="note">No model results are available in this category yet. Its candidates remain separate from measured benchmarks.</div>`}<div class="section-head"><h2>${f ? "Benchmarks in this category" : "Benchmark directory"}</h2><span class="small">Native scores · no mixed-metric ranking</span></div><div class="toolbar"><input id="search" class="search" aria-label="Search benchmarks" placeholder="Search tasks, datasets or methods…" value="${esc(query)}"><select id="list-mode" aria-label="Result availability"><option value="measured" ${listMode === "measured" ? "selected" : ""}>Measured results</option><option value="all" ${listMode === "all" ? "selected" : ""}>All active candidates</option></select><a class="download-link" href="data/measurements.csv" download>Download results ↓</a></div><div id="benchmark-directory"></div><p class="small" style="margin-top:17px">† Code-line format deviation; see strict-format analysis. A published task score is conditional on its frozen slice and procedure. “Best verified specialist” means the highest matching score among inspected references; it does not establish current global SOTA. ${route("methods", "Read the methodology →")}</p>`;
  if ($("#mobile-category"))
    $("#mobile-category").onchange = (e) => {
      location.hash = e.target.value ? "#/category/" + e.target.value : "#/";
    };
  if ($("#benchmark-picker"))
    $("#benchmark-picker").onchange = (e) => {
      selectedTask = e.target.value;
      selectedSlice = "";
      explorer(fam);
    };
  $("#search").oninput = (e) => {
    query = e.target.value;
    directory(es);
  };
  $("#list-mode").onchange = (e) => {
    listMode = e.target.value;
    directory(es);
  };
  directory(es);
  if (scored.length) renderChart("#featured-chart", selectedTask, true);
}
function directory(es) {
  const q = query.toLowerCase(),
    filtered = es.filter(
      (e) =>
        (listMode === "all" || measured(e.id)) &&
        (!q ||
          JSON.stringify([
            e.id,
            title(e),
            DATASETS[e.id],
            e.resource,
            e.data,
            e.specialist_baselines,
          ])
            .toLowerCase()
            .includes(q)),
    );
  $("#benchmark-directory").innerHTML =
    `<div class="table-panel table-wrap"><table><thead><tr><th>Benchmark / dataset</th><th>Category</th><th>Best measured general model</th><th>Best verified specialist / reference</th><th>Metric</th></tr></thead><tbody>${
      filtered
        .map((e) => {
          const b = brief(e.id);
          return `<tr><td>${route("benchmark/" + e.id, esc(title(e)), "bench-name")}<span class="bench-sub">${e.id} · ${esc(DATASETS[e.id] || e.resource)}</span></td><td><span class="small">${esc(CATEGORIES[e.family_code])}</span></td><td>${b.bestModel ? `<span class="number">${fmt(b.bestModel.score)}</span><span class="score-caption">${label(b.bestModel.model)}${b.bestModel.line_limit_compliant === false ? " †" : ""}${b.nSlices > 1 ? " · mean of " + b.nSlices + " slices" : ""}</span>` : '<span class="badge">Not run</span>'}</td><td>${b.reference ? `<span class="number">${fmt(b.reference.score)}</span><span class="score-caption">${esc(methodName(b.reference))}${isSpecialist(b.reference) ? "" : " · baseline/reference"}</span>` : '<span class="small">Unverified</span>'}</td><td>${b.bestModel ? `<span class="small">${esc(b.bestModel.metric)} ${b.bestModel.direction === "higher" ? "↑" : "↓"}</span>` : "—"}</td></tr>`;
        })
        .join("") ||
      '<tr><td colspan="5" class="empty">No matching benchmarks. Try another category or result-availability filter.</td></tr>'
    }</tbody></table></div>`;
}
function referenceSelection(c) {
  const selected = [];
  const add = (r) => {
    if (r && !selected.some((v) => v.model === r.model)) selected.push(r);
  };
  add(c.reference);
  add(c.frozen);
  const baseline = c.rs.find((r) => r.model === "task-baseline");
  if (valid(baseline)) add(baseline);
  if (showAllRefs)
    for (const r of c.rs)
      if (!MODELS.includes(r.model) && !r.model.startsWith("vassi-run-"))
        add(r);
  return selected;
}
function renderChart(target, id, compact = false) {
  const e = catalog.entries.find((e) => e.id === id),
    all = rowsFor(id),
    slices = [
      ...new Set(
        all.filter((r) => MODELS.includes(r.model)).map((r) => r.slice_id),
      ),
    ];
  if (!slices.includes(selectedSlice)) selectedSlice = slices[0];
  let c = comparisons(id, selectedSlice);
  if (id === "B01" && b01Metric === "all-event-f1") {
    const convert = (r) =>
      r
        ? {
            ...r,
            score: r.posthoc_secondary_metrics?.all_event_f1,
            metric: "All-output event F1 (post-hoc)",
            direction: "higher",
          }
        : r;
    c = {
      ...c,
      rs: c.rs.map(convert),
      specialists: c.specialists.map(convert),
      specialist: convert(c.specialist),
      reference: convert(c.reference),
      frozen: convert(c.frozen),
    };
  }
  const native = c.rs.find(valid);
  if (!native) {
    $(target).innerHTML =
      '<p class="empty">No valid measurements for this slice.</p>';
    return;
  }
  const refs = showReferences ? referenceSelection(c) : [],
    generals = MODELS.filter((m) => !hiddenModels.has(m)).map(
      (m) => c.rs.find((r) => r.model === m) || { model: m, status: "missing" },
    );
  $(target).innerHTML =
    `<div class="chart-card"><div class="chart-head"><div><h2>${compact ? route("benchmark/" + id, esc(title(e))) : esc(title(e))}</h2><p class="small">${esc(native.metric)} · ${native.direction === "higher" ? "higher" : "lower"} is better · ${id}</p></div><div class="segmented" role="group" aria-label="Chart or table"><button data-view="graph" class="${plotView === "graph" ? "active" : ""}">Graph</button><button data-view="table" class="${plotView === "table" ? "active" : ""}">Table</button></div></div><div class="plot-controls">${id === "B01" ? `<label>Plot metric <select id="metric-picker"><option value="primary" ${b01Metric === "primary" ? "selected" : ""}>Frozen mean GT-unit accuracy</option><option value="all-event-f1" ${b01Metric === "all-event-f1" ? "selected" : ""}>All-output event F1 · post-hoc</option></select></label>` : ""}<label>Evaluation slice <select id="slice-picker">${slices.map((s) => `<option value="${s}" ${s === selectedSlice ? "selected" : ""}>${id === "C05" ? "Preparation " + s : s}</option>`).join("")}</select></label><label><input id="show-ref" type="checkbox" ${showReferences ? "checked" : ""}>Include references</label><label><input id="all-ref" type="checkbox" ${showAllRefs ? "checked" : ""}>Show additional references</label>${plotView === "graph" ? `<label class="right"><input id="zero-axis" type="checkbox" ${startAtZero ? "checked" : ""}>Line axis starts at zero</label>` : ""}</div>${plotView === "graph" ? `${referenceCards(refs, c.frozen)}<p class="plot-reading-key"><span class="solid-key"></span>Solid connected points = general models. <span class="dashed-key"></span>Dashed horizontal lines = specialists. <span class="dotted-key"></span>Dotted lines = other references.</p><div class="chart-grid"><section><p class="chart-label">Performance across model versions</p>${linePlot(generals, refs, native.direction, c.specialists)}</section><section><p class="chart-label">General models and specialist references</p>${barPlot([...generals, ...refs], native.direction)}</section></div><div class="legend">${MODELS.map((m) => `<label><input type="checkbox" data-model="${m}" ${!hiddenModels.has(m) ? "checked" : ""}><i class="dot" style="background:${COLORS[m]}"></i>${label(m)}</label>`).join("")}${refs.map((r, i) => `<span><i class="dash" style="border-color:${refColor(r, i)}"></i>${esc(methodName(r))} · ${fmt(r.score)}</span>`).join("")}</div>` : `<div class="table-wrap">${scoreTable(c.rs)}</div>`}<div class="chart-foot">${chartCaveat(id, c)} ${compact ? route("benchmark/" + id, "Inspect protocol, sources and all scores →") : ""}<br>Connected points show version order, not elapsed time or a compute scaling law. Line axes ${startAtZero ? "include zero" : "adapt to the score range; inspect the ticks"}; bars include zero. One generated program per model/task.</div></div>`;
  $(target)
    .querySelectorAll?.("[data-view]")
    .forEach(
      (b) =>
        (b.onclick = () => {
          plotView = b.dataset.view;
          renderChart(target, id, compact);
        }),
    );
  if ($("#metric-picker"))
    $("#metric-picker").onchange = (ev) => {
      b01Metric = ev.target.value;
      renderChart(target, id, compact);
    };
  $("#slice-picker").onchange = (ev) => {
    selectedSlice = ev.target.value;
    renderChart(target, id, compact);
  };
  $("#show-ref").onchange = (ev) => {
    showReferences = ev.target.checked;
    renderChart(target, id, compact);
  };
  $("#all-ref").onchange = (ev) => {
    showAllRefs = ev.target.checked;
    renderChart(target, id, compact);
  };
  if ($("#zero-axis"))
    $("#zero-axis").onchange = (ev) => {
      startAtZero = ev.target.checked;
      renderChart(target, id, compact);
    };
  document.querySelectorAll("[data-model]").forEach(
    (b) =>
      (b.onchange = () => {
        b.checked
          ? hiddenModels.delete(b.dataset.model)
          : hiddenModels.add(b.dataset.model);
        renderChart(target, id, compact);
      }),
  );
}
function refColor(r, i = 0) {
  return isSpecialist(r)
    ? ["#24796d", "#5f9e75", "#688c5e", "#4b806b"][i % 4]
    : r.model === "canonical-posterior"
      ? "#8e6ab0"
      : "#8a939c";
}
function referenceCards(refs, frozen) {
  if (!refs.length)
    return '<p class="reference-empty">No reference lines are shown.</p>';
  return `<div class="reference-strip" aria-label="Named reference scores">${refs
    .filter(valid)
    .map(
      (r, i) =>
        `<div class="reference-card ${isSpecialist(r) ? "specialist" : "baseline"}"><div class="reference-kicker"><span class="reference-key" style="color:${refColor(r, i)}">R${i + 1} · ${isSpecialist(r) ? "Specialist · dashed line" : "Other reference · dotted line"}</span>${r.model === frozen?.model ? '<span class="reference-policy">Primary comparator</span>' : ""}</div><div class="reference-value"><span>${esc(methodName(r))}</span><strong>${fmt(r.score)}</strong></div><span class="reference-policy">${esc(evidence(r))}</span></div>`,
    )
    .join("")}</div>`;
}
function linePlot(general, refs, direction, specialists = []) {
  let vals = [...general, ...refs].filter(valid).map((r) => r.score);
  if (showReferences)
    vals.push(
      ...specialists
        .filter((r) => r.model.startsWith("vassi-run-"))
        .map((r) => r.score),
    );
  if (!vals.length) return '<p class="empty">No finite scores.</p>';
  const shown = refs.filter(valid),
    plotHeight = Math.max(190, shown.length * 38 + 15),
    top = 40,
    bottom = top + plotHeight;
  let lo = Math.min(...vals),
    hi = Math.max(...vals),
    padding = Math.max((hi - lo) * 0.16, Math.abs(hi) * 0.025, 1e-6);
  lo = startAtZero ? Math.min(0, lo - padding) : lo - padding;
  hi += padding;
  const x = (i) => 88 + 125 * i,
    y = (v) => bottom - ((v - lo) / (hi - lo)) * plotHeight;
  const labels = shown
    .map((r, i) => ({ r, i, ideal: y(r.score), position: y(r.score) }))
    .sort((a, b) => a.ideal - b.ideal);
  for (let i = 0; i < labels.length; i++)
    labels[i].position = Math.max(
      top + 10,
      labels[i].ideal,
      i ? labels[i - 1].position + 38 : top + 10,
    );
  if (labels.length && labels.at(-1).position > bottom - 10) {
    labels.at(-1).position = bottom - 10;
    for (let i = labels.length - 2; i >= 0; i--)
      labels[i].position = Math.min(
        labels[i].position,
        labels[i + 1].position - 38,
      );
  }
  const labelPosition = new Map(labels.map((v) => [v.i, v.position]));
  let path = "",
    prior = false;
  for (const r of general) {
    if (valid(r)) {
      path +=
        (prior ? " L" : " M") + x(MODELS.indexOf(r.model)) + " " + y(r.score);
      prior = true;
    } else prior = false;
  }
  const archives = specialists.filter((r) => r.model.startsWith("vassi-run-"));
  return `<svg class="plot line-plot" viewBox="0 0 570 ${bottom + 68}" role="img" aria-label="Model-version line chart with named specialist reference lines"><title>Solid connected points: general model scores. Horizontal dashed lines: specialists. Dotted lines: other references. ${direction} is better.</title>${[
    0, 0.25, 0.5, 0.75, 1,
  ]
    .map((t) => {
      const v = lo + t * (hi - lo);
      return `<line x1="65" x2="365" y1="${y(v)}" y2="${y(v)}" stroke="#e5ebef"/><text x="56" y="${y(v) + 4}" text-anchor="end">${fmt(v)}</text>`;
    })
    .join(
      "",
    )}${archives.length > 1 && showReferences ? `<rect x="65" width="300" y="${y(Math.max(...archives.map((r) => r.score)))}" height="${Math.abs(y(Math.min(...archives.map((r) => r.score))) - y(Math.max(...archives.map((r) => r.score))))}" fill="#24796d" opacity=".12"><title>Range of 20 archived VASSI runs; not independent tasks</title></rect>` : ""}${shown
    .map((r, i) => {
      const yy = y(r.score),
        ly = labelPosition.get(i),
        name = methodName(r),
        short = name.length > 24 ? name.slice(0, 23) + "…" : name;
      return `<g class="direct-reference-label"><line x1="65" x2="365" y1="${yy}" y2="${yy}" stroke="${refColor(r, i)}" stroke-width="2" stroke-dasharray="${isSpecialist(r) ? "7 4" : "2 5"}"/><path d="M365 ${yy} L376 ${yy} L389 ${ly}" fill="none" stroke="${refColor(r, i)}" stroke-width="1"/><text x="395" y="${ly - 4}" class="reference-label-name" style="fill:${refColor(r, i)}">R${i + 1} · ${esc(short)}</text><text x="395" y="${ly + 10}" class="reference-label-score">${fmt(r.score)} · ${isSpecialist(r) ? "specialist" : "other reference"}</text><title>R${i + 1}: ${esc(name)}, ${fmt(r.score)}. ${evidence(r)}</title></g>`;
    })
    .join(
      "",
    )}<path d="${path}" fill="none" stroke="#547b97" stroke-width="2"/>${general
    .map((r) => {
      const xx = x(MODELS.indexOf(r.model));
      return `${valid(r) ? `<circle cx="${xx}" cy="${y(r.score)}" r="5.5" fill="${COLORS[r.model]}"><title>${label(r.model)}: ${fmt(r.score)}</title></circle><text class="value-label" x="${xx}" y="${y(r.score) - 13}" text-anchor="middle">${fmt(r.score)}${r.line_limit_compliant === false ? "†" : ""}</text>` : `<text x="${xx}" y="${top + plotHeight / 2}" text-anchor="middle">Failed</text>`}<text x="${xx}" y="${bottom + 29}" text-anchor="middle">${label(r.model).replace("GPT-", "")}</text>`;
    })
    .join(
      "",
    )}<text x="215" y="${bottom + 58}" text-anchor="middle">General model version</text></svg>`;
}
function barPlot(rs, direction) {
  const vals = rs.filter(valid).map((r) => r.score);
  let lo = Math.min(0, ...vals),
    hi = Math.max(0, ...vals);
  if (hi === lo) hi = lo + 1;
  const scale = (v) => 195 + ((v - lo) / (hi - lo)) * 300,
    zero = scale(0),
    height = rs.length * 42 + 50;
  const ticks = [...new Set([lo, (lo + hi) / 2, 0, hi])].sort((a, b) => a - b);
  return `<svg class="plot" viewBox="0 0 570 ${height}" role="img" aria-label="Bar chart including general models and named specialist or baseline scores"><title>Native metric; ${direction} is better. Bar axis includes zero.</title>${ticks
    .map((v) => {
      return `<line x1="${scale(v)}" x2="${scale(v)}" y1="5" y2="${height - 32}" stroke="${v === 0 ? "#b5c2cc" : "#e9edf0"}"/><text x="${scale(v)}" y="${height - 10}" text-anchor="middle">${fmt(v)}</text>`;
    })
    .join("")}${rs
    .map((r, i) => {
      const yy = 12 + i * 42;
      return `<text x="181" y="${yy + 15}" text-anchor="end">${esc(methodName(r))}${r.line_limit_compliant === false ? "†" : ""}</text>${valid(r) ? `<rect x="${Math.min(zero, scale(r.score))}" y="${yy}" width="${Math.max(0.8, Math.abs(scale(r.score) - zero))}" height="23" fill="${COLORS[r.model] || refColor(r, i)}"><title>${esc(methodName(r))}: ${fmt(r.score)} · ${evidence(r)}</title></rect><text class="value-label" x="560" y="${yy + 15}" text-anchor="end">${fmt(r.score)}</text>` : `<text x="360" y="${yy + 15}">Failed</text>`}`;
    })
    .join("")}</svg>`;
}
function chartCaveat(id, c) {
  let text = c.specialist
    ? "Dashed horizontal lines show the named specialist scores above and beside the plot. "
    : c.reference
      ? "This task has a conventional or mathematical reference; a strongest specialist result is not established. "
      : "No matched reference verified. ";
  if (c.specialist && c.specialists.length > 1)
    text +=
      "The highest inspected specialist point score is a test-selected descriptive envelope, not a prospective model-selection result. ";
  if (id === "A09")
    text +=
      "VASSI uses richer full-frame inputs/training; its 20-run range is shaded. Preselected run00 remains the primary scientific comparator. ";
  if (id === "C05")
    text +=
      "Historical 2017 archives have different tuning histories; preparation1 was development evidence. ";
  if (id === "M04")
    text +=
      "All three posterior estimators nearly agree; tiny differences reflect numerical quadrature. The post-hoc posterior reference and frozen MLE optimize different objectives. ";
  if (id === "N05")
    text +=
      "One file, 61 deterministic fields, shared with D02; the reference is correct by construction. ";
  if (id === "B01")
    text +=
      "One 10-second stationary simulation. The all-output event F1 sensitivity counts extra spikes: GPT-6 0.5998, MountainSort5 0.9621. Select it above to inspect both plots. This diagnostic was added post hoc; directory and macro statistics retain the frozen primary metric. ";
  if (id === "J08")
    text +=
      "Two held-out fields × five human raters; archived StarDist optimization history differs. ";
  return (
    esc(text) +
    "†Formatting deviations remain visible and are excluded from strict subsets."
  );
}
function scoreTable(rs) {
  return `<table><thead><tr><th>Method</th><th>Score</th><th>Evidence</th><th>Execution seconds</th><th>Details</th></tr></thead><tbody>${rs.map((r) => `<tr><td><span class="dot" style="background:${COLORS[r.model] || refColor(r)}"></span> ${esc(methodName(r))}${r.line_limit_compliant === false ? " †" : ""}</td><td>${valid(r) ? fmt(r.score) : "Failed"}</td><td><span class="badge ${isSpecialist(r) ? "verified" : MODELS.includes(r.model) ? "general" : ""}">${evidence(r)}</span></td><td>${Number.isFinite(r.seconds) ? r.seconds.toFixed(2) : "Unavailable"}</td><td class="wrap small">${r.status === "failed" ? esc((r.reason || "Execution failed").trim().split("\n").pop()) : r.scoring_diagnostics ? esc(`${r.posthoc_secondary_metrics ? "All-output event F1 " + fmt(r.posthoc_secondary_metrics.all_event_f1) + " (post-hoc); " : ""}${r.scoring_diagnostics.n_predicted_units} predicted units; ${(r.scoring_diagnostics.redundant_unit_ids || []).length} redundant; ${(r.scoring_diagnostics.false_positive_unit_ids || []).length} false-positive units`) : r.model === "canonical-posterior" ? "Added post hoc; objective-aligned audit" : r.line_limit_compliant === false ? "Unchanged format deviation" : "See protocol and prediction artifacts"}</td></tr>`).join("")}</tbody></table>`;
}
function benchmark(id, tab = "results") {
  const e = catalog.entries.find((e) => e.id === id);
  if (!e) {
    $("#app").innerHTML =
      "<h1>Benchmark unavailable</h1><p>It may have been archived. " +
      route("excluded", "Inspect exclusion decisions →") +
      "</p>";
    return;
  }
  const b = brief(id);
  $("#app").innerHTML =
    `<p class="breadcrumb">${route("", "Benchmarks")} / ${route("category/" + e.family_code, esc(CATEGORIES[e.family_code]))} / ${id}</p><p class="eyebrow">${id} · ${esc(CATEGORIES[e.family_code])}</p><h1>${esc(title(e))}</h1><p class="lede">${esc(e.executed_slice || e.resource)}</p><div class="detail-top"><span class="badge ${measured(id) ? "verified" : ""}">${measured(id) ? "Measured exploratory protocol" : "Candidate · not run"}</span><span class="badge">T3 · generated analysis code</span><span class="badge">Current global SOTA unverified</span></div><nav class="tabs" aria-label="Benchmark information">${[
      ["results", "Results"],
      ["evaluation", "Evaluation details"],
      ["sources", "Data & sources"],
    ]
      .map(([v, t]) =>
        route("benchmark/" + id + "/" + v, t, tab === v ? "active" : ""),
      )
      .join("")}</nav><div id="benchmark-content"></div>`;
  if (tab === "results") {
    if (!measured(id)) {
      $("#benchmark-content").innerHTML =
        `<div class="note"><strong>No model results.</strong> ${esc(e.admission_reason)}</div>${link(GH + "/blob/main/" + e.admission_evidence_file, "Admission evidence")}`;
      return;
    }
    const ref = b.reference;
    $("#benchmark-content").innerHTML =
      `<div class="detail-summary"><div class="reference-box"><span class="small">Best measured general model${b.nSlices > 1 ? " · slice-equal mean" : ""}</span><strong>${fmt(b.bestModel?.score)}</strong><p>${b.bestModel ? label(b.bestModel.model) + (b.bestModel.line_limit_compliant === false ? " · format deviation" : "") : "All attempts failed"}</p></div><div class="reference-box specialist"><span class="small">${ref && isSpecialist(ref) ? "Best verified specialist in inspected set" : "Available baseline / reference"}</span><strong>${fmt(ref?.score)}</strong><p>${ref ? esc(methodName(ref)) : "Not established"} · training and selection histories differ</p></div></div><div id="detail-chart"></div><details><summary>What can this result establish?</summary><p>${esc(e.limitations)}</p><p>This measures a model-generated numerical analysis procedure. One submission per model; public-data contamination and provider checkpoint resolution remain unverified. Specialist training, feature access and tuning budgets can differ. Missing results are unknown, not zero.</p></details><div class="actions"><a class="button secondary" href="data/${id}.json" download>Detailed records ↓</a>${link(GH + "/tree/main/experiments/" + id, "Frozen code & protocol", "button secondary")}${link(GH + "/tree/main/results/predictions/" + id, "Predictions", "button secondary")}</div>`;
    renderChart("#detail-chart", id);
  } else if (tab === "evaluation") {
    $("#benchmark-content").innerHTML =
      `<div class="doc-grid"><section class="doc-panel"><h2>Evaluation contract</h2><dl class="kv"><dt>Input</dt><dd>${esc(e.data)}</dd><dt>Executed slice</dt><dd>${esc(e.executed_slice || "Not yet defined")}</dd><dt>Ground truth</dt><dd>${esc(e.ground_truth)}</dd><dt>Metric / split</dt><dd>${esc(e.recommended_metrics)}<br>${esc(e.recommended_split)}</dd></dl></section><section class="doc-panel"><h2>Validity and procedure</h2><p>${esc(e.limitations)}</p><p>${esc(e.admission_reason)}</p><div class="link-list">${measured(id) ? link(GH + "/blob/main/experiments/" + id + (id === "C05" ? "/phase2-protocol.md" : "/protocol.md"), "Exact frozen protocol") : ""}${link(GH + "/blob/main/benchmarks/" + e.family_code + "/" + id + "/worklog.md", "Steps actually completed")}${measured(id) ? link(GH + "/blob/main/experiments/" + id + (["C05", "M04"].includes(id) ? "/generation-provenance.json" : "/run-spec.json"), "Frozen input and prompt identities") : ""}${link(GH + "/blob/main/" + e.admission_evidence_file, "Admission assessment")}</div></section></div>`;
  } else {
    $("#benchmark-content").innerHTML =
      `<div class="doc-panel"><h2>Primary data and method sources</h2><p>Sources retain their original terms. A source association is not a claim that every asset was acquired or every paper fully reviewed. Measured-task manifests describe the actual files used.</p><div class="link-list">${e.source_urls.map((u, i) => link(u, esc(u.replace(/^https?:\/\//, "")))).join("")}</div><div class="actions">${link(GH + "/tree/main/" + (measured(id) ? "experiments/" + id : "benchmarks/" + e.family_code + "/" + id), "Source manifests and preparation")}${link(GH + "/blob/main/benchmarks/" + e.family_code + "/" + id + "/data.json", "Data and rights assessment")}</div></div>`;
  }
}
function modelsPage(model) {
  const summaries = summary.model_summaries.filter(
    (s) => !model || s.model === model,
  );
  $("#app").innerHTML =
    `<p class="eyebrow">Model comparisons</p><h1>${model ? label(model) : "Models in the experiment"}</h1><p class="lede">Exact requested hosted model IDs, one high-reasoning no-tool code submission per task. Same explicit task prompt; full provider context and internal checkpoint identity are not independently observable.</p><div class="model-cards">${summaries.map((s) => route("model/" + s.model, `<h2>${label(s.model)}</h2><strong>${s.valid} / ${s.attempted}</strong><p>Numerically valid evaluation slices</p><p>${s.strict_format_valid} strict-format valid · ${s.failed} failed</p>`, "model-card")).join("")}</div><div class="section-head"><h2>Native scores by task</h2><span class="small">Slice-equal mean where multiple slices exist</span></div><div class="table-panel table-wrap"><table><thead><tr><th>Benchmark</th>${MODELS.map((m) => `<th>${label(m)}</th>`).join("")}<th>Best verified specialist / reference</th><th>Metric</th></tr></thead><tbody>${summary.measured_task_ids
      .map((id) => {
        const e = catalog.entries.find((e) => e.id === id);
        if (!e) return "";
        const b = brief(id);
        return `<tr><td>${route("benchmark/" + id, esc(title(e)))}<span class="bench-sub">${id} · ${b.nSlices} slice${b.nSlices === 1 ? "" : "s"}</span></td>${MODELS.map((m) => `<td>${fmt(b.models.find((r) => r.model === m)?.score)}${b.models.find((r) => r.model === m)?.line_limit_compliant === false ? " †" : ""}</td>`).join("")}<td>${fmt(b.reference?.score)}<span class="score-caption">${b.reference ? esc(methodName(b.reference)) : "Unknown"}</span></td><td class="small">${esc(b.bestModel?.metric || "No valid score")}</td></tr>`;
      })
      .join(
        "",
      )}</tbody></table></div><p class="note">These native metrics cannot be averaged into a universal model ranking. Reliability, directional improvement and reference comparisons have separate denominators. ${route("analysis", "Explore the analysis →")}</p>`;
}
function analysisPage() {
  const classes = [
    ...new Set(summary.reference_envelopes.map((r) => r.reference_class)),
  ];
  if (!classes.includes(analysisClass)) analysisClass = classes[0];
  $("#app").innerHTML =
    `<p class="eyebrow">Cross-task analysis</p><h1>Where do models improve?</h1><p class="lede">Track point-score changes and reference comparisons while keeping task, family, failure and evidence-class denominators visible.</p><div class="doc-panel" style="margin-top:26px"><h2>Comparison with references</h2><div class="toolbar"><label for="reference-class" class="small">Reference evidence</label><select id="reference-class">${classes.map((c) => `<option value="${c}" ${c === analysisClass ? "selected" : ""}>${esc(c.replaceAll("_", " "))}</option>`).join("")}</select></div><div class="table-wrap"><table><thead><tr><th>Model</th><th>Point wins / slices</th><th>Lost / tied / failed</th><th>Tasks / families</th><th>Family-equal win fraction</th><th>Strict-format wins / eligible slices</th></tr></thead><tbody>${summary.model_summaries
      .map((s) => {
        const c = s.reference_class_summaries[analysisClass],
          a = c?.exploratory,
          b = c?.strict;
        return `<tr><td>${label(s.model)}</td><td>${a?.wins ?? 0} / ${a?.n_slice_comparisons ?? 0}</td><td>${a?.losses ?? 0} / ${a?.numerical_ties ?? 0} / ${a?.failed_or_missing ?? 0}</td><td>${a?.n_tasks ?? 0} / ${a?.n_families ?? 0}</td><td>${fmt(a?.family_equal_win_fraction)}</td><td>${b?.wins ?? 0} / ${b?.n_slice_comparisons ?? 0}</td></tr>`;
      })
      .join(
        "",
      )}</tbody></table></div><p class="small">Primary scientific comparator selection follows the frozen/reference policy, which can differ from the best-inspected envelope displayed on benchmark plots. No current-SOTA or matched-total-effort superiority claim.</p></div><div class="doc-panel" style="margin-top:22px"><h2>Model-version changes</h2><div class="table-wrap"><table><thead><tr><th>Pair</th><th>Improved / slices</th><th>Declined</th><th>Ties</th><th>Failed / missing</th><th>Task / family count</th><th>Family-equal improvement fraction</th></tr></thead><tbody>${summary.paired_macro_summaries
      .map((p) => {
        const a = p.exploratory;
        return `<tr><td>${label(p.older)} → ${label(p.newer)}</td><td>${a.wins} / ${a.n_slice_comparisons}</td><td>${a.losses}</td><td>${a.numerical_ties}</td><td>${a.failed_or_missing}</td><td>${a.n_tasks} / ${a.n_families}</td><td>${fmt(a.family_equal_win_fraction)}</td></tr>`;
      })
      .join(
        "",
      )}</tbody></table></div><p class="small">M04 quadrature differences and N05 deterministic correctness are excluded from this progress aggregate. The aggregate includes synthetic B01 and semisynthetic repair tasks. Failures remain in the denominator. New datasets or simulations are not automatically independent biological replications.</p></div><details open><summary>How aggregation works</summary><p>For descriptive directional win fractions, average slices within task, tasks within category, then categories equally. Incompatible native metric deltas are never averaged. A numerical difference above1e−9 is a point win, not statistical significance or a practical-equivalence threshold. One generated program per version, convenience-selected tasks and public labels prevent causal scaling conclusions.</p></details><div class="actions"><a class="button secondary" href="data/summary.json" download>All derived statistics ↓</a><a class="button secondary" href="data/measurements.csv" download>Measurements ↓</a>${link(GH + "/blob/main/analysis/findings.md", "Interpretation & limitations", "button secondary")}</div>`;
  $("#reference-class").onchange = (e) => {
    analysisClass = e.target.value;
    analysisPage();
  };
}
function methodsPage() {
  $("#app").innerHTML =
    `<p class="eyebrow">Methods & data</p><h1>Trace every result.</h1><p class="lede">A benchmark is an exact input, target, split, scorer and model procedure. The broader neuroscience evidence map remains separate from the measured results explorer.</p><div class="doc-grid"><section class="doc-panel"><h2>What is measured</h2><p>T3: a single general-model code submission followed by local numerical execution. Models use general scientific libraries; specialist packages and pretrained assets are separate references. This does not directly measure native raw-signal understanding or full autonomous lab workflows.</p><p>Exact prompts, frozen data/code hashes, submitted programs, generation usage/tool counts, predictions and errors are retained. Current general models: GPT-5.6 Sol, GPT-6 Sol and GPT-6.1 Sol.</p></section><section class="doc-panel"><h2>Specialist evidence</h2><p>Named specialist methods appear on line charts and bar plots wherever verified matching predictions exist. Archived specialist masks/predictions, local specialist reproductions, conventional baselines and mathematical audits are identified separately.</p><p>The highest inspected point score is a descriptive test-selected envelope. It cannot certify the current global best, comparable training inputs or equal tuning effort. Published scores on a different split are not inserted into these plots.</p></section></div><div class="doc-grid"><section class="doc-panel"><h2>Coverage and exclusions</h2><p>The historical evidence map covers 114 task-resource associations across 14 families. The active catalog is pruned when a reusable endpoint, data rights, release or scorer is unresolved. Concrete high-effort tasks remain candidates, with missing results shown as unknown.</p><p>Pruning does not prove exhaustive coverage. Removed candidates retain their decision trail and reactivation requirements. Broad clinical, causal, control and mechanistic perspectives still have gaps.</p>${route("excluded", "Inspect archived candidates →")}</section><section class="doc-panel"><h2>Validity controls</h2><p>Biological grouping, human vs synthetic truth, adaptation policy and reference information access are explicit per task. Source identities, acquired-file/buffer hashes and scorer checks are recorded. Failures and formatting deviations stay visible.</p><p>Small biological samples, public-label contamination, unequal specialist histories and one-generation uncertainty remain. No neuron/frame pseudo-replication intervals or universal mixed-metric capability score.</p></section></div><div class="link-list">${[
      ["README.md", "Main research plan and status"],
      ["docs/release-v06.md", "Current release report"],
      ["docs/taxonomy.md", "Taxonomy and coverage justification"],
      ["docs/methodology.md", "Evaluation methodology"],
      ["docs/macro-analysis-plan.md", "Macro analysis and weighting"],
      ["docs/prior-work.md", "Related benchmarks and literature"],
      ["literature/README.md", "Sources, searches and review depth"],
      ["registry/admission-decisions.json", "Every admission decision"],
      ["registry/current-best.json", "Current-best verification ledger"],
      ["docs/reproduce.md", "Reproduce the experiments"],
    ]
      .map(([p, t]) => link(GH + "/blob/main/" + p, t))
      .join("")}</div>`;
}
function excludedPage() {
  $("#app").innerHTML =
    `<p class="eyebrow">Quality control / archive</p><h1>Archived benchmark candidates</h1><p class="lede">These entries are removed from the active benchmark catalog. The reason and evidence remain inspectable; a resource can be reconsidered when its release, rights or evaluation contract is resolved.</p><div class="note">No measured task is removed because a model performed poorly. Setup difficulty alone is not evidence of bad data.</div><div class="table-panel table-wrap"><table><thead><tr><th>Candidate</th><th>Reason for archival</th><th>Reactivation requirement</th></tr></thead><tbody>${excluded.map((e) => `<tr><td>${esc(e.id || e.benchmark_id)}<span class="bench-sub">${esc(e.resource || e.task || "")}</span></td><td class="wrap">${esc(e.reason || e.rationale || "See source review")}</td><td class="wrap small">${esc(e.reactivation_requirements || e.reactivation_requirement || "Resolve the documented data, release or protocol gate; freeze a separate execution contract.")}</td></tr>`).join("") || '<tr><td colspan="3">See the repository exclusion ledger.</td></tr>'}</tbody></table></div><div class="actions">${link(GH + "/blob/main/literature/active-pruning-v05.md", "Review rationale", "button secondary")}${link(GH + "/blob/main/registry/catalog-history/v04-114.json", "Historical full evidence map", "button secondary")}</div>`;
}
window.addEventListener("hashchange", () => {
  selectedSlice = "";
  draw();
  window.scrollTo({ top: 0 });
});
Promise.all([
  fetch("data/catalog.json").then((r) => r.json()),
  fetch("data/summary.json").then((r) => r.json()),
  fetch("data/measurements.jsonl").then((r) => r.text()),
  fetch("data/exclusions.json")
    .then((r) => (r.ok ? r.json() : []))
    .catch(() => []),
])
  .then(([c, s, t, x]) => {
    catalog = c;
    summary = s;
    records = t
      .trim()
      .split("\n")
      .filter(Boolean)
      .map((v) => JSON.parse(v));
    excluded = Array.isArray(x) ? x : x.entries || x.decisions || [];
    draw();
  })
  .catch((e) => {
    $("#app").innerHTML =
      "<h1>Results could not load</h1><p>Please reload, or inspect the source repository.</p>";
    console.error(e);
  });
