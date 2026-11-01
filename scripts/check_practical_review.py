"""Portable independent arithmetic/provenance checks; never executes models."""
from pathlib import Path
from collections import Counter
import hashlib,json,math
R=Path(__file__).resolve().parents[1];D=R/'analysis/practical-review-2026-11-01'
def read(p):return json.loads((R/p).read_text())
def sha(p):return hashlib.sha256((R/p).read_bytes()).hexdigest()
def valid(r):return r.get('status')=='measured' and isinstance(r.get('score'),(int,float)) and math.isfinite(r['score'])
def outcome(v):return 'better' if v>1e-9 else 'worse' if v< -1e-9 else 'numerical_tie'
x=read('analysis/practical-review-2026-11-01/trajectories.json');rep=read('results/repairs-v1.json')
rows=[json.loads(l) for l in (R/'results/measurements.jsonl').read_text().splitlines()]
assert len(rows)==208 and len(x['tasks'])==30 and len({t['family_code'] for t in x['tasks']})==14
for p,h in x['input_sha256'].items():assert sha(p)==h
for p,h in read('experiments/repairs-v1/original-preservation.json').items():assert sha(p)==h
assert len(rep['attempts'])==13 and len(rep['latest_successes'])==7 and len(rep['unresolved'])==4
assert sum(not r['control_originally_successful'] for r in rep['latest_successes'])==4
assert sum(not r['control_originally_successful'] and r['line_limit_compliant'] for r in rep['latest_successes'])==3
for r in rep['latest_successes']:
 assert sha(r['prediction_file'])==r['prediction_sha256'] and sha(r['code_file'])==r['code_sha256']
 key=r['original_key'];assert len([a for a in rows if all(a[k]==v for k,v in key.items())])==1
for t in x['tasks']:
 originals=[r for r in rows if r['benchmark_id']==t['benchmark_id']]
 for view in [t]+([t['repair_assisted']] if 'repair_assisted' in t else []):
  rs=[dict(r) for r in originals]
  if view is not t:
   for r in rep['latest_successes']:
    if r['original_key']['benchmark_id']!=t['benchmark_id']:continue
    a=next(a for a in rs if all(a[k]==v for k,v in r['original_key'].items()));a.update(status=r['status'],score=r['score'])
  for m in x['models']:
   vals=[r for r in rs if r['model']==m]
   expected=sum(r['score'] for r in vals)/len(vals) if all(valid(r) for r in vals) else None
   assert view['scores'][m]==expected,(t['benchmark_id'],m)
  orient=1 if view['direction']=='higher' else -1
  for p in view['pairs']:
   a,b=view['scores'][p['older']],view['scores'][p['newer']]
   assert p['outcome']==(outcome(orient*(b-a)) if a is not None and b is not None else 'incomplete')
  a,b,c=[view['scores'][m] for m in x['models']]
  expected=(c-a)*orient/2 if all(v is not None for v in [a,b,c]) else None
  assert view['ordinal_direction_adjusted_slope']==expected
 assert t['specialist_review']==read(t['specialist_evidence_file'])
 assert t['specialist_review']['reviewed_on']=='2026-11-01'
 assert t['primary_reference']['current_sota_verified'] is False
 assert t['specialist_review']['search_queries'] and t['specialist_review']['candidates'] and t['specialist_review']['sources']
 for s in t['specialist_review']['sources']:assert s['url'].startswith('https://')
for key,repair in [('task_direction_summaries',False),('repair_assisted_task_direction_summaries',True)]:
 for p in x[key]:
  ts=[t for t in x['tasks'] if p['scope']=='all_measured_tasks' or t['observed_macro_eligible']]
  if repair:ts=[t.get('repair_assisted',t) for t in ts]
  expected=Counter(next(a for a in t['pairs'] if (a['older'],a['newer'])==(p['older'],p['newer']))['outcome'] for t in ts)
  assert p['counts']==dict(expected) and p['n_tasks']==len(ts)
assert (R/'website/data/practical-review.json').read_bytes()==(D/'trajectories.json').read_bytes()
for r in read('analysis/practical-review-2026-11-01/review-fingerprints.json'):
 assert sha(r['review_file'])==r['review_sha256'] and sha(r['protocol_file'])==r['protocol_sha256']
sources=read('analysis/practical-review-2026-11-01/specialist-source-ledger.json');coverage=read('analysis/practical-review-2026-11-01/specialist-coverage.json')
assert coverage['unique_source_urls']==len({s['url'] for s in sources})==166 and coverage['candidate_entries']==137
manifest=read('analysis/practical-review-2026-11-01/artifact-manifest.json')
for r in manifest['files']:assert sha(r['path'])==r['sha256'],r['path']
assert manifest['repair_results_sha256']==sha('results/repairs-v1.json')
for r in read('registry/current-best.json'):
 if r['benchmark_id'] in {t['benchmark_id'] for t in x['tasks']}:assert r['checked_on']=='2026-11-01' and r['score'] is None and r['status']=='not verified'
print('Practical review passed: 30 task trajectories, both tracks, 7 repair/control identities, 4 unresolved archives, 30 current-specialist reviews, source/protocol fingerprints and immutable original ledger.')
