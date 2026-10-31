"""Audit B03 retained outputs against simulator state without running any method.

No adapter imports, reference fitting, generated-code execution or voltage
regeneration. Writes only an optional report outside experiments/ and cache/.
"""
from pathlib import Path
import argparse,ast,hashlib,json
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
MODELS=('gpt-5.6-sol','gpt-6-sol','gpt-6.1-sol')
REFERENCES=('task-baseline',)
ALLOWED={'numpy','scipy','sklearn','math','collections','functools','itertools','statistics','gc'}

def require(ok,message):
 if not ok:raise AssertionError(message)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def inside_root(relative):
 p=(ROOT/relative).resolve();require(p.is_relative_to(ROOT.resolve()),'Path outside repository');return p

def static_code_review(code,seeds,periods):
 """Static evidence only; does not prove all semantic task restrictions."""
 tree=ast.parse(code);imports=[];blocked=[];source_calls=[];seed_literals=[];period_literals=[]
 for node in ast.walk(tree):
  if isinstance(node,ast.Import):imports.extend(a.name.split('.')[0] for a in node.names)
  if isinstance(node,ast.ImportFrom):imports.append((node.module or '').split('.')[0])
  if isinstance(node,ast.Call):
   name=node.func.id if isinstance(node.func,ast.Name) else node.func.attr if isinstance(node.func,ast.Attribute) else ''
   if name in {'open','exec','eval','compile','__import__','input','breakpoint'}:blocked.append(name)
   if name in {'generate_drifting_recording','generate_displacement_vector','make_one_displacement_vector'}:source_calls.append(name)
  if isinstance(node,ast.Constant) and isinstance(node.value,(int,float)) and not isinstance(node.value,bool):
   if node.value in seeds:seed_literals.append(node.value)
   if node.value in periods:period_literals.append(dict(value=node.value,line=node.lineno))
 require(set(imports)<=ALLOWED,'Forbidden generated-code import')
 require(not blocked,'Forbidden generated-code call')
 require(not source_calls and not seed_literals,'Hidden simulator regeneration/source-seed evidence in submission')
 return dict(ast_parsed=True,imports=sorted(set(imports)),forbidden_imports_or_calls=False,
  hidden_seed_literals_found=seed_literals,simulator_regeneration_calls_found=source_calls,
  period_value_literals_for_human_review=period_literals,
  limitation='Numeric periods can legitimately be filter sizes or inferred-trajectory priors; listed literals alone do not prove forbidden regeneration. Static checks do not prove arbitrary semantic compliance.')

def code_checks(folder,manifest):
 seeds={r['parameters']['seed'] for r in manifest['records']}
 periods={motion['period_s'] for r in manifest['records'] for motion in r['parameters']['generate_displacement_vector_kwargs']['motion_list'] if 'period_s' in motion}
 result={}
 for model in MODELS:
  source=folder/(model+'.json')
  if not source.exists():continue
  obj=json.loads(source.read_text());code=obj['code'];h=hashlib.sha256(code.encode()).hexdigest()
  retained=folder/(model+'.py')
  if retained.exists():require(retained.read_bytes()==code.encode(),'Saved program differs from generation: '+model)
  result[model]=dict(generation_json_sha256=sha(source),code_sha256=h,code_lines=len(code.splitlines()),
   line_limit_compliant=len(code.splitlines())<240,retained_program_exists=retained.exists(),
   saved_program_matches_generation=retained.exists(),**static_code_review(code,seeds,periods))
 return result

def source_and_arrays(folder,spec,manifest):
 cache=ROOT/'data/cache/B03'
 require(sha(cache/'data.npz')==spec['data_sha256']==manifest['data_sha256'],'Prepared data hash mismatch')
 sources=json.loads((folder/'source-manifest.json').read_text())
 for f in sources['files']:require(sha(inside_root(f['path']))==f['sha256'],'Original source code hash mismatch')
 require(manifest['software']==dict(spikeinterface='0.105.4',probeinterface='0.4.2'),'Simulation source version changed')
 require(len(manifest['records'])==8,'Incomplete simulation set')
 xs=[];ys=[];seeds=[];checks=[]
 for i,info in enumerate(manifest['records']):
  path=cache/'raw'/f'simulation-{i:02d}.npz';meta=path.with_suffix('.json')
  require(json.loads(meta.read_text())==info,'Retained simulation metadata differs from frozen manifest')
  require(sha(path)==info['source_array_sha256'],'Retained simulator archive changed')
  require(info['simulation']==i and info['split']==('train' if i<4 else 'test'),'Split order changed')
  params=info['parameters'];seeds.append(params['seed'])
  require(params['num_units']==64 and params['duration']==90. and params['sampling_frequency']==20000.,'Simulation contract changed')
  drift=params['generate_displacement_vector_kwargs']
  require(drift['displacement_sampling_frequency']==5. and drift['drift_start_um']==[0.,30.] and drift['drift_stop_um']==[0.,-30.] and drift['drift_step_um']==2.,'Displacement grid changed')
  with np.load(path,allow_pickle=False) as z:
   vector=np.asarray(z['displacement_vectors']);unit=np.asarray(z['unit_displacements'])
   require(vector.shape==(450,2,1) and unit.shape==(450,64,2),'Invalid original state dimensions')
   state=vector[:,1,0]
   require(np.isfinite(state).all() and np.all(np.abs(state)<=30.+1e-7),'Invalid latent displacement')
   require(np.allclose(unit[:,:,1],state[:,None],rtol=0,atol=1e-12) and np.all(unit[:,:,0]==0),'Nonrigid/unexpected source motion')
   # Nearest2um template grid; descending-grid argmin breaks exact ties upward.
   quantized=-30.+2*np.searchsorted(np.arange(-29.,30.,2.),state,side='right')
   require(np.array_equal(quantized,z['quantized_displacement_5hz']),'Actual grid position mismatch')
   target=np.array([sum(quantized[5*t:5*t+5])/5. for t in range(90)],dtype=float)
   target-=sum(target)/90.;target=target.astype(np.float32)
   require(np.allclose(target,z['target'],rtol=0,atol=2e-6),'Original time-bin target mismatch')
   peaks=z['peaks'];locations=z['peak_locations'];events=z['spike_vector']
   require(len(peaks)==len(locations)==info['detected_peaks'] and len(events)==info['raw_n_events'],'Event coverage changed')
   require(np.unique(events['unit_index']).size==64 and np.all(np.diff(events['sample_index'])>=0),'Original spike vectors invalid')
   geometry=z['geometry'];require(geometry.shape==(64,2),'Geometry changed')
   require(np.array_equal(np.unique(geometry[:,1]),np.arange(0.,640.,20.)),'Probe depth changed')
   require(np.all(z['noise_estimate_uv']>0) and np.isfinite(z['noise_estimate_uv']).all(),'Noise invalid')
   raster=np.histogram2d(peaks['sample_index']/20000.,locations['y'],bins=[np.arange(91.),np.arange(-20.,645.,5.)])[0].astype(np.float32)
   require(np.array_equal(raster,z['histogram']) and int(raster.sum())==info['histogram_count'],'Observed raster mismatch')
   require(np.array_equal(z['depth_edges'],np.arange(-20.,645.,5.)) and np.array_equal(z['temporal_edges'],np.arange(91.)),'Raster bin axes changed')
   xs.append(raster);ys.append(target)
   checks.append(dict(simulation=i,split=info['split'],archive_sha256=sha(path),true_events=len(events),observed_peaks=len(peaks),
    state_quantization_and_timebin_reconstruction=True,observation_raster_reconstruction=True))
 require(len(set(seeds))==8 and not set(seeds[:4]).intersection(seeds[4:]),'Simulation-seed overlap')
 with np.load(cache/'data.npz',allow_pickle=False) as z:
  for split,idx in [('train',range(4)),('test',range(4,8))]:
   require(np.array_equal(z[split+'_x'],np.stack([xs[i] for i in idx])),'Prepared observations differ from source')
   require(np.allclose(z[split+'_y'],np.stack([ys[i] for i in idx]),rtol=0,atol=2e-6),'Prepared targets differ from source')
   require(np.array_equal(z[split+'_groups'],list(idx)),'Prepared simulation IDs changed')
 return np.stack(ys[4:]).astype(float),checks

def audit(require_complete=False,code_only=False):
 folder=ROOT/'experiments/B03';spec=json.loads((folder/'run-spec.json').read_text())
 require(spec['benchmark_id']=='B03' and spec['run_id']=='batch-v11','Unexpected frozen run')
 for rel,h in spec['frozen_files'].items():require(sha(inside_root(rel))==h,'Frozen hash mismatch: '+rel)
 require(sha(folder/'prompt.txt')==spec['prompt_sha256'],'Prompt changed')
 require(sha(folder/'adapter.py')==spec['adapter_sha256'],'Adapter changed')
 manifest=json.loads((folder/'data-manifest.json').read_text());codes=code_checks(folder,manifest)
 # Hidden numeric source seeds must not have been supplied in the prompt.
 prompt=(folder/'prompt.txt').read_text()
 require(all(str(r['parameters']['seed']) not in prompt for r in manifest['records']),'Hidden source seed leaked into prompt')
 if code_only:return dict(benchmark_id='B03',run_id='batch-v11',scope='Static available-generation audit only',generated_code_checks=codes,
  missing_generation_models=sorted(set(MODELS)-set(codes)),submitted_programs_executed=False)
 truth,simulation_checks=source_and_arrays(folder,spec,manifest)
 rows=json.loads((ROOT/'results/B03.json').read_text())
 rows=[r for r in rows if r.get('run_id','batch-v11')=='batch-v11' and r.get('slice_id')=='batch-v11']
 require(len({r['model'] for r in rows})==len(rows),'Duplicate attempts')
 audited=[];failed=[];present=set()
 for row in rows:
  model=row['model'];require(model in MODELS+REFERENCES,'Unexpected method');present.add(model)
  if row['status']!='measured':failed.append(dict(model=model,status=row['status'],reason=row.get('reason')));continue
  path=inside_root(row['prediction_file']);require(sha(path)==row['prediction_sha256'],'Saved prediction changed')
  with np.load(path,allow_pickle=False) as z:pred=np.asarray(z['predictions'],dtype=float)
  require(pred.shape==(4,90) and np.isfinite(pred).all(),'Invalid retained displacement array')
  # Fix only the unidentifiable constant, separately for each whole recording.
  centered=pred-pred.mean(axis=1,keepdims=True);actual=truth-truth.mean(axis=1,keepdims=True)
  residual=centered-actual
  per=np.linalg.norm(residual,axis=1)/np.sqrt(90.)
  mae=np.sum(np.abs(residual),axis=1)/90.;maximum=np.max(np.abs(residual),axis=1);value=float(sum(per)/4.)
  require(row['metric']=='recording_mean_motion_rmse_um' and row['direction']=='lower','Metric changed')
  for name,expected in [('score',value),('per_unit',per),('recording_mae_um',mae),('recording_max_error_um',maximum)]:
   require(np.allclose(row[name],expected,rtol=1e-7,atol=2e-6),'Independent original-state metric mismatch: '+name)
  require(row['prompt_sha256']==spec['prompt_sha256'],'Attempt prompt changed')
  if model in MODELS:
   require(model in codes and codes[model]['retained_program_exists'],'Missing generated/saved code')
   h=codes[model]['code_sha256'];require(row['code_sha256']==h,'Attempt program hash mismatch')
   require(row['code_lines']==codes[model]['code_lines'] and row['line_limit_compliant']==codes[model]['line_limit_compliant'],'Code compliance record mismatch')
  else:h=sha(folder/'adapter.py');require(row['code_sha256']==h,'Reference implementation hash mismatch')
  audited.append(dict(model=model,score=value,per_recording_rmse_um=per.tolist(),per_recording_mae_um=mae.tolist(),
   per_recording_max_error_um=maximum.tolist(),prediction_sha256=sha(path),code_sha256=h,original_simulator_state_metrics_match=True))
 missing=sorted(set(MODELS+REFERENCES)-present);complete=not missing and not failed and len(audited)==4
 if require_complete:require(complete,'Incomplete or failed batch attempts')
 return dict(benchmark_id='B03',run_id='batch-v11',verification_status='passed' if complete else 'passed_for_available_measured_attempts',complete=complete,
  frozen_files_verified=len(spec['frozen_files']),data_sha256=sha(ROOT/'data/cache/B03/data.npz'),simulation_checks=simulation_checks,
  generated_code_checks=codes,measured_attempts=audited,failed_attempts=failed,missing_attempts=missing,
  source_voltage_regenerated=False,models_or_references_executed=False,scope='Synthetic rigid processed-raster endpoint; seed replication, not biological subjects')

def main():
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',type=Path);parser.add_argument('--require-complete',action='store_true');parser.add_argument('--code-only',action='store_true');args=parser.parse_args()
 report=json.dumps(audit(args.require_complete,args.code_only),indent=2)+'\n'
 if args.output:
  out=args.output.resolve()
  require(not out.is_relative_to((ROOT/'experiments').resolve()) and not out.is_relative_to((ROOT/'data/cache').resolve()),'Cannot write experiment/cache')
  out.parent.mkdir(parents=True,exist_ok=True);out.write_text(report)
 print(report,end='')
if __name__=='__main__':main()
