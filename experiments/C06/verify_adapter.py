"""Validate preparation without running or scoring any candidate method."""
from pathlib import Path
import ast,importlib.util,json
import numpy as np
from scipy.io import loadmat
from scipy.ndimage import gaussian_filter1d
P=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('c06adapter',P/'adapter.py')
a=importlib.util.module_from_spec(spec);spec.loader.exec_module(a)

def verify():
 manifest=json.loads((P/'data-manifest.json').read_text())
 a.acquire() # Recheck every byte count, SHA1 Git blob, and current local SHA256.
 assert a.digest(a.CACHE/'data.npz')==manifest['data_sha256']
 # Use the unmodified publisher function to cross-check MAT interpretation.
 source=P/'source/utils.py';tree=ast.parse(source.read_text())
 node=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='load_recordings_from_file')
 ns={'np':np,'sio':__import__('scipy.io',fromlist=['loadmat'])}
 exec(compile(ast.Module(body=[node],type_ignores=[]),str(source),'exec'),ns)
 original=ns[node.name]
 with np.load(a.CACHE/'data.npz') as z:
  assert z['train_x'].shape==(21,3,900) and z['test_x'].shape==(24,3,900)
  assert set(z['train_cells']).isdisjoint(z['test_cells'])
  assert set(z['train_groups']).isdisjoint(z['test_groups'])
  for row in manifest['recordings']:
   split=row['split'];i=row['row'];n=row['n'];name=row['cell']+'.mat'
   r=original(str(a.CACHE/'raw'/name))[row['recording']]
   assert np.allclose(z[split+'_x'][i,0,:n],r['dff'])
   assert z[split+'_x'][i,1].sum()==n
   assert np.all(z[split+'_y'][i,n:]==-1)
   assert np.all(z[split+'_x'][i,:,n:]==0)
   t=r['t'];dt=row['dt'];edges=np.r_[t[0]-dt/2,(t[1:]+t[:-1])/2,t[-1]+dt/2]
   # Independent searchsorted/bincount route, including histogram's final edge.
   events=r['spikes'];events=events[(events>=edges[0])&(events<=edges[-1])]
   indices=np.minimum(np.searchsorted(edges,events,side='right')-1,n-1)
   assert np.array_equal(np.bincount(indices,minlength=n),z[split+'_counts'][i,:n])
   assert int(z[split+'_counts'][i,:n].sum())==row['spikes_in_frame_support']
   expected=gaussian_filter1d(z[split+'_counts'][i,:n].astype(float),.2/row['dt'],mode='reflect')
   assert np.allclose(expected,z[split+'_y'][i,:n])
   assert np.isclose(expected.sum(),row['spikes_in_frame_support'])
 # Synthetic fixtures only: two neurons in A score 1, one neuron in B scores 0.
 # Equal animals must yield .5, distinct from neuron-pooled 2/3.
 toy_truth=np.array([[0.,1.,2.,-1.],[0.,2.,4.,-1.],[0.,1.,2.,-1.]])
 toy_pred=np.array([[0.,1.,2.,999.],[0.,2.,4.,999.],[1.,1.,1.,999.]])
 toy=a._score_groups(toy_pred,toy_truth,np.array(['a','b','c']),np.array(['A','A','B']))
 assert np.isclose(toy['score'],.5) and len(toy['per_unit'])==3
 result=dict(status='passed',raw_files=15,recordings=45,all_publisher_traces_match=True,
  train_test_neurons_and_specimens_disjoint=True,all_histogram_and_smoothing_checks_pass=True,
  synthetic_grouped_scorer_checks_pass=True,method_execution=False,real_slice_method_scores=False,data_sha256=manifest['data_sha256'])
 (P/'validation.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
if __name__=='__main__':verify()
