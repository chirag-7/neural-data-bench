"""Centralize all task records and derive exploratory, direction-aware paired summaries.
No averaging across native metrics; weighting is slice→task→family. Public test labels,
one generation and unequal reference histories preclude confirmatory superiority claims.
"""
from pathlib import Path
from collections import defaultdict
import csv,hashlib,json,math
R=Path(__file__).resolve().parents[1];MODELS=['gpt-5.6-sol','gpt-6-sol','gpt-6.1-sol']
def mean(xs):return sum(xs)/len(xs) if xs else None
def valid(r):return r is not None and isinstance(r.get('score'),(float,int)) and math.isfinite(r['score'])
def outcome(delta):return 'win' if delta>1e-9 else 'loss' if delta< -1e-9 else 'numerical_tie'
def weighted(rows,key='outcome'):
 tasks=defaultdict(list)
 for x in rows:tasks[x['benchmark_id']].append(x)
 task=[]
 for t,rs in sorted(tasks.items()):
  task.append(dict(benchmark_id=t,family_code=t[0],n_slices=len(rs),win_fraction=mean([int(r[key]=='win') for r in rs]),loss_fraction=mean([int(r[key]=='loss') for r in rs]),tie_fraction=mean([int(r[key]=='numerical_tie') for r in rs]),failure_fraction=mean([int(r[key]=='failed_or_missing') for r in rs])))
 families=[]
 for fam in sorted(set(t['family_code'] for t in task)):
  ts=[t for t in task if t['family_code']==fam];families.append(dict(family_code=fam,n_tasks=len(ts),**{k:mean([t[k] for t in ts]) for k in ['win_fraction','loss_fraction','tie_fraction','failure_fraction']}))
 return dict(n_tasks=len(task),n_families=len(families),n_slice_comparisons=len(rows),wins=sum(r[key]=='win' for r in rows),losses=sum(r[key]=='loss' for r in rows),numerical_ties=sum(r[key]=='numerical_tie' for r in rows),failed_or_missing=sum(r[key]=='failed_or_missing' for r in rows),task_equal_win_fraction=mean([t['win_fraction'] for t in task]),family_equal_win_fraction=mean([f['win_fraction'] for f in families]),task_summaries=task,family_summaries=families)
def main():
 catalog=json.loads((R/'registry/catalog.json').read_text());records=[]
 for p in sorted((R/'results').glob('*.json')):
  rows=json.loads(p.read_text())
  if isinstance(rows,list) and all(isinstance(r,dict) and 'benchmark_id'in r for r in rows):records+=rows
 for r in records:
  if r.get('posthoc_secondary_metrics'):
   for key in ['all_event_f1','all_event_precision','all_event_recall']:r['posthoc_'+key]=r['posthoc_secondary_metrics'][key]
  r['family_code']=r['benchmark_id'][0];r['exploratory']=True
  codefile=R/f'experiments/{r["benchmark_id"]}/{r["model"]}.json'
  if r['model']in MODELS and codefile.exists():
   n=len(json.loads(codefile.read_text())['code'].splitlines());r.setdefault('code_lines',n);r.setdefault('line_limit_compliant',n<240)
  r['strict_format_compliant']=r.get('line_limit_compliant',True)
  r['score_evidence']='archived_predictions_rescored' if r.get('reference_type')=='archived_predictions_rescored' else 'new_local_measurement'
 (R/'results/measurements.jsonl').write_text(''.join(json.dumps(r,allow_nan=False)+'\n' for r in records))
 cols=['benchmark_id','family_code','slice_id','model','status','score','metric','direction','n_units','seconds','track','score_evidence','strict_format_compliant','prediction_file','prediction_sha256','code_sha256','reason','posthoc_all_event_f1','posthoc_all_event_precision','posthoc_all_event_recall','sliced_w2','chance_target','n_posterior_draws_per_unit','scoring_seconds','scorer_audit_file']
 with (R/'results/measurements.csv').open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=cols,extrasaction='ignore',lineterminator='\n');w.writeheader();w.writerows(records)
 lookup={(r['benchmark_id'],r['slice_id'],r['model']):r for r in records};keys=sorted(set((r['benchmark_id'],r['slice_id']) for r in records if r['model']in MODELS));refs=[]
 for task,sid in keys:
  rows=[r for r in records if r['benchmark_id']==task and r['slice_id']==sid and valid(r)];ref=None
  if task=='B01':ref=lookup.get((task,sid,'mountainsort5'));cls='local_specialist';evidence='MountainSort5 fixed configuration; one standard stationary simulation, not current SOTA'
  elif task=='B03':ref=lookup.get((task,sid,'task-baseline'));cls='local_specialist';evidence='Official SI decentralized registration numerical code on same synthetic voltage-derived peak rasters;physical injected displacement truth,not realdrift/globalSOTA'
  elif task=='B08':ref=lookup.get((task,sid,'spikepack'));cls='local_specialist';evidence='Original Spikepack100us on alternateFALCONdata;timing intentionally lossy;ambiguous utility whitelist prevents clean model-version inference;excluded from aggregate comparisons'
  elif task=='C06':ref=lookup.get((task,sid,'task-baseline'));cls='local_specialist';evidence='OASIS AR1 with training-only scale and200ms smoothing;custom heldoutfish endpoint,not strongest CASCADE;global checkpoints overlaptestsource'
  elif task=='E06':ref=lookup.get((task,sid,'task-baseline'));cls='conventional_domain_reference';evidence='Official ZAPBench NLinear architecture,local analytical ridge1 optimization;shared256neurons,onebrain,two dependent slices,not published/globalbest'
  elif task=='B07':ref=lookup.get((task,sid,'wavpack-high'));cls='local_specialist';evidence='Frozen WavPack5.8.0 lossless very-high mode on16 real shortchunks, all384channels, exact-byte reconstruction; delta-Blosc alternative retained; not full streaming/paper/current-global-best benchmark'
  elif task=='H02':ref=lookup.get((task,sid,'xdawn-tslr'));cls='local_specialist';evidence='Fixed pyRiemann xDAWN/tangent-space logistic pipeline, same subject-disjoint source and train-only fitting; no current-SOTA claim'
  elif task=='K04':ref=lookup.get((task,sid,'singler'));cls='local_specialist';evidence='Official SingleR0.5.0 on same500 genes; donor-layer mean profiles from training only. One test donor; supervised layer transfer, not spatial clustering leaderboard'
  elif task=='L06':ref=lookup.get((task,sid,'polya-gamma'));cls='local_specialist';evidence='Local Polya-Gamma Gibbs adaptation; ten synthetic GLM observations, known likelihood, custom2000draw C2ST. Same sampler family as archived reference, unequal implementation effort; no originalSBI/globalSOTAclaim'
  elif task=='M01':ref=lookup.get((task,sid,'behavioral-glm'));cls='conventional_domain_reference';evidence='Source-inspired pooled behavioral GLM with signed-contrast/history/block basis and train-mouse weighting; not original peranimal fits or global best'
  elif task=='H01':ref=lookup.get((task,sid,'pyriemann-aligned'));cls='local_specialist';evidence='pyRiemann subject-centered tangent SVM; post-hoc domain reference, explicit group IDs/offline unlabeled adaptation differ'
  elif task=='H08':ref=lookup.get((task,sid,'yasa-eeg'));cls='pretrained_specialist';evidence='Published YASA EEG checkpoint on identical night signals; NSRR pretraining and target training budgets differ'
  elif task=='J08':ref=lookup.get((task,sid,'task-baseline'));cls='historical_specialist';evidence='Author archived StarDist masks, exact two fields/five human raters; different optimization history'
  elif task=='C05':
   archives=[r for r in rows if r['model']in ['deneux','speiser','friedrich','rupprecht']]
   if archives:ref=max(archives,key=lambda r:r['score'])
   cls='historical_specialist';evidence='Test-selected envelope among up to four inspected 2017 archives, not current SOTA'
  elif task=='A09':ref=lookup.get((task,sid,'vassi-run-00'));cls='historical_specialist';evidence='Archived VASSI run00, selected before rescoring; unequal full-frame inputs/training/tuning'
  elif task=='I10':ref=lookup.get((task,sid,'mriqc-rfc-2017'));cls='historical_specialist';evidence='Archived MRIQC2017 predictions, same DS030 rows; different training labels/features/tuning'
  elif task=='M04':ref=lookup.get((task,sid,'canonical-mle'));cls='synthetic_objective_mismatched';evidence='Frozen local MLE; recovery score favors posterior medians, post-hoc reference retained separately'
  else:ref=lookup.get((task,sid,'task-baseline'));cls='deterministic_correctness' if task=='N05' else 'conventional_baseline';evidence='Audited deterministic reference, correct by construction' if task=='N05' else 'Local conventional task baseline; strongest specialist unverified'
  if valid(ref):refs.append(dict(benchmark_id=task,slice_id=sid,model=ref['model'],score=ref['score'],metric=ref['metric'],direction=ref['direction'],reference_class=cls,evidence=evidence,budget_matched=False,current_sota=False,aggregate_eligible=task!='B08'))
 comparisons=[]
 for model in MODELS:
  for ref in refs:
   r=lookup.get((ref['benchmark_id'],ref['slice_id'],model));delta=(r['score']-ref['score'])*(1 if ref['direction']=='higher' else -1) if valid(r) else None
   comparisons.append(dict(benchmark_id=ref['benchmark_id'],slice_id=ref['slice_id'],model=model,reference=ref['model'],reference_class=ref['reference_class'],direction_adjusted_delta=delta,outcome=outcome(delta) if delta is not None else 'failed_or_missing',strict_format_compliant=bool(r and r['strict_format_compliant']),budget_matched=False))
 progress=[]
 for old,new in [(MODELS[0],MODELS[1]),(MODELS[1],MODELS[2]),(MODELS[0],MODELS[2])]:
  for task,sid in keys:
   a=lookup.get((task,sid,old));b=lookup.get((task,sid,new));delta=(b['score']-a['score'])*(1 if b['direction']=='higher' else -1) if valid(a) and valid(b) else None
   progress.append(dict(benchmark_id=task,slice_id=sid,older=old,newer=new,metric=b.get('metric',a.get('metric')) if b and a else None,direction_adjusted_delta=delta,outcome=outcome(delta) if delta is not None else 'failed_or_missing',improved=delta is not None and delta>1e-9,older_valid=valid(a),newer_valid=valid(b),strict_pair_compliant=bool(a and b and a['strict_format_compliant'] and b['strict_format_compliant']),interpretation='Numerical quadrature ordering, not capability progress' if task=='M04' else 'One program per model; exploratory point score only'))
 model_summaries=[]
 for model in MODELS:
  rows=[r for r in records if r['model']==model];ok=[r for r in rows if valid(r)];cs=[r for r in comparisons if r['model']==model and r['benchmark_id']!='B08'];byclass={}
  for cls in sorted(set(r['reference_class'] for r in cs)):
   rs=[r for r in cs if r['reference_class']==cls];byclass[cls]=dict(exploratory=weighted(rs),strict=weighted([r for r in rs if r['strict_format_compliant']]))
  c=[r for r in ok if r['benchmark_id']=='C05'];m=[r for r in ok if r['benchmark_id']=='M04']
  observed_byclass={}
  for cls in sorted(set(r['reference_class'] for r in cs)):
   rs=[r for r in cs if r['reference_class']==cls and r['benchmark_id'] not in ['B01','B03','L06','M04','N05']];observed_byclass[cls]=dict(exploratory=weighted(rs),strict=weighted([r for r in rs if r['strict_format_compliant']]))
  model_summaries.append(dict(observed_data_reference_class_summaries=observed_byclass,model=model,attempted=len(rows),valid=len(ok),failed=len(rows)-len(ok),strict_format_valid=sum(r['strict_format_compliant'] for r in ok),C05_preparation_equal_mean_of_medians=mean([r['score'] for r in c]),C05_n_preparations=len(c),C05_reference_wins=sum(r['outcome']=='win' and r['benchmark_id']=='C05' for r in cs),M04_normalized_mae=m[0]['score'] if m else None,M04_reference_wins=sum(r['outcome']=='win' and r['benchmark_id']=='M04' for r in cs),reference_class_summaries=byclass))
 paired=[]
 for old,new in [(MODELS[0],MODELS[1]),(MODELS[1],MODELS[2]),(MODELS[0],MODELS[2])]:
  ps=[p for p in progress if p['older']==old and p['newer']==new and p['benchmark_id'] not in ['M04','N05','B08']]
  paired.append(dict(older=old,newer=new,observed_data=weighted([p for p in ps if p['benchmark_id'] not in ['B01','B03','L06']]),observed_data_strict=weighted([p for p in ps if p['benchmark_id'] not in ['B01','B03','L06'] and p['strict_pair_compliant']]),exclusions=['M04: near-identical numerical estimators','N05: deterministic file correctness reported separately','B08: ambiguous utility whitelist;retrospective aggregate exclusion,all attempts retained'],exploratory=weighted(ps),strict=weighted([p for p in ps if p['strict_pair_compliant']])))
 tasks=sorted(set(k[0] for k in keys));summary=dict(version=catalog.get('release','0.8'),date=max(r.get('date','2026-10-30') for r in records),mapped_entries=len(catalog['entries']),historical_mapped_entries=catalog.get('historical_mapped_entries',114),archived_candidates=catalog.get('archived_candidates',0),mapped_families=len(catalog['families']),measured_tasks=len(tasks),measured_task_ids=tasks,measured_families=len(set(t[0] for t in tasks)),measured_biological_benchmarks=len([t for t in tasks if t not in ['B01','B03','L06','M04','N05','H16']]),measured_synthetic_tasks=4,fully_synthetic_task_ids=['B01','B03','L06','M04'],semisynthetic_repair_task_ids=['H16','A14'],models=MODELS,model_summaries=model_summaries,reference_envelopes=refs,reference_comparisons=comparisons,generation_progress=progress,paired_macro_summaries=paired,record_count=len(records),model_attempts=sum(r['model']in MODELS for r in records),weighting='Native deltas never averaged. For descriptive win fractions average slices within task, tasks within family, families equally. Report reference classes separately. Failed/missing attempts remain denominator, strict format subsets have explicit denominator.',dataset_dependencies=['D02 and N05 share the same Allen intracellular file','K01 shares the broader AllenCellTypes collection, different target/protocol','C05 five preparations are one task','A09 twenty reference runs are not twenty tasks','F04 900 repeated trials represent30 images andone preparation','H16 semisynthetic mixtures, participant IDs unavailable','K04 four testsections are one held-out donor; annotations are expression-assisted','M01 observed five-trial histories and known blockprior; nonoverlapping target/history blocks; labs overlap','B08 shares G01 FALCON sources,1monkey;lossy timing;utility-whitelist ambiguity excludes aggregate inference','E06 two dependent slices use samebrain,neurons andtrainingarrays','C06 allDS04neurons;2testfish;Pearson ignores spike-count calibration','A15 twenty testrecordings are one unseenbird;annotationcoverage incomplete','B03 eight synthetic simulations are MonteCarlo instances,not biological cohorts','B07 sixteen short real-voltage chunks represent fourteen animals; compression is lab infrastructure, not neural interpretation','L06 ten synthetic observations share one design; likelihood-informed posterior sampling, custom2000drawC2ST, not originalSBI leaderboard','H02 extra generations remain separate from this first-submission panel'],claims_withheld=['Exhaustive coverage of neuroscience or literature','Universal mixed-metric model ranking','Current global SOTA','Matched-total-effort generalist superiority','Stable causal generation/scaling trend','Pruning implies exhaustive domain coverage','Biological population uncertainty without biological IDs'])
 summary['protocol_ambiguity_exclusions']={'task_ids':['B08'],'reason':'Prompt ordinaryutilities wording vs frozen heapq rejection;retrospective aggregate exclusion,not a clean capabilityfailure. Native results and both failures retained;raw comparison rows remain exported.'}
 summary['analysis_scopes']={'default':'observed_data','observed_data':{'excluded_task_ids':['B01','B03','L06','M04','N05'],'description':'Observed-data sources, including artificial corruption in A14/H16; fully synthetic and deterministic file tasks excluded'},'all':{'description':'Includes fully synthetic tasks; B08 ambiguous contract excluded from aggregates, M04 quadrature and N05 correctness excluded from version changes'}}
 (R/'analysis/summary.json').write_text(json.dumps(summary,indent=2,allow_nan=False))
 # Generation audit is derived only from actual local logs, preserved on clones without logs.
 for task in tasks:
  if task in ['C05','M04']:continue
  provenance=[];d=R/f'experiments/{task}'
  for model in MODELS:
   p=R.parents[1]/'work/expansion-models'/f'{task}-{model}.jsonl';sub=d/(model+'.json')
   if not p.exists() or not sub.exists():continue
   events=[json.loads(x) for x in p.read_text().splitlines() if x.strip()];code=json.loads(sub.read_text())['code']
   provenance.append(dict(requested_model=model,reasoning_effort='high',generation_replicates=1,user_prompt_sha256=hashlib.sha256((d/'prompt.txt').read_bytes()).hexdigest(),code_sha256=hashlib.sha256(code.encode()).hexdigest(),code_lines=len(code.splitlines()),usage=next((e.get('usage') for e in reversed(events) if e.get('type')=='turn.completed'),None),tool_events=sum(e.get('item',{}).get('type') not in [None,'agent_message','reasoning'] for e in events),effective_context='Identical explicit user prompt; CLI/provider instructions also present, byte-identical full context unestablished',command_policy=['exec','--ephemeral','--ignore-user-config','--skip-git-repo-check','--sandbox read-only','model_reasoning_effort=high']))
  if provenance:
   dest=d/'generation-provenance.json'
   if not dest.exists():dest.write_text(json.dumps(provenance,indent=2))
   else:
    previous=json.loads(dest.read_text())
    for item in provenance:
     prior=next(x for x in previous if x['requested_model']==item['requested_model'])
     for key in ['code_sha256','usage','tool_events']:assert prior[key]==item[key],(task,key)
 print(json.dumps(dict(tasks=tasks,records=len(records),models=[{k:s[k] for k in ['model','attempted','valid','strict_format_valid']} for s in model_summaries]),indent=2))
if __name__=='__main__':main()
