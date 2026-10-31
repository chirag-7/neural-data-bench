"""Same E06 frozen program, unseen-stimulus taxis slice, no new generation."""
from pathlib import Path
import importlib.util,json
import numpy as np
ROOT=Path(__file__).resolve().parents[4]
CACHE=ROOT/'data/cache/E06-taxis'
def original():
 s=importlib.util.spec_from_file_location('e06_parent',ROOT/'experiments/E06/adapter.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def prepare():
 m=original();a=np.load(m.CACHE/'raw/traces-selected.npy',allow_pickle=False);lo=m.OFFSETS[3]+1;hi=m.OFFSETS[4]-1
 starts=np.arange(lo+256,hi-32+1,32,dtype=int)
 with np.load(m.CACHE/'data.npz',allow_pickle=False) as z:
  arrays={k:z[k] for k in ['train_x','train_y','train_groups','train_target_starts','neuron_indices']}
 arrays.update(test_x=np.stack([a[t-64:t] for t in starts]),test_y=np.stack([a[t:t+32] for t in starts]),test_groups=np.full(len(starts),3,dtype=int),test_target_starts=starts)
 np.savez_compressed(CACHE/'data.npz',**arrays)
 manifest=dict(benchmark_id='E06',slice_id='taxis',status='prepared; parent freeze pending',same_program_as='E06',shared_source_dependence='Same animal/session, fixed neurons and same training arrays; distinct heldout stimulus condition3',official_holdout_bounds=[lo,hi],first_target=int(starts[0]),context=64,horizon=32,official_max_context_padding=256,test_stride=32,test_targets=starts.tolist(),shapes={k:list(v.shape) for k,v in arrays.items()},prepared_sha256=m.sha(CACHE/'data.npz'),parent_data_sha256=m.sha(m.CACHE/'data.npz'),raw_subset_sha256=m.sha(m.CACHE/'raw/traces-selected.npy'))
 (Path(__file__).parent/'data-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');return manifest
def load():
 with np.load(CACHE/'data.npz',allow_pickle=False) as z:return tuple(z[k] for k in ['train_x','train_y','test_x','test_y'])
def baseline(train_x,train_y,test_x):return original().baseline(train_x,train_y,test_x)
def score(predictions,truth,test_x=None):return original().score(predictions,truth,test_x)
if __name__=='__main__':print(json.dumps(prepare(),indent=2))
