"""Refit unchanged frozen E01 programs on additional official NLB source slices."""
from pathlib import Path
import importlib.util,json,hashlib,subprocess,sys,os,time
import numpy as np
from expansion import ROOT as R,MODELS,validate_code,sha
D=R/'experiments/E01'
def load_adapter(name):
 p=D/f'slices/{name}/adapter.py';s=importlib.util.spec_from_file_location('slice_'+name,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m

def freeze(name):
 d=D/'slices'/name;seal=json.loads((d/'preparation-seal.json').read_text());spec=dict(benchmark_id='E01',slice_id=name,date='2026-10-30',status='frozen before any model-program execution on this source',track='T3-frozen-program-transfer',no_new_generation=True,base_prompt_sha256=sha(D/'prompt.txt'),adapter_sha256=sha(d/'adapter.py'),base_adapter_sha256=sha(D/'adapter.py'),data_sha256=sha(R/f'data/cache/E01-{name}/data.npz'),source_seal_sha256=sha(d/'preparation-seal.json'),model_code_sha256={m:hashlib.sha256(json.loads((D/(m+'.json')).read_text())['code'].encode()).hexdigest() for m in MODELS},timeout_seconds=180,one_numerical_thread=True)
 assert spec['data_sha256']==seal['prepared_npz_sha256'] and spec['base_adapter_sha256']==seal['base_adapter_sha256'];(d/'run-spec.json').write_text(json.dumps(spec,indent=2));print(name,'frozen transfer')
def one(name,model):
 d=D/'slices'/name;spec=json.loads((d/'run-spec.json').read_text());assert sha(d/'adapter.py')==spec['adapter_sha256'] and sha(D/'adapter.py')==spec['base_adapter_sha256'];assert sha(R/f'data/cache/E01-{name}/data.npz')==spec['data_sha256'];a=load_adapter(name);x,y,xt,truth=a.load();info={}
 if model in MODELS:
  o=json.loads((D/(model+'.json')).read_text());code=o['code'];assert hashlib.sha256(code.encode()).hexdigest()==spec['model_code_sha256'][model];validate_code(code);ns={};exec(compile(code,model,'exec'),ns);f=ns['fit_predict'];info=dict(code_sha256=spec['model_code_sha256'][model],code_lines=len(code.splitlines()),line_limit_compliant=len(code.splitlines())<240,description=o['description'])
 else:f=a.baseline
 start=time.perf_counter();pred=np.asarray(f(x.copy(),y.copy(),xt.copy()));seconds=time.perf_counter()-start;assert pred.shape==truth.shape and np.isfinite(pred).all() and (pred>=0).all();score=a.score(pred,truth);dest=R/f'results/predictions/E01/{name}--{model}.npz';np.savez_compressed(dest,predictions=pred)
 return dict(benchmark_id='E01',slice_id=name,model=model,status='measured',date='2026-10-30',track='T3-frozen-program-transfer' if model in MODELS else 'reference',reference_type='local_reproduction',score=score,metric='bits_per_spike',direction='higher',n_units=len(truth),seconds=seconds,generation_replicates=1 if model in MODELS else None,no_new_generation=True,base_prompt_sha256=spec['base_prompt_sha256'],prediction_file=str(dest.relative_to(R)),prediction_sha256=sha(dest),input_sha256={f'data/cache/E01-{name}/data.npz':spec['data_sha256']},adapter_file=str((d/'adapter.py').relative_to(R)),source_protocol=str((d/'protocol.md').relative_to(R)),n_scored_count_coordinates=int(np.isfinite(truth).sum()),scoring_mask='Exact official archived target NaN mask; hidden set-time jitter for DMFC; no shifting/filling',superiority_eligible=False,superiority_reason='Transparent Gaussian+Ridge reference; strong current specialist unverified',**info)
def evaluate(name):
 p=R/'results/E01.json';rows=[r for r in json.loads(p.read_text()) if r['slice_id']!=name];env=dict(os.environ,OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',VECLIB_MAXIMUM_THREADS='1',MKL_NUM_THREADS='1')
 for model in MODELS+['task-baseline']:
  log=R/f'results/execution/E01-{name}-{model}.txt'
  try:
   v=subprocess.run([sys.executable,str(Path(__file__).resolve()),'one',name,model],capture_output=True,text=True,timeout=180,env=env);log.write_text(v.stdout+'\n'+v.stderr)
   if v.returncode:raise RuntimeError(v.stderr[-1800:])
   r=json.loads(v.stdout.strip().splitlines()[-1])
  except Exception as e:r=dict(benchmark_id='E01',slice_id=name,model=model,status='failed',date='2026-10-30',reason=str(e),no_new_generation=True)
  rows.append(r);p.write_text(json.dumps(rows,indent=2));print('E01',name,model,r['status'],r.get('score'),flush=True)
if __name__=='__main__':
 if sys.argv[1]=='freeze':freeze(sys.argv[2])
 elif sys.argv[1]=='evaluate':evaluate(sys.argv[2])
 else:print(json.dumps(one(sys.argv[2],sys.argv[3])))
