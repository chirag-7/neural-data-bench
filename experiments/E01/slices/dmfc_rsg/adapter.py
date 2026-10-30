"""Frozen-program portability slice; no changes to original E01 programs."""
from pathlib import Path
import importlib.util
import numpy as np
P=Path(__file__).resolve().parent
REPO=P.parents[3]
CACHE=REPO/'data/cache/E01-dmfc_rsg'

def prepare():
 spec=importlib.util.spec_from_file_location('nlb_slice_preparation',P.parent/'prep_common.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
 return m.prepare('dmfc_rsg')

def load():
 with np.load(CACHE/'data.npz') as z:return tuple(z[k] for k in ['train_x','train_y','test_x','test_y'])

def _original_adapter():
 path=REPO/'experiments/E01/adapter.py'
 spec=importlib.util.spec_from_file_location('unchanged_e01_reference',path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
 return m

def baseline(train_x,train_y,test_x):return _original_adapter().baseline(train_x,train_y,test_x)
def score(predictions,spikes):return _original_adapter().score(predictions,spikes)
if __name__=='__main__':
 import json
 print(json.dumps(prepare(),indent=2))
