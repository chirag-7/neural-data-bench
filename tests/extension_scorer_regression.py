"""Scorer-only regression; never executes generated procedures or modifies data.
Creates scratch copies in --scratch and compares every non-codec saved prediction
against its original ledger score. Posterior C2ST is opt-in because it is slow.
The new execution seal is bypassed ONLY for this scorer regression: original
prediction hashes are explicitly checked. No new model result is recorded.
"""
from pathlib import Path
import argparse, json, shutil, sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import extension_evaluate as e
p=argparse.ArgumentParser();p.add_argument('--scratch',required=True);p.add_argument('--include-posterior',action='store_true');a=p.parse_args()
base=Path(a.scratch).resolve();base.mkdir(parents=True,exist_ok=True)
rows=[json.loads(s) for s in (ROOT/'results/measurements.jsonl').read_text().splitlines()]
e.check=lambda task=None:None
out=[]
for task in e.manifest()['tasks']:
 for sid in task['original_slices']:
  t=task['benchmark_id']
  if t in {'B07','B08'} or t=='L06' and not a.include_posterior:continue
  r=next(r for r in rows if r['benchmark_id']==t and r['slice_id']==sid and r['model'].startswith('gpt') and r['status']=='measured')
  f=ROOT/r['prediction_file'];assert e.sha(f)==r['prediction_sha256']
  d=base/t/sid;d.mkdir(parents=True,exist_ok=True)
  shutil.copyfile(f,d/('predictions.json' if t=='N05' else 'predictions.npz'))
  e.folder=lambda *args,d=d:d
  try:
   audit_dir=ROOT/'data/cache/extension-scorer-regression'/base.name/t/sid
   if t=='L06':audit_dir.mkdir(parents=True,exist_ok=True)
   v=e.score(t,sid,e.MODELS[0],audit_dir=audit_dir if t=='L06' else None);delta=abs(v['score']-r['score']);assert delta<1e-10,(v['score'],r['score'])
   row=dict(task=t,slice_id=sid,status='passed',score=v['score'],absolute_delta=delta,original_prediction_file=r['prediction_file'],original_prediction_sha256=r['prediction_sha256'])
  except Exception as ex:row=dict(task=t,slice_id=sid,status='failed',reason=repr(ex))
  print(json.dumps(row),flush=True);out.append(row)
(base/'report.json').write_text(json.dumps(out,indent=2)+'\n')
assert all(r['status']=='passed' for r in out)
