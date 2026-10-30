"""Validate scorer equivalence and archived-score agreement, not model accuracy."""
from pathlib import Path
import ast, importlib.util, json
import numpy as np
import pandas as pd

HERE=Path(__file__).resolve().parent
DATA=HERE.parents[1]/'work/spikefinder/reference'
spec=importlib.util.spec_from_file_location('pilot',HERE/'evaluate.py')
pilot=importlib.util.module_from_spec(spec);spec.loader.exec_module(pilot)
tree=ast.parse((DATA/'spikefinder_eval.py').read_text())
nodes=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ['_downsample','_corr']]
namespace=dict(np.__dict__)
exec(compile(ast.Module(body=nodes,type_ignores=[]),'official_scorer_functions','exec'),namespace)
truth=pd.read_csv(DATA/'truth.test.spikes.csv')
pred=pd.read_csv(DATA/'deneux.test.spikes.csv')
reference=[]
for c in truth:
    mask=truth[c].notna() & pred[c].notna()
    x=namespace['_downsample'](pred.loc[mask,c],4)
    y=namespace['_downsample'](truth.loc[mask,c],4)
    reference.append(float(namespace['_corr'](x,y)))
ours=pilot.score(pred.to_numpy(),truth.to_numpy())['per_neuron']
assert np.allclose(reference,ours,rtol=0,atol=1e-12)
archive=pd.read_csv(DATA/'results_30_06_17.csv')
rows=archive[(archive.algo=='deneux')&(archive.dset==1)&(archive.split=='test')&(archive.measure=='corr')].sort_values('cell')
assert np.allclose(ours,rows.value.to_numpy(),rtol=0,atol=1e-10)
assert np.isclose(pilot.score(truth.to_numpy(),truth.to_numpy())['mean'],1)
assert np.isclose(pilot.score(2*truth.to_numpy()+3,truth.to_numpy())['mean'],1)
assert pilot.score(np.zeros_like(truth.to_numpy()),truth.to_numpy())['mean']==0
print(json.dumps({'official_function_equivalence':'passed','published_archived_per_neuron_agreement':'passed','identity_and_positive_affine_invariance':'passed','constant_prediction_convention':'zero correlation','absolute_tolerance':1e-10,'deneux_scores':ours},indent=2))
