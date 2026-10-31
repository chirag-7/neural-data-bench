"""Batchable frozen T3 runner; per-task attempts are immutable, release integration is separate."""
from pathlib import Path
import argparse,hashlib,importlib.util,json,os,subprocess,sys,time
import numpy as np
from expansion import ROOT as R,MODELS,generate,validate_code
from compression_candidates import code_namespace
WORK=R.parents[1]/'work'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def mod(task,name='adapter'):
 p=R/f'experiments/{task}/{name}.py';s=importlib.util.spec_from_file_location(task+'_'+name,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def freeze(task):
 d=R/f'experiments/{task}';assert not any(d.glob('gpt-*.json')) and not (d/'run-spec.json').exists()
 groups=task in ['C06','K05','K06']
 if task=='B08':
  intro="""Implement compress(times, labels)->bytes and decompress(blob)->(times,labels). Decode only from blob in a fresh namespace. Inputs are one complete globally sorted float64 timestamp vector in seconds plus matching int32 unit labels. Preserve all labels and order, nondecreasing times, max50microsecond timing error per event (allowance1e-10s). All7recordings must pass; mean bits/event lowerbetter; every blob byte counts. Allowed compression stdlib zlib,bz2,lzma,struct,json,io,base64 plus usual numerical/utilities. No specialist package or file access. Read exact contract below."""
  data_paths=[R/f['path'] for f in mod(task).manifest()['files']]
 else:
  a=mod(task);x,y,xt,yt=a.load();assert all(np.isfinite(v).all() for v in [x[np.isfinite(x)],y,xt[np.isfinite(xt)],yt])
  group_description=({'K05':'a dictionary with group_ids (training donor IDs) and block_ids (training tissue-block IDs)','K06':'a dictionary with group_ids (training mouse IDs) and cv_fold (predeclared mouse-stratified training CV folds)'}.get(task,'the real training animal grouping vector'))+'; for train-only grouping/validation/weight construction, never biological predictors' if groups else 'None; no condition/stimulus or source group IDs are supplied'
  intro=f"""Implement fit_predict(train_x, train_y, test_x, train_groups)->numpy.ndarray. Shapes train_x={x.shape},train_y={y.shape},test_x={xt.shape}; output={yt.shape}. train_groups is {group_description}. Test groups/labels are scorer-only. Learn all fitted transforms from training data only. Return complete finite output in target units and follow mask/label rules below. Reference implementation receives the same training groups where needed. Allowed imports numpy,scipy,sklearn,math,collections,functools,itertools,statistics,gc. No pretrained weights, specialist packages, file/network/subprocess access or dynamic exec/eval."""
  data_paths=[R/f'data/cache/{task}/data.npz']
  if task=='E06':data_paths.append(R/'data/cache/E06-taxis/data.npz')
 prompt='''Single-shot neuroscience numerical procedure construction. Do not call tools, browse, read files or execute during generation. Return only JSON fields description and code, containing complete self-contained Python. Do not claim a score. One unchanged submission, no execution feedback or repairs. Under240 source lines including blanks; whole fit/predict or encode/decode workload180seconds, one numerical CPU thread, approximately4GB requested memory not enforced. Use deterministic seeds. Explicit prompt shared across the exact three requested Sol versions, reasoning effort high.\n\n'''+intro+'\n\nFrozen task contract:\n'+(d/'protocol.md').read_text()
 if task=='E06':
  prompt=prompt.replace(f'output={yt.shape}', 'output=(len(test_x),32,256)')+'\n\nSecond prespecified dependent slice (same program, no new generation):\n'+(d/'slices/taxis/protocol.md').read_text()
 (d/'prompt.txt').write_text(prompt);(d/'response_schema.json').write_text(json.dumps(dict(type='object',properties=dict(description=dict(type='string'),code=dict(type='string')),required=['description','code'],additionalProperties=False)))
 files=[p for p in d.rglob('*') if p.is_file() and (p.suffix in ['.py','.json','.md','.txt'] or p.name in ['LICENSE','COPYING']) and '__pycache__' not in p.parts and p.name not in ['worklog.md','run-spec.json']]+data_paths+[Path(__file__).resolve(),R/'scripts/expansion.py',R/'scripts/compression_candidates.py']
 manifest=R/f'data/manifests/{task}.json'
 if manifest.exists():files.append(manifest)
 spec=dict(benchmark_id=task,run_id='batch-v11',slice_id='batch-v11',date='2026-10-31',track='T3',models=MODELS,reasoning_effort='high',generation_replicates=1,timeout_seconds=180,line_limit_exclusive=240,memory_enforced=False,train_groups_supplied=groups,prompt_sha256=sha(d/'prompt.txt'),adapter_sha256=sha(d/'adapter.py'),frozen_files={str(p.relative_to(R)):sha(p) for p in sorted(set(files))},status='Frozen before model calls and all real-slice method scores')
 if task!='B08':spec['data_sha256']=sha(R/f'data/cache/{task}/data.npz')
 (d/'run-spec.json').write_text(json.dumps(spec,indent=2)+'\n');print(task,'frozen')
def check(task):
 spec=json.loads((R/f'experiments/{task}/run-spec.json').read_text())
 for p,h in spec['frozen_files'].items():assert sha(R/p)==h,p
 return spec
def one(task,model,slice_id='batch-v11'):
 spec=check(task);d=R/f'experiments/{task}';general=model in MODELS;info={}
 if general:
  obj=json.loads((d/(model+'.json')).read_text());code=obj['code']
  if task=='B08':ns=code_namespace(code)
  else:validate_code(code);ns={};exec(compile(code,'generated','exec'),ns)
  (d/(model+'.py')).write_text(code)
  info=dict(description=obj['description'],code_sha256=hashlib.sha256(code.encode()).hexdigest(),code_lines=len(code.splitlines()),line_limit_compliant=len(code.splitlines())<240)
 else:info=dict(code_sha256=sha(d/('reference.py' if task=='B08' else 'adapter.py')),selection='Fixed before model generation or evaluation scores')
 a=mod(task,'slices/taxis/adapter') if task=='E06' and slice_id=='taxis' else mod(task);meta=json.loads((R/f'data/cache/{task}/metadata.json').read_text()) if task!='B08' else {}
 if task=='B08':
  arrays=a.load();sources=a.manifest()['files'];ref=mod(task,'reference') if not general else None;items=[];enc_s=dec_s=0.
  folder=R/f'results/bitstreams/{task}/{model}';folder.mkdir(parents=True,exist_ok=True)
  for j,((t,y),src) in enumerate(zip(arrays,sources)):
   start=time.perf_counter();b=ns['compress'](t.copy(),y.copy()) if general else ref.compress(t,y,model);es=time.perf_counter()-start
   assert isinstance(b,(bytes,bytearray,memoryview));b=bytes(b);p=folder/f'{j:02d}.bin';p.write_bytes(b)
   decoder=code_namespace(code)['decompress'] if general else lambda x:ref.decompress(x,model)
   start=time.perf_counter();tt,yy=decoder(b);ds=time.perf_counter()-start;err=a.validate(tt,yy,t,y)
   item=dict(recording=src['recording'],n_events=len(t),compressed_file=str(p.relative_to(R)),compressed_bytes=len(b),compressed_sha256=sha(p),decoded_times_sha256=hashlib.sha256(np.ascontiguousarray(tt).tobytes()).hexdigest(),decoded_labels_sha256=hashlib.sha256(np.ascontiguousarray(yy).tobytes()).hexdigest(),max_timing_error_seconds=err,labels_exact=True,encode_seconds=es,decode_seconds=ds);items.append(item)
   (folder/'partial-audit.json').write_text(json.dumps(items,indent=2)+'\n');enc_s+=es;dec_s+=ds
  per=[8*v['compressed_bytes']/v['n_events'] for v in items];scored=dict(score=float(np.mean(per)),metric='mean_encoded_bits_per_event_50us',direction='lower',per_unit=per,n_recordings=7,n_source_animals=1,n_events=sum(v['n_events'] for v in items),max_timing_error_seconds=max(v['max_timing_error_seconds'] for v in items),encode_seconds=enc_s,decode_seconds=dec_s)
  pred=R/f'results/predictions/{task}/batch-v11--{model}.json';pred.parent.mkdir(parents=True,exist_ok=True);pred.write_text(json.dumps(items,indent=2)+'\n');elapsed=enc_s+dec_s;n_units=7
 else:
  x,y,xt,truth=a.load();groups=None
  if spec['train_groups_supplied']:
   with np.load(R/f'data/cache/{task}/data.npz') as z:
    groups=z['train_groups'].copy()
    if task=='K05':groups=dict(group_ids=groups,block_ids=z['train_blocks'].copy())
    if task=='K06':groups=dict(group_ids=groups,cv_fold=z['train_cv_fold'].copy())
  np.random.seed(0);start=time.perf_counter();output=ns['fit_predict'](x.copy(),y.copy(),xt.copy(),groups) if general else (mod(task).mean_reference(x.copy(),y.copy(),xt.copy()) if model=='mean-baseline' else a.baseline(x.copy(),y.copy(),xt.copy()));elapsed=time.perf_counter()-start
  output=np.asarray(output);scored=a.score(output,truth,xt);pred=R/f'results/predictions/{task}/{slice_id}--{model}.npz';pred.parent.mkdir(parents=True,exist_ok=True);np.savez_compressed(pred,predictions=output);n_units=len(truth)
 return dict(benchmark_id=task,slice_id=slice_id,run_id='batch-v11',model=model,status='measured',date='2026-10-31',track='T3' if general else 'reference',reference_type='local_specialist_reproduction' if model=='spikepack' or task=='C06' and not general else 'local_reproduction',n_units=n_units,seconds=elapsed,prediction_file=str(pred.relative_to(R)),prediction_sha256=sha(pred),prompt_sha256=spec['prompt_sha256'],truth_type='recorded_timestamps_with_fixed_lossy_tolerance_and_exact_unit_labels' if task=='B08' else meta.get('truth_type','original experimental targets'),baseline_name=meta.get('baseline_name',meta.get('reference')) if not general else None,superiority_eligible=False,superiority_reason='Bounded custom source/split,one code generation,unequal total reference effort,current global best unverified',**info,**scored)
def evaluate(task):
 check(task);path=R/f'results/{task}.json';rows=json.loads(path.read_text()) if path.exists() else []
 refs=['spikepack','task-baseline'] if task=='B08' else ['task-baseline','mean-baseline'] if task=='E06' else ['task-baseline']
 env=dict(os.environ,OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',VECLIB_MAXIMUM_THREADS='1',MKL_NUM_THREADS='1')
 for sid in (['batch-v11','taxis'] if task=='E06' else ['batch-v11']):
  for model in MODELS+refs:
   assert not any(r['model']==model and r['slice_id']==sid for r in rows),'Do not overwrite prior attempts'
   log=R/f'results/execution/{task}-{sid}-{model}.txt'
   try:
    out=subprocess.run([sys.executable,str(Path(__file__).resolve()),'one',task,model,'--slice',sid],capture_output=True,text=True,env=env,timeout=180);log.write_text(out.stdout+'\n'+out.stderr)
    if out.returncode:raise RuntimeError(out.stderr[-2400:])
    row=json.loads(out.stdout.strip().splitlines()[-1])
   except Exception as ex:row=dict(benchmark_id=task,slice_id=sid,model=model,status='failed',date='2026-10-31',reason=str(ex))
   rows.append(row);path.write_text(json.dumps(rows,indent=2)+'\n');print(task,sid,model,row['status'],row.get('score'),flush=True)
if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('action',choices=['freeze','generate','evaluate','one']);parser.add_argument('task');parser.add_argument('model',nargs='?');parser.add_argument('--slice',default='batch-v11');args=parser.parse_args()
 if args.action=='freeze':freeze(args.task)
 elif args.action=='generate':check(args.task);generate(args.task)
 elif args.action=='evaluate':evaluate(args.task)
 else:print(json.dumps(one(args.task,args.model,args.slice)))
