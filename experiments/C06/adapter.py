"""Custom CASCADE DS04 animal-held-out, native-rate spike-rate inference.

No CASCADE prediction, pretrained model or simulated calcium is used. Acquisition
is pinned to public Git blobs; raw files remain a local cache under upstream terms.
"""
from pathlib import Path
import hashlib,json,re,subprocess
import numpy as np
from scipy.io import loadmat
from scipy.ndimage import gaussian_filter1d

P=Path(__file__).resolve().parent
CACHE=P.parents[1]/'data/cache/C06'
TRAIN_ANIMALS=['190115_Fish2','190125_Fish1']
TEST_ANIMALS=['190116_Fish1','190301_Fish1']
SIGMA_SECONDS=.2

def digest(p):
 return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def acquire():
 index=json.loads((P/'source/acquisition-index.json').read_text())
 (CACHE/'raw').mkdir(parents=True,exist_ok=True)
 records=[]
 for item in index['files']:
  dest=CACHE/'raw'/Path(item['path']).name
  url='https://raw.githubusercontent.com/HelmchenLabSoftware/Cascade/'+index['commit']+'/'+item['path']
  if not dest.exists():
   subprocess.run(['curl','--fail','--location','--retry','2','--max-time','90','--silent','--show-error',url,'-o',str(dest)],check=True)
  raw=dest.read_bytes()
  assert len(raw)==item['size']
  assert hashlib.sha1(('blob '+str(len(raw))+'\0').encode()+raw).hexdigest()==item['sha']
  records.append(dict(path=str(dest.relative_to(P.parents[1])),url=url,bytes=len(raw),git_blob_sha1=item['sha'],sha256=digest(dest)))
 return records

def prepare():
 sources=acquire();recordings=[]
 for source in sources:
  path=P.parents[1]/source['path']
  animal=re.search(r'(\d{6}_Fish\d+)',path.name).group(1)
  cell=path.stem
  raw=loadmat(path,simplify_cells=True)['CAttached']
  raw=[raw] if isinstance(raw,dict) else list(raw)
  for j,r in enumerate(raw):
   t=np.asarray(r['fluo_time'],dtype=float).ravel()
   full_f=np.asarray(r['fluo_mean'],dtype=float).ravel()
   # Publisher loader truncates extra fluorescence entries without timestamps.
   f=full_f[:len(t)]
   s=np.asarray(r['events_AP'],dtype=float).ravel()/10000.
   assert len(t)==len(f) and len(t)>2 and np.isfinite(t).all() and np.isfinite(f).all()
   assert np.all(np.diff(t)>0)
   dt=float(np.median(np.diff(t)))
   assert np.max(np.abs(np.diff(t)-dt))<dt*.02
   edges=np.r_[t[0]-dt/2,(t[1:]+t[:-1])/2,t[-1]+dt/2]
   counts=np.histogram(s[np.isfinite(s)],bins=edges)[0]
   target=gaussian_filter1d(counts.astype(float),SIGMA_SECONDS/dt,mode='reflect')
   assert np.isclose(target.sum(),counts.sum())
   recordings.append(dict(animal=animal,cell=cell,recording=j,n=len(t),dt=dt,
    first_frame_seconds=float(t[0]),last_frame_seconds=float(t[-1]),
    duration_seconds=float(len(t)*dt),untimed_fluorescence_tail_dropped=int(len(full_f)-len(t)),spikes_in_frame_support=int(counts.sum()),
    events_outside_frame_support=int(np.isfinite(s).sum()-counts.sum()),
    dff=f.astype(np.float32),target=target.astype(np.float32),counts=counts.astype(np.int16)))
 assert len(sources)==15 and sorted({r['animal'] for r in recordings})==sorted(TRAIN_ANIMALS+TEST_ANIMALS)
 maxlen=max(r['n'] for r in recordings);arrays={};manifest=[]
 for split,animals in [('train',TRAIN_ANIMALS),('test',TEST_ANIMALS)]:
  rec=[r for r in recordings if r['animal'] in animals]
  x=np.zeros((len(rec),3,maxlen),np.float32);y=np.full((len(rec),maxlen),-1,np.float32)
  counts=np.full((len(rec),maxlen),-1,np.int16)
  for i,r in enumerate(rec):
   n=r['n'];x[i,0,:n]=r['dff'];x[i,1,:n]=1;x[i,2,:n]=r['dt'];y[i,:n]=r['target'];counts[i,:n]=r['counts']
   manifest.append(dict(split=split,row=i,**{k:v for k,v in r.items() if k not in ['dff','target','counts']}))
  arrays.update({split+'_x':x,split+'_y':y,split+'_counts':counts,
    split+'_groups':np.array([r['animal'] for r in rec]),split+'_cells':np.array([r['cell'] for r in rec])})
 np.savez_compressed(CACHE/'data.npz',**arrays)
 manifest=dict(benchmark_id='C06',custom_endpoint='CASCADE DS04 native-rate OGB1 zebrafish pDp animal-held-out',
  source_commit=json.loads((P/'source/acquisition-index.json').read_text())['commit'],sources=sources,
  total_source_bytes=sum(s['bytes'] for s in sources),recordings=manifest,shapes={k:list(v.shape) for k,v in arrays.items()},
  data_sha256=digest(CACHE/'data.npz'),train_animals=TRAIN_ANIMALS,test_animals=TEST_ANIMALS,
  selection='All 15 DS04 neuron files and every released recording; fixed alternating lexicographic animal split, no label-based filtering.',
  license='Upstream repository GPL-3.0; no separate data-specific declaration found. Preserve upstream attribution/terms; no independent raw-data redistribution grant asserted.')
 (P/'data-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
 return manifest

def load():
 with np.load(CACHE/'data.npz') as z:return tuple(z[k] for k in ['train_x','train_y','test_x','test_y'])

def score(predictions,truth,test_x=None):
 """Equal-animal mean of equal-neuron Pearson on smoothed counts/native bin."""
 pred=np.asarray(predictions);truth=np.asarray(truth)
 assert pred.shape==truth.shape and np.isfinite(pred).all() and np.all(pred>=0)
 with np.load(CACHE/'data.npz') as z:
  assert np.array_equal(truth,z['test_y']), 'Use canonical full test set; grouping is fixed'
  cells=z['test_cells'];animals=z['test_groups']
 return _score_groups(pred,truth,cells,animals)

def _score_groups(pred,truth,cells,animals):
 """Pure grouped scorer, also independently verifiable on synthetic fixtures."""
 results=[]
 for cell in np.unique(cells):
  rows=np.flatnonzero(cells==cell);actual=[];estimated=[]
  for i in rows:
   valid=truth[i]>=0;actual.extend(truth[i,valid]);estimated.extend(pred[i,valid])
  a=np.asarray(actual);b=np.asarray(estimated)
  corr=float(np.corrcoef(a,b)[0,1]) if np.std(a)>0 and np.std(b)>0 else 0.
  spikes=float(a.sum());error=float(np.abs(a-b).sum()/max(spikes,1e-12));bias=float((b-a).sum()/max(spikes,1e-12))
  results.append(dict(cell=str(cell),animal=str(animals[rows[0]]),pearson=corr,relative_error=error,relative_bias=bias,n_frames=len(a)))
 grouped=[dict(animal=str(a),pearson=float(np.mean([r['pearson'] for r in results if r['animal']==a]))) for a in np.unique(animals)]
 return dict(score=float(np.mean([r['pearson'] for r in grouped])),metric='animal_mean_neuron_pearson_smoothed200ms',direction='higher',per_unit=[r['pearson'] for r in results],cell_results=results,animal_results=grouped)

def baseline(train_x,train_y,test_x):
 """OASIS default AR1, train-only global amplitude, then matched 200ms smoothing.

 Fixed conventional specialist reference; not CASCADE or current SOTA. Its fitted
 calcium parameters may use the unlabeled whole test recording (offline task).
 """
 from oasis.functions import deconvolve
 def infer(x):
  out=np.zeros((len(x),x.shape[-1]),float)
  for i,row in enumerate(x):
   n=int(row[1].sum());trace=np.asarray(row[0,:n],dtype=float)
   events=np.maximum(deconvolve(trace,penalty=1,optimize_g=0)[1],0)
   out[i,:n]=gaussian_filter1d(events,SIGMA_SECONDS/float(row[2,0]),mode='reflect')
  return out
 training=infer(train_x);valid=train_y>=0
 scale=float(train_y[valid].sum()/max(training[valid].sum(),1e-12))
 return infer(test_x)*scale

if __name__=='__main__':
 m=prepare();print(json.dumps({k:v for k,v in m.items() if k not in ['sources','recordings']},indent=2))
