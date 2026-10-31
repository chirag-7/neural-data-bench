"""Independent source/split/scorer audit; no predictive methods or real-data scores."""
from pathlib import Path
import hashlib,json,importlib.util
import numpy as np
from scipy.io import loadmat
import h5py
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1];CACHE=ROOT/'data/cache/K06'
def run():
    manifest=json.loads((HERE/'source.json').read_text())
    for row in manifest['files']:
        p=ROOT/row['path'];assert p.stat().st_size==row['bytes'] and hashlib.sha256(p.read_bytes()).hexdigest()==row['sha256']
    d=np.load(CACHE/'data.npz',allow_pickle=False);rows=json.loads((CACHE/'row-manifest.json').read_text())
    with h5py.File(CACHE/'groundTruth_cell_list.mat') as f:
        def read(key):
            a=f['gt'][key][()]
            if a.dtype.kind!='O':return a.ravel().tolist()
            return [''.join(chr(int(x)) for x in f[ref][()].ravel()) for ref in a.ravel()]
        gt={k:read(k) for k in ['menu_UID','menu_name','menu_groundTruth','menu_animals']}
    allowed={(s,int(uid)):(label,animal) for s,uid,label,animal in zip(gt['menu_name'],gt['menu_UID'],gt['menu_groundTruth'],gt['menu_animals']) if animal.startswith('AllenInstitute_') and label in ['PV','SST']}
    assert len(allowed)==207==len(rows)
    assert set(d['train_groups']).isdisjoint(d['test_groups'])
    assert len(set(d['train_groups']))==11 and len(set(d['test_groups']))==5
    memo={};scalars=['troughToPeak','troughtoPeakDerivative','ab_ratio','PT_ratio','waveform_duration','waveform_halfwidth']
    for split in ['train','test']:
        wanted=[r for r in rows if r['split']==split]
        assert [r['session']+':'+str(r['source_uid']) for r in wanted]==d[split+'_units'].tolist()
        for i,r in enumerate(wanted):
            assert allowed[(r['session'],r['source_uid'])]==(r['label'],r['animal'])
            if r['session'] not in memo:memo[r['session']]=loadmat(CACHE/(r['session']+'.cell_metrics.cellinfo.mat'),simplify_cells=True)['cell_metrics']
            g=memo[r['session']];ids=np.atleast_1d(g['UID']);ix=ids.tolist().index(r['source_uid'])
            assert ix+1 in np.atleast_1d(g['groundTruthClassification'][r['label']])
            assert str(np.atleast_1d(g['animal'])[ix])==r['animal']
            assert int(r['label']=='SST')==d[split+'_y'][i]
            t=np.asarray(g['waveforms']['time'] if len(ids)==1 else g['waveforms']['time'][ix]).ravel()
            w=np.asarray(g['waveforms']['filt'] if len(ids)==1 else g['waveforms']['filt'][ix]).ravel()
            shape=np.interp(np.linspace(-.5,1.5,81),t,w)/max(abs(w))
            expected=np.r_[[np.atleast_1d(g[k])[ix] for k in scalars],shape]
            np.testing.assert_allclose(d[split+'_x'][i],expected,equal_nan=True)
    assert np.isfinite(d['train_x'][:,6:]).all() and np.isfinite(d['test_x'][:,6:]).all()
    for fold in set(d['train_cv_fold']):
        assert set(d['train_y'][d['train_cv_fold']==fold])=={0,1}
        assert set(d['train_groups'][d['train_cv_fold']==fold]).isdisjoint(d['train_groups'][d['train_cv_fold']!=fold])
    spec=importlib.util.spec_from_file_location('adapter',HERE/'adapter.py');a=importlib.util.module_from_spec(spec);spec.loader.exec_module(a)
    # PV mouse A accuracy1, PV B accuracy0, SST C accuracy1 => grouped balanced .75.
    assert a.aggregate(np.array([0,0,1,1]),np.array([0,0,0,1]),np.array(['A','A','B','C']))==.75
    report=dict(benchmark_id='K06',status='verified preparation; not frozen',source_files_verified=len(manifest['files']),checks=['Exact source hashes/bytes','207 source mouse/session/UID matches','GT list agrees with per-session independent optotag classifications','All six scalar and81 waveform predictors independently reconstructed','11/5 mouse disjointness','3 training CV folds mouse-disjoint and class-covered','No genetic/ID/opto-response/firing/ACG/ISI predictor fields','Toy scorer verifies class-balanced mouse aggregation'],method_runs=0,model_calls=0,real_slice_method_scores=0)
    (HERE/'verification.json').write_text(json.dumps(report,indent=2)+'\n');print(report)
if __name__=='__main__':run()
