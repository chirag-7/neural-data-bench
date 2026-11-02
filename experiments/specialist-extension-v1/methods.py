"""Local source-audited specialist adaptations; train-only fitting, fixed seed/budget."""
import numpy as np,time,copy,importlib.util
from pathlib import Path
SEED=20261102
BUDGET=140.0
HERE=Path(__file__).parent

def split_groups(groups,n):
 if groups is None:return np.arange(n)%5==0
 groups=np.asarray(groups);u=np.unique(groups);val=u[-max(1,len(u)//5):];return np.isin(groups,val)

def train(net,x,y,valid,kind='mse',batch=64,max_epochs=200):
 import torch
 torch.set_num_threads(1);torch.manual_seed(SEED)
 x=torch.as_tensor(np.asarray(x),dtype=torch.float32);y=torch.as_tensor(np.asarray(y),dtype=torch.long if kind=='class' else torch.float32)
 tr=np.flatnonzero(~valid);va=np.flatnonzero(valid)
 if len(va)>256:va=va[np.linspace(0,len(va)-1,256).astype(int)]
 opt=torch.optim.Adam(net.parameters(),lr=.001);rng=np.random.default_rng(SEED);best=float('inf');state=copy.deepcopy(net.state_dict());start=time.monotonic();history=[]
 def loss(p,target):
  if kind=='class':return torch.nn.functional.cross_entropy(p,target)
  if kind=='poisson':return torch.mean(torch.exp(torch.clamp(p,-14,8))-target*torch.clamp(p,-14,8))
  return torch.mean((p-target)**2)
 steps=0
 for epoch in range(max_epochs):
  net.train()
  for ind in np.array_split(rng.permutation(tr),max(1,int(np.ceil(len(tr)/batch)))):
   opt.zero_grad();v=loss(net(x[ind]),y[ind]);v.backward();torch.nn.utils.clip_grad_norm_(net.parameters(),5.);opt.step();steps+=1
   if time.monotonic()-start>BUDGET:break
  net.eval()
  with torch.no_grad():v=float(loss(net(x[va]),y[va]))
  history.append(v)
  if v<best:best=v;state=copy.deepcopy(net.state_dict())
  if time.monotonic()-start>BUDGET:break
 net.load_state_dict(state);net.eval()
 return {'epochs':len(history),'steps':steps,'validation_loss':best,'validation_n':len(va),'training_n':len(tr),'validation_history':history,'training_seconds':time.monotonic()-start,'early_stop':'minimum training-validation loss, fixed 140s cap'}

def predict(net,x,batch=64):
 import torch
 out=[]
 with torch.no_grad():
  for i in range(0,len(x),batch):out.append(net(torch.as_tensor(np.asarray(x[i:i+batch]),dtype=torch.float32)).numpy())
 return np.concatenate(out)

def a14(x,y,q,groups):
 import torch
 from torch import nn
 def prepare(v):
  v=np.asarray(v,float);missing=~np.isfinite(v);filled=v.copy()
  for i in range(len(v)):
   for j in range(3):
    good=~missing[i,:,j];filled[i,:,j]=np.interp(np.arange(31),np.flatnonzero(good),v[i,good,j])
  center=v[:,:,12:15];relative=(filled.reshape(-1,31,6,3)-center[:,:,None,:]).reshape(-1,31,18)
  return filled,relative,missing
 a,z,mask=prepare(x);b,u,mt=prepare(q);scale=float(np.std(z))+1e-8
 z=np.concatenate([z/scale,mask[:,:,::3].astype(float)],axis=2);u=np.concatenate([u/scale,mt[:,:,::3].astype(float)],axis=2)
 target=(y[:,:,0:3]-a[:,:,0:3])/scale
 class BiGRU(nn.Module):
  def __init__(self):super().__init__();self.gru=nn.GRU(24,64,batch_first=True,bidirectional=True);self.linear=nn.Linear(64,3)
  def forward(self,v):
   h,_=self.gru(v);return self.linear(h[:,:,:64]+h[:,:,64:])[:,12:19]
 torch.manual_seed(SEED);net=BiGRU();info=train(net,z,target[:,12:19],split_groups(groups,len(x)),batch=64)
 out=b.copy();out[:,12:19,:3]+=predict(net,u)*scale
 return out,info

def h16(x,y,q,groups):
 import torch
 from torch import nn
 # Port of official EEGdenoiseNet simple_CNN: four64-channel conv/BN/ReLU/dropout blocks and dense512 output.
 layers=[];channels=1
 for _ in range(4):layers +=[nn.Conv1d(channels,64,3,padding=1),nn.BatchNorm1d(64),nn.ReLU(),nn.Dropout(.3)];channels=64
 layers +=[nn.Flatten(),nn.Linear(64*512,512)]
 torch.manual_seed(SEED);net=nn.Sequential(*layers);info=train(net,x[:,None,:],y,split_groups(None,len(x)),batch=32,max_epochs=100)
 return predict(net,q[:,None,:],32),info

def e06(x,y,q,groups):
 import torch
 from torch import nn
 class NLinear(nn.Module):
  def __init__(self):super().__init__();self.linear=nn.Linear(64,32);nn.init.constant_(self.linear.weight,1/64);nn.init.zeros_(self.linear.bias)
  def forward(self,v):
   last=v[:,-1:,:];return self.linear((v-last).transpose(1,2)).transpose(1,2)+last
 torch.manual_seed(SEED);net=NLinear();info=train(net,x,y,split_groups(groups,len(x)),batch=32,max_epochs=1000)
 return predict(net,q,32),info

def e01(x,y,q,groups):
 import torch
 from torch import nn
 class Population(nn.Module):
  def __init__(self):super().__init__();self.gru=nn.GRU(x.shape[2],32,batch_first=True,bidirectional=True);self.latent=nn.Linear(64,8);self.readout=nn.Linear(8,y.shape[2])
  def forward(self,v):
   h,_=self.gru(torch.log1p(v));return self.readout(self.latent(h))
 torch.manual_seed(SEED);net=Population();mean=np.maximum(y.mean((0,1)),1e-5)
 with torch.no_grad():net.readout.bias.copy_(torch.as_tensor(np.log(mean)))
 info=train(net,x,y,split_groups(groups,len(x)),kind='poisson',batch=16,max_epochs=500)
 return np.exp(np.clip(predict(net,q),-14,8)),info

def f04(x,y,q,groups):
 import torch
 from torch import nn
 mean=float(np.mean(x));scale=float(np.std(x))+1e-8
 a=((x-mean)/scale).reshape(-1,1,18,18);b=((q-mean)/scale).reshape(-1,1,18,18)
 torch.manual_seed(SEED);net=nn.Sequential(nn.Conv2d(1,16,5,padding=2),nn.Softplus(),nn.Conv2d(16,16,3,padding=1),nn.Softplus(),nn.Flatten(),nn.Linear(16*18*18,y.shape[1]))
 with torch.no_grad():net[-1].bias.copy_(torch.as_tensor(np.log(np.maximum(y.mean(0),1e-5)),dtype=torch.float32))
 info=train(net,a,y,split_groups(groups,len(x)),kind='poisson',batch=64,max_epochs=200)
 return np.exp(np.clip(predict(net,b),-14,8)),info

def a15(x,y,q,groups):
 import torch
 from scipy.signal import stft
 spec=importlib.util.spec_from_file_location('tweetynet_source',HERE/'source/yardencsGitHub--tweetynet--src--tweetynet--network.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
 def features(v):
  v=v[np.isfinite(v)];n=len(v)//32
  _,_,z=stft(np.pad(v,(112,144),mode='reflect'),fs=32000,nperseg=256,noverlap=224,boundary=None,padded=False)
  z=np.log(np.maximum(abs(z[:,:n])**2,1e-12));return (z-np.median(z,axis=1,keepdims=True)).astype(np.float32)
 fs=[features(v) for v in x];qs=[features(v) for v in q];length=128;chunks=[];labels=[];recordings=[]
 for i,(f,target) in enumerate(zip(fs,y)):
  n=np.sum(target>=0);assert n==f.shape[1]
  for start in range(0,n-length+1,length):chunks.append(f[:,start:start+length]);labels.append(target[start:start+length]);recordings.append(i)
 chunks=np.stack(chunks)[:,None];labels=np.stack(labels);recordings=np.array(recordings);rng=np.random.default_rng(SEED)
 if len(chunks)>3000:
  keep=np.sort(rng.choice(len(chunks),3000,replace=False));chunks=chunks[keep];labels=labels[keep];recordings=recordings[keep]
 val=split_groups(np.asarray(groups)[recordings],len(chunks));torch.manual_seed(SEED)
 net=module.TweetyNet(2,input_shape=(1,129,length),conv1_filters=8,conv2_filters=16,hidden_size=32)
 info=train(net,chunks,labels,val,'class',batch=16,max_epochs=100)
 logits=predict(net,chunks[val],16);prob=np.exp(logits-logits.max(1,keepdims=True));prob=prob[:,1]/prob.sum(1);truth=labels[val]
 scores=[]
 for t in [.3,.5,.7]:
  p=prob>=t;tp=np.sum(p&(truth==1));scores.append(2*tp/max(1,np.sum(p)+np.sum(truth==1)))
 threshold=[.3,.5,.7][int(np.argmax(scores))]
 out=np.zeros((len(q),q.shape[1]//32),dtype=np.int8)
 from scipy.ndimage import binary_closing
 for i,f in enumerate(qs):
  n=f.shape[1];pad=(-n)%length;v=np.pad(f,((0,0),(0,pad)),mode='edge').reshape(129,-1,length).transpose(1,0,2)[:,None]
  logits=predict(net,v,16);p=np.exp(logits-logits.max(1,keepdims=True));p=(p[:,1]/p.sum(1)).reshape(-1)[:n];mask=binary_closing(p>=threshold,structure=np.ones(5))
  edges=np.diff(np.r_[False,mask,False].astype(int));starts=np.flatnonzero(edges==1);stops=np.flatnonzero(edges==-1)
  for a,b in zip(starts,stops):
   if b-a<10:mask[a:b]=False
  out[i,:n]=mask
 info.update(threshold=threshold,training_chunks=len(chunks),chunk_length=128,conv_filters=[8,16],hidden_size=32);return out,info

def d02(x,y,q,groups):
 from scipy.optimize import least_squares
 t=(np.arange(500)+.5)*.002;a=x.mean(1);b=q.mean(1)
 # Passive soma+dendritic two-time-constant charging model, fit only to four training sweeps.
 def basis(v,w):return v[:,None]*(w[0]*(1-np.exp(-t/np.exp(w[2])))+w[1]*(1-np.exp(-t/np.exp(w[3]))))
 fit=least_squares(lambda w:(basis(a,w)-y).ravel(),[.05,.05,np.log(.01),np.log(.1)],bounds=([0,0,np.log(.001),np.log(.001)],[10,10,np.log(.5),np.log(.5)]),max_nfev=3000)
 return basis(b,fit.x),{'fit_success':bool(fit.success),'parameters':fit.x.tolist(),'training_mse':float(np.mean((basis(a,fit.x)-y)**2))}

def i07(x,y,q,groups):
 from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
 from sklearn.preprocessing import StandardScaler
 # Hemodynamic temporal-pattern discrimination: mean/slope contrasts, optical density only.
 def feat(v):return np.concatenate([v.mean(-1),v[:,:,4:].mean(-1)-v[:,:,:4].mean(-1)],axis=1)
 a,b=feat(x),feat(q);scale=StandardScaler().fit(a);model=LinearDiscriminantAnalysis(solver='lsqr',shrinkage='auto').fit(scale.transform(a),y)
 return model.predict(scale.transform(b)),{'features':'channel mean and late-minus-early optical-density contrast','classifier':'shrinkage LDA','hemoglobin_conversion':False}

def l04(x,y,q,groups):
 from sklearn.preprocessing import SplineTransformer,StandardScaler
 from sklearn.linear_model import PoissonRegressor
 from sklearn.pipeline import make_pipeline
 from sklearn.metrics import mean_poisson_deviance
 # Position-by-direction tensor spline Poisson GLM; choose regularization on a chronological training holdout.
 def features(a,fit=None):
  if fit is None:fit=SplineTransformer(n_knots=8,degree=3,include_bias=False).fit(a[:,:1])
  b=fit.transform(a[:,:1]);direction=(a[:,1]>0)[:,None];return np.c_[b,b*direction,direction],fit
 n=int(.8*len(x));a,s=features(x[:n]);v,_=features(x[n:],s);loss=[]
 for alpha in [.0001,.001,.01,.1]:
  model=PoissonRegressor(alpha=alpha,max_iter=1000).fit(a,y[:n]);loss.append(mean_poisson_deviance(y[n:],model.predict(v)))
 alpha=[.0001,.001,.01,.1][int(np.argmin(loss))];a,s=features(x);b,_=features(q,s);model=PoissonRegressor(alpha=alpha,max_iter=1000).fit(a,y)
 return model.predict(b),{'family':'spline Poisson place-field GLM with direction interaction','alpha':alpha,'validation':'last20% of chronological training bins; no test labels'}

def k06(x,y,q,groups):
 import umap,networkx as nx
 from sklearn.impute import SimpleImputer
 # Published WaveMAP UMAP graph + Louvain clustering, followed by explicit train-only genetic-label mapping.
 a=x[:,6:];b=q[:,6:];imputer=SimpleImputer().fit(a);a=imputer.transform(a);b=imputer.transform(b)
 a=a/np.maximum(np.max(abs(a),axis=1,keepdims=True),1e-8);b=b/np.maximum(np.max(abs(b),axis=1,keepdims=True),1e-8)
 reducer=umap.UMAP(n_neighbors=15,min_dist=.1,n_components=2,random_state=SEED,n_jobs=1).fit(a)
 graph=nx.from_scipy_sparse_array(reducer.graph_);clusters=nx.community.louvain_communities(graph,resolution=1.5,seed=SEED)
 tags=np.zeros(len(a),int);prob=[];counts=np.bincount(y,minlength=2)
 for j,c in enumerate(clusters):
  ind=np.array(sorted(c));tags[ind]=j;w=np.bincount(y[ind],minlength=2)/counts;prob.append(w[1]/max(w.sum(),1e-12))
 # New waveforms are attached through nearest training embedding; no test-fitted graph.
 z=reducer.transform(b);dist=np.sum((z[:,None,:]-reducer.embedding_[None,:,:])**2,axis=2);neigh=np.argsort(dist,axis=1)[:,:5]
 p=np.mean(np.asarray(prob)[tags[neigh]],axis=1)
 return (p>=.5).astype(int),{'n_clusters':len(clusters),'resolution':1.5,'n_neighbors':15,'label_transfer':'five nearest train embeddings; inverse-class weighted training cluster labels','embedding_training_only':True}
METHODS={'A14':a14,'A15':a15,'D02':d02,'E01':e01,'E06':e06,'F04':f04,'H16':h16,'I07':i07,'L04':l04,'K06':k06}

def g01(x,y,q,groups):
 from sklearn.preprocessing import StandardScaler
 from sklearn.linear_model import Ridge
 from sklearn.metrics import r2_score
 # FALCON-style causal ridge decoder with chronological train-only regularization selection.
 n=int(.8*len(x));scale=StandardScaler().fit(x[:n]);a=scale.transform(x[:n]);v=scale.transform(x[n:]);scores=[]
 alphas=[1.,10.,100.,1000.,10000.]
 for alpha in alphas:
  model=Ridge(alpha=alpha).fit(a,y[:n]);scores.append(r2_score(y[n:],model.predict(v),multioutput='variance_weighted'))
 alpha=alphas[int(np.argmax(scores))];scale=StandardScaler().fit(x);model=Ridge(alpha=alpha).fit(scale.transform(x),y)
 return model.predict(scale.transform(q)),{'alpha':alpha,'validation_scores':scores,'validation':'chronological last20% of training rows; no IDs or test-fitted normalization','temporal_test_state':False}
METHODS['G01']=g01
