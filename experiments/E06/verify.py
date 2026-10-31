"""Independent exact source/split/scorer checks; no real method predictions."""
from pathlib import Path
import ast,hashlib,importlib.util,json,types
import numpy as np
P=Path(__file__).resolve().parent;ROOT=P.parents[1]
def load_module(path,name):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
m=load_module(P/'adapter.py','e06')
for item in json.loads((P/'source-checks.json').read_text())['files']:
 b=(P/item['file']).read_bytes();assert hashlib.sha256(b).hexdigest()==item['sha256'];assert hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()==item['git_blob_sha1']
# Execute only the two unchanged original pure splitting helpers.
source=ast.parse((P/'source-data_utils.py').read_text());nodes=[n for n in source.body if isinstance(n,ast.FunctionDef) and n.name in ['get_condition_bounds','adjust_condition_bounds_for_split']]
ns={'constants':types.SimpleNamespace(CONDITION_OFFSETS=m.OFFSETS,CONDITION_PADDING=1,TEST_FRACTION=.2,VAL_FRACTION=.1,MAX_CONTEXT_LENGTH=256)}
exec(compile(ast.Module(body=nodes,type_ignores=[]),'official_split','exec'),ns)
raw=np.load(m.CACHE/'raw/traces-selected.npy',allow_pickle=False)
report={}
for label,cache in [('parent',m.CACHE),('taxis',ROOT/'data/cache/E06-taxis')]:
 with np.load(cache/'data.npz',allow_pickle=False) as z:
  assert np.array_equal(z['neuron_indices'],m.IDS)
  for prefix in ['train','test']:
   starts=z[prefix+'_target_starts'];groups=z[prefix+'_groups']
   for j,(t,c) in enumerate(zip(starts,groups)):
    bounds=ns['get_condition_bounds'](int(c));split='train' if prefix=='train' else 'test_holdout' if label=='taxis' else 'test'
    lo,hi=ns['adjust_condition_bounds_for_split'](split,*bounds,64)
    assert t-64>=lo and t+32<=hi
    assert np.array_equal(z[prefix+'_x'][j],raw[t-64:t]);assert np.array_equal(z[prefix+'_y'][j],raw[t:t+32])
   if prefix=='test':
    for c in np.unique(groups):assert np.all(np.diff(starts[groups==c])==32)
  assert not (set(z['train_groups'])&{3});report[label]={k:list(z[k].shape) for k in ['train_x','train_y','test_x','test_y']}
with np.load(m.CACHE/'data.npz') as a,np.load(ROOT/'data/cache/E06-taxis/data.npz') as b:
 assert np.array_equal(a['train_x'],b['train_x']) and np.array_equal(a['train_y'],b['train_y'])
rng=np.random.default_rng(1);x=rng.normal(size=(5,64,3));y=rng.normal(size=(5,32,3));q=rng.normal(size=(2,64,3));pred=m.baseline(x,y,q);assert pred.shape==(2,32,3) and np.isfinite(pred).all()
assert m.score(np.ones((2,32,3)),np.zeros((2,32,3)))['score']==1
report.update(status='passed',official_source_blob_checks=True,all_windows_exact_raw_reconstruction=True,official_split_helpers_parity=True,toy_reference_and_scorer=True,no_real_method_scores=True)
(P/'validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
