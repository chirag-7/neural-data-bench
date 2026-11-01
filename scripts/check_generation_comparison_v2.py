"""Check current comparison consistency and frozen-input provenance (stdlib)."""
from pathlib import Path
import argparse, hashlib, json, math
R=Path(__file__).resolve().parents[1]
MODELS=['gpt-4.1-2025-04-14','gpt-5-2025-08-07','gpt-5.6-sol','gpt-6.1-sol']
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text())
def main():
 p=argparse.ArgumentParser();p.add_argument('--output-root',type=Path,default=R/'analysis/generation-comparison-v2');p.add_argument('--no-website',action='store_true');a=p.parse_args();d=read(a.output_root/'generation-comparison.json');s=read(a.output_root/'comparison-summary.json');rows=[json.loads(x) for x in (a.output_root/'comparison-measurements.jsonl').read_text().splitlines()]
 assert d['models']==s['models']==MODELS
 assert len(d['tasks'])==30 and len({t['benchmark_id'] for t in d['tasks']})==30
 assert len({t['family_code'] for t in d['tasks']})==14
 assert len([r for r in rows if r['model'] in MODELS])==148
 assert not any(r['model']=='gpt-6-sol' for r in rows)
 assert len({(r['benchmark_id'],r['slice_id'],r['model']) for r in rows})==len(rows),'Duplicate record key'
 for path,h in d['input_sha256'].items():
  q=Path(path);q=q if q.is_absolute() else R/q;assert sha(q)==h,(path,'input changed')
 for t in d['tasks']:
  for track in [t,t['first_attempt'],t['repair_assisted']]:
   assert set(track['scores'])==set(MODELS) and len(track['pairs'])==6
   assert all(v is None or isinstance(v,(int,float)) and math.isfinite(v) for v in track['scores'].values())
   for pair in track['pairs']:
    complete=all(track['scores'][m] is not None for m in [pair['older'],pair['newer']])
    assert (pair['outcome']=='incomplete')!=complete
    assert (pair['raw_native_delta'] is not None)==complete
  assert t['scores']==t['repair_assisted']['scores']
  assert t['specialist_review']['benchmark_id']==t['benchmark_id']
  assert not t['primary_reference']['current_sota_verified']
 for row in d['task_direction_summaries']:
  assert sum(row['counts'].values())==row['n_tasks']
 for row in d['strict_format_task_direction_summaries']:
  assert row['eligible_task_pairs']+row['incomplete']+row['format_ineligible']==30
  assert sum(row['counts'].values())==row['eligible_task_pairs']
 for m in MODELS:
  r=next(x for x in s['model_summaries'] if x['model']==m);assert r['valid']+r['failed']==r['attempted']==37
  assert r['strict_format_valid']<=r['valid']
 if not a.no_website:
  for name in ['generation-comparison.json','comparison-summary.json','comparison-measurements.jsonl']:
   assert (R/'website/data'/name).read_bytes()==(a.output_root/name).read_bytes(),name
 print('Four-model comparison:30tasks,14categories,148attempts,6pairs/task; provenance and failure handling checked.')
if __name__=='__main__':main()
