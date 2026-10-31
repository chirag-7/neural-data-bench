"""Mouse-disjoint conditional choice prediction with disjoint target/history blocks."""
from pathlib import Path
import hashlib,io,json,zipfile,collections
import numpy as np
from sklearn.metrics import log_loss,accuracy_score
R=Path(__file__).resolve().parents[2];D=R/'experiments/M01';C=R/'data/cache/M01'
FIELDS=['choice','contrastLeft','contrastRight','feedbackType','probabilityLeft']
FEATURES=['contrastLeft','contrastRight','probabilityLeft']+[f'previous_choice_lag{k}' for k in range(1,6)]+[f'previous_feedback_lag{k}' for k in range(1,6)]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def prepare():
 source=json.loads((D/'source-record.json').read_text());item=next(v for v in source['files'] if v['name'].endswith('.zip'));p=C/'raw'/item['name']
 assert p.stat().st_size==item['size'] and hashlib.md5(p.read_bytes()).hexdigest()==item['computed_md5']
 arrays=collections.defaultdict(list);subjects=collections.defaultdict(dict);checks=[];rows=[]
 with zipfile.ZipFile(p) as z:
  for name in z.namelist():
   if name.endswith('/_ibl_trials.choice.npy'):
    parts=name.split('/');assert parts[2]=='Subjects';subject=parts[3];session='/'.join(parts[:-1]);required=[session+'/_ibl_trials.'+v+'.npy' for v in FIELDS]
    if all(n in z.namelist() for n in required):subjects[subject][(parts[4],parts[5],parts[1])]=session
  for index,subject in enumerate(sorted(subjects)):
   # Latest complete session by date/run/lab; structural selection only, no score/performance filter.
   key=max(subjects[subject]);session=subjects[subject][key];data={f:np.load(io.BytesIO(z.read(session+'/_ibl_trials.'+f+'.npy')),allow_pickle=False).reshape(-1) for f in FIELDS};n=len(data['choice']);assert all(len(v)==n for v in data.values())
   digest=hashlib.sha256(('M01-v1:'+subject).encode()).hexdigest();split='test' if int(digest[:8],16)%5==0 else 'train'
   labels=data['choice'];left=data['contrastLeft'];right=data['contrastRight'];prior=data['probabilityLeft'];feedback=data['feedbackType'];candidates=np.arange(5,min(n,1000),6);retained=[]
   for t in candidates:
    if labels[t] not in [-1,1] or not np.isfinite(prior[t]) or not 0<=prior[t]<=1 or not (np.isfinite(left[t]) or np.isfinite(right[t])):continue
    l=0 if np.isnan(left[t]) else float(left[t]);r=0 if np.isnan(right[t]) else float(right[t]);assert np.isfinite([l,r]).all() and 0<=l<=1 and 0<=r<=1
    history=np.arange(t-1,t-6,-1);hc=np.where(np.isin(labels[history],[-1,0,1]),labels[history],0);hf=np.where(np.isin(feedback[history],[-1,1]),feedback[history],0)
    x=np.r_[l,r,prior[t],hc,hf].astype(np.float32);assert x.shape==(13,) and np.isfinite(x).all()
    arrays[split+'_x'].append(x);arrays[split+'_y'].append(int(labels[t]==1));arrays[split+'_groups'].append(subject);retained.append(int(t));rows.append(dict(subject=subject,lab=key[2],session=session,target_trial=int(t),history_trials=history.tolist(),split=split))
   assert not set(retained)&{h for t in retained for h in range(t-5,t)},'Evaluated targets must never become another example history'
   checks.append(dict(subject=subject,lab=key[2],session=session,split=split,n_source_trials=n,n_candidate_targets=len(candidates),n_retained=len(retained),sessions_available=len(subjects[subject]),source_members={f:hashlib.sha256(z.read(session+'/_ibl_trials.'+f+'.npy')).hexdigest() for f in FIELDS}))
 arrays={k:np.asarray(v) for k,v in arrays.items()};assert not set(arrays['train_groups'])&set(arrays['test_groups']);assert set(arrays['train_y'])=={0,1}
 np.savez_compressed(C/'data.npz',**arrays)
 meta=dict(benchmark_id='M01',dataset='IBL Dec2019 public behavior archive',primary_metric='mouse_equal_binary_log_loss',direction='lower',feature_names=FEATURES,label_encoding={'0':'source choice -1 turn CCW','1':'source choice +1 turn CW'},train_shape=list(arrays['train_x'].shape),test_shape=list(arrays['test_x'].shape),train_mice=len(set(arrays['train_groups'])),test_mice=len(set(arrays['test_groups'])),train_labs=sorted({c['lab'] for c in checks if c['split']=='train' and c['n_retained']}),test_labs=sorted({c['lab'] for c in checks if c['split']=='test' and c['n_retained']}),units='contrast and block probability in0..1; historical choice -1/0/+1, feedback -1/0/+1',truth_type='Recorded mouse choices, not latent cognitive parameters',history_policy='Observed prior-five trial outcomes permitted; disjoint six-trial blocks ensure no scored test target appears in any test input',adaptation='No test-fitted transforms or joining/matching examples; independent conditional one-step probabilities, not sequential rollout',data_quality='Original beta archive warning and missing events retained in source README; only explicit structural target/input exclusions')
 (C/'metadata.json').write_text(json.dumps(meta,indent=2)+'\n');(D/'selection-verification.json').write_text(json.dumps(dict(subjects=checks,source_sessions=len([n for n in z.namelist() if n.endswith('/_ibl_trials.choice.npy')]),train_test_mice_disjoint=True,target_history_trial_sets_disjoint=True,source_zip_md5_verified=True),indent=2)+'\n');(D/'trial-manifest.json').write_text(json.dumps(rows,separators=(',',':'))+'\n')
 (R/'data/manifests/M01.json').write_text(json.dumps(dict(benchmark_id='M01',license=source['license'],source=source['url_public_html'],files=[dict(path=str(p.relative_to(R)),url=item['download_url'],bytes=p.stat().st_size,publisher_md5=item['computed_md5'],publisher_md5_verified=True,sha256=sha(p))],prepared_file='data/cache/M01/data.npz',prepared_sha256=sha(C/'data.npz')),indent=2)+'\n');print(json.dumps(meta,indent=2))
def load():
 with np.load(C/'data.npz') as z:return tuple(z[k] for k in ['train_x','train_y','test_x','test_y'])
def train_groups():
 with np.load(C/'data.npz') as z:return z['train_groups']
def baseline(x,y,xt,groups):return np.full(len(xt),float(np.mean(y)))
def score(pred,truth,test_x=None):
 pred=np.asarray(pred);assert pred.shape==truth.shape and np.isfinite(pred).all() and (pred>=0).all() and (pred<=1).all();p=np.clip(pred,1e-6,1-1e-6)
 with np.load(C/'data.npz') as z:g=z['test_groups']
 results=[dict(group=str(v),n=int((g==v).sum()),score=float(log_loss(truth[g==v],p[g==v],labels=[0,1]))) for v in np.unique(g)]
 return dict(score=float(np.mean([v['score'] for v in results])),metric='mouse_equal_binary_log_loss',direction='lower',per_unit=[v['score'] for v in results],group_results=results,pooled_log_loss=float(log_loss(truth,p,labels=[0,1])),pooled_accuracy=float(accuracy_score(truth,p>=.5)),score_clipping=[1e-6,1-1e-6])
if __name__=='__main__':prepare()
