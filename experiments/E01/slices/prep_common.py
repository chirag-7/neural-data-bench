"""Preparation only: new official NLB sources for unchanged-program portability.

Does not import, generate or execute evaluated-model programs.
"""
from pathlib import Path
import hashlib,importlib.util,json,sys,urllib.request
import numpy as np
ROOT=Path(__file__).resolve().parents[3]
P=Path(__file__).resolve().parent
VENDOR=ROOT/'experiments/E01/vendor'
sys.path.insert(0,str(VENDOR))
CONFIG={
 'area2_bump':{'dandiset':'000127','version':'0.220113.0359','subject':'Han','session_date':'2017-12-07','task':'Center-out reaching with externally applied arm perturbations; area2 somatosensory cortex','train_asset':'ded26b6c-418d-43f5-8a37-dfd072c2dbd4','test_asset':'f907b288-a9b4-4c6e-9d66-6812f306e253','test_bytes':492576,'train_bytes':1822876234,'test_shape':[98,30,16],'heldin':49,'heldout':16},
 'dmfc_rsg':{'dandiset':'000130','version':'0.241017.1448','subject':'Haydn','session_date':'2016-12-11','task':'Ready-set-go time interval reproduction; dorsomedial frontal cortex','train_asset':'c90cbccc-31a5-4815-88e6-822d8c5ca68c','test_asset':'a2c3ced1-2869-4483-aa19-8815c2d18c91','test_bytes':1553584,'train_bytes':14119912,'test_shape':[283,75,14],'heldin':40,'heldout':14}}

def digest(path):
 h=hashlib.sha256()
 with open(path,'rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()

def _dataset(source):
 import h5py
 from pynwb import NWBHDF5IO,TimeSeries
 from nlb_tools.nwb_interface import NWBDataset
 handle=h5py.File(source,'r');io=NWBHDF5IO(file=handle,mode='r',load_namespaces=True);nwb=io.read()
 skip=[]
 for obj in nwb.objects.values():
  if isinstance(obj,TimeSeries):
   skip.append(obj.name)
   if obj.parent is not None:skip.append(obj.parent.name+'_'+obj.name)
 dataset=NWBDataset(nwb,skip_fields=skip)
 return dataset,handle,io,skip

def prepare(name):
 import h5py
 from nlb_tools.make_tensors import make_train_input_tensors,make_eval_input_tensors
 cfg=CONFIG[name];cache=ROOT/('data/cache/E01-'+name);out=P/name;(cache/'raw').mkdir(parents=True,exist_ok=True)
 train_path=cache/'raw/train.nwb';test_path=cache/'raw/test.nwb'
 train_url='https://api.dandiarchive.org/api/assets/'+cfg['train_asset']+'/download/'
 test_url='https://api.dandiarchive.org/api/assets/'+cfg['test_asset']+'/download/'
 range_reader=None
 def acquire(url,path,nbytes):
  if not path.exists():
   with urllib.request.urlopen(url,timeout=120) as response,path.open('wb') as target:
    import shutil
    shutil.copyfileobj(response,target)
  assert path.stat().st_size==nbytes
 acquire(test_url,test_path,cfg['test_bytes'])
 if name!='area2_bump':acquire(train_url,train_path,cfg['train_bytes'])
 if name=='area2_bump':
  spec=importlib.util.spec_from_file_location('nlb_range',P/'range_reader.py');r=importlib.util.module_from_spec(spec);spec.loader.exec_module(r)
  range_reader=r.RangeReader(train_url,cfg['train_bytes'],cache/'raw/train-range-blocks')
  source=range_reader
 else:source=str(train_path)
 train,train_h,train_io,train_skip=_dataset(source)
 test,test_h,test_io,test_skip=_dataset(str(test_path))
 train.resample(20);test.resample(20)
 # Train and test are parsed separately with official NWBDataset support for NWBFile objects.
 # No artificial concatenation/time shifts; identical20ms origin in original files.
 a=make_train_input_tensors(train,name,trial_split=['train','val'],save_file=False,seed=0)
 b=make_eval_input_tensors(test,name,trial_split='test',save_file=False,seed=0)
 train_x=a['train_spikes_heldin'].astype(np.float32);train_y=a['train_spikes_heldout'].astype(np.float32)
 official_x=b['eval_spikes_heldin'].astype(np.float32)
 shared=ROOT/'data/cache/E01/raw/eval_data_test.h5'
 assert digest(shared)=='f2f434d30193251b58e6a693381fdd185c8fbc0e47d38f8810e65295bc42c865'
 with h5py.File(shared) as f:truth=f[name+'_20/eval_spikes_heldout'][:].astype(np.float32)
 assert list(truth.shape)==cfg['test_shape'] and official_x.shape[:2]==truth.shape[:2]
 assert train_x.shape[-1]==official_x.shape[-1]==cfg['heldin']
 assert train_y.shape[-1]==truth.shape[-1]==cfg['heldout']
 good=np.isfinite(train_x).all(axis=(1,2))&np.isfinite(train_y).all(axis=(1,2))
 assert good.all(),'Do not silently remove or repair incomplete training counts; examine source protocol first'
 observed=np.isfinite(official_x).all(axis=-1)
 assert np.all(np.isfinite(official_x)==observed[...,None]),'Mixed-neuron missingness incompatible with structural padding'
 assert observed.all(),'Official fixed-context input must be fully observed; do not fill NaNs'
 target_observed=np.isfinite(truth).all(axis=-1)
 assert np.all(np.isfinite(truth)==target_observed[...,None])
 if name=='dmfc_rsg':
  assert all(np.array_equal(np.flatnonzero(row),np.arange(np.flatnonzero(row)[0],np.flatnonzero(row)[-1]+1)) for row in target_observed),'Official target valid mask must be contiguous per trial'
 else:assert target_observed.all()
 test_x=official_x.copy()
 assert np.array_equal(test_x[observed],official_x[observed])
 arrays={'train_x':train_x,'train_y':train_y,'test_x':test_x,'test_y':truth,'test_input_observed_mask':observed,'test_target_observed_mask':target_observed,'train_groups':np.array([cfg['subject']+'_'+cfg['session_date']]*len(train_x)),'test_groups':np.array([cfg['subject']+'_'+cfg['session_date']]*len(test_x)),'train_units':np.array([cfg['subject']+'_traintrial'+str(i) for i in train.trial_info.loc[train.trial_info['split'].isin(['train','val']),'trial_id'].tolist()]),'test_units':np.array([cfg['subject']+'_testtrial'+str(i) for i in test.trial_info.loc[test.trial_info['split']=='test','trial_id'].tolist()])}
 np.savez_compressed(cache/'data.npz',**arrays)
 manifest={'benchmark_id':'E01','slice_id':name,'source':cfg,'data_license':'CC BY4.0 as confirmed in source-record.json','nlb_tools_commit':'42f8410b88e12db136910fa2f888b025ea0aa2ae','bin_width_ms':20,'official_train_tensor_seed':0,'train_splits_combined':['train','val'],'skipped_behavior_fields':{'train':train_skip,'test':test_skip},'shapes':{k:list(v.shape) for k,v in arrays.items()},'train_requested_splits':train.trial_info['split'].value_counts().to_dict(),'test_requested_splits':test.trial_info['split'].value_counts().to_dict(),'train_file':{'url':train_url,'sha256':digest(train_path) if name!='area2_bump' else None,'range_read':range_reader.manifest() if range_reader else None},'test_file':{'url':test_url,'sha256':digest(test_path)},'shared_groundtruth_file':'data/cache/E01/raw/eval_data_test.h5','shared_groundtruth_sha256':digest(shared),'target_group':name+'_20/eval_spikes_heldout','observed_input_bins_per_trial':observed.sum(axis=1).tolist(),'test_input_padding_bins':int((~observed).sum()),'test_target_unscored_bins':int((~target_observed).sum()),'target_scored_bins_per_trial':target_observed.sum(axis=1).tolist(),'target_mask_unmodified':True,'padding_policy':'All official fixed75bin input values retained; target-only jittered variable-window NaNmask from official archive unchanged' if name=='dmfc_rsg' else 'No missing input or target values; no padding replacement','prepared_sha256':digest(cache/'data.npz'),'array_sha256':{k:hashlib.sha256(np.ascontiguousarray(arrays[k]).tobytes()).hexdigest() for k in ['train_x','train_y','test_x','test_y']},'general_model_calls':0,'frozen_base_E01_programs_modified':False}
 (out/'data-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
 # Keep source datasets available only for optional caller diagnostics; prepared arrays are independent copies.
 train_io.close();test_io.close();train_h.close();test_h.close()
 return manifest
