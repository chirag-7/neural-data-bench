"""Donor-disjoint supervised prediction of orthogonal Circle-panel nuclear fractions."""
from pathlib import Path
import csv, hashlib, json, re
import numpy as np
ROOT = Path(__file__).resolve().parents[2]
CACHE = ROOT / 'data/cache/K05'
TARGETS = ['Astro', 'EndoMural', 'Inhib']
SEED = 20261031

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def prepare():
    rows = list(csv.DictReader((CACHE/'HALO_cell_type_proportions.csv').open()))
    truth = {}
    for row in rows:
        if row['Combo'] == 'Circle' and row['Confidence'] in ['OK', 'High'] and row['cell_type'] in TARGETS:
            key = (row['Sample'], row['cell_type'])
            assert key not in truth
            truth[key] = float(row['prop'])
    with (CACHE/'DLPFC_bulk_counts.txt').open() as stream:
        reader = csv.reader(stream, delimiter='\t')
        ids = next(reader)[1:]
        data = list(reader)
    genes = np.array([r[0] for r in data])
    counts = np.array([r[1:] for r in data], dtype=np.float64).T
    assert counts.shape == (110, len(genes)) and np.all(counts >= 0)
    selected, records = [], []
    for i, name in enumerate(ids):
        match = re.fullmatch(r'([^_]+)_(Br\d+)_(Ant|Mid|Post)_(Bulk|Cyto|Nuc)', name)
        assert match, name
        library, donor, position, extraction = match.groups()
        block = donor + '_' + position.lower()
        if all((block, t) in truth for t in TARGETS):
            selected.append(i)
            records.append(dict(sample_id=name, donor=donor, block=block, library=library, extraction=extraction))
    x = np.log2(1 + counts[selected] / counts[selected].sum(axis=1, keepdims=True) * 1e6)
    y = np.array([[truth[(r['block'], t)] for t in TARGETS] for r in records])
    groups = np.array([r['donor'] for r in records]); blocks = np.array([r['block'] for r in records])
    donors = np.array(sorted(set(groups))); rng = np.random.default_rng(SEED)
    held = sorted(rng.permutation(donors)[:max(2, int(np.ceil(len(donors)*.3)))].tolist())
    te = np.flatnonzero(np.isin(groups, held)); tr = np.flatnonzero(~np.isin(groups, held))
    assert not set(groups[tr]) & set(groups[te]) and len(tr) and len(te)
    # Select variable genes using training bulk samples only, before any model receives arrays.
    order = np.lexsort((genes, -np.var(x[tr], axis=0)))[:2000]
    x = x[:, order]
    arrays = {}
    for name, idx in [('train',tr),('test',te)]:
        for key, value in [('x',x),('y',y),('groups',groups),('blocks',blocks),('units',np.array([r['sample_id'] for r in records]))]:
            arrays[name+'_'+key] = value[idx]
    np.savez_compressed(CACHE/'data.npz', **arrays)
    meta = dict(benchmark_id='K05', slice_id='dlpfc-circle-orthogonal-fraction-donorholdout-v1',
        status='prepared for parent review; not frozen; no model or reference scores',
        dataset='Human DLPFC multi-assay cellular deconvolution study', seed=SEED,
        executed_deviation='Supervised bulk-to-orthogonal-fraction calibration; not reference-only deconvolution',
        input='float64 samples x 2000 genes, log2(1+CPM), library sum computed over all 21745 genes; train-only variance selection',
        feature_names=genes[order].tolist(), target_names=TARGETS,
        units='fractions of all detected nuclei in the adjacent Circle IF/RNAScope section, including unclassified Other nuclei in the denominator',
        label_encoding={'0':'Astro/GFAP','1':'EndoMural/CLDN5','2':'Inhib/GAD1'},
        target='Three independently measured HALO Circle-panel prop columns; never prop_sn or adjusted combined-panel prop',
        direction='lower', metric='donor_block_macro_rmse', primary_metric='donor_block_macro_rmse',
        train_shape=list(x[tr].shape),test_shape=list(x[te].shape),n_train=len(tr),n_test=len(te),
        train_donors=sorted(set(groups[tr])),test_donors=held,n_train_blocks=len(set(blocks[tr])),n_test_blocks=len(set(blocks[te])),
        split='Sorted unique eligible donors, numpy default_rng(20261031) permutation, first ceil(30%) (minimum2) held out; all blocks/extractions/library preps remain together',
        grouping='donor, then tissue block, then bulk library/extraction replicate; replicates share orthogonal fraction labels',
        primary_aggregation='For each target, average squared errors across bulk replicates within block, blocks within donor, then donors equally; take square root; average the three target RMSEs equally',
        reference='Train-donor GroupKFold ridge regression with inner-train top1000 variance selection within outer-train top2000 and train-fold scaling and alpha grid, equal donor/block training weights; no paper SOTA claim',
        eligible_circle_blocks=sorted({r['block'] for r in records}),
        limitations=['Only 10 source donors and fewer eligible high-confidence matched donors; all replicates from a block share a label',
        'Three Circle-panel marker-positive fractions, not a complete mutually exclusive cellular composition; outputs need not sum to one',
        'Adjacent sections introduce sampling/morphology mismatch; HALO pipeline annotations are imperfect orthogonal measurements',
        'Confidence filter follows upstream image QC; it is fixed before split and applied uniformly',
        'Library protocol and extraction are confounds; features contain expression only, no donor/ID/protocol columns',
        'Single-nucleus reference not supplied; endpoint tests supervised calibration, not zero-label deconvolution'],
        license='Upstream repository MIT includes downloaded processed count TSV, fraction CSV, analysis code and README; no raw human sequencing/images redistributed',
        terms_url='https://github.com/LieberInstitute/Human_DLPFC_Deconvolution/blob/main/LICENSE',
        data_sha256=sha(CACHE/'data.npz'))
    (CACHE/'metadata.json').write_text(json.dumps(meta,indent=2)+'\n')
    (CACHE/'row-manifest.json').write_text(json.dumps([dict(r,split='test' if i in te else 'train') for i,r in enumerate(records)],indent=2)+'\n')
    return meta

def load():
    with np.load(CACHE/'data.npz',allow_pickle=False) as d:
        return tuple(d[k].copy() for k in ['train_x','train_y','test_x','test_y'])

def aggregate(pred, truth, groups, blocks):
    pred = np.asarray(pred)
    if pred.shape != truth.shape or not np.isfinite(pred).all() or np.any((pred < 0)|(pred > 1)):
        raise ValueError('Expected finite fractions in [0,1] with truth shape')
    errors=(pred-truth)**2
    donor_mse=[]
    for donor in sorted(set(groups)):
        donor_mse.append(np.mean([np.mean(errors[blocks==b],axis=0) for b in sorted(set(blocks[groups==donor]))],axis=0))
    return float(np.sqrt(np.mean(donor_mse,axis=0)).mean())

def score(pred, truth, test_x=None):
    with np.load(CACHE/'data.npz',allow_pickle=False) as d:
        groups=d['test_groups'];blocks=d['test_blocks']
    value=aggregate(pred,truth,groups,blocks)
    per=[aggregate(np.asarray(pred)[groups==g],truth[groups==g],groups[groups==g],blocks[groups==g]) for g in sorted(set(groups))]
    return dict(score=value,metric='donor_block_macro_rmse',direction='lower',per_unit=per,unit_ids=sorted(set(groups)),unit_definition='donor-level macro RMSE; primary recomputes square root after pooling donor MSEs')

def baseline(train_x, train_y, test_x):
    """Fixed conventional supervised reference; caller may execute only after freeze."""
    from sklearn.linear_model import Ridge
    from sklearn.preprocessing import StandardScaler
    from sklearn.model_selection import GroupKFold
    with np.load(CACHE/'data.npz',allow_pickle=False) as d:
        groups=d['train_groups']; blocks=d['train_blocks']
    def weights(g,b):
        return np.array([1./(len(set(b[g==a])) * sum(b==block)) for a,block in zip(g,b)])
    def fitted(x,y,xt,alpha,g,b):
        keep=np.argsort(-np.var(x,axis=0),kind='stable')[:1000]
        x=x[:,keep];xt=xt[:,keep]
        scaler=StandardScaler().fit(x); xx=scaler.transform(x)
        model=Ridge(alpha=alpha,solver='svd').fit(xx,y,sample_weight=weights(g,b)*len(g)/len(set(g)))
        return np.clip(model.predict(scaler.transform(xt)),0,1)
    candidates=[1.,10.,100.,1000.,10000.]
    folds=list(GroupKFold(min(4,len(set(groups)))).split(train_x,train_y,groups))
    losses=[]
    for alpha in candidates:
        pred=np.zeros_like(train_y)
        for a,b in folds:pred[b]=fitted(train_x[a],train_y[a],train_x[b],alpha,groups[a],blocks[a])
        losses.append(aggregate(pred,train_y,groups,blocks))
    return fitted(train_x,train_y,test_x,candidates[int(np.argmin(losses))],groups,blocks)

if __name__=='__main__':
    m=prepare();print({k:m[k] for k in ['train_shape','test_shape','train_donors','test_donors','n_train_blocks','n_test_blocks']})
