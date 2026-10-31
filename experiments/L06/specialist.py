"""Local Polya-Gamma Gibbs adaptation of the original author reference algorithm.

Uses polyagamma's independent implementation instead of original pypolyagamma.
No true parameter initialization, no target samples, no post-score tuning.
"""
import numpy as np
from scipy.optimize import minimize
from scipy.special import expit
from polyagamma import random_polyagamma

def mode_and_precision(X,y,Q):
    def fun(b):
        a=X@b
        return np.logaddexp(0,a).sum()-y@a+.5*b@Q@b
    def jac(b): return X.T@(expit(X@b)-y)+Q@b
    def hess(b):
        p=expit(X@b);return X.T@((p*(1-p))[:,None]*X)+Q
    result=minimize(fun,np.zeros(X.shape[1]),jac=jac,hess=hess,method='trust-exact',
                    options={'gtol':1e-8,'maxiter':100})
    return result.x,hess(result.x)

def sample_posterior(design_matrix,spike_trains,prior_precision,n_samples,seed):
    X=design_matrix;Q=prior_precision;rng=np.random.default_rng(seed)
    out=np.empty((len(spike_trains),n_samples,X.shape[1]))
    for j,y in enumerate(spike_trains):
        b,_=mode_and_precision(X,y,Q);z=X.T@(y-.5);k=0
        for t in range(2500+2*n_samples):
            w=random_polyagamma(1.,X@b,random_state=rng)
            P=X.T@(w[:,None]*X)+Q;L=np.linalg.cholesky(P)
            b=np.linalg.solve(P,z)+np.linalg.solve(L.T,rng.standard_normal(X.shape[1]))
            if t>=2500 and (t-2500)%2==0:out[j,k]=b;k+=1
    return out
