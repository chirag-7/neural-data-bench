"""Independent raw-input reconstruction and official scorer parity; no model calls."""
from pathlib import Path
import hashlib,importlib.util,json,sys
import h5py,numpy as np
P=Path(__file__).resolve().parent
sys.path.insert(0,str(P.parent/'vendor'))
from nlb_tools.evaluation import bits_per_spike

def verify(name):
 spec=importlib.util.spec_from_file_location(name,P/name/'adapter.py');a=importlib.util.module_from_spec(spec);spec.loader.exec_module(a)
 tx,ty,x,y=a.load();checks=[]
 for arr in (tx,ty,x,y):
  v=arr[np.isfinite(arr)];assert (v>=0).all() and np.equal(v,np.round(v)).all()
 for label,pred in [('evaluation_mean',np.broadcast_to(np.nanmean(y,axis=(0,1),keepdims=True),y.shape).astype(float).copy()),('fixed_random',np.random.default_rng(1717).uniform(.01,1.,size=y.shape))]:
  ours=a.score(pred,y);official=float(bits_per_spike(pred.copy(),y.astype(float)))
  assert abs(ours-official)<1e-12
  checks.append({'case':label,'ours':ours,'official':official,'absolute_difference':abs(ours-official)})
 with h5py.File(a.CACHE/'raw/test.nwb') as f:
  times=f['units/spike_times'][:];ends=f['units/spike_times_index'][:];ids=f['units/id'][:]
  field='move_onset_time' if name=='area2_bump' else 'go_time';offset=.1 if name=='area2_bump' else 1.5
  onsets=f['intervals/trials/'+field][:];trials=f['intervals/trials/id'][:]
  assert not f['units/heldout'][:].any()
  direct=np.zeros_like(x);previous=0
  for neuron,end in enumerate(ends):
   spk=np.round(times[previous:end]*1000,6).astype(int);previous=end
   for trial,onset in enumerate(onsets):
    left=int(np.ceil(np.round((onset-offset)*1000,6)/20)*20)
    rel=spk[(spk>=left)&(spk<left+x.shape[1]*20)]
    direct[trial,:,neuron]=np.bincount((rel-left)//20,minlength=x.shape[1])
  assert np.array_equal(direct,x),'Independent raw spike counts must equal every input element'
  public_trial_fields=list(f['intervals/trials'])
 shared=a.REPO/'data/cache/E01/raw/eval_data_test.h5'
 with h5py.File(shared) as f:
  target=f[name+'_20/eval_spikes_heldout'][:]
  assert np.array_equal(y,target,equal_nan=True)
  aux={}
  if name=='dmfc_rsg':
   j=f['dmfc_rsg_20/eval_jitter'][:];m=np.isfinite(y).all(-1)
   aux={'official_hidden_jitter_bins':j.tolist(),'official_target_finite_bins':m.sum(1).tolist(),'target_mask_is_contiguous_per_trial':bool(all(np.array_equal(np.flatnonzero(row),np.arange(np.flatnonzero(row)[0],np.flatnonzero(row)[-1]+1)) for row in m)),'test_source_omits_set_time': 'set_time' not in public_trial_fields,'target_alignment_independent_raw_heldout_verification':'Impossible from public testNWB, which contains only held-in counts and packed go_time. Exact provided target array retained; no inferred unjittering/realignment.'}
 try:a.score(-np.ones_like(y),y);raise RuntimeError('negative predictions passed')
 except AssertionError:pass
 result={'slice':name,'scorer_cases':checks,'independent_testinput_count_equal':True,'independent_testinput_elements':int(x.size),'official_target_exact_equal_including_nan':True,'test_input_shape':list(x.shape),'test_target_shape':list(y.shape),'all_input_counts_finite':bool(np.isfinite(x).all()),'finite_target_entries':int(np.isfinite(y).sum()),'negative_predictions_rejected':True,'raw_neuron_ids':ids.tolist(),'raw_trial_ids':trials.tolist(),'public_test_trial_fields':public_trial_fields,**aux}
 (P/name/'validation.json').write_text(json.dumps(result,indent=2)+'\n');print(name,x.shape,y.shape,'PASS')
for name in ['area2_bump','dmfc_rsg']:verify(name)
