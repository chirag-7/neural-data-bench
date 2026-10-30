"""Append audited specialist predictions without changing existing Sol submissions/results."""
from pathlib import Path
import json,hashlib,sys
import numpy as np
from expansion import ROOT as R,adapter,scoring,metadata,sha
REFERENCES=[('H01','pyriemann-aligned','specialist-aligned-runtime.json','local_specialist_reproduction'),('H01','pyriemann-ts-svm','specialist-runtime.json','local_specialist_reproduction'),('H08','yasa-eeg','specialist-runtime.json','pretrained_specialist')]
def main():
 for task,model,runtime,kind in REFERENCES:
  if not (R/f'results/{task}.json').exists():continue
  info=json.loads((R/f'experiments/{task}/{runtime}').read_text());file=info['prediction_file'];p=R/file;assert sha(p)==info['prediction_sha256'];x,y,xt,truth=adapter(task).load()
  with np.load(p) as z:pred=z['predictions']
  scored=scoring(task,pred,truth,xt,metadata(task));record=dict(benchmark_id=task,slice_id='expansion-v1',model=model,status='measured',date='2026-10-30',track='reference',reference_type=kind,n_units=len(truth),seconds=info['seconds'],prediction_file=file,prediction_sha256=sha(p),input_sha256={f'data/cache/{task}/data.npz':sha(R/f'data/cache/{task}/data.npz')},specialist_runtime_record=f'experiments/{task}/{runtime}',superiority_eligible=False,superiority_reason='Published specialist implementation/checkpoint applied to exact slice; training/selection budgets differ and current strongest method unverified',**scored)
  rp=R/f'results/{task}.json';rows=[r for r in json.loads(rp.read_text()) if r['model']!=model];rows.append(record);rp.write_text(json.dumps(rows,indent=2));print(task,model,scored['score'])
if __name__=='__main__':main()
