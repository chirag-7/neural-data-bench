// Versioned, protocol-based navigation overlay. Never modifies native measurements.
let taskFacetData = null;
const facetState = {input_type:'', combination:'', operation:'', generalization:'', category:''};
function facetAssignment(id) { return taskFacetData?.assignments.find(a=>a.benchmark_id===id); }
function facetMatches(id, useCategory=true) {
 const a=facetAssignment(id); if(!a)return false;
 return (!facetState.input_type || a.input_type===facetState.input_type) &&
 (!facetState.combination || a.input_components.join('+')===facetState.combination) &&
 (!facetState.operation || a.operation===facetState.operation) &&
 (!facetState.generalization || a.generalization.includes(facetState.generalization)) &&
 (!useCategory || !facetState.category || a.family_code===facetState.category);
}
function facetActive(useCategory=true) { return Object.entries(facetState).some(([k,v])=>v && (useCategory || k!=='category')); }
function facetName(k,v) { return taskFacetData?.vocabulary[k]?.[v]?.label || v; }
function facetBadges(id) {
 const a=facetAssignment(id); if(!a)return '';
 return `<div class="facet-badges" aria-label="Task classification"><span class="badge">${esc(a.scope==='executed'?'Executed contract':'Proposed contract')}</span>${['input_type','operation'].map(k=>`<span class="badge">${esc(facetName(k,a[k]))}</span>`).join('')}${a.input_type==='multimodal'?`<span class="badge">${esc(a.input_components.map(v=>facetName('input_type',v)).join(' + '))}</span>`:''}${a.generalization.map(v=>`<span class="badge">${esc(facetName('generalization',v))}</span>`).join('')} ${link(GH+'/blob/main/docs/task-classification/'+id+'.md','Why these labels?','small')}</div>`;
}
function facetToolbar(ids, includeCategory=false) {
 if(!taskFacetData)return '';
 const selected=ids.filter(id=>facetMatches(id,includeCategory)).length;
 const options=(k)=>`<option value="">All ${k==='input_type'?'data types':k==='operation'?'analysis tasks':'generalization settings'}</option>`+Object.entries(taskFacetData.vocabulary[k]).map(([v,o])=>`<option value="${v}" ${facetState[k]===v?'selected':''}>${esc(o.label)}</option>`).join('');
 const combos=[...new Set(taskFacetData.assignments.filter(a=>a.input_type==='multimodal').map(a=>a.input_components.join('+')))];
 return `<section class="facet-panel" aria-label="Scientific task filters"><div class="facet-heading"><strong>Filter by the evaluated task</strong><button type="button" id="facet-reset" class="facet-reset">Clear filters</button></div><div class="facet-filters">${includeCategory?`<label>Category<select id="facet-category"><option value="">All categories</option>${categoryOptions(facetState.category)}</select></label>`:''}<label>Input data type<select id="facet-input_type">${options('input_type')}</select></label><label>Analysis task<select id="facet-operation">${options('operation')}</select></label><label>Generalization setting<select id="facet-generalization">${options('generalization')}</select></label>${facetState.input_type==='multimodal'?`<label class="facet-combination">Multimodal combination<select id="facet-combination"><option value="">All combinations</option>${combos.map(v=>`<option value="${v}" ${facetState.combination===v?'selected':''}>${esc(v.split('+').map(c=>facetName('input_type',c)).join(' + '))}</option>`).join('')}</select></label>`:''}</div><p class="small facet-scope"><strong>${selected} / ${ids.length} tasks</strong> match these filters${includeCategory?' (category included)':''}. ${includeCategory?'Counts below describe this selected subset.':'Search and result availability also apply below.'} ${link(GH+'/blob/main/docs/task-classification/README.md','Definitions & scientific rationale →')}</p><details class="facet-help"><summary>What these labels mean</summary><p>Input labels describe data processed by the generated code, rather than necessarily data directly ingested by the LLM. Labels reflect executed protocols for measured tasks and provisional plans for candidates. Targets and auxiliary metadata do not make an input multimodal. No measured task currently has joint multimodal inputs.</p><p>Filters intersect and select whole tasks; all their original slices remain in the task mean. A task may have more than one generalization label. Filtered counts are descriptive, often small and dependent; they do not establish causal advantages or scaling laws. Full-panel downloads retain all original rows.</p></details></section>`;
}
function bindFacetToolbar(redraw, includeCategory=false) {
 for(const k of ['input_type','operation','generalization',...(includeCategory?['category']:[])]) {
  const el=$('#facet-'+k);if(el)el.onchange=e=>{facetState[k]=e.target.value;if(k==='input_type')facetState.combination='';redraw();};
 }
 const combo=$('#facet-combination');if(combo)combo.onchange=e=>{facetState.combination=e.target.value;redraw();};
 const reset=$('#facet-reset');if(reset)reset.onclick=()=>{for(const k of Object.keys(facetState))if(includeCategory || k!=='category')facetState[k]='';redraw();};
}
function facetDirectionSummary(tasks, models) {
 return models.flatMap((older,i)=>models.slice(i+1).map(newer=>{
  const counts={better:0,worse:0,numerical_tie:0,incomplete:0};
  for(const t of tasks){ const a=t.scores?.[older],b=t.scores?.[newer];const delta=(b-a)*(t.direction==='lower'?-1:1);counts[!Number.isFinite(a)||!Number.isFinite(b)?'incomplete':Math.abs(delta)<=1e-9?'numerical_tie':delta>0?'better':'worse']++; }
  return {scope:'all_measured_tasks',n_tasks:tasks.length,older,newer,counts};
 }));
}
function facetEndpointSubset(e, ids) {
 const task_ids=Object.fromEntries(Object.entries(e.task_ids).map(([k,v])=>[k,v.filter(id=>ids.has(id))]));
 const counts=Object.fromEntries(Object.entries(task_ids).map(([k,v])=>[k,v.length]));
 const complete_pairs=counts.better+counts.worse+counts.numerical_tie;
 return {...e,task_ids,counts,n_tasks:Object.values(counts).reduce((a,b)=>a+b,0),complete_pairs,better_fraction_of_complete:complete_pairs?counts.better/complete_pairs:0};
}
function facetPatternSubset(base) {
 const tasks=base.tasks.filter(t=>facetMatches(t.benchmark_id)),ids=new Set(tasks.map(t=>t.benchmark_id));
 const count=(rows,key)=>rows.reduce((c,t)=>(c[t[key]]=(c[t[key]]||0)+1,c),{});
 const monotonic=tasks.filter(t=>t.trajectory_class==='strictly_improving');
 const tc={strictly_improving:0,mixed_reversals:0,numerically_flat:0,strictly_declining:0,nondecreasing_with_ties:0,nonincreasing_with_ties:0,incomplete:0,...count(tasks,'trajectory_class')};
 const strict=tasks.filter(t=>t.strict_complete);
 const families=[...new Set(tasks.map(t=>t.family))];
 return {...base,tasks,n_tasks:tasks.length,n_families:families.length,n_complete_trajectories:tasks.filter(t=>t.complete_trajectory).length,
 endpoint:facetEndpointSubset(base.endpoint,ids),pair_summaries:base.pair_summaries.map(e=>facetEndpointSubset(e,ids)),strict_endpoint:facetEndpointSubset(base.strict_endpoint,ids),observed_endpoint:facetEndpointSubset(base.observed_endpoint,ids),trajectory_counts:tc,strict_complete_trajectories:strict.length,strict_trajectory_counts:count(strict,'trajectory_class'),
 monotonic_task_ids:monotonic.map(t=>t.benchmark_id),monotonic_family_count:new Set(monotonic.map(t=>t.family)).size,
 diminishing_gains:{...base.diminishing_gains,n_monotonic:monotonic.length,strictly_diminishing:monotonic.filter(t=>t.diminishing_every_step).length,last_smaller_than_first:monotonic.filter(t=>t.last_gain_smaller_than_first).length},
 metric_direction_counts:{higher:tasks.filter(t=>t.direction==='higher').length,lower:tasks.filter(t=>t.direction==='lower').length},
 family_summaries:families.map(f=>{const ts=tasks.filter(t=>t.family===f);return {family:f,name:ts[0].family_name,n_tasks:ts.length,strictly_improving:ts.filter(t=>t.trajectory_class==='strictly_improving').length,mixed_reversals:ts.filter(t=>t.trajectory_class==='mixed_reversals').length,incomplete:ts.filter(t=>!t.complete_trajectory).length};})};
}
function facetLagSubset(base) {
 const pairs=base.task_pairs.filter(t=>facetMatches(t.benchmark_id));
 const summaries=base.summaries.map(s=>{const rows=pairs.filter(t=>t.older===s.older&&t.newer===s.newer);const keys=s.analysis==='raw'?['better','worse','numerical_tie','incomplete']:['better','worse','within_band','not_estimable'];const counts=Object.fromEntries(keys.map(k=>[k,rows.filter(t=>t[s.analysis]===k).length]));return {...s,n_tasks:rows.length,counts};});
 return {...base,task_pairs:pairs,summaries,n_tasks:new Set(pairs.map(t=>t.benchmark_id)).size,n_families:new Set(pairs.map(t=>t.family)).size};
}
function facetNoResults() { return '<p class="empty">No measured tasks match this combination. Change or clear the filters. Proposed candidates can be explored in Benchmarks → All active candidates.</p>'; }
