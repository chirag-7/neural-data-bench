// A separate, auditable analysis view. All displayed numbers come from the report payload.
let macroReportData = null;
let macroBucket = 'quantitative';
const macroEsc = (v) => String(v ?? '').replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;').replaceAll('"','&quot;');
const macroFmt = (x) => Number(x).toFixed(4);
const macroName = (v) => v.replace('gpt-','').replace('-sol',' Sol');
const MACRO_ROOT = 'https://github.com/chirag-7/neural-data-bench/blob/main/analysis/macro-patterns/';
async function macroReportPage() {
  const app = document.querySelector('#app');
  if (!macroReportData) {
    app.innerHTML = '<p class="eyebrow">Cross-benchmark synthesis</p><h1>What patterns survive the checks?</h1><p>Loading the audited analysis…</p>';
    try {
      const response = await fetch('data/macro-report.json');
      if (!response.ok) throw new Error('Report unavailable');
      macroReportData = await response.json();
    } catch (_) {
      if (location.hash.includes('analysis/report')) app.innerHTML = `<h1>Macro report</h1><p>The report could not load. <a href="${MACRO_ROOT}report.md">Read the versioned report on GitHub →</a></p>`;
      return;
    }
    if (!location.hash.includes('analysis/report')) return;
  }
  const data = macroReportData;
  const names = {quantitative:'Quantitative',qualitative:'Qualitative',combined:'Quantitative + qualitative'};
  const tasks = {C1:['C06','B01'],C2:['E06'],C3:['B08','H02']};
  app.innerHTML = `<p class="breadcrumb"><a href="#/analysis">Analysis</a> / Macro findings</p>
    <p class="eyebrow">Evidence synthesis · snapshot ${macroEsc(data.snapshot)}</p>
    <h1>${macroEsc(data.title)}</h1>
    <p class="lede">${macroEsc(data.conclusion)}</p>
    <div class="stats"><div class="stat"><strong>24</strong><span>eligible observed-data tasks</span></div><div class="stat"><strong>13</strong><span>benchmark categories</span></div><div class="stat"><strong>31</strong><span>dependent evaluation slices</span></div><div class="stat"><strong>0</strong><span>established scaling laws</span></div></div>
    <div class="note">A descriptive signal is different from statistical proof. The category-level diagnostics do not reject their assumed null after adjustment. That also does not establish that all differences are noise. Measurement scores and original failures remain unchanged.</div>
    <div class="macro-tabs" role="tablist" aria-label="Finding type">${Object.entries(names).map(([key,value])=>`<button role="tab" aria-selected="${key===macroBucket}" data-macro-bucket="${key}">${value}</button>`).join('')}</div>
    <section aria-label="${names[macroBucket]} findings" class="macro-findings">${data.buckets[macroBucket].map((item)=>`<article class="doc-panel"><p class="eyebrow">${macroEsc(item.id)} · ${macroEsc(item.status)}</p><h2>${macroEsc(item.title)}</h2><p>${macroEsc(item.text)}</p>${tasks[item.id]?`<div class="actions">${tasks[item.id].map(t=>`<a class="button secondary" href="#/benchmark/${t}/results">Inspect ${t} →</a>`).join('')}</div>`:''}</article>`).join('')}</section>
    <div class="doc-panel macro-section"><h2>Version comparisons: signal and uncertainty</h2><p>Directional wins use native metrics without mixing their sizes. Slices average within task; tasks within category; categories equally. The signed diagnostic counts a newer-only numerical failure as a loss. Its two-sided p-values require an assumed independent, symmetric category-contrast null.</p>
    <div class="table-wrap"><table><thead><tr><th>Comparison</th><th>Wins / losses / failed</th><th>Family-equal win fraction</th><th>Conservative signed contrast</th><th>Conditional p</th><th>Holm p · 3 pairs</th></tr></thead><tbody>${data.pairs.map(p=>`<tr><td>${macroName(p.older)} → ${macroName(p.newer)}</td><td>${p.counts.win??0} / ${p.counts.loss??0} / ${p.counts.failed_or_missing??0}${p.counts.tie?` · ${p.counts.tie} tie`:''}</td><td>${macroFmt(p.family_win)}</td><td>${macroFmt(p.conservative_net)}</td><td>${macroFmt(p.conditional_p)}</td><td>${macroFmt(p.holm_p)}</td></tr>`).join('')}</tbody></table></div>
    <p class="small">All pairs use 24 tasks / 13 categories / 31 slices here. Common-support strict sensitivity uses the same 20 tasks / 12 categories / 23 slices for all pairs. Complete-case filtering can remove an entire category; it is not automatically a fairer panel.</p></div>
    <figure class="doc-panel macro-section"><img class="macro-figure" src="data/macro-patterns.png" alt="Family-balanced version win fractions with benchmark-composition intervals, and task-balanced win fractions within reference evidence strata"><figcaption class="small">Intervals resample benchmark categories, not animals or model generations. Different reference strata contain different tasks and budgets. The dashed 0.5 guide is descriptive; ties and failures mean it is not a calibrated null.</figcaption></figure>
    <details class="doc-panel macro-section"><summary>What is excluded, and why the tests do not establish a law</summary><p>${macroEsc(data.assumptions)}</p><p>Observed scope excludes fully synthetic B01/B03/L06/M04, deterministic N05 and ambiguous B08. Artificial corruption of observed signals in A14/H16 remains included. B08’s exclusion was retrospective and is disclosed. No meaningful scientific equivalence margins were set before these results. A model-version label is not a measurement of compute, size or training data.</p></details>
    <div class="actions macro-section"><a class="button" href="${MACRO_ROOT}report.md">Full report & sensitivity tables ↗</a><a class="button secondary" href="${MACRO_ROOT}methods.md">Methods & assumptions ↗</a><a class="button secondary" href="${MACRO_ROOT}statistics.json">Complete statistics ↗</a><a class="button secondary" href="${MACRO_ROOT}main-conservative-slices.csv">Native margins & diagnostic rows ↗</a></div>
    <p class="small macro-section">Retrospective synthesis revision ${macroEsc(data.revision)}. <a href="${MACRO_ROOT}independent-review.md">Independent arithmetic and interpretation review ↗</a>. <a href="https://github.com/chirag-7/neural-data-bench/blob/main/analysis/quick-audit-v12.json">Quick check of all 30 measured tasks ↗</a>.</p>`;
  document.querySelectorAll('[data-macro-bucket]').forEach(button=>{button.onclick=()=>{macroBucket=button.dataset.macroBucket;macroReportPage();};});
}
