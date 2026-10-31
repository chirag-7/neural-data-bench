"""Independent A15 saved-output audit. No adapters, predictions or model fitting.
Run after batch outputs exist; optionally write report with --output.
"""
from pathlib import Path
import argparse,csv,hashlib,json
import numpy as np
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import maximum_bipartite_matching
ROOT=Path(__file__).resolve().parents[1]
MODELS=('gpt-5.6-sol','gpt-6-sol','gpt-6.1-sol','task-baseline')
METRIC='recording_macro_event_f1_20ms_onset_20ms_or_20pct_offset'
def require(ok,msg):
    if not ok:raise AssertionError(msg)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def inside(rel):
    p=(ROOT/rel).resolve();require(p.is_relative_to(ROOT.resolve()),'Path outside repo');return p

def audit(require_complete=False):
    exp=ROOT/'experiments/A15';cache=ROOT/'data/cache/A15';spec=json.loads((exp/'run-spec.json').read_text())
    require(spec['benchmark_id']=='A15' and spec['run_id']=='batch-v11','Wrong run')
    require(not spec['train_groups_supplied'],'Hidden training metadata privilege')
    for rel,digest in spec['frozen_files'].items():require(sha(inside(rel))==digest,'Frozen file changed:'+rel)
    require(sha(cache/'data.npz')==spec['data_sha256'],'Data hash changed')
    source=json.loads((exp/'source.json').read_text())
    for r in source['files']:
        p=inside(r['path']);require(p.stat().st_size==r['bytes'] and sha(p)==r['sha256'],'Source changed:'+r['path'])
    rows=json.loads((cache/'row-manifest.json').read_text());test=[r for r in rows if r['split']=='test']
    require(len(test)==20 and {r['bird'] for r in test}=={'or60yw70'},'Wrong outer source grouping')
    require(not {r['bird'] for r in test}&{r['bird'] for r in rows if r['split']=='train'},'Specimen leakage')
    # Access only small target/ID arrays, not padded waveform arrays.
    with np.load(cache/'data.npz',allow_pickle=False) as z:truth=z['test_y'];stored=z['test_events'];units=z['test_units']
    require(units.tolist()==[r['recording'] for r in test],'Source order mismatch');events=[]
    for i,r in enumerate(test):
        csvrows=list(csv.DictReader((cache/(r['recording']+'_annotations.csv')).open()))
        ev=np.array(sorted((float(z['start_seconds'])*.001,float(z['stop_seconds'])*.001) for z in csvrows))
        require(np.all(ev[:,1]>ev[:,0]) and np.min(ev)>=0 and np.max(ev)<=r['duration_seconds']+1/32000,'Invalid source event bounds')
        np.testing.assert_allclose(ev,stored[i][np.isfinite(stored[i,:,0])],rtol=0,atol=1e-12)
        events.append(ev)
    path=ROOT/'results/A15.json';results=json.loads(path.read_text()) if path.exists() else []
    results=[r for r in results if r.get('run_id','batch-v11')=='batch-v11' and r.get('slice_id')=='batch-v11']
    seen=set();audited=[];failed=[]
    for row in results:
        model=row['model'];require(model in MODELS and model not in seen,'Unexpected/duplicate attempt');seen.add(model)
        if row['status']!='measured':failed.append(dict(model=model,status=row['status'],reason=row.get('reason')));continue
        predpath=inside(row['prediction_file']);require(sha(predpath)==row['prediction_sha256'],'Prediction hash changed')
        with np.load(predpath,allow_pickle=False) as z:p=z['predictions']
        require(p.shape==truth.shape and np.isfinite(p).all() and np.isin(p,[0,1]).all(),'Invalid binary mask')
        per=[];tps=[];nps=[];nts=[]
        for i,ev in enumerate(events):
            mask=p[i,:test[i]['n_frames']].astype(bool);edges=np.diff(np.r_[0,mask,0].astype(np.int8));pe=np.c_[np.flatnonzero(edges==1),np.flatnonzero(edges==-1)]*.001
            if len(pe) and len(ev):
                allowed=(abs(pe[:,None,0]-ev[None,:,0])<=.020+1e-12)&(abs(pe[:,None,1]-ev[None,:,1])<=np.maximum(.020,.2*np.diff(ev,axis=1).ravel())[None,:]+1e-12)
                match=maximum_bipartite_matching(csr_matrix(allowed),perm_type='column');tp=int(np.count_nonzero(match>=0))
            else:tp=0
            f1=2*tp/(len(pe)+len(ev)) if len(pe)+len(ev) else 1.
            per.append(f1);tps.append(tp);nps.append(len(pe));nts.append(len(ev))
        require(row['metric']==METRIC and row['direction']=='higher','Metric metadata changed')
        require(np.isclose(row['score'],np.mean(per),rtol=1e-12,atol=1e-15),'Independent eventF1 mismatch')
        np.testing.assert_allclose(row['per_unit'],per,rtol=1e-12,atol=1e-15)
        require(row['unit_ids']==units.tolist() and row['true_positive_events']==tps and row['predicted_event_counts']==nps and row['reference_event_counts']==nts,'Event count/order mismatch')
        program=exp/(model+'.py') if model!='task-baseline' else exp/'adapter.py'
        require(sha(program)==row['code_sha256'],'Program hash changed');require(row['prompt_sha256']==spec['prompt_sha256'],'Prompt hash changed')
        audited.append(dict(model=model,score=float(np.mean(per)),prediction_sha256=sha(predpath),program_sha256=sha(program),independent_maximum_bipartite_event_matching=True,original_source_intervals_verified=True))
    missing=sorted(set(MODELS)-seen);complete=not missing and not failed
    if require_complete:require(complete,'Missing/failed expected attempts')
    return dict(benchmark_id='A15',run_id='batch-v11',verification_status='passed' if complete else 'passed_for_available_measured_attempts',complete=complete,source_files_verified=len(source['files']),n_test_recordings=20,n_test_birds=1,source_label_events=sum(len(e) for e in events),measured_attempts=audited,failed_attempts=failed,missing_models=missing,models_or_references_executed=False)
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--require-complete',action='store_true');p.add_argument('--output',type=Path);a=p.parse_args();report=audit(a.require_complete);text=json.dumps(report,indent=2)+'\n'
    if a.output:a.output.write_text(text)
    print(text)
