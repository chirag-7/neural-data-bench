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
const GH = "https://github.com/chirag-7/neural-data-bench";
const HISTORICAL_MODELS = ["gpt-5.6-sol", "gpt-6-sol", "gpt-6.1-sol"];
const COMPARISON_MODELS = ["gpt-4.1-2025-04-14", "gpt-5-2025-08-07", "gpt-5.6-sol", "gpt-6.1-sol"];
let MODELS = [...HISTORICAL_MODELS], comparisonActive = false, historicalRecords = [];
const COLORS = {
  "gpt-4.1-2025-04-14": "#347e73",
  "gpt-5-2025-08-07": "#3c7fa4",
  "gpt-5.6-sol": "#9475aa",
  "gpt-6-sol": "#3c7fa4",
  "gpt-6.1-sol": "#c77735",
};
const NAMES = {
  "gpt-4.1-2025-04-14": "GPT-4.1",
  "gpt-5-2025-08-07": "GPT-5",
  "gpt-5.6-sol": "GPT-5.6 Sol",
  "gpt-6-sol": "GPT-6 Sol",
  "gpt-6.1-sol": "GPT-6.1 Sol",
  "wavpack-high": "WavPack 5.8 · lossless very-high",
  "delta-blosc-zstd": "Delta + Blosc/Zstd9 · bitshuffle",
  mountainsort5: "MountainSort5 · scheme 1",
  "yasa-eeg": "YASA · pretrained EEG",
  "pyriemann-ts-svm": "pyRiemann · TS-SVM",
  "pyriemann-aligned": "pyRiemann · aligned TS-SVM",
  "polya-gamma": "Polya–Gamma Gibbs · local",
  laplace: "Laplace approximation",
  singler: "SingleR · donor-layer profiles",
  "behavioral-glm": "Behavioral GLM · paper-inspired",
  "xdawn-tslr": "xDAWN · fixed",
  "xdawn-tslr-tuned": "xDAWN · train-CV tuned",
  "canonical-posterior": "Posterior median · post-hoc audit",
  "canonical-mle": "Canonical MLE",
  "oasis-default": "OASIS · default AR1",
  "raw-calcium": "Raw calcium",
  spikepack: "Spikepack · 100 µs grid",
  "mean-baseline": "Mean of observed history",
  midpoint: "Midpoint",
  "mriqc-rfc-2017": "MRIQC · archived 2017",
  deneux: "Deneux · archived",
  speiser: "Speiser · archived",
  friedrich: "Friedrich · archived",
  rupprecht: "Rupprecht · archived",
};
const METRIC_LABELS = {
  recording_mean_motion_rmse_um: "Recording-mean motion RMSE (µm)",
  mean_encoded_bits_per_event_50us: "Mean encoded bits/event · ≤50 µs timing error",
  animal_mean_neuron_pearson_smoothed200ms: "Animal-equal neuron Pearson correlation · 200 ms smoothing",
  mse_dff: "Calcium forecast mean squared error (dF/F)²",
  donor_block_macro_rmse: "Donor/block-balanced fraction RMSE",
  class_balanced_mouse_accuracy: "Class-balanced mouse accuracy",
  recording_macro_event_f1_20ms_onset_20ms_or_20pct_offset: "Recording-mean event F1 · 20 ms onset / duration-aware offset",
};
const metricLabel = (metric) => METRIC_LABELS[metric] || metric;
const CATEGORIES = {
  A: "Behavior & movement",
  B: "Extracellular data",
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
  A15: "Birdsong acoustic-event detection",
  B03: "Synthetic probe-motion recovery",
  B08: "Spike-event compression · 50 µs tolerance",
  C06: "Held-out-fish spike inference",
  E06: "Zebrafish activity forecasting",
  K05: "Measured cell-fraction calibration",
  K06: "Optotagged PV/SST waveform inference",
  B01: "Extracellular spike sorting",
  B07: "Lossless voltage compression",
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
  L06: "Spiking-neuron posterior inference",
  K04: "Cortical-layer label transfer",
  M01: "Conditional mouse-choice prediction",
  L04: "Place-cell count encoding",
  M04: "Cognitive parameter recovery",
  N05: "NWB file analysis",
};
const DATASETS = {
  A09: "CalMS21 · processed pose context",
  A14: "Rat7M · artificial HeadF gaps",
  A15: "DAS / Bengalese finch · one held-out bird",
  B03: "SpikeInterface · eight synthetic recordings",
  B08: "FALCON M2 · seven runs shared with G01",
  C06: "CASCADE DS04 · two held-out fish",
  E06: "ZAPBench · one brain, two dependent slices",
  K05: "Human DLPFC · orthogonal IF/RNAScope fractions",
  K06: "CellExplorer / Allen · five held-out mice",
  B01: "MEArec · 10 s stationary simulation",
  B07: "AIND / IBL · 16 real short chunks",
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
  L06: "sbibm · ten synthetic GLM observations",
  K04: "HumanPilot DLPFC · held-out donor",
  M01: "IBL behavior · 17 held-out mice",
  L04: "Kramer · one rat place cell",
  M04: "Synthetic two-choice Q-learning agents",
  N05: "Allen · one legacy NWB file",
};
let b01Metric = "primary";
let catalog,
  summary,
  replication,
  records = [],
  excluded = [],
  selectedTask = "A09",
  selectedSlice = "",
  l06Metric = "c2st",
  c06Metric = "primary",
  l06Observation = "mean",
  plotView = "graph",
  showAllRefs = false,
  showReferences = true,
  startAtZero = false,
  query = "",
  listMode = "measured",
  hiddenModels = new Set(),
  analysisClass = "historical_specialist",
  analysisScope = "observed_data";
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
    if (r.benchmark_id === "B07") return "Raw zlib9";
    if (r.benchmark_id === "B03") return "SpikeInterface · decentralized registration";
    if (r.benchmark_id === "B08") return "Quantized deltas + zlib9";
    if (r.benchmark_id === "C06") return "OASIS AR1 · training-calibrated";
    if (r.benchmark_id === "E06") return "NLinear · analytical ridge1";
    if (r.benchmark_id === "K05") return "Donor-CV weighted ridge";
    if (r.benchmark_id === "K06") return "Mouse-CV SVM / ExtraTrees";
    if (r.benchmark_id === "A15") return "Spectral boosting · event-CV";
    if (r.benchmark_id === "J08") return "StarDist · author archive";
    if (r.benchmark_id === "N05") return "Audited file reference";
    if (r.benchmark_id === "G01") return "FALCON-style ridge";
    if (r.benchmark_id === "K04") return "Balanced multinomial logit";
    if (r.benchmark_id === "M01") return "Training mean choice probability";
    if (r.benchmark_id === "H02") return "Shrinkage LDA · time bins";
    if (r.benchmark_id === "F04") return "PCA–Poisson GLM";
    return "Conventional task baseline";
  }
  return label(r.model);
}
function isSpecialist(r) {
  if (["historical_specialist", "local_specialist", "pretrained_specialist"].includes(r.display_reference_class)) return true;
  return (
    [
      "spikepack",
      "wavpack-high",
      "delta-blosc-zstd",
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
      "polya-gamma",
      "singler",
      "behavioral-glm",
      "xdawn-tslr-tuned",
    ].includes(r.model) ||
    r.model.startsWith("vassi-run-") ||
    (["J08", "B03", "C06"].includes(r.benchmark_id) && r.model === "task-baseline")
  );
}
function isDomainReference(r) {
  return r.model === "behavioral-glm" || (r.benchmark_id === "E06" && r.model === "task-baseline");
}
function evidence(r) {
  if (MODELS.includes(r.model)) return "General-model code";
  if (r.display_reference_class === "historical_specialist") return "Archived specialist · current best unverified";
  if (r.display_reference_class === "local_specialist") return "Local specialist · current best unverified";
  if (r.display_reference_class === "pretrained_specialist") return "Pretrained specialist · current best unverified";
  if (r.benchmark_id === "B07" && isSpecialist(r)) return "Domain-aligned codec reference";
  if (r.model === "behavioral-glm") return "Source-inspired pooled domain reference";
  if (r.benchmark_id === "E06" && r.model === "task-baseline") return "Conventional domain reference · altered NLinear optimization";
  if (["B03", "C06", "B08"].includes(r.benchmark_id) && isSpecialist(r)) return "Local specialist reproduction · global best unverified";
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
    if (a.length && (!comparisonActive || a.length === ss.length))
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
  else if (p[0] === "analysis" && p[1] === "patterns") generationPatternsPage();
  else if (p[0] === "analysis" && p[1] === "practical") practicalReviewPage();
  else if (p[0] === "analysis" && p[1] === "report") macroReportPage();
  else if (p[0] === "analysis") analysisPage();
  else if (p[0] === "methods") methodsPage();
  else if (p[0] === "excluded") excludedPage();
  else explorer(p[0] === "category" ? p[1] : "");
}
function mobileFilter(fam) {
  return `<div class="mobile-filter"><label class="screen-reader" for="mobile-category">Category</label><select id="mobile-category"><option value="">All categories</option>${catalog.families.map((f) => `<option value="${f.code}" ${fam === f.code ? "selected" : ""}>${esc(CATEGORIES[f.code] || f.name)}</option>`).join("")}</select></div>`;
}
function categoryOptions(selected) {
  return catalog.families.map((family) => `<option value="${family.code}" ${family.code === selected ? "selected" : ""}>${esc(CATEGORIES[family.code] || family.name)}</option>`).join("");
}
function categoryTasks(family, measuredOnly = false) {
  return catalog.entries.filter((entry) => entry.family_code === family && (!measuredOnly || measured(entry.id)));
}
function taskOptions(entries, selected, placeholder = false) {
  return (placeholder ? '<option value="">Choose a benchmark…</option>' : '') + entries.map((entry) => `<option value="${entry.id}" ${entry.id === selected ? "selected" : ""}>${entry.id} · ${esc(title(entry))}</option>`).join("");
}
function detailJumpMarkup(family, id) {
  return `<div class="toolbar benchmark-jump" aria-label="Jump to a benchmark"><label>Category <select id="detail-category-picker">${categoryOptions(family)}</select></label><label>Benchmark <select id="detail-benchmark-picker">${taskOptions(categoryTasks(family), id, true)}</select></label></div>`;
}
function bindDetailJump(tab) {
  $("#detail-category-picker").onchange = (event) => {
    $("#detail-jump").innerHTML = detailJumpMarkup(event.target.value, "");
    bindDetailJump(tab);
  };
  $("#detail-benchmark-picker").onchange = (event) => {
    if (event.target.value) location.hash = "#/benchmark/" + event.target.value + "/" + (["evaluation", "sources"].includes(tab) ? tab : "results");
  };
}
function explorer(fam = "") {
  const f = catalog.families.find((f) => f.code === fam),
    es = catalog.entries.filter((e) => !fam || e.family_code === fam),
    selectedCategory = fam || catalog.entries.find((entry) => entry.id === selectedTask)?.family_code || catalog.families[0].code,
    scored = categoryTasks(selectedCategory, true),
    choices = scored.length ? scored : categoryTasks(selectedCategory);
  if (choices.length && !choices.some((entry) => entry.id === selectedTask)) selectedTask = choices[0].id;
  $("#app").innerHTML =
    `<p class="eyebrow">General models × specialist methods</p><h1>${f ? esc(CATEGORIES[fam] || f.name) : "Neuroscience benchmark results"}</h1><p class="lede">${f ? esc(f.tasks) : "Explore measured performance by task, compare general models with verified specialist references, and follow each result to its data and evaluation protocol. Models generate analysis code, which is then fitted locally."}</p>${!fam ? `<p class="note">Choose a category, then a benchmark. ${route("analysis/practical", "Version changes, repaired runs & current specialists →")} ${route("analysis/report", "Previous cross-benchmark findings →")}</p>` : ""}${!fam ? `<div class="stats"><div class="stat"><strong>${summary.measured_tasks}</strong><span>tasks with model attempts</span></div><div class="stat"><strong>${summary.measured_families} / ${catalog.families.length}</strong><span>categories represented</span></div><div class="stat"><strong>${MODELS.length}</strong><span>general models evaluated</span></div><div class="stat"><strong>${summary.model_attempts}</strong><span>model × slice attempts</span></div></div>` : ""}${choices.length ? `<div class="toolbar benchmark-jump" aria-label="Explore by category and benchmark"><label>Category <select id="category-picker">${categoryOptions(selectedCategory)}</select></label><label>Benchmark <select id="benchmark-picker">${taskOptions(choices, selectedTask)}</select></label>${route("benchmark/" + selectedTask, "Open benchmark →", "button secondary")}</div>${fam ? '<div id="featured-chart"></div>' : ""}` : `<div class="note">No active benchmarks in this category.</div>`}<div class="section-head"><h2>${f ? "Benchmarks in this category" : "Explore benchmark categories"}</h2><span class="small">Native scores · no mixed-metric ranking</span></div><div class="toolbar"><input id="search" class="search" aria-label="Search benchmarks" placeholder="Search tasks, datasets or methods…" value="${esc(query)}"><select id="list-mode" aria-label="Result availability"><option value="measured" ${listMode === "measured" ? "selected" : ""}>Measured results</option><option value="all" ${listMode === "all" ? "selected" : ""}>All active candidates</option></select><a class="download-link" href="data/${comparisonActive ? "comparison-measurements.jsonl" : "measurements.csv"}" download>Download results ↓</a></div><div id="benchmark-directory"></div><p class="small" style="margin-top:17px">† Code-line format deviation; see strict-format analysis. A published task score is conditional on its frozen slice and procedure. ${comparisonActive ? "Directory scores use the current retained comparison results, including documented repairs." : "Directory scores use each task’s first submission."} H02’s replication tab includes its stronger train-CV specialist and repeated submissions. The highest inspected reference score does not establish current global SOTA. ${route("methods", "Read the methodology →")}</p>`;
  if ($("#mobile-category"))
    $("#mobile-category").onchange = (e) => {
      location.hash = e.target.value ? "#/category/" + e.target.value : "#/";
    };
  if ($("#category-picker")) $("#category-picker").onchange = (event) => {
    const entries = categoryTasks(event.target.value, true);
    selectedTask = (entries[0] || categoryTasks(event.target.value)[0])?.id || "";
    selectedSlice = "";
    if (fam) location.hash = "#/category/" + event.target.value;
    else explorer("");
  };
  if ($("#benchmark-picker"))
    $("#benchmark-picker").onchange = (e) => {
      selectedTask = e.target.value;
      selectedSlice = "";
      explorer(fam);
    };
  $("#search").oninput = (e) => {
    query = e.target.value;
    directory(es, !fam);
  };
  $("#list-mode").onchange = (e) => {
    listMode = e.target.value;
    directory(es, !fam);
  };
  directory(es, !fam);
  if (fam && scored.length) renderChart("#featured-chart", selectedTask, true);
}
function directory(es, grouped = false) {
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
  if (grouped) {
    const families = catalog.families.filter((family) => filtered.some((entry) => entry.family_code === family.code));
    $("#benchmark-directory").innerHTML = `<div class="category-grid">${families.map((family) => {
      const entries = filtered.filter((entry) => entry.family_code === family.code);
      return `<section class="category-card" aria-labelledby="category-title-${family.code}"><div class="category-card-head"><h3 id="category-title-${family.code}">${route("category/" + family.code, esc(CATEGORIES[family.code] || family.name))}</h3><span class="count">${entries.length}</span></div><p class="small">${esc(family.tasks)}</p><label class="category-task-label" for="category-task-${family.code}">Open a benchmark</label><select id="category-task-${family.code}" aria-label="Benchmark in ${esc(CATEGORIES[family.code] || family.name)}">${taskOptions(entries, "", true)}</select><details class="category-task-details"><summary>Browse task names</summary><ul class="category-task-list">${entries.map((entry) => {
        const result = brief(entry.id).bestModel;
        return `<li>${route("benchmark/" + entry.id, `<span class="task-id">${entry.id}</span>${esc(title(entry))}`)}<span class="small">${result ? esc(metricLabel(result.metric)) : "Candidate · not run"}</span></li>`;
      }).join("")}</ul></details></section>`;
    }).join("")}</div>${families.length ? "" : '<p class="empty">No matching benchmarks. Try another search or result-availability filter.</p>'}`;
    for (const family of families) $("#category-task-" + family.code).onchange = (event) => {
      if (event.target.value) location.hash = "#/benchmark/" + event.target.value + "/results";
    };
    return;
  }
  $("#benchmark-directory").innerHTML =
    `<div class="table-panel table-wrap"><table><thead><tr><th>Benchmark / dataset</th><th>Category</th><th>Best measured general model</th><th>Tested reference</th><th>Metric</th></tr></thead><tbody>${
      filtered
        .map((e) => {
          const b = brief(e.id);
          return `<tr><td>${route("benchmark/" + e.id, esc(title(e)), "bench-name")}<span class="bench-sub">${e.id} · ${esc(DATASETS[e.id] || e.resource)}</span></td><td><span class="small">${esc(CATEGORIES[e.family_code])}</span></td><td>${b.bestModel ? `<span class="number">${fmt(b.bestModel.score)}</span><span class="score-caption">${label(b.bestModel.model)}${b.bestModel.line_limit_compliant === false ? " †" : ""}${b.nSlices > 1 ? " · mean of " + b.nSlices + " slices" : ""}</span>` : '<span class="badge">Not run</span>'}</td><td>${b.reference ? `<span class="number">${fmt(b.reference.score)}</span><span class="score-caption">${esc(methodName(b.reference))}${isSpecialist(b.reference) ? "" : " · baseline/reference"}</span>` : '<span class="small">Unverified</span>'}</td><td>${b.bestModel ? `<span class="small">${esc(metricLabel(b.bestModel.metric))} ${b.bestModel.direction === "higher" ? "↑" : "↓"}</span>` : "—"}</td></tr>`;
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
  if (c.rs.some((r) => r.benchmark_id === "B07")) add(c.rs.find((r) => r.model === "delta-blosc-zstd"));
  const baseline = c.rs.find((r) => r.model === "task-baseline") || c.rs.find((r) => r.benchmark_id === "L06" && r.model === "laplace");
  if (valid(baseline)) add(baseline);
  if (showAllRefs)
    for (const r of c.rs)
      if (!MODELS.includes(r.model) && !r.model.startsWith("vassi-run-"))
        add(r);
  return selected;
}
function calciumCountError(row) {
  const cells = row.cell_results;
  if (!Array.isArray(cells) || !cells.length || cells.some((cell) => !cell.animal || !Number.isFinite(cell.relative_error))) return undefined;
  const animals = [...new Set(cells.map((cell) => cell.animal))];
  return animals.reduce((total, animal) => {
    const values = cells.filter((cell) => cell.animal === animal).map((cell) => cell.relative_error);
    return total + values.reduce((a, b) => a + b, 0) / values.length;
  }, 0) / animals.length;
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
  if (id === "L06") {
    const convert = (r) => {
      if (!r) return r;
      const per = l06Metric === "sliced-w2" ? r.per_observation_sliced_w2 : r.per_unit;
      const score = l06Observation === "mean" ? (l06Metric === "sliced-w2" ? r.sliced_w2 : r.score) : per?.[Number(l06Observation)];
      return { ...r, score, metric: l06Metric === "sliced-w2" ? "Prior-whitened sliced Wasserstein-2" : "Classifier accuracy · chance target 0.5", direction: "lower" };
    };
    c = { ...c, rs: c.rs.map(convert), specialists: c.specialists.map(convert), specialist: convert(c.specialist), reference: convert(c.reference), frozen: convert(c.frozen) };
  }
  if (id === "C06" && c06Metric === "relative-error") {
    const convert = (r) => r ? { ...r, score: calciumCountError(r), metric: "Animal-equal neuron relative count error · predeclared secondary", direction: "lower" } : r;
    c = { ...c, rs: c.rs.map(convert), specialists: c.specialists.map(convert), specialist: convert(c.specialist), reference: convert(c.reference), frozen: convert(c.frozen) };
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
    `<div class="chart-card"><div class="chart-head"><div><h2>${compact ? route("benchmark/" + id, esc(title(e))) : esc(title(e))}</h2><p class="small">${esc(metricLabel(native.metric))} · ${native.direction === "higher" ? "higher" : "lower"} is better · ${id}</p></div><div class="segmented" role="group" aria-label="Chart or table"><button data-view="graph" class="${plotView === "graph" ? "active" : ""}">Graph</button><button data-view="table" class="${plotView === "table" ? "active" : ""}">Table</button></div></div><div class="plot-controls">${id === "L06" ? `<label>Posterior metric <select id="metric-picker"><option value="c2st" ${l06Metric === "c2st" ? "selected" : ""}>Primary · classifier accuracy (target 0.5)</option><option value="sliced-w2" ${l06Metric === "sliced-w2" ? "selected" : ""}>Secondary · sliced Wasserstein-2</option></select></label><label>Observation <select id="observation-picker"><option value="mean" ${l06Observation === "mean" ? "selected" : ""}>Mean of all ten</option>${Array.from({length:10},(_,i)=>`<option value="${i}" ${l06Observation === String(i) ? "selected" : ""}>Observation ${i+1}</option>`).join("")}</select></label>` : ""}${id === "C06" ? `<label>Calcium metric <select id="metric-picker"><option value="primary" ${c06Metric === "primary" ? "selected" : ""}>Primary · animal-equal Pearson correlation</option><option value="relative-error" ${c06Metric === "relative-error" ? "selected" : ""}>Secondary · relative count error</option></select></label>` : ""}${id === "B01" ? `<label>Plot metric <select id="metric-picker"><option value="primary" ${b01Metric === "primary" ? "selected" : ""}>Frozen mean GT-unit accuracy</option><option value="all-event-f1" ${b01Metric === "all-event-f1" ? "selected" : ""}>All-output event F1 · post-hoc</option></select></label>` : ""}<label>Evaluation slice <select id="slice-picker">${slices.map((s) => `<option value="${s}" ${s === selectedSlice ? "selected" : ""}>${id === "C05" ? "Preparation " + s : id === "E06" ? (s === "taxis" ? "Unseen taxis stimulus · dependent slice" : "Seen-stimulus temporal forecast") : s}</option>`).join("")}</select></label><label><input id="show-ref" type="checkbox" ${showReferences ? "checked" : ""}>Include references</label><label><input id="all-ref" type="checkbox" ${showAllRefs ? "checked" : ""}>Show additional references</label>${plotView === "graph" ? `<label class="right"><input id="zero-axis" type="checkbox" ${startAtZero ? "checked" : ""}>Line axis starts at zero</label>` : ""}</div>${plotView === "graph" ? `${referenceCards(refs, c.frozen)}<p class="plot-reading-key"><span class="solid-key"></span>Solid connected points = general models. <span class="dashed-key"></span>Dashed horizontal lines = specialists or domain references. <span class="dotted-key"></span>Dotted lines = other references.</p><div class="chart-grid"><section><p class="chart-label">Performance across model versions</p>${linePlot(generals, refs, native.direction, c.specialists)}</section><section><p class="chart-label">General models and named references</p>${barPlot([...generals, ...refs], native.direction)}</section></div><div class="legend">${MODELS.map((m) => `<label><input type="checkbox" data-model="${m}" ${!hiddenModels.has(m) ? "checked" : ""}><i class="dot" style="background:${COLORS[m]}"></i>${label(m)}</label>`).join("")}${refs.map((r, i) => `<span><i class="dash" style="border-color:${refColor(r, i)}"></i>${esc(methodName(r))} · ${fmt(r.score)}</span>`).join("")}</div>` : `<div class="table-wrap">${scoreTable(c.rs)}</div>`}<div class="chart-foot">${chartCaveat(id, c)} ${compact ? route("benchmark/" + id, "Inspect protocol, sources and all scores →") : ""}<br>Connected points show version order, not elapsed time or a compute scaling law. Line axes ${startAtZero ? "include zero" : "adapt to the score range; inspect the ticks"}; bars include zero. ${comparisonActive ? "Final retained results: repairs are identified in provenance; API and Codex generation contexts differ." : "First-submission panel: one generated program per model/task."}${id === "H02" ? " " + route("benchmark/H02/replication", "Inspect three-generation follow-up →") : ""}</div></div>`;
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
      if (id === "L06") l06Metric = ev.target.value;
      else if (id === "C06") c06Metric = ev.target.value;
      else b01Metric = ev.target.value;
      renderChart(target, id, compact);
    };
  if (id === "L06") $("#observation-picker").onchange = (ev) => {
    l06Observation = ev.target.value;
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
  return (isSpecialist(r) || isDomainReference(r))
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
        `<div class="reference-card ${isSpecialist(r) ? "specialist" : "baseline"}"><div class="reference-kicker"><span class="reference-key" style="color:${refColor(r, i)}">R${i + 1} · ${r.benchmark_id === "B07" && isSpecialist(r) ? "Codec reference · dashed line" : isDomainReference(r) ? "Domain reference · dashed line" : isSpecialist(r) ? "Specialist · dashed line" : "Other reference · dotted line"}</span>${r.model === frozen?.model ? '<span class="reference-policy">Primary comparator</span>' : ""}</div><div class="reference-value"><span>${esc(methodName(r))}</span><strong>${fmt(r.score)}</strong></div><span class="reference-policy">${esc(evidence(r))}</span></div>`,
    )
    .join("")}</div>`;
}
function notScoredLabel(row) {
  if (row.not_scored_reason) return row.not_scored_reason;
  if (!MODELS.includes(row.model) && !HISTORICAL_MODELS.includes(row.model)) return 'Reference output unavailable from archive';
  return /exceeded|timed out/i.test(row.reason || '') ? 'Not scored within computation limit' : 'Not scored under task requirements';
}
function linePlot(general, refs, direction, specialists = [], zeroAxis = startAtZero, modelOrder = MODELS) {
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
  lo = zeroAxis ? Math.min(0, lo - padding) : lo - padding;
  hi += padding;
  if (direction === "lower" && vals.every(v => v >= 0)) lo = Math.max(0, lo);
  const x = (i) => 88 + (250 / Math.max(1, modelOrder.length - 1)) * i,
    y = (v) => direction === 'lower' ? top + ((v - lo) / (hi - lo)) * plotHeight : bottom - ((v - lo) / (hi - lo)) * plotHeight;
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
        (prior ? " L" : " M") + x(modelOrder.indexOf(r.model)) + " " + y(r.score);
      prior = true;
    } else prior = false;
  }
  const archives = specialists.filter((r) => r.model.startsWith("vassi-run-"));
  return `<p class="small metric-direction-key">* = manually repaired, where marked. Better performance ↑ · ${direction === "lower" ? "lower native score is better; vertical axis reversed" : "higher native score is better"}</p><svg class="plot line-plot" viewBox="0 0 570 ${bottom + 68}" role="img" aria-label="Model-version line chart with named specialist reference lines"><title>Solid connected points: general model scores. Horizontal dashed lines: specialists. Dotted lines: other references. ${direction} is better. Better scores are higher on the page; lower-is-better axes are reversed.</title>${[
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
      return `<g class="direct-reference-label"><line x1="65" x2="365" y1="${yy}" y2="${yy}" stroke="${refColor(r, i)}" stroke-width="2" stroke-dasharray="${(isSpecialist(r) || isDomainReference(r)) ? "7 4" : "2 5"}"/><path d="M365 ${yy} L376 ${yy} L389 ${ly}" fill="none" stroke="${refColor(r, i)}" stroke-width="1"/><text x="395" y="${ly - 4}" class="reference-label-name" style="fill:${refColor(r, i)}">R${i + 1} · ${esc(short)}</text><text x="395" y="${ly + 10}" class="reference-label-score">${fmt(r.score)} · ${isDomainReference(r) ? "domain reference" : r.benchmark_id === "B07" && isSpecialist(r) ? "codec reference" : isSpecialist(r) ? "specialist" : "other reference"}</text><title>R${i + 1}: ${esc(name)}, ${fmt(r.score)}. ${evidence(r)}</title></g>`;
    })
    .join(
      "",
    )}<path d="${path}" fill="none" stroke="#547b97" stroke-width="2"/>${general
    .map((r) => {
      const xx = x(modelOrder.indexOf(r.model));
      return `${valid(r) && Number.isFinite(r.range_min) ? `<g class="generation-range"><line x1="${xx}" x2="${xx}" y1="${y(r.range_min)}" y2="${y(r.range_max)}" stroke="${COLORS[r.model]}" stroke-width="2"/><path d="M${xx-6} ${y(r.range_min)}h12 M${xx-6} ${y(r.range_max)}h12" stroke="${COLORS[r.model]}"/><title>${label(r.model)} generation range ${fmt(r.range_min)} to ${fmt(r.range_max)}; not a confidence interval</title></g>` : ""}${valid(r) ? `<circle cx="${xx}" cy="${y(r.score)}" r="5.5" fill="${COLORS[r.model]}"><title>${label(r.model)}: ${fmt(r.score)}</title></circle><text class="value-label" x="${xx}" y="${y((direction === "lower" ? r.range_min : r.range_max) ?? r.score) - 13}" text-anchor="middle">${fmt(r.score)}${r.line_limit_compliant === false ? "†" : ""}${r.repair_applied ? " *" : ""}</text>` : `<text x="${xx}" y="${top + plotHeight / 2}" text-anchor="middle">Not scored<title>${esc(notScoredLabel(r))}</title></text>`}<text x="${xx}" y="${bottom + 29}" text-anchor="middle">${label(r.model).replace("GPT-", "")}</text>`;
    })
    .join(
      "",
    )}<text x="215" y="${bottom + 58}" text-anchor="middle">General model version</text></svg>`;
}
function barPlot(rs, direction) {
  const vals = rs.filter(valid).flatMap((r) => [r.score,r.range_min,r.range_max].filter(Number.isFinite));
  let lo = Math.min(0, ...vals),
    hi = Math.max(0, ...vals);
  if (hi === lo) hi = lo + 1;
  const scale = (v) => 195 + ((v - lo) / (hi - lo)) * 300,
    zero = scale(0),
    height = rs.length * 42 + 50;
  const ticks = [...new Set([lo, (lo + hi) / 2, 0, hi])].sort((a, b) => a - b);
  return `<p class="small metric-direction-key">* = manually repaired, where marked. Raw native scores · ${direction === "lower" ? "lower is better" : "higher is better"}; read the values rather than bar length.</p><svg class="plot" viewBox="0 0 570 ${height}" role="img" aria-label="Bar chart including general models and named specialist or baseline scores"><title>Native metric; ${direction} is better. Bar axis includes zero.</title>${ticks
    .map((v) => {
      return `<line x1="${scale(v)}" x2="${scale(v)}" y1="5" y2="${height - 32}" stroke="${v === 0 ? "#b5c2cc" : "#e9edf0"}"/><text x="${scale(v)}" y="${height - 10}" text-anchor="middle">${fmt(v)}</text>`;
    })
    .join("")}${rs
    .map((r, i) => {
      const yy = 12 + i * 42;
      return `<text x="181" y="${yy + 15}" text-anchor="end">${esc(methodName(r))}${r.line_limit_compliant === false ? "†" : ""}${r.repair_applied ? " *" : ""}</text>${valid(r) ? `<rect x="${Math.min(zero, scale(r.score))}" y="${yy}" width="${Math.max(0.8, Math.abs(scale(r.score) - zero))}" height="23" fill="${COLORS[r.model] || refColor(r, i)}"><title>${esc(methodName(r))}: ${fmt(r.score)} · ${evidence(r)}</title></rect>${Number.isFinite(r.range_min) ? `<g class="generation-range"><line x1="${scale(r.range_min)}" x2="${scale(r.range_max)}" y1="${yy+12}" y2="${yy+12}" stroke="#233c50" stroke-width="2"/><path d="M${scale(r.range_min)} ${yy+7}v10 M${scale(r.range_max)} ${yy+7}v10" stroke="#233c50"/><title>Generation range ${fmt(r.range_min)} to ${fmt(r.range_max)}; not a confidence interval</title></g>` : ""}<text class="value-label" x="560" y="${yy + 15}" text-anchor="end">${fmt(r.score)}</text>` : `<text x="360" y="${yy + 15}">Not scored<title>${esc(notScoredLabel(r))}</title></text>`}`;
    })
    .join("")}</svg>`;
}
function chartCaveat(id, c) {
  let text = id === "M01"
    ? "The dashed horizontal line shows the source-inspired behavioral GLM; its name and score appear above and beside the plot. "
    : c.specialist
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
      "The historical Sol posterior estimators nearly agree; those small differences reflect numerical quadrature. The post-hoc posterior reference and frozen MLE optimize different objectives. ";
  if (id === "N05")
    text +=
      "One file, 61 deterministic fields, shared with D02; the reference is correct by construction. ";
  if (id === "B01")
    text +=
      "One 10-second stationary simulation. The post-hoc all-output event F1 sensitivity counts extra spikes; the historical GPT-6 result was 0.5998 versus MountainSort5 0.9621. Select it above to inspect both plots. This diagnostic was added post hoc; directory and macro statistics retain the frozen primary metric. ";
  if (id === "B03") text += "Eight synthetic recordings with known imposed displacement; four held-out simulations, not animals. Relative motion uses a per-record constant-offset gauge only: no scorer sign, scale or time alignment. The local SpikeInterface registration reference shares the processed peak-count raster; global best is unverified. ";
  if (id === "B08") text += comparisonActive ? "Timing is intentionally lossy: maximum 50 µs error per event, with exact labels and event order. Seven FALCON runs share G01 sources and one monkey. The corrected harness permits heapq. Original import failures remain in the historical audit. Specialist scores are local codec comparisons, not a verified global best. " : "Timing is intentionally lossy: maximum 50 µs error per event, with exact labels and event order. Seven FALCON runs share G01 sources and one monkey. Two heapq import-whitelist failures are retained: the prompt said ordinary utilities while the frozen harness rejected heapq. This contract ambiguity excludes B08 from all aggregate reference and model-version claims; native results and failure details remain visible. Spikepack is a local specialist codec, not a global-best result. ";
  if (id === "C06") text += "Two held-out fish; complete recordings remain separate. Pearson correlation ignores amplitude calibration. The predeclared relative count error averages neurons equally within animal, then animals equally; lower is better. Switching metrics changes these plots only, never directory or macro primary scores. OASIS AR1 is a local specialist reference; CASCADE global checkpoints overlap this test source and are not used. ";
  if (id === "E06") text += "One zebrafish brain and a fixed 256-neuron subset. The temporal and unseen-taxis slices share neurons, training arrays and unchanged generated code; they are not independent tasks or animals. Each 32-frame forecast uses its own 64 observed past frames. NLinear uses conventional analytical ridge1 optimization, not published weights or verified global best. ";
  if (id === "K05") text += "Three held-out human donors with replicated tissue blocks. Targets are orthogonal IF/RNAScope marker-positive fractions, not computational deconvolution labels; they need not sum to one. Both models and weighted-ridge reference receive numeric expression columns without gene IDs. This is supervised fraction calibration, not reference-only deconvolution or global best. ";
  if (id === "K06") text += "Five held-out mice, optotagged PV/SST classes, waveform features only. Mouse/class-balanced accuracy preserves biological grouping. Acquisition cohort and Cre-line differences may remain. The training-CV SVM/ExtraTrees comparator is conventional; current specialist best is unverified. ";
  if (id === "A15") text += "Twenty test recordings are one held-out bird. Source syllable boundaries use amplitude segmentation with human-assigned labels and incomplete call coverage. Event F1 uses onset and offset tolerances, not exhaustive vocalization truth. The spectral boosting reference is conventional; GPT-5.6 Sol retains a 268-line format deviation. Global best is unverified. ";
  if (id === "B07") text += "All 16 fixed real-voltage chunks must decode byte-exactly. Lower encoded bits per int16 sample is better; raw storage is 16 bits/sample. WavPack and delta–Blosc/Zstd are dashed codec references; raw zlib9 is dotted. Roughly 0.137 seconds per recording: this is a short-chunk storage diagnostic, not full streaming, neural interpretation or a global-best result. WavPack remains the frozen primary comparator even when another inspected codec compresses better. ";
  if (id === "L06") text += "Ten synthetic posteriors share one stimulus. Primary C2ST accuracy should approach 0.5; near-chance differences are noisy. Secondary sliced Wasserstein-2 should approach zero. The observation selector changes this plot only; directory and macro scores retain the mean primary over all ten. Reported sampling seconds cover the full ten-posterior call, excluding classifier scoring. The dashed line is the local Polya–Gamma Gibbs sampler, related to the archived reference algorithm. Known likelihood and a custom 2,000-draw scorer: these are not original simulator-only SBI leaderboard scores. ";
  if (id === "K04") text += "Four test sections are one held-out donor. Curated layer labels use expression assistance; no spatial coordinates are provided. SingleR is a fixed local label-transfer reference, not a spatial-clustering leaderboard winner. ";
  if (id === "M01") text += "Seventeen held-out mice, with labs shared across train/test. Inputs include known block prior and observed histories; disjoint target/history blocks prevent target reuse. This is conditional prediction, not rollout. The source-inspired GLM is not an established strongest specialist. ";
  if (id === "J08")
    text +=
      "Two held-out fields × five human raters; archived StarDist optimization history differs. ";
  return (
    esc(text) +
    "†Formatting deviations remain visible and are excluded from strict subsets."
  );
}
function scoreTable(rs) {
  return `<table><thead><tr><th>Method</th><th>Score</th><th>Evidence</th><th>${rs.some((r) => r.benchmark_id === "B07") ? "All-16 codec seconds" : rs.some((r) => r.benchmark_id === "L06") ? "All-ten sampling seconds" : "Execution seconds"}</th><th>Details</th></tr></thead><tbody>${rs.map((r) => `<tr><td><span class="dot" style="background:${COLORS[r.model] || refColor(r)}"></span> ${esc(methodName(r))}${r.line_limit_compliant === false ? " †" : ""}</td><td>${valid(r) ? fmt(r.score) : esc(notScoredLabel(r))}</td><td><span class="badge ${isSpecialist(r) ? "verified" : MODELS.includes(r.model) ? "general" : ""}">${evidence(r)}</span></td><td>${Number.isFinite(r.seconds) ? r.seconds.toFixed(2) : "Unavailable"}</td><td class="wrap small">${r.status === "failed" ? esc(r.not_scored_reason || (r.reason || "Output unavailable").trim().split("\n").pop()) : r.scoring_diagnostics ? esc(`${r.posthoc_secondary_metrics ? "All-output event F1 " + fmt(r.posthoc_secondary_metrics.all_event_f1) + " (post-hoc); " : ""}${r.scoring_diagnostics.n_predicted_units} predicted units; ${(r.scoring_diagnostics.redundant_unit_ids || []).length} redundant; ${(r.scoring_diagnostics.false_positive_unit_ids || []).length} false-positive units`) : r.model === "canonical-posterior" ? "Added post hoc; objective-aligned audit" : r.line_limit_compliant === false ? "Unchanged format deviation" : "See protocol and prediction artifacts"}</td></tr>`).join("")}</tbody></table>`;
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
    `<div id="detail-jump">${detailJumpMarkup(e.family_code, id)}</div><p class="breadcrumb">${route("", "Benchmarks")} / ${route("category/" + e.family_code, esc(CATEGORIES[e.family_code]))} / ${id}</p><p class="eyebrow">${id} · ${esc(CATEGORIES[e.family_code])}</p><h1>${esc(title(e))}</h1><p class="lede">${esc(e.executed_slice || e.resource)}</p><div class="detail-top"><span class="badge ${measured(id) ? "verified" : ""}">${measured(id) ? "Measured exploratory protocol" : "Candidate · not run"}</span><span class="badge">T3 · generated analysis code</span><span class="badge">Current global SOTA unverified</span></div><nav class="tabs" aria-label="Benchmark information">${[
      ["results", comparisonActive ? "Current results" : id === "H02" ? "Original results" : "Results"],
      ...(id === "H02" ? [["replication", "Historical replication"]] : []),
      ...(measured(id) ? [["specialists", "Current specialists"]] : []),
      ...(REPAIR_TASKS.includes(id) ? [["repairs", "Historical repair audit"]] : []),
      ["evaluation", "Evaluation details"],
      ["sources", "Data & sources"],
    ]
      .map(([v, t]) =>
        route("benchmark/" + id + "/" + v, t, tab === v ? "active" : ""),
      )
      .join("")}</nav><div id="benchmark-content"></div>`;
  bindDetailJump(tab);
  if (tab === "specialists") {
    specialistReviewPanel(id);
  } else if (tab === "repairs" && REPAIR_TASKS.includes(id)) {
    repairReviewPanel(id);
  } else if (tab === "results") {
    if (!measured(id)) {
      $("#benchmark-content").innerHTML =
        `<div class="note"><strong>No model results.</strong> ${esc(e.admission_reason)}</div>${link(GH + "/blob/main/" + e.admission_evidence_file, "Admission evidence")}`;
      return;
    }
    const ref = b.reference;
    $("#benchmark-content").innerHTML =
      `${!comparisonActive && REPAIR_TASKS.includes(id) ? `<div class="note"><strong>These are unchanged first-attempt results.</strong> ${route("benchmark/" + id + "/repairs", "Inspect the actual repaired runs and unresolved archive cases →")} Manual debugging is a separate evidence track.</div>` : ""}<div class="detail-summary"><div class="reference-box"><span class="small">${id === "L06" ? "Lowest general C2ST · descriptive point" : "Best measured general model"}${b.nSlices > 1 ? " · slice-equal mean" : ""}</span><strong>${fmt(b.bestModel?.score)}</strong><p>${b.bestModel ? label(b.bestModel.model) + (b.bestModel.line_limit_compliant === false ? " · format deviation" : "") : "All attempts failed"}</p></div><div class="reference-box specialist"><span class="small">${id === "B07" ? "Best inspected codec reference" : id === "L06" ? "Fixed Polya–Gamma sampler reference" : id === "M01" ? "Source-inspired domain reference" : id === "H02" ? "Original fixed specialist · see replication tab" : id === "C06" ? "Local OASIS reference · global best unverified" : id === "B03" ? "Local SpikeInterface reference · global best unverified" : id === "B08" ? "Local Spikepack reference · global best unverified" : id === "E06" ? "Conventional NLinear domain reference" : ref && isSpecialist(ref) ? "Highest inspected specialist point · global best unverified" : "Available baseline / reference"}</span><strong>${fmt(ref?.score)}</strong><p>${ref ? esc(methodName(ref)) : "Not established"} · training and selection histories differ</p></div></div><div id="detail-chart"></div><details><summary>What can this result establish?</summary><p>${esc(e.limitations)}</p><p>This measures a model-generated numerical analysis procedure. One submission per model; public-data contamination and provider checkpoint resolution remain unverified. Specialist training, feature access and tuning budgets can differ. Missing results are unknown, not zero.</p></details><div class="actions"><a class="button secondary" href="data/${comparisonActive ? "comparison-measurements.jsonl" : id + ".json"}" download>${comparisonActive ? "Current comparison records" : "Detailed records"} ↓</a>${link(GH + "/tree/main/experiments/" + id, "Frozen code & protocol", "button secondary")}${link(GH + "/tree/main/results/predictions/" + id, "Predictions", "button secondary")}</div>`;
    renderChart("#detail-chart", id);
  } else if (tab === "replication" && id === "H02") {
    $("#benchmark-content").innerHTML = replicationPanel();
  } else if (tab === "evaluation") {
    $("#benchmark-content").innerHTML =
      `<div class="doc-grid"><section class="doc-panel"><h2>Evaluation contract</h2><dl class="kv"><dt>Input</dt><dd>${esc(e.data)}</dd><dt>Executed slice</dt><dd>${esc(e.executed_slice || "Not yet defined")}</dd><dt>Ground truth</dt><dd>${esc(e.ground_truth)}</dd><dt>Metric / split</dt><dd>${esc(e.recommended_metrics)}<br>${esc(e.recommended_split)}</dd></dl></section><section class="doc-panel"><h2>Validity and procedure</h2><p>${esc(e.limitations)}</p><p>${esc(e.admission_reason)}</p><div class="link-list">${measured(id) ? link(GH + "/blob/main/experiments/" + id + (id === "C05" ? "/phase2-protocol.md" : "/protocol.md"), "Exact frozen protocol") : ""}${link(GH + "/blob/main/benchmarks/" + e.family_code + "/" + id + "/worklog.md", "Steps actually completed")}${measured(id) ? link(GH + "/blob/main/experiments/" + id + (["C05", "M04"].includes(id) ? "/generation-provenance.json" : "/run-spec.json"), "Frozen input and prompt identities") : ""}${link(GH + "/blob/main/" + e.admission_evidence_file, "Admission assessment")}</div></section></div>`;
  } else {
    $("#benchmark-content").innerHTML =
      `<div class="doc-panel"><h2>Primary data and method sources</h2><p>Sources retain their original terms. A source association is not a claim that every asset was acquired or every paper fully reviewed. Measured-task manifests describe the actual files used.</p><div class="link-list">${e.source_urls.map((u, i) => link(u, esc(u.replace(/^https?:\/\//, "")))).join("")}</div><div class="actions">${link(GH + "/tree/main/" + (measured(id) ? "experiments/" + id : "benchmarks/" + e.family_code + "/" + id), "Source manifests and preparation")}${link(GH + "/blob/main/benchmarks/" + e.family_code + "/" + id + "/data.json", "Data and rights assessment")}</div></div>`;
  }
}

function replicationPanel() {
  if (!replication) return '<p class="empty">Replication data unavailable.</p>';
  const generals = replication.generation_summary.map((s) => ({
    model: s.model, score: s.mean, range_min: s.minimum, range_max: s.maximum,
    status: s.valid ? "measured" : "failed", direction: "higher",
  }));
  const refs = replication.references.filter((r) => ["xdawn-tslr", "xdawn-tslr-tuned"].includes(r.model));
  return `<p class="eyebrow">Historical three-model follow-up · includes GPT-6 Sol</p><h2>How much does a fresh generation change the result?</h2><p class="lede">Exactly two fresh submissions per model plus the original. Points and bars show the mean of all numerically valid attempts; whiskers show their minimum–maximum range, not confidence intervals.</p><div class="note">This task and follow-up were chosen after viewing the first scores. Three generations are not three datasets. These repeated generations are excluded from current cross-task totals; new tasks can extend that panel. No best-of-three selection or execution feedback.</div>${referenceCards(refs, refs.find((r) => r.model === "xdawn-tslr"))}<div class="chart-card"><p class="plot-reading-key"><span class="solid-key"></span>General-model means · whiskers = generation range. <span class="dashed-key"></span>Named specialist scores.</p><div class="chart-grid"><section><p class="chart-label">Mean ROC-AUC across model versions</p>${linePlot(generals, refs, "higher", refs, false, HISTORICAL_MODELS)}</section><section><p class="chart-label">Generation means and specialist references</p>${barPlot([...generals, ...refs], "higher")}</section></div><p class="small">Equal weight to each held-out person. Line axis adapts to scores; bars include zero. Version order is not elapsed time. Specialist search/refit used a 180-second limit, but equal total development or tuning effort is unestablished.</p></div><div class="table-panel table-wrap"><table><thead><tr><th>Model</th><th>Attempt 1</th><th>Attempt 2</th><th>Attempt 3</th><th>Mean</th><th>Valid / planned</th><th>Strict valid</th></tr></thead><tbody>${replication.generation_summary.map((s) => `<tr><td>${label(s.model)}</td>${s.per_attempt.map((a) => `<td>${a.status === "measured" ? fmt(a.score) : "Failed"}${a.line_limit_compliant === false ? " †" : ""}</td>`).join("")}<td>${fmt(s.mean)}</td><td>${s.valid} / ${s.attempted}</td><td>${s.strict_valid} / ${s.attempted}</td></tr>`).join("")}</tbody></table></div><details open><summary>How was the specialist chosen?</summary><p>The additional xDAWN reference compares 12 configurations using five-fold grouped validation on the 15 training people: 2 or 4 spatial filters, target-only or both-class templates, and logistic C of 0.1, 1 or 10. Covariance estimates, tangent reference and scaling are fitted inside each training fold. Highest equal-person validation ROC-AUC selects the final configuration; test people enter only final inference and scoring.</p><p>The fixed original reference remains visible. The tuned reference is a retrospective sensitivity, not proof of current global best. All candidate validation scores and the selected configuration are retained.</p></details><div class="actions"><a class="button secondary" href="data/H02-replication.csv" download>Every follow-up record ↓</a>${link(GH + "/blob/main/experiments/H02/replication-v1/results.md", "Results and limits", "button secondary")}${link(GH + "/tree/main/experiments/H02/replication-v1", "Plan, programs and verification", "button secondary")}</div>`;
}

function modelsPage(model) {
  if (comparisonActive && model === "gpt-6-sol") {
    $("#app").innerHTML = `<p class="eyebrow">Historical model</p><h1>GPT-6 Sol</h1><p>This model remains in the preserved three-model audit and is excluded from the current four-model comparison.</p>${route("analysis/report", "Open historical findings →", "button secondary")}`;
    return;
  }
  const summaries = summary.model_summaries.filter(
    (s) => !model || s.model === model,
  );
  $("#app").innerHTML =
    `<p class="eyebrow">Model comparisons</p><h1>${model ? label(model) : "Models in the experiment"}</h1><p class="lede">Exact requested model IDs and retained execution results. ${comparisonActive ? "GPT-4.1 and GPT-5 use the Responses API; existing Sol programs use Codex. Reasoning controls and provider context differ, so version order is not a controlled scaling experiment." : "One high-reasoning no-tool code submission per task; full provider context and checkpoint identity are not independently observable."}</p><div class="model-cards">${summaries.map((s) => route("model/" + s.model, `<h2>${label(s.model)}</h2><strong>${s.valid} / ${s.attempted}</strong><p>${comparisonActive ? "Final numeric slices · includes manual repairs" : "Numerically valid evaluation slices"}</p><p>${s.strict_format_valid} meet line limits${comparisonActive ? " after any documented repairs" : ""} · ${s.failed} not scored</p>`, "model-card")).join("")}</div><div class="section-head"><h2>Native scores by task</h2><span class="small">Slice-equal mean where multiple slices exist</span></div><div class="table-panel table-wrap"><table><thead><tr><th>Benchmark</th>${MODELS.map((m) => `<th>${label(m)}</th>`).join("")}<th>Tested reference</th><th>Metric</th></tr></thead><tbody>${summary.measured_task_ids
      .map((id) => {
        const e = catalog.entries.find((e) => e.id === id);
        if (!e) return "";
        const b = brief(id);
        return `<tr><td>${route("benchmark/" + id, esc(title(e)))}<span class="bench-sub">${id} · ${b.nSlices} slice${b.nSlices === 1 ? "" : "s"}</span></td>${MODELS.map((m) => `<td>${fmt(b.models.find((r) => r.model === m)?.score)}${b.models.find((r) => r.model === m)?.line_limit_compliant === false ? " †" : ""}</td>`).join("")}<td>${fmt(b.reference?.score)}<span class="score-caption">${b.reference ? esc(methodName(b.reference)) : "Unknown"}</span></td><td class="small">${esc(metricLabel(b.bestModel?.metric) || "No valid score")}</td></tr>`;
      })
      .join(
        "",
      )}</tbody></table></div><p class="note">These native metrics cannot be averaged into a universal model ranking. Reliability, directional improvement and reference comparisons have separate denominators. ${route("analysis", "Explore the analysis →")}</p>`;
}
function analysisPage() {
  if (comparisonActive) { generationPatternsPage(); return; }
  const classes = [
    ...new Set(summary.reference_envelopes.filter((r) => r.aggregate_eligible !== false && r.benchmark_id !== "B08" && (analysisScope === "all" || !(summary.analysis_scopes?.observed_data?.excluded_task_ids || ["B01","B03","L06","M04","N05"]).includes(r.benchmark_id))).map((r) => r.reference_class)),
  ];
  if (!classes.includes(analysisClass)) analysisClass = classes[0];
  $("#app").innerHTML =
    `<p class="eyebrow">Cross-task analysis</p><h1>Where do models improve?</h1><div class="actions">${route("analysis/practical", "Task changes, repaired runs & specialist guidance →", "button")}${route("analysis/report", "Previous cross-task analysis →", "button secondary")}</div><p class="note">First-submission suite: one generation per task. ${route("benchmark/H02/replication", "P300 now has a separate three-generation follow-up →")} Its repeated attempts are excluded from the cross-task totals below.</p><p class="lede">Track point-score changes and reference comparisons while keeping task, family, failure and evidence-class denominators visible.</p><div class="toolbar"><label for="analysis-scope" class="small">Data scope</label><select id="analysis-scope"><option value="observed_data" ${analysisScope === "observed_data" ? "selected" : ""}>Observed-data sources</option><option value="all" ${analysisScope === "all" ? "selected" : ""}>Include fully synthetic tasks</option></select></div><p class="small">Observed-data scope includes artificial corruption of real signals/trajectories (H16/A14). It excludes fully synthetic B01/B03/L06/M04 and deterministic file task N05. B08 remains visible but is excluded from aggregates in both scopes because its utility-import contract was ambiguous.</p><div class="doc-panel" style="margin-top:26px"><h2>Comparison with references</h2><div class="toolbar"><label for="reference-class" class="small">Reference evidence</label><select id="reference-class">${classes.map((c) => `<option value="${c}" ${c === analysisClass ? "selected" : ""}>${esc(c.replaceAll("_", " "))}</option>`).join("")}</select></div><div class="table-wrap"><table><thead><tr><th>Model</th><th>Point wins / slices</th><th>Lost / tied / failed</th><th>Tasks / families</th><th>Family-equal win fraction</th><th>Strict-format wins / eligible slices</th></tr></thead><tbody>${summary.model_summaries
      .map((s) => {
        const c = (analysisScope === "observed_data" ? s.observed_data_reference_class_summaries : s.reference_class_summaries)[analysisClass],
          a = c?.exploratory,
          b = c?.strict;
        return `<tr><td>${label(s.model)}</td><td>${a?.wins ?? 0} / ${a?.n_slice_comparisons ?? 0}</td><td>${a?.losses ?? 0} / ${a?.numerical_ties ?? 0} / ${a?.failed_or_missing ?? 0}</td><td>${a?.n_tasks ?? 0} / ${a?.n_families ?? 0}</td><td>${fmt(a?.family_equal_win_fraction)}</td><td>${b?.wins ?? 0} / ${b?.n_slice_comparisons ?? 0}</td></tr>`;
      })
      .join(
        "",
      )}</tbody></table></div><p class="small">Primary scientific comparator selection follows the frozen/reference policy, which can differ from the best-inspected envelope displayed on benchmark plots. No current-SOTA or matched-total-effort superiority claim.</p></div><div class="doc-panel" style="margin-top:22px"><h2>Model-version changes</h2><div class="table-wrap"><table><thead><tr><th>Pair</th><th>Improved / slices</th><th>Declined</th><th>Ties</th><th>Failed / missing</th><th>Task / family count</th><th>Family-equal improvement fraction</th></tr></thead><tbody>${summary.paired_macro_summaries
      .map((p) => {
        const a = analysisScope === "observed_data" ? p.observed_data : p.exploratory;
        return `<tr><td>${label(p.older)} → ${label(p.newer)}</td><td>${a.wins} / ${a.n_slice_comparisons}</td><td>${a.losses}</td><td>${a.numerical_ties}</td><td>${a.failed_or_missing}</td><td>${a.n_tasks} / ${a.n_families}</td><td>${fmt(a.family_equal_win_fraction)}</td></tr>`;
      })
      .join(
        "",
      )}</tbody></table></div><p class="small">M04 quadrature differences, N05 deterministic correctness and B08 utility-whitelist ambiguity are excluded from this progress aggregate. ${analysisScope === "observed_data" ? "This view excludes fully synthetic B01, B03 and L06; artificial corruption tasks remain included." : "This view includes fully synthetic B01, B03 and L06, plus artificial corruption tasks."} Other failed or missing attempts remain in the denominator; B08 is explicitly excluded, not counted as a capability failure. New datasets or simulations are not automatically independent biological replications.</p></div><details open><summary>How aggregation works</summary><p>For descriptive directional win fractions, average slices within task, tasks within category, then categories equally. Incompatible native metric deltas are never averaged. A numerical difference above1e−9 is a point win, not statistical significance or a practical-equivalence threshold. One generated program per version, convenience-selected tasks and public labels prevent causal scaling conclusions.</p></details><div class="actions"><a class="button secondary" href="data/summary.json" download>All derived statistics ↓</a><a class="button secondary" href="data/measurements.csv" download>Measurements ↓</a>${link(GH + "/blob/main/analysis/findings.md", "Interpretation & limitations", "button secondary")}</div>`;
  $("#analysis-scope").onchange = (e) => {
    analysisScope = e.target.value;
    analysisPage();
  };
  $("#reference-class").onchange = (e) => {
    analysisClass = e.target.value;
    analysisPage();
  };
}
function methodsPage() {
  $("#app").innerHTML =
    `<p class="eyebrow">Methods & data</p><h1>Trace every result.</h1><p class="lede">A benchmark is an exact input, target, split, scorer and model procedure. The broader neuroscience evidence map remains separate from the measured results explorer.</p><div class="doc-grid"><section class="doc-panel"><h2>What is measured</h2><p>T3: a single general-model code submission followed by local numerical execution. Models use general scientific libraries; specialist packages and pretrained assets are separate references. This does not directly measure native raw-signal understanding or full autonomous lab workflows.</p><p>Exact prompts, frozen data/code hashes, submitted programs, generation usage/tool counts, predictions and errors are retained. Current general models: ${MODELS.map(label).join(", ")}. ${comparisonActive ? "GPT-4.1 and GPT-5 were generated through the Responses API; the Sol submissions came through Codex. Provider context, reasoning controls and repair histories differ. The historical audit retains GPT-6 Sol." : "This historical snapshot includes GPT-6 Sol."}</p></section><section class="doc-panel"><h2>Specialist evidence</h2><p>Named specialist methods appear on line charts and bar plots wherever verified matching predictions exist. Archived specialist masks/predictions, local specialist reproductions, conventional baselines and mathematical audits are identified separately.</p><p>The highest inspected point score is a descriptive test-selected envelope. It cannot certify the current global best, comparable training inputs or equal tuning effort. Published scores on a different split are not inserted into these plots.</p></section></div><div class="doc-grid"><section class="doc-panel"><h2>Coverage and exclusions</h2><p>The historical evidence map covers 114 task-resource associations across 14 families. The active catalog is pruned when a reusable endpoint, data rights, release or scorer is unresolved. Concrete high-effort tasks remain candidates, with missing results shown as unknown.</p><p>Pruning does not prove exhaustive coverage. Removed candidates retain their decision trail and reactivation requirements. Broad clinical, causal, control and mechanistic perspectives still have gaps.</p>${route("excluded", "Inspect archived candidates →")}</section><section class="doc-panel"><h2>Validity controls</h2><p>Biological grouping, human vs synthetic truth, adaptation policy and reference information access are explicit per task. Source identities, acquired-file/buffer hashes and scorer checks are recorded. Failures and formatting deviations stay visible.</p><p>Small biological samples, public-label contamination, unequal specialist histories and one-generation uncertainty remain. No neuron/frame pseudo-replication intervals or universal mixed-metric capability score.</p></section></div><div class="link-list">${[
      ["README.md", "Main research plan and status"],
      ["docs/release-v11.md", "Original 30-task release report"],
      ["docs/generation-extension.md", "Four-model extension: design and audit trail"],
      ["docs/progress-assessment.md", "Progress assessment and evidence gaps"],
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
async function currentComparisonData() {
  const responses = await Promise.all([fetch("data/comparison-summary.json"), fetch("data/comparison-measurements.jsonl")]);
  if (responses.every(r => r.status === 404 || !r.ok)) return null;
  if (responses.some(r => !r.ok)) throw Error("Current comparison payload is incomplete");
  const [s, text] = await Promise.all([responses[0].json(), responses[1].text()]);
  if (JSON.stringify(s.models) !== JSON.stringify(COMPARISON_MODELS)) throw Error("Unexpected comparison model order");
  const rs = text.trim().split("\n").filter(Boolean).map(v => JSON.parse(v));
  if (rs.some(r => r.model === "gpt-6-sol")) throw Error("Historical GPT-6 Sol leaked into current measurements");
  return {summary:s, records:rs};
}
Promise.all([
  fetch("data/catalog.json").then((r) => r.json()),
  fetch("data/summary.json").then((r) => r.json()),
  fetch("data/measurements.jsonl").then((r) => r.text()),
  fetch("data/exclusions.json")
    .then((r) => (r.ok ? r.json() : []))
    .catch(() => []),
  currentComparisonData(),
  fetch("data/H02-replication.json").then((r) => {
    if (!r.ok) throw new Error("Replication results unavailable");
    return r.json();
  }),
])
  .then(([c, s, t, x, current, rep]) => {
    catalog = c;
    summary = s;
    replication = rep;
    records = t
      .trim()
      .split("\n")
      .filter(Boolean)
      .map((v) => JSON.parse(v));
    historicalRecords = records.map(row => ({...row}));
    if (current) { summary = current.summary; records = current.records; MODELS = [...COMPARISON_MODELS]; comparisonActive = true; }
    excluded = Array.isArray(x) ? x : x.entries || x.decisions || [];
    draw();
  })
  .catch((e) => {
    $("#app").innerHTML =
      "<h1>Results could not load</h1><p>Please reload, or inspect the source repository.</p>";
    console.error(e);
  });
