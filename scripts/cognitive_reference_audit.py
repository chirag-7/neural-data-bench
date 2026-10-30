"""Post-hoc objective-matched reference, separate from the frozen MLE baseline."""
import hashlib,json,time
import numpy as np
from scipy.integrate import simpson,cumulative_trapezoid
from evaluate import ROOT,nll

def posterior_medians(choices,rewards,resolution):
    alpha=np.linspace(.01,.99,resolution);beta=np.linspace(.1,10,resolution)
    estimates=[]
    for c,r in zip(choices,rewards):
        q=np.full((len(alpha),2),.5);diff=[]
        for a,v in zip(c,r):
            diff.append(q[:,1]-q[:,0]);q[:,a]+=alpha*(v-q[:,a])
        diff=np.array(diff).T
        losses=np.empty((len(alpha),len(beta)))
        for j in range(0,len(beta),24):
            z=diff[:,None,:]*beta[None,j:j+24,None]
            losses[:,j:j+24]=np.sum(np.logaddexp(0,z)-c[None,None,:]*z,axis=2)
        density=np.exp(losses.min()-losses)
        marginals=[simpson(density,x=beta,axis=1),simpson(density,x=alpha,axis=0)]
        row=[]
        for grid,marginal in zip([alpha,beta],marginals):
            cdf=cumulative_trapezoid(marginal,x=grid,initial=0);cdf/=cdf[-1]
            row.append(np.interp(.5,cdf,grid))
        estimates.append(row)
    return np.array(estimates)

def main():
    arrays=np.load(ROOT/'data/cache/cognitive-v1.npz');c=arrays['choices'];r=arrays['rewards'];truth=arrays['truth']
    t=time.perf_counter();coarse=posterior_medians(c,r,257);pred=posterior_medians(c,r,513);elapsed=time.perf_counter()-t
    error=np.mean(np.abs(pred-truth)/[.98,9.9],axis=1)
    path=ROOT/'results/predictions/M04/synthetic-v1--canonical-posterior.npz';np.savez_compressed(path,predictions=pred)
    record=dict(benchmark_id='M04',slice_id='synthetic-v1',model='canonical-posterior',status='measured',date='2026-10-30',track='reference',reference_type='local_reproduction_posthoc',generation_replicates=None,seconds=elapsed,metric='range_normalized_mae',direction='lower',n_units=24,truth_type='synthetic_known_parameters',score=float(error.mean()),mean=float(error.mean()),per_unit=error.tolist(),per_parameter_mae=np.mean(np.abs(pred-truth),axis=0).tolist(),nll_per_trial=float(np.mean([nll(p,cc,rr)[0]/len(cc) for p,cc,rr in zip(pred,c,r)])),prediction_file=str(path.relative_to(ROOT)),prediction_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),code_sha256=hashlib.sha256(__import__('pathlib').Path(__file__).read_bytes()).hexdigest(),description='Independent dense quadrature with Simpson marginalization and trapezoid-CDF inversion; uniform priors over prompt bounds. Post-hoc audit, not the frozen primary MLE reference.',convergence_check=dict(coarse_resolution=257,fine_resolution=513,max_range_normalized_estimate_change=float(np.max(np.abs(pred-coarse)/[.98,9.9])),coarse_score=float(np.mean(np.abs(coarse-truth)/[.98,9.9]))))
    p=ROOT/'results/M04.json';records=[x for x in json.loads(p.read_text()) if x['model']!='canonical-posterior'];records.append(record);p.write_text(json.dumps(records,indent=2))
    (ROOT/'results/execution/M04-posterior-reference-audit.txt').write_text(json.dumps(record,indent=2));print(json.dumps(record,indent=2))
if __name__=='__main__':main()
