"""Separate post-hoc repairs: never modify or integrate original single shots.

prepare seals source/patch/input hashes before any repaired procedure is scored.
evaluate runs each procedure with180s/one numerical thread and preserves outputs.
B08 runs all unchanged programs/references under the explicit heapq whitelist;
verify-decode is a fresh process with only code and payloads, never original data.
"""
from pathlib import Path
import argparse,ast,concurrent.futures,difflib,hashlib,importlib.util,json,os,subprocess,sys,time
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'experiments/repairs-v1'
MODELS=('gpt-5.6-sol','gpt-6-sol','gpt-6.1-sol')
METHODS={'B08':MODELS+('spikepack','task-baseline'),'J08':('gpt-6.1-sol',),'N05':('gpt-5.6-sol',)}
THREADS=dict(OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',MKL_NUM_THREADS='1',VECLIB_MAXIMUM_THREADS='1',NUMEXPR_NUM_THREADS='1',PYTHONDONTWRITEBYTECODE='1')

def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def write(path,value):Path(path).parent.mkdir(parents=True,exist_ok=True);Path(path).write_text(json.dumps(value,indent=2,allow_nan=False)+'\n')
def module(path,name):
 spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
def original_rows(task):return json.loads((ROOT/f'results/{task}.json').read_text())
def code_namespace(code,task):
 allowed={'numpy','scipy','sklearn','math','collections','functools','itertools','statistics','gc'}
 if task=='B08':allowed|={'heapq','zlib','bz2','lzma','struct','json','io','base64'}
 if task=='N05':allowed={'numpy','h5py','math','json','re','collections','functools','itertools','statistics'}
 for n in ast.walk(ast.parse(code)):
  if isinstance(n,ast.Import):assert all(v.name.split('.')[0] in allowed for v in n.names)
  if isinstance(n,ast.ImportFrom):assert (n.module or '').split('.')[0] in allowed
  if isinstance(n,ast.Call) and isinstance(n.func,ast.Name):assert n.func.id not in {'open','exec','eval','compile','__import__','input','breakpoint'}
 ns={};exec(compile(code,'posthoc-repaired-program','exec'),ns);return ns

def c05_diagnosis():
 import pandas as pd
 cache=ROOT/'data/cache/spikefinder';cases=[]
 for row in original_rows('C05'):
  if row['status']=='measured':continue
  sid=row['slice_id'];method=row['model'];source=cache/f'{sid}.{method}.csv';inputs=cache/f'{sid}.test.calcium.csv'
  table=pd.read_csv(source);a=table.to_numpy(float);x=pd.read_csv(inputs).to_numpy(float)
  bad=[]
  for j in range(x.shape[1]):
   finite_input=np.flatnonzero(np.isfinite(x[:,j]));missing=finite_input[(finite_input>=a.shape[0])|~np.isfinite(a[np.minimum(finite_input,a.shape[0]-1),j])]
   bad.append(dict(cell=j,input_observations=len(finite_input),missing_archived_predictions=len(missing),first_missing_indices=missing[:12].tolist()))
  cases.append(dict(benchmark_id='C05',slice_id=sid,model=method,original_status='failed',
   status='not_repairable_without_new_predictions',score=None,original_failure=row['reason'],
   source_file=str(source.relative_to(ROOT)),source_sha256=sha(source),source_shape=list(a.shape),input_shape=list(x.shape),
   numeric_headers_are_present=table.columns.tolist()==[str(i) for i in range(a.shape[1])],coverage=bad,
   reason='Archived values are genuinely absent/nonfinite on observed input support; no documented invertible row/cell alignment recovers missing scientific predictions. Complete-coverage contract cannot be repaired by padding, interpolation, copying truth or dropping target samples.',
   legacy_scorer_note='Original upstream scorer jointly masks prediction/target NaNs and truncates after40ms downsampling. That is a different partial-coverage scoring contract; adopting it would not repair complete-coverage predictions. No legacy score is substituted.'))
 return cases

def prepare():
 BASE.mkdir(parents=True,exist_ok=True)
 original_files=[ROOT/'results/measurements.jsonl']
 for task in ['B08','J08','N05','C05']:original_files.append(ROOT/f'results/{task}.json')
 preservation={str(p.relative_to(ROOT)):sha(p) for p in original_files}
 for task,methods in METHODS.items():
  folder=BASE/task;folder.mkdir(exist_ok=True);assert not (folder/'run-spec.json').exists(),'Repair seal already exists'
  originals=[];changes=[]
  for method in methods:
   if method not in MODELS:continue
   source=ROOT/f'experiments/{task}/{method}.json';obj=json.loads(source.read_text());before=obj['code'];after=before
   if task=='J08':
    assert before.count('np.unique(gt, return_inverse=True)')==1 and before.count('np.unique(pred, return_inverse=True)')==1
    after=before.replace('np.unique(gt, return_inverse=True)','np.unique(gt.ravel(), return_inverse=True)').replace('np.unique(pred, return_inverse=True)','np.unique(pred.ravel(), return_inverse=True)')
   elif task=='N05':
    old='        handle.visititems(visitor)\n        result = {}'
    new='        handle.visititems_links(lambda name, link: visitor(name, handle[name]) if isinstance(link, h5py.HardLink) else None)\n        result = {}'
    assert before.count(old)==1;after=before.replace(old,new)
   (folder/(method+'.original.py')).write_text(before);(folder/(method+'.py')).write_text(after)
   diff=''.join(difflib.unified_diff(before.splitlines(True),after.splitlines(True),fromfile='original/'+method+'.py',tofile='repairs-v1/'+method+'.py'))
   (folder/(method+'.patch.diff')).write_text(diff)
   originals.append(dict(model=method,source_json=str(source.relative_to(ROOT)),source_json_sha256=sha(source),
    original_code_sha256=hashlib.sha256(before.encode()).hexdigest(),repaired_code_sha256=hashlib.sha256(after.encode()).hexdigest(),
    code_unchanged=before==after,original_code_lines=len(before.splitlines()),repaired_code_lines=len(after.splitlines())))
   changes.append(dict(model=method,diff_file=str((folder/(method+'.patch.diff')).relative_to(ROOT))))
  reason={'B08':'Harness-only repair: explicitly allow heapq as ordinary standard-library utility; all three generated programs are byte-unchanged. Re-run same two references as controls. Timing/labels/fidelity/scorer/budget unchanged. Original rejected attempts remain failures.',
   'J08':'Two-line shape repair: flatten arrays before np.unique(return_inverse=True), so inverse labels and flattened pixel masks share dimensions under current NumPy. No thresholds, features, hyperparameters, labels, matching rules or scoring are changed.',
   'N05':'One-line metadata traversal repair: visititems deduplicates hard-linked HDF5 objects and misses stimulus aliases under the sweep path. visititems_links visits every hard-link path; resolve handle[name], then preserve original sweep/role/unit metadata logic. No expected numerical answers or source-specific measured values are introduced.'}[task]
  (folder/'rationale.md').write_text('# Separate post-hoc repair v1\n\n'+reason+'\n\nThis is repair-assisted performance, never a replacement for the original single-shot attempt. No new LLM call or test-label-dependent parameter tuning. Sealed before rescoring,180seconds and one numerical CPU thread per procedure. B08 additional fresh-process decoding is verification, separately timed.\n')
  inputs=[]
  if task=='B08':
   a=module(ROOT/'experiments/B08/adapter.py','repair_b08_manifest');inputs=[ROOT/f['path'] for f in a.manifest()['files']]+[ROOT/'experiments/B08/reference.py',ROOT/'data/manifests/B08.json']
   for f in (ROOT/'experiments/B08/upstream').rglob('*'):
    if f.is_file() and '__pycache__' not in f.parts:inputs.append(f)
  elif task=='J08':inputs=[ROOT/'data/cache/J08/data.npz',ROOT/'experiments/J08/adapter.py']
  else:inputs=[ROOT/'data/cache/N05'/name for name in ['fixture.nwb','expected.json','tolerances.json']]+[ROOT/'scripts/workflow.py']
  sources=[ROOT/v['source_json'] for v in originals]+[ROOT/f'results/{task}.json',ROOT/f'experiments/{task}/run-spec.json']
  files=[f for f in folder.iterdir() if f.is_file()]+inputs+sources+[Path(__file__).resolve()]
  spec=dict(repair_track='posthoc-repairs-v1',benchmark_id=task,methods=list(methods),date='2026-11-01',
   original_outputs_preserved=True,originals=originals,patches=changes,rationale=reason,
   no_new_model_calls=True,no_test_targets_in_patch_logic=True,timeout_seconds=180,numerical_threads=1,
   procedure='encode+fresh namespace decode for all7recordings' if task=='B08' else 'single repaired extract/fit_predict call',
   frozen_files={str(f.relative_to(ROOT)):sha(f) for f in sorted(set(files))},status='sealed before repaired execution and scoring')
  write(folder/'run-spec.json',spec)
 folder=BASE/'C05';folder.mkdir(exist_ok=True);assert not (folder/'run-spec.json').exists()
 cases=c05_diagnosis();write(folder/'diagnosis.json',cases)
 evidence={'pin':'def1f8c2c5268eb71e83f57c265d4b3c102fb5f8','source_manifest':'data/manifests/spikefinder.json',
  'primary_sources':['https://github.com/berenslab/spikefinder_analysis','https://github.com/berenslab/spikefinder_analysis/blob/def1f8c2c5268eb71e83f57c265d4b3c102fb5f8/spikefinder_eval.py'],
  'evidence':'Upstream score() jointly masks NaNs and crops pairs; archive CSVs already contain0..N-1headers. No orientation/header correction supplies missing values. Preserving complete support is scientifically necessary for comparability.',
  'reactivation':'Obtain a complete timestamp-aligned original submission with a documented source/version mapping, or run the original algorithm to create new scientific predictions under a separately frozen reproduction track.'}
 write(folder/'source-evidence.json',evidence)
 files=[ROOT/'results/C05.json',ROOT/'data/manifests/spikefinder.json',ROOT/'data/cache/spikefinder/spikefinder_eval.py',folder/'diagnosis.json',folder/'source-evidence.json']
 files+=[ROOT/c['source_file'] for c in cases]
 write(folder/'run-spec.json',dict(repair_track='posthoc-repairs-v1',benchmark_id='C05',status='not repairable from archived values under original complete-coverage contract',cases=4,frozen_files={str(p.relative_to(ROOT)):sha(p) for p in files},no_predictions_fabricated=True))
 write(BASE/'original-preservation.json',preservation)
 print('Sealed B08/J08/N05 repairs and all4C05 source diagnoses; no repaired scoring performed.',flush=True)

def check(task):
 spec=json.loads((BASE/task/'run-spec.json').read_text())
 for rel,h in spec['frozen_files'].items():assert sha(ROOT/rel)==h,'Repair seal mismatch: '+rel
 return spec

def one(task,method):
 spec=check(task);folder=BASE/task;out=folder/'artifacts'/method;out.mkdir(parents=True,exist_ok=False)
 code=(folder/(method+'.py')).read_text() if method in MODELS else None
 if code is not None:ns=code_namespace(code,task)
 np.random.seed(0);start=time.perf_counter()
 if task=='B08':
  adapter=module(ROOT/'experiments/B08/adapter.py','repair_codec_adapter');arrays=adapter.load();sources=adapter.manifest()['files']
  reference=module(ROOT/'experiments/B08/reference.py','repair_codec_reference') if code is None else None
  items=[];encode_s=decode_s=0.
  for i,((t,y),source) in enumerate(zip(arrays,sources)):
   then=time.perf_counter();blob=ns['compress'](t.copy(),y.copy()) if code is not None else reference.compress(t,y,method);es=time.perf_counter()-then
   assert isinstance(blob,(bytes,bytearray,memoryview));blob=bytes(blob);p=out/f'{i:02d}.bin';p.write_bytes(blob)
   decode=code_namespace(code,task)['decompress'] if code is not None else lambda b:reference.decompress(b,method)
   then=time.perf_counter();tt,yy=decode(blob);ds=time.perf_counter()-then;error=adapter.validate(tt,yy,t,y)
   items.append(dict(recording=source['recording'],n_events=len(t),compressed_file=str(p.relative_to(ROOT)),compressed_bytes=len(blob),compressed_sha256=sha(p),
    decoded_times_sha256=hashlib.sha256(np.ascontiguousarray(tt).tobytes()).hexdigest(),decoded_labels_sha256=hashlib.sha256(np.ascontiguousarray(yy).tobytes()).hexdigest(),max_timing_error_seconds=error,labels_exact=True,encode_seconds=es,decode_seconds=ds))
   write(out/'payloads.json',items);encode_s+=es;decode_s+=ds
  per=[8*r['compressed_bytes']/r['n_events'] for r in items]
  scored=dict(score=float(np.mean(per)),metric='mean_encoded_bits_per_event_50us',direction='lower',per_unit=per,n_recordings=7,n_events=sum(r['n_events'] for r in items),max_timing_error_seconds=max(r['max_timing_error_seconds'] for r in items),encode_seconds=encode_s,decode_seconds=decode_s)
  prediction=out/'payloads.json'
 elif task=='J08':
  adapter=module(ROOT/'experiments/J08/adapter.py','repair_j08');x,y,xt,truth=adapter.load()
  then=time.perf_counter();pred=np.asarray(ns['fit_predict'](x.copy(),y.copy(),xt.copy()));elapsed=time.perf_counter()-then
  # Original scorer sees the same independent human masks; no new consensus.
  scored=dict(score=adapter.score(pred,truth),metric='instance_f1_iou50_multirater',direction='higher',per_unit=[adapter.score(pred[i:i+1],truth[i:i+1]) for i in range(len(pred))])
  prediction=out/'predictions.npz';np.savez_compressed(prediction,predictions=pred);scored['estimator_seconds']=elapsed
 else:
  sys.path.insert(0,str(ROOT/'scripts'));import workflow
  then=time.perf_counter();answer=ns['extract'](str(ROOT/'data/cache/N05/fixture.nwb'));elapsed=time.perf_counter()-then
  scored=workflow.score(answer);prediction=out/'answer.json';write(prediction,answer);scored['estimator_seconds']=elapsed
 elapsed=time.perf_counter()-start
 old=next(r for r in original_rows(task) if r['model']==method)
 return dict(benchmark_id=task,repair_track='posthoc-repairs-v1',method=method,status='measured',
  original_status=old['status'],repair_kind='harness_only' if task=='B08' else 'manual_minimal_algorithm_patch',
  control_originally_successful=old['status']=='measured',no_new_model_calls=True,original_first_attempt_replaced=False,
  seconds=elapsed,code_sha256=hashlib.sha256(code.encode()).hexdigest() if code is not None else sha(ROOT/'experiments/B08/reference.py'),
  code_lines=len(code.splitlines()) if code is not None else None,line_limit_compliant=len(code.splitlines())<240 if code is not None else None,
  repair_spec_sha256=sha(folder/'run-spec.json'),prediction_file=str(prediction.relative_to(ROOT)),prediction_sha256=sha(prediction),**scored)

def decode(plan_path):
 plan=json.loads(Path(plan_path).read_text());method=plan['method'];program=ROOT/plan['program'];assert sha(program)==plan['program_file_sha256']
 if method in MODELS:
  code=program.read_text();ns=code_namespace(code,'B08');fn=ns['decompress'];codehash=hashlib.sha256(code.encode()).hexdigest()
 else:
  ref=module(program,'repair_decode_reference');fn=lambda b:ref.decompress(b,method);codehash=sha(program)
 result=[]
 for i,item in enumerate(plan['payloads']):
  p=ROOT/item['compressed_file'];assert sha(p)==item['compressed_sha256'];t,y=fn(p.read_bytes())
  assert isinstance(t,np.ndarray) and isinstance(y,np.ndarray) and t.shape==y.shape and np.isfinite(t).all() and np.all(np.diff(t)>=0)
  out=ROOT/plan['output_dir']/f'{i:02d}.npz';np.savez_compressed(out,times=t,labels=y)
  result.append(dict(decoded_file=str(out.relative_to(ROOT)),sha256=sha(out),n_events=len(t),times_sha256=hashlib.sha256(np.ascontiguousarray(t).tobytes()).hexdigest(),labels_sha256=hashlib.sha256(np.ascontiguousarray(y).tobytes()).hexdigest()))
 report=dict(pid=os.getpid(),parent_pid=os.getppid(),encoder_invoked=False,source_arrays_loaded=False,code_sha256=codehash,items=result)
 write(ROOT/plan['report_file'],report)

def verify_b08(row):
 method=row['method'];folder=BASE/'B08/artifacts'/method;dest=folder/'fresh-decode';dest.mkdir(exist_ok=False)
 items=json.loads((ROOT/row['prediction_file']).read_text());program=BASE/'B08'/(method+'.py') if method in MODELS else ROOT/'experiments/B08/reference.py'
 plan=dict(method=method,program=str(program.relative_to(ROOT)),program_file_sha256=sha(program),payloads=items,output_dir=str(dest.relative_to(ROOT)),report_file=str((dest/'audit.json').relative_to(ROOT)))
 pp=dest/'plan.json';write(pp,plan);env=dict(os.environ,**THREADS)
 proc=subprocess.run([sys.executable,str(Path(__file__).resolve()),'decode','--plan',str(pp)],env=env,capture_output=True,text=True,timeout=180,cwd=dest)
 (dest/'stdout.txt').write_text(proc.stdout);(dest/'stderr.txt').write_text(proc.stderr);assert proc.returncode==0,proc.stderr[-3000:]
 report=json.loads((dest/'audit.json').read_text());assert report['pid']!=os.getpid() and not report['encoder_invoked'] and not report['source_arrays_loaded']
 assert report['code_sha256']==row['code_sha256']
 adapter=module(ROOT/'experiments/B08/adapter.py','repair_decode_validation');originals=adapter.load();errors=[]
 for saved,item,(t,y) in zip(items,report['items'],originals):
  p=ROOT/item['decoded_file'];assert sha(p)==item['sha256'];assert item['times_sha256']==saved['decoded_times_sha256'] and item['labels_sha256']==saved['decoded_labels_sha256']
  with np.load(p,allow_pickle=False) as z:error=adapter.validate(z['times'],z['labels'],t,y)
  errors.append(error)
 assert len(errors)==7
 return dict(status='passed',fresh_process=True,encoder_invoked=False,original_arrays_only_loaded_after_child_exit=True,n_recordings=7,max_timing_error_seconds=max(errors),report_file=str((dest/'audit.json').relative_to(ROOT)),report_sha256=sha(dest/'audit.json'))

def evaluate():
 output=ROOT/'results/repairs-v1.json';assert not output.exists(),'Never overwrite a repair track'
 env=dict(os.environ,**THREADS);jobs=[(t,m) for t,methods in METHODS.items() for m in methods]
 def run(job):
  task,method=job;folder=BASE/task;log=folder/'execution'/f'{method}.txt';log.parent.mkdir(exist_ok=True)
  try:
   p=subprocess.run([sys.executable,str(Path(__file__).resolve()),'one','--task',task,'--method',method],env=env,capture_output=True,text=True,timeout=180)
   log.write_text(p.stdout+'\n'+p.stderr)
   assert p.returncode==0,p.stderr[-3500:]
   row=json.loads(p.stdout.strip().splitlines()[-1])
   if task=='B08':row['independent_decode']=verify_b08(row)
  except Exception as exc:row=dict(benchmark_id=task,method=method,repair_track='posthoc-repairs-v1',status='repair_failed',reason=str(exc),original_first_attempt_replaced=False)
  row['execution_log']=str(log.relative_to(ROOT));return row
 rows=[]
 with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
  futures={pool.submit(run,j):j for j in jobs}
  for f in concurrent.futures.as_completed(futures):
   row=f.result();rows.append(row);print(row['benchmark_id'],row['method'],row['status'],row.get('score'),flush=True)
   write(output,dict(track='posthoc-repairs-v1',status='running',attempts=rows,c05_cases=json.loads((BASE/'C05/diagnosis.json').read_text())))
 original=json.loads((BASE/'original-preservation.json').read_text())
 for rel,h in original.items():assert sha(ROOT/rel)==h,'Original result changed: '+rel
 for task in ['B08','J08','N05','C05']:check(task)
 report=dict(track='posthoc-repairs-v1',status='complete',not_single_shot=True,excluded_from_original_macro=True,
  new_model_calls=0,attempts=sorted(rows,key=lambda r:(r['benchmark_id'],r['method'])),c05_cases=json.loads((BASE/'C05/diagnosis.json').read_text()),
  original_results_and_ledger_unchanged=True,original_preservation_file=str((BASE/'original-preservation.json').relative_to(ROOT)),
  original_failures_considered=8,repair_assisted_failures_recovered=sum(r['status']=='measured' and r.get('original_status')=='failed' for r in rows),
  controls_reexecuted=sum(r['status']=='measured' and r.get('control_originally_successful') for r in rows),
  irreparable_archived_cases=4,scientific_caveat='Post-hoc debugging and explicit harness correction; do not mix repair-assisted performance with unchanged first-submission evidence. Missing archived predictions were not fabricated.')
 write(output,report);print('Separate repair track complete:',str(output.relative_to(ROOT)),flush=True)

if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('action',choices=['prepare','evaluate','one','decode']);p.add_argument('--task');p.add_argument('--method');p.add_argument('--plan');args=p.parse_args()
 if args.action=='prepare':prepare()
 elif args.action=='evaluate':evaluate()
 elif args.action=='one':print(json.dumps(one(args.task,args.method),allow_nan=False))
 else:decode(args.plan)
