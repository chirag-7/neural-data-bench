"""Independent simulator/observable/target/split checks, no real method scores."""
from pathlib import Path
import hashlib,importlib.util,json
import numpy as np
P=Path(__file__).resolve().parent;ROOT=P.parents[1];CACHE=ROOT/'data/cache/B03'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def verify():
 import spikeinterface
 from spikeinterface.generation import generate_drifting_recording
 from spikeinterface.preprocessing import bandpass_filter
 assert spikeinterface.__version__=='0.105.4'
 manifest=json.loads((P/'data-manifest.json').read_text());source=json.loads((P/'source-manifest.json').read_text())
 for f in source['files']:assert sha(ROOT/f['path'])==f['sha256']
 assert sha(CACHE/'data.npz')==manifest['data_sha256']
 assert manifest['software']==dict(spikeinterface='0.105.4',probeinterface='0.4.2')
 reconstructed=[];seeds=[];summaries=[]
 for i,info in enumerate(manifest['records']):
  seed=info['parameters']['seed'];seeds.append(seed)
  raw=CACHE/'raw'/f'simulation-{i:02d}.npz';assert sha(raw)==info['source_array_sha256']
  assert info['split']==('train' if i<4 else 'test')
  assert info['parameters']['num_units']==64 and info['parameters']['duration']==90.
  assert info['parameters']['amplitude_std']==.15 and info['noise_median_uv']>0
  with np.load(raw,allow_pickle=False) as z:
   geometry=z['geometry'];assert geometry.shape==(64,2)
   assert np.unique(geometry[:,0]).size==2 and np.unique(geometry[:,1]).size==32
   assert np.all(np.diff(np.unique(geometry[:,1]))==20.)
   events=z['spike_vector'];assert len(events)==info['raw_n_events']
   assert np.unique(events['unit_index']).size==64
   peaks=z['peaks'];loc=z['peak_locations']
   assert len(peaks)==len(loc)==info['detected_peaks']
   assert np.isfinite(loc['y']).all() and np.isfinite(z['noise_estimate_uv']).all()
   assert np.all(z['noise_estimate_uv']>0)
   # Independent reconstruction of exactly what algorithms observe.
   raster=np.histogram2d(peaks['sample_index']/20000.,loc['y'],bins=[np.arange(91.),np.arange(-20.,645.,5.)])[0]
   assert np.array_equal(raster,z['histogram']) and raster.shape==(90,132)
   assert int(raster.sum())==info['histogram_count']
   assert np.array_equal(z['temporal_edges'],np.arange(91.))
   assert np.array_equal(z['depth_edges'],np.arange(-20.,645.,5.))
   # Source injection uses the nearest2um template position, with descending
   # grid breaking exact ties toward the larger displacement.
   state=z['displacement_vectors'][:,1,0]
   assert state.shape==(450,) and np.allclose(z['unit_displacements'][:,:,1],state[:,None])
   quantized=-30.+2*np.searchsorted(np.arange(-29.,30.,2.),state,side='right')
   assert np.array_equal(quantized,z['quantized_displacement_5hz'])
   target=np.array([quantized[5*t:5*t+5].mean() for t in range(90)]);target-=target.mean()
   assert np.array_equal(target.astype(np.float32),z['target'])
   reconstructed.append((raster.astype(np.float32),target.astype(np.float32)))
   # Recreate generator metadata and one voltage second, never a motion method.
   # This directly checks actual per-spike selected template positions, rather
   # than trusting a trajectory label divorced from the injected waveform.
   # JSON serializes generator range tuples as lists; restore their semantics.
   params=json.loads(json.dumps(info['parameters']))
   params['generate_noise_kwargs']['noise_levels']=tuple(params['generate_noise_kwargs']['noise_levels'])
   params['generate_sorting_kwargs']['firing_rates']=tuple(params['generate_sorting_kwargs']['firing_rates'])
   params['generate_templates_kwargs']['unit_params']={k:tuple(v) for k,v in params['generate_templates_kwargs']['unit_params'].items()}
   static,drifting,sorting,extra=generate_drifting_recording(**params)
   segment=drifting.segments[0]
   actual=segment.drifting_templates.displacements[segment.displacement_indices,1]
   ticks=(events['sample_index']/20000.*5.).astype(np.int64)
   assert np.array_equal(sorting.to_spike_vector(),events)
   assert np.array_equal(actual,quantized[ticks])
   replay=bandpass_filter(drifting,freq_min=300.,freq_max=6000.,filter_order=3,dtype='float32')
   first=replay.get_traces(start_frame=0,end_frame=20000)
   assert hashlib.sha256(np.ascontiguousarray(first).tobytes()).hexdigest()==info['voltage_first_second_sha256']
   del static,drifting,sorting,extra,replay
   summaries.append(dict(simulation=i,source_sha256=sha(raw),n_true_spikes=len(events),n_observed_peaks=len(peaks),
    noise_median_uv=info['noise_median_uv'],target_std_um=float(np.std(target)),known_simulator_truth=True,
    actual_per_spike_template_displacement_verified=True,first_second_voltage_regenerated_exactly=True))
 assert len(set(seeds))==8
 with np.load(CACHE/'data.npz',allow_pickle=False) as z:
  for prefix,indices in [('train',range(4)),('test',range(4,8))]:
   assert np.array_equal(z[prefix+'_x'],np.stack([reconstructed[i][0] for i in indices]))
   assert np.array_equal(z[prefix+'_y'],np.stack([reconstructed[i][1] for i in indices]))
   assert np.array_equal(z[prefix+'_groups'],list(indices))
  assert set(z['train_groups']).isdisjoint(z['test_groups'])
 # Scorer fixture uses unrelated artificial constants only, never real outputs.
 spec=importlib.util.spec_from_file_location('b03_adapter',P/'adapter.py');a=importlib.util.module_from_spec(spec);spec.loader.exec_module(a)
 truth=np.zeros((4,90));prediction=np.tile(np.r_[-np.ones(45),np.ones(45)],(4,1))
 assert a.score(prediction+123.,truth)['score']==1.
 assert a.score(np.ones((4,90))*20.,truth)['score']==0.
 report=dict(status='passed',data_sha256=manifest['data_sha256'],all_simulations_retained=True,
  distinct_simulation_seeds=True,voltage_observable_rasters_reconstructed=True,nearest_template_displacement_targets_reconstructed=True,
  recording_equal_gauge_invariant_scorer_toy_checks=True,real_method_execution=False,real_method_scores=False,simulations=summaries)
 (P/'validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
if __name__=='__main__':verify()
