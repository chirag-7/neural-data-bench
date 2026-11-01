"""Task-native version trajectories, current-specialist evidence and repair sensitivity.

Original first-attempt scores are immutable. Slopes use ordinal version positions
0/1/2, not time/compute. No incompatible native metric magnitudes are pooled.
"""
from pathlib import Path
from collections import defaultdict, Counter
import argparse,csv,hashlib,json,math

R=Path(__file__).resolve().parents[1]
D=R/'analysis/practical-review-2026-11-01'
REV=R/'literature/specialist-review-2026-11-01'
MODELS=['gpt-5.6-sol','gpt-6-sol','gpt-6.1-sol']
EXCLUDE={'B01','B03','B08','L06','M04','N05'}
METRIC_NOTES={
 'M04':'Known-equation numerical estimators nearly coincide; tiny ordering is numerical, not demonstrated capability progress.',
 'L06':'C2ST should approach chance0.5; tiny finite-classifier differences near chance do not establish posterior quality ordering.',
 'N05':'Deterministic field correctness has ceiling1; perfect scores demonstrate this file/schema only.',
 'C06':'High Pearson can coexist with poor count calibration; inspect the predeclared relative count error.',
 'B01':'Frozen GT-unit accuracy and post-hoc all-output event F1 reverse two model orderings.',
 'E06':'Equal-slice native mean is descriptive only; the same program improves on main but regresses on unseen taxis.',
 'B08':'Two original failures reflect ambiguous heapq whitelist wording. Original macro excludes this task; harness-repaired track is separate.'}
def read(p):return json.loads(Path(p).read_text())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def valid(r):return bool(r and r.get('status')=='measured' and isinstance(r.get('score'),(float,int)) and math.isfinite(r['score']))
def mean(v):return sum(v)/len(v) if v else None
def sign(v):return 'better' if v>1e-9 else 'worse' if v< -1e-9 else 'numerical_tie'
def save(p,o):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(o,indent=2,ensure_ascii=False,allow_nan=False)+'\n')
def csvsave(p,rows):
 if not rows:return
 with p.open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n');w.writeheader();w.writerows(rows)
def trajectory(rows,task):
 sid=sorted({r['slice_id'] for r in rows if r['model'] in MODELS})
 rs=[r for r in rows if valid(r)];metric=rs[0]['metric'];direction=rs[0]['direction'];orient=1 if direction=='higher' else -1
 assert all(r['metric']==metric and r['direction']==direction for r in rs),(task,'incompatible metrics within task')
 vals={};compliance={}
 for m in MODELS:
  a=[r for r in rows if r['model']==m];assert len(a)==len(sid),(task,m)
  vals[m]=mean([r['score'] for r in a]) if all(valid(r) for r in a) else None
  compliance[m]=all(r.get('strict_format_compliant',r.get('line_limit_compliant',True)) for r in a)
 pairs=[]
 for older,newer in [(MODELS[0],MODELS[1]),(MODELS[0],MODELS[2]),(MODELS[1],MODELS[2])]:
  a,b=vals[older],vals[newer];delta=b-a if a is not None and b is not None else None
  pairs.append(dict(older=older,newer=newer,raw_native_delta=delta,direction_adjusted_delta=orient*delta if delta is not None else None,
                    outcome=sign(orient*delta) if delta is not None else 'incomplete',
                    relative_loss_reduction_percent=100*(a-b)/a if delta is not None and direction=='lower' and a>0 and (('rmse' in metric) or ('mse' in metric) or ('bits_per' in metric)) else None))
 a,b,c=[vals[m] for m in MODELS];complete=all(v is not None for v in [a,b,c]);slope=(c-a)*orient/2 if complete else None
 if complete:
  q=sign((b-a)*orient),sign((c-b)*orient)
  label={('better','better'):'both steps improve',('worse','worse'):'both steps regress',('better','worse'):'peaks at GPT-6',('worse','better'):'dips at GPT-6',('numerical_tie','numerical_tie'):'numerically unchanged',('numerical_tie','better'):'tie then improvement',('numerical_tie','worse'):'tie then regression',('better','numerical_tie'):'improvement then tie',('worse','numerical_tie'):'regression then tie'}[q]
 else:label='incomplete original attempts'
 return dict(benchmark_id=task,n_slices=len(sid),slice_ids=sid,metric=metric,direction=direction,scores=vals,format_compliant=compliance,pairs=pairs,
             ordinal_direction_adjusted_slope=slope,slope_units=metric+' per ordinal version step',trajectory=label,
             flat_interpretation='Numerical tie only; no prospective practical-equivalence margin or repeated-generation test.' if label=='numerically unchanged' else 'No practical flatness/equivalence conclusion from a single generated program.',
             interpretation=METRIC_NOTES.get(task,'Task-native point changes; single source/procedure and generation limitations remain.'),
             observed_macro_eligible=task not in EXCLUDE)

def main():
 p=argparse.ArgumentParser();p.add_argument('--require-specialists',action='store_true');p.add_argument('--require-repairs',action='store_true');args=p.parse_args();D.mkdir(parents=True,exist_ok=True)
 original=(R/'results/measurements.jsonl').read_bytes();records=[json.loads(x) for x in original.decode().splitlines()];summary=read(R/'analysis/summary.json');catalog=read(R/'registry/catalog.json');entries={e['id']:e for e in catalog['entries']}
 repair_path=R/'results/repairs-v1.json';repair_results=read(repair_path) if repair_path.exists() else None
 if args.require_repairs:assert repair_results and repair_results.get('latest_successes'),'Final repair record missing'
 latest=repair_results.get('latest_successes',[]) if repair_results else []
 tasks=sorted({r['benchmark_id'] for r in records if r['model'] in MODELS});out=[];native_slices=[]
 for t in tasks:
  rows=[r for r in records if r['benchmark_id']==t];o=trajectory(rows,t);e=entries[t];o.update(task=e['task'],family_code=e['family_code'],executed_slice=e.get('executed_slice'),source_limitations=e.get('limitations',''))
  path=REV/(t+'.json');review=read(path) if path.exists() else None
  if args.require_specialists:assert review is not None,(t,'missing current review')
  o['specialist_review']=review;o['specialist_evidence_file']=str(path.relative_to(R)) if review else None
  refs=[r for r in summary['reference_envelopes'] if r['benchmark_id']==t];assert len(refs)==o['n_slices'],t
  o['primary_reference']=dict(names=sorted({r['model'] for r in refs}),score=mean([r['score'] for r in refs]),reference_class=refs[0]['reference_class'],current_sota_verified=False,
     evidence='; '.join(dict.fromkeys(r['evidence'] for r in refs)))
  for pair in o['pairs']:pair['strict_pair_compliant']=all(o['format_compliant'][m] for m in [pair['older'],pair['newer']])
  for m in MODELS:
   a=o['scores'][m];o.setdefault('versus_primary_reference',{})[m]=dict(direction_adjusted_delta=(a-o['primary_reference']['score'])*(1 if o['direction']=='higher' else -1) if a is not None else None,
       outcome=sign((a-o['primary_reference']['score'])*(1 if o['direction']=='higher' else -1)) if a is not None else 'incomplete')
  o['best_general_model']=max((m for m in MODELS if o['scores'][m] is not None),key=lambda m:o['scores'][m]*(1 if o['direction']=='higher' else -1),default=None)
  wins=[m for m in MODELS if o['versus_primary_reference'][m]['outcome']=='better']
  specialist=o['primary_reference']['reference_class'] in ['local_specialist','historical_specialist','pretrained_specialist']
  o['switch_decision']='evaluate_as_an_alternative' if wins else 'retain_reference_and_investigate'
  o['switch_now_evidence']='No general replacement recommendation: current-best matched comparison, practical margin, independent-source replication and operational validation are incomplete.'
  if t=='N05':o['switch_decision']='correctness_ceiling_on_this_file';o['switch_now_evidence']='Two original procedures already reach1.0 on61fields; deterministic extractor selection still needs other schemas/files.'
  if wins and not specialist:o['switch_now_evidence']='A general procedure beats the tested conventional reference here. Strongest current specialist is not established on this custom slice; benchmark the stronger candidate before replacement.'
  o['observed_general_winners_vs_tested_reference']=wins
  effective=[dict(r) for r in rows]
  applied=[]
  for repair in latest:
   key=repair.get('original_key',{})
   if key.get('benchmark_id')!=t or not valid(repair):continue
   match=next(r for r in effective if (r['slice_id'],r['model'])==(key['slice_id'],key['model']))
   match.update({k:v for k,v in repair.items() if k not in ['model','benchmark_id','slice_id','original_key']});match['repair_applied']=True
   if 'line_limit_compliant' in repair:match['strict_format_compliant']=repair['line_limit_compliant']
   applied.append(repair)
  if applied:
   repaired=trajectory(effective,t);repaired['chart_rows']=[{k:r.get(k) for k in ['benchmark_id','slice_id','model','status','score','metric','direction','reference_type','line_limit_compliant','strict_format_compliant','baseline_name','description','repair_applied']} for r in effective]
   repaired['versus_primary_reference']={m:dict(direction_adjusted_delta=(a-o['primary_reference']['score'])*(1 if o['direction']=='higher' else -1),outcome=sign((a-o['primary_reference']['score'])*(1 if o['direction']=='higher' else -1))) if a is not None else dict(direction_adjusted_delta=None,outcome='incomplete') for m,a in repaired['scores'].items()}
   repaired['primary_reference']=o['primary_reference']
   repaired['best_general_model']=max((m for m in MODELS if repaired['scores'][m] is not None),key=lambda m:repaired['scores'][m]*(1 if o['direction']=='higher' else -1),default=None)
   repaired['observed_general_winners_vs_tested_reference']=[m for m in MODELS if repaired['versus_primary_reference'][m]['outcome']=='better']
   o['repair_assisted']=repaired
  attempts=[a for a in repair_results.get('attempts',[]) if (a.get('original_key',{}).get('benchmark_id',a.get('benchmark_id'))==t)] if repair_results else []
  unresolved=[a for a in repair_results.get('unresolved',[]) if a.get('original_key',{}).get('benchmark_id',a.get('benchmark_id'))==t] if repair_results else []
  o['repair_info']={'latest_successes':applied,'attempts':attempts,'unresolved':unresolved}
  out.append(o)
  for r in rows:
   if r['model'] in MODELS:native_slices.append({k:r.get(k) for k in ['benchmark_id','slice_id','model','status','score','metric','direction','strict_format_compliant','reason']})
 summaries=[]
 for scope in ['all_measured_tasks','observed_data_tasks']:
  selected=[o for o in out if scope=='all_measured_tasks' or o['observed_macro_eligible']]
  for older,newer in [(MODELS[0],MODELS[1]),(MODELS[0],MODELS[2]),(MODELS[1],MODELS[2])]:
   ps=[next(p for p in o['pairs'] if p['older']==older and p['newer']==newer) for o in selected]
   summaries.append(dict(scope=scope,older=older,newer=newer,n_tasks=len(ps),counts=dict(Counter(p['outcome'] for p in ps)),
      estimand='Sign of each task native equal-slice mean; distinct from previous mean-of-slice-signs family statistic. Failures remain incomplete, never zero.'))
 family=[]
 for fam in sorted({o['family_code'] for o in out}):
  es=[o for o in out if o['family_code']==fam]
  family.append(dict(family_code=fam,n_tasks=len(es),comparisons=[dict(older=a,newer=b,counts=dict(Counter(next(p for p in o['pairs'] if p['older']==a and p['newer']==b)['outcome'] for o in es))) for a,b in [(MODELS[0],MODELS[1]),(MODELS[0],MODELS[2]),(MODELS[1],MODELS[2])]]))
 assert (R/'results/measurements.jsonl').read_bytes()==original
 result=dict(revision='2026-11-01-v13',measurement_snapshot='0.11-original-first-attempts',input_sha256={'results/measurements.jsonl':hashlib.sha256(original).hexdigest(),'analysis/summary.json':sha(R/'analysis/summary.json')},
    models=MODELS,tasks=out,task_direction_summaries=summaries,family_summaries=family,
    ordinal_slope_warning='Version positions0,1,2 are equally spaced labels chosen only for descriptive plotting. Slope is not per month, dollar, parameter or FLOP, not a scaling law or forecast; middle-version reversals remain shown.',
    repair_results=repair_results,
    flatness_warning='Numerical tie is not statistical/practical equivalence. No meaningful margin or generation variability was prospectively measured. M04 tiny numerical estimator differences and near-chance L06 need special interpretation.',
    switching_warning='No blanket switch recommendation follows from beating a weak/local/historical reference. Current specialist candidates and exact matched evaluation are separate evidence.',
    coverage={'measured_tasks':len(tasks),'specialist_reviews_present':sum(o['specialist_review'] is not None for o in out)})
 repair_summaries=[]
 for scope in ['all_measured_tasks','observed_data_tasks']:
  selected=[o.get('repair_assisted',o) for o in out if scope=='all_measured_tasks' or o['observed_macro_eligible']]
  for older,newer in [(MODELS[0],MODELS[1]),(MODELS[0],MODELS[2]),(MODELS[1],MODELS[2])]:
   ps=[next(p for p in o['pairs'] if p['older']==older and p['newer']==newer) for o in selected]
   repair_summaries.append(dict(scope=scope,older=older,newer=newer,n_tasks=len(ps),counts=dict(Counter(p['outcome'] for p in ps)),interpretation='Repair-assisted usability sensitivity; selective post-hoc debugging is not unbiased model-generation evidence.'))
 result['repair_assisted_task_direction_summaries']=repair_summaries
 save(D/'trajectories.json',result);csvsave(D/'all-model-slices.csv',native_slices)
 csvsave(D/'task-trajectories.csv',[dict(benchmark_id=o['benchmark_id'],family=o['family_code'],task=o['task'],metric=o['metric'],direction=o['direction'],n_slices=o['n_slices'],gpt56=o['scores'][MODELS[0]],gpt6=o['scores'][MODELS[1]],gpt61=o['scores'][MODELS[2]],delta6_vs56=o['pairs'][0]['raw_native_delta'],delta61_vs56=o['pairs'][1]['raw_native_delta'],delta61_vs6=o['pairs'][2]['raw_native_delta'],ordinal_direction_adjusted_slope=o['ordinal_direction_adjusted_slope'],trajectory=o['trajectory'],primary_reference=o['primary_reference']['score'],reference_class=o['primary_reference']['reference_class'],general_winners_vs_reference=','.join(o['observed_general_winners_vs_tested_reference']),switch_decision=o['switch_decision']) for o in out])
 print(json.dumps({'coverage':result['coverage'],'task_direction_summaries':summaries},indent=2))
if __name__=='__main__':main()
