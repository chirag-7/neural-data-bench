"""Derive central measurements and descriptive paired comparisons, without mixed-metric averaging."""
from pathlib import Path
import csv, hashlib, json, math
ROOT=Path(__file__).resolve().parents[1]
MODELS=['gpt-5.6-sol','gpt-6-sol','gpt-6.1-sol']
def mean(xs):return sum(xs)/len(xs) if xs else None
catalog=json.loads((ROOT/'registry/catalog.json').read_text())
records=[]
for task in ['C05','M04']:
 p=ROOT/f'results/{task}.json'
 if p.exists():records += json.loads(p.read_text())
# Recompute family and task labels from the canonical registry, never infer independence from entry count.
for r in records:
 r['family_code']=r['benchmark_id'][0]
 r['exploratory']=True
 r['strict_format_compliant']=r.get('line_limit_compliant',True)
 r['score_evidence']='new_local_measurement' if r.get('reference_type')!='archived_predictions_rescored' else 'archived_predictions_rescored'
(ROOT/'results/measurements.jsonl').write_text(''.join(json.dumps(r,allow_nan=False)+'\n' for r in records))
cols=['benchmark_id','family_code','slice_id','model','status','score','metric','direction','n_units','seconds','track','score_evidence','strict_format_compliant','prediction_file','code_sha256','reason']
with (ROOT/'results/measurements.csv').open('w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=cols,extrasaction='ignore');w.writeheader();w.writerows(records)
refs=[]
for sid in ['1','2','3','4','5']:
 rs=[r for r in records if r['benchmark_id']=='C05' and r['slice_id']==sid and r.get('score') is not None]
 archives=[r for r in rs if r['model'] in ['deneux','speiser','friedrich','rupprecht']]
 if archives:
  best=max(archives,key=lambda r:r['score']);refs.append(dict(benchmark_id='C05',slice_id=sid,model=best['model'],score=best['score'],evidence='best available complete result among up to four inspected archives; selected using test scores, not current SOTA',n_archive_candidates=len(archives)))
for r in records:
 if r['benchmark_id']=='M04' and r['model']=='canonical-mle' and r.get('score') is not None:refs.append(dict(benchmark_id='M04',slice_id=r['slice_id'],model=r['model'],score=r['score'],evidence='local correctly specified multistart MLE; not literature SOTA'))
lookup={(r['benchmark_id'],r['slice_id'],r['model']):r for r in records}
comparisons=[]
for model in MODELS:
 for ref in refs:
  r=lookup.get((ref['benchmark_id'],ref['slice_id'],model))
  if not r or r.get('score') is None:continue
  delta=(r['score']-ref['score'])*(1 if r['direction']=='higher' else -1)
  comparisons.append(dict(benchmark_id=r['benchmark_id'],slice_id=r['slice_id'],model=model,reference=ref['model'],direction_adjusted_delta=delta,outcome='win' if delta>1e-9 else 'loss' if delta< -1e-9 else 'numerical_tie',budget_matched=False,strict_format_compliant=r['strict_format_compliant'],caveat='Performance-only; reference construction/supervision/selection differs'))
progress=[]
keys=sorted(set((r['benchmark_id'],r['slice_id']) for r in records if r['model'] in MODELS))
for old,new in [(MODELS[0],MODELS[1]),(MODELS[1],MODELS[2]),(MODELS[0],MODELS[2])]:
 for task,sid in keys:
  a=lookup.get((task,sid,old));b=lookup.get((task,sid,new))
  if not a or not b or a.get('score') is None or b.get('score') is None:continue
  delta=(b['score']-a['score'])*(1 if b['direction']=='higher' else -1)
  progress.append(dict(benchmark_id=task,slice_id=sid,older=old,newer=new,metric=b['metric'],direction_adjusted_delta=delta,improved=delta>1e-9,interpretation='numerical ordering only; near-identical quadrature estimators' if task=='M04' else 'exploratory point-score change; one frozen program',strict_pair_compliant=a.get('line_limit_compliant',True) and b.get('line_limit_compliant',True)))
summary=dict(version='0.3',date='2026-10-30',mapped_entries=len(catalog['entries']),mapped_families=len(catalog['families']),measured_tasks=len(set(r['benchmark_id'] for r in records if r.get('score') is not None)),measured_families=len(set(r['family_code'] for r in records if r.get('score') is not None)),measured_biological_benchmarks=1 if any(r['benchmark_id']=='C05' for r in records) else 0,measured_synthetic_tasks=1 if any(r['benchmark_id']=='M04' for r in records) else 0,models=MODELS,reference_envelopes=refs,reference_comparisons=comparisons,generation_progress=progress,model_summaries=[],claims_withheld=['Universal neuroscience ranking','Current global SOTA','Matched-total-effort generalist superiority','Stable causal generation/scaling trend','Biological population uncertainty without animal IDs'])
for model in MODELS:
 attempted=[r for r in records if r['model']==model];valid=[r for r in attempted if r.get('score') is not None]
 c=[r for r in valid if r['benchmark_id']=='C05'];m=[r for r in valid if r['benchmark_id']=='M04'];comps=[r for r in comparisons if r['model']==model]
 summary['model_summaries'].append(dict(model=model,attempted=len(attempted),valid=len(valid),strict_format_valid=sum(r['strict_format_compliant'] for r in valid),C05_preparation_equal_mean_of_medians=mean([r['score'] for r in c]),C05_n_preparations=len(c),M04_normalized_mae=m[0]['score'] if m else None,C05_strict_eligible_preparations=sum(r['strict_format_compliant'] for r in c),C05_strict_reference_wins=sum(r['outcome']=='win' and r['benchmark_id']=='C05' and r['strict_format_compliant'] for r in comps),C05_reference_wins=sum(r['outcome']=='win' and r['benchmark_id']=='C05' for r in comps),M04_reference_wins=sum(r['outcome']=='win' and r['benchmark_id']=='M04' for r in comps)))
(ROOT/'analysis/summary.json').write_text(json.dumps(summary,indent=2,allow_nan=False))
# Sanitized generation provenance: preserve actual usage/events, omit machine/auth identifiers.
for task,logdir,subdir in [('C05','pilot-models','experiments/C05/pilot-v1'),('M04','cognitive-models','experiments/M04')]:
 provenance=[]
 for model in MODELS:
  p=ROOT.parents[1]/'work'/logdir/(model+'.jsonl');submission=ROOT/subdir/(model+'.json')
  if not p.exists() or not submission.exists():continue
  events=[json.loads(x) for x in p.read_text().splitlines() if x.strip()];code=json.loads(submission.read_text())['code'];prompt=ROOT/subdir/'prompt.txt'
  provenance.append(dict(requested_model=model,reasoning_effort='high',generation_replicates=1,user_prompt_sha256=hashlib.sha256(prompt.read_bytes()).hexdigest(),code_sha256=hashlib.sha256(code.encode()).hexdigest(),usage=next((e.get('usage') for e in reversed(events) if e.get('type')=='turn.completed'),None),tool_events=sum(e.get('item',{}).get('type') not in [None,'agent_message','reasoning'] for e in events),effective_context='CLI/provider supplied instructions also present; byte-identical full effective context not established',command_policy=['exec','--ephemeral','--ignore-user-config','--skip-git-repo-check','--sandbox read-only','model_reasoning_effort=high'],code_lines=len(code.splitlines())))
 (ROOT/f'experiments/{task}/generation-provenance.json').write_text(json.dumps(provenance,indent=2))
# Synthetic input semantic manifest.
cp=ROOT/'data/cache/cognitive-v1.npz'
if cp.exists():
 import numpy as np
 a=np.load(cp);(ROOT/'data/manifests/cognitive.json').write_text(json.dumps(dict(path='data/cache/cognitive-v1.npz',generator='scripts/evaluate.py:make_cognitive',seed=20261030,sha256=hashlib.sha256(cp.read_bytes()).hexdigest(),arrays={k:dict(shape=list(a[k].shape),dtype=str(a[k].dtype),sha256=hashlib.sha256(a[k].tobytes()).hexdigest()) for k in a.files},license='Project-generated synthetic data; no human or animal participants'),indent=2))
print(json.dumps(summary['model_summaries'],indent=2))
