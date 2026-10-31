"""Post-hoc all-output event accounting; original primary scores and predictions stay unchanged."""
from pathlib import Path
import json,hashlib,importlib.util
import numpy as np
import spikeinterface as si
import spikeinterface.comparison as sc
R=Path(__file__).resolve().parents[2];D=R/'experiments/B01'
s=importlib.util.spec_from_file_location('b01_frozen',D/'adapter.py');a=importlib.util.module_from_spec(s);s.loader.exec_module(a)
def counts_metrics(tp,n_true,n_pred):
 assert 0<=tp<=min(n_true,n_pred)
 fp=n_pred-tp;fn=n_true-tp
 return dict(tp=int(tp),fp=int(fp),fn=int(fn),n_true_events=int(n_true),n_predicted_events=int(n_pred),all_event_precision=float(tp/n_pred) if n_pred else 0.,all_event_recall=float(tp/n_true) if n_true else 0.,all_event_f1=float(2*tp/(n_true+n_pred)) if n_true+n_pred else 1.)
def greedy_count(x,y,delta=12):
 i=j=count=0
 while i<len(x) and j<len(y):
  if x[i]<y[j]-delta:i+=1
  elif y[j]<x[i]-delta:j+=1
  else:count+=1;i+=1;j+=1
 return count
def secondary(pred,truth,units):
 def obj(events,ids):return si.NumpySorting.from_unit_dict({int(u):np.sort(events[events[:,1]==u,0]).astype(np.int64) for u in ids},sampling_frequency=32000.)
 c=sc.compare_sorter_to_ground_truth(obj(truth,units),obj(pred,np.unique(pred[:,1])),**a.COMPARE_PARAMETERS)
 raw=c.get_performance(method='raw_count');tp=int(raw['tp'].sum());independent=0
 for u,row in raw.iterrows():
  v=int(row['tested_id'])
  if v!=-1:
   ct=greedy_count(np.sort(truth[truth[:,1]==u,0]),np.sort(pred[pred[:,1]==v,0]));assert ct==int(row['tp']),(u,v,ct,row['tp']);independent+=ct
 assert independent==tp
 primary=float(c.get_performance(method='by_unit')['accuracy'].mean())
 return counts_metrics(tp,len(truth),len(pred)),primary
if __name__=='__main__':
 assert si.__version__=='0.105.4'
 truth,units=a.load_truth();rp=R/'results/B01.json';records=json.loads(rp.read_text());out=[]
 for r in records:
  if r['status']!='measured':continue
  p=R/r['prediction_file'];assert hashlib.sha256(p.read_bytes()).hexdigest()==r['prediction_sha256']
  with np.load(p) as z:pred=z['predictions']
  v,primary=secondary(pred,truth,units);assert abs(primary-r['score'])<1e-12
  r['posthoc_secondary_metrics']=v;r['secondary_amendment']='experiments/B01/secondary-amendment.md';out.append(dict(model=r['model'],primary_mean_gt_accuracy=primary,**v))
 # Explicit conservation fixtures, including an entire unmatched cluster.
 gt=np.array([[100,0],[300,0],[500,0],[700,0]],dtype=np.int64)
 for pred,expected in [(gt.copy(),(4,0,0,1.)),(np.vstack([gt,[900,1]]),(4,1,0,8/9)),(np.vstack([gt,np.column_stack([gt[:,0],np.ones(4,int)])]),(4,4,0,2/3))]:
  v,primary=secondary(pred,gt,np.array([0]));assert (v['tp'],v['fp'],v['fn'])==expected[:3] and abs(v['all_event_f1']-expected[3])<1e-12 and primary==1.
 rp.write_text(json.dumps(records,indent=2)+'\n');(D/'secondary-audit.json').write_text(json.dumps(dict(policy='Post-hoc, original frozen primary unchanged',implementation_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),independent_pair_count_equivalence='passed for every matched pair and three fixtures',records=out),indent=2)+'\n');print(json.dumps(out,indent=2))
