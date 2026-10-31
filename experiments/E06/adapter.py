"""Bounded ZAPBench causal population forecasting, official temporal bounds.
Code-derived NLinear reference: google-research/zapbench, Apache-2.0;
source commit 7347b3b21a3f332e281b774c945f1505dd966abf.
"""
from pathlib import Path
import hashlib,json
import numpy as np
ROOT=Path(__file__).resolve().parents[2]
CACHE=ROOT/'data/cache/E06'
PIN='7347b3b21a3f332e281b774c945f1505dd966abf'
OFFSETS=(0,649,2422,3078,3735,5047,5638,6623,7279,7879)
CONDITIONS=(0,1,2,4,5,6,7,8)
CONTEXT=64
HORIZON=32
IDS=np.arange(0,71721,280,dtype=np.int64)[:256]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def prepare():
 a=np.load(CACHE/'raw/traces-selected.npy',allow_pickle=False)
 assert a.shape==(7879,256) and np.isfinite(a).all()
 tr=[];te=[];tg=[];eg=[];bounds=[]
 for c in CONDITIONS:
  lo,hi=OFFSETS[c]+1,OFFSETS[c+1]-1
  n=hi-lo; nt=int(n*.2);nv=int(n*.1);cut=lo+n-nt-nv;test0=hi-nt
  # All training context and target indices lie in the official training block.
  for t in range(lo+CONTEXT,cut-HORIZON+1,16):tr.append(t);tg.append(c)
  # Non-overlapping evaluation targets, matching first official test target.
  for t in range(test0,hi-HORIZON+1,HORIZON):te.append(t);eg.append(c)
  bounds.append(dict(condition=c,full=[lo,hi],train=[lo,cut],validation=[cut,test0],test=[test0,hi]))
 def windows(starts,offset,length):return np.stack([a[t+offset:t+offset+length] for t in starts])
 arrays=dict(train_x=windows(tr,-CONTEXT,CONTEXT),train_y=windows(tr,0,HORIZON),test_x=windows(te,-CONTEXT,CONTEXT),test_y=windows(te,0,HORIZON),train_groups=np.array(tg),test_groups=np.array(eg),train_target_starts=np.array(tr),test_target_starts=np.array(te),neuron_indices=IDS)
 np.savez_compressed(CACHE/'data.npz',**arrays)
 manifest=dict(benchmark_id='E06',status='prepared; parent freeze pending',source_commit=PIN,timeseries='240930_traces',source_shape=[7879,71721],source_gcs='gs://zapbench-release/volumes/20240930/traces/',source_https='https://zapbench-release.storage.googleapis.com/volumes/20240930/traces/',data_license='CC-BY-4.0',source_code_license='Apache-2.0',attribution='Alex Bo-Yuan Chen, Ahrens lab HHMI Janelia (recording); CellMap Project Team HHMI Janelia (annotations); Google Research (processing and benchmark)',selection='256 neuron columns arange(0,71721,280)[:256], fixed without responses or evaluation scores',neuron_indices=IDS.tolist(),context=CONTEXT,horizon=HORIZON,training_stride=16,test_target_stride=32,condition_bounds=bounds,excluded_condition=dict(index=3,name='taxis',reason='official heldout stimulus condition deliberately excluded: endpoint is same-condition temporal forecasting only'),shapes={k:list(v.shape) for k,v in arrays.items()},raw_subset_bytes=(CACHE/'raw/traces-selected.npy').stat().st_size,raw_subset_sha256=sha(CACHE/'raw/traces-selected.npy'),prepared_bytes=(CACHE/'data.npz').stat().st_size,prepared_sha256=sha(CACHE/'data.npz'))
 (Path(__file__).parent/'data-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
 return manifest

def load():
 with np.load(CACHE/'data.npz',allow_pickle=False) as z:return tuple(z[k] for k in ['train_x','train_y','test_x','test_y'])

def baseline(train_x,train_y,test_x):
 """Shared temporal NLinear map; fixed ridge1; fits training only.
 Same affine/last-observation-normalized architecture as official NLinear,
 solved analytically with ridge rather than reproducing its JAX optimization.
 """
 x=np.asarray(train_x,dtype=np.float64);y=np.asarray(train_y,dtype=np.float64);q=np.asarray(test_x,dtype=np.float64)
 last=x[:,-1:,:];a=(x-last).transpose(0,2,1).reshape(-1,x.shape[1]);b=(y-last).transpose(0,2,1).reshape(-1,y.shape[1])
 am=a.mean(0);bm=b.mean(0);a-=am;b-=bm
 w=np.linalg.solve(a.T@a+np.eye(a.shape[1]),a.T@b)
 z=(q-q[:,-1:,:]).transpose(0,2,1).reshape(-1,q.shape[1]);out=(z-am)@w+bm
 return out.reshape(len(q),q.shape[2],y.shape[1]).transpose(0,2,1)+q[:,-1:,:]

def mean_reference(train_x,train_y,test_x):
 return np.repeat(np.asarray(test_x).mean(axis=1,keepdims=True),HORIZON,axis=1)

def score(predictions,truth,test_x=None):
 p=np.asarray(predictions,dtype=np.float64);y=np.asarray(truth,dtype=np.float64)
 if p.shape!=y.shape or y.ndim!=3 or not np.isfinite(p).all() or not np.isfinite(y).all():raise ValueError('Expected finite forecast array matching truth (N,32,256)')
 per=np.mean((p-y)**2,axis=(1,2))
 return dict(score=float(per.mean()),metric='mse_dff',direction='lower',per_unit=per.tolist())

if __name__=='__main__':print(json.dumps(prepare(),indent=2))
