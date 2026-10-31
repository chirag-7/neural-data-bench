"""Subject-disjoint P300 target ranking, Brain Invaders 2012 v3, CC BY4.0."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import hashlib,io,json,urllib.request,zipfile
import numpy as np
from scipy.io import loadmat
from scipy.signal import butter,sosfiltfilt
R=Path(__file__).resolve().parents[2];D=R/'experiments/H02';C=R/'data/cache/H02'
CHANNELS=['F7','F3','Fz','F4','F8','T7','C3','Cz','C4','T8','P7','P3','Pz','P4','P8','O1','O2']
KEEP=[i for i,n in enumerate(CHANNELS) if n!='Fz']
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def acquire(item):
 p=C/'raw'/item['name'];p.parent.mkdir(parents=True,exist_ok=True)
 if not p.exists():
  temp=p.with_suffix('.partial')
  with urllib.request.urlopen(item['url'],timeout=120) as response:temp.write_bytes(response.read())
  temp.replace(p)
 assert p.stat().st_size==item['size'] and 'md5:'+hashlib.md5(p.read_bytes()).hexdigest()==item['checksum']
 return p

def prepare():
 source=json.loads((D/'source-record.json').read_text());assert source['license']['id']=='cc-by-4.0'
 items=sorted(source['files'],key=lambda v:v['name']);assert len(items)==25
 with ThreadPoolExecutor(max_workers=4) as pool:paths=list(pool.map(acquire,items))
 arrays={k:[] for k in ['train_x','train_y','test_x','test_y','train_groups','test_groups']};manifest=[];epochs=[];checks=[]
 sos=butter(4,[.5,20],fs=128,btype='bandpass',output='sos')
 for item,p in zip(items,paths):
  subject=int(p.stem.split('_')[-1]);split='train' if subject<=15 else 'test'
  with zipfile.ZipFile(p) as z:
   member=f'subject_{subject:02d}/training.mat';b=z.read(member);csv=z.read(f'subject_{subject:02d}/training.csv');a=loadmat(io.BytesIO(b))['training'];other=np.loadtxt(io.BytesIO(csv),delimiter=',',usecols=[0,18,19])
  assert a.ndim==2 and a.shape[1]==20 and np.isfinite(a).all()
  assert np.allclose(np.diff(a[:,0]),1/128,rtol=0,atol=1e-10)
  assert other.shape==(len(a),3) and np.array_equal(other[:,1:],a[:,18:20]);assert np.max(np.abs(other[:,0]-a[:,0]))<.01
  assert np.isin(a[:,18:20],[0.,1.]).all() and np.all(a[:,19]<=a[:,18])
  events=np.flatnonzero(a[:,18]);assert np.diff(events).min()>1
  x=a[:,1:18].T[KEEP].copy();x-=x.mean(axis=0,keepdims=True);x=sosfiltfilt(sos,x,axis=-1)
  retained=[];skipped=[]
  for event,e in enumerate(events):
   if e<26 or e+128>len(a):skipped.append(int(e));continue
   epoch=x[:,e:e+128]-x[:,e-26:e].mean(axis=-1,keepdims=True);assert epoch.shape==(16,128) and np.isfinite(epoch).all()
   label=int(a[e,19]);arrays[split+'_x'].append(epoch.astype(np.float32));arrays[split+'_y'].append(label);arrays[split+'_groups'].append(subject);retained.append(int(e));epochs.append(dict(subject=subject,split=split,event_sample=int(e),label=label))
  y=np.array([q['label'] for q in epochs if q['subject']==subject]);assert set(y)=={0,1}
  checks.append(dict(subject=subject,n_source_flash_events=len(events),n_retained=len(retained),n_targets=int(y.sum()),n_nontargets=int((y==0).sum()),geometry_skipped=skipped,mat_csv_marker_equivalence=True,mat_csv_max_timestamp_difference=float(np.max(np.abs(other[:,0]-a[:,0])))))
  manifest.append(dict(subject=subject,path=str(p.relative_to(R)),url=item['url'],bytes=p.stat().st_size,publisher_md5=item['checksum'],publisher_md5_verified=True,sha256=sha(p),training_member=member,training_member_sha256=hashlib.sha256(b).hexdigest()))
  print('Prepared H02 subject',subject,len(retained),flush=True)
 arrays={k:np.asarray(v) for k,v in arrays.items()};assert not set(arrays['train_groups'])&set(arrays['test_groups']);np.savez_compressed(C/'data.npz',**arrays)
 meta=dict(benchmark_id='H02',dataset='Brain Invaders 2012',version='v3 / Zenodo2649069',license='CC BY4.0',primary_metric='subject_equal_roc_auc',direction='higher',sampling_rate_hz=128,units='microvolts per original author/MOABB convention',channels=[CHANNELS[i] for i in KEEP],train_subjects=list(range(1,16)),test_subjects=list(range(16,26)),train_shape=list(arrays['train_x'].shape),test_shape=list(arrays['test_x'].shape),train_groups=arrays['train_groups'].tolist(),test_groups=arrays['test_groups'].tolist(),primary_aggregation='Mean of10 held-out subject ROC-AUCs; binary target1/nontarget0',baseline_name='Fixed16time-bin shrinkage LDA',truth_type='experimentally recorded target/nontarget flash markers',input='float32(trials,16 EEGchannels,128samples),0–1s afterflash; baseline prior26samples; common-average and0.5–20Hz zero-phase filtering within each calibration run',adaptation='No fitting any transform or threshold on held-out test input; within-epoch baseline/CAR fixed preprocessing only')
 (C/'metadata.json').write_text(json.dumps(meta,indent=2)+'\n');(D/'preparation-verification.json').write_text(json.dumps(dict(subjects=checks,channel_order_matches_pinned_author_loader=True,removed_ground_channel='Fz',no_amplitude_or_label_dependent_trial_exclusion=True,mat_csv_event_and_target_equivalence_all25=True,train_test_subjects_disjoint=True,n_train=len(arrays['train_x']),n_test=len(arrays['test_x']),data_sha256=sha(C/'data.npz')),indent=2)+'\n');(D/'trial-manifest.json').write_text(json.dumps(epochs,separators=(',',':'))+'\n');(R/'data/manifests/H02.json').write_text(json.dumps(dict(benchmark_id='H02',source=source['url'],license='CC BY4.0',files=manifest,prepared_file='data/cache/H02/data.npz',prepared_sha256=sha(C/'data.npz')),indent=2)+'\n');return meta

def load():
 with np.load(C/'data.npz') as z:return tuple(z[k] for k in ['train_x','train_y','test_x','test_y'])
def train_groups():
 with np.load(C/'data.npz') as z:return z['train_groups']
def baseline(x,y,xt,groups):
 from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
 a=x.reshape(len(x),16,16,8).mean(axis=-1).reshape(len(x),-1);b=xt.reshape(len(xt),16,16,8).mean(axis=-1).reshape(len(xt),-1)
 return LinearDiscriminantAnalysis(solver='lsqr',shrinkage='auto').fit(a,y).decision_function(b)
def score(pred,truth,test_x=None):
 from sklearn.metrics import roc_auc_score
 pred=np.asarray(pred);assert pred.shape==truth.shape and np.isfinite(pred).all()
 with np.load(C/'data.npz') as z:groups=z['test_groups']
 assert len(groups)==len(truth);values=[dict(group=str(g),n=int((groups==g).sum()),score=float(roc_auc_score(truth[groups==g],pred[groups==g])),metric='roc_auc') for g in np.unique(groups)]
 return dict(score=float(np.mean([v['score'] for v in values])),metric='subject_equal_roc_auc',direction='higher',pooled_roc_auc=float(roc_auc_score(truth,pred)),per_unit=[v['score'] for v in values],group_results=values)
if __name__=='__main__':print(json.dumps(prepare(),default=lambda x:None)[:1500])
