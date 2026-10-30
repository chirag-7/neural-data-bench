"""Frozen single-shot T3 submissions for pluggable task adapters. Trusted local research code only."""
from pathlib import Path
import argparse,ast,hashlib,importlib.util,json,os,subprocess,sys,time
import numpy as np
from sklearn.metrics import balanced_accuracy_score,f1_score,accuracy_score,mean_squared_error
ROOT=Path(__file__).resolve().parents[1];WORK=ROOT.parents[1]/'work'
MODELS=['gpt-5.6-sol','gpt-6-sol','gpt-6.1-sol']
BRIEFS={
'K01':'''Predict independent expert morphology labels from 11 electrophysiological cell features, mouse Allen Cell Types. Rows are distinct cells; train/test donors are disjoint. Labels 0/1 and exact mapping/features are in the context below. Features may contain NaNs. No morphology, genetic, anatomical or identifier predictors are included. Return integer class labels of shape (n_test,). Primary macro-F1 (higher is better); balanced accuracy secondary. Fit preprocessing on training only; use deterministic seeds. It is a donor-held-out processed-feature task, not raw trace classification.''',
'H01':'''Decode left-vs-right imagined hand movement from real EEG. train_x/test_x shape (trials,64 channels,480 samples),160Hz,3-second epochs from 1 to4 seconds after cue. Training subjects1–5 and held-out test subjects6–8 are disjoint. Inputs microvolts, 64 EEG channels in PhysioNet order. Each trial is independent; do not join adjacent trials into continuous signals. train_y=0 left imagined fist,1 right imagined fist. Return integer predictions shape(n_test,). Primary balanced accuracy. General signal processing and spatial/statistical features may be implemented using NumPy/SciPy/sklearn; no specialist library. This is processed epoch decoding, no test calibration labels.''',
'I10':'''Predict whether an MRI structural scan is acceptable from precomputed MRIQC image quality metrics. Each row is a distinct participant scan. Train ABIDE, test independent DS030 cohort. Target0=exclude (rater_1=-1),1=include (doubtful0 oraccept1), following the original binary classifier convention. No identifiers, site, rater or label fields are input features. Features are numeric image-quality measurements only and may contain NaNs. Return integer labels shape(n_test,). Primary balanced accuracy. Do not fit to test labels; unsupervised per-feature input statistics allowed only if disclosed. Prefer train-only imputation/scaling. This is IQM classification, not raw-image QC.''',
'A09':'''Classify mouse social behavior from pose. Inputs shape(frames,7 temporal offsets,28 coordinates), offsets[-15,-5,-1,0,1,5,15] frames relative to target frame. There are two animals×7 keypoints×xy=28 pixel coordinates, original CalMS21 flattening order (mouse, coordinate x/y, landmark); seven landmarks are nose,left ear,right ear,neck,left hip,right hip,tail base. Context windows were built independently within each recording and labels use distinct official train/test recordings. Labels0attack,1investigation,2mount,3other. Return integer label per target frame. Each example already has context; do not smooth or create windows across examples (recordings are concatenated without IDs). Primary macro-F1. Temporal features, distances and conventional classifiers may be built with general libraries. Repeated frames/animals within recordings are correlated; no independent-animal claim.''',
'A14':'''Impute an interior missing landmark gap in measured rat motion-capture trajectories. Input shape(Nwindows,31 timeframes,18 coordinate features): six 3D landmarks in Rat7M order HeadF,HeadB,HeadL,SpineF,SpineM,SpineL (x,y,z each). One HeadF 7-frame gap is replaced with NaNs in each example, while other coordinates and timepoints are observed. train_y contains complete observed trajectories for training windows. Train animals1–3 and test animals4–5; windows independent and do not join them. Return full array of test_x.shape, with finite predictions at missing positions. Primary RMSE only at artificially missing positions with finite measured truth (lower better), in native mocap coordinate units (physical calibration unverified). Do not claim raw image pose capability. Offline/acausal interpolation allowed.''',
'H16':'''Repair ocular artifacts in EEG segments. Input rows are noisy EEG segments, train_y is matching clean EEG segments, test_x are noisy held-out segments. Data consist of semisynthetic clean+EOG mixtures from EEGdenoiseNet; neither clean nor artifact source segment crosses train/test. Return denoised array of test_x.shape. This is offline semisynthetic repair, not pristine in-vivo ground truth. Sampling and normalization context below must be respected. Primary relative RMSE = average per-segment norm(pred-clean)/norm(clean), lower better. General scipy signal processing, regression or learned estimators allowed; no external weights or specialist packages.'''
}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def adapter(task):
 p=ROOT/f'experiments/{task}/adapter.py';s=importlib.util.spec_from_file_location('adapter_'+task,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m

def metadata(task):
 candidates=[ROOT/f'experiments/{task}/metadata.json',ROOT/f'data/cache/{task}/metadata.json']
 return json.loads(next(p for p in candidates if p.exists()).read_text())

def freeze(task):
 m=adapter(task);x,y,xt,yt=m.load();d=ROOT/f'experiments/{task}';meta=metadata(task)
 # Explicitly whitelist descriptive context, excluding test targets, frequencies and groups.
 context={k:meta[k] for k in ['feature_names','label_encoding','sampling_hz','sampling_rate','sampling_rate_hz','units','input','input_description','input_details','normalization','channels','keypoint_names','classes','feature_description','input_units','landmarks','sample_rate_hz'] if k in meta}
 prompt='''You are participating in a single-shot neuroscience code-synthesis experiment. Do not call tools, browse, read files or execute code. Return only JSON with description and code.\n\nImplement Python fit_predict(train_x,train_y,test_x) returning predictions with the specified shape. No test target labels are supplied.\n\n'''+BRIEFS[task]+'\n\nPrepared input context: '+json.dumps(dict(train_x_shape=list(x.shape),train_y_shape=list(y.shape),test_x_shape=list(xt.shape),**context))+'\n\nAllowed imports: numpy, scipy, sklearn, math, collections, functools, itertools, statistics, gc. No file/network/subprocess access, dynamic exec/eval, pretrained assets or specialist neuroscience packages. Use deterministic seeds. One submission, no execution feedback. The entire fit_predict call must finish in180 seconds on one numerical CPU thread, approximately4GB working memory (memory request is not enforced). Keep code below240 lines including blanks. Return JSON fields description (method and training/validation policy), code (complete self-contained Python source with fit_predict and helpers). Do not claim a score.\n'
 (d/'prompt.txt').write_text(prompt);(d/'response_schema.json').write_text(json.dumps(dict(type='object',properties=dict(description=dict(type='string'),code=dict(type='string')),required=['description','code'],additionalProperties=False)))
 spec=dict(benchmark_id=task,run_id='expansion-v1',date='2026-10-30',track='T3',models=MODELS,reasoning_effort='high',generation_replicates=1,timeout_seconds=180,line_limit_exclusive=240,memory_enforced=False,prompt_sha256=sha(d/'prompt.txt'),adapter_sha256=sha(d/'adapter.py'),data_sha256=sha(ROOT/f'data/cache/{task}/data.npz'),status='frozen before model generation',test_targets_not_in_prompt=True)
 (d/'run-spec.json').write_text(json.dumps(spec,indent=2));print(task,'frozen',x.shape,y.shape,xt.shape,yt.shape)

def generate(task):
 cli='/Applications/ChatGPT.app/Contents/Resources/codex-cli/CodexCLI.app/Contents/MacOS/codex';d=ROOT/f'experiments/{task}';jobs=[]
 for model in MODELS:
  out=d/(model+'.json');log=WORK/'expansion-models'/f'{task}-{model}.jsonl';cwd=WORK/'expansion-contexts'/task/model;cwd.mkdir(parents=True,exist_ok=True)
  if out.exists():print(task,model,'existing submission preserved',flush=True);continue
  command=[cli,'exec','--ephemeral','--ignore-user-config','--skip-git-repo-check','--sandbox','read-only','--model',model,'-c','model_reasoning_effort=high','--output-schema',str(d/'response_schema.json'),'--output-last-message',str(out),'--json','-']
  with (d/'prompt.txt').open('r') as inp, log.open('w') as stream:
   jobs.append((model,subprocess.Popen(command,stdin=inp,stdout=stream,stderr=subprocess.PIPE,text=True,cwd=cwd)))
 for model,p in jobs:
  _,err=p.communicate(timeout=600);print(task,model,'generation_exit',p.returncode,flush=True)
  (WORK/'expansion-models'/f'{task}-{model}.infrastructure.txt').write_text(err or '')

def validate_code(code):
 allowed={'numpy','scipy','sklearn','math','collections','functools','itertools','statistics','gc'}
 for n in ast.walk(ast.parse(code)):
  if isinstance(n,ast.Import) and any(x.name.split('.')[0] not in allowed for x in n.names):raise ValueError('Disallowed import')
  if isinstance(n,ast.ImportFrom) and (n.module or '').split('.')[0] not in allowed:raise ValueError('Disallowed import')
  if isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id in {'open','exec','eval','compile','__import__','input','breakpoint'}:raise ValueError('Disallowed call')

def scoring(task,pred,truth,test_x,meta):
 metric=meta.get('primary_metric',meta.get('metric','macro_f1'));metric=metric.get('name') if isinstance(metric,dict) else metric
 if task in ['K01','A09','I10','H01']:
  pred=np.asarray(pred).reshape(-1)
  if pred.shape!=truth.shape or not np.all(np.isfinite(pred)) or not np.all(np.isin(pred,np.unique(truth))):raise ValueError('Invalid class output')
  b=float(balanced_accuracy_score(truth,pred));f=float(f1_score(truth,pred,average='macro',zero_division=0));a=float(accuracy_score(truth,pred));primary='balanced_accuracy' if task in ['H01','I10'] else 'macro_f1';return dict(score=b if primary=='balanced_accuracy' else f,metric=primary,direction='higher',balanced_accuracy=b,macro_f1=f,accuracy=a,per_unit=(pred==truth).astype(float).tolist())
 if pred.shape!=truth.shape or not np.all(np.isfinite(pred[np.isfinite(truth)])):raise ValueError('Invalid output shape/nonfinite prediction')
 if task=='A14':
  mask=np.isnan(test_x)&np.isfinite(truth);err=(pred-truth)[mask];per=np.sqrt(np.nanmean(np.where(mask,(pred-truth)**2,np.nan),axis=tuple(range(1,truth.ndim))));return dict(score=float(np.sqrt(np.mean(err**2))),metric='rmse_missing',direction='lower',mae_missing=float(np.mean(np.abs(err))),per_unit=per.tolist(),n_masked_coordinates=int(mask.sum()))
 if task=='H16':
  per=np.linalg.norm(pred-truth,axis=1)/np.maximum(np.linalg.norm(truth,axis=1),1e-12);return dict(score=float(per.mean()),metric='temporal_rrmse',direction='lower',per_unit=per.tolist(),rmse=float(np.sqrt(np.mean((pred-truth)**2))))
 if hasattr(adapter(task),'score'):return adapter(task).score(pred,truth,test_x)
 raise ValueError('No approved scorer for '+task)

def one(task,model):
 d=ROOT/f'experiments/{task}';spec=json.loads((d/'run-spec.json').read_text());assert sha(d/'adapter.py')==spec['adapter_sha256'];assert sha(ROOT/f'data/cache/{task}/data.npz')==spec['data_sha256'];m=adapter(task);x,y,xt,truth=m.load();meta=metadata(task);info={}
 if model in MODELS:
  obj=json.loads((d/(model+'.json')).read_text());code=obj['code'];validate_code(code);ns={};exec(compile(code,model,'exec'),ns);f=ns['fit_predict'];info=dict(description=obj['description'],code_sha256=hashlib.sha256(code.encode()).hexdigest(),code_lines=len(code.splitlines()),line_limit_compliant=len(code.splitlines())<240);(d/(model+'.py')).write_text(code)
 else:f=m.baseline
 np.random.seed(0);t=time.perf_counter();pred=np.asarray(f(x.copy(),y.copy(),xt.copy()));elapsed=time.perf_counter()-t
 scored=scoring(task,pred,truth,xt,meta);dest=ROOT/f'results/predictions/{task}/expansion-v1--{model}.npz';dest.parent.mkdir(parents=True,exist_ok=True);np.savez_compressed(dest,predictions=pred)
 # Per-test-unit group summaries are descriptive clusters, not automatic independent samples.
 groups=meta.get('test_groups',meta.get('groups_test'))
 grouped=[]
 if groups is not None and len(groups)==len(truth):
  groups=np.asarray(groups)
  for g in np.unique(groups):
   idx=groups==g;ss=scoring(task,pred[idx],truth[idx],xt[idx],meta);grouped.append(dict(group=str(g),score=ss['score'],n=int(idx.sum())))
 return dict(benchmark_id=task,slice_id='expansion-v1',run_id='expansion-v1',model=model,status='measured',date='2026-10-30',track='T3' if model in MODELS else 'reference',reference_type='local_reproduction',baseline_name=meta.get('baseline_name','Conventional task baseline') if model=='task-baseline' else None,superiority_eligible=False,superiority_reason='Local conventional baseline; current strongest specialist and matched total tuning effort unverified',generation_replicates=1 if model in MODELS else None,n_units=len(truth),seconds=elapsed,truth_type=meta.get('truth_type','experimental_labels'),prediction_file=str(dest.relative_to(ROOT)),prediction_sha256=sha(dest),input_sha256={f'data/cache/{task}/data.npz':spec['data_sha256']},prompt_sha256=spec['prompt_sha256'],group_results=grouped,**info,**scored)

def evaluate_task(task):
 records=[];env=dict(os.environ,OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',MKL_NUM_THREADS='1',VECLIB_MAXIMUM_THREADS='1')
 for model in MODELS+['task-baseline']:
  p=ROOT/f'results/execution/{task}-expansion-v1-{model}.txt'
  try:
   run=subprocess.run([sys.executable,str(Path(__file__).resolve()),'one',task,model],capture_output=True,text=True,env=env,timeout=180);p.write_text(run.stdout+'\n'+run.stderr)
   if run.returncode:raise RuntimeError(run.stderr[-1800:])
   record=json.loads(run.stdout.strip().splitlines()[-1])
  except Exception as ex:record=dict(benchmark_id=task,slice_id='expansion-v1',model=model,status='failed',reason=str(ex),date='2026-10-30')
  records.append(record);print(task,model,record['status'],record.get('score'),flush=True)
  (ROOT/f'results/{task}.json').write_text(json.dumps(records,indent=2))
 # Preserve actual generation usage without provider machine/context identifiers.
 provenance=[]
 for model in MODELS:
  p=WORK/'expansion-models'/f'{task}-{model}.jsonl'
  if not p.exists():continue
  events=[json.loads(s) for s in p.read_text().splitlines() if s.strip()];usage=next((e.get('usage') for e in reversed(events) if e.get('type')=='turn.completed'),None);provenance.append(dict(requested_model=model,reasoning_effort='high',generation_replicates=1,usage=usage,tool_events=sum(e.get('item',{}).get('type') not in [None,'agent_message','reasoning'] for e in events),prompt_sha256=sha(ROOT/f'experiments/{task}/prompt.txt'),effective_context='Identical explicit user prompt; provider/CLI instructions can differ.'))
 (ROOT/f'experiments/{task}/generation-provenance.json').write_text(json.dumps(provenance,indent=2))

def main():
 p=argparse.ArgumentParser();p.add_argument('action',choices=['freeze','generate','evaluate','one']);p.add_argument('task');p.add_argument('model',nargs='?');a=p.parse_args()
 if a.action=='freeze':freeze(a.task)
 elif a.action=='generate':generate(a.task)
 elif a.action=='evaluate':evaluate_task(a.task)
 else:print(json.dumps(one(a.task,a.model)))
if __name__=='__main__':main()
