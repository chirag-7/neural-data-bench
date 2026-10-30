"""N05 deterministic file-extraction track, distinct from array-learning experiments."""
from pathlib import Path
import ast,hashlib,importlib.util,json,os,subprocess,sys,time
import numpy as np
from expansion import ROOT,WORK,MODELS,generate,sha
TASK='N05';D=ROOT/'experiments/N05';CACHE=ROOT/'data/cache/N05'
def freeze():
 prompt='''Single-shot neuroscience file-analysis code evaluation. Do not call tools, browse, read files or execute code during generation. Return JSON description and code only. Implement extract(nwb_path) returning the specified JSON-serializable dictionary. At execution you may read ONLY the supplied NWB/HDF5 file with h5py. No other file, network, subprocess, external assets, reference answers, dynamic exec/eval or hardcoded measured values. Allowed imports numpy,h5py,math,json,re,collections,functools,itertools,statistics. Inspect file structure programmatically; do not assume modern NWB2. One submission, no feedback;180seconds,oneCPUthread,approx4GB unmeasured,<240code lines.\n\n'''+(D/'task.json').read_text()
 (D/'prompt.txt').write_text(prompt);(D/'response_schema.json').write_text(json.dumps(dict(type='object',properties=dict(description=dict(type='string'),code=dict(type='string')),required=['description','code'],additionalProperties=False)))
 spec=dict(benchmark_id=TASK,date='2026-10-30',track='T3-file-analysis',models=MODELS,prompt_sha256=sha(D/'prompt.txt'),fixture_sha256=sha(CACHE/'fixture.nwb'),reference_sha256=sha(D/'reference.py'),expected_sha256=sha(CACHE/'expected.json'),tolerances_sha256=sha(CACHE/'tolerances.json'),status='frozen before model generation',generation_replicates=1,timeout_seconds=180,line_limit_exclusive=240)
 (D/'run-spec.json').write_text(json.dumps(spec,indent=2));print('N05 frozen:61 deterministic leaves,one real sharedNWBfile')
def flatten(x,prefix=''):
 out={}
 for k,v in x.items():
  key=prefix+'/'+str(k)
  if isinstance(v,dict):out.update(flatten(v,key))
  else:out[key]=v
 return out

def score(answer):
 expected=flatten(json.loads((CACHE/'expected.json').read_text()));pred=flatten(answer) if isinstance(answer,dict) else {};tol=json.loads((CACHE/'tolerances.json').read_text());checks=[]
 for key,value in expected.items():
  v=pred.get(key);ok=False
  if isinstance(value,str):ok=isinstance(v,str) and v==value
  elif isinstance(v,(int,float)) and not isinstance(v,bool) and np.isfinite(v):
   t=tol[key.rsplit('/',1)[-1]];ok=abs(v-value)<=t['atol']+t['rtol']*abs(value)
  checks.append(dict(field=key,correct=bool(ok)))
 return dict(score=float(np.mean([r['correct'] for r in checks])),metric='field_accuracy',direction='higher',n_units=len(checks),per_unit=[int(r['correct']) for r in checks],field_results=checks,all_fields_correct=all(r['correct'] for r in checks))
def one(model):
 spec=json.loads((D/'run-spec.json').read_text());assert sha(CACHE/'fixture.nwb')==spec['fixture_sha256'];assert sha(CACHE/'expected.json')==spec['expected_sha256'];info={}
 if model in MODELS:
  obj=json.loads((D/(model+'.json')).read_text());code=obj['code'];allowed={'numpy','h5py','math','json','re','collections','functools','itertools','statistics'}
  for n in ast.walk(ast.parse(code)):
   if isinstance(n,ast.Import) and any(v.name.split('.')[0] not in allowed for v in n.names):raise ValueError('Forbidden import')
   if isinstance(n,ast.ImportFrom) and (n.module or '').split('.')[0] not in allowed:raise ValueError('Forbidden import')
   if isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id in ['open','exec','eval','compile','__import__','input']:raise ValueError('Forbidden call')
  ns={};exec(compile(code,model,'exec'),ns);f=ns['extract'];info=dict(description=obj['description'],code_sha256=hashlib.sha256(code.encode()).hexdigest(),code_lines=len(code.splitlines()),line_limit_compliant=len(code.splitlines())<240);(D/(model+'.py')).write_text(code)
 else:
  s=importlib.util.spec_from_file_location('reference',D/'reference.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m);f=m.extract
 t=time.perf_counter();answer=f(str(CACHE/'fixture.nwb'));elapsed=time.perf_counter()-t;sc=score(answer);p=ROOT/f'results/predictions/N05/expansion-v1--{model}.json';p.parent.mkdir(exist_ok=True,parents=True);p.write_text(json.dumps(answer,indent=2))
 return dict(benchmark_id=TASK,slice_id='expansion-v1',model=model,status='measured',date='2026-10-30',track='T3-file-analysis' if model in MODELS else 'reference',reference_type='deterministic_audited_calculation',superiority_eligible=False,superiority_reason='Reference correct by construction; correctness, not empirical specialist superiority',generation_replicates=1 if model in MODELS else None,seconds=elapsed,truth_type='deterministic_file_calculations',prediction_file=str(p.relative_to(ROOT)),prediction_sha256=sha(p),dataset_group='Allen-cell464212183-shared-D02',input_sha256={'data/cache/N05/fixture.nwb':spec['fixture_sha256']},**info,**sc)
def evaluate():
 records=[];env=dict(os.environ,OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',MKL_NUM_THREADS='1',VECLIB_MAXIMUM_THREADS='1')
 for model in MODELS+['task-baseline']:
  p=ROOT/f'results/execution/N05-expansion-v1-{model}.txt'
  try:
   run=subprocess.run([sys.executable,str(Path(__file__).resolve()),'one',model],capture_output=True,text=True,timeout=180,env=env);p.write_text(run.stdout+'\n'+run.stderr)
   if run.returncode:raise RuntimeError(run.stderr[-1800:])
   r=json.loads(run.stdout.strip().splitlines()[-1])
  except Exception as e:r=dict(benchmark_id=TASK,slice_id='expansion-v1',model=model,status='failed',reason=str(e),date='2026-10-30')
  records.append(r);print(model,r['status'],r.get('score'),flush=True);(ROOT/'results/N05.json').write_text(json.dumps(records,indent=2))
if __name__=='__main__':
 a=sys.argv[1]
 if a=='freeze':freeze()
 elif a=='generate':generate(TASK)
 elif a=='evaluate':evaluate()
 else:print(json.dumps(one(sys.argv[2])))
