"""Re-score every expanded stored prediction; no retraining, model calls or source downloads."""
import hashlib,importlib.util,json
import numpy as np
from expansion import ROOT as R,MODELS,adapter,metadata,scoring,sha
import workflow
records=[json.loads(x) for x in (R/'results/measurements.jsonl').read_text().splitlines()];tasks=sorted(set(r['benchmark_id'] for r in records)-{'C05','M04'});checks={};count=0
for task in tasks:
 d=R/f'experiments/{task}';spec=json.loads((d/'run-spec.json').read_text());assert sha(d/'prompt.txt')==spec['prompt_sha256'];provenance=json.loads((d/'generation-provenance.json').read_text());assert len(provenance)==3
 for p in provenance:
  assert p['tool_events']==0 and p['usage'] is not None
  assert p['code_sha256']==hashlib.sha256(json.loads((d/(p['requested_model']+'.json')).read_text())['code'].encode()).hexdigest()
 if task=='N05':
  for path,key in [(d/'reference.py','reference_sha256'),(R/'data/cache/N05/fixture.nwb','fixture_sha256'),(R/'data/cache/N05/expected.json','expected_sha256'),(R/'data/cache/N05/tolerances.json','tolerances_sha256')]:assert sha(path)==spec[key]
 elif task=='B01':
  assert sha(d/'adapter.py')==spec['adapter_sha256'];assert sha(R/'data/cache/B01/inputs.npz')==spec['inputs_sha256'];assert sha(R/'data/cache/B01/truth.npz')==spec['truth_sha256']
 else:
  assert sha(d/'adapter.py')==spec['adapter_sha256'];assert sha(R/f'data/cache/{task}/data.npz')==spec['data_sha256'];x,y,xt,truth=adapter(task).load();meta=metadata(task)
 for r in [v for v in records if v['benchmark_id']==task]:
  if r['status']!='measured':continue
  p=R/r['prediction_file'];assert sha(p)==r['prediction_sha256']
  if task=='N05':res=workflow.score(json.loads(p.read_text()))
  else:
   with np.load(p) as z:pred=z['predictions'] if 'predictions'in z else z['pred'] if 'pred'in z else z[z.files[0]]
   if task=='B01':res=dict(score=adapter('B01').score(pred)['mean_gt_accuracy'])
   elif r.get('adapter_file'):
    path=R/r['adapter_file'];s=importlib.util.spec_from_file_location('rescore_slice',path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);sd=json.loads((path.parent/'run-spec.json').read_text());assert sha(path)==sd['adapter_sha256'];assert sha(R/f'data/cache/E01-{r["slice_id"]}/data.npz')==sd['data_sha256'];a,b,c,t=m.load();res=dict(score=m.score(pred,t));assert pred.shape==t.shape and np.isfinite(pred).all() and (pred>=0).all()
   else:res=scoring(task,pred,truth,xt,meta)
   if task=='F04':
    _,inverse=np.unique(xt,axis=0,return_inverse=True)
    for group in np.unique(inverse):assert np.max(np.ptp(pred[inverse==group],axis=0))<1e-12
  assert np.isclose(res['score'],r['score'],rtol=0,atol=1e-12),(task,r['model'],res['score'],r['score']);count+=1
 if task not in ['N05','B01']:
  with np.load(R/f'data/cache/{task}/data.npz') as z:
   if task in ['A09','A14','E01','F04','H01','H08','I07','K01','J08']:assert not set(map(str,z['train_groups'])) & set(map(str,z['test_groups']))
   if task=='H16':
    for kind in ['clean','artifact']:assert not set(z['train_'+kind+'_indices']) & set(z['test_'+kind+'_indices'])
   if task=='L04':assert z['test_times'].min()-z['train_times'].max()>=1.
 checks[task]=dict(predictions_rescored=sum(v['status']=='measured' and v['benchmark_id']==task for v in records),frozen_hashes='passed',generation_provenance='3 submissions,zero observed tool events')
checks['scope']='Exact prediction rescoring/hash/provenance checks, not independent expert validation or proof of uncontaminated pretraining';checks['expanded_tasks']=len(tasks);checks['expanded_prediction_records_rescored']=count
(R/'analysis/validation-expansion.json').write_text(json.dumps(checks,indent=2));print(json.dumps(checks,indent=2))
