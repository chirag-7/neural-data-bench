"""Frozen L06 posterior interface: generation, sampling and scoring are separate."""
from pathlib import Path
import hashlib,importlib.util,json,os,subprocess,sys,time
import numpy as np
from expansion import ROOT as R,MODELS,validate_code
D=R/'experiments/L06';C=R/'data/cache/L06'

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def module(name):
    s=importlib.util.spec_from_file_location('l06_'+name,D/(name+'.py'));m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m

def check():
    spec=json.loads((D/'run-spec.json').read_text())
    for path,h in spec['frozen_files'].items():assert sha(R/path)==h,path
    return spec

def freeze():
    assert not any(D.glob('gpt-*.json')) and not (R/'results/L06.json').exists()
    prompt='''Single-shot neuroscience posterior-sampling code-construction experiment. Do not call tools, browse, read files or execute during generation. Return only JSON with description and code.

Implement sample_posterior(design_matrix,spike_trains,prior_precision,n_samples,seed).

For each of ten observations, sample the posterior of a ten-parameter Bernoulli spiking-neuron GLM. design_matrix X is float64(100,10): intercept then nine causal stimulus lags. spike_trains is float64(10,100), binary observed spikes. Different rows are DIFFERENT parameter vectors/posteriors, not repeated sequences from one vector. Q=prior_precision is float64(10,10), symmetric positive definite. Prior mean zero. The known unnormalized log posterior for observation y is:
sum(y*(X@beta)-logaddexp(0,X@beta)) - 0.5*beta.T@Q@beta.
The stimulus is common to all observations. It comes from standard Gaussian values; lags are causal with zero padding. Prior penalizes roughness of nine filter coefficients; offset precision0.5. Do not impose a diagonal/independent prior. Use the supplied Q.

Return finite posterior draws shape(10,n_samples,10), n_samples=10000, seed=20261031. Each observation needs its OWN posterior. You receive no posterior reference samples, true parameters, training corpus or validation scores. Likelihood/gradient calculations are allowed without a simulation-call limit. This is a custom likelihood-informed inference track, not black-box SBI. Represent posterior uncertainty and joint dependence, not just point estimates.

Primary evaluation: mean classifier two-sample-test accuracy against original reference posteriors across ten observations, lower/near0.5 better. Scorer uses 2000 evenly spaced draws per distribution, 5-fold shuffled MLP classification. Finite scores near chance are noisy. Secondary prior-whitened sliced Wasserstein2 on all10000draws. Scorer data/outputs are not available to your procedure.

Allowed imports numpy,scipy,sklearn,math,collections,functools,itertools,statistics,gc. No file/network/subprocess access, dynamic exec/eval, pretrained assets or specialist packages (no PyMC,Stan,Pyro,polyagamma). All helper functions self-contained. One submission, no execution feedback. Entire call across ALL TEN observations must finish in180seconds on one numerical CPUthread. Approximately4GB memory requested but not enforced. Keep code below240lines including blanks. Deterministic use of seed required. The runtime has numpy2.3.5,scipy1.18.1,scikit-learn1.9.1. Return complete Python code and concise description including uncertainty/sampling and tuning/burn-in choices. Do not claim a score.
'''
    (D/'prompt.txt').write_text(prompt)
    (D/'response_schema.json').write_text(json.dumps(dict(type='object',properties=dict(description=dict(type='string'),code=dict(type='string')),required=['description','code'],additionalProperties=False)))
    files=[D/n for n in ['adapter.py','protocol.md','specialist.py','laplace.py','scorer.py','prompt.txt','response_schema.json']]+[Path(__file__).resolve(),C/'data.npz',C/'metadata.json',R/'data/manifests/L06.json']
    spec=dict(benchmark_id='L06',run_id='posterior-v1',date='2026-10-31',track='T3',models=MODELS,
              reasoning_effort='high',generation_replicates=1,timeout_seconds=180,line_limit_exclusive=240,
              memory_enforced=False,adapter_sha256=sha(D/'adapter.py'),data_sha256=sha(C/'data.npz'),prompt_sha256=sha(D/'prompt.txt'),
              frozen_files={str(p.relative_to(R)):sha(p) for p in files},
              status='frozen before any model generation or method score',reference_samples_not_in_prompt=True)
    (D/'run-spec.json').write_text(json.dumps(spec,indent=2)+'\n');print('L06 frozen',flush=True)

def sample(model):
    spec=check();X,Y,Q=module('adapter').inputs();info={}
    if model in MODELS:
        obj=json.loads((D/(model+'.json')).read_text());code=obj['code'];validate_code(code)
        ns={};exec(compile(code,model,'exec'),ns);f=ns['sample_posterior'];(D/(model+'.py')).write_text(code)
        info=dict(description=obj['description'],code_sha256=hashlib.sha256(code.encode()).hexdigest(),code_lines=len(code.splitlines()),line_limit_compliant=len(code.splitlines())<240)
    else:
        name={'polya-gamma':'specialist','laplace':'laplace'}[model];f=module(name).sample_posterior
        info=dict(code_sha256=sha(D/(name+'.py')),selection='Fixed before generation and any evaluated method score')
    t=time.perf_counter();pred=module('scorer').validate(f(X.copy(),Y.copy(),Q.copy(),10000,20261031));elapsed=time.perf_counter()-t
    p=R/f'results/predictions/L06/posterior-v1--{model}.npz';p.parent.mkdir(parents=True,exist_ok=True);np.savez_compressed(p,predictions=pred)
    out=dict(benchmark_id='L06',slice_id='posterior-v1',model=model,status='sampled',date='2026-10-31',track='T3' if model in MODELS else 'reference',
             n_units=10,n_posterior_draws_per_unit=10000,seconds=elapsed,prediction_file=str(p.relative_to(R)),prediction_sha256=sha(p),
             input_sha256={'data/cache/L06/data.npz':spec['data_sha256']},prompt_sha256=spec['prompt_sha256'],truth_type='synthetic_reference_posterior',
             reference_type='local_specialist_reproduction' if model=='polya-gamma' else 'local_reproduction',
             superiority_eligible=False,superiority_reason='Synthetic custom likelihood-informed track, one generation; no global-best/equal-research-effort claim',**info)
    pending=R/'results/posterior-pending';pending.mkdir(exist_ok=True);(pending/(model+'.json')).write_text(json.dumps(out,indent=2)+'\n')
    print(model,'sampled',elapsed,flush=True)

def evaluate():
    check();p=R/'results/L06.json';rows=json.loads(p.read_text()) if p.exists() else []
    env=dict(os.environ,OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',VECLIB_MAXIMUM_THREADS='1',MKL_NUM_THREADS='1')
    for model in MODELS+['polya-gamma','laplace']:
        assert not any(r['model']==model for r in rows),'Existing attempt must be preserved'
        log=R/f'results/execution/L06-posterior-v1-{model}.txt'
        try:
            out=subprocess.run([sys.executable,str(Path(__file__).resolve()),'sample',model],capture_output=True,text=True,env=env,timeout=180);log.write_text(out.stdout+'\n'+out.stderr)
            if out.returncode:raise RuntimeError(out.stderr[-2000:])
            row=json.loads((R/f'results/posterior-pending/{model}.json').read_text())
        except Exception as ex:row=dict(benchmark_id='L06',slice_id='posterior-v1',model=model,status='failed',date='2026-10-31',reason=str(ex))
        rows.append(row);p.write_text(json.dumps(rows,indent=2)+'\n');print('attempt',model,row['status'],flush=True)

def score_all():
    check();p=R/'results/L06.json';rows=json.loads(p.read_text());ref=module('adapter').references();_,_,Q=module('adapter').inputs();scorer=module('scorer')
    for row in rows:
        if row['status']!='sampled':continue
        pred=np.load(R/row['prediction_file'])['predictions'];audit=R/f'results/scorer-audits/L06/{row["model"]}.npz'
        t=time.perf_counter();scored=scorer.score(pred,ref,Q,audit)
        row.update(scored,status='measured',scoring_seconds=time.perf_counter()-t,scorer_audit_file=str(audit.relative_to(R)),scorer_audit_sha256=sha(audit))
        p.write_text(json.dumps(rows,indent=2,allow_nan=False)+'\n');print('completed_score',row['model'],row['score'],flush=True)

if __name__=='__main__':
    action=sys.argv[1]
    if action=='freeze':freeze()
    elif action=='sample':sample(sys.argv[2])
    elif action=='score':score_all()
    else:evaluate()
