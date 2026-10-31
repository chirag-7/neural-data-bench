"""Independent source/split/scorer audit; runs no predictive method or real-data score."""
from pathlib import Path
import csv,hashlib,json,importlib.util
import numpy as np
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1];CACHE=ROOT/'data/cache/K05'
def run():
    manifest=json.loads((HERE/'source.json').read_text())
    for row in manifest['files']:
        p=ROOT/row['path'];assert p.stat().st_size==row['bytes'] and hashlib.sha256(p.read_bytes()).hexdigest()==row['sha256']
    d=np.load(CACHE/'data.npz',allow_pickle=False);meta=json.loads((CACHE/'metadata.json').read_text());rows=json.loads((CACHE/'row-manifest.json').read_text())
    truth=list(csv.DictReader((CACHE/'HALO_cell_type_proportions.csv').open()));source={(r['Sample'],r['cell_type']):r for r in truth if r['Combo']=='Circle'}
    counts=list(csv.reader((CACHE/'DLPFC_bulk_counts.txt').open(),delimiter='\t'));names=counts[0][1:];genes=[r[0] for r in counts[1:]]
    full=np.array([r[1:] for r in counts[1:]],dtype=float).T;assert len(set(genes))==len(genes)==21745
    assert set(d['train_groups']).isdisjoint(d['test_groups']) and set(d['train_blocks']).isdisjoint(d['test_blocks'])
    assert len(rows)==63 and len(set(r['sample_id'] for r in rows))==63
    for split in ['train','test']:
        wanted=[r for r in rows if r['split']==split]
        assert [r['sample_id'] for r in wanted]==d[split+'_units'].tolist()
        for i,r in enumerate(wanted):
            cells=[a for a in truth if a['Sample']==r['block'] and a['Combo']=='Circle'];denom=sum(int(a['n_cell']) for a in cells)
            assert cells and len({a['Confidence'] for a in cells})==1
            expected=[]
            for target in ['Astro','EndoMural','Inhib']:
                z=source[(r['block'],target)];assert z['Confidence'] in ['High','OK']
                fraction=int(z['n_cell'])/denom;assert abs(fraction-float(z['prop']))<1e-12;expected.append(fraction)
            np.testing.assert_allclose(d[split+'_y'][i],expected,rtol=1e-12)
            vec=full[names.index(r['sample_id'])];logged=np.log2(1+vec/vec.sum()*1e6)
            np.testing.assert_allclose(d[split+'_x'][i],logged[[genes.index(g) for g in meta['feature_names']]])
    training=np.log2(1+full[[names.index(n) for n in d['train_units']]]/full[[names.index(n) for n in d['train_units']]].sum(axis=1,keepdims=True)*1e6)
    chosen=np.lexsort((np.array(genes),-training.var(axis=0)))[:2000]
    assert np.array(genes)[chosen].tolist()==meta['feature_names']
    spec=importlib.util.spec_from_file_location('adapter',HERE/'adapter.py');a=importlib.util.module_from_spec(spec);spec.loader.exec_module(a)
    # Unequal replicates/blocks: donor A contributes mean of block MSEs, not row count.
    pred=np.array([[.1,.1,.1],[.3,.3,.3],[.5,.5,.5],[.7,.7,.7]])
    actual=a.aggregate(pred,np.zeros_like(pred),np.array(['A','A','A','B']),np.array(['A1','A1','A2','B1']))
    expected=np.sqrt(((((.1**2+.3**2)/2)+.5**2)/2+.7**2)/2)
    assert abs(actual-expected)<1e-12
    report=dict(benchmark_id='K05',status='verified preparation; not frozen',source_files_verified=len(manifest['files']),checks=['Exact source hashes/bytes','63 one-to-one bulk sample IDs','Raw Circle n_cell/all-nuclei denominator reproduces prop','Only image Confidence OK/High','No prop_sn, adjusted composition or imputed truth','Donor and block disjointness','Exact 2000 train-only variable genes and logCPM values','Toy scorer verifies equal replicate/block/donor hierarchy'],method_runs=0,model_calls=0,real_slice_method_scores=0)
    (HERE/'verification.json').write_text(json.dumps(report,indent=2)+'\n');print(report)
if __name__=='__main__':run()
