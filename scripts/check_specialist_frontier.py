"""Independently recompute frontier choices, quartiles and direction counts; no fitting."""
from pathlib import Path
from fractions import Fraction
from collections import Counter
import json,hashlib,math,csv
R=Path(__file__).resolve().parents[1];P=R/'analysis/specialist-frontier-v1/comparison.json';d=json.loads(P.read_text())
assert P.read_bytes()==(R/'website/data/specialist-frontier.json').read_bytes()
for p,h in d['input_sha256'].items():assert hashlib.sha256((R/p).read_bytes()).hexdigest()==h,p
source=json.loads((R/'analysis/generation-comparison-v2/generation-comparison.json').read_text());tasks={t['benchmark_id']:t for t in source['tasks']};assert len(d['tasks'])==len(tasks)==30
counts={k:{mode:Counter() for mode in ['raw','iqr_0.1','iqr_0.5']} for k in ['specialist_only','all_available_references']}
for t in d['tasks']:
 original=tasks[t['benchmark_id']];assert t['general_scores']==original['scores'];assert t['direction']==original['direction'];assert t['metric']==original['metric']
 sign=1 if t['direction']=='higher' else -1;values=sorted(Fraction.from_float(v) for v in t['general_scores'].values());q1=(values[0]+3*values[1])/4;q3=(3*values[2]+values[3])/4;scale=float(q3-q1)
 assert abs(t['general_panel_iqr']-scale)<1e-12
 best=max(sign*v for v in original['scores'].values());assert abs(sign*t['best_general_score']-best)<1e-12
 for c in t['candidates']:
  if c['source']=='H02-replication references':rs=[r for r in json.loads((R/'website/data/H02-replication.json').read_text())['references'] if r['model']==c['model']]
  else:rs=[r for r in original['chart_rows'] if r['model']==c['model']]
  assert len(rs)==original['n_slices'] and all(r['status']=='measured' and r['score'] is not None for r in rs)
  assert abs(c['score']-sum(r['score'] for r in rs)/len(rs))<1e-12
 for key,scope in [('best_specialist','specialist_only'),('best_available_reference','all_available_references')]:
  ref=t[key];pool=[r for r in t['candidates'] if key!='best_specialist' or r['specialist']]
  assert bool(ref)==bool(pool)
  if not ref:
   for mode in counts[scope]:counts[scope][mode]['unavailable']+=1
   continue
  assert abs(sign*ref['score']-max(sign*r['score'] for r in pool))<1e-12
  delta=sign*(t['best_general_score']-ref['score']);raw='numerical_tie' if abs(delta)<=1e-9 else 'general_better' if delta>0 else 'specialist_better';assert ref['classes']['raw']==raw
  for mode in counts[scope]:
   expected=raw if mode=='raw' else 'within_band' if raw=='numerical_tie' else 'not_estimable' if scale==0 else 'general_better' if delta/scale>float(mode.split('_')[1])+1e-12 else 'specialist_better' if delta/scale < -float(mode.split('_')[1])-1e-12 else 'within_band'
   assert ref['classes'][mode]==expected;counts[scope][mode][expected]+=1
for scope in counts:
 for row in d['summaries'][scope]:assert dict(counts[scope][row['analysis']])==row['counts'];assert sum(row['counts'].values())==30
assert counts['specialist_only']['raw']==Counter(general_better=10,specialist_better=4,unavailable=16)
assert counts['specialist_only']['iqr_0.5']==Counter(general_better=3,specialist_better=1,within_band=10,unavailable=16)
a={t['benchmark_id']:t for t in d['tasks']}
assert a['H02']['best_specialist']['methods']==['xdawn-tslr-tuned']
assert a['A09']['best_specialist']['methods']==['vassi-run-15']
assert a['B07']['best_specialist']['methods']==['delta-blosc-zstd']
assert a['C05']['best_specialist']['methods']==['rupprecht']
assert {r['model'] for r in a['C05']['excluded_candidates']}=={'deneux','speiser'}
assert a['M01']['best_specialist'] is None and a['M01']['best_available_reference']['methods']==['behavioral-glm']
with (P.parent/'task-comparisons.csv').open() as f:assert len(list(csv.DictReader(f)))==60
print('Specialist frontier: 30 tasks, 14 specialist comparisons; independently verified quartiles, selections, complete slice coverage, all six summaries and unchanged source hashes.')
