"""Independently audit retained C06 predictions; never execute any model/reference.

Read original MAT fluorescence/event arrays, reconstruct the complete fixed split,
and independently rebin/smooth spikes and rescore saved outputs. Optional output
may be written outside experiments/ and data/cache/. Run after results exist.
"""
from pathlib import Path
import argparse,hashlib,json,re
import numpy as np
from scipy.io import loadmat

ROOT=Path(__file__).resolve().parents[1]
MODELS=('gpt-5.6-sol','gpt-6-sol','gpt-6.1-sol')
REFERENCES=('task-baseline',)
TRAIN=('190115_Fish2','190125_Fish1')
TEST=('190116_Fish1','190301_Fish1')

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def require(ok,message):
 if not ok:raise AssertionError(message)
def inside_root(relative):
 p=(ROOT/relative).resolve()
 require(p.is_relative_to(ROOT.resolve()),'Path outside repository')
 return p

def smooth_counts(counts,dt):
 """Explicit normalized Gaussian and half-sample symmetric boundary extension.

 Independent implementation of declared sigma .2s, truncation4, reflect padding;
 does not call the preparation/scoring Gaussian routine or any adapter function.
 """
 sigma=.2/dt;radius=int(4*sigma+.5)
 offsets=np.arange(-radius,radius+1,dtype=float)
 kernel=np.exp(-.5*(offsets/sigma)**2);kernel/=kernel.sum()
 return np.convolve(np.pad(np.asarray(counts,dtype=float),(radius,radius),mode='symmetric'),kernel,mode='valid')

def original_recordings(index,manifest):
 require(index['commit']==manifest['source_commit'],'Source commit changed')
 published={Path(r['path']).name:r for r in index['files']}
 recorded={Path(r['path']).name:r for r in manifest['sources']}
 require(len(published)==15 and set(published)==set(recorded),'Incomplete DS04 source list')
 output=[];source_hashes=[]
 for name,item in sorted(published.items()):
  require(item['path'].startswith('Ground_truth/DS04-OGB1-zf-pDp/'),'Unexpected source family')
  p=ROOT/'data/cache/C06/raw'/name;b=p.read_bytes()
  require(len(b)==item['size']==recorded[name]['bytes'],'Source byte count mismatch')
  gitsha=hashlib.sha1(('blob '+str(len(b))+'\0').encode()+b).hexdigest()
  require(gitsha==item['sha']==recorded[name]['git_blob_sha1'],'Original Git blob changed')
  require(sha(p)==recorded[name]['sha256'],'Original MAT SHA256 changed')
  source_hashes.append(dict(file=name,sha256=sha(p),git_blob_sha1=gitsha,bytes=len(b)))
  animal=re.search(r'(\d{6}_Fish\d+)',name).group(1)
  require(animal in TRAIN+TEST,'Unexpected specimen')
  chunks=loadmat(p,simplify_cells=True)['CAttached']
  chunks=[chunks] if isinstance(chunks,dict) else list(chunks)
  for j,r in enumerate(chunks):
   t=np.asarray(r['fluo_time'],dtype=float).ravel()
   f=np.asarray(r['fluo_mean'],dtype=float).ravel()[:len(t)]
   s=np.asarray(r['events_AP'],dtype=float).ravel()/10000.
   require(len(t)==len(f) and len(t)>2 and np.isfinite(t).all() and np.isfinite(f).all(),'Invalid source trace')
   require(np.all(np.diff(t)>0),'Unsorted frame times')
   dt=float(np.median(np.diff(t)))
   edges=np.concatenate(([t[0]-dt/2],(t[:-1]+t[1:])/2,[t[-1]+dt/2]))
   valid=s[np.isfinite(s)&(s>=edges[0])&(s<=edges[-1])]
   # Histogram-equivalent construction via event index search and bincount.
   positions=np.minimum(np.searchsorted(edges,valid,side='right')-1,len(t)-1)
   counts=np.bincount(positions,minlength=len(t))
   smoothed=smooth_counts(counts,dt)
   require(np.isclose(smoothed.sum(),counts.sum(),rtol=1e-13,atol=1e-12),'Smoothing loses spike mass')
   output.append(dict(animal=animal,cell=Path(name).stem,recording=j,n=len(t),dt=dt,
    fluorescence=f,counts=counts,target=smoothed.astype(np.float32),spikes=int(counts.sum()),
    events_outside=int(np.isfinite(s).sum()-len(valid))))
 require(len(output)==45,'Incomplete recording coverage')
 return output,source_hashes

def independent_metrics(pred,truth,cells,animals):
 require(pred.shape==truth.shape and np.isfinite(pred).all() and np.all(pred>=0),'Invalid saved prediction')
 cell_results=[]
 for cell in sorted(set(cells)):
  ids=np.flatnonzero(cells==cell)
  require(len(set(animals[ids]))==1,'A neuron spans specimens')
  a=np.concatenate([truth[i,truth[i]>=0] for i in ids]).astype(float)
  b=np.concatenate([pred[i,truth[i]>=0] for i in ids]).astype(float)
  ac=a-a.mean();bc=b-b.mean();den=float(np.sqrt(np.dot(ac,ac)*np.dot(bc,bc)))
  corr=float(np.dot(ac,bc)/den) if den>0 else 0.
  total=max(float(a.sum()),1e-12)
  cell_results.append(dict(cell=str(cell),animal=str(animals[ids[0]]),pearson=corr,
   relative_error=float(np.abs(b-a).sum()/total),relative_bias=float((b-a).sum()/total),n_frames=len(a)))
 animal_results=[]
 for animal in sorted(set(animals)):
  entries=[r for r in cell_results if r['animal']==animal]
  animal_results.append(dict(animal=str(animal),**{key:float(np.mean([r[key] for r in entries])) for key in ['pearson','relative_error','relative_bias']}))
 return dict(score=float(np.mean([r['pearson'] for r in animal_results])),cell_results=cell_results,
  animal_results=animal_results,relative_error_equal_animal=float(np.mean([r['relative_error'] for r in animal_results])),
  relative_bias_equal_animal=float(np.mean([r['relative_bias'] for r in animal_results])))

def audit(require_complete=False):
 d=ROOT/'experiments/C06';cache=ROOT/'data/cache/C06'
 spec=json.loads((d/'run-spec.json').read_text());manifest=json.loads((d/'data-manifest.json').read_text())
 require(spec['benchmark_id']=='C06' and spec['run_id']=='batch-v11','Unexpected frozen run')
 for rel,h in spec['frozen_files'].items():require(sha(inside_root(rel))==h,'Frozen hash mismatch: '+rel)
 require(sha(d/'prompt.txt')==spec['prompt_sha256'],'Prompt changed')
 require(sha(cache/'data.npz')==spec['data_sha256']==manifest['data_sha256'],'Prepared data changed')
 require(sha(d/'adapter.py')==spec['adapter_sha256'],'Adapter changed')
 source_manifest=json.loads((d/'source-manifest.json').read_text())
 for r in source_manifest['files']:require(sha(inside_root(r['path']))==r['sha256'],'Retained source file changed')
 records,hashes=original_recordings(json.loads((d/'source/acquisition-index.json').read_text()),manifest)
 require(set(TRAIN).isdisjoint(TEST),'Specimen overlap')
 require(manifest['train_animals']==list(TRAIN) and manifest['test_animals']==list(TEST),'Split contract changed')
 arrays={};data_checks={}
 with np.load(cache/'data.npz',allow_pickle=False) as z:
  for split,groups,nrows,ncells in [('train',TRAIN,21,7),('test',TEST,24,8)]:
   rec=[r for r in records if r['animal'] in groups];require(len(rec)==nrows,'Recording split changed')
   x=z[split+'_x'];y=z[split+'_y'];cells=z[split+'_cells'];animals=z[split+'_groups']
   require(x.shape==(nrows,3,900) and y.shape==(nrows,900),'Prepared shape changed')
   require(len(set(cells))==ncells,'Neuron coverage changed')
   reconstructed=np.full(y.shape,-1,dtype=np.float32)
   for i,r in enumerate(rec):
    n=r['n'];require(cells[i]==r['cell'] and animals[i]==r['animal'],'Row identity changed')
    require(np.array_equal(x[i,0,:n],r['fluorescence'].astype(np.float32)),'Fluorescence mismatch')
    require(np.array_equal(x[i,1],np.arange(900)<n),'Valid mask mismatch')
    require(np.all(x[i,2,:n]==np.float32(r['dt'])) and np.all(x[i,:,n:]==0),'Timing/padding mismatch')
    require(np.array_equal(z[split+'_counts'][i,:n],r['counts']),'Event count mismatch')
    require(np.all(z[split+'_counts'][i,n:]==-1) and np.all(y[i,n:]==-1),'Target padding mismatch')
    require(np.allclose(y[i,:n],r['target'],rtol=1e-7,atol=5e-8),'Independent spike smoothing mismatch')
    # Rescore against targets rebuilt from original electrical events, rather
    # than trusting cached targets merely because their hash is sealed.
    reconstructed[i,:n]=r['target']
   arrays[split]=dict(truth=reconstructed,cells=cells.copy(),animals=animals.copy())
   data_checks[split]=dict(neurons=ncells,recordings=nrows,spikes=sum(r['spikes'] for r in rec),
    excluded_untimed_events=sum(r['events_outside'] for r in rec),original_traces_targets_match=True)
 require(set(arrays['train']['cells']).isdisjoint(arrays['test']['cells']),'Neuron overlap')
 rows=json.loads((ROOT/'results/C06.json').read_text())
 rows=[r for r in rows if r.get('run_id','batch-v11')=='batch-v11' and r.get('slice_id')=='batch-v11']
 require(len({r['model'] for r in rows})==len(rows),'Duplicate attempts')
 audited=[];failed=[];present=set();generated_code_checks=[]
 for row in rows:
  model=row['model'];require(model in MODELS+REFERENCES,'Unexpected model');present.add(model)
  if model in MODELS:
   code=json.loads((d/(model+'.json')).read_text())['code'];h=hashlib.sha256(code.encode()).hexdigest()
   retained=d/(model+'.py')
   if retained.exists():require(retained.read_bytes()==code.encode(),'Retained code differs from generation')
   generated_code_checks.append(dict(model=model,generation_code_sha256=h,retained_program_exists=retained.exists(),
    retained_program_matches_generation=retained.exists(),code_lines=len(code.splitlines()),line_limit_compliant=len(code.splitlines())<240,
    attempt_code_digest_available='code_sha256' in row))
   if 'code_sha256' in row:require(row['code_sha256']==h,'Attempt code changed')
  if row['status']!='measured':
   require(bool(row.get('reason')),'Failure reason missing');failed.append(dict(model=model,status=row['status'],reason=row['reason']));continue
  p=inside_root(row['prediction_file']);require(sha(p)==row['prediction_sha256'],'Saved prediction hash mismatch')
  with np.load(p,allow_pickle=False) as z:pred=z['predictions']
  truth=arrays['test'];metrics=independent_metrics(pred,truth['truth'],truth['cells'],truth['animals'])
  require(row['metric']=='animal_mean_neuron_pearson_smoothed200ms' and row['direction']=='higher','Wrong metric')
  require(np.isclose(metrics['score'],row['score'],rtol=1e-8,atol=1e-9),'Primary metric mismatch')
  require(np.allclose([r['pearson'] for r in metrics['cell_results']],row['per_unit'],rtol=1e-8,atol=1e-9),'Per-neuron correlation mismatch')
  require(len(row['cell_results'])==8 and len(row['animal_results'])==2,'Missing grouped metrics')
  for actual,stored in zip(metrics['cell_results'],row['cell_results']):
   require(all(actual[k]==stored[k] for k in ['cell','animal','n_frames']),'Cell identity mismatch')
   for key in ['pearson','relative_error','relative_bias']:
    # Original scorer may sum float32; audit arithmetic uses float64.
    require(np.isclose(actual[key],stored[key],rtol=2e-6,atol=2e-7),'Cell metric mismatch: '+key)
  for actual,stored in zip(metrics['animal_results'],row['animal_results']):
   require(actual['animal']==stored['animal'] and np.isclose(actual['pearson'],stored['pearson'],rtol=1e-8,atol=1e-9),'Animal aggregation mismatch')
   for key in ['relative_error','relative_bias']:
    if key in stored:require(np.isclose(actual[key],stored[key],rtol=2e-6,atol=2e-7),'Animal secondary mismatch')
  require(row['prompt_sha256']==spec['prompt_sha256'],'Attempt prompt mismatch')
  if model in MODELS:
   require((d/(model+'.py')).read_bytes()==code.encode(),'Retained code differs from generation')
   require(row['code_sha256']==h and row['code_lines']==len(code.splitlines()),'Code provenance mismatch')
   require(row['line_limit_compliant']==(len(code.splitlines())<240),'Line compliance mismatch')
  else:h=sha(d/'adapter.py');require(row['code_sha256']==h,'Reference code changed')
  audited.append(dict(model=model,prediction_sha256=sha(p),program_sha256=h,**metrics))
 missing=sorted(set(MODELS+REFERENCES)-present);complete=not missing and not failed and len(audited)==4
 if require_complete:require(complete,'Incomplete or failed attempts')
 return dict(benchmark_id='C06',run_id='batch-v11',verification_status='passed' if complete else 'passed_for_available_measured_attempts',
  complete=complete,frozen_files_verified=len(spec['frozen_files']),original_mat_files=hashes,data_checks=data_checks,
  train_test_specimens_and_neurons_disjoint=True,independent_event_binning_and_gaussian_reconstruction=True,
  measured_attempts=audited,failed_attempts=failed,missing_attempts=missing,generated_code_checks=generated_code_checks,models_or_references_executed=False,
  scope='All released DS04 recordings; two heldout acute specimens, not a new cohort or official CASCADE benchmark')

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path);p.add_argument('--require-complete',action='store_true');args=p.parse_args()
 report=json.dumps(audit(args.require_complete),indent=2)+'\n'
 if args.output:
  out=args.output.resolve()
  require(not out.is_relative_to((ROOT/'experiments').resolve()) and not out.is_relative_to((ROOT/'data/cache').resolve()),'Cannot write experiment/cache')
  out.parent.mkdir(parents=True,exist_ok=True);out.write_text(report)
 print(report,end='')
if __name__=='__main__':main()
