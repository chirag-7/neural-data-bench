"""Independent source, retained C2ST decisions, Wasserstein and freeze audit.

Does not refit classifiers or rerun samplers. Original classifier fitting can be
repeated with the frozen scorer; held-out decisions make all reported accuracy
arithmetic independently checkable without a second expensive training run.
"""
from pathlib import Path
import hashlib,importlib.util,json
import numpy as np
R=Path(__file__).resolve().parents[1];D=R/'experiments/L06';C=R/'data/cache/L06'
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def verify(write=True):
    spec=json.loads((D/'run-spec.json').read_text())
    for path,digest in spec['frozen_files'].items(): assert sha(R/path)==digest,path
    manifest=json.loads((R/'data/manifests/L06.json').read_text())
    for f in manifest['files']: assert sha(R/f['path'])==f['sha256']
    with np.load(C/'data.npz') as z: X,Y,Q,ref=[z[k] for k in ['design','spikes','precision','reference']]
    stimulus=np.random.RandomState(42).normal(size=100).astype(np.float32)
    for row in range(100):
        assert X[row,0]==1
        for col in range(1,10):assert X[row,col]==(stimulus[row-col+1] if row>=col-1 else 0)
    difference=np.zeros((9,9),dtype=np.float32)
    for i in range(9):
        difference[i,i]=1
        if i>0:difference[i,i-1]=-1
    F=difference@difference
    for i in range(9):F[i,i]+=np.sqrt(np.float32(i)/np.float32(9))
    expect=np.zeros((10,10));expect[0,0]=.5;expect[1:,1:]=F.T@F
    assert np.array_equal(Q,expect) and np.linalg.eigvalsh(Q).min()>0
    for j in range(10):
        src=C/f'source/num_observation_{j+1}'
        assert np.array_equal(Y[j],np.loadtxt(src/'observation_raw.csv',delimiter=',',skiprows=1).reshape(-1))
        assert np.array_equal(ref[j],np.loadtxt(src/'reference_posterior_samples.csv.bz2',delimiter=',',skiprows=1))
        sufficient=np.loadtxt(src/'observation.csv',delimiter=',',skiprows=1).reshape(-1)
        assert np.allclose(X.T@Y[j],sufficient,rtol=1e-6,atol=3e-5)
    vals,U=np.linalg.eigh(Q);root=(U*np.sqrt(vals))@U.T
    rng=np.random.default_rng(1729);directions=rng.standard_normal((10,128));directions/=np.sqrt((directions**2).sum(axis=0))
    projection=root@directions;checks=[]
    for record in json.loads((R/'results/L06.json').read_text()):
        if record['status']!='measured':continue
        p=R/record['prediction_file'];assert sha(p)==record['prediction_sha256']
        pred=np.load(p)['predictions'];assert pred.shape==(10,10000,10) and np.isfinite(pred).all()
        a=R/record['scorer_audit_file'];assert sha(a)==record['scorer_audit_sha256']
        with np.load(a) as audit:
            guesses,labels,folds=[audit[k] for k in ['predicted_class','true_class','fold_id']]
            assert guesses.shape==(10,4000) and np.isin(guesses,[0,1]).all()
            assert np.array_equal(labels,np.r_[np.zeros(2000),np.ones(2000)])
            assert sorted(np.bincount(folds).tolist())==[800]*5
            expected_fold_ids=np.empty(4000,dtype=np.int8)
            order=np.random.RandomState(1).permutation(4000)
            for k in range(5):expected_fold_ids[order[800*k:800*(k+1)]]=k
            assert np.array_equal(folds,expected_fold_ids)
            scores=[]
            for j in range(10):
                fold_acc=np.asarray([np.mean(guesses[j,folds==k]==labels[folds==k]) for k in range(5)])
                assert np.array_equal(fold_acc,audit['fold_accuracy'][j])
                scores.append(float(np.float32(fold_acc.mean())))
            assert np.array_equal(scores,audit['per_observation_c2st'])
        assert np.array_equal(scores,record['per_unit']) and abs(np.mean(scores)-record['score'])<1e-12
        distances=[]
        for j in range(10):
            A=pred[j]@projection;B=ref[j]@projection
            per_direction=[]
            for k in range(128):
                delta=sorted(A[:,k])-np.asarray(sorted(B[:,k]));per_direction.append(np.mean(delta*delta))
            distances.append(float(np.sqrt(np.mean(per_direction))))
        assert np.allclose(distances,record['per_observation_sliced_w2'],atol=1e-12,rtol=0)
        assert abs(np.mean(distances)-record['sliced_w2'])<1e-12
        checks.append(dict(model=record['model'],prediction_sha256=sha(p),n_observations=10,
                           c2st_heldout_decisions=40000,accuracy_arithmetic='passed',
                           prior_whitened_sliced_w2='independently reproduced within1e-12'))
    event_checks=[]
    for model in ['gpt-5.6-sol','gpt-6-sol','gpt-6.1-sol']:
        event_file=D/'generation-events'/(model+'.jsonl');events=[json.loads(s) for s in event_file.read_text().splitlines()]
        tools=sum(e.get('item',{}).get('type') not in [None,'agent_message','reasoning'] for e in events)
        messages=[e['item']['text'] for e in events if e.get('item',{}).get('type')=='agent_message']
        assert tools==0 and json.loads(messages[-1])==json.loads((D/(model+'.json')).read_text())
        event_checks.append(dict(model=model,event_file=str(event_file.relative_to(R)),sha256=sha(event_file),tool_events=tools,submission_matches_final_generation_event=True))
    out=dict(source_files_verified=len(manifest['files']),source_design_prior_and_observations='passed',
             all_ten_reference_posteriors_match_original_csv=True,frozen_files='passed',
             hidden_true_parameter_files_acquired=False,prediction_checks=checks,
             c2st_audit_scope='Recompute all held-out decision accuracies/fold allocation, no classifier refit; frozen scorer and original decisions retained',
             reference_limit='Original reference is finite Polya-Gamma MCMC, not analytic exact truth',generation_checks=event_checks)
    if write:(D/'verification.json').write_text(json.dumps(out,indent=2)+'\n')
    return out

if __name__=='__main__': print(json.dumps(verify(),indent=2))
