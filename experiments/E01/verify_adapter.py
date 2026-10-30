import sys,json,importlib.util
from pathlib import Path
import numpy as np,h5py
P=Path(__file__).resolve().parent
sys.path.insert(0,str(P/'vendor'))
from nlb_tools.evaluation import bits_per_spike
spec=importlib.util.spec_from_file_location('e01_adapter',P/'adapter.py');a=importlib.util.module_from_spec(spec);spec.loader.exec_module(a)
train_x,train_y,test_x,test_y=a.load()
null=np.broadcast_to(test_y.mean(axis=(0,1),keepdims=True),test_y.shape).astype(float).copy()
random=np.random.default_rng(1717).uniform(.01,1.,size=test_y.shape)
checks=[]
for name,pred in [('evaluation_mean',null),('fixed_random',random)]:
 ours=a.score(pred,test_y);official=bits_per_spike(pred.copy(),test_y.astype(float))
 assert abs(ours-official)<1e-12
 checks.append({'case':name,'ours':ours,'official':float(official),'absolute_difference':abs(ours-official)})
# Independent count extraction from raw NWB HDF5, without official NWB loader.
with h5py.File(a.CACHE/'raw/test.nwb') as f:
 times=f['units/spike_times'][:];ends=f['units/spike_times_index'][:];ids=f['units/id'][:]
 onsets=f['intervals/trials/move_onset_time'][:]
 assert np.array_equal(f['intervals/trials/id'][:],np.arange(100))
 assert not f['units/heldout'][:].any()
 direct=np.zeros_like(test_x)
 previous=0
 for neuron,end in enumerate(ends):
  spikes_ms=np.round(times[previous:end]*1000,6).astype(int);previous=end
  for trial,onset in enumerate(onsets):
   left=int(np.ceil(np.round((onset-.250)*1000,6)/20)*20)
   relevant=spikes_ms[(spikes_ms>=left)&(spikes_ms<left+700)]
   direct[trial,:,neuron]=np.bincount((relevant-left)//20,minlength=35)
 assert np.array_equal(direct,test_x)
 assert test_y.shape==(len(onsets),35,35)
 try:a.score(-np.ones_like(test_y),test_y);raise RuntimeError('negativepassed')
 except AssertionError:pass
 result={'scorer_cases':checks,'raw_input_count_check':'Independent raw HDF5 spike-time extraction, integer1ms truncation and20ms aggregation EXACTLY equals all100×35×107 official testinput counts. Confirms trialorder, neuronorder and bin alignment. Test targets loaded directly from same named official release group.','independent_testinput_equal':True,'test_input_shape':list(test_x.shape),'test_target_shape':list(test_y.shape),'test_finite':bool(np.isfinite(test_y).all()),'negative_predictions_rejected':True,'discarded_validation_attempt':'Forecast groundtruth cannot be equality-checked against testNWB because future spikes are intentionally omitted and trialtime compressed; an initial comparison was invalid and is not used as a gate. No input/target arrays changed in response.'}
(P/'validation.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
