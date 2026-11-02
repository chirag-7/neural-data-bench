"""Separate reference execution: immutable inputs, saved predictions, unchanged scorers."""
from pathlib import Path
import os,sys,json,hashlib,importlib.util,time,traceback
import numpy as np
R=Path(__file__).resolve().parents[2];HERE=Path(__file__).parent
sys.path.insert(0,str(HERE));import methods

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def module(p):
 spec=importlib.util.spec_from_file_location('refadapter_'+str(p).replace('/','_'),p);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

def score(id,adapter,pred,truth,x):
 if id=='G01':return {'score':adapter.score(truth,pred),'metric':'r2_variance_weighted','direction':'higher'}
 if hasattr(adapter,'score'):
  if id=='E01':return {'score':adapter.score(pred,truth),'metric':'bits_per_spike','direction':'higher'}
  return adapter.score(pred,truth,x)
 if id=='A14':mask=~np.isfinite(x)&np.isfinite(truth);return {'score':float(np.sqrt(np.mean((pred[mask]-truth[mask])**2))),'metric':'rmse_missing','direction':'lower'}
 if id=='D02':return {'score':float(np.sqrt(np.mean((pred-truth)**2))),'metric':'rmse_mV','direction':'lower'}
 if id=='F04':
  from scipy.special import gammaln
  p=np.maximum(pred,1e-9);return {'score':float(np.mean(p-truth*np.log(p)+gammaln(truth+1))),'metric':'poisson_nll','direction':'lower'}
 if id=='H16':return {'score':float(np.mean(np.sqrt(np.mean((pred-truth)**2,axis=1))/np.sqrt(np.mean(truth**2,axis=1)))),'metric':'temporal_rrmse','direction':'lower'}
 if id=='I07':
  from sklearn.metrics import balanced_accuracy_score
  return {'score':float(balanced_accuracy_score(truth,pred)),'metric':'balanced_accuracy','direction':'higher'}
 raise ValueError(id)

def main(id):
 spec=json.loads((HERE/'freeze.json').read_text());assert sha(HERE/'methods.py')==spec['code_sha256']['methods.py'];assert sha(HERE/'run.py')==spec['code_sha256']['run.py']
 cases=spec['cases'][id];outputs=[];start=time.monotonic()
 for case in cases:
  assert sha(R/case['data'])==case['sha256'];m=module(R/case['adapter']);assert sha(R/case['adapter'])==case['adapter_sha256']
  with np.load(R/case['data'],allow_pickle=False) as z:x=z['train_x'].copy();y=z['train_y'].copy();q=z['test_x'].copy();groups=z['train_groups'].copy() if 'train_groups' in z else None
  # E06 uses identical training and one concatenated prediction call for both slices.
  if id=='E06':
   arrays=[]
   for c in cases:
    assert sha(R/c['data'])==c['sha256']
    with np.load(R/c['data'],allow_pickle=False) as z:assert np.array_equal(x,z['train_x']) and np.array_equal(y,z['train_y']);arrays.append(z['test_x'].copy())
   q=np.concatenate(arrays)
  tick=time.monotonic();pred,info=methods.METHODS[id](x,y,q,groups);seconds=time.monotonic()-tick
  assert np.isfinite(pred).all()
  target_cases=cases if id=='E06' else [case];offset=0
  for target_case in target_cases:
   with np.load(R/target_case['data'],allow_pickle=False) as z:target=z['test_y'];tx=z['test_x'];p=pred[offset:offset+len(tx)] if id=='E06' else pred
   if id=='E06':offset+=len(tx)
   dest=HERE/'predictions'/(id+'--'+target_case['slice_id']+'.npz');dest.parent.mkdir(exist_ok=True)
   if id=='A14':np.savez_compressed(dest,missing_values=p[~np.isfinite(tx)].astype(np.float64))
   else:np.savez_compressed(dest,prediction=p)
   sm=module(R/target_case['adapter']);result=score(id,sm,p,target,tx)
   row={'benchmark_id':id,'slice_id':target_case['slice_id'],'status':'measured','score':result['score'],'metric':result['metric'],'direction':result['direction'],'seconds':seconds,'within_180s':seconds<=180,'prediction_file':str(dest.relative_to(R)),'prediction_sha256':sha(dest),'data_file':target_case['data'],'data_sha256':target_case['sha256'],'adapter_file':target_case['adapter'],'adapter_sha256':target_case['adapter_sha256'],'fit_info':info,'score_details':result,'seed':methods.SEED,'threads':1,'device':'cpu'};outputs.append(row)
  if id=='E06':break
 (HERE/'runs').mkdir(exist_ok=True);(HERE/'runs'/(id+'.json')).write_text(json.dumps(outputs,indent=2,allow_nan=False)+'\n');print(json.dumps([{'id':r['benchmark_id'],'slice':r['slice_id'],'score':r['score'],'seconds':r['seconds']} for r in outputs]))
if __name__=='__main__':
 try:main(sys.argv[1])
 except Exception:
  (HERE/'runs').mkdir(exist_ok=True);(HERE/'runs'/(sys.argv[1]+'-failure.json')).write_text(json.dumps({'benchmark_id':sys.argv[1],'status':'failed','traceback':traceback.format_exc()},indent=2)+'\n');raise
