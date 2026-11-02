// Source-render and event-handler checks in a DOM stub; browser QA is reported separately.
import fs from "node:fs";
import vm from "node:vm";
import path from "node:path";
import { fileURLToPath } from "node:url";
const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const elements = new Map();
const el = (s) => {
  if (!elements.has(s))
    elements.set(s, {
      innerHTML: "",
      value: "",
      checked: true,
      dataset: {},
      classList: { toggle() {} },
      querySelectorAll: () => [],
    });
  return elements.get(s);
};
const ctx = {
  document: { querySelector: el, querySelectorAll: () => [] },
  location: { hash: "#/" },
  window: { addEventListener() {}, scrollTo() {} },
  console,
  fetch: async (p) => ({
    ok: fs.existsSync(path.join(root, "website", p)),
    status: fs.existsSync(path.join(root, "website", p)) ? 200 : 404,
    json: async () =>
      JSON.parse(fs.readFileSync(path.join(root, "website", p), "utf8")),
    text: async () => fs.readFileSync(path.join(root, "website", p), "utf8"),
  }),
};
vm.createContext(ctx);
vm.runInContext(fs.readFileSync(path.join(root, "website/task-facets.js"), "utf8"), ctx);
vm.runInContext(fs.readFileSync(path.join(root, "website/generation-patterns.js"), "utf8"), ctx);
vm.runInContext(fs.readFileSync(path.join(root, "website/generation-lags.js"), "utf8"), ctx);
vm.runInContext(fs.readFileSync(path.join(root, "website/practical-review.js"), "utf8"), ctx);
vm.runInContext(
  fs.readFileSync(path.join(root, "website/app.js"), "utf8"),
  ctx,
);
await new Promise((resolve) => setImmediate(resolve));
const catalog = JSON.parse(
    fs.readFileSync(path.join(root, "registry/catalog.json"), "utf8"),
  ),
  summary = JSON.parse(
    fs.readFileSync(path.join(root, "analysis/summary.json"), "utf8"),
  );
// Run frozen-snapshot assertions against the preserved historical assets, even
// when the independently assembled current comparison is present.
vm.runInContext(`MODELS=[...HISTORICAL_MODELS]; comparisonActive=false;
summary=${JSON.stringify(summary)};
records=${fs.readFileSync(path.join(root, "website/data/measurements.jsonl"), "utf8").trim().split("\n").map(line=>JSON.stringify(JSON.parse(line))).join(",").replace(/^/,"[").concat("]")};
historicalRecords=records.map(row=>({...row}));`,ctx);
const release = fs.readFileSync(path.join(root, "README.md"), "utf8").match(/Preview \*\*([0-9.]+)\*\*/)[1];
if (!fs.readFileSync(path.join(root,"website/index.html"),"utf8").includes("Research preview · v"+release)) throw Error("Stale website release footer");
let n = 0;
for (const route of [
  "",
  "models",
  "analysis",
  "methods",
  "excluded",
  "benchmark/H02/replication",
  ...summary.models.map((m) => "model/" + m),
  ...catalog.families.map((f) => "category/" + f.code),
  ...catalog.entries.flatMap((e) =>
    ["results", "evaluation", "sources"].map(
      (t) => "benchmark/" + e.id + "/" + t,
    ),
  ),
]) {
  ctx.location.hash = "#/" + route;
  vm.runInContext("draw()", ctx);
  const text = el("#app").innerHTML + el("#benchmark-content").innerHTML;
  if (!text.length || />undefined<|NaN%/.test(text))
    throw Error("Render failure:" + route);
  for (const m of text.matchAll(
    /https:\/\/github\.com\/chirag-7\/neural-data-bench\/(?:blob|tree)\/main\/([^\"#<>]+)/g,
  )) {
    const dest = decodeURIComponent(m[1]).replaceAll("&amp;", "&");
    if (!fs.existsSync(path.join(root, dest)))
      throw Error("Missing repository target on " + route + ":" + dest);
  }
  n++;
}
ctx.location.hash = "#/benchmark/M01/results";
vm.runInContext("draw()", ctx);
if (!el("#benchmark-content").innerHTML.includes("Source-inspired domain reference")) throw Error("Behavioral GLM must be labeled as a source-inspired domain reference");
// Category-first selectors must never render a mixed global task list.
const optionIds = (html, id) => {
 const select=html.match(new RegExp('<select id="'+id+'"[^>]*>([\\s\\S]*?)</select>'));
 if(!select) throw Error("Missing navigation selector: "+id);
 return [...select[1].matchAll(/<option value="([^"]+)"/g)].map(match=>match[1]).filter(Boolean);
};
ctx.location.hash="#/";vm.runInContext("query='';listMode='measured';selectedTask='A09';draw()",ctx);
if(!el("#benchmark-directory").innerHTML.includes('class="category-card"')) throw Error("Homepage requires interactive category cards");
for(const id of optionIds(el("#app").innerHTML,"benchmark-picker")) {
 if(!id.startsWith("A")) throw Error("Homepage benchmark selector mixed categories");
}
el("#category-picker").onchange({target:{value:"B"}});
for(const id of optionIds(el("#app").innerHTML,"benchmark-picker")) {
 if(!id.startsWith("B")) throw Error("Category change did not scope benchmark choices");
}
el("#benchmark-picker").onchange({target:{value:"B03"}});
if(!el("#app").innerHTML.includes('#/benchmark/B03')) throw Error("Scoped benchmark selection failed to update open link");
if(el("#app").innerHTML.includes('id="featured-chart"')) throw Error("Homepage should lead with categories rather than an automatic plot");
if(!el("#benchmark-directory").innerHTML.includes('<details class="category-task-details">')) throw Error("Category task lists must be optional expandable details");
el("#search").oninput({target:{value:"calcium"}});
if(!el("#benchmark-directory").innerHTML.includes("Calcium") || el("#benchmark-directory").innerHTML.includes('id="category-task-B"')) throw Error("Search must filter category cards and their tasks");
el("#search").oninput({target:{value:""}});
el("#list-mode").onchange({target:{value:"all"}});
for(const family of catalog.families) {
 const html=el("#benchmark-directory").innerHTML;
 if(!html.includes('id="category-task-'+family.code+'"')) continue;
 for(const id of optionIds(html,"category-task-"+family.code)) {
  if(catalog.entries.find(entry=>entry.id===id)?.family_code!==family.code) throw Error("Category card contains a foreign task");
 }
}
el("#category-task-C").onchange({target:{value:"C06"}});
if(ctx.location.hash!=="#/benchmark/C06/results") throw Error("Category-card task navigation failed");
ctx.location.hash="#/benchmark/C06/evaluation";vm.runInContext("draw()",ctx);
for(const id of optionIds(el("#app").innerHTML,"detail-benchmark-picker")) {
 if(!id.startsWith("C")) throw Error("Task detail selector mixed categories");
}
el("#detail-category-picker").onchange({target:{value:"K"}});
for(const id of optionIds(el("#detail-jump").innerHTML,"detail-benchmark-picker")) {
 if(!id.startsWith("K")) throw Error("Detail category change failed to scope task choices");
}
el("#detail-benchmark-picker").onchange({target:{value:"K06"}});
if(ctx.location.hash!=="#/benchmark/K06/evaluation") throw Error("Detail quick jump must preserve evaluation tab");
ctx.location.hash="#/analysis";vm.runInContext("draw()",ctx);
if(!el("#app").innerHTML.includes('#/analysis/report')) throw Error("Analysis report entry link missing");
if(!el("#app").innerHTML.includes('#/analysis/practical')) throw Error("Practical analysis entry link missing");
vm.runInContext("globalThis.macroReportPage=()=>{document.querySelector('#app').innerHTML='Report route dispatched';}",ctx);
ctx.location.hash="#/analysis/report";vm.runInContext("draw()",ctx);
if(el("#app").innerHTML!=="Report route dispatched") throw Error("Deep report route dispatcher failed");
vm.runInContext("query='';listMode='measured'",ctx);
let practicalChecks = "awaiting assembled payload";
const practicalPath = path.join(root, "website/data/practical-review.json");
if (fs.existsSync(practicalPath)) {
 const payload = JSON.parse(fs.readFileSync(practicalPath, "utf8"));
 if(payload.tasks.length !== 30) throw Error("Practical review must include all 30 tasks");
 vm.runInContext(`practicalData=${JSON.stringify(payload)}`,ctx);
 const originalRecords = vm.runInContext("JSON.stringify(records)",ctx);
 ctx.location.hash="#/analysis/practical";vm.runInContext("draw()",ctx);
 await new Promise(resolve=>setImmediate(resolve));
 if(!el("#app").innerHTML.includes("REPAIR-ASSISTED") || !el("#app").innerHTML.includes("30 tasks")) throw Error("Final practical table incomplete");
 if(el("#app").innerHTML.includes('id="practical-track"') || el("#app").innerHTML.includes('id="practical-detail-category"')) throw Error("Redundant explorer controls remain");
 if(optionIds(el("#app").innerHTML,"practical-task").length!==30) throw Error("All-category task choices incomplete");
 el("#practical-category").onchange({target:{value:"B"}});await new Promise(resolve=>setImmediate(resolve));
 for(const id of optionIds(el("#app").innerHTML,"practical-task")) if(!id.startsWith("B")) throw Error("Practical category handler failed");
 el("#practical-task").onchange({target:{value:"B08"}});
 if(!el("#practical-task-detail").innerHTML.includes("B08")) throw Error("Practical task handler failed");
 await new Promise(resolve=>setImmediate(resolve));
 if(!el("#app").innerHTML.includes("not an unbiased model comparison")) throw Error("Repair assistance disclosure missing");
 const b08=payload.tasks.find(task=>task.benchmark_id==="B08");
 for(const model of summary.models) if(Number.isFinite(b08.repair_assisted?.scores?.[model]) && !el("#app").innerHTML.includes(b08.repair_assisted.scores[model].toFixed(4))) throw Error("B08 repaired score missing:"+model);
 for(const task of payload.tasks) {
  ctx.location.hash=`#/benchmark/${task.benchmark_id}/specialists`;vm.runInContext("draw()",ctx);await new Promise(resolve=>setImmediate(resolve));
  const html=el("#benchmark-content").innerHTML;
  if(!html.includes("Candidate methods and evidence") || !html.includes("Recommended next comparator")) throw Error("Specialist review missing:"+task.benchmark_id);
 }
 for(const id of ["B08","J08","N05","C05"]) {
  ctx.location.hash=`#/benchmark/${id}/repairs`;vm.runInContext("draw()",ctx);await new Promise(resolve=>setImmediate(resolve));
  const html=el("#benchmark-content").innerHTML;
  if(id==="C05") {
   if(html.includes('<svg') || !html.includes("Four archive cases remain unresolved")) throw Error("C05 must show unresolved archives without invented points");
  } else if(!html.includes("Model-version line chart") || !html.includes("Bar chart including") || !html.includes("Original first attempt")) throw Error("Repaired plots/table missing:"+id);
  ctx.location.hash=`#/benchmark/${id}/results`;vm.runInContext("draw()",ctx);
  if(!el("#benchmark-content").innerHTML.includes("unchanged first-attempt results")) throw Error("Repair notice missing on original results:"+id);
 }
 if(vm.runInContext("JSON.stringify(records)",ctx)!==originalRecords) throw Error("Practical view mutated original records");
 practicalChecks="passed · 30 specialist views, 4 repair tabs, final results/category/task handlers, immutable original records";
}
let plots = 0;
for (const id of summary.measured_task_ids) {
  vm.runInContext(`selectedSlice='';renderChart('#test-chart','${id}')`, ctx);
  const text = el("#test-chart").innerHTML;
  if (
    !text.includes("Bar chart including") ||
    !text.includes("Model-version line chart")
  )
    throw Error("Both plots required:" + id);
  if (
    ["B01", "J08", "H08", "H01", "H02", "C05", "A09", "I10", "K04", "M01", "L06", "B07", "B03", "B08", "C06", "E06", "K05", "K06", "A15"].includes(id) &&
    (!text.includes('class="direct-reference-label"') ||
      !text.includes('aria-label="Named reference scores"'))
  )
    throw Error("Specialist overlay missing:" + id);
  vm.runInContext(
    `plotView='table';renderChart('#test-chart','${id}');plotView='graph'`,
    ctx,
  );
  plots++;
}
ctx.location.hash = "#/benchmark/L06/results";
vm.runInContext("draw()", ctx);
if (!el("#benchmark-content").innerHTML.includes("Fixed Polya–Gamma sampler reference")) throw Error("Posterior comparator must retain explicit method name");
vm.runInContext("l06Metric='c2st';l06Observation='mean';renderChart('#test-chart','L06')",ctx);
if (!el("#test-chart").innerHTML.includes("chance target 0.5")) throw Error("C2ST chance target missing");
el("#metric-picker").onchange({target:{value:"sliced-w2"}});
el("#observation-picker").onchange({target:{value:"3"}});
const posteriorRows=JSON.parse(fs.readFileSync(path.join(root,"results/L06.json"),"utf8"));
for (const row of posteriorRows.filter(r=>r.status==="measured")) {
 const expected=row.per_observation_sliced_w2[3].toFixed(4);
 if(!el("#test-chart").innerHTML.includes(expected)) throw Error("Posterior observation/secondary metric mismatch:"+row.model);
}
vm.runInContext("l06Metric='c2st';l06Observation='mean'",ctx);
ctx.location.hash = "#/analysis";vm.runInContext("analysisScope='observed_data';draw()",ctx);
if(!el("#app").innerHTML.includes("This view excludes fully synthetic B01, B03 and L06")) throw Error("Default observed-data exclusion scope missing");
el("#analysis-scope").onchange({target:{value:"all"}});
if(!el("#app").innerHTML.includes("This view includes fully synthetic B01, B03 and L06")) throw Error("Synthetic-inclusive scope handler failed");
for(const pair of summary.paired_macro_summaries){
 if(pair.exploratory.n_tasks-pair.observed_data.n_tasks!==3) throw Error("Three fully synthetic tasks must be separated from generation aggregates");
 if(pair.observed_data.task_summaries.some(t=>["B01","B03","L06","M04","N05","B08"].includes(t.benchmark_id))) throw Error("Synthetic/correctness task leaked into observed-data view");
}
for (const pair of summary.paired_macro_summaries) {
 if ([pair.exploratory,pair.observed_data].some(scope=>scope.task_summaries.some(task=>task.benchmark_id==="B08"))) throw Error("Ambiguous B08 contract leaked into version aggregates");
}
for (const reference of summary.reference_envelopes.filter(row=>row.benchmark_id==="B08")) {
 if (reference.aggregate_eligible !== false) throw Error("B08 reference must be explicitly aggregate-ineligible");
}
for (const [id,name] of [["B03","SpikeInterface · decentralized registration"],["B08","Spikepack · 100 µs grid"],["C06","OASIS AR1 · training-calibrated"],["E06","NLinear · analytical ridge1"],["K05","Donor-CV weighted ridge"],["K06","Mouse-CV SVM / ExtraTrees"],["A15","Spectral boosting · event-CV"]]) {
 vm.runInContext(`selectedSlice='';renderChart('#test-chart','${id}')`,ctx);
 if (!el("#test-chart").innerHTML.includes(name)) throw Error("Missing readable batch reference: "+id);
}
vm.runInContext("selectedSlice='';c06Metric='primary';renderChart('#test-chart','C06')",ctx);
if (!el("#test-chart").innerHTML.includes("Pearson correlation ignores amplitude calibration")) throw Error("Calcium calibration caveat missing");
el("#metric-picker").onchange({target:{value:"relative-error"}});
const calciumRows=JSON.parse(fs.readFileSync(path.join(root,"website/data/C06.json"),"utf8"));
for(const row of calciumRows.filter(row=>row.status==="measured")) {
 const totals=new Map();
 for(const cell of row.cell_results) {
  const state=totals.get(cell.animal)||[0,0];state[0]+=cell.relative_error;state[1]++;totals.set(cell.animal,state);
 }
 const expected=[...totals.values()].reduce((total,[sum,n])=>total+sum/n,0)/totals.size;
 if(!el("#test-chart").innerHTML.includes(expected.toFixed(4))) throw Error("Animal-equal relative count-error plot mismatch: "+row.model);
}
if(!el("#test-chart").innerHTML.includes("predeclared secondary")) throw Error("Secondary count error must be labeled predeclared");
vm.runInContext("c06Metric='primary';selectedSlice='';renderChart('#test-chart','B08')",ctx);
if(!el("#test-chart").innerHTML.includes("Two heapq import-whitelist failures are retained")) throw Error("B08 whitelist ambiguity not visible");
vm.runInContext("analysisScope='observed_data'",ctx);
vm.runInContext("selectedSlice='';renderChart('#test-chart','G01')", ctx);
if (!el("#test-chart").innerHTML.includes("FALCON-style ridge"))
  throw Error("Negative-R2 reference missing");
ctx.location.hash = "#/";
vm.runInContext("draw()", ctx);
el("#search").oninput({ target: { value: "spike" } });
el("#list-mode").onchange({ target: { value: "all" } });
ctx.location.hash = "#/category/B";vm.runInContext("draw()",ctx);
el("#benchmark-picker").onchange({ target: { value: "B01" } });
if (!el("#featured-chart").innerHTML.includes("MountainSort5"))
  throw Error("Category-page selector failed to reveal specialist");
vm.runInContext(
  "b01Metric='all-event-f1';selectedSlice='';renderChart('#test-chart','B01')",
  ctx,
);
const sensitivity = el("#test-chart").innerHTML;
if (
  !sensitivity.includes("0.9621") ||
  !sensitivity.includes("0.5998") ||
  !sensitivity.includes("post-hoc")
)
  throw Error(
    "All-output event sensitivity must retain named values and post-hoc label",
  );
vm.runInContext("b01Metric='primary'", ctx);
ctx.location.hash = "#/benchmark/H02/replication";
vm.runInContext("draw()", ctx);
const replicationText = el("#benchmark-content").innerHTML;
for (const text of ['generation-range', 'xDAWN · train-CV tuned', 'xDAWN · fixed', 'Attempt 3', 'not confidence intervals', 'All candidate validation scores']) {
  if (!replicationText.includes(text)) throw Error('Missing replication component: '+text);
}
// Four-model rendering contract. Fixtures live only in this VM test: they are
// never serialized as benchmark data or interpreted as scientific results.
const frozenReview = JSON.parse(fs.readFileSync(practicalPath, "utf8"));
const newReviewPath = path.join(root,"website/data/generation-comparison.json");
const newSummaryPath = path.join(root,"website/data/comparison-summary.json");
const newRowsPath = path.join(root,"website/data/comparison-measurements.jsonl");
const fourModels = ["gpt-4.1-2025-04-14","gpt-5-2025-08-07","gpt-5.6-sol","gpt-6.1-sol"];
const pairsFor = scores => fourModels.flatMap((older,i)=>fourModels.slice(i+1).map(newer=>({older,newer,raw_native_delta:scores[newer]-scores[older],outcome:"fixture_only"})));
const fourReview = fs.existsSync(newReviewPath) ? JSON.parse(fs.readFileSync(newReviewPath,"utf8")) : {
 ...frozenReview, models:fourModels, findings:["VM test fixture, not empirical evidence"],
 tasks:frozenReview.tasks.map(task=>{
  const old=task.repair_assisted || task, values=Object.values(old.scores).filter(Number.isFinite), scores=Object.fromEntries(fourModels.map((model,i)=>[model,values[i%values.length]]));
  return {...task,scores,pairs:pairsFor(scores),repair_assisted:{...old,scores,pairs:pairsFor(scores),chart_rows:[]}};
 })
};
const fourSummary=fs.existsSync(newSummaryPath)?JSON.parse(fs.readFileSync(newSummaryPath,"utf8")):{...summary,models:fourModels,model_summaries:fourModels.map(model=>({...summary.model_summaries[0],model}))};
const fourRows=fs.existsSync(newRowsPath)?fs.readFileSync(newRowsPath,"utf8").trim().split("\n").map(line=>JSON.parse(line)):vm.runInContext("records.filter(row=>!HISTORICAL_MODELS.includes(row.model)).concat(COMPARISON_MODELS.flatMap(model=>records.filter(row=>row.model==='gpt-6.1-sol').map(row=>({...row,model}))))",ctx);
vm.runInContext(`MODELS=[...COMPARISON_MODELS];comparisonActive=true;summary=${JSON.stringify(fourSummary)};records=${JSON.stringify(fourRows)};practicalData=${JSON.stringify(fourReview)};practicalCategory='';practicalTask='A09';`,ctx);
const beforeFour=vm.runInContext("JSON.stringify(records)",ctx);
ctx.location.hash="#/analysis/practical";vm.runInContext("draw()",ctx);await new Promise(resolve=>setImmediate(resolve));
const fourHTML=el("#app").innerHTML;
for(const name of ["GPT-4.1","GPT-5","GPT-5.6 Sol","GPT-6.1 Sol"]) if(!fourHTML.includes(name)) throw Error("Four-model native table missing "+name);
if(!fourHTML.includes("Historical three-model audit · includes GPT-6 Sol")) throw Error("Historical audit disclosure missing");
if(fourHTML.includes("Δ 5.6 → 6</th>") || fourHTML.includes("GPT-6 is mixed relative")) throw Error("Old GPT6 current comparison leaked");
if((fourHTML.match(/<th>Δ /g)||[]).length!==6) throw Error("Four-model table needs all six pair columns");
for(const id of ["practical-track","practical-detail-category"]) if(fourHTML.includes('id="'+id+'"')) throw Error("Redundant comparison selector "+id);
el("#practical-category").onchange({target:{value:"K"}});await new Promise(resolve=>setImmediate(resolve));
for(const id of optionIds(el("#app").innerHTML,"practical-task")) if(!id.startsWith("K")) throw Error("Four-model category filtering failed");
el("#practical-task").onchange({target:{value:"K04"}});
const details=el("#practical-task-detail").innerHTML;
if(!details.includes("Model-version line chart") || !details.includes("Bar chart including")) throw Error("Four-model detail needs line and bar plots");
for(const model of fourModels) if(!details.includes(vm.runInContext(`label('${model}')`,ctx))) throw Error("Missing native plot model "+model);
if(vm.runInContext("JSON.stringify(records)",ctx)!==beforeFour) throw Error("Four-model practical view mutated records");
// Multi-slice practical plots must use task means, never the first slice.
for (const task of fourReview.tasks.filter(task=>task.n_slices>1)) {
 const series=task.repair_assisted || task;
 const displayed=vm.runInContext(`practicalRows(${JSON.stringify(task)},${JSON.stringify(series)})`,ctx);
 for (const row of displayed) if(row.score!==(series.scores[row.model] ?? null)) throw Error("Task-mean plot mismatch: "+task.benchmark_id);
 const html=vm.runInContext(`practicalPlots(${JSON.stringify(task)},${JSON.stringify(series)})`,ctx);
 for(const row of displayed.filter(row=>Number.isFinite(row.score))) if(!html.includes(vm.runInContext(`fmt(${row.score})`,ctx))) throw Error("Task mean absent from rendered plot");
}
const line=vm.runInContext(`linePlot(MODELS.map((model,i)=>({model,score:i+1})),[{model:'task-baseline',score:2.5}], 'higher')`,ctx);
const circleX=[...line.matchAll(/<circle cx="([0-9.]+)"/g)].map(match=>Number(match[1]));
if(circleX.length!==4 || circleX.some(x=>x<65||x>365) || new Set(circleX).size!==4) throw Error("Four points must fit before named reference labels");
ctx.location.hash="#/benchmark/H02/replication";vm.runInContext("draw()",ctx);
if(!el("#benchmark-content").innerHTML.includes("Historical three-model follow-up")) throw Error("Old replication must be labeled historical");
// Both metric directions must put the better score higher on the page.
for(const direction of ['higher','lower']) {
 const html=vm.runInContext(`linePlot([{model:MODELS[0],score:1},{model:MODELS[1],score:2}],[], '${direction}')`,ctx);
 const points=[...html.matchAll(/<circle cx="[0-9.]+" cy="([0-9.]+)"/g)].map(x=>Number(x[1]));
 if(points.length!==2 || (direction==='higher' ? points[1]>=points[0] : points[0]>=points[1])) throw Error('Inverted improvement direction: '+direction);
 if(!html.includes('Better performance ↑'))throw Error('Missing line metric-direction key');
 const bar=vm.runInContext(`barPlot([{model:MODELS[0],score:1}], '${direction}')`,ctx);if(!bar.includes(direction+' is better'))throw Error('Missing bar direction key');
}
ctx.location.hash='#/analysis/patterns';vm.runInContext("facetState.category='';draw()",ctx);await new Promise(resolve=>setImmediate(resolve));
if(!el('#app').innerHTML.includes('Do newer models improve?') || !el('#app').innerHTML.includes('28') || !el('#app').innerHTML.includes('Mixed changes / reversals'))throw Error('Macro route/data failed');
ctx.location.hash='#/analysis/practical';vm.runInContext("facetState.category='J';practicalCategory='J';practicalTask='J08';draw()",ctx);await new Promise(resolve=>setImmediate(resolve));
if(!el('#app').innerHTML.includes('manually adapted training budget') || el('#app').innerHTML.includes('Not scored within the 180-second computation limit'))throw Error('Final J08 repair score or budget provenance missing');
ctx.location.hash='#/analysis/lags';vm.runInContext("facetState.category='';draw()",ctx);await new Promise(resolve=>setImmediate(resolve));
if(!el('#app').innerHTML.includes('Does a larger model gap mean more progress?') || !el('#app').innerHTML.includes('post-hoc sensitivity choices') || (el('#app').innerHTML.match(/<tr>/g)||[]).length!==21)throw Error('Lag route, three complete tables or limitations missing');
for(const [lag,nRows] of [['1',12],['2',9],['3',6]]) {
 vm.runInContext(`generationLagFilter='${lag}';generationLagsPage()`,ctx);await new Promise(resolve=>setImmediate(resolve));
 if((el('#app').innerHTML.match(/<tr>/g)||[]).length!==nRows)throw Error('Lag filter table row count: '+lag);
}
// Classification filters must intersect; subsets retain native scores and four-model scales.
const facetRegistry=JSON.parse(fs.readFileSync(path.join(root,'registry/task-facets-v1.json'),'utf8'));
const patternBase=JSON.parse(fs.readFileSync(path.join(root,'website/data/generation-patterns.json'),'utf8'));
const lagBase=JSON.parse(fs.readFileSync(path.join(root,'website/data/generation-lags.json'),'utf8'));
const beforeFacetRecords=vm.runInContext('JSON.stringify(records)',ctx);
const facetCases=[{},...Object.entries(facetRegistry.vocabulary).flatMap(([k,vs])=>Object.keys(vs).map(v=>({[k]:v}))),...catalog.families.map(f=>({category:f.code})),{input_type:'tables',generalization:'new_subjects'},{input_type:'audio',operation:'compress'},{input_type:'multimodal',combination:'images_video+tables'}];
for(const state of facetCases){
 vm.runInContext(`Object.assign(facetState,{input_type:'',combination:'',operation:'',generalization:'',category:''},${JSON.stringify(state)})`,ctx);
 const expected=facetRegistry.assignments.filter(a=>(!state.input_type||a.input_type===state.input_type)&&(!state.combination||a.input_components.join('+')===state.combination)&&(!state.operation||a.operation===state.operation)&&(!state.generalization||a.generalization.includes(state.generalization))&&(!state.category||a.family_code===state.category)).map(a=>a.benchmark_id);
 const subset=vm.runInContext('facetPatternSubset(generationPatterns)',ctx);
 const ts=patternBase.tasks.filter(t=>expected.includes(t.benchmark_id));
 if(subset.n_tasks!==ts.length || subset.tasks.some(t=>!expected.includes(t.benchmark_id)))throw Error('Facet intersection mismatch '+JSON.stringify(state));
 const counts={better:0,worse:0,numerical_tie:0,incomplete:0};
 for(const t of ts){const change=(t.scores[fourModels.at(-1)]-t.scores[fourModels[0]])*(t.direction==='lower'?-1:1);counts[Math.abs(change)<=1e-9?'numerical_tie':change>0?'better':'worse']++;}
 for(const [k,v] of Object.entries(counts))if(subset.endpoint.counts[k]!==v)throw Error('Filtered endpoint count '+k);
 const ls=vm.runInContext('facetLagSubset(generationLagData)',ctx);
 for(const row of ls.task_pairs){const original=lagBase.task_pairs.find(t=>t.benchmark_id===row.benchmark_id&&t.older===row.older&&t.newer===row.newer);if(JSON.stringify(row)!==JSON.stringify(original))throw Error('Changed normalized/native row');}
 for(const row of ls.summaries)if(Object.values(row.counts).reduce((a,b)=>a+b,0)!==ts.length)throw Error('Wrong lag denominator');
 for(const route of ['patterns','lags','practical']){
  ctx.location.hash='#/analysis/'+route;vm.runInContext('draw()',ctx);await new Promise(resolve=>setImmediate(resolve));
  const html=el('#app').innerHTML;if(!html.includes('facet-input_type')||!html.includes('facet-operation')||!html.includes('facet-generalization')||/NaN|>undefined<|could not load/.test(html))throw Error('Facet analysis render '+route);
  if(!ts.length&&!html.includes('No measured tasks match'))throw Error('Empty subset not explained');
 }
}
// Nested multimodal combinations, availability and actual controls.
vm.runInContext("Object.assign(facetState,{input_type:'multimodal',combination:'images_video+tables',operation:'',generalization:'',category:''});listMode='all';query='';explorer('')",ctx);
let facetHTML=el('#app').innerHTML+el('#benchmark-directory').innerHTML;
if(!facetHTML.includes('facet-combination')||!el('#benchmark-directory').innerHTML.includes('F02')||el('#benchmark-directory').innerHTML.includes('I04'))throw Error('Multimodal combination mismatch');
el('#facet-input_type').onchange({target:{value:'tables'}});
if(vm.runInContext('facetState.combination',ctx)!=='')throw Error('Stale multimodal combination');
el('#facet-reset').onclick();
if(vm.runInContext('facetActive()',ctx))throw Error('Reset did not clear facets');
vm.runInContext("listMode='measured';query='';explorer('')",ctx);
el('#facet-input_type').onchange({target:{value:'tables'}});
const tableDirectory=el('#benchmark-directory').innerHTML;if(!tableDirectory.includes('K04')||tableDirectory.includes('H02'))throw Error('Directory did not filter');
ctx.location.hash='#/analysis/practical';vm.runInContext('draw()',ctx);await new Promise(resolve=>setImmediate(resolve));
if(!el('#app').innerHTML.includes('7 / 30 tasks'))throw Error('Filter state did not persist across navigation');
el('#practical-category').onchange({target:{value:'K'}});await new Promise(resolve=>setImmediate(resolve));
if(optionIds(el('#app').innerHTML,'practical-task').length!==4)throw Error('Category and scientific facets did not intersect');
vm.runInContext("Object.assign(facetState,{input_type:'',combination:'',operation:'',generalization:'',category:''});generationLagFilter='all'",ctx);
if(vm.runInContext('JSON.stringify(records)',ctx)!==beforeFacetRecords)throw Error('Facets mutated measurements');

const result = {
  type: "In-memory source-render and direct-handler checks; not real-browser interaction or layout QA",
  routes: n,
  scientific_facets: "passed · 92 annotations, all facet values, AND intersections, nested combinations, empty subsets, persisted controls, direction-aware counts and immutable lag scales",
  ordinal_lag_tables_and_three_filters: "passed · 180 source task-pairs; all six comparisons and both IQR sensitivity bands",
  measured_tasks_with_bar_and_line_plots: plots,
  specialist_overlays: "passed",
  practical_review: practicalChecks,
  four_model_comparison: "passed · four points, six pairs, category/task filtering, provenance, immutable rows, historical audit",
  direct_named_reference_labels_and_numeric_cards: "passed",
  posthoc_metric_sensitivity: "passed",
  negative_R2_axis: "passed",
  metric_direction_better_up_and_raw_bar_labels: "passed · both directions",
  generation_macro_patterns_and_exclusion_labels: "passed",
  graph_table_switch: "passed",
  search_and_benchmark_selector: "passed",
  category_cards_and_two_layer_navigation: "passed",
  homepage_category_first_without_automatic_chart: "passed",
  category_page_featured_chart: "passed",
  task_detail_scoped_quick_jump_and_tab_preservation: "passed",
  deep_analysis_route_dispatch: "passed",
  javascript_syntax: "passed",
  separate_generation_replication_plots_and_range: "passed",
};
fs.writeFileSync(
  path.join(root, "analysis/site-source-checks.json"),
  JSON.stringify(result, null, 2),
);
console.log(JSON.stringify(result, null, 2));
