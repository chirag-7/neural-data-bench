"""Real place-cell count prediction, temporal holdout,20ms bins. Custom diagnostic."""
from pathlib import Path
import hashlib,json,urllib.request
import numpy as np
from scipy.io import loadmat
ROOT=Path(__file__).resolve().parents[2];CACHE=ROOT/'data/cache/L04';PIN='060e67e81096b900773e2166910c5f3aca6365f8'
def prepare():
 CACHE.mkdir(parents=True,exist_ok=True);raw=CACHE/'spikes-1.mat'
 if not raw.exists():raw.write_bytes(urllib.request.urlopen(f'https://raw.githubusercontent.com/Mark-Kramer/Case-Studies-Python/{PIN}/matfiles/spikes-1.mat',timeout=90).read())
 a=loadmat(raw);t=a['t'].ravel();x=a['X'].ravel();st=a['spiketimes'].ravel();dt=float(np.median(np.diff(t)));assert np.isclose(dt,.001,atol=1e-7)
 width=20;n=len(t)//width;end=t[0]+n*width*dt-dt/2;edges=t[0]-dt/2+np.arange(n+1)*width*dt
 counts=np.histogram(st,edges)[0].astype(float);position=x[:n*width].reshape(n,width).mean(axis=1);velocity=np.gradient(position,width*dt);features=np.c_[position,velocity]
 split=int(.6*n);gap=50;train_x=features[:split];train_y=counts[:split];test_x=features[split+gap:];test_y=counts[split+gap:]
 np.savez_compressed(CACHE/'data.npz',train_x=train_x,train_y=train_y,test_x=test_x,test_y=test_y,train_times=t[0]+np.arange(split)*.02,test_times=t[0]+np.arange(split+gap,n)*.02)
 meta=dict(benchmark_id='L04',slice_id='real-place-cell-temporal-v1',metric='bits_per_spike_train_mean',direction='higher',truth_type='observed_extracellular_spike_counts',input='float64(timebin,2):positioncm andvelocitycm/second;20ms bins,one recorded hippocampal place cell',feature_names=['mean_position_cm','velocity_cm_per_second'],train_shape=list(train_x.shape),test_shape=list(test_x.shape),train_null_mean=float(train_y.mean()),spike_total=int(counts.sum()),n_train=len(train_y),n_test=len(test_y),sampling_hz=50,baseline_name='Quadratic position×direction PoissonGLM, fixedtinyL2',source=f'https://github.com/Mark-Kramer/Case-Studies-Python/tree/{PIN}',license='MIT repository; raw source cached, source attribution retained',limitations=['Single public teaching recording; author describes in-vivo rat hippocampal cell, no animal ID metadata','Temporal60/40split with1sbuffer; bins not independent biological samples','20ms target aggregation differs from original1mstutorial','No confidence-interval, goodness-of-fit, stationarity or causal claim'])
 (CACHE/'metadata.json').write_text(json.dumps(meta,indent=2));return meta

def load():
 with np.load(CACHE/'data.npz') as z:return tuple(z[k] for k in ['train_x','train_y','test_x','test_y'])
def baseline(train_x,train_y,test_x):
 from scipy.optimize import minimize
 def design(a):
  x=(a[:,0]-50)/50;d=(a[:,1]>0).astype(float);return np.c_[np.ones(len(x)),x,x*x,d,d*x,d*x*x]
 a,b=design(train_x),design(test_x);reg=np.array([0,1,1,1,1,1])*1e-5
 def fn(w):
  z=np.clip(a@w,-30,20);m=np.exp(z);return np.mean(m-train_y*z)+.5*np.sum(reg*w*w),a.T@(m-train_y)/len(train_y)+reg*w
 initial=np.zeros(6);initial[0]=np.log(max(train_y.mean(),1e-8));fit=minimize(fn,initial,jac=True,method='L-BFGS-B',options={'maxiter':2000,'ftol':1e-12,'gtol':1e-9});return np.exp(np.clip(b@fit.x,-30,20))
def score(pred,truth,test_x=None):
 from scipy.special import gammaln
 p=np.asarray(pred,float).reshape(-1);y=np.asarray(truth,float);assert p.shape==y.shape and np.isfinite(p).all() and (p>=0).all();p=np.maximum(p,1e-12);ref=json.loads((CACHE/'metadata.json').read_text())['train_null_mean'];nll=p-y*np.log(p)+gammaln(y+1);null=ref-y*np.log(ref)+gammaln(y+1)
 return dict(score=float((null.sum()-nll.sum())/(y.sum()*np.log(2))),metric='bits_per_spike_train_mean',direction='higher',poisson_nll_per_bin=float(nll.mean()),per_unit=None)
if __name__=='__main__':print(json.dumps(prepare(),indent=2))
