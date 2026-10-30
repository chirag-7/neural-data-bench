"""Reproduce the fixed five-neuron pilot. See README.md for acquisition and limits."""
from pathlib import Path
import argparse, ast, hashlib, importlib.metadata, json, os, subprocess, sys, time
import numpy as np
import pandas as pd

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
DATA=ROOT/'work/spikefinder'

def score(pred,truth):
    if pred.shape!=truth.shape:raise ValueError(f'Wrong shape {pred.shape}; expected {truth.shape}')
    out=[]
    for c in range(truth.shape[1]):
        mask=np.isfinite(truth[:,c])
        x=np.asarray(pred[mask,c],float);y=truth[mask,c]
        if not np.all(np.isfinite(x)):raise ValueError('Missing prediction on a labeled sample')
        # Exact corr/downsample=4 operation in official spikefinder_eval.py.
        xb=np.convolve(x,np.ones(4),'valid')[::4]
        yb=np.convolve(y,np.ones(4),'valid')[::4]
        corr=float(np.corrcoef(xb,yb)[0,1]) if np.std(xb)>0 else 0.0
        out.append(corr)
    return dict(per_neuron=out,mean=float(np.mean(out)),median=float(np.median(out)))

def validate_code(code):
    tree=ast.parse(code)
    permitted={'numpy','scipy','sklearn','math','collections','functools','itertools','statistics','gc'}
    forbidden={'open','exec','eval','compile','__import__','input','breakpoint'}
    for n in ast.walk(tree):
        if isinstance(n,ast.Import):
            for x in n.names:
                if x.name.split('.')[0] not in permitted:raise ValueError('Disallowed import '+x.name)
        if isinstance(n,ast.ImportFrom) and (n.module or '').split('.')[0] not in permitted:
            raise ValueError('Disallowed import '+str(n.module))
        if isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id in forbidden:
            raise ValueError('Disallowed call '+n.func.id)
    return tree

def one(name):
    obj=json.loads((HERE/f'{name}.json').read_text())
    code=obj['code']
    if name!='oasis-reference':validate_code(code)
    (HERE/f'{name}.py').write_text(code)
    train=pd.read_csv(DATA/'1.train.calcium.csv').to_numpy(float)
    labels=pd.read_csv(DATA/'1.train.spikes.csv').to_numpy(float)
    test=pd.read_csv(DATA/'reference/1.test.calcium.csv').to_numpy(float)
    namespace={}
    exec(compile(code,str(HERE/f'{name}.py'),'exec'),namespace)
    np.random.seed(0)
    start=time.perf_counter()
    pred=np.asarray(namespace['fit_predict'](train.copy(),labels.copy(),test.copy()),float)
    elapsed=time.perf_counter()-start
    if pred.shape!=test.shape:raise ValueError('Wrong output shape')
    valid=np.isfinite(test)
    if not np.all(np.isfinite(pred[valid])):raise ValueError('Nonfinite outputs')
    if np.min(pred[valid]) < -1e-10:raise ValueError('Negative outputs')
    np.savez_compressed(HERE/f'{name}.predictions.npz',predictions=pred)
    truth=pd.read_csv(DATA/'reference/truth.test.spikes.csv').to_numpy(float)
    result=dict(model=name,status='measured',description=obj['description'],seconds=elapsed,code_sha256=hashlib.sha256(code.encode()).hexdigest(),**score(pred,truth))
    (HERE/f'{name}.scores.json').write_text(json.dumps(result,indent=2))
    print(json.dumps(result))

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--one');args=ap.parse_args()
    if args.one:return one(args.one)
    env=dict(os.environ,OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',MKL_NUM_THREADS='1',VECLIB_MAXIMUM_THREADS='1')
    results=[]
    for model in ['gpt-6.1-sol','gpt-6-sol','gpt-5.6-sol','oasis-reference']:
        if not (HERE/f'{model}.json').exists():
            results.append(dict(model=model,status='not_run',reason='No code submission'));continue
        start=time.perf_counter()
        try:
            run=subprocess.run([sys.executable,str(Path(__file__).resolve()),'--one',model],capture_output=True,text=True,timeout=180,env=env)
            (HERE/f'{model}.execution.txt').write_text(run.stdout+'\n'+run.stderr)
            if run.returncode:raise RuntimeError(run.stderr[-1600:])
            results.append(json.loads((HERE/f'{model}.scores.json').read_text()))
        except Exception as ex:
            results.append(dict(model=model,status='failed',seconds=time.perf_counter()-start,reason=str(ex)))
    truth=pd.read_csv(DATA/'reference/truth.test.spikes.csv').to_numpy(float)
    for name in ['deneux','speiser','friedrich','rupprecht']:
        path=DATA/f'reference/{name}.test.spikes.csv'
        if not path.exists():continue
        pred=pd.read_csv(path).to_numpy(float)
        results.append(dict(model=name+' (archived)',status='archived_predictions_rescored',**score(pred,truth)))
    test=pd.read_csv(DATA/'reference/1.test.calcium.csv').to_numpy(float)
    results.append(dict(model='Raw calcium baseline',status='measured_simple_baseline',**score(test,truth)))
    log={}
    for name in ['gpt-6.1-sol','gpt-6-sol','gpt-5.6-sol']:
        path=ROOT/f'work/pilot-models/{name}.jsonl'
        if not path.exists():continue
        events=[json.loads(x) for x in path.read_text().splitlines() if x.strip()]
        tools=[e for e in events if e.get('item',{}).get('type') not in [None,'agent_message','reasoning']]
        usage=next((e.get('usage') for e in reversed(events) if e.get('type')=='turn.completed'),None)
        code=json.loads((HERE/f'{name}.json').read_text())['code']
        log[name]=dict(usage=usage,tool_events=len(tools),events=len(events),code_lines=len(code.splitlines()),nonblank_code_lines=sum(bool(x.strip()) for x in code.splitlines()),line_limit_compliant=len(code.splitlines())<180)
    versions={n:importlib.metadata.version(n) for n in ['numpy','pandas','scipy','scikit-learn','oasis-deconv']}
    payload=dict(benchmark_id='C05',pilot_id='spikefinder-dataset1-test-v1',date='2026-10-30',metric='Pearson correlation after 40-ms binning',primary_aggregation='median across five held-out neurons',secondary_aggregation='mean across five held-out neurons',track='T3 single-shot code synthesis with external execution; no tools during generation',models_requested=['gpt-6.1-sol','gpt-6-sol','gpt-5.6-sol'],reasoning_effort='high',runs_per_model=1,train_neurons=11,test_neurons=5,sampling_hz=100,causal=False,test_labels_visible_to_models=False,prompt_sha256=hashlib.sha256((HERE/'prompt.txt').read_bytes()).hexdigest(),input_hashes={str(p.relative_to(DATA)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [DATA/'1.train.calcium.csv',DATA/'1.train.spikes.csv',DATA/'reference/1.test.calcium.csv',DATA/'reference/truth.test.spikes.csv']},versions=versions,model_provenance=log,results=results,best_comparable_reference='Highest archived dataset-1 test correlation among complete five-neuron submissions in results_30_06_17.csv; not verified current global SOTA.',limitations=['One dataset and five neurons; not a broad neuroscience score','One generated program per model; no repeated-run uncertainty','Models can fit numerical estimators on training data; this is not direct native signal inference','Public historical labels may have appeared in pretraining, although no tools or raw labels were supplied','No subject/animal IDs available in this slice; neurons are not independent animals','Specialist archive and current OASIS have different supervision/tuning budgets; compare performance, not equal-effort superiority','Offline acausal inference; no online latency claim','Model names are requested CLI IDs; provider-internal checkpoint resolution not independently observable'])
    payload['protocol_deviations']=['GPT-5.6 Sol returned 188 code lines including blanks against the requested fewer-than-180 limit. Its unmodified program is scored and flagged; strict formatting compliance is not claimed.','A shared missing cloudpickle dependency prevented initial imports; the harness environment was repaired before rerunning the unchanged model programs.','The approximate 3 GB requested memory budget was not enforced or independently measured.']
    payload['versions'].update({n:importlib.metadata.version(n) for n in ['joblib','threadpoolctl','cloudpickle','narwhals']})
    (HERE/'results.json').write_text(json.dumps(payload,indent=2))
    print(json.dumps(payload,indent=2))

if __name__=='__main__':main()
