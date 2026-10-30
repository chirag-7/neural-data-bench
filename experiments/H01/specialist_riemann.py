"""Train-only subject-CV pyRiemann tangent-space SVM reference; post-hoc addition, not SOTA."""
from pathlib import Path
import json,hashlib,time
import numpy as np
from scipy.signal import butter,sosfiltfilt
from sklearn.model_selection import LeaveOneGroupOut
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC
from sklearn.metrics import balanced_accuracy_score
from pyriemann.estimation import Covariances
from pyriemann.tangentspace import TangentSpace
import pyriemann
R=Path(__file__).resolve().parents[2];C=R/'data/cache/H01'
def fit_predict(x,y,xt,groups):
 candidates=[];prepared={}
 for band in [(7,30),(8,35),(8,15)]:
  sos=butter(4,band,fs=160,btype='bandpass',output='sos');a=sosfiltfilt(sos,x.astype(float),axis=-1);b=sosfiltfilt(sos,xt.astype(float),axis=-1);a-=a.mean(axis=-1,keepdims=True);b-=b.mean(axis=-1,keepdims=True);cov=Covariances(estimator='oas');ca=cov.transform(a);cb=cov.transform(b);ca/=np.trace(ca,axis1=1,axis2=2)[:,None,None];cb/=np.trace(cb,axis1=1,axis2=2)[:,None,None];prepared[band]=(ca,cb)
  predictions={v:np.empty(len(y),int) for v in [.1,1.,10.]}
  for tr,va in LeaveOneGroupOut().split(ca,y,groups):
   ts=TangentSpace(metric='riemann',tsupdate=False);f=ts.fit_transform(ca[tr]);fv=ts.transform(ca[va]);sc=StandardScaler();f=sc.fit_transform(f);fv=sc.transform(fv)
   for cost in predictions:predictions[cost][va]=SVC(C=cost,kernel='linear',class_weight='balanced').fit(f,y[tr]).predict(fv)
  for cost,p in predictions.items():candidates.append(dict(band=list(band),C=cost,validation_balanced_accuracy=float(balanced_accuracy_score(y,p))))
 best=max(candidates,key=lambda r:r['validation_balanced_accuracy']);ca,cb=prepared[tuple(best['band'])];ts=TangentSpace(metric='riemann',tsupdate=False);a=ts.fit_transform(ca);b=ts.transform(cb);sc=StandardScaler();a=sc.fit_transform(a);b=sc.transform(b);pred=SVC(C=best['C'],kernel='linear',class_weight='balanced').fit(a,y).predict(b)
 return pred,dict(selected=best,training_only_candidates=candidates,pyriemann_version=pyriemann.__version__,no_test_input_adaptation=True)
if __name__=='__main__':
 with np.load(C/'data.npz') as z:x,y,xt=(z[k] for k in ['train_x','train_y','test_x']);groups=z['train_groups']
 start=time.perf_counter();pred,selection=fit_predict(x,y,xt,groups);elapsed=time.perf_counter()-start
 dest=R/'results/predictions/H01/specialist--pyriemann-ts-svm.npz';np.savez_compressed(dest,predictions=pred);(R/'experiments/H01/specialist-selection.json').write_text(json.dumps(selection,indent=2));(R/'experiments/H01/specialist-runtime.json').write_text(json.dumps(dict(seconds=elapsed,model='pyriemann-ts-svm',prediction_file=str(dest.relative_to(R)),prediction_sha256=hashlib.sha256(dest.read_bytes()).hexdigest()),indent=2));print('pyRiemann prediction complete',elapsed,selection['selected'])
