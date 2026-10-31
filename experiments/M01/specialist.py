"""Pooled behavioral GLM using the original paper's stimulus/history/block basis."""
import numpy as np
from sklearn.linear_model import LogisticRegression
def design(x,levels):
 signed=x[:,1]-x[:,0];contrast=np.abs(signed);last_choice=x[:,3];last_feedback=x[:,8]
 return np.column_stack([*[np.sign(signed)*np.isclose(contrast,v,atol=1e-7,rtol=0) for v in levels],
                         last_choice*(last_feedback==1),last_choice*(last_feedback==-1),
                         2*x[:,2]-1])
def fit_predict(x,y,xt,groups):
 # Categorical signed-contrast coefficients; retain every observed training contrast.
 levels=np.unique(np.abs(x[:,1]-x[:,0]));levels=levels[levels>0]
 # C=1e6 approximates the paper's unpenalized MLE, with a finite numerical penalty.
 model=LogisticRegression(C=1e6,solver='lbfgs',max_iter=1000,random_state=20261030)
 # Equal total weight per training mouse, consistent with the subject-equal endpoint.
 _,inverse,counts=np.unique(groups,return_inverse=True,return_counts=True)
 weights=len(y)/(len(counts)*counts[inverse])
 model.fit(design(x,levels),y,sample_weight=weights)
 return model.predict_proba(design(xt,levels))[:,1]
