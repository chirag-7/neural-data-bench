"""SingleR 0.5.0; donor-by-layer reference profiles from outer training only."""
import numpy as np
import singler
import importlib.metadata
def fit_predict(x,y,xt,groups):
 assert importlib.metadata.version('singler')=='0.5.0'
 profiles=[];labels=[]
 for g in np.unique(groups):
  for label in np.unique(y[groups==g]):
   profiles.append(x[(groups==g)&(y==label)].mean(axis=0,dtype=np.float64));labels.append(str(int(label)))
 reference=np.stack(profiles).T;features=[str(i) for i in range(x.shape[1])]
 built=singler.train_single(reference,labels,ref_features=features,test_features=features,
                           marker_method='classic',num_de=50,aggregate=False,num_threads=1)
 result=singler.classify_single(xt.T,built,quantile=.8,use_fine_tune=True,
                               fine_tune_threshold=.05,num_threads=1)
 return np.asarray(result['best'],dtype=int)
