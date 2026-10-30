"""Frozen, reviewed submissions only. No network. See docs/methodology.md."""
from pathlib import Path
import argparse, ast, hashlib, json, os, subprocess, sys, time
import numpy as np
import pandas as pd
from scipy.optimize import minimize
ROOT=Path(__file__).resolve().parents[1]
MODELS=['gpt-5.6-sol','gpt-6-sol','gpt-6.1-sol']
DATA=ROOT/'data/cache'
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def score(pred,truth):
    if pred.shape!=truth.shape:raise ValueError('Prediction shape mismatch')
    values=[]
    for j in range(truth.shape[1]):
        mask=np.isfinite(truth[:,j]);x=pred[mask,j];y=truth[mask,j]
        if not np.all(np.isfinite(x)):raise ValueError('Nonfinite predictions on labels')
        x=np.convolve(x,np.ones(4),'valid')[::4];y=np.convolve(y,np.ones(4),'valid')[::4]
        values.append(float(np.corrcoef(x,y)[0,1]) if np.std(x)>0 else 0.)
    return dict(per_unit=values,mean=float(np.mean(values)),score=float(np.median(values)))
def load_code(path,fn):
    obj=json.loads(path.read_text());code=obj['code'];tree=ast.parse(code)
    allowed={'numpy','scipy','sklearn','math','collections','functools','itertools','statistics','gc'}
    for n in ast.walk(tree):
        if isinstance(n,ast.Import) and any(x.name.split('.')[0] not in allowed for x in n.names):raise ValueError('Forbidden import')
        if isinstance(n,ast.ImportFrom) and (n.module or '').split('.')[0] not in allowed:raise ValueError('Forbidden import')
        if isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id in {'open','exec','eval','compile','__import__','input','breakpoint'}:raise ValueError('Forbidden call')
    ns={};exec(compile(code,str(path),'exec'),ns)
    return ns[fn],dict(description=obj['description'],code_sha256=hashlib.sha256(code.encode()).hexdigest(),code_lines=len(code.splitlines()),line_limit_compliant=len(code.splitlines())<180)
def nll(theta,choice,reward):
    theta=np.atleast_2d(theta);a=theta[:,0];b=theta[:,1];q0=np.full(len(a),.5);q1=q0.copy();loss=np.zeros(len(a))
    for c,r in zip(choice,reward):
        z=b*(q1-q0);loss+=np.logaddexp(0,z)-c*z
        if c:q1+=a*(r-q1)
        else:q0+=a*(r-q0)
    return loss
def make_cognitive():
    p=DATA/'cognitive-v1.npz'
    if p.exists():return p
    rng=np.random.default_rng(20261030);truth=np.column_stack([rng.uniform(.1,.9,24),rng.uniform(.5,8,24)])
    choices=np.zeros((24,240),int);rewards=choices.copy()
    for i,(alpha,beta) in enumerate(truth):
        q=np.array([.5,.5])
        for t in range(240):
            prob=1/(1+np.exp(-beta*(q[1]-q[0])));c=int(rng.random()<prob)
            rates=[.8,.2] if (t//60)%2==0 else [.2,.8];r=int(rng.random()<rates[c]);q[c]+=alpha*(r-q[c]);choices[i,t]=c;rewards[i,t]=r
    np.savez_compressed(p,choices=choices,rewards=rewards,truth=truth)
    return p
def mle(choices,rewards):
    grid=np.array(np.meshgrid(np.linspace(.01,.99,16),np.linspace(.1,10,24))).reshape(2,-1).T
    out=[];diagnostics=[]
    for c,r in zip(choices,rewards):
        loss=nll(grid,c,r);starts=grid[np.argsort(loss)[:4]]
        fits=[minimize(lambda x:float(nll(x,c,r)[0]),s,method='L-BFGS-B',bounds=[(.01,.99),(.1,10)],options={'ftol':1e-11}) for s in starts]
        best=min(fits,key=lambda z:z.fun);out.append(best.x);diagnostics.append(dict(success=bool(best.success),nll=float(best.fun),message=str(best.message)))
    return np.array(out),diagnostics
def one(task,slice_id,model):
    np.random.seed(0);folder=ROOT/'results/predictions'/task;folder.mkdir(parents=True,exist_ok=True)
    info={};diag=None
    if task=='C05':
        d=DATA/'spikefinder';load=lambda k:pd.read_csv(d/f'{slice_id}.{k}.csv').to_numpy(float)
        test=load('test.calcium')
        if model in MODELS:
            f,info=load_code(ROOT/f'experiments/C05/pilot-v1/{model}.json','fit_predict')
            train=load('train.calcium');labels=load('train.spikes');t=time.perf_counter();pred=np.asarray(f(train.copy(),labels.copy(),test.copy()),float);seconds=time.perf_counter()-t
        elif model=='oasis-default':
            from oasis.functions import deconvolve
            t=time.perf_counter();pred=np.full(test.shape,np.nan)
            for j in range(test.shape[1]):
                mask=np.isfinite(test[:,j]);pred[mask,j]=deconvolve(test[mask,j],penalty=1)[1]
            seconds=time.perf_counter()-t
        elif model=='raw-calcium':pred=test;seconds=None
        else:pred=pd.read_csv(d/f'{slice_id}.{model}.csv').to_numpy(float);seconds=None
        if model in MODELS and (not np.all(np.isfinite(pred[np.isfinite(test)])) or np.min(pred[np.isfinite(test)])< -1e-10):raise ValueError('Invalid output at finite inputs')
        truth=load('test.spikes');scores=score(pred,truth)
        metadata=dict(metric='median_pearson_40ms',direction='higher',n_units=truth.shape[1],truth_type='simultaneous_electrophysiology',input_sha256={str(p.relative_to(ROOT)):digest(p) for p in d.glob(f'{slice_id}.*')})
    else:
        path=make_cognitive();arrays=np.load(path);choices=arrays['choices'];rewards=arrays['rewards'];truth=arrays['truth']
        if model in MODELS:f,info=load_code(ROOT/f'experiments/M04/{model}.json','estimate')
        t=time.perf_counter()
        if model in MODELS:pred=np.asarray(f(choices.copy(),rewards.copy()),float)
        elif model=='canonical-mle':pred,diag=mle(choices,rewards)
        else:pred=np.tile([.5,5.05],(len(choices),1))
        seconds=time.perf_counter()-t
        if pred.shape!=truth.shape or not np.all(np.isfinite(pred)) or np.any(pred< [.01,.1]) or np.any(pred> [.99,10]):raise ValueError('Invalid parameter estimate')
        errors=np.mean(np.abs(pred-truth)/[.98,9.9],axis=1)
        scores=dict(per_unit=errors.tolist(),score=float(np.mean(errors)),mean=float(np.mean(errors)),per_parameter_mae=np.mean(np.abs(pred-truth),axis=0).tolist(),nll_per_trial=float(np.mean([nll(p,c,r)[0]/len(c) for p,c,r in zip(pred,choices,rewards)])),optimization_diagnostics=diag)
        metadata=dict(metric='range_normalized_mae',direction='lower',n_units=len(choices),truth_type='synthetic_known_parameters',input_sha256={str(path.relative_to(ROOT)):digest(path)})
    target=folder/f'{slice_id}--{model}.npz';np.savez_compressed(target,predictions=pred)
    return dict(benchmark_id=task,slice_id=str(slice_id),model=model,status='measured',date='2026-10-30',track='T3' if model in MODELS else 'reference',reference_type='archived_predictions_rescored' if task=='C05' and model in ['deneux','speiser','friedrich','rupprecht'] else 'local_reproduction',generation_replicates=1 if model in MODELS else None,seconds=seconds,prediction_file=str(target.relative_to(ROOT)),prediction_sha256=digest(target),**info,**metadata,**scores)
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--one',nargs=3);ap.add_argument('--task',choices=['C05','M04']);args=ap.parse_args()
    if args.one:print(json.dumps(one(*args.one)));return
    tasks=[args.task] if args.task else ['C05','M04']
    env=dict(os.environ,OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',MKL_NUM_THREADS='1',VECLIB_MAXIMUM_THREADS='1')
    for task in tasks:
        records=[]
        models=MODELS+(['deneux','speiser','friedrich','rupprecht','oasis-default','raw-calcium'] if task=='C05' else ['canonical-mle','midpoint'])
        for sid in (range(1,6) if task=='C05' else ['synthetic-v1']):
            for model in models:
                start=time.perf_counter();label=f'{task}-{sid}-{model}';p=ROOT/f'results/execution/{label}.txt';p.parent.mkdir(parents=True,exist_ok=True)
                try:
                    run=subprocess.run([sys.executable,str(Path(__file__).resolve()),'--one',task,str(sid),model],capture_output=True,text=True,timeout=180,env=env)
                    p.write_text(run.stdout+'\n'+run.stderr)
                    if run.returncode:raise RuntimeError(run.stderr[-1200:])
                    record=json.loads(run.stdout.strip().splitlines()[-1])
                except Exception as ex:record=dict(benchmark_id=task,slice_id=str(sid),model=model,status='failed',reason=str(ex),seconds=time.perf_counter()-start,date='2026-10-30')
                records.append(record);print(label,record['status'],record.get('score'),flush=True)
                (ROOT/f'results/{task}.json').write_text(json.dumps(records,indent=2))
    # Store each task independently; JSONL centralization is scripts/summarize.py.
if __name__=='__main__':main()
