"""Prepared original sbibm Bernoulli-GLM observations; references are scorer-only."""
from pathlib import Path
import hashlib,json,struct
import numpy as np
R=Path(__file__).resolve().parents[2]
C=R/'data/cache/L06'

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()

def prepare():
    """Read fixed-size original tensor storage without executing pickle objects."""
    manifest=json.loads((R/'data/manifests/L06.json').read_text())
    for f in manifest['files']: assert sha(R/f['path'])==f['sha256']
    source=C/'source'
    raw=(source/'design_matrix.pt').read_bytes()
    assert len(raw)==4344 and struct.unpack('<q',raw[336:344])[0]==1000
    design=np.frombuffer(raw[344:],dtype='<f4').copy().reshape(100,10)
    stimulus=np.random.RandomState(42).randn(100).astype(np.float32)
    expected=np.zeros((100,10),dtype=np.float32);expected[:,0]=1
    for j in range(9): expected[j:,j+1]=stimulus[:100-j]
    assert np.array_equal(design,expected)
    stimraw=(source/'stimulus_I.pt').read_bytes()
    assert np.array_equal(np.frombuffer(stimraw[-400:],dtype='<f4'),stimulus)
    D=np.eye(9,dtype=np.float32)-np.diag(np.ones(8,dtype=np.float32),-1)
    F=D@D+np.sqrt(np.diag(np.arange(9,dtype=np.float32)/np.float32(9)))
    precision=np.zeros((10,10),dtype=np.float32);precision[0,0]=.5;precision[1:,1:]=F.T@F
    spikes=[];reference=[];summary=[]
    for i in range(1,11):
        d=source/f'num_observation_{i}'
        spikes.append(np.loadtxt(d/'observation_raw.csv',delimiter=',',skiprows=1).reshape(100))
        reference.append(np.loadtxt(d/'reference_posterior_samples.csv.bz2',delimiter=',',skiprows=1))
        summary.append(np.loadtxt(d/'observation.csv',delimiter=',',skiprows=1).reshape(10))
    spikes=np.asarray(spikes);reference=np.asarray(reference);summary=np.asarray(summary)
    assert spikes.shape==(10,100) and np.isin(spikes,[0,1]).all()
    assert reference.shape==(10,10000,10) and np.isfinite(reference).all()
    assert np.allclose(spikes@design,summary,atol=3e-5,rtol=1e-6)
    np.savez_compressed(C/'data.npz',design=design.astype(np.float64),spikes=spikes,
                        precision=precision.astype(np.float64),reference=reference)
    meta=dict(feature_names=['offset']+[f'stimulus_lag_{j}' for j in range(9)],
              units='dimensionless model parameters; dt=1,100 bins, fixed stimulus seed42',
              input='100x10 design,10x100 binary spikes,10x10 Gaussian prior precision',
              original_observation_ids=list(range(1,11)),n_posterior_draws=10000,
              primary_metric='c2st_accuracy_2000',direction='lower',
              chance_target=.5,independence='Ten simulated observations share one stimulus/model; not ten biological preparations')
    (C/'metadata.json').write_text(json.dumps(meta,indent=2)+'\n')
    return dict(source_files_verified=len(manifest['files']),design_exactly_matches_author_seed=True,
                summary_matches_XTy=True,n_observations=10,reference_shape=list(reference.shape))

def inputs():
    with np.load(C/'data.npz') as z: return z['design'],z['spikes'],z['precision']

def references():
    with np.load(C/'data.npz') as z: return z['reference']

if __name__=='__main__': print(json.dumps(prepare(),indent=2))
