"""Allen-only optotagged PV/SST inference from extracellular waveform metrics."""
from pathlib import Path
import hashlib, json
import numpy as np
ROOT=Path(__file__).resolve().parents[2]
CACHE=ROOT/'data/cache/K06'
SEED=20261031
SCALARS=['troughToPeak','troughtoPeakDerivative','ab_ratio','PT_ratio','waveform_duration','waveform_halfwidth']
GRID=np.linspace(-.5,1.5,81)

def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def groundtruth():
    import h5py
    with h5py.File(CACHE/'groundTruth_cell_list.mat') as h:
        def decode(o):
            if isinstance(o,h5py.Reference):return decode(h[o])
            a=o[()]
            if a.dtype.kind=='O':return [decode(r) for r in a.ravel()]
            if o.attrs.get('MATLAB_class')==b'char':return ''.join(chr(int(i)) for i in a.ravel())
            return a.ravel().tolist()
        return {k:decode(h['gt'][k]) for k in ['menu_UID','menu_animals','menu_groundTruth','menu_name']}

def prepare():
    from scipy.io import loadmat
    gt=groundtruth();records=[];features=[]
    eligible=[i for i,a in enumerate(gt['menu_animals']) if a.startswith('AllenInstitute_') and gt['menu_groundTruth'][i] in ['PV','SST']]
    memo={}
    for i in eligible:
        session=gt['menu_name'][i]
        if session not in memo:memo[session]=loadmat(CACHE/(session+'.cell_metrics.cellinfo.mat'),simplify_cells=True)['cell_metrics']
        g=memo[session];uids=np.atleast_1d(g['UID']);n=len(uids);idx=np.flatnonzero(uids==gt['menu_UID'][i]);assert len(idx)==1
        ix=int(idx[0]);label=gt['menu_groundTruth'][i];animal=gt['menu_animals'][i]
        assert str(np.atleast_1d(g['animal'])[ix])==animal
        # Ground-truth classification stores one-based row indices, not source UID values.
        assert ix+1 in np.atleast_1d(g['groundTruthClassification'][label])
        values=[float(np.atleast_1d(g[k])[ix]) for k in SCALARS]
        def waveform(k):
            value=g['waveforms'][k]
            return np.asarray(value if n==1 else value[ix],dtype=float).ravel()
        t,w=waveform('time'),waveform('filt')
        assert len(t)==len(w) and np.isfinite(t).all() and np.isfinite(w).all() and np.all(np.diff(t)>0)
        # t is milliseconds. Coverage and nonzero amplitude are verified for every cell.
        assert t.min()<=GRID[0] and t.max()>=GRID[-1] and np.max(np.abs(w))>0
        normalized=np.interp(GRID,t,w)/np.max(np.abs(w))
        features.append(values+normalized.tolist())
        records.append(dict(animal=animal,session=session,source_uid=int(uids[ix]),label=label))
    x=np.array(features,dtype=float);x[~np.isfinite(x)]=np.nan
    y=np.array([int(r['label']=='SST') for r in records],dtype=np.int64)
    groups=np.array([r['animal'] for r in records]);rng=np.random.default_rng(SEED);held=[]
    for label in [0,1]:
        animals=np.array(sorted(set(groups[y==label])))
        assert not set(animals)&set(groups[y!=label])
        held.extend(rng.permutation(animals)[:max(1,int(np.ceil(.25*len(animals))))].tolist())
    held=sorted(held);te=np.flatnonzero(np.isin(groups,held));tr=np.flatnonzero(~np.isin(groups,held))
    assert not set(groups[tr])&set(groups[te]) and set(y[tr])==set(y[te])=={0,1}
    # Train-only CV explicitly stratifies mouse groups; no cell or session crosses folds.
    fold_map={};rng=np.random.default_rng(SEED+1)
    for label in [0,1]:
        animals=np.array(sorted(set(groups[tr][y[tr]==label])))
        for j,a in enumerate(rng.permutation(animals)):fold_map[a]=j%3
    arrays={}
    for name,idx in [('train',tr),('test',te)]:
        for key,value in [('x',x),('y',y),('groups',groups),('units',np.array([r['session']+':'+str(r['source_uid']) for r in records]))]:arrays[name+'_'+key]=value[idx]
    arrays['train_cv_fold']=np.array([fold_map[a] for a in groups[tr]])
    np.savez_compressed(CACHE/'data.npz',**arrays)
    names=SCALARS+['normalized_filtered_waveform_t%+.3fms'%t for t in GRID]
    meta=dict(benchmark_id='K06',slice_id='allen-cellexplorer-pv-sst-waveform-mouseholdout-v1',
        status='prepared for parent review; not frozen; no model or reference scores',
        dataset='CellExplorer ground truth subset contributed by Josh Siegle / Allen Institute',
        input='float64 cells x87 features: six waveform scalar metrics and 81 interpolated normalized filtered mean-waveform samples; NaN means missing scalar',
        feature_names=names,units='Widths/durations and waveform sample grid in ms; ab_ratio/PT_ratio dimensionless; sampled filtered waveform divided by maximum absolute source waveform amplitude',
        label_encoding={'0':'optotagged PV','1':'optotagged SST'},n_classes=2,
        target='Genetic optotag classification, independently measured from predictor waveform descriptors; no putativeCellType or optotag-response predictors',
        excluded_predictors=['Genotype/Cre line','Animal/session/unit IDs','Brain region and coordinates','PutativeCellType','Optotagging modulation/time/significance','Response curves','Firing rates/autocorrelograms/ISI metrics'],
        grouping='Allen source mouse ID; one included session per mouse',seed=SEED,
        split='Sorted mice separately for PV then SST; numpy default_rng(20261031) permutation continued across classes; first ceil(25%) per class held out',
        train_shape=list(x[tr].shape),test_shape=list(x[te].shape),n_train=len(tr),n_test=len(te),
        n_train_mice=len(set(groups[tr])),n_test_mice=len(set(groups[te])),train_mice=sorted(set(groups[tr])),test_mice=held,
        label_counts={'train':np.bincount(y[tr],minlength=2).tolist(),'test':np.bincount(y[te],minlength=2).tolist()},
        metric='class_balanced_mouse_accuracy',primary_metric='class_balanced_mouse_accuracy',direction='higher',
        primary_aggregation='Compute accuracy within each held-out mouse, mean mice within each true class, then mean the two classes; pooled balanced accuracy secondary',
        reference='Training-mouse-stratified3fold selection among standardized/imputed RBF SVM and ExtraTrees, using primary grouped metric; no verified SOTA claim',
        missing_scalar_fraction=float(np.isnan(x[:,:6]).mean()),
        license='Allen Institute Terms of Use, research/noncommercial with attribution, applies to original Allen source content; CellExplorer code BSD-3-Clause is retained separately and not asserted to license contributor data',
        terms_url='https://alleninstitute.org/legal/terms-of-use',raw_redistribution='Source caches remain local/excluded from version control; retain source manifests and preparation code',
        limitations=['Only two genetically optotagged interneuron classes from one laboratory/resource; not general multi-class molecular taxonomy',
        'Class is mouse/Cre-line-level; genetic line and acquisition cohort may confound waveform generalization despite excluded metadata',
        'Only five PV mice in source subset; small held-out mouse counts imply substantial uncertainty',
        'Source collection is not balanced across brain areas; region is incomplete in consolidated metadata and is not a predictor',
        'Waveforms are upstream processed averages, not a raw spike sorting or waveform extraction benchmark',
        'Temporal firing/response features excluded because optotag manipulation intervals could contaminate them'],
        data_sha256=sha(CACHE/'data.npz'))
    (CACHE/'metadata.json').write_text(json.dumps(meta,indent=2)+'\n')
    (CACHE/'row-manifest.json').write_text(json.dumps([dict(r,split='test' if i in te else 'train') for i,r in enumerate(records)],indent=2)+'\n')
    return meta

def load():
    with np.load(CACHE/'data.npz',allow_pickle=False) as d:return tuple(d[k].copy() for k in ['train_x','train_y','test_x','test_y'])

def aggregate(pred,truth,groups):
    pred=np.asarray(pred)
    if pred.shape!=truth.shape or not np.isfinite(pred).all() or not np.isin(pred,[0,1]).all():raise ValueError('Expected one integer PV/SST class per cell')
    per=[]
    for label in [0,1]:
        mice=sorted(set(groups[truth==label]));assert mice
        per.append(np.mean([np.mean(pred[groups==mouse]==truth[groups==mouse]) for mouse in mice]))
    return float(np.mean(per))

def score(pred,truth,test_x=None):
    with np.load(CACHE/'data.npz',allow_pickle=False) as d:groups=d['test_groups']
    value=aggregate(pred,truth,groups)
    mice=sorted(set(groups));per=[float(np.mean(np.asarray(pred)[groups==g]==truth[groups==g])) for g in mice]
    return dict(score=value,metric='class_balanced_mouse_accuracy',direction='higher',per_unit=per,unit_ids=mice,unit_labels=[int(truth[groups==g][0]) for g in mice],unit_definition='mouse accuracy; primary averages mice within each class before averaging classes')

def baseline(train_x,train_y,test_x):
    """Fixed conventional reference; no test labels or test transforms fitted."""
    from sklearn.svm import SVC
    from sklearn.ensemble import ExtraTreesClassifier
    from sklearn.impute import SimpleImputer
    from sklearn.preprocessing import StandardScaler
    from sklearn.pipeline import make_pipeline
    from sklearn.base import clone
    with np.load(CACHE/'data.npz',allow_pickle=False) as d:groups=d['train_groups'];folds=d['train_cv_fold']
    candidates=[make_pipeline(SimpleImputer(strategy='median',add_indicator=True),StandardScaler(),SVC(C=c,kernel='rbf',class_weight='balanced')) for c in [.1,1,10,100]]
    candidates+=[make_pipeline(SimpleImputer(strategy='median',add_indicator=True),ExtraTreesClassifier(n_estimators=500,max_features=f,class_weight='balanced',random_state=SEED,n_jobs=1)) for f in ['sqrt',1.]]
    cv=[]
    for model in candidates:
        pred=np.zeros_like(train_y)
        for fold in sorted(set(folds)):
            a=folds!=fold;b=~a;fit=clone(model).fit(train_x[a],train_y[a]);pred[b]=fit.predict(train_x[b])
        cv.append(aggregate(pred,train_y,groups))
    model=clone(candidates[int(np.argmax(cv))]).fit(train_x,train_y)
    return model.predict(test_x)

if __name__=='__main__':
    m=prepare();print({k:m[k] for k in ['train_shape','test_shape','n_train_mice','n_test_mice','label_counts']})
