"""Sleep-EDF first-night, participant-disjoint, fixed wall-clock overnight diagnostic."""
from pathlib import Path
import hashlib,json,urllib.request,re,concurrent.futures
import numpy as np
R=Path(__file__).resolve().parents[2];C=R/'data/cache/H08';BASE='https://physionet.org/files/sleep-edfx/1.0.0/'
PAIRS=[('SC4001E0-PSG.edf','SC4001EC-Hypnogram.edf'),('SC4011E0-PSG.edf','SC4011EH-Hypnogram.edf'),('SC4021E0-PSG.edf','SC4021EH-Hypnogram.edf'),('SC4031E0-PSG.edf','SC4031EC-Hypnogram.edf'),('SC4041E0-PSG.edf','SC4041EC-Hypnogram.edf'),('SC4051E0-PSG.edf','SC4051EC-Hypnogram.edf'),('SC4061E0-PSG.edf','SC4061EC-Hypnogram.edf'),('SC4071E0-PSG.edf','SC4071EC-Hypnogram.edf')]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def fetch(name):
 p=C/name;url=BASE+name
 if not p.exists():
  with urllib.request.urlopen(url,timeout=180) as stream,p.open('wb') as f:
   while b:=stream.read(1048576):f.write(b)
 return p,url
def prepare():
 import mne
 C.mkdir(exist_ok=True,parents=True);sumfile,_=fetch('SHA256SUMS.txt');sums={}
 for line in sumfile.read_text().splitlines():
  a=line.split(maxsplit=1)
  if len(a)==2:sums[a[1].lstrip('*')]=a[0]
 names=['sleep-cassette/'+n for pair in PAIRS for n in pair]
 for name in names:(C/name).parent.mkdir(exist_ok=True,parents=True)
 with concurrent.futures.ThreadPoolExecutor(max_workers=4) as ex:acquired=list(ex.map(fetch,names))
 manifest=[]
 for (p,url),name in zip(acquired,names):
  actual=sha(p);assert actual==sums[name],name;manifest.append(dict(path=str(p.relative_to(R)),url=url,bytes=p.stat().st_size,sha256=actual,publisher_sha256_match=True))
 xs=[];ys=[];slices=[];mapping={'Sleep stage W':0,'Sleep stage 1':1,'Sleep stage 2':2,'Sleep stage 3':3,'Sleep stage 4':3,'Sleep stage R':4}
 for subject,(signal,annotation) in enumerate(PAIRS):
  raw=mne.io.read_raw_edf(C/'sleep-cassette'/signal,include=['EEG Fpz-Cz'],preload=False,verbose='ERROR');ann=mne.read_annotations(C/'sleep-cassette'/annotation)
  assert raw.info['sfreq']==100.
  assert (C/'sleep-cassette'/signal).read_bytes()[168:184]==(C/'sleep-cassette'/annotation).read_bytes()[168:184], 'PSG/hypnogram EDF startdate/time mismatch'
  assert ann.orig_time is None or ann.orig_time==raw.info['meas_date']
  start=raw.info['meas_date'];seconds=start.hour*3600+start.minute*60+start.second;offset=(20*3600-seconds)%(24*3600);offset=int(np.ceil(offset/30)*30);assert (offset+43200)*100<=raw.n_times
  data=raw.get_data(start=offset*100,stop=(offset+43200)*100,units='uV')[0].astype(np.float32).reshape(1440,3000);labels=np.full(1440,-1,dtype=np.int64)
  for i in range(1440):
   lo=offset+30*i;hi=lo+30
   for onset,duration,description in zip(ann.onset,ann.duration,ann.description):
    if onset<=lo+1e-5 and onset+duration>=hi-1e-5:
     labels[i]=mapping.get(description,-1);break
  assert np.isfinite(data).all() and (labels>=0).sum()>1300
  xs.append(data);ys.append(labels);slices.append(dict(subject=subject,signal=signal,annotation=annotation,recording_start=start.isoformat(),offset_seconds=offset,window_start_clock=(start.hour*3600+start.minute*60+start.second+offset)%86400,n_epochs=1440,valid_expert_labels=int((labels>=0).sum()),class_counts={str(k):int((labels==k).sum()) for k in range(5)}));print('H08 prepared',subject,offset,slices[-1]['class_counts'],flush=True)
 x=np.asarray(xs);y=np.asarray(ys);np.savez_compressed(C/'data.npz',train_x=x[:5],train_y=y[:5],test_x=x[5:],test_y=y[5:],train_groups=np.arange(5),test_groups=np.arange(5,8))
 meta=dict(benchmark_id='H08',metric='macro_f1_sleep',direction='higher',truth_type='independent_human_sleep_stage_annotations',input='(night,1440 consecutive30second epochs,3000EEGsamples);100Hz,EEG Fpz-Cz in microvolts;full12hwallclockwindow starting20:00 roundedupto source30sgrid',sampling_hz=100,units='microvolts',label_encoding={'0':'Wake','1':'N1','2':'N2','3':'N3=R&Kstages3and4','4':'REM','-1':'unknown/movement/crossannotation epoch,trainingignore,excludedfromscore'},train_groups=list(range(5)),test_groups=list(range(5,8)),train_subjects=list(range(5)),test_subjects=list(range(5,8)),baseline_name='Fixed spectral/statistical HistGradientBoosting,trainingnightsonly',slices=slices,license='ODC-By1.0',source='https://physionet.org/content/sleep-edfx/1.0.0/',limitations=['Threeheldoutsubjects,firstnightonly,firsteightnotrandomcohort','Fixed20:00–08:00clockwindow,notstandardlabel-trimmedSleepEDF20protocol','SingleFpz-CzEEG;noEOG/EMG/demographics','R&K5classmapping;notfullAASMannotations','YASApretrainedNSRRmodelhasdifferenttrainingbudget,butidenticalprovidednightcontext','Publicdata/pretrainingcontaminationunverified'])
 (C/'metadata.json').write_text(json.dumps(meta,indent=2));(R/'data/manifests/H08.json').write_text(json.dumps(dict(benchmark_id='H08',source_version='1.0.0',doi='10.13026/C2X676',license='ODC-By1.0',files=manifest,prepared_sha256=sha(C/'data.npz'),slices=slices),indent=2));return meta

def load():
 with np.load(C/'data.npz') as z:return tuple(z[k] for k in ['train_x','train_y','test_x','test_y'])
def features(x):
 from scipy.signal import welch
 from scipy.stats import skew,kurtosis
 a=x.reshape(-1,3000).astype(float);f,p=welch(a,fs=100,nperseg=400,axis=-1);total=np.trapezoid(p[(slice(None),)*(p.ndim-1)+( (f>=.5)&(f<=30),)],f[(f>=.5)&(f<=30)],axis=-1)
 cols=[np.log(np.std(a,axis=-1)+1e-6),skew(a,axis=-1),kurtosis(a,axis=-1),np.mean(np.diff(np.sign(a),axis=-1)!=0,axis=-1),np.log(total+1e-8)]
 for low,high in [(.5,2),(2,4),(4,8),(8,12),(12,16),(16,30)]:
  mask=(f>=low)&(f<high);power=np.trapezoid(p[:,mask],f[mask],axis=-1);cols.extend([np.log(power+1e-8),power/(total+1e-8)])
 return np.nan_to_num(np.column_stack(cols))
def baseline(x,y,xt):
 from sklearn.ensemble import HistGradientBoostingClassifier
 a=features(x);b=features(xt);labels=y.ravel();mask=labels>=0;m=HistGradientBoostingClassifier(max_iter=100,max_leaf_nodes=31,l2_regularization=1.,early_stopping=False,random_state=20261030);return m.fit(a[mask],labels[mask]).predict(b).reshape(xt.shape[:2])
def score(pred,truth,test_x):
 from sklearn.metrics import f1_score,balanced_accuracy_score,accuracy_score
 pred=np.asarray(pred);assert pred.shape==truth.shape and np.isfinite(pred).all() and np.isin(pred,np.arange(5)).all();mask=truth>=0
 groups=[dict(group=str(g+5),score=float(f1_score(truth[g][truth[g]>=0],pred[g][truth[g]>=0],labels=np.arange(5),average='macro',zero_division=0)),metric='macro_f1_sleep',n=int((truth[g]>=0).sum())) for g in range(len(truth))]
 return dict(score=float(f1_score(truth[mask],pred[mask],labels=np.arange(5),average='macro',zero_division=0)),metric='macro_f1_sleep',direction='higher',accuracy=float(accuracy_score(truth[mask],pred[mask])),balanced_accuracy=float(balanced_accuracy_score(truth[mask],pred[mask])),per_unit=[g['score'] for g in groups],night_results=groups,n_scored_epochs=int(mask.sum()))
if __name__=='__main__':prepare()
