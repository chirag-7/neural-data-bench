"""B01 unsupervised sorting track. Inputs and hidden truth are stored separately."""
from pathlib import Path
import json,hashlib,subprocess,sys,os,time
import numpy as np
from expansion import ROOT as R,MODELS,adapter,generate,sha,validate_code
D=R/'experiments/B01';C=R/'data/cache/B01'
def freeze():
 meta=json.loads((C/'metadata.json').read_text());prompt='''Single-shot neuroscience algorithm-code benchmark. Do not call tools, browse, read files or execute during generation. Return JSON description and code only.\nImplement sort(recording_uv,fs,channel_positions_um) returning an integer NumPy array(n_events,2) of[sample_index, arbitrary nonnegative unit_id]. No supervision is supplied.\n\n'''+meta['task_description']+'''\nScoring: official SpikeInterface one-to-one Hungarian ground-truth unit matching with0.4ms nominal event tolerance (12samples at32kHz). Primary mean GT-unit accuracy=TP/(TP+FN+FP), averaged over hidden true units; extra/redundant output-unit counts reported. Do not manufacture units using hidden true counts. Empty valid output scores0. Whole-recording unsupervised adaptation and acausal snippets allowed.\nAllowed imports numpy,scipy,sklearn,math,collections,functools,itertools,statistics,gc. No file/network/subprocess access, dynamic exec/eval, specialist packages, external assets, source file or truth. One submission/no feedback. Finish entire call in180seconds on one numerical CPUthread, approximately4GB unmeasured working memory. Keep code below240lines includingblanks. Use deterministic seeds; finite integer eventindices andnonnegativeIDs, no duplicate eventwithinunit. Return JSON description(method/validation policy) and code(complete sortandhelpers). Do not claim a score.\n'''
 (D/'prompt.txt').write_text(prompt);(D/'response_schema.json').write_text(json.dumps(dict(type='object',properties=dict(description=dict(type='string'),code=dict(type='string')),required=['description','code'],additionalProperties=False)));spec=dict(benchmark_id='B01',run_id='sorting-v1',date='2026-10-30',track='T3-unsupervised',models=MODELS,generation_replicates=1,reasoning_effort='high',prompt_sha256=sha(D/'prompt.txt'),adapter_sha256=sha(D/'adapter.py'),inputs_sha256=sha(C/'inputs.npz'),truth_sha256=sha(C/'truth.npz'),status='frozen before model generation',timeout_seconds=180,line_limit_exclusive=240,memory_enforced=False);(D/'run-spec.json').write_text(json.dumps(spec,indent=2));print('B01 frozen blind sorting protocol')
def one(model):
 spec=json.loads((D/'run-spec.json').read_text());assert sha(D/'adapter.py')==spec['adapter_sha256'] and sha(C/'inputs.npz')==spec['inputs_sha256'];a=adapter('B01');x,fs,pos=a.load();info={}
 if model in MODELS:
  o=json.loads((D/(model+'.json')).read_text());code=o['code'];validate_code(code);ns={};exec(compile(code,model,'exec'),ns);f=ns['sort'];info=dict(description=o['description'],code_sha256=hashlib.sha256(code.encode()).hexdigest(),code_lines=len(code.splitlines()),line_limit_compliant=len(code.splitlines())<240);(D/(model+'.py')).write_text(code);start=time.perf_counter();pred=a.validate_events(f(x,fs,pos));seconds=time.perf_counter()-start
 else:
  with np.load(C/'specialist-events.npz') as z:pred=z[z.files[0]]
  original=json.loads((C/'specialist-reference.json').read_text());seconds=original.get('seconds',original.get('runtime_seconds'));info=dict(source_specialist_record=original)
 assert sha(C/'truth.npz')==spec['truth_sha256'];sc=a.score(pred);p=R/f'results/predictions/B01/sorting-v1--{model}.npz';p.parent.mkdir(exist_ok=True,parents=True);np.savez_compressed(p,predictions=pred)
 return dict(benchmark_id='B01',slice_id='sorting-v1',model=model,status='measured',date='2026-10-30',track='T3-unsupervised' if model in MODELS else 'reference',reference_type='local_specialist_reproduction' if model not in MODELS else None,specialist_name='MountainSort5 0.5.9 scheme1' if model not in MODELS else None,score=sc['mean_gt_accuracy'],metric='mean_gt_accuracy',direction='higher',n_units=sc['n_gt_units'],seconds=seconds,per_unit=list(sc['per_gt_unit_accuracy'].values()),prediction_file=str(p.relative_to(R)),prediction_sha256=sha(p),input_sha256={'data/cache/B01/inputs.npz':spec['inputs_sha256'],'data/cache/B01/truth.npz':spec['truth_sha256']},scoring_diagnostics=sc,superiority_eligible=False,superiority_reason='One short standard simulation; current best and equivalent total effort unverified',**info)
def evaluate():
 records=[];env=dict(os.environ,OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',VECLIB_MAXIMUM_THREADS='1',MKL_NUM_THREADS='1')
 for model in MODELS+['mountainsort5']:
  log=R/f'results/execution/B01-sorting-v1-{model}.txt'
  try:
   p=subprocess.run([sys.executable,str(Path(__file__).resolve()),'one',model],env=env,capture_output=True,text=True,timeout=180);log.write_text(p.stdout+'\n'+p.stderr)
   if p.returncode:raise RuntimeError(p.stderr[-1800:])
   r=json.loads(p.stdout.strip().splitlines()[-1])
  except Exception as e:r=dict(benchmark_id='B01',slice_id='sorting-v1',model=model,status='failed',reason=str(e),date='2026-10-30')
  records.append(r);(R/'results/B01.json').write_text(json.dumps(records,indent=2));print('B01',model,r['status'],r.get('score'),flush=True)
if __name__=='__main__':
 if sys.argv[1]=='freeze':freeze()
 elif sys.argv[1]=='generate':generate('B01')
 elif sys.argv[1]=='evaluate':evaluate()
 else:print(json.dumps(one(sys.argv[2])))
