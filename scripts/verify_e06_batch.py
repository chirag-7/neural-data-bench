"""Independent E06 batch audit, without executing submitted/reference programs.
Run after results exist. Reads frozen contracts/cache/predictions; writes only
an optional --output report. No adapter imports, model fitting or predictions.
"""
from pathlib import Path
import argparse,hashlib,json
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
MODELS=('gpt-5.6-sol','gpt-6-sol','gpt-6.1-sol')
REFERENCES=('task-baseline','mean-baseline')
OFFSETS=(0,649,2422,3078,3735,5047,5638,6623,7279,7879)
CONDITIONS=(0,1,2,4,5,6,7,8)
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def require(ok,message):
 if not ok:raise AssertionError(message)
def inside_root(relative):
 p=(ROOT/relative).resolve();require(p.is_relative_to(ROOT.resolve()),'Path outside repository');return p

def audit(require_complete=False):
 d=ROOT/'experiments/E06';spec=json.loads((d/'run-spec.json').read_text())
 require(spec['benchmark_id']=='E06' and spec['run_id']=='batch-v11','Unexpected frozen run')
 frozen=spec['frozen_files']
 for rel,digest in frozen.items():require(sha(inside_root(rel))==digest,'Frozen hash mismatch: '+rel)
 require(sha(d/'prompt.txt')==spec['prompt_sha256'],'Prompt hash mismatch')
 rawpath=ROOT/'data/cache/E06/raw/traces-selected.npy'
 manifest=json.loads((d/'data-manifest.json').read_text())
 require(sha(rawpath)==manifest['raw_subset_sha256'],'Original selected-array hash mismatch')
 raw=np.load(rawpath,allow_pickle=False)
 require(raw.shape==(7879,256) and np.isfinite(raw).all(),'Invalid original array')
 arrays={};data_checks={};training_targets=set();test_targets={}
 for sid,cache in [('batch-v11','E06'),('taxis','E06-taxis')]:
  rel=f'data/cache/{cache}/data.npz';path=ROOT/rel
  require(rel in frozen,'Slice data absent from frozen seal: '+sid)
  require(sha(path)==frozen[rel],'Slice data hash mismatch: '+sid)
  with np.load(path,allow_pickle=False) as z:a={k:z[k] for k in z.files}
  arrays[sid]=a
  require(np.array_equal(a['neuron_indices'],np.arange(0,71721,280)[:256]),'Neuron selection changed')
  expected_train=[];expected_groups=[]
  for c in CONDITIONS:
   lo,hi=OFFSETS[c]+1,OFFSETS[c+1]-1;n=hi-lo
   cut=lo+n-int(.2*n)-int(.1*n)
   starts=list(range(lo+64,cut-32+1,16));expected_train+=starts;expected_groups +=[c]*len(starts)
  require(np.array_equal(a['train_target_starts'],expected_train),'Unexpected complete train window schedule')
  require(np.array_equal(a['train_groups'],expected_groups),'Unexpected training groups')
  expected_test=[];test_groups=[]
  for c in ([3] if sid=='taxis' else CONDITIONS):
   lo,hi=OFFSETS[c]+1,OFFSETS[c+1]-1
   start=lo+256 if sid=='taxis' else hi-int((hi-lo)*.2)
   starts=list(range(start,hi-32+1,32));expected_test+=starts;test_groups +=[c]*len(starts)
  require(np.array_equal(a['test_target_starts'],expected_test),'Unexpected complete test window schedule')
  require(np.array_equal(a['test_groups'],test_groups),'Unexpected test groups')
  for prefix in ['train','test']:
   starts=a[prefix+'_target_starts'];groups=a[prefix+'_groups']
   require(a[prefix+'_x'].shape==(len(starts),64,256),'Input shape mismatch')
   require(a[prefix+'_y'].shape==(len(starts),32,256),'Target shape mismatch')
   for i,(t,c) in enumerate(zip(starts,groups)):
    require(np.array_equal(a[prefix+'_x'][i],raw[t-64:t]),'Original context mismatch')
    require(np.array_equal(a[prefix+'_y'][i],raw[t:t+32]),'Original target mismatch')
    if prefix=='train':training_targets.update(range(int(t),int(t)+32))
  targets=[t for start in expected_test for t in range(start,start+32)]
  require(len(targets)==len(set(targets)),'Overlapping evaluation targets within slice')
  test_targets[sid]=set(targets)
  data_checks[sid]=dict(data_sha256=sha(path),test_windows=len(expected_test),train_windows=len(expected_train),all_windows_match_original=True)
 require(not training_targets.intersection(set.union(*test_targets.values())),'Training/evaluation target overlap')
 require(not test_targets['batch-v11'].intersection(test_targets['taxis']),'Cross-slice target overlap')
 for key in ['train_x','train_y','train_target_starts','train_groups','neuron_indices']:
  require(np.array_equal(arrays['batch-v11'][key],arrays['taxis'][key]),'Slice training data differs')
 rows=json.loads((ROOT/'results/E06.json').read_text());rows=[r for r in rows if r.get('run_id','batch-v11')=='batch-v11' and r.get('slice_id') in arrays]
 require(len({(r['slice_id'],r['model']) for r in rows})==len(rows),'Duplicate attempt records')
 audited=[];codes={};failed=[];present=set()
 for row in rows:
  sid=row['slice_id'];model=row['model'];present.add((sid,model))
  require(model in MODELS+REFERENCES,'Unexpected model/reference identifier')
  if row['status']!='measured':failed.append(dict(slice_id=sid,model=model,status=row['status'],reason=row.get('reason')));continue
  predpath=inside_root(row['prediction_file'])
  require(sha(predpath)==row['prediction_sha256'],'Saved prediction hash mismatch')
  with np.load(predpath,allow_pickle=False) as z:p=np.asarray(z['predictions'],dtype=np.float64)
  starts=arrays[sid]['test_target_starts']
  require(p.shape==(len(starts),32,256) and np.isfinite(p).all(),'Invalid saved prediction shape/value')
  # Reconstruct truth directly from original traces; do not import adapter/score.
  truth=np.stack([raw[t:t+32] for t in starts]).astype(np.float64)
  per=np.mean((p-truth)**2,axis=(1,2));value=float(per.mean())
  require(row['metric']=='mse_dff' and row['direction']=='lower','Metric changed')
  require(np.isclose(value,row['score'],rtol=1e-12,atol=1e-15),'Direct raw-source MSE mismatch')
  if 'per_unit' in row:require(np.allclose(per,row['per_unit'],rtol=1e-12,atol=1e-15),'Per-window MSE mismatch')
  require(row['prompt_sha256']==spec['prompt_sha256'],'Attempt prompt differs')
  if model in MODELS:
   code=json.loads((d/(model+'.json')).read_text())['code'];codehash=hashlib.sha256(code.encode()).hexdigest()
   require((d/(model+'.py')).read_bytes()==code.encode(),'Saved program differs from generation')
   require(row['code_sha256']==codehash,'Attempt code hash differs')
  else:
   codehash=sha(d/'adapter.py');require(row['code_sha256']==codehash,'Reference implementation hash differs')
  if model in codes:require(codes[model]==codehash,'Program changed between slices')
  codes[model]=codehash
  audited.append(dict(slice_id=sid,model=model,score=value,prediction_sha256=sha(predpath),program_sha256=codehash,original_trace_mse_matches=True))
 expected={(sid,model) for sid in arrays for model in MODELS+REFERENCES};missing=sorted(expected-present)
 paired=[model for model in MODELS+REFERENCES if sum(r['model']==model for r in audited)==2]
 complete=not missing and not failed and len(audited)==len(expected)
 if require_complete:require(complete,'Incomplete/failed batch attempts')
 return dict(benchmark_id='E06',run_id='batch-v11',verification_status='passed' if complete else 'passed_for_available_measured_attempts',complete=complete,frozen_file_count=len(frozen),source_array_sha256=sha(rawpath),data_checks=data_checks,train_test_target_disjoint=True,main_taxis_targets_disjoint=True,training_arrays_identical=True,program_reuse_verified_models=paired,measured_attempts=audited,failed_attempts=failed,missing_attempts=[dict(slice_id=sid,model=model) for sid,model in missing],models_or_references_executed=False,scope='One animal/session; dependent stimulus slice, not independent biological replication')

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path);p.add_argument('--require-complete',action='store_true');args=p.parse_args()
 result=audit(args.require_complete);text=json.dumps(result,indent=2)+'\n'
 if args.output:
  out=args.output.resolve();require(not out.is_relative_to((ROOT/'experiments/E06').resolve()) and not out.is_relative_to((ROOT/'data/cache').resolve()),'Cannot write frozen experiment/cache');out.parent.mkdir(parents=True,exist_ok=True);out.write_text(text)
 print(text,end='')
if __name__=='__main__':main()
