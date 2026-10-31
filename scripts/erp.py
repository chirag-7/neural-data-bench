"""H02 grouped ERP protocol. Frozen programs receive training-person IDs explicitly."""
from pathlib import Path
import hashlib,json,os,subprocess,sys,time
import numpy as np
from expansion import ROOT as R,MODELS,adapter,sha,validate_code
D=R/'experiments/H02';C=R/'data/cache/H02'
def freeze():
 a=adapter('H02');x,y,xt,_=a.load()
 prompt='''Single-shot neuroscience code-construction experiment. Do not call tools, browse, read files or execute during generation. Return only JSON fields description and code.\n\nImplement fit_predict(train_x,train_y,test_x,train_groups) returning one finite real TARGET score per test trial (higher means more likely target; probability calibration is not required).\nData: real Brain Invaders2012 P300 EEG calibration runs, all25people. People1–15 train,16–25 are held-out test people. train_groups gives training person IDs for subject-held-out validation; test person identifiers are not passed. No test labels.\nEach trial is16EEGchannels×128samples at128Hz,0≤t<1s after flash. Units microvolts. Prepared using common-average reference, per-recording fourth-order0.5–20Hz zero-phase Butterworth filtering, preceding26sample baseline subtraction, and removal of groundFz. Inputs contain EEG only, no stimulus marker/time/identifier predictors. train_y1target,0nontarget. Trials overlap within people; never join rows into a continuous recording. This is offline cross-person target ranking, not online game/symbol selection.\nPrimary metric: compute ROC-AUC separately for each held-out person and average people equally; scorer alone has test groups. Same target-score direction1for all people. Fit all normalization, feature transforms, covariance references, classifiers and supervised tuning using training people only. Do not fit transforms or thresholds to test inputs, infer their row/person boundaries, or use transductive adaptation. Deterministic per-epoch feature calculations allowed. Use train_groups when validating generalization.\n'''+json.dumps(dict(train_x_shape=list(x.shape),train_y_shape=list(y.shape),test_x_shape=list(xt.shape),channels=json.loads((C/'metadata.json').read_text())['channels']))+'''\nAllowed imports numpy,scipy,sklearn,math,collections,functools,itertools,statistics,gc. No file/network/subprocess access, dynamic exec/eval, pretrained assets or specialist packages. One submission and no execution feedback. Entire fit_predict call must finish in180seconds on one numerical CPUthread, approximately4GB requested memory (not enforced). Code below240lines including blanks; deterministic seeds. Return complete Python code and concise description of method and train-only validation. Do not claim a score.\n'''
 (D/'prompt.txt').write_text(prompt);(D/'response_schema.json').write_text(json.dumps(dict(type='object',properties=dict(description=dict(type='string'),code=dict(type='string')),required=['description','code'],additionalProperties=False)))
 spec=dict(benchmark_id='H02',run_id='expansion-v1',date='2026-10-30',track='T3',models=MODELS,generation_replicates=1,reasoning_effort='high',timeout_seconds=180,line_limit_exclusive=240,memory_enforced=False,prompt_sha256=sha(D/'prompt.txt'),adapter_sha256=sha(D/'adapter.py'),specialist_sha256=sha(D/'specialist.py'),data_sha256=sha(C/'data.npz'),protocol_sha256=sha(D/'protocol.md'),status='frozen before any model generation or reference score',test_targets_not_in_prompt=True)
 (D/'run-spec.json').write_text(json.dumps(spec,indent=2)+'\n');print('H02 frozen',x.shape,xt.shape)
def one(model):
 spec=json.loads((D/'run-spec.json').read_text());assert sha(D/'adapter.py')==spec['adapter_sha256'] and sha(C/'data.npz')==spec['data_sha256'];a=adapter('H02');x,y,xt,truth=a.load();g=a.train_groups();info={}
 if model=='xdawn-tslr':
  info=json.loads((D/'specialist-runtime.json').read_text());p=R/info['prediction_file'];assert sha(p)==info['prediction_sha256']
  with np.load(p) as z:pred=z['predictions']
  elapsed=info['seconds']
 else:
  if model in MODELS:
   o=json.loads((D/(model+'.json')).read_text());code=o['code'];validate_code(code);ns={};exec(compile(code,model,'exec'),ns);f=ns['fit_predict'];info=dict(description=o['description'],code_sha256=hashlib.sha256(code.encode()).hexdigest(),code_lines=len(code.splitlines()),line_limit_compliant=len(code.splitlines())<240);(D/(model+'.py')).write_text(code)
  else:f=a.baseline
  np.random.seed(0);t=time.perf_counter();pred=np.asarray(f(x.copy(),y.copy(),xt.copy(),g.copy()));elapsed=time.perf_counter()-t
 scored=a.score(pred,truth);p=R/f'results/predictions/H02/expansion-v1--{model}.npz';p.parent.mkdir(parents=True,exist_ok=True)
 if model!='xdawn-tslr':np.savez_compressed(p,predictions=pred)
 return dict(benchmark_id='H02',slice_id='expansion-v1',model=model,status='measured',date='2026-10-30',track='T3' if model in MODELS else 'reference',reference_type='local_specialist_reproduction' if model=='xdawn-tslr' else 'local_reproduction',n_units=10,n_test_trials=len(truth),seconds=elapsed,prediction_file=str(p.relative_to(R)),prediction_sha256=sha(p),input_sha256={'data/cache/H02/data.npz':spec['data_sha256']},prompt_sha256=spec['prompt_sha256'],superiority_eligible=False,superiority_reason='Custom one-dataset split, one generation; fixed specialist configuration does not certify current strongest method or matched total effort',**{k:v for k,v in info.items() if k not in ['seconds','model','prediction_file','prediction_sha256']},**scored)
def evaluate():
 rows=[];env=dict(os.environ,OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',VECLIB_MAXIMUM_THREADS='1',MKL_NUM_THREADS='1')
 for model in MODELS+['task-baseline','xdawn-tslr']:
  log=R/f'results/execution/H02-expansion-v1-{model}.txt'
  try:
   p=subprocess.run([sys.executable,str(Path(__file__).resolve()),'one',model],env=env,capture_output=True,text=True,timeout=180);log.write_text(p.stdout+'\n'+p.stderr)
   if p.returncode:raise RuntimeError(p.stderr[-1800:])
   r=json.loads(p.stdout.strip().splitlines()[-1])
  except Exception as ex:r=dict(benchmark_id='H02',slice_id='expansion-v1',model=model,status='failed',date='2026-10-30',reason=str(ex))
  rows.append(r);(R/'results/H02.json').write_text(json.dumps(rows,indent=2)+'\n');print('H02',model,r['status'],r.get('score'),flush=True)
if __name__=='__main__':
 if sys.argv[1]=='freeze':freeze()
 elif sys.argv[1]=='evaluate':evaluate()
 else:print(json.dumps(one(sys.argv[2])))
