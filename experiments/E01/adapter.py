"""MC Maze Small, official neuron/trial split, 20ms population rate diagnostic."""
from pathlib import Path
import hashlib,json,sys,urllib.request
import numpy as np
REPO=Path(__file__).resolve().parents[2]
CACHE=REPO/'data/cache/E01'
PIN='42f8410b88e12db136910fa2f888b025ea0aa2ae'
FILES={
 'train.nwb':'https://api.dandiarchive.org/api/assets/7821971e-c6a4-4568-8773-1bfa205c13f8/download/',
 'test.nwb':'https://api.dandiarchive.org/api/assets/544a660e-a173-46f3-985a-60fd67e6ae1f/download/',
 'eval_data_test.h5':f'https://media.githubusercontent.com/media/neurallatents/nlb_tools/{PIN}/data/eval_data_test.h5'}

EXPECTED_SHA256={'train.nwb': 'dcaf3a524e2b2f65f163ee3b07789b8474bdfc6ca66098bc542ab93dff489884', 'test.nwb': 'ca8a0bef5f189eafb9db1961d617e065cb461360718fde1c16a538922a6fa5fe', 'eval_data_test.h5': 'f2f434d30193251b58e6a693381fdd185c8fbc0e47d38f8810e65295bc42c865'}

def sha256(path):
 h=hashlib.sha256()
 with open(path,'rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()

def prepare():
 import h5py
 sys.path.insert(0,str(Path(__file__).parent/'vendor'))
 from nlb_tools.nwb_interface import NWBDataset
 from nlb_tools.make_tensors import make_train_input_tensors,make_eval_input_tensors
 (CACHE/'raw').mkdir(parents=True,exist_ok=True)
 raw_manifest=[]
 for name,url in FILES.items():
  path=CACHE/'raw'/name
  if not path.exists():
   with urllib.request.urlopen(url,timeout=180) as r:path.write_bytes(r.read())
  assert sha256(path)==EXPECTED_SHA256[name], 'Raw file checksum mismatch: '+name
  raw_manifest.append({'file':name,'url':url,'bytes':path.stat().st_size,'sha256':sha256(path)})
 dataset=NWBDataset(str(CACHE/'raw'))
 dataset.resample(20)
 train=make_train_input_tensors(dataset,'mc_maze_small',trial_split=['train','val'],save_file=False)
 test=make_eval_input_tensors(dataset,'mc_maze_small',trial_split='test',save_file=False)
 with h5py.File(CACHE/'raw/eval_data_test.h5') as f:
  truth=f['mc_maze_small_20/eval_spikes_heldout'][:].astype(np.float32)
 arrays={'train_x':train['train_spikes_heldin'].astype(np.float32),'train_y':train['train_spikes_heldout'].astype(np.float32),'test_x':test['eval_spikes_heldin'].astype(np.float32),'test_y':truth}
 mask=dataset.trial_info['split'].isin(['train','val'])
 td=dataset.make_trial_data(align_field='move_onset_time',align_range=(-250,450),ignored_trials=~mask)
 train_ids=td.trial_id.unique().astype(int)
 test_ids=dataset.trial_info.loc[dataset.trial_info['split']=='test','trial_id'].to_numpy().astype(int)
 arrays.update({'train_groups':train_ids,'test_groups':test_ids,'train_units':np.array(['Jenkins_small_trial'+str(i) for i in train_ids]),'test_units':np.array(['Jenkins_small_trial'+str(i) for i in test_ids])})
 assert arrays['train_x'].shape==(99,35,107)
 assert arrays['train_y'].shape==(99,35,35)
 assert arrays['test_x'].shape==(100,35,107) and arrays['test_y'].shape==(100,35,35)
 assert all(np.isfinite(arrays[k]).all() and (arrays[k]>=0).all() for k in ['train_x','train_y','test_x','test_y'])
 assert not set(train_ids)&set(test_ids)
 np.savez_compressed(CACHE/'data.npz',**arrays)
 record={'dandiset':'000140','version':'0.220113.0408','nlb_tools_commit':PIN,'official_lfs_sha256':EXPECTED_SHA256['eval_data_test.h5'],'bin_width_ms':20,'align_field':'move_onset_time','align_range_ms':[-250,450],'training_splits_combined':['train','val'],'requested_training_trials':100,'retained_training_trials':len(train_ids),'excluded_training_trial_ids':sorted(set(dataset.trial_info.loc[mask,'trial_id'])-set(train_ids)),'exclusion_reason':'Official make_trial_data allow_nans=False produces no valid aligned timepoints for final training trial199; retained trial IDs recorded. No target-based selection.','test_trials':100,'heldin_neurons':107,'heldout_neurons':35,'raw_files':raw_manifest,'shapes':{k:list(v.shape) for k,v in arrays.items()},'prepared_sha256':sha256(CACHE/'data.npz')}
 (Path(__file__).parent/'data-manifest.json').write_text(json.dumps(record,indent=2)+'\n')
 return record

def load():
 with np.load(CACHE/'data.npz') as z:return tuple(z[k] for k in ['train_x','train_y','test_x','test_y'])

def baseline(train_x,train_y,test_x):
 """Gaussian-smoothed population readout with fixed ridge penalty, not SOTA."""
 from scipy.ndimage import gaussian_filter1d
 from sklearn.linear_model import Ridge
 a=gaussian_filter1d(np.asarray(train_x,dtype=float),sigma=1,axis=1,mode='nearest')
 b=gaussian_filter1d(np.asarray(test_x,dtype=float),sigma=1,axis=1,mode='nearest')
 model=Ridge(alpha=100.0)
 model.fit(a.reshape(-1,a.shape[-1]),np.asarray(train_y).reshape(-1,train_y.shape[-1]))
 pred=model.predict(b.reshape(-1,b.shape[-1])).reshape(b.shape[:2]+(train_y.shape[-1],))
 return np.maximum(pred,1e-6)

def score(predictions,spikes):
 """Exact NLB bits/spike metric. Null mean uses evaluation truth for normalization only."""
 from scipy.special import gammaln
 p=np.asarray(predictions,dtype=np.float64).copy(); y=np.asarray(spikes,dtype=np.float64)
 assert p.shape==y.shape and np.isfinite(p).all() and (p>=0).all()
 p[p==0]=1e-9
 null=np.broadcast_to(np.nanmean(y,axis=(0,1),keepdims=True),y.shape).copy();null[null==0]=1e-9
 nll=lambda a:np.nansum(a-y*np.log(a)+gammaln(y+1))
 return float((nll(null)-nll(p))/np.nansum(y)/np.log(2))

if __name__=='__main__':print(json.dumps(prepare(),indent=2))
