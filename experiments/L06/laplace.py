"""Conventional Gaussian Laplace approximation, frozen before generation."""
import numpy as np
from scipy.optimize import minimize
from scipy.special import expit

def sample_posterior(design_matrix,spike_trains,prior_precision,n_samples,seed):
    X=design_matrix;Q=prior_precision;rng=np.random.default_rng(seed);out=[]
    for y in spike_trains:
        def f(b):
            a=X@b;return np.logaddexp(0,a).sum()-y@a+.5*b@Q@b
        def g(b):return X.T@(expit(X@b)-y)+Q@b
        def h(b):
            p=expit(X@b);return X.T@((p*(1-p))[:,None]*X)+Q
        opt=minimize(f,np.zeros(10),jac=g,hess=h,method='trust-exact',options={'gtol':1e-8,'maxiter':100})
        L=np.linalg.cholesky(h(opt.x));out.append(opt.x+np.linalg.solve(L.T,rng.standard_normal((10,n_samples))).T)
    return np.asarray(out)
