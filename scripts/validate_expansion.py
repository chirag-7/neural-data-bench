"""Re-score every expanded stored prediction; no retraining, model calls or source downloads."""
import hashlib,importlib.util,json
import numpy as np
from expansion import ROOT as R,MODELS,adapter,metadata,scoring,sha
import workflow
BATCHEXPANDED={'B03','B08','C06','E06','K05','K06','A15'}

def validate_batch_task(task,task_rows):
 """Read-only independent rescoring; never run preparation/fitting/decoders."""
 d=R/f'experiments/{task}';spec=json.loads((d/'run-spec.json').read_text())
 assert spec['run_id']=='batch-v11' and sha(d/'prompt.txt')==spec['prompt_sha256']
 for filename,digest in spec['frozen_files'].items():assert sha(R/filename)==digest,filename
 prov=json.loads((d/'generation-provenance.json').read_text());events=json.loads((d/'generation-event-files.json').read_text())
 assert len(prov)==len(events)==3 and {p['requested_model'] for p in prov}==set(MODELS)
 for model in MODELS:
  obj=json.loads((d/(model+'.json')).read_text());codehash=hashlib.sha256(obj['code'].encode()).hexdigest()
  p=next(v for v in prov if v['requested_model']==model);e=next(v for v in events if v['model']==model)
  assert p['code_sha256']==codehash and p['tool_events']==0 and p['usage'] is not None and p['user_prompt_sha256']==spec['prompt_sha256']
  assert sha(R/e['event_file'])==e['sha256'] and e['tool_events']==0 and e['submission_matches_final_generation_event']
  raw=[json.loads(line) for line in (R/e['event_file']).read_text().splitlines() if line.strip()]
  messages=[v['item']['text'] for v in raw if v.get('type')=='item.completed' and v.get('item',{}).get('type')=='agent_message']
  assert json.loads(messages[-1])==obj and next(v['usage'] for v in reversed(raw) if v.get('type')=='turn.completed')==p['usage']
  assert sum(v.get('item',{}).get('type') not in [None,'agent_message','reasoning'] for v in raw)==0
 paths={'B03':'results/audits/B03-batch-v11.json','C06':'results/audits/C06-batch-v11.json',
  'E06':'results/verification/E06-batch-v11.json','K05':'results/audits/cells-batch-v11.json',
  'K06':'results/audits/cells-batch-v11.json','B08':'results/verification/B08-independent-final.json','A15':'results/audits/A15-batch-v11.json'}
 retained=json.loads((R/paths[task]).read_text())
 if task=='B08':
  # Fresh-process independent decoding was completed and retained separately.
  # Do not invoke verify_event_batch (which spawns decoders) during validation.
  audit=retained;assert not audit['encoder_invoked'] and not audit['missing_attempts'] and len(audit['original_sources'])==7
  for row in task_rows:
   key=(row['slice_id'],row['model'])
   if row['status']!='measured':
    assert any(v['model']==row['model'] and v['status']==row['status'] and v['reason']==row['reason'] for v in audit['failed_attempts']);continue
   identity=next(v for v in audit['measured_attempts'] if v['model']==row['model'])
   p=R/row['prediction_file'];assert sha(p)==row['prediction_sha256'];items=json.loads(p.read_text())
   assert len(items)==7 and identity['seven_recordings_passed'] and identity['code_sha256']==row['code_sha256']
   per=[]
   for item,source in zip(items,audit['original_sources']):
    blob=R/item['compressed_file'];assert sha(blob)==item['compressed_sha256'] and blob.stat().st_size==item['compressed_bytes']
    assert item['recording']==source['recording'] and item['n_events']==source['n_events'] and item['labels_exact']
    assert item['max_timing_error_seconds']<=50e-6+1e-10
    per.append(8*item['compressed_bytes']/item['n_events'])
   assert np.allclose(per,identity['per_record_bits_per_event'],rtol=0,atol=1e-12)
   assert np.isclose(sum(per)/7,row['score'],rtol=0,atol=1e-12) and np.isclose(identity['score'],row['score'],rtol=0,atol=1e-12)
   assert identity['total_encoded_bytes']==sum(v['compressed_bytes'] for v in items)
   assert identity['max_timing_error_seconds']<=50e-6+1e-10 and row['prompt_sha256']==spec['prompt_sha256']
 else:
  if task=='B03':
   from verify_motion_batch import audit as independent
   audit=independent(require_complete=True)
  elif task=='C06':
   from verify_c06_batch import audit as independent
   audit=independent(require_complete=True)
  elif task=='E06':
   from verify_e06_batch import audit as independent
   audit=independent(require_complete=True)
  elif task in ['K05','K06']:
   from verify_cell_batch import audit_task
   audit=audit_task(task,require_complete=True)
   retained=next(v for v in retained['tasks'] if v['benchmark_id']==task)
  else:
   from verify_a15_batch import audit as independent
   audit=independent(require_complete=True)
  assert audit['complete'] and not audit['models_or_references_executed']
  fresh={(v.get('slice_id','batch-v11'),v['model']):v for v in audit['measured_attempts']}
  old={(v.get('slice_id','batch-v11'),v['model']):v for v in retained['measured_attempts']}
  assert set(fresh)==set(old)
  for row in task_rows:
   assert row['status']=='measured';key=(row['slice_id'],row['model']);a=fresh[key];b=old[key]
   assert a['prediction_sha256']==b['prediction_sha256']==row['prediction_sha256']
   assert a.get('code_sha256',a.get('program_sha256'))==row['code_sha256']
   value=a.get('score',a.get('independent_metric',{}).get('score'));oldvalue=b.get('score',b.get('independent_metric',{}).get('score'))
   assert np.isclose(value,row['score'],rtol=1e-7,atol=2e-6) and np.isclose(oldvalue,value,rtol=1e-7,atol=2e-6)
 for row in task_rows:
  if row.get('scorer_audit_file'):assert row['scorer_audit_file']==paths[task] and sha(R/paths[task])==row['scorer_audit_sha256']
 n=sum(v['status']=='measured' for v in task_rows)
 return dict(predictions_rescored=n,frozen_hashes='passed',generation_provenance='3 unchanged submissions; raw retained no-tool events/usage checked',
  independent_audit_file=paths[task],independent_audit_sha256=sha(R/paths[task]),
  source_and_scorer_audit='Completed independent decoder report and all retained payload hashes/byte counts' if task=='B08' else 'Original source targets independently reconstructed and saved predictions rescored',
  failed_attempts_preserved=sum(v['status']!='measured' for v in task_rows),models_references_generators_or_decoders_executed=False)

records=[json.loads(x) for x in (R/'results/measurements.jsonl').read_text().splitlines()];tasks=sorted(set(r['benchmark_id'] for r in records)-{'C05','M04'});checks={};count=0
if BATCHEXPANDED.intersection(tasks):
 assert BATCHEXPANDED.issubset(tasks),'Partially integrated batch task set'
 for line in (R/'results/archive/v10-measurements.jsonl').read_text().splitlines():assert json.loads(line) in records,'A v0.10 historical measurement changed'
for task in tasks:
 if task in BATCHEXPANDED:
  checked=validate_batch_task(task,[r for r in records if r['benchmark_id']==task]);checks[task]=checked;count+=checked['predictions_rescored'];continue
 if task=='B07':
  from verify_compression import verify as verify_codec
  v=verify_codec(write=False);n=len(v['prediction_checks']);checks[task]=dict(predictions_rescored=n,frozen_hashes='passed',bitstreams_verified=sum(x['bitstreams_verified'] for x in v['prediction_checks']),source_bytes_verified=v['source_bytes_verified']);count+=n;continue
 if task=='L06':
  from verify_posteriors import verify
  v=verify(write=False);n=len(v['prediction_checks']);checks[task]=dict(predictions_rescored=n,frozen_hashes='passed',source_and_posterior_audit='All primary accuracies from heldout decisions and all secondary slicedW2 independently reproduced; no classifier refit');count+=n;continue
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
   if task in ['A09','A14','E01','F04','H01','H02','H08','I07','K01','K04','M01','J08']:assert not set(map(str,z['train_groups'])) & set(map(str,z['test_groups']))
   if task=='H16':
    for kind in ['clean','artifact']:assert not set(z['train_'+kind+'_indices']) & set(z['test_'+kind+'_indices'])
   if task=='L04':assert z['test_times'].min()-z['train_times'].max()>=1.
 checks[task]=dict(predictions_rescored=sum(v['status']=='measured' and v['benchmark_id']==task for v in records),frozen_hashes='passed',generation_provenance='3 submissions,zero observed tool events')
checks['scope']='Exact prediction rescoring/hash/provenance checks, not independent expert validation or proof of uncontaminated pretraining';checks['expanded_tasks']=len(tasks);checks['expanded_prediction_records_rescored']=count
(R/'analysis/validation-expansion.json').write_text(json.dumps(checks,indent=2));print(json.dumps(checks,indent=2))
