"""Independent B08 saved-blob audit; never calls an encoder or fitted model.
Each method is decoded in a new Python subprocess with only code and blobs.
Original/prepared source arrays are loaded by the parent AFTER child decoding.
Optional artifacts/report paths must be outside frozen experiments and caches.
"""
from pathlib import Path
import argparse,ast,hashlib,importlib.util,json,os,subprocess,sys,tempfile
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
MODELS=('gpt-5.6-sol','gpt-6-sol','gpt-6.1-sol')
METHODS=MODELS+('spikepack','task-baseline')
def require(ok,message):
 if not ok:raise AssertionError(message)
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def array_sha(a):return hashlib.sha256(np.ascontiguousarray(a).tobytes()).hexdigest()
def root_path(relative):
 p=(ROOT/relative).resolve();require(p.is_relative_to(ROOT.resolve()),'Repository path escaped');return p
def writable(path):
 p=Path(path).resolve()
 require(not p.is_relative_to((ROOT/'experiments').resolve()) and not p.is_relative_to((ROOT/'data/cache').resolve()),'Refusing frozen experiment/cache output')
 return p

def child(planpath):
 # No manifest, original recording, prepared array or encoder invocation here.
 plan=json.loads(Path(planpath).read_text());model=plan['model'];program=Path(plan['program'])
 require(sha(program)==plan['program_file_sha256'],'Child program file mismatch')
 if model in MODELS:
  code=json.loads(program.read_text())['code'];allowed={'numpy','scipy','sklearn','math','collections','functools','itertools','statistics','gc','zlib','bz2','lzma','struct','json','io','base64'}
  tree=ast.parse(code)
  for node in ast.walk(tree):
   if isinstance(node,ast.Import):require(all(a.name.split('.')[0] in allowed for a in node.names),'Disallowed submitted import')
   if isinstance(node,ast.ImportFrom):require((node.module or '').split('.')[0] in allowed,'Disallowed submitted import')
   if isinstance(node,ast.Call) and isinstance(node.func,ast.Name):require(node.func.id not in {'open','eval','exec','compile','__import__','input','breakpoint'},'Disallowed submitted call')
  ns={};exec(compile(tree,'retained-generated-code','exec'),ns);decode=ns['decompress'];codehash=hashlib.sha256(code.encode()).hexdigest()
 else:
  s=importlib.util.spec_from_file_location('frozen_event_reference',program);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
  decode=lambda blob:m.decompress(blob,model);codehash=sha(program)
 require(codehash==plan['code_sha256'],'Child code digest mismatch')
 out=[]
 for i,item in enumerate(plan['blobs']):
  bp=Path(item['path']);require(sha(bp)==item['sha256'],'Child blob hash mismatch');blob=bp.read_bytes()
  result=decode(blob)
  require(isinstance(result,(tuple,list)) and len(result)==2,'Decoder did not return times,labels')
  t,y=result;require(isinstance(t,np.ndarray) and isinstance(y,np.ndarray),'Decoder outputs must be arrays')
  require(t.ndim==y.ndim==1 and t.shape==y.shape,'Decoder output shape mismatch')
  require(np.issubdtype(t.dtype,np.floating) and np.issubdtype(y.dtype,np.integer),'Decoder output dtype mismatch')
  require(np.isfinite(t).all() and np.all(np.diff(t)>=0),'Decoder times not finite/nondecreasing')
  path=Path(plan['output_dir'])/f'{i:02d}.npz';np.savez_compressed(path,times=t,labels=y)
  out.append(dict(decoded_file=str(path),decoded_file_sha256=sha(path),times_sha256=array_sha(t),labels_sha256=array_sha(y),n_events=len(t),bytes=len(blob),blob_sha256=sha(bp)))
 report=dict(model=model,pid=os.getpid(),parent_pid=os.getppid(),encoder_invoked=False,source_arrays_loaded=False,code_sha256=codehash,items=out)
 Path(plan['audit_path']).write_text(json.dumps(report,indent=2)+'\n')

def audit(artifacts,timeout,require_complete=False):
 d=ROOT/'experiments/B08';spec=json.loads((d/'run-spec.json').read_text());frozen=spec['frozen_files']
 require(spec['benchmark_id']=='B08' and spec['run_id']=='batch-v11','Unexpected frozen B08 run')
 for rel,digest in frozen.items():require(sha(root_path(rel))==digest,'Frozen seal mismatch: '+rel)
 require(sha(d/'prompt.txt')==spec['prompt_sha256'],'Prompt mismatch')
 manifest=json.loads((ROOT/'data/manifests/B08.json').read_text());sources=manifest['files'];require(len(sources)==7,'Expected seven recordings')
 rows=json.loads((ROOT/'results/B08.json').read_text());rows=[r for r in rows if r.get('slice_id')=='batch-v11']
 require(len({r['model'] for r in rows})==len(rows),'Duplicate method attempts')
 artifacts=writable(artifacts);artifacts.mkdir(parents=True,exist_ok=False)
 child_reports={};failed=[];measured={};blob_records={}
 # Decode all methods before reading any original/prepared numerical array.
 for row in rows:
  model=row['model'];require(model in METHODS,'Unexpected method')
  if row['status']!='measured':failed.append(dict(model=model,status=row['status'],reason=row.get('reason')));continue
  require(row['prompt_sha256']==spec['prompt_sha256'],'Attempt prompt mismatch')
  pp=root_path(row['prediction_file']);require(sha(pp)==row['prediction_sha256'],'Prediction audit hash mismatch')
  items=json.loads(pp.read_text());require(len(items)==7,'Incomplete saved payload set')
  folder=artifacts/model;folder.mkdir()
  program=d/(model+'.json') if model in MODELS else d/'reference.py'
  if model in MODELS:
   code=json.loads(program.read_text())['code'];codehash=hashlib.sha256(code.encode()).hexdigest()
   require((d/(model+'.py')).read_bytes()==code.encode(),'Generated JSON/program mismatch')
  else:codehash=sha(program)
  require(codehash==row['code_sha256'],'Attempt program hash mismatch')
  blobs=[]
  for i,(item,source) in enumerate(zip(items,sources)):
   require(item['recording']==source['recording'],'Saved payload recording order mismatch')
   bp=root_path(item['compressed_file']);require(sha(bp)==item['compressed_sha256'],'Payload digest mismatch')
   require(bp.stat().st_size==item['compressed_bytes'],'Payload byte count mismatch')
   blobs.append(dict(path=str(bp),sha256=item['compressed_sha256']))
  plan=dict(model=model,program=str(program),program_file_sha256=sha(program),code_sha256=codehash,blobs=blobs,output_dir=str(folder),audit_path=str(folder/'child-audit.json'))
  planpath=folder/'decode-plan.json';planpath.write_text(json.dumps(plan,indent=2)+'\n')
  env=dict(os.environ,OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',MKL_NUM_THREADS='1',VECLIB_MAXIMUM_THREADS='1')
  try:
   run=subprocess.run([sys.executable,str(Path(__file__).resolve()),'--child-plan',str(planpath)],cwd=folder,env=env,capture_output=True,text=True,timeout=timeout)
   (folder/'child-stdout.txt').write_text(run.stdout);(folder/'child-stderr.txt').write_text(run.stderr)
   require(run.returncode==0,'Fresh decode subprocess failed; retained stderr: '+str(folder/'child-stderr.txt'))
   report=json.loads((folder/'child-audit.json').read_text());require(report['pid']!=os.getpid(),'Decoder process was not fresh')
   require(not report['encoder_invoked'] and not report['source_arrays_loaded'],'Invalid decoder isolation report')
   child_reports[model]=report;measured[model]=row;blob_records[model]=items
  except Exception as exc:
   failure=dict(model=model,status='independent_decode_failed',reason=str(exc));failed.append(failure);(folder/'verification-failure.json').write_text(json.dumps(failure,indent=2)+'\n')
 # Independent original-component reconstruction occurs only after child returns.
 gpath=ROOT/'data/manifests/G01.json'
 # Frozen B08 manifest anchors all three original component hashes and G01
 # extracted-cache hashes. Legacy G01 run-spec does not seal its manifest.
 require('data/manifests/B08.json' in frozen,'Original component anchors lack frozen B08 seal')
 gmanifest=json.loads(gpath.read_text());gindex={x['asset_id']:x for x in gmanifest['files']};originals=[];source_audit=[]
 for source in sources:
  g=gindex[source['source_asset_id']];sp=root_path(source['source_cache'])
  require(source['source_cache']==g['extracted_npz_path'],'G01 component cache identity mismatch')
  require(sha(sp)==source['source_cache_sha256']==g['extracted_npz_sha256'],'Original extracted-cache hash mismatch')
  with np.load(sp,allow_pickle=False) as z:
   components={key:z[key] for key in ['unit_ids','spike_times','spike_times_index']}
  for key,a in components.items():
   desc=g['components'][key];require(array_sha(a)==source['original_component_sha256'][key]==desc['sha256_contiguous_bytes'],'Original component hash mismatch: '+key)
   require(list(a.shape)==desc['shape'] and str(a.dtype)==desc['dtype'],'Original component shape/dtype mismatch: '+key)
  ids=components['unit_ids'];times=components['spike_times'];ends=components['spike_times_index'].astype(np.int64)
  require(ends.ndim==1 and len(ends)==len(ids) and np.all(np.diff(ends)>=0) and ends[-1]==len(times),'Invalid ragged event indices')
  labels=np.repeat(ids.astype(np.int32),np.diff(np.r_[0,ends]));order=np.argsort(times,kind='stable');times=times[order];labels=labels[order]
  require(times.dtype==np.dtype('float64') and len(times)==source['n_events'],'Original event count/dtype mismatch')
  prepared=root_path(source['path']);require(sha(prepared)==source['sha256'],'Prepared array hash mismatch');require(prepared.stat().st_size==source['bytes'],'Prepared byte count mismatch')
  with np.load(prepared,allow_pickle=False) as z:
   require(z['times'].dtype==np.dtype('float64') and z['labels'].dtype==np.dtype('int32'),'Prepared dtype mismatch')
   require(np.array_equal(z['times'],times) and np.array_equal(z['labels'],labels),'Stable-sort/unit expansion differs from originals')
  require(np.isfinite(times).all() and np.all(np.diff(times)>=0),'Original prepared timing invalid')
  originals.append((times,labels));source_audit.append(dict(recording=source['recording'],n_events=len(times),original_component_hashes_verified=True,stable_sort_reconstruction_exact=True))
 require(sum(len(t) for t,y in originals)==1052545,'Unexpected total event count')
 results=[]
 for model,report in child_reports.items():
  row=measured[model];per=[];errors=[];total_bytes=0
  require(len(report['items'])==7,'Incomplete fresh decode audit')
  for decoded,saved,(times,labels) in zip(report['items'],blob_records[model],originals):
   dp=Path(decoded['decoded_file']);require(sha(dp)==decoded['decoded_file_sha256'],'Derived child output changed')
   with np.load(dp,allow_pickle=False) as z:t=z['times'];y=z['labels']
   require(t.shape==times.shape and y.shape==labels.shape,'Fresh decoded event count mismatch')
   require(np.isfinite(t).all() and np.issubdtype(t.dtype,np.floating) and np.issubdtype(y.dtype,np.integer),'Decoded value/dtype mismatch')
   require(np.array_equal(y,labels) and np.all(np.diff(t)>=0),'Decoded labels/order or nondecreasing time mismatch')
   error=float(np.max(np.abs(t-times)));require(error<=50e-6+1e-10,'Lossy timing tolerance exceeded')
   require(array_sha(t)==decoded['times_sha256']==saved['decoded_times_sha256'],'Decoded-time hash differs from original run')
   require(array_sha(y)==decoded['labels_sha256']==saved['decoded_labels_sha256'],'Decoded-label hash differs from original run')
   require(decoded['blob_sha256']==saved['compressed_sha256'] and decoded['bytes']==saved['compressed_bytes'],'Decoded payload identity mismatch')
   require(saved['n_events']==len(times) and saved['labels_exact'] is True,'Original run fidelity/count record mismatch')
   require(np.isclose(error,saved['max_timing_error_seconds'],rtol=1e-12,atol=1e-14),'Reported timing error differs')
   per.append(8*decoded['bytes']/len(times));errors.append(error);total_bytes+=decoded['bytes']
  value=float(np.mean(per));require(row['metric']=='mean_encoded_bits_per_event_50us' and row['direction']=='lower','Unexpected primary metric')
  require(np.isclose(value,row['score'],rtol=1e-12,atol=1e-14) and np.allclose(per,row['per_unit'],rtol=1e-12,atol=1e-14),'Unweighted mean bits/event mismatch')
  require(row['n_events']==1052545 and row['n_recordings']==7,'Run event/recording total mismatch')
  require(np.isclose(max(errors),row['max_timing_error_seconds'],rtol=1e-12,atol=1e-14),'Run max timing error mismatch')
  results.append(dict(model=model,score=value,per_record_bits_per_event=per,total_encoded_bytes=total_bytes,max_timing_error_seconds=max(errors),fresh_decoder_pid=report['pid'],code_sha256=report['code_sha256'],seven_recordings_passed=True))
 missing=sorted(set(METHODS)-{r['model'] for r in rows});complete=not missing and not failed and len(results)==5
 report=dict(benchmark_id='B08',verification_status='passed' if complete else 'incomplete_or_failed_attempts_preserved',complete=complete,frozen_files_checked=len(frozen),original_sources=source_audit,measured_attempts=results,failed_attempts=failed,missing_attempts=missing,artifact_directory=str(artifacts),encoder_invoked=False,timing_contract='Intentionally lossy <=50us+1e-10s/event; exact unit labels and event order; not exact source timing',shared_source='All seven original FALCON M2 runs shared with G01; one monkey, not independent cohort')
 (artifacts/'independent-audit.json').write_text(json.dumps(report,indent=2)+'\n')
 if require_complete:require(complete,'Incomplete/failed event audit; evidence retained at '+str(artifacts))
 return report

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--child-plan',type=Path);p.add_argument('--artifacts',type=Path);p.add_argument('--output',type=Path);p.add_argument('--timeout',type=float,default=180);p.add_argument('--require-complete',action='store_true');a=p.parse_args()
 if a.child_plan:child(a.child_plan);return
 artifacts=a.artifacts or Path(tempfile.mkdtemp(prefix='B08-independent-parent-'))/'audit'
 try:report=audit(artifacts,a.timeout,a.require_complete)
 except Exception as exc:
  if artifacts.exists():
   failure=artifacts/('parent-audit-failure-'+str(os.getpid())+'.json')
   with failure.open('x') as f:json.dump(dict(status='failed',reason=str(exc),exception_type=type(exc).__name__,existing_method_results_preserved=True),f,indent=2)
  raise
 text=json.dumps(report,indent=2)+'\n'
 if a.output:
  out=writable(a.output);require(not out.exists(),'Refusing to overwrite prior verification report');out.parent.mkdir(parents=True,exist_ok=True);out.write_text(text)
 print(text,end='')
if __name__=='__main__':main()
